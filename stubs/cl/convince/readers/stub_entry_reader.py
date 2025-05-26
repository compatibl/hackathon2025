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
from cl.convince.readers.entry_reader_mixin import EntryReaderMixin
from stubs.cl.convince.readers.stub_entry import StubEntry
from stubs.cl.convince.readers.stub_entry_reader_key import StubEntryReaderKey


@dataclass(slots=True, kw_only=True)
class StubEntryReader(StubEntryReaderKey, EntryReaderMixin[StubEntryReaderKey, StubEntry]):
    """Stub for EntryReaderMixin."""

    def get_key(self) -> StubEntryReaderKey:
        return StubEntryReaderKey(reader_id=self.reader_id)

    def read(self, text: str) -> StubEntry:
        # Stub, use the last three characters as the value
        value = text[-3:]
        return StubEntry(text=text, value=value)
