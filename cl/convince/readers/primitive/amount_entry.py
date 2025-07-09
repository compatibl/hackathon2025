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
from cl.convince.readers.primitive.amount_entry_key import AmountEntryKey
from cl.convince.readers.primitive.number_entry_key import NumberEntryKey
from cl.convince.readers.static.ccy_entry_key import CcyEntryKey


@dataclass(slots=True, kw_only=True)
class AmountEntry(AmountEntryKey, RecordMixin):
    """Entry for an amount with or without currency specification."""

    value: NumberEntryKey = required()
    """Entry for the numerical value of the amount inclusive of units multiplier."""

    ccy: CcyEntryKey | None = None
    """Optional entry for the currency if specified along with the amount."""

    def get_key(self) -> AmountEntryKey:
        return AmountEntryKey(text=self.text).build()
