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

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from cl.runtime.primitive.timestamp import Timestamp
from cl.runtime.records.record_mixin import RecordMixin
from cl.convince.llms.completion_cache import CompletionCache
from cl.convince.llms.completion_util import CompletionUtil
from cl.convince.llms.llm_key import LlmKey


@dataclass(slots=True, kw_only=True)
class Llm(LlmKey, RecordMixin[LlmKey], ABC):
    """Provides an API for single query and chat completion."""

    _completion_cache: CompletionCache | None = None
    """Completion cache is used to return cached LLM responses."""

    def get_key(self) -> LlmKey:
        return LlmKey(llm_id=self.llm_id)

    def init(self) -> None:
        """Similar to __init__ but can use fields set after construction."""
        self._completion_cache = CompletionCache(channel=self.llm_id).build()

    def completion(self, query: str) -> str:
        """Text-in, text-out single query completion without model-specific tags (uses response caching)."""

        # Get cache key with trial_id, EOL normalization, and stripped leading and trailing whitespace
        query_with_trial_id = CompletionUtil.format_query(query)

        if not self._completion_cache:
            # Initialize completion cache on first use, error message if self is not yet frozen
            self.check_frozen()
            self._completion_cache = CompletionCache(channel=self.llm_id).build()

        # Try to find in completion cache by cache_key, make cloud provider call only if not found
        if (result := self._completion_cache.get(query_with_trial_id)) is None:
            # Request identifier is UUIDv7 timestamp in time-ordered dash-delimited format
            # is used to prevent LLM cloud provider caching and to identify LLM API calls
            # for audit log and error reporting purposes
            request_id = Timestamp.create()

            # Invoke LLM by calling the cloud provider API
            result = self.uncached_completion(request_id, query_with_trial_id)

            # Save the result in cache before returning, request_id is recorded
            # but not taken into account during lookup
            self._completion_cache.add(request_id, query_with_trial_id, result)

        # Remove leading and trailing whitespace and normalize EOL in result
        result = CompletionUtil.format_completion(result)
        return result

    @abstractmethod
    def uncached_completion(self, request_id: str, query: str) -> str:
        """Perform completion without CompletionCache lookup, call completion instead."""
