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
from typing_extensions import final
from cl.runtime.parsers.locale import Locale
from cl.runtime.records.for_dataclasses.extensions import required
from cl.runtime.settings.settings import Settings


@dataclass(slots=True, kw_only=True)
@final
class LlmSettings(Settings):
    """LLM settings."""

    llm_type: str = required()
    """Type name of the default LLM instance."""

    llm_id: str = required()
    """Identifier of the default LLM instance."""

    llm_locale: str | None = None
    """
    Locale the default LLM instance is instructed to use in BCP 47 language-country format, for example en-US.
    This applies to LLM completions only and has no effect on the UI or the data file format.
    """


