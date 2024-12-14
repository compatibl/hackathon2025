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

from cl.convince.context.llm_context import LlmContext
from cl.convince.llms.claude.claude_llm import ClaudeLlm
from cl.convince.llms.gpt.gpt_llm import GptLlm
from cl.convince.llms.llama.llama_llm import LlamaLlm
from cl.convince.llms.llm import Llm
from cl.convince.llms.llm_key import LlmKey
from cl.runtime import Context
from cl.runtime.context.testing_context import TestingContext
from cl.runtime.parsers.locale import Locale
from cl.runtime.parsers.locale_key import LocaleKey
from cl.runtime.primitive.string_util import StringUtil
from cl.convince.settings.llm_settings import LlmSettings
from cl.runtime.settings.preload_settings import PreloadSettings


def test_with_context():
    """Test 'with' clause."""

    with TestingContext():

        # With clause, no fields set
        llm_settings = LlmSettings.instance()
        with LlmContext(allow_root=True):
            llm_context = LlmContext.current()
            assert llm_context.locale.locale_id == llm_settings.locale
            assert llm_context.full_llm.llm_id == llm_settings.full
            assert llm_context.mini_llm.llm_id == llm_settings.mini

        # With clause, all fields set
        locale_param = LocaleKey(locale_id='en-US')
        full_llm_param = LlmKey(llm_id='full_llm')
        mini_llm_param = LlmKey(llm_id='mini_llm')
        with LlmContext(allow_root=True, locale=locale_param, full_llm=full_llm_param, mini_llm=mini_llm_param):
            llm_context = LlmContext.current()
            assert llm_context.locale is locale_param
            assert llm_context.full_llm is full_llm_param
            assert llm_context.mini_llm is mini_llm_param

        # Call 'current' method outside with clause
        with pytest.raises(RuntimeError):
            LlmContext.current()

        # With clause without setting allow_root=True
        with pytest.raises(RuntimeError):
            with LlmContext():
                pass


if __name__ == "__main__":
    pytest.main([__file__])
