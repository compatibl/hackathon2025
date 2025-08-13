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
from cl.runtime.contexts.context_manager import activate
from cl.convince.llms.llm_draw import LlmDraw
from stubs.cl.runtime import StubDataclass


def test_append_token():
    """Test LlmDraw.add_token method."""

    assert LlmDraw.get_trial() is None
    with activate(LlmDraw.append_token("abc")) as trial_context_1:
        # One token in chain
        assert trial_context_1.trial_chain == ("abc",)
        assert LlmDraw.get_trial() == "abc"
        with activate(LlmDraw.append_token(123)) as trial_context_2:
            # Two tokens in chain
            assert trial_context_2.trial_chain == (
                "abc",
                "123",
            )
            assert LlmDraw.get_trial() == "abc\\123"
        assert trial_context_1.trial_chain == ("abc",)
        assert LlmDraw.get_trial() == "abc"
        with activate(LlmDraw.append_token(None)) as trial_context_3:
            # One token in chain, None is ignored
            assert trial_context_3.trial_chain == ("abc",)
            assert LlmDraw.get_trial() == "abc"


def test_exceptions():
    """Test LlmDraw exceptions."""

    with pytest.raises(RuntimeError, match="A LlmDraw must be one of the following primitive classes"):
        # Not a primitive type
        LlmDraw.append_token(StubDataclass())
    with pytest.raises(RuntimeError, match="empty string"):
        # Empty string
        LlmDraw.append_token("")
    with pytest.raises(RuntimeError, match="newline"):
        # Contains newline
        LlmDraw.append_token("\n")
    with pytest.raises(RuntimeError, match="backslash"):
        # Contains backslash
        LlmDraw.append_token("\\")


if __name__ == "__main__":
    pytest.main([__file__])
