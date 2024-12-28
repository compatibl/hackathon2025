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

import pytest
from cl.tradeentry.entries.ccy_entry import CcyEntry
from cl.runtime.log.exceptions.user_error import UserError
from cl.runtime.parsers.locale_key import LocaleKey
from cl.runtime.testing.regression_guard import RegressionGuard
from cl.convince.entries.entry_key import EntryKey
from cl.tradeentry.entries.ccy_expert import CcyExpert
from cl.tradeentry.entries.ccy_expert_key import CcyExpertKey
from cl.tradeentry.entries.multiple_choice_ccy_expert import MultipleChoiceCcyExpert


def test_create_key():
    """Test EntryKey.create_key method."""

    guard = RegressionGuard()

    # Fields
    locale = LocaleKey(locale_id="en-GB")
    expert = CcyExpertKey(expert_id="Sample Expert")

    # Check with type and description only
    entry = CcyEntry(text="Sample Text", locale=locale, expert=expert)
    entry.init_all()
    guard.write(entry.entry_id)

    # Check with body
    entry = CcyEntry(text=" ".join(20 * ["Long Text"]), locale=locale, expert=expert)
    entry.init_all()
    guard.write(entry.entry_id)

    # Check with data
    entry = CcyEntry(text="Multiline\nText", locale=locale, expert=expert)
    entry.init_all()
    guard.write(entry.entry_id)

    # Check with both
    entry = CcyEntry(text="Sample Text", locale=locale, expert=expert, data="Sample Data")
    entry.init_all()
    guard.write(entry.entry_id)

    # Verify
    guard.verify_all()


def test_check_entry_id():
    """Test EntryKey.check_entry_id method."""

    # Valid without hash
    EntryKey(entry_id="text (type, en-US)").init_all()

    # Valid with hash
    EntryKey(entry_id="text (type, en-US, 00000000000000000000000000000000)").init_all()

    # Not valid
    with pytest.raises(UserError):
        EntryKey(entry_id="text").init_all()
    with pytest.raises(UserError):
        EntryKey(entry_id="text(").init_all()
    with pytest.raises(UserError):
        EntryKey(entry_id="text)").init_all()


if __name__ == "__main__":
    pytest.main([__file__])
