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

import os
from dataclasses import dataclass
from typing import Tuple
from typing_extensions import Self
from cl.runtime.exceptions.error_util import ErrorUtil
from cl.runtime.settings.settings import Settings


@dataclass(slots=True, kw_only=True)
class ConvinceSettings(Settings):
    """Locale and related conventions."""

    locale: str | None = None
    """Default locale for AI in BCP 47 language-country format, for example en-US (has no effect on the front end)."""

    load_completions_from_csv: bool | None = None
    """Completions are loaded from CSV files by default, use this field to change."""

    save_completions_to_csv: bool | None = None
    """Completions are saved to CSV files by default on Windows only, use this field to change."""

    _language: str | None = None
    """Two-letter lowercase language code for AI applications, no effect on front end."""

    _country: str | None = None
    """Two-letter UPPERCASE country code (not region) for AI applications, no effect on front end."""

    def init(self) -> Self:
        """Similar to __init__ but can use fields set after construction, return self to enable method chaining."""
        # Set default locale
        if self.locale is None:
            self.locale = "en-US"

        # Load completions from a local file unless turned off explicitly
        if self.load_completions_from_csv is None:
            self.load_completions_from_csv = True

        # Save completions to a local file on Windows only
        if self.save_completions_to_csv is None:
            self.save_completions_to_csv = os.name == "nt"

        # Validate locale and get language and region
        language, country = self.parse_locale(self.locale)

        # Assign language and country fields
        self._language = language
        self._country = country

        # Return self to enable method chaining
        return self

    def get_language(self) -> str:
        """Two-letter lowercase language code."""
        return self._language

    def get_country(self) -> str:
        """Two-letter UPPERCASE country code (not region)."""
        return self._country

    @classmethod
    def parse_locale(cls, locale: str) -> Tuple[str, str]:
        """Locale is in BCP 47 language-country format, for example en-US (second token must be country, not region)."""
        locale_tokens = locale.split("-")
        format_msg = "  - Locale not in BCP 47 ll-CC format where ll is language and CC is country, for example en-US"
        if len(locale_tokens) != 2:
            raise ErrorUtil.value_error(
                locale,
                details=f"{format_msg}\n  - It has {len(locale_tokens)} dash-delimited tokens instead of 2",
                value_name="locale",
                data_type=ConvinceSettings,
            )
        if not len(language := locale_tokens[0]) == 2 and language.islower():
            raise ErrorUtil.value_error(
                locale,
                details=f"{format_msg}\n  - Its first part must be a two-letter lowercase language code",
                value_name="locale",
                data_type=ConvinceSettings,
            )
        if not len(country := locale_tokens[1]) == 2 and country.isupper():
            raise ErrorUtil.value_error(
                locale,
                details=f"{format_msg}\n  - Its second part must be a two-letter UPPERCASE country code (not region)",
                value_name="locale",
                data_type=ConvinceSettings,
            )

        return language, country

    @classmethod
    def get_prefix(cls) -> str:
        return "convince"
