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

import collections
import os
from typing import Iterable
from cl.convince.llms.llm_draw import LlmDraw
from cl.runtime.contexts.context_manager import active_or_none


class CompletionUtil:
    """Helper methods for LLM completions."""

    @classmethod
    def format_query(cls, query: str) -> str:
        """Add trial, strip leading and trailing whitespace, and normalize EOL."""

        # Strip leading and trailing whitespace and EOL
        result = query.strip()

        # Get draw_id from the active draw context and add it to the beginning of the formatted query
        if (draw := active_or_none(LlmDraw)) is not None:
            result = f"Trial: {draw.draw_id}\n{result}"

        # Normalize EOL
        result = cls.to_python_eol(result)
        return result

    @classmethod
    def format_completion(cls, value: str) -> str:
        """Strip leading and trailing whitespace, and normalize EOL."""

        # Strip leading and trailing whitespace and EOL
        result = value.strip()

        # Normalize EOL
        result = cls.to_python_eol(result)
        return result

    @classmethod
    def to_python_eol(cls, data: Iterable[str] | str | None):
        """Convert all types of EOL to \n for Python strings."""
        if data is None:
            return None
        if not isinstance(data, str) and isinstance(data, collections.abc.Iterable):
            # If data is iterable return list of adjusted elements
            # Convert EOL only, do not strip leading or trailing whitespace
            return [cls.to_python_eol(x) for x in data]
        else:
            # Replace endings format to \n
            data = data.replace("\r\r\n", "\n")
            data = data.replace("\r\n", "\n")
            return data

    @classmethod
    def to_os_eol(cls, data: Iterable[str] | str | None):
        """Convert all types of EOL to 'os.linesep' for writing the file to disk."""
        if data is None:
            return None
        if not isinstance(data, str) and isinstance(data, collections.abc.Iterable):
            # If data is iterable return list of adjusted elements
            return [cls.to_os_eol(x) for x in data]
        else:
            # Raise an exception if data contains os.linesep characters that are not \n, since
            # they will be lost after normalization.
            if os.linesep != "\n" and os.linesep in data:
                raise RuntimeError("Can not normalize data contains os.linesep characters that are not \\n.")

            # Replace \n to os.linesep
            adjusted_data = data.replace("\n", os.linesep)
            return adjusted_data
