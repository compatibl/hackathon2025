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
import os
from dataclasses import dataclass
from typing import Any
from cl.runtime.contexts.context_manager import active
from cl.runtime.contexts.context_manager import active_or_default
from cl.runtime.db.data_source import DataSource
from cl.runtime.qa.qa_util import QaUtil
from cl.runtime.records.data_mixin import DataMixin
from cl.runtime.server.env import Env
from cl.runtime.settings.project_settings import ProjectSettings
from cl.convince.llms.completion import Completion
from cl.convince.llms.completion_key_gen import CompletionKeyGen
from cl.convince.llms.completion_util import CompletionUtil
from cl.convince.llms.llm_key import LlmKey
from cl.convince.settings.completion_settings import CompletionSettings

_supported_extensions = ["csv"]
"""The list of supported output file extensions (formats)."""

_csv_headers = ["RequestID", "Query", "Completion"]
"""CSV column headers."""


def _error_extension_not_supported(ext: str) -> Any:
    raise RuntimeError(
        f"Extension {ext} is not supported by CompletionCache. "
        f"Supported extensions: {', '.join(_supported_extensions)}"
    )


@dataclass(slots=True, kw_only=True)
class CompletionCache(DataMixin):
    """
    Cache LLM completions for reducing AI cost (disable when testing the LLM itself)

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
        if active_or_default(Env).testing:  # TODO: Add a standard way to specify the working directory in Env
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

    def add(self, request_id: str, query: str, completion: str) -> None:
        """Add to file even if already exits, the latest will take precedence during lookup."""

        # Remove leading and trailing whitespace and normalize EOL in value
        completion = CompletionUtil.format_completion(completion)

        # Create and save a completion record
        completion_record = Completion(
            llm=LlmKey(llm_id=self.channel),
            query=query,
            completion=completion,
            timestamp=request_id,
        ).build()

        # Save completions to DB (including preloads) outside a test
        active(DataSource).save_one(completion_record)

        # Save completions to a file unless explicitly turned off in CompletionSettings
        if CompletionSettings.instance().completion_save_to_csv:

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

                    # Write the new completion without checking if one already exists
                    writer.writerow(
                        CompletionUtil.to_os_eol([request_id, completion_record.query, completion_record.completion])
                    )

                    # Flush immediately to ensure all of the output is on disk in the event of exception
                    file.flush()
            else:
                # Should not be reached here because of a previous check in __init__
                _error_extension_not_supported(self.ext)

    def get(self, query: str) -> str | None:
        """Return completion for the specified query if found and None otherwise."""

        # Set only those fields that are required for computing the key
        completion_key = CompletionKeyGen(llm=LlmKey(llm_id=self.channel), query=query).build().get_key()

        # Return completion string from DB or None if the record is not found
        completion = active(DataSource).load_one_or_none(completion_key, cast_to=Completion)
        result = completion.completion if completion is not None else None
        return result

    def load_completion_dict(self) -> None:
        """Load cache file."""
        # Load if the file exists unless explicitly turned off in CompletionSettings
        if not self._completions_loaded:
            self._completions_loaded = True

            if CompletionSettings.instance().completion_load_from_csv and os.path.exists(self.output_path):
                # Populate the dictionary from file if exists but not yet loaded
                with open(self.output_path, mode="r", newline="", encoding="utf-8") as file:
                    reader = csv.reader(file, delimiter=",", quotechar='"', escapechar="\\", lineterminator=os.linesep)

                    # Read and validate the headers
                    headers_in_file = next(reader, None)
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
                            query=row[1],
                            completion=row[2],
                            timestamp=row[0],
                        ).build()
                        for row_ in reader
                        if (row := CompletionUtil.to_python_eol(row_))
                    ]

                    # Save to DB unless inside a test
                    active(DataSource).save_many(completions)
