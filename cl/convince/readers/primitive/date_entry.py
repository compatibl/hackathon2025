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

import datetime as dt
from dataclasses import dataclass
from cl.runtime.records.record_mixin import RecordMixin
from cl.runtime.records.for_dataclasses.extensions import required
from cl.convince.readers.primitive.date_entry_key import DateEntryKey


@dataclass(slots=True, kw_only=True)
class DateEntry(DateEntryKey, RecordMixin):
    """Maps a date string to its value taking into account locale conventions and formatting rules."""

    date: dt.date = required()
    """Date specified by the entry."""

    def get_key(self) -> DateEntryKey:
        return DateEntryKey(text=self.text).build()
