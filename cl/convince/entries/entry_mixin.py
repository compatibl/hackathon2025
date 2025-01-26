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

from cl.runtime.contexts.db_context import DbContext
from cl.runtime.log.exceptions.user_error import UserError
from cl.runtime.primitive.bool_util import BoolUtil
from cl.runtime.primitive.string_util import StringUtil
from cl.runtime.records.type_util import TypeUtil
from cl.convince.contexts.llm_context import LlmContext


class EntryMixin:
    """Contains description, body and supporting data of user entry along with the entry processing result."""

    def init(self) -> None:
        """Generate entry_id from text, locale and data fields."""

        # Check text
        if StringUtil.is_empty(self.text):
            raise UserError(f"Empty 'text' field in {TypeUtil.name(self)}.")

        # If locale is None, get it from LlmContext
        if self.locale is None:
            self.locale = LlmContext.get_locale()

        # Convert field types if necessary
        if self.verified is not None and isinstance(self.verified, str):
            self.verified = BoolUtil.parse_or_none(self.verified, name="verified")

        # Generate digest if multiline or more than 80 characters
        self.entry_id = StringUtil.digest(
            self.text,
            text_params=(self.locale.locale_id,),
            hash_params=(self.data,),
        )

    def get_text(self) -> str:
        """Get the complete text of the entry."""
        # TODO: Support data
        if self.data is not None:
            raise RuntimeError("Entry 'data' field is not yet supported.")
        result = self.text
        return result

    # TODO: Restore abstract when implemented for all entries
    def run_generate(self) -> None:
        """Generate or regenerate the proposed value."""
        raise UserError(f"Propose handler is not yet implemented for {TypeUtil.name(self)}.")

    def run_reset(self) -> None:
        """Clear all output fields and the verification flag."""
        if self.verified:
            raise UserError(
                f"Entry {self.entry_id} is marked as verified, run Unmark Verified before running Reset. "
                f"This is a safety feature to prevent overwriting verified entries."
            )

        # Create a record of the same type but copy the base class fields except verified
        record_type = type(self)
        result = record_type(text=self.text, locale=self.locale, data=self.data)  # noqa
        result.build()

        # Save to replace the current record
        DbContext.save_one(result)

    def run_mark_verified(self) -> None:
        """Mark verified."""
        self.verified = True
        DbContext.save_one(self)

    def run_unmark_verified(self) -> None:
        """Unmark verified."""
        self.verified = False
        DbContext.save_one(self)
