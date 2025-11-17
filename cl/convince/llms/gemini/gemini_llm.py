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

import logging
import re
import time
from dataclasses import dataclass
from typing import Any
from google import genai  # noqa
from google.genai.errors import ClientError
from cl.runtime.contexts.context_manager import active_or_none
from cl.runtime.contexts.user_secrets import UserSecrets
from cl.runtime.records.typename import typenameof
from cl.convince.llms.llm import Llm
from cl.convince.llms.llm_request_telemetry import LlmRequestTelemetry
from cl.convince.settings.gemini_settings import GeminiSettings

_logger = logging.getLogger(__name__)

_RATIONALE_SEPARATOR = "\n=====RATIONALE=====\n"


@dataclass(slots=True, kw_only=True)
class GeminiLlm(Llm):
    """Implements Gemini LLM API."""

    model_name: str | None = None
    """Model name in Gemini format including version if any, defaults to 'llm_id'."""

    response_type: str | None = None
    """Response type from PRIMITIVE_TYPES, can omit if response_enum is set. """

    response_enum: list[str] | None = None
    """Response enumeration, the model will not output values outside this set."""

    include_rationale: bool | None = None
    """If True, rationale for the response is requested along with the response."""

    max_retries: int = 10
    """Maximum number of retries for throttled requests."""

    default_retry_delay_sec: int = 2
    """Initial retry delay for throttled requests when recommended delay cannot be extracted from the message."""

    max_retry_delay_sec: int = 120
    """Limit retry delay for throttled requests to this value in seconds when set by rule or extracted from message."""

    _structured_output: bool = False
    """Indicates whether structured output is requested."""

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""

        if self.response_type is None:
            # Default response_type is string
            self.response_type = "str"
        elif self.response_type == "str":
            pass
        elif self.response_type in ("int", "float"):
            if self.response_enum is not None:
                raise RuntimeError(
                    f"{type(self).__name__}.response_enum must be None for response_type '{self.response_type}'."
                )

        # Determine if structured output should be used
        self._structured_output = (
            self.response_type != "str" or self.response_enum is not None or self.include_rationale
        )

    def uncached_completion(self, request_id: str, query: str) -> Any:
        """Perform completion without CompletionCache lookup, call completion instead."""

        # Prefix a unique RequestID to the model for audit log purposes and
        # to stop model provider from caching the results
        query_with_request_id = f"RequestID: {request_id}\n\n{query}"

        # Model name may be different from llm_id
        model_name = self.model_name if self.model_name is not None else self.llm_id

        if not self._structured_output:
            # Do not specify
            response_mime_type = None
            response_schema = None
        else:
            response_mime_type = "application/json"

            if self.response_type == "str":
                gemini_response_type = genai.types.Type.STRING
            elif self.response_type == "int":
                gemini_response_type = genai.types.Type.INTEGER
            elif self.response_type == "float":
                gemini_response_type = genai.types.Type.NUMBER
            else:
                raise RuntimeError(f"Unsupported {typenameof(self)}.response_type={self.response_type}.")

            if self.response_enum is not None:
                properties = {
                    "response": genai.types.Schema(type=gemini_response_type, enum=list(self.response_enum)),
                }
            else:
                properties = {
                    "response": genai.types.Schema(
                        type=gemini_response_type,
                    ),
                }
            required = ["response"]

            # Add rationale if requested
            if self.include_rationale:
                properties["rationale"] = genai.types.Schema(
                    type=genai.types.Type.STRING,
                )
                required.append("rationale")

            # Full response schema
            response_schema = genai.types.Schema(
                type=genai.types.Type.OBJECT,
                required=required,
                properties=properties,
            )

        # Configuration settings for the model
        generation_config = genai.types.GenerateContentConfig(
            thinking_config=genai.types.ThinkingConfig(
                thinking_budget=0,
                include_thoughts=False,
            ),
            response_mime_type=response_mime_type,
            response_schema=response_schema,
        )

        # Get client
        client = self._get_client()

        # Retry the specified number of times
        retry_delay = None
        response = None
        for _ in range(self.max_retries):

            # Sleep retry delay if set
            if retry_delay is not None:
                _logger.info(f"LLM request failed due to throttling, retrying with delay {retry_delay}s.")
                time.sleep(retry_delay)

            try:
                # Run LLM request using Client
                response = client.models.generate_content(
                    model=model_name,
                    config=generation_config,
                    contents=genai.types.Content(
                        role="user",
                        parts=[
                            genai.types.Part.from_text(text=query_with_request_id),
                        ],
                    ),
                )
                _logger.info("LLM request completed successfully.", extra={"save_to_db": False})

                # Stop retry cycle if request completed successfully
                break
            except ClientError as e:

                # Error code 429 is a throttling error, raise if other errors
                if e.code != (retry_error_code := 429):
                    raise

                # Try to get retry delay from Exception message
                retry_delay_from_error = None
                if match := re.search(r"retry in ([0-9]*\.?[0-9]+)s", e.message):
                    # Detected retry delay in seconds in the error message
                    retry_delay_from_error = float(match.group(1))
                elif match := re.search(r"retry in ([0-9]*\.?[0-9]+)ms", e.message):
                    # Detected retry delay in milliseconds in the error message
                    retry_delay_from_error = float(match.group(1)) / 1000.0

                if retry_delay_from_error is not None:
                    # Report retry delay from the error
                    _logger.info(
                        f"Gemini returned error {retry_error_code} with retry delay {retry_delay_from_error}s.\n"
                        f"Error message: {e.message}.\n",
                        extra={"save_to_db": False},
                    )
                else:
                    _logger.info(
                        f"Gemini returned error {retry_error_code} but retry delay could not be retrieved.\n"
                        f"Error message: {e.message}.\n",
                        extra={"save_to_db": False},
                    )

                if retry_delay_from_error is not None:
                    # Use retry delay from the error if available, ignore the previous value in this case
                    retry_delay = retry_delay_from_error
                elif retry_delay is not None:
                    # Increase by 50% of previous value if already set
                    retry_delay = 1.5 * retry_delay
                else:
                    # Use default retry delay if not yet set
                    retry_delay = self.default_retry_delay_sec

                # Limit the range irrespective of how it was obtained
                if retry_delay is not None:
                    if retry_delay < 0.01:
                        # Use default if less than 10ms
                        retry_delay = self.default_retry_delay_sec
                    elif retry_delay > self.max_retry_delay_sec:
                        # Use max to limit in case of an extraction error or too high due to incrementing by rule
                        retry_delay = self.max_retry_delay_sec

        # Raise error if LLM request is not completed after max_retries attempts
        if response is None:
            raise RuntimeError(f"LLM completion is failed after {self.max_retries} retries.")
        return response

    def extract_completion_usage_info(self, response: Any) -> LlmRequestTelemetry:
        """Extract usage from the completion."""
        return LlmRequestTelemetry(
            input_tokens=response.usage_metadata.prompt_token_count,
            output_tokens=response.usage_metadata.candidates_token_count,
            total_tokens=response.usage_metadata.total_token_count,
        )

    def extract_text_from_completion(self, response: Any) -> str:
        """Extract text from the completion."""
        if self._structured_output:
            # Structured output is requested, get result from the parsed response
            if isinstance(response.parsed, dict):
                # Use a custom separator to return two values if rationale is requested
                if self.include_rationale:
                    result = (
                        str(response.parsed.get("response", "error"))
                        + _RATIONALE_SEPARATOR
                        + str(response.parsed.get("rationale", "error"))
                    )
                else:
                    result = str(response.parsed.get("response", "error"))
            else:
                # Return "error" if response is not a dict
                result = "error"
            return result
        else:
            # Structured output not requested
            result = str(response.text)
            return result

    @classmethod
    def _get_client(cls) -> genai.Client:
        """Instantiate Gemini Client."""

        # Check if UserSecrets is active and specifies GEMINI_API_KEY
        if (user_secrets := active_or_none(UserSecrets)) is not None:
            api_key_from_user_secrets = user_secrets.decrypt_secret("GEMINI_API_KEY")
        else:
            api_key_from_user_secrets = None

        # Check if Dynaconf specifies GEMINI_API_KEY
        api_key_from_dynaconf = GeminiSettings.instance().gemini_api_key

        if api_key_from_user_secrets is not None:
            _logger.debug("Using GEMINI_API_KEY from UserSecrets.", extra={"save_to_db": False})
            api_key = api_key_from_user_secrets
        elif api_key_from_dynaconf is not None:
            _logger.debug("Using GEMINI_API_KEY from Dynaconf.", extra={"save_to_db": False})
            api_key = api_key_from_dynaconf
        else:
            raise RuntimeError("GEMINI_API_KEY is not specified in either UserSecrets or Dynaconf.")

        client = genai.Client(api_key=api_key)
        return client
