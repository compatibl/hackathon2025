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
from cl.runtime import RecordMixin
from cl.runtime.contexts.context_manager import active
from cl.runtime.db.data_source import DataSource
from cl.convince.readers.entry_mixin import EntryMixin


class EntryReaderMixin(RecordMixin, ABC):
    """Mixin for types that read text and return an entry record."""

    __slots__ = ()
    """To prevent creation of __dict__ in derived types."""

    @abstractmethod
    def read(self, text: str) -> EntryMixin:
        """Return an entry containing the input text and the data extracted from it."""

    def run_read_one(self, text: str) -> None:
        """Save the entry record obtained from the specified entry text."""
        result = self.read(text)
        active(DataSource).save_one(result)

    def run_read_many(self, texts: list[str]) -> None:
        """Save entry records obtained from the specified entry texts."""
        results = [self.read(text) for text in texts]  # TODO: Implement via workflow
        active(DataSource).save_many(results)
