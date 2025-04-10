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
from cl.runtime.contexts.context import Context
from cl.runtime.parsers.locale_key import LocaleKey
from cl.runtime.records.for_dataclasses.extensions import required
from cl.convince.llms.llm_key import LlmKey
from cl.convince.settings.llm_settings import LlmSettings


@dataclass(slots=True, kw_only=True)
class LlmContext(Context):
    """LLM defaults."""

    locale: LocaleKey = required()
    """Default locale for LLM completions only (this has no effect on the UI or the data file format)."""

    full_llm: LlmKey = required()
    """Default full LLM."""

    mini_llm: LlmKey = required()
    """Default mini LLM."""

    @classmethod
    def get_context_type(cls) -> str:
        return "LlmContext"

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""

        # Initialize empty fields in this context instance from the current context instance or settings,
        # except when self is already the current context
        if self.locale is None:
            self.locale = self.get_locale_or_none()
        if self.full_llm is None:
            self.full_llm = self.get_full_llm_or_none()
        if self.mini_llm is None:
            self.mini_llm = self.get_mini_llm_or_none()

    @classmethod
    def get_locale(cls) -> LocaleKey:
        """Default locale for LLM completions only (this has no effect on the UI or the data file format)."""
        if (result := cls.get_locale_or_none()) is not None:
            return result
        else:
            raise RuntimeError("LLM locale is not specified in LLmContext or LlmSettings.")

    @classmethod
    def get_locale_or_none(cls) -> LocaleKey | None:
        """Default locale for LLM completions only (this has no effect on the UI or the data file format)."""
        if (context := cls.current_or_none()) is not None and context.locale is not None:
            # Use the value from the current context if not None
            return context.locale
        elif (settings := LlmSettings.instance()).locale is not None:
            # Otherwise use the value from settings if not None
            return LocaleKey(locale_id=settings.locale)
        else:
            # If neither is defined, return None
            return None

    @classmethod
    def get_full_llm(cls) -> LlmKey:
        """Default full LLM."""
        if (result := cls.get_full_llm_or_none()) is not None:
            return result
        else:
            # If neither is defined, error message
            raise RuntimeError("Full LLM is not specified in LLmContext or LlmSettings.")

    @classmethod
    def get_full_llm_or_none(cls) -> LlmKey | None:
        """Default full LLM."""
        if (context := cls.current_or_none()) is not None and context.full_llm is not None:
            # Use the value from the current context if not None
            return context.full_llm
        elif (settings := LlmSettings.instance()).full is not None:
            # Otherwise use the value from settings if not None
            return LlmKey(llm_id=settings.full).build()
        else:
            # If neither is defined, return None
            return None

    @classmethod
    def get_mini_llm(cls) -> LlmKey:
        """Default mini LLM."""
        if (result := cls.get_mini_llm_or_none()) is not None:
            return result
        else:
            # If neither is defined, error message
            raise RuntimeError("Mini LLM is not specified in LLmContext or LlmSettings.")

    @classmethod
    def get_mini_llm_or_none(cls) -> LlmKey | None:
        """Default mini LLM."""
        if (context := cls.current_or_none()) is not None and context.mini_llm is not None:
            # Use the value from the current context if not None
            return context.mini_llm
        elif (settings := LlmSettings.instance()).mini is not None:
            # Otherwise use the value from settings if not None
            return LlmKey(llm_id=settings.mini)
        else:
            # If neither is defined, return None
            return None
