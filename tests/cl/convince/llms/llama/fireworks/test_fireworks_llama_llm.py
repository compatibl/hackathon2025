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
from cl.convince.llms.llama.fireworks.fireworks_llama_llm import FireworksLlamaLlm
from cl.runtime.testing.pytest.pytest_fixtures import testing_db

def test_smoke(testing_db):
    """Test FireworksLlamaLlm class."""
    llms = [
        FireworksLlamaLlm(llm_id="llama-v3-8b-instruct"),
        FireworksLlamaLlm(llm_id="llama-v3-8b-instruct-0.2", model_name="llama-v3-8b-instruct", temperature=0.2),
    ]
    for llm in llms:
        assert "4" in llm.completion("2 times 2?")


if __name__ == "__main__":
    pytest.main([__file__])
