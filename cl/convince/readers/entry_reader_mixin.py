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
from typing import Generic
from typing import List
from typing import TypeVar
from cl.runtime import RecordMixin
from cl.runtime.contexts.db_context import DbContext
from cl.runtime.records.generic_util import GenericUtil
from cl.runtime.records.protocols import TKey

TEntry = TypeVar("TEntry")
"""Generic type parameter for an entry."""


class EntryReaderMixin(Generic[TKey, TEntry], RecordMixin, ABC):
    """Generic mixin for types that read text and return an entry record."""

    __slots__ = ()
    """To prevent creation of __dict__ in derived types."""

    @classmethod
    def get_entry_type(cls):
        """The actual type passed as TEntry argument to the generic definition of this class or its descendants."""
        # Second argument of EntryReaderMixin[TKey, TEntry]
        return GenericUtil.get_bound_type(cls, TEntry)

    @abstractmethod
    def read(self, text: str) -> TEntry:
        """Return an entry containing the input text and the data extracted from it."""

    def run_read_one(self, text: str) -> None:
        """Save the entry record obtained from the specified entry text."""
        result = self.read(text)
        DbContext.save_one(result)

    def run_read_many(self, texts: List[str]) -> None:
        """Save entry records obtained from the specified entry texts."""
        results = [self.read(text) for text in texts]  # TODO: Implement via workflow
        DbContext.save_many(results)
