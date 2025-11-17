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
from typing import Any
from typing import ClassVar
from openai import OpenAI
from cl.runtime.contexts.context_manager import active_or_default
from cl.runtime.contexts.user_secrets import UserSecrets
from cl.runtime.log.exceptions.user_error import UserError
from cl.runtime.primitive.float_util import FloatUtil
from cl.runtime.records.typename import typename
from cl.convince.llms.llm import Llm
from cl.convince.llms.llm_request_telemetry import LlmRequestTelemetry
from cl.convince.settings.openai_settings import OpenaiSettings


@dataclass(slots=True, kw_only=True)
class GptLlm(Llm):
    """Implements GPT LLM API."""

    model_name: str | None = None
    """Model name in OpenAI format including version if any (optional, defaults to 'llm_id' field of the base class)."""

    temperature: float | None = None
    """Sampling temperature, optimal value and valid range are model-dependent (optional)."""

    base_url: str | None = None
    """
    Base URL inclusive of protocol version for the REST API (optional, passed as 'base_url' to OpenAI SDK).

    Notes:
        Specify this URL for providers other than OpenAI that use OpenAI REST API protocol,
        for example 'https://api.fireworks.ai/inference/v1'.
    """

    api_key_secret_name: str | None = "OPENAI_API_KEY"
    """Secret name for api key. Set None for self-hosted llms."""

    _client: ClassVar[OpenAI] = None
    """OpenAI client instance."""

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""
        if self.temperature is not None:
            if isinstance(self.temperature, float) or isinstance(self.temperature, int):
                self.temperature = float(self.temperature)
                # Compare with tolerance in case it is calculated by a formula
                if FloatUtil.less(self.temperature, 0.0) or FloatUtil.more(self.temperature, 1.0):
                    raise RuntimeError(
                        f"{typename(type(self))} field temperature={self.temperature} "
                        f"is outside the range from 0 to 1."
                    )
                # Ensure that roundoff error does not move it out of range
                self.temperature = min(max(self.temperature, 0.0), 1.0)
            else:
                raise RuntimeError(f"{typename(type(self))} field 'api_base_url' must be None or a number from 0 to 1")

    def uncached_completion(self, request_id: str, query: str) -> Any:
        """Perform completion without CompletionCache lookup, call completion instead."""

        # Prefix a unique RequestID to the model for audit log purposes and
        # to stop model provider from caching the results
        query_with_request_id = f"RequestID: {request_id}\n\n{query}"

        model_name = self.model_name if self.model_name is not None else self.llm_id
        messages = [{"role": "user", "content": query_with_request_id}]

        client = self._get_client()
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=self.temperature,
        )

        return response

    def extract_completion_usage_info(self, response: Any) -> LlmRequestTelemetry:
        """Extract usage from the completion."""
        return LlmRequestTelemetry(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
        )

    def extract_text_from_completion(self, response: Any) -> str:
        """Extract text from the completion."""
        return response.choices[0].message.content

    def _get_client(self) -> OpenAI:
        """Instantiate and cache the OpenAI client instance."""
        cls = type(self)
        if cls._client is None:

            if self.api_key_secret_name:
                # Try loading API key from context.secrets first and then from settings
                api_key = (
                    active_or_default(UserSecrets).decrypt_secret(self.api_key_secret_name)
                    or OpenaiSettings.instance().openai_api_key
                )
                if api_key is None:
                    raise UserError(
                        f"Provide {self.api_key_secret_name} in Account > My Keys (users) or using Dynaconf (developers)."
                    )
            else:
                api_key = "self-hosted"  # required for OpenAI client initialization

            cls._client = OpenAI(
                api_key=api_key,
                base_url=self.base_url,
            )
        return cls._client
