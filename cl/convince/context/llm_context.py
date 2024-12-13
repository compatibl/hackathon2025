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
from typing_extensions import Self

from cl.convince.llms.llm import Llm
from cl.convince.llms.llm_key import LlmKey
from cl.convince.settings.llm_settings import LlmSettings
from cl.runtime import Context
from cl.runtime.context.base_context import BaseContext
from cl.runtime.parsers.locale import Locale
from cl.runtime.parsers.locale_key import LocaleKey
from cl.runtime.records.dataclasses_extensions import missing


@dataclass(slots=True, kw_only=True)
class LlmContext(BaseContext):
    """LLM settings in the Convince package."""

    locale: Locale = missing()
    """Default locale for LLM completions only (this has no effect on the UI or the data file format)."""

    full_llm: Llm = missing()
    """Default full LLM."""

    mini_llm: Llm = missing()
    """Default mini LLM."""

    def init(self) -> Self:
        """Similar to __init__ but can use fields set after construction, return self to enable method chaining."""

        # Initialize empty fields from settings only for the root context
        if self._is_root:
            settings = LlmSettings.instance()
            context = Context.current()
            if self.locale is None:
                # Try loading the locale from storage
                locale = context.load_one(Locale, LocaleKey(locale_id=settings.locale), is_record_optional=True)
                if locale is None:
                    # Create with default settings if does not exist
                    locale = Locale(locale_id=settings.locale).init_all()
                self.locale = locale
            if self.full_llm is None:
                self.full_llm = context.load_one(Llm, LlmKey(llm_id=settings.full))
            if self.mini_llm is None:
                self.mini_llm = context.load_one(Llm, LlmKey(llm_id=settings.mini))

        # Freeze to prevent further modifications (ok to call even if already frozen)
        self.freeze()

        # Return self to enable method chaining
        return self

    @classmethod
    def _create(cls):
        """Create root instance of the extension from settings."""
