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

import csv
import hashlib
import os
from dataclasses import dataclass
from typing import Any
from cl.runtime.contexts.context_manager import active
from cl.runtime.contexts.context_manager import active_or_default
from cl.runtime.db.data_source import DataSource
from cl.runtime.primitive.string_util import StringUtil
from cl.runtime.qa.qa_util import QaUtil
from cl.runtime.records.for_dataclasses.dataclass_mixin import DataclassMixin
from cl.runtime.serializers.json_serializers import JsonSerializers
from cl.runtime.server.env import Env
from cl.runtime.settings.project_settings import ProjectSettings
from cl.convince.llms.completion import Completion
from cl.convince.llms.completion_key import CompletionKey
from cl.convince.llms.completion_util import CompletionUtil
from cl.convince.llms.llm_key import LlmKey
from cl.convince.prompts.composite_prompt import CompositePrompt
from cl.convince.prompts.composite_prompt import PromptTextElement
from cl.convince.prompts.prompt import Prompt
from cl.convince.settings.completion_settings import CompletionSettings

_supported_extensions = ["csv"]
"""The list of supported output file extensions (formats)."""

_csv_headers = ["completion_id", "parent_completion_id", "query", "completion", "timestamp"]
"""CSV column headers."""


def _error_extension_not_supported(ext: str) -> Any:
    raise RuntimeError(
        f"Extension {ext} is not supported by CompletionCache. "
        f"Supported extensions: {', '.join(_supported_extensions)}"
    )


@dataclass(slots=True, kw_only=True)
class CompletionCache(DataclassMixin):
    # TODO fix tests for CompletionCache
    """
    Cache LLM completions for reducing AI cost (disable when testing the LLM itself)

    Completion cache has a tree structure where root represents the start of conversation with llm.
    Each subsequent interaction provided with message history will create a node with the reference to the parent (query-answer) cache record.
    The ID of the new completion record is generated based on the entire conversation history.
    Thus, completion cache structures query-answer calls into conversation trees.

    Notes:
        - After each model call, input and output are recorded in 'channel.completions.csv'
        - The channel may be based on llm_id or include some of all of the LLM settings or their hash
        - If exactly the same input is subsequently found in the completions file, it is used without calling the LLM
        - To record a new completions file, delete the existing one
    """

    channel: str | None = None
    """Dot-delimited string or an iterable of dot-delimited tokens to uniquely identify the cache."""

    ext: str | None = None
    """Output file extension (format) without the dot prefix, defaults to 'csv'."""

    output_path: str | None = None
    """Path for the cache file where completions are stored."""

    _completions_loaded: bool = False
    """Flag indicating stored completions were loaded."""

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""

        # Find base_path=dir_path/test_module by examining call stack for test function signature test_*
        # Directory 'project_root/completions' is used when not running under a test
        if active_or_default(Env).is_test():  # TODO: Add a standard way to specify the working directory in Env
            base_dir = QaUtil.get_test_dir_from_call_stack()
        else:
            base_dir = os.path.join(ProjectSettings.instance().get_resources_root(), "completions")

        # If not found, use base path relative to project root
        if base_dir is None:
            project_root = ProjectSettings.get_project_root()
            base_dir = os.path.join(project_root, "completions")

        if self.ext is not None:
            # Remove dot prefix if specified
            self.ext = self.ext.removeprefix(".")
            if self.ext not in _supported_extensions:
                _error_extension_not_supported(self.ext)
        else:
            # Use csv if not specified
            self.ext = "csv"

        # Cache file path
        if self.channel is None or self.channel == "":
            cache_filename = f"completions.{self.ext}"
        else:
            cache_filename = f"{self.channel}.completions.{self.ext}"
        self.output_path = os.path.join(base_dir, cache_filename)

        # Load completion dictionary from disk
        self.load_completion_dict()

    @staticmethod
    def create_cache_key(llm_id: str, query: str | Prompt) -> str:
        """Creates cache key for the llm completion."""

        if isinstance(query, CompositePrompt):
            query = "".join(
                reversed(
                    [
                        (
                            el.text
                            if isinstance(el, PromptTextElement)
                            else hashlib.sha1(str(el).encode("utf-8")).hexdigest()
                        )
                        for el in query.elements
                    ]
                )
            )
        elif isinstance(query, Prompt):
            raise RuntimeError(f"Query type '{type(query).__name__}' is not supported.")

        return StringUtil.human_readable_hash(query, text_params=(llm_id,))

    def add(self, request_id: str, key: str, query: str | Prompt, completion: str) -> None:
        """Add to file even if already exits, the latest will take precedence during lookup."""

        if CompletionSettings.instance().completion_disable_caching:
            return

        # Remove leading and trailing whitespace and normalize EOL in value
        completion = CompletionUtil.format_completion(completion)

        parent_key = None

        # Search for parent key only in CompositePrompt, fort others set it to None
        if isinstance(query, CompositePrompt):
            elements = query.elements
            length = len(elements)

            # If length <= 1, the root of conversation reached
            if length > 1:
                # Traverse backwards from the second-to-last element
                for i in range(length - 2, -1, -1):
                    current_element = elements[i]
                    if isinstance(current_element, PromptTextElement) and current_element.role == "user":
                        # Find the assistant reply that follows this user
                        next_assistant = next(
                            (
                                e
                                for e in elements[i + 1 :]
                                if isinstance(e, PromptTextElement) and e.role == "assistant"
                            ),
                            None,
                        )

                        # Slice conversation up to and including this user message
                        history_slice = elements[: i + 1]

                        # Build prompt and compute key
                        parent_prompt = CompositePrompt(elements=history_slice)
                        slice_key = CompletionCache.create_cache_key(self.channel, parent_prompt)

                        # Check if cached
                        cache_record = active(DataSource).load_one_or_none(
                            CompletionKey(completion_id=slice_key),
                            cast_to=Completion,
                        )

                        if cache_record is None:
                            # Recursively add parent cache node with its assistant reply
                            self.add(
                                request_id=f"{request_id}-parent-{i // 2}",
                                key=slice_key,
                                query=parent_prompt,
                                completion=(next_assistant.text if next_assistant else ""),
                            )

                        parent_key = slice_key
                        break

            # TODO: remove when Unions are supported in field spec ("str | CompositePrompt")
            query = JsonSerializers.DEFAULT.serialize(query)

        # Create and save a completion record
        completion_record = Completion(
            completion_id=key,
            parent_completion_id=parent_key,
            llm=LlmKey(llm_id=self.channel),
            query=query,
            completion=completion,
            timestamp=request_id,
        ).build()

        # Save completions to DB (including preloads) outside a test
        active(DataSource).replace_one(completion_record, commit=True)

        # Save completions to a file unless explicitly turned off in CompletionSettings
        if CompletionSettings.instance().completion_save_to_csv:
            self.add_to_csv(completion_record, request_id)

    def add_to_csv(self, completion_record: Completion, request_id: str) -> None:
        # Check if the file already exists
        is_new = not os.path.exists(self.output_path)

        # If file does not exist, create directory if directory does not exist
        if is_new:
            output_dir = os.path.dirname(self.output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

        if self.ext == "csv":
            with open(self.output_path, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(
                    file,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                    escapechar="\\",
                    lineterminator=os.linesep,
                )

                if is_new:
                    # Write the headers if the file is new
                    writer.writerow(CompletionUtil.to_os_eol(_csv_headers))

                # NOT ADDING THE VALUE TO COMPLETION DICT HERE IS NOT A BUG
                # Because we are not adding to the dict here but only writing to a file,
                # the model will not reuse cached completions within the same session,
                # preventing incorrect measurement of stability

                # Convert composite prompt to json string
                # TODO: Uncomment when Unions are supported in field spec ("str | CompositePrompt")
                # query = JsonSerializers.DEFAULT.serialize(completion_record.query)

                # Write the new completion without checking if one already exists
                writer.writerow(
                    CompletionUtil.to_os_eol(
                        [
                            completion_record.completion_id,
                            completion_record.parent_completion_id,
                            completion_record.query,
                            completion_record.completion,
                            request_id,
                        ]
                    )
                )

                # Flush immediately to ensure all of the output is on disk in the event of exception
                file.flush()
        else:
            # Should not be reached here because of a previous check in __init__
            _error_extension_not_supported(self.ext)

    def get(self, key: str) -> str | None:
        """Return completion for the specified query key if found and None otherwise."""

        if CompletionSettings.instance().completion_disable_caching:
            return None

        # Return completion string from DB or None if the record is not found
        completion = active(DataSource).load_one_or_none(CompletionKey(completion_id=key).build(), cast_to=Completion)
        return completion.completion if completion is not None else None

    def load_completion_dict(self) -> None:
        """Load cache file."""

        if CompletionSettings.instance().completion_disable_caching:
            self._completions_loaded = True
            return

        # Load if the file exists unless explicitly turned off in CompletionSettings
        if not self._completions_loaded:
            self._completions_loaded = True

            if CompletionSettings.instance().completion_load_from_csv and os.path.exists(self.output_path):
                # Populate the dictionary from file if exists but not yet loaded
                with open(self.output_path, mode="r", newline="", encoding="utf-8") as file:
                    reader = csv.DictReader(
                        file, delimiter=",", quotechar='"', escapechar="\\", lineterminator=os.linesep
                    )

                    # Read and validate the headers
                    headers_in_file = reader.fieldnames
                    if headers_in_file != _csv_headers:
                        max_len = 20
                        headers_in_file = [h if len(h) < max_len else f"{h[:max_len]}..." for h in headers_in_file]
                        headers_in_file_str = ", ".join(headers_in_file)
                        expected_headers_str = ", ".join(_csv_headers)
                        raise ValueError(
                            f"Expected column headers in completions cache are {expected_headers_str}. "
                            f"Actual headers: {headers_in_file_str}."
                        )

                    # Create and save a completion record
                    completions = [
                        Completion(
                            llm=LlmKey(llm_id=self.channel),
                            # Deser json string query
                            # TODO: Uncomment when Unions are supported in field spec ("str | CompositePrompt")
                            # query=JsonSerializers.DEFAULT.deserialize(row.pop("query")),
                            **row,
                        ).build()
                        for row_ in reader
                        if (row := CompletionUtil.to_python_eol(row_))
                    ]

                    # Save to DB unless inside a test
                    active(DataSource).replace_many(
                        completions, commit=True
                    )  # TODO: Review to see how to use insert_many instead
