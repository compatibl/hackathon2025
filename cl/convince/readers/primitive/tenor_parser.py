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
from cl.tradeentry.readers.date_reader import DateReader
from cl.tradeentry.readers.tenor_entry import TenorEntry
from cl.tradeentry.readers.tenor_reader import TenorReader

_TENOR_RE = re.compile(r"(\d+)([ymwd])")


@dataclass(slots=True, kw_only=True)
class RegexTenorReader(TenorReader):
    """Implementation of TenorReader using regex."""

    def read(self, text: str) -> TenorEntry:

        result = TenorEntry(text=text)

        # Try to parse as tenor first
        if matches := re.findall(_TENOR_RE, text.lower()):

            matches_dict = {unit: num for num, unit in matches}

            # Set each field based on matches or set to None if not present
            result.years = int(matches_dict.get("y", 0)) or None
            result.months = int(matches_dict.get("m", 0)) or None
            result.weeks = int(matches_dict.get("w", 0)) or None
            result.days = int(matches_dict.get("d", 0)) or None
        else:
            raise NotImplementedError()
            date_reader = DateReader(text=text).build()
            date_entry = date_reader.date
            result.run_generate()
            result.date = date_entry.date

        return result.build()
