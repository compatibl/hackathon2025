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
from cl.runtime.log.exceptions.user_error import UserError
from cl.runtime.records.for_dataclasses.extensions import required
from cl.runtime.records.key_mixin import KeyMixin

_ISO_RE = re.compile(r"^[A-Z]{3}$")
"""Regex for the ISO-4217 currency code."""


@dataclass(slots=True)
class CcyKey(KeyMixin):
    """Currency recorded using its 3-letter uppercase ISO-4217 code."""

    iso_code: str = required()
    """3-letter uppercase ISO-4217 code for the currency."""

    @classmethod
    def get_key_type(cls) -> type:
        return CcyKey

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""
        if self.iso_code is not None:
            self._check_iso_code_format(self.iso_code)

    @classmethod
    def _check_iso_code_format(cls, iso_code: str) -> None:
        """Check that the currency conforms to ISO-4217 format."""
        if not bool(_ISO_RE.match(iso_code)):
            raise UserError(
                f"Currency identifier {iso_code} does not confirm to the 3-letter uppercase "
                f"ISO-4217 format (for example USD, EUR, GBP, etc.)"
            )
