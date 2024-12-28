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
from typing import Type
from typing_extensions import Self
from cl.runtime.context.base_context import BaseContext
from cl.runtime.parsers.locale_key import LocaleKey
from cl.runtime.records.dataclasses_extensions import missing
from cl.convince.llms.llm_key import LlmKey
from cl.convince.settings.llm_settings import LlmSettings


@dataclass(slots=True, kw_only=True)
class LlmContext(BaseContext):
    """LLM defaults."""

    locale: LocaleKey = missing()
    """Default locale for LLM completions only (this has no effect on the UI or the data file format)."""

    full_llm: LlmKey = missing()
    """Default full LLM."""

    mini_llm: LlmKey = missing()
    """Default mini LLM."""

    @classmethod
    def get_context_type(cls) -> str:
        """
        The lookup of current context for cls will be done using the key returned by cls.get_context_type().

        Notes:
          - Contexts that have different key types are isolated from each other and have independent 'with' clauses.
          - By convention, the returned string is the name of the base class for this context type in PascalCase
        """
        return "LlmContext"

    def __post_init__(self):
        """Set fields to their values in settings if not specified."""

        # Initialize empty fields from settings
        settings = LlmSettings.instance()
        if self.locale is None and settings.locale is not None:
            self.locale = LocaleKey(locale_id=settings.locale)
        if self.full_llm is None and settings.full is not None:
            self.full_llm = LlmKey(llm_id=settings.full)
        if self.mini_llm is None and settings.mini is not None:
            self.mini_llm = LlmKey(llm_id=settings.mini)

        # Return self to enable method chaining
        return self

    @classmethod
    def get_locale(cls) -> LocaleKey:
        """Default locale for LLM completions only (this has no effect on the UI or the data file format)."""
        if (context := cls.current_or_none()) is not None:
            return context.locale
        else:
            settings = LlmSettings.instance()
            return LocaleKey(locale_id=settings.locale)

    @classmethod
    def get_full_llm(cls) -> LlmKey:
        """Default full LLM."""
        if (context := cls.current_or_none()) is not None:
            return context.full_llm
        else:
            settings = LlmSettings.instance()
            return LlmKey(llm_id=settings.full)

    @classmethod
    def get_mini_llm(cls) -> LlmKey:
        """Default mini LLM."""
        if (context := cls.current_or_none()) is not None:
            return context.mini_llm
        else:
            settings = LlmSettings.instance()
            return LlmKey(llm_id=settings.mini)
