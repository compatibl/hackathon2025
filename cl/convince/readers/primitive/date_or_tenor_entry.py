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
from cl.runtime.records.record_mixin import RecordMixin
from cl.convince.readers.primitive.date_or_tenor_entry_key import DateOrTenorEntryKey


@dataclass(slots=True, kw_only=True)
class DateOrTenorEntry(DateOrTenorEntryKey, RecordMixin):
    """Maps a date or tenor string to its value taking into account locale conventions and formatting rules."""

    date: str | None = None
    """The only field if specified as a date (output)."""

    years: int | None = None
    """Years component of the time interval (output)."""

    months: int | None = None
    """Months component of the time interval (output)."""

    weeks: int | None = None
    """Weeks component of the time interval (output)."""

    days: int | None = None
    """Days component of the time interval (output)."""

    business_days: int | None = None
    """Business days component of the time interval (output)."""

    def get_key(self) -> DateOrTenorEntryKey:
        return DateOrTenorEntryKey(text=self.text).build()
