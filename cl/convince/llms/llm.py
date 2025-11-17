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

import time
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import Self
from cl.runtime.contexts.context_manager import active
from cl.runtime.contexts.context_manager import active_or_none
from cl.runtime.db.data_source import DataSource
from cl.runtime.log.task_log import TaskLog
from cl.runtime.parsers.locale import Locale
from cl.runtime.parsers.locale_key import LocaleKey
from cl.runtime.parsers.locale_keys import LocaleKeys
from cl.runtime.primitive.timestamp import Timestamp
from cl.runtime.records.for_dataclasses.extensions import required
from cl.runtime.records.key_util import KeyUtil
from cl.runtime.records.record_mixin import RecordMixin
from cl.runtime.schema.type_info import TypeInfo
from cl.convince.llms.completion_cache import CompletionCache
from cl.convince.llms.completion_util import CompletionUtil
from cl.convince.llms.llm_key import LlmKey
from cl.convince.llms.llm_request_telemetry import LlmRequestTelemetry
from cl.convince.prompts.prompt import Prompt
from cl.convince.settings.convince_settings import ConvinceSettings
from cl.convince.settings.llm_settings import LlmSettings


@dataclass(slots=True, kw_only=True)
class Llm(LlmKey, RecordMixin, ABC):
    """Provides an API for single query and chat completion."""

    llm_locale: LocaleKey = required()
    """Locale used by the LLM, may differ from the active locale."""

    _completion_cache: CompletionCache | None = None
    """Completion cache is used to return cached LLM responses."""

    def get_key(self) -> LlmKey:
        return LlmKey(llm_id=self.llm_id).build()

    @classmethod
    def default(cls) -> Self:
        # Default instance based on LlmSettings
        llm_settings = LlmSettings.instance()
        llm_type = TypeInfo.from_type_name(llm_settings.llm_type)
        llm_id = llm_settings.llm_id
        llm_locale = LocaleKey(locale_id=llm_settings.llm_locale).build()
        return llm_type(llm_id=llm_id, llm_locale=llm_locale).build()

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""

        if self.llm_id is None:
            # Default to LlmSettings.llm_id if not specified
            self.llm_id = LlmSettings.instance().llm_id

        if self.llm_locale is None:
            if (llm_settings_locale := LlmSettings.instance().llm_locale) is not None:
                # Try using locale from LlmSettings first
                self.llm_locale = LocaleKey(locale_id=llm_settings_locale)
            elif (active_locale := active_or_none(Locale)) is not None:
                # Otherwise use the active locale
                self.llm_locale = active_locale
            else:
                # Default to en-US if no locale is specified
                self.llm_locale = LocaleKeys.EN_US

        if not KeyUtil.is_equal(self.llm_locale, LocaleKeys.EN_US):
            # TODO: Enable locale other than en-US after the code using LLM locale is added
            raise RuntimeError("LLM locale customization is not yet supported.")

        # Initialize completion cache
        self._completion_cache = CompletionCache(channel=self.llm_id).build()

    def completion(self, query: str | Prompt) -> str:
        """Text-in, text-out single query completion without model-specific tags (uses response caching)."""

        # Get cache key with trial, EOL normalization, and stripped leading and trailing whitespace
        query_create = CompletionUtil.format_query(query)

        cache_key = CompletionCache.create_cache_key(self.llm_id, query)
        if not self._completion_cache:
            # Initialize completion cache on first use, error message if self is not yet frozen
            # to prevent the cache from being out of sync with the object
            self.check_frozen()
            self._completion_cache = CompletionCache(channel=self.llm_id).build()

        # Try to find in completion cache by cache_key, make cloud provider call only if not found
        if (result := self._completion_cache.get(cache_key)) is None:
            # Request identifier is UUIDv7 timestamp in time-ordered dash-delimited format
            # is used to prevent LLM cloud provider caching and to identify LLM API calls
            # for audit log and error reporting purposes
            request_id = Timestamp.create()

            # Invoke LLM by calling the cloud provider API
            result = self.perform_completion(request_id, query_create)

            # Save the result in cache before returning, request_id is recorded
            # but not taken into account during lookup
            self._completion_cache.add(request_id, cache_key, query_create, result)

        # Remove leading and trailing whitespace and normalize EOL in result
        result = CompletionUtil.format_completion(result)
        return result

    def perform_completion(self, request_id: str, query: str | Prompt) -> str:
        """Perform completion without CompletionCache lookup, and collect telemetry, call completion instead."""
        start_time = time.perf_counter_ns()

        response = self.uncached_completion(request_id, query)

        if not ConvinceSettings.instance().convince_disable_telemetry_collection:
            task_log = active_or_none(TaskLog)
            if task_log:
                # Create a telemetry record
                telemetry = self.extract_completion_usage_info(response)
                telemetry.prompt_id = request_id
                telemetry.task_id = task_log.task_run_id
                telemetry.request_time_sec = (time.perf_counter_ns() - start_time) / 1_000_000

                # Save telemetry record to DB
                active(DataSource).insert_one(telemetry.build(), commit=True)

        return self.extract_text_from_completion(response)

    @abstractmethod
    def uncached_completion(self, request_id: str, query: str) -> Any:
        """Perform completion without CompletionCache lookup, call completion instead."""

    @abstractmethod
    def extract_completion_usage_info(self, response: Any) -> LlmRequestTelemetry:
        """Extract usage from the completion."""

    @abstractmethod
    def extract_text_from_completion(self, response: Any) -> str:
        """Extract text from the completion."""
