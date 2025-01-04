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
from cl.runtime.parsers.locale import Locale
from cl.runtime.settings.settings import Settings


@dataclass(slots=True, kw_only=True)
class LlmSettings(Settings):
    """LLM settings in the Convince package."""

    locale: str | None = None
    """
    Locale that LLM is instructed to use in BCP 47 language-country format, for example en-US.
    This applies to LLM completions only and has no effect on the UI or the data file format.
    """

    full: str | None = None
    """String identifier of the full LLM used in the absence of override (ensure the LLM record exists)."""

    mini: str | None = None
    """String identifier of the mini LLM used in the absence of override (ensure the LLM record exists)."""

    @classmethod
    def get_prefix(cls) -> str:
        return "convince_llm"

    def init(self) -> None:
        """Similar to __init__ but can use fields set after construction."""

        # Validate locale format by running init_all for a locale object
        Locale(locale_id=self.locale).init_all()
