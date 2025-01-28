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

import re
from dataclasses import dataclass
from typing import List
from cl.runtime.contexts.db_context import DbContext
from cl.runtime.contexts.trial_context import TrialContext
from cl.runtime.log.exceptions.user_error import UserError
from cl.runtime.primitive.bool_util import BoolUtil
from cl.runtime.primitive.string_util import StringUtil
from cl.runtime.records.for_dataclasses.extensions import required
from cl.runtime.records.type_util import TypeUtil
from cl.convince.contexts.llm_context import LlmContext
from cl.convince.llms.llm import Llm
from cl.convince.prompts.formatted_prompt import FormattedPrompt
from cl.convince.prompts.prompt import Prompt
from cl.convince.prompts.prompt_key import PromptKey
from cl.convince.retrievers.multiple_choice_retrieval import MultipleChoiceRetrieval
from cl.convince.retrievers.retriever import Retriever
from cl.convince.retrievers.retriever_util import RetrieverUtil

_TRIPLE_BACKTICKS_RE = re.compile(r"```(.*?)```", re.DOTALL)
"""Regex for text between triple backticks."""

_BRACES_RE = re.compile(r"\{(.*?)\}")
"""Regex for text between curly braces."""

_TEMPLATE = """You will be provided with an input text, a description of a parameter, and possible values of this parameter.
Your goal is to extract the value of the parameter from the provided input text.

You must reply with JSON formatted strictly according to the JSON specification in which all values are strings.
The JSON must have the following keys:

{{
    "success": "<Y if you successfully extracted the parameter value and it matches one of the provided choices and N otherwise. This field is required.>",
    "param_value": "<Parameter value you extracted which matches one of the provided choices. Leave this field empty in case of failure.>",
    "justification": "<Justification for the parameter value you extracted in case of success or the reason why you were not able to find the parameter in case of failure. This field is required.>"
}}
Input text: ```{InputText}```
Parameter description: ```{ParamDescription}```
Semicolon-delimited list of valid choices: ```{ValidChoices}```

Keep in mind that the input text does not need to be one of the valid choices. Rather, you must use your knowledge as
Senior Quantitative Analyst to determine if the input has the same meaning or maps to one of the valid choices,
without necessarily being exactly the same or having the same format.

Examples:
  - When input text is $, a valid choice may be USD
  - When input text is %, a valid choice may be percent
"""


@dataclass(slots=True, kw_only=True)
class MultipleChoiceRetriever(Retriever):
    """Instructs the model to select the value of parameter from the provided choices."""

    prompt: PromptKey = required()
    """Prompt used to perform the retrieval."""

    max_retries: int = required()
    """How many times to retry the annotation in case changes other than braces are detected."""

    def init(self) -> None:
        """Similar to __init__ but can use fields set after construction."""
        if self.prompt is None:
            self.prompt = FormattedPrompt(
                prompt_id="MultipleChoiceRetriever",
                params_type=TypeUtil.name(MultipleChoiceRetrieval),  # TODO: More detailed error message for mismatch
                template=_TEMPLATE,
            )  # TODO: Review the handling of defaults

        # Default max_retries
        if self.max_retries is None:
            self.max_retries = 1

    def retrieve(
        self,
        *,
        input_text: str,
        param_description: str,
        valid_choices: List[str],
    ) -> MultipleChoiceRetrieval:

        # Load the full LLM specified by the context
        llm = DbContext.load_one(Llm, LlmContext.get_full_llm())

        # Load the prompt
        prompt = DbContext.load_one(Prompt, self.prompt)
        valid_choices_str = "; ".join(valid_choices)

        trial_count = 2
        for retry_index in range(self.max_retries):
            is_last_trial = retry_index == self.max_retries - 1

            # Append retry_index to trial_id to avoid reusing a cached completion
            trial_id = str(retry_index) if self.max_retries > 1 else None
            with TrialContext(trial_id=trial_id).build() as trial_context:

                # Strip starting and ending whitespace
                input_text = input_text.strip()  # TODO: Perform more advanced normalization

                try:
                    # Create a retrieval record
                    retrieval = MultipleChoiceRetrieval(
                        retriever=self.get_key(),
                        trial_id=trial_context.trial_id,
                        input_text=input_text,
                        param_description=param_description,
                        valid_choices=valid_choices,
                    )

                    # Create braces extraction prompt
                    rendered_prompt = prompt.render(params=retrieval)

                    # Get text annotated with braces and check that the only difference is braces and whitespace
                    completion = llm.completion(rendered_prompt)

                    # Extract the results
                    json_result = RetrieverUtil.extract_json(completion)
                    if json_result is not None:
                        retrieval.success = json_result.get("success", None)
                        retrieval.param_value = json_result.get("param_value", None)
                        retrieval.justification = json_result.get("justification", None)
                    else:
                        raise UserError(
                            f"Unable to retrieve a parameter from the following input:\n"
                            f"Parameter: {param_description}\n"
                            f"Input: {input_text}\n"
                            f"LLM response: {completion}\n"
                        )

                    # Normalize output
                    if retrieval.success is not None:
                        retrieval.success = retrieval.success.strip()
                    if retrieval.param_value is not None:
                        retrieval.param_value = retrieval.param_value.strip()

                    # Self-reported success or failure
                    success = BoolUtil.parse(retrieval.success, name="success")
                    if not success:
                        # Parameter is not found, continue with the next trial
                        continue

                    if StringUtil.is_not_empty(retrieval.param_value):
                        # Check that extracted_value is one of the provided choices
                        if retrieval.param_value not in valid_choices:
                            if not is_last_trial:
                                # Continue if not the last trial
                                continue
                            else:
                                # Otherwise report an error
                                # TODO: Use unified diff
                                raise UserError(
                                    f"The extracted parameter is among the valid choices.\n"
                                    f"Extracted value: ```{retrieval.param_value}```\n"
                                    f"Semicolon-delimited list of valid choices: ```{valid_choices_str}```\n"
                                )
                    else:
                        raise RuntimeError(
                            f"Extraction success reported by {llm.llm_id}, however "
                            f"the annotated text is empty. Input text:\n{input_text}\n"
                        )

                    # Return retrieval
                    return retrieval

                except Exception as e:
                    retrieval.success = "N"
                    retrieval.justification = str(e)
                    retrieval.build()
                    DbContext.save_one(retrieval)
                    if is_last_trial:
                        # Rethrow only when the last trial is reached
                        raise UserError(
                            f"Unable to extract parameter from the input text after {trial_count} trials.\n"
                            f"Input text: {input_text}\n"
                            f"Parameter description: {param_description}\n"
                            f"Last trial error information: {retrieval.justification}\n"
                        )
                else:
                    retrieval.success = "Y"
                    retrieval.build()
                    DbContext.save_one(retrieval)

        # The method should always return from the loop, adding as a backup in case this changes in the future
        raise UserError(
            f"Unable to extract parameter from the input text.\n"
            f"Input text: {input_text}\n"
            f"Parameter description: {param_description}\n"
        )
