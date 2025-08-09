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
from cl.runtime.contexts.context_manager import active_or_default
from cl.convince.contexts.llm_context import LlmContext
from cl.convince.settings.llm_settings import LlmSettings


def test_llm_context():
    """Smoke test."""

    settings = LlmSettings.instance()
    assert active_or_default(LlmContext).locale.locale_id == settings.llm_locale
    assert active_or_default(LlmContext).full_llm.llm_id == settings.llm_full
    assert active_or_default(LlmContext).mini_llm.llm_id == settings.llm_mini


if __name__ == "__main__":
    pytest.main([__file__])
