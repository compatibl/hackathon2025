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
from cl.runtime.log.exceptions.user_error import UserError
from cl.runtime.parsers.locale_key import LocaleKey
from cl.runtime.testing.regression_guard import RegressionGuard
from stubs.cl.convince.entries.stub_entry import StubEntry
from stubs.cl.convince.entries.stub_entry_key import StubEntryKey


def test_init():
    """Test StubEntryKey.create_key method."""

    guard = RegressionGuard()

    # Fields
    locale = LocaleKey(locale_id="en-GB")

    # Check with type and description only
    entry = StubEntry(text="Sample Text", locale=locale).build()
    entry.build()
    guard.write(entry.entry_id)

    # Check with body
    entry = StubEntry(text=" ".join(20 * ["Long Text"]), locale=locale).build()
    entry.build()
    guard.write(entry.entry_id)

    # Check with data
    entry = StubEntry(text="Multiline\nText", locale=locale).build()
    entry.build()
    guard.write(entry.entry_id)

    # Check with both
    entry = StubEntry(text="Sample Text", locale=locale, data="Sample Data").build()
    entry.build()
    guard.write(entry.entry_id)

    # Verify
    guard.verify_all()


def test_check_entry_id():
    """Test StubEntryKey.check_entry_id method."""

    # Valid without hash
    StubEntryKey(entry_id="text (type, en-US)").build()

    # Valid with hash
    StubEntryKey(entry_id="text (type, en-US, 00000000000000000000000000000000)").build()

    # Not valid
    with pytest.raises(UserError):
        StubEntryKey(entry_id="text").build()
    with pytest.raises(UserError):
        StubEntryKey(entry_id="text(").build()
    with pytest.raises(UserError):
        StubEntryKey(entry_id="text)").build()


if __name__ == "__main__":
    pytest.main([__file__])
