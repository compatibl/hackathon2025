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
from cl.runtime.contexts.db_context import DbContext
from cl.runtime.exceptions.error_util import ErrorUtil
from cl.runtime.primitive.float_util import FloatUtil
from cl.runtime.records.for_dataclasses.extensions import required
from cl.convince.retrievers.annotating_retriever import AnnotatingRetriever
from cl.convince.readers.primitive.amount_entry import AmountEntry
from cl.convince.readers.primitive.amount_reader import AmountReader
from cl.convince.readers.static.ccy_reader import CcyReader
from cl.convince.readers.static.ccy_reader_key import CcyReaderKey
from cl.convince.readers.primitive.number_entry_key import NumberEntryKey
from cl.convince.readers.primitive.number_reader import NumberReader

_AMOUNT = """Numerical value of the amount (including possible space, commas and other
decimal point and thousands separators between digits) or its text representation (e.g. 'ten') 
including any scale unit such as  'm' or 'millions', 'b' or 'bn' or 'billions' but excluding any
currency symbols such as '$', 'USD' or 'dollars'.

Ensure you do not include anything other than digits and scale units, even if additional non-digit
symbols such as a currency symbol are not separated by a space from the digits which may happen
especially with the currency amount.

Pay attention to the examples where you initially provided an incorrect answer:

Input: $100m
Your answer: {$100}m
Correct answer: ${100m}

Input: USD 100,000,000
Your answer: USD {100},000,000
Correct answer: USD {100,000,000}
"""

_CURRENCY = """Currency symbol, natural language description or ISO-4217 code.
Semicolon-delimited examples: $; dollar; USD
"""


@dataclass(slots=True, kw_only=True)
class AmountFormat(AmountReader):
    """Basic implementation of AmountReader."""

    number_reader: NumberEntryKey | None = None
    """Reader for the numerical value of the amount inclusive of units multiplier."""

    ccy_reader: CcyReaderKey = required()
    """Reader for the currency if specified along with the amount."""

    def read(self, text: str) -> AmountEntry:

        result = AmountEntry(text=text)

        # Get retriever
        retriever = AnnotatingRetriever(
            retriever_id="AnnotatingRetriever",
        ).build()

        # Currency symbol preprocessing to avoid JSON formatting issues
        # when the LLM attempts to escape the symbol (e.g. \$ or '\$')
        # TODO: Use a configurable list
        text = text.replace("$US", "USD")
        text = text.replace("$", "USD")
        text = text.replace("$CA", "CAD")
        text = text.replace("€", "EUR")

        # Any unverified component will set this field to False
        verified = True

        # Currency description
        currency_description = retriever.retrieve(
            input_text=text,
            param_description=_CURRENCY,
            is_required=False,
        )
        if currency_description is not None:
            # Try to load an existing entry using reverse lookup
            ccy_reader = DbContext.load_one(CcyReader, self.ccy_reader)
            result.ccy = ccy_reader.read(currency_description)

        # Extract the currency if present
        amount_description = retriever.retrieve(
            input_text=text,
            param_description=_AMOUNT,
            is_required=True,
        )
        if amount_description is not None:
            # Try to load an existing entry using reverse lookup
            number_reader = DbContext.load_one(NumberReader, self.number_reader)
            result.value = number_reader.read(amount_description).value

        return result.build()

    @classmethod
    def _parse_and_check_amount(cls, amount_str: str) -> float:
        """Convert to float value if provided as a string, detailed error message if the conversion fails."""
        try:
            # Convert and check the amount
            result = float(amount_str)
            cls._check_amount(result)
            return result
        except Exception as e:  # noqa
            # Rethrow with details
            raise ErrorUtil.value_error(
                amount_str,
                details=f"Conversion of amount to a floating number failed.\n{e}",
                value_name="amount",
                data_type=AmountEntry,
            )

    @classmethod
    def _check_amount(cls, amount: float) -> None:
        """Check numerical value of the amount, detailed error message if the check fails."""
        # Check range with tolerance
        if FloatUtil.less(amount, 0.0):
            raise ErrorUtil.value_error(
                amount,
                details=f"The amount is negative.",
                value_name="amount",
                data_type=AmountEntry,
            )
        elif FloatUtil.less(amount, 1.0):
            raise ErrorUtil.value_error(
                amount,
                details=f"""
The amount is less than one. Choosing the units that require fractional amounts 
is contrary to the capital markets conventions.""",
                value_name="amount",
                data_type=AmountEntry,
            )
