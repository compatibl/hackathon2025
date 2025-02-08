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
from cl.runtime.settings.preload_settings import PreloadSettings
from cl.runtime.testing.pytest.pytest_fixtures import pytest_default_db  # noqa
from cl.tradeentry.readers.multiple_choice_ccy_reader import MultipleChoiceCcyReader


def test_multiple_choice_ccy_reader(pytest_default_db):
    """Smoke test."""
    PreloadSettings.instance().save_and_configure()

    reader = MultipleChoiceCcyReader(ccy_reader_id="test").build()
    entry = reader.read("USD")
    assert entry.ccy.iso_code == "USD"


if __name__ == "__main__":
    pytest.main([__file__])
