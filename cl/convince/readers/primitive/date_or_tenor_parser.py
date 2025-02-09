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

import re
from dataclasses import dataclass
from cl.runtime.contexts.db_context import DbContext
from cl.convince.readers.primitive.date_entry import DateEntry
from cl.convince.readers.primitive.date_or_tenor_entry import DateOrTenorEntry
from cl.convince.readers.primitive.date_or_tenor_reader import DateOrTenorReader

_TENOR_RE = re.compile(r"(\d+)([ymwd])")


@dataclass(slots=True, kw_only=True)
class RegexDateOrTenorReader(DateOrTenorReader):
    """Implementation of DateOrTenorReader using regex."""

    def read(self, text: str) -> DateOrTenorEntry:

        # Try to parse as tenor first
        if matches := re.findall(_TENOR_RE, text.lower()):

            matches_dict = {unit: num for num, unit in matches}

            # Set each field based on matches or set to None if not present
            self.years = int(matches_dict.get("y", 0)) or None
            self.months = int(matches_dict.get("m", 0)) or None
            self.weeks = int(matches_dict.get("w", 0)) or None
            self.days = int(matches_dict.get("d", 0)) or None
        else:
            date_reader = DateEntry(text=text).build()
            date_entry.run_generate()
            self.date = date_entry.date

        # Save
        DbContext.save_one(self)
