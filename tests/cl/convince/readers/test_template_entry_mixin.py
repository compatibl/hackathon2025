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
from cl.runtime.qa.pytest.pytest_fixtures import pytest_default_db  # noqa
from cl.runtime.templates.fstring_template_engine import FstringTemplateEngine
from stubs.cl.runtime.templates.stub_template import StubTemplate
from stubs.cl.convince.readers.stub_template_entry import StubTemplateEntry


def test_describe_correction(pytest_default_db):
    """Test EntryMixin."""

    valid_text = "The value is abc"
    invalid_text = "The value is def"
    template_body = "The value is {value}"
    value = "abc"

    # Test valid
    engine = FstringTemplateEngine()
    template = StubTemplate(body=template_body, engine=engine).build()
    entry = StubTemplateEntry(text=valid_text, template=template, value=value).build()
    assert entry.describe_correction() is None

    # Test not valid
    entry = StubTemplateEntry(text=invalid_text, template=template, value=value).build()
    assert entry.describe_correction() == "Diff"  # TODO: Use unified diff


if __name__ == "__main__":
    pytest.main([__file__])
