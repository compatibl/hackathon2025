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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from typing_extensions import Self

from cl.runtime import RecordMixin
from cl.runtime.contexts.db_context import DbContext
from cl.runtime.records.clone_util import CloneUtil
from cl.runtime.records.key_mixin import KeyMixin
from cl.runtime.records.protocols import TKey
from cl.runtime.records.type_util import TypeUtil
from cl.runtime.templates.template_mixin import TemplateMixin


@dataclass(slots=True, kw_only=True)
class EntryMixin(Generic[TKey], RecordMixin[TKey], ABC):
    """
    Optional generic mixin for a text entry with a describe_correction method.
    Declare MyEntry as MyEntry(MyKey, EntryMixin[MyKey]).
    """

    @property
    @abstractmethod
    def text(self) -> str:
        """Full text of the entry."""

    @abstractmethod
    def describe_correction(self) -> str | None:
        """Describe the required correction for AI or return None if the data matches the input text."""

    def run_validate(self) -> None:
        """Error message if the entry does not match validated text."""
        if (correction := self.describe_correction()) is not None:
            # TODO: Also record correction as a log message or a dedicated record
            raise RuntimeError(
                f"Entry validation failed for {TypeUtil.name(self)} with the following message:\n"
                f"{correction}\nText of the entry:\n{self.text}")
