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

import datetime
from dataclasses import dataclass
from dataclasses import field

from cl.runtime.primitive.datetime_util import DatetimeUtil
from cl.runtime.records.record_mixin import RecordMixin
from cl.convince.llms.llm_request_telemetry_key import LlmRequestTelemetryKey


@dataclass(slots=True, kw_only=True)
class LlmRequestTelemetry(LlmRequestTelemetryKey, RecordMixin):
    """Record for storing usage info for LLM requests."""

    task_id: str = ""
    """ID of the worker's task within which the llm request was executed."""

    input_tokens: int = 0
    """Number of tokens in the input prompt."""

    output_tokens: int = 0
    """Nuber of tokens in the output response."""

    total_tokens: int = 0
    """Total nuber of tokens in the input prompt and in the output response."""

    request_time_sec: float = 0.0
    """Time taken to complete the request in seconds, including sleep and system time."""

    created: datetime.datetime | None = field(default_factory=DatetimeUtil.now)
    """Time when the record was created."""

    def get_key(self) -> LlmRequestTelemetryKey:
        return LlmRequestTelemetryKey(prompt_id=self.prompt_id).build()
