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
from cl.runtime.parsers.locale_key import LocaleKey
from cl.runtime.records.data_mixin import DataMixin
from cl.runtime.records.for_dataclasses.extensions import required
from cl.convince.llms.llm_key import LlmKey
from cl.convince.settings.llm_settings import LlmSettings


@dataclass(slots=True, kw_only=True)
class LlmContext(DataMixin):
    """LLM defaults."""

    locale: LocaleKey = required()
    """Default locale for LLM completions only (this has no effect on the UI or the data file format)."""

    full_llm: LlmKey = required()
    """Default full LLM."""

    mini_llm: LlmKey = required()
    """Default mini LLM."""

    @classmethod
    def get_base_type(cls) -> type:
        return LlmContext

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""

        # Initialize empty fields in this context instance from the current context instance or settings,
        # except when self is already the current context
        settings = None
        if self.locale is None:
            settings = settings or LlmSettings.instance()
            if settings.llm_locale is not None:
                self.locale = LocaleKey(locale_id=settings.llm_locale)
            else:
                raise RuntimeError("LLM locale is not specified in LLmContext or LlmSettings.")
        if self.full_llm is None:
            settings = settings or LlmSettings.instance()
            if settings.llm_full is not None:
                self.full_llm = LlmKey(llm_id=settings.llm_full).build()
            else:
                raise RuntimeError("Full LLM is not specified in LLmContext or LlmSettings.")
        if self.mini_llm is None:
            settings = settings or LlmSettings.instance()
            if settings.llm_mini is not None:
                self.mini_llm = LlmKey(llm_id=settings.llm_mini).build()
            else:
                raise RuntimeError("Mini LLM is not specified in LLmContext or LlmSettings.")

