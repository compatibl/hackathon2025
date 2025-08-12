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
from typing import List
from cl.runtime.contexts.context_manager import activate
from cl.runtime.parsers.locale import Locale
from cl.runtime.qa.regression_guard import RegressionGuard
from cl.runtime.settings.preload_settings import PreloadSettings
from cl.convince.contexts.llm_context import LlmContext
from cl.convince.llms.claude.claude_llm import ClaudeLlm
from cl.convince.llms.gpt.gpt_llm import GptLlm
from cl.convince.llms.llama.llama_llm import LlamaLlm
from cl.convince.retrievers.annotating_retriever import AnnotatingRetriever
from stubs.cl.convince.experiments.stub_llms import get_stub_full_llms

ENTRY_TEXT = "Sell 10y SOFR swap at 3.45%"
PARAM_DESCRIPTION = "Fixed rate."
PARAM_SAMPLES = [
    "Pay fixed",
    "We pay fixed",
    "Long",
    "Buy",
    "Receive fixed",
    "Rec fixed",
    "We receive fixed",
    "Short",
    "Sell",
]


def _test_extract(input_text: str, param_description: str, param_samples: list[str] | None = None) -> None:
    """Test extraction of the specified parameters from the entries."""
    # TODO: Use samples in few-shot test
    param_samples_str = "".join(f"  - {x}\n" for x in param_samples) if param_samples is not None else None
    stub_full_llms = get_stub_full_llms()
    for llm in stub_full_llms:
        with activate(LlmContext(full_llm=llm).build()):
            retriever = AnnotatingRetriever(
                retriever_id="test_annotating_retriever",
            )
            retriever.build()
            guard = RegressionGuard(channel=llm.llm_id)
            param_value = retriever.retrieve(input_text=input_text, param_description=param_description)
            guard.write(f"Input Text: {input_text} Retrieved Value: {param_value}")
    RegressionGuard().verify_all()


def test_zero_shot(default_db_fixture):
    """Test without samples."""
    PreloadSettings.instance().save_and_configure(final_record_types=[Locale, GptLlm, LlamaLlm, ClaudeLlm])
    _test_extract(ENTRY_TEXT, PARAM_DESCRIPTION)


if __name__ == "__main__":
    pytest.main([__file__])
