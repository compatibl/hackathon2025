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
from google.genai import Client
from google.genai.types import GenerateContentConfig
from cl.runtime.contexts.context_manager import active_or_default
from cl.runtime.contexts.user_context import UserContext
from cl.runtime.log.exceptions.user_error import UserError
from cl.convince.llms.llm import Llm
from cl.convince.settings.google_settings import GoogleSettings


@dataclass(slots=True, kw_only=True)
class GeminiLlm(Llm):
    """Implements Gemini LLM API."""

    model_name: str | None = None
    """Model name in Gemini format including version if any, defaults to 'llm_id'."""

    temperature: float | None = 0.2
    """
    Controls the randomness of the output.
    Values can range from [0.0, 1.0], inclusive. A value closer to 1.0 will produce responses
    that are more varied and creative, while a value closer to 0.0 will typically result
    in more straightforward responses from the model.
    """

    top_p: float | None = None
    """The maximum cumulative probability of tokens to consider when sampling."""

    top_k: int | None = None
    """The maximum number of tokens to consider when sampling."""

    seed: int | None = None
    """Seed used in decoding. If not set, the request uses a randomly generated seed."""

    def uncached_completion(self, request_id: str, query: str) -> str:
        """Perform completion without CompletionCache lookup, call completion instead."""

        # Prefix a unique RequestID to the model for audit log purposes and
        # to stop model provider from caching the results
        query_with_request_id = f"RequestID: {request_id}\n\n{query}"

        model_name = self.model_name if self.model_name is not None else self.llm_id

        # Try loading API key from context.secrets first and then from settings
        api_key = (
            active_or_default(UserContext).decrypt_secret("GOOGLE_API_KEY") or GoogleSettings.instance().google_api_key
        )
        if api_key is None:
            raise UserError("Provide GOOGLE_API_KEY in Account > My Keys (users) or using Dynaconf (developers).")

        # Collect parameters for content generation
        generation_config = GenerateContentConfig(
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            seed=self.seed,
        )
        generation_params = dict(
            model=model_name,
            contents=query,
            config=generation_config,
        )

        # Generate content
        client = Client(api_key=api_key)
        response = client.models.generate_content(**generation_params)

        result = response.text
        return result

    @classmethod
    def create_prompt_from_messages(cls, messages: list[dict]) -> list[dict[str, str]]:
        """
        Having a list of messages in the following format:
        [
            {"role": "system", "content": "System Prompt"},
            {"role": "user", "content": "What is 2 + 2?"},
            {"role": "assistant", "content": "2+2 is equals to 4"},
            {"role": "user", "content": "Answer only with resulting number"},
        ]
        Returns:
        [
            {"role": "system", "parts": [{"text": "System Prompt"}]},
            {"role": "user", "parts": [{"text": "What is 2 + 2?"}]},
            {"role": "assistant", "parts": [{"text": "2+2 is equals to 4"}]},
            {"role": "user", "parts": [{"text": "Answer only with resulting number"}]},
        ]
        """
        return [{"role": message.role.name, "parts": [{"text": message.content}]} for message in messages]
