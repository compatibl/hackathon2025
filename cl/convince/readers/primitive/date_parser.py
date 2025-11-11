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
import dateparser
from cl.runtime.exceptions.error_util import ErrorUtil
from cl.convince.readers.primitive.date_entry import DateEntry
from cl.convince.readers.primitive.date_reader import DateReader


@dataclass(slots=True, kw_only=True)
class DateParser(DateReader):
    """Rules-based date reader."""

    def read(self, text: str) -> DateEntry:

        result = DateEntry(text=text)

        # TODO: Check if the entry already exists in DB

        # Parse date
        if date := dateparser.parse(text):
            result.date = date
        else:
            raise ErrorUtil.value_error(
                text,
                details=f"Text '{text}' cannot be converted to a date.",
                value_name="text",
                method_name="generate",
                data_type=DateParser,
            )

        return result.build()
