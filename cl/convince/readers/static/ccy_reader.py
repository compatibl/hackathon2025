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
from cl.convince.readers.entry_reader_mixin import EntryReaderMixin
from cl.convince.readers.static.ccy_entry import CcyEntry
from cl.convince.readers.static.ccy_reader_key import CcyReaderKey


@dataclass(slots=True, kw_only=True)
class CcyReader(CcyReaderKey, EntryReaderMixin[CcyReaderKey, CcyEntry], ABC):
    """Maps string description of a currency to the ISO-4217 three-letter currency code."""

    def get_key(self) -> CcyReaderKey:
        return CcyReaderKey(reader_id=self.reader_id).build()
