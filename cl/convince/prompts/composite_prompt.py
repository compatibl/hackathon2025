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
from enum import IntEnum
from cl.runtime.file.file_data import FileData
from cl.convince.prompts.prompt import Prompt


class Role(IntEnum):
    """Prompt element role."""

    SYSTEM = 1
    """System message."""

    USER = 2
    """User message."""

    ASSISTANT = 3
    """Assistant message."""


@dataclass(slots=True, kw_only=True)
class BasePromptElement:
    """Element of CompositePrompt."""

    role: Role
    """Role for an llm request."""


@dataclass(slots=True, kw_only=True)
class PromptTextElement(BasePromptElement):
    """Text element of CompositePrompt."""

    text: str | None = None
    """Text content."""


@dataclass(slots=True, kw_only=True)
class PromptFileElement(BasePromptElement):
    """Image element of CompositePrompt."""

    content: FileData | None = None
    """File content."""


@dataclass(slots=True, kw_only=True)
class CompositePrompt(Prompt):
    """
    LLM prompt composed of several elements.
    To be rendered into a query specifically inside a llm instance.
    """

    elements: list[BasePromptElement]
    """Prompt's elements."""
