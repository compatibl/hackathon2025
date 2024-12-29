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
from typing import Type
from typing_extensions import Self
from cl.runtime.log.exceptions.user_error import UserError
from cl.runtime.records.dataclasses_extensions import required
from cl.runtime.records.key_mixin import KeyMixin
from cl.runtime.records.protocols import is_key

_MD5_HEX_RE = re.compile(r"^[0-9a-f]+$")
"""Regex for MD5 hex."""


@dataclass(slots=True, kw_only=True)
class EntryKey(KeyMixin):
    """Contains description, body and supporting data of user entry along with the entry processing result."""

    entry_id: str = required()
    """Based on record type, description and MD5 hash of body and data if present."""

    @classmethod
    def get_key_type(cls) -> Type:
        return EntryKey

    def init(self) -> Self:
        # Validate entry_id inside a key but not inside a record where it will be set automatically
        if is_key(self):
            if "(" not in self.entry_id or ")" not in self.entry_id:
                raise UserError(
                    f"""
The field 'EntryId' does not conform to one of the valid formats:
Format 1: digest (type, locale)
Format 2: digest (type, locale, md5)
EntryId: {self.entry_id}
"""
                )

        # Return self to enable method chaining
        return self
