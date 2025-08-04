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
from cl.runtime.contexts.data_context import DataContext
from cl.runtime.records.for_dataclasses.extensions import required
from cl.convince.data.static.ccy import Ccy
from cl.convince.data.static.ccy_key import CcyKey
from cl.convince.readers.static.ccy_entry import CcyEntry
from cl.convince.readers.static.ccy_reader import CcyReader
from cl.convince.retrievers.multiple_choice_retriever import MultipleChoiceRetriever
from cl.convince.retrievers.retriever_key import RetrieverKey

_CURRENCY_ISO_CODE = "Currency code in strict ISO-4217 format of three uppercase letters, no variations allowed."
"""Parameter description for the currency ISO-4217 code."""


@dataclass(slots=True, kw_only=True)
class CcyParser(CcyReader):
    """Selects ISO-4217 currency code from a list of valid choices."""

    retriever: RetrieverKey = required()
    """Retriever to perform currency retrieval from the entry text."""

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""
        # Use retriever with default parameters if not specified
        if self.retriever is None:
            self.retriever = MultipleChoiceRetriever().build()

    def read(self, text: str) -> CcyEntry:

        # Load objects from storage if specified as a key
        retriever = DataContext.load_one(self.retriever, cast_to=MultipleChoiceRetriever)

        # Get the list of all currency codes
        ccy_keys = DataContext.load_type(CcyKey, cast_to=Ccy)
        iso_codes = [ccy.iso_code for ccy in ccy_keys]

        # Retrieve ISO code
        retrieval = retriever.retrieve(
            input_text=text,
            param_description=_CURRENCY_ISO_CODE,
            valid_choices=iso_codes,
        )

        # Currency key is the result
        ccy = CcyKey(iso_code=retrieval.param_value).build()

        # Build and return a populated entry
        result = CcyEntry()
        result.text = text
        result.ccy = ccy
        return result.build()
