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
from cl.runtime import RecordMixin
from cl.runtime.records.for_dataclasses.extensions import required
from cl.convince.data.static.ccy_key import CcyKey
from cl.convince.readers.static.ccy_entry_key import CcyEntryKey


@dataclass(slots=True, kw_only=True)
class CcyEntry(CcyEntryKey, RecordMixin):
    """Maps string description of a currency to the ISO-4217 three-letter currency code."""

    ccy: CcyKey = required()
    """Generated currency key in ISO-4217 format."""

    def get_key(self) -> CcyEntryKey:
        return CcyEntryKey(text=self.text).build()
