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
from dataclasses import dataclass
from cl.runtime.log.exceptions.user_error import UserError
from cl.runtime.primitive.string_util import StringUtil
from cl.runtime.records.for_dataclasses.extensions import required
from cl.runtime.records.record_mixin import RecordMixin
from cl.runtime.records.type_util import TypeUtil
from cl.convince.llms.completion_key import CompletionKey
from cl.convince.llms.llm_key import LlmKey


@dataclass(slots=True, kw_only=True)
class CompletionKeyGen(CompletionKey, RecordMixin[CompletionKey], ABC):
    """Provides an API for single query and chat completion, this class is a key generator."""

    llm: LlmKey = required()
    """LLM for which the completion is recorded."""

    query: str = required()
    """Query for which the completion is recorded."""

    def get_key(self) -> CompletionKey:
        return CompletionKey(completion_id=self.completion_id)

    def init(self) -> None:
        """Generate completion_id from llm_id, trial_id and query fields."""

        # Check that all of the fields required to compute completion_id are set
        if self.llm is None:
            raise UserError(f"Empty 'llm' field in {TypeUtil.name(self)}.")
        if StringUtil.is_empty(self.query):
            raise UserError(f"Empty 'query' field in {TypeUtil.name(self)}.")

        # Create a unique identifier using StringUtil.digest, this will
        # add MD5 hash if multiline or more than 80 characters
        self.completion_id = StringUtil.digest(self.query, text_params=(self.llm.llm_id,))
