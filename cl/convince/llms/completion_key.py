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
from cl.runtime.log.exceptions.user_error import UserError
from cl.runtime.records.for_dataclasses.dataclass_mixin import DataclassMixin
from cl.runtime.records.for_dataclasses.extensions import required
from cl.runtime.records.key_mixin import KeyMixin
from cl.runtime.records.protocols import is_key_type


@dataclass(slots=True)
class CompletionKey(DataclassMixin, KeyMixin):
    """Record of a previous LLM completion used to avoid making repeated LLM calls for the same query and trial."""

    completion_id: str = required()
    """Unique completion identifier is a hash of completion parameters."""

    @classmethod
    def get_key_type(cls) -> type[KeyMixin]:
        return CompletionKey

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""
        # Validate completion_id inside a key but not inside a record where it will be set based on other fields
        # TODO: Use standard helper classes
        if is_key_type(type(self)):
            if "(" not in self.completion_id or ")" not in self.completion_id:
                raise UserError(
                    f"""
The field 'CompletionId' does not conform to one of the valid formats:
Format 1: digest (llm, trial)
Format 2: digest (llm, trial, md5)
CompletionId: {self.completion_id}
"""
                )
