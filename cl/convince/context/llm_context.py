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
from cl.runtime.context.extension_context import ExtensionContext
from cl.runtime.parsers.locale_key import LocaleKey
from cl.runtime.records.dataclasses_extensions import missing
from cl.convince.llms.llm_key import LlmKey
from cl.convince.settings.llm_settings import LlmSettings


@dataclass(slots=True, kw_only=True)
class LlmContext(ExtensionContext):
    """LLM defaults."""

    locale: LocaleKey = missing()
    """Default locale for LLM completions only (this has no effect on the UI or the data file format)."""

    full_llm: LlmKey = missing()
    """Default full LLM."""

    mini_llm: LlmKey = missing()
    """Default mini LLM."""

    @classmethod
    def get_base_type(cls) -> Type:
        """Return base class of this extension category even if called from a derived class, do not use 'return cls'."""
        return LlmContext

    @classmethod
    def create_default(cls) -> Self:
        """Create default extension instance, this method will be called for the class returned by 'get_base_type'."""
        return LlmContext()

    def init(self) -> Self:
        """Similar to __init__ but can use fields set after construction, return self to enable method chaining."""

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
