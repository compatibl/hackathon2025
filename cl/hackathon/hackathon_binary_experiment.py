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
from cl.runtime.primitive.timestamp import Timestamp
from cl.runtime.stats.binary_experiment import BinaryExperiment
from cl.runtime.stats.binary_trial import BinaryTrial
from cl.runtime.stats.condition_key import ConditionKey
from cl.convince.llms.llama.fireworks.fireworks_llama_llm import FireworksLlamaLlm
from cl.hackathon.hackathon_condition import HackathonCondition


@dataclass(slots=True, kw_only=True)
class HackathonBinaryExperiment(BinaryExperiment):
    """Trade entry experiment."""

    def create_trial(self, condition: ConditionKey) -> BinaryTrial:
        """
        Create and return a new trial record with actual and (if applicable) expected fields
        without checking if max_trials has already been reached.
        """

        condition_obj = active(DataSource).load_one(condition, cast_to=HackathonCondition)
        prompt = (
            f"{Timestamp.create()}: {condition_obj.preamble}\n\n"
            f"{condition_obj.query}\n\n"
            f"Respond with yes or no in lowercase and output no other text.\n"
            f"Any other output or any additional text will be considered a failed response.\n"
        )

        llm = FireworksLlamaLlm(llm_id="llama4-scout-instruct-basic").build()
        response = llm.completion(prompt)
        if response == condition_obj.expected_response:
            # Must match the expected response exactly
            outcome = True
        else:
            # Consider any invalid response as a failed response
            outcome = False

        result = BinaryTrial(
            experiment=self.get_key(),
            condition=condition,
            outcome=outcome,
        ).build()
        return result
