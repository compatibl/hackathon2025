# Copyright (C) 2023-present The Project Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass
from cl.runtime.contexts.context_manager import active
from cl.runtime.db.data_source import DataSource
from cl.runtime.primitive.float_util import FloatUtil
from cl.runtime.primitive.timestamp import Timestamp
from cl.runtime.stat.binary_experiment import BinaryExperiment
from cl.runtime.stat.binary_trial import BinaryTrial
from cl.runtime.stat.case_key import CaseKey
from cl.convince.llms.gemini.gemini_llm import _RATIONALE_SEPARATOR
from cl.convince.llms.gemini.gemini_llm import GeminiLlm
from cl.hackathon.hackathon_case import HackathonCase
from cl.hackathon.hackathon_trial import HackathonTrial


@dataclass(slots=True, kw_only=True)
class HackathonExperiment(BinaryExperiment):
    """Trade entry experiment."""

    mitigation_prompt: str | None = None
    """Solution for the hackathon challenge is the text added after the query to counteract the cognitive bias."""

    max_retries: int = 10
    """Maximum number of retries for throttled requests."""

    default_retry_delay_sec: int = 2
    """Default retry delay in seconds for throttled requests when it cannot be extracted from the message."""

    max_retry_delay_sec: int = 120
    """Limit retry delay for throttled requests to this value in seconds when set by rule or extracted from message."""

    def create_trial(self, condition: CaseKey) -> BinaryTrial:
        """
        Create and return a new trial record with actual and (if applicable) expected fields
        without checking if num_trials has already been reached.
        """

        case = active(DataSource).load_one(condition, cast_to=HackathonCase)

        # Format components
        mitigation_prompt_txt = self.mitigation_prompt if self.mitigation_prompt else ""
        bias_prompt_txt = f"\n\n{case.bias_prompt}\n\n" if case.bias_prompt else ""
        business_prompt_with_substitution = case.business_prompt.format(bias_prompt=bias_prompt_txt)

        # Create LLM input
        llm_input = f"{Timestamp.create()}\n\n{mitigation_prompt_txt}\n\n{business_prompt_with_substitution}\n"

        # Create LLM
        llm = GeminiLlm(
            llm_id="gemini-2.5-flash-lite",
            response_type=case.response_type,
            response_enum=case.response_enum,
            include_rationale=case.include_rationale,
            max_retries=self.max_retries,
            default_retry_delay_sec=self.default_retry_delay_sec,
            max_retry_delay_sec=self.max_retry_delay_sec,
        ).build()

        # Make a call to the LLM
        response = llm.completion(llm_input)

        # Extract rationale if requested
        if case.include_rationale:
            if _RATIONALE_SEPARATOR in response:
                response, rationale = response.split(_RATIONALE_SEPARATOR, 1)
                response = response.strip()
                rationale = rationale.strip()
            else:
                rationale = "error"
        else:
            rationale = None

        # Analyze the response
        if case.expected_value is not None:
            if response == case.expected_value:
                # Must match the expected response exactly
                outcome = True
            else:
                # Consider any invalid response as a failed response
                outcome = False
        elif case.expected_min is not None:
            try:
                numeric_response = float(response)
                if FloatUtil.more_or_equal(numeric_response, case.expected_min):
                    outcome = True
                else:
                    outcome = False
            except ValueError:
                # Consider not a number as a failed response
                outcome = False
        else:
            raise RuntimeError("Both expected_value and expected_min are None.")

        result = HackathonTrial(
            experiment=self.get_key(),
            param=condition,
            outcome=outcome,
            response=response,
            rationale=rationale,
            mitigation_prompt=self.mitigation_prompt,
            bias_prompt=case.bias_prompt,
            business_prompt=case.business_prompt,
            llm_input=llm_input,
            expected_value=case.expected_value,
            expected_min=case.expected_min,
            response_type=case.response_type,
            response_enum=case.response_enum,
            include_rationale=case.include_rationale,
        ).build()
        return result
