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
from cl.runtime.contexts.db_context import DbContext
from cl.runtime.records.for_dataclasses.extensions import required
from stubs.cl.convince.entries.stub_entry_key import StubEntryKey

from typing import Type
from typing import TYPE_CHECKING
from cl.runtime import RecordMixin
from cl.convince.entries.base_entry import BaseEntry
from cl.runtime.records.empty_mixin import EmptyMixin

_FINAL_KEY = StubEntryKey if TYPE_CHECKING else EmptyMixin
"""Add final key type as an additional base only when type checking to avoid multiple inheritance of dataclasses."""


@dataclass(slots=True, kw_only=True)
class StubEntry(BaseEntry, _FINAL_KEY, RecordMixin[StubEntryKey]):
    """Maps currency string specified by the user to the ISO-4217 three-letter currency code."""

    value: str | None = None
    """Value (output)."""

    @classmethod
    def get_key_type(cls) -> Type:
        return StubEntryKey

    def get_key(self) -> StubEntryKey:
        return StubEntryKey(entry_id=self.entry_id)

    def run_generate(self) -> None:
        """Retrieve parameters from this entry and save the resulting entries."""

        # Load expert from storage if specified as a key
        ccy_expert_key = CcyExpertKey(expert_id="Default")  # TODO: Define a method to return default identifier
        ccy_expert = DbContext.load_one(CcyExpert, ccy_expert_key)

        # Populate output fields of self
        ccy_expert.populate(self)

        # Save self to DB
        DbContext.save_one(self)
