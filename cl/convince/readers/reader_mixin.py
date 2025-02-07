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

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic
from typing import List
from typing import TypeVar
from cl.runtime.contexts.db_context import DbContext

TEntry = TypeVar("TEntry")
"""Generic type parameter for a record."""


@dataclass(slots=True, kw_only=True)
class ReaderMixin(Generic[TEntry], ABC):
    """Generic mixin for the reader classes parameterized by the entry type."""

    @abstractmethod
    def read(self, text: str) -> TEntry:
        """Return entry record for the specified entry text."""

    def run_read_one(self, text: str) -> None:
        """Save entry record for the specified entry text."""
        result = self.read(text)
        DbContext.save_one(result)

    def run_read_many(self, texts: List[str]) -> None:
        """Save entry records for the specified entry texts."""
        results = [self.read(text) for text in texts]  # TODO: Implement via workflow
        DbContext.save_many(results)
