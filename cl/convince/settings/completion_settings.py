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

from dataclasses import dataclass
from typing_extensions import final
from cl.runtime.contexts.os_util import OsUtil
from cl.runtime.settings.settings import Settings


@dataclass(slots=True, kw_only=True)
@final
class CompletionSettings(Settings):
    """Settings that apply to the entire Convince package."""

    load_from_csv: bool | None = None
    """Determines if completions are loaded from CSV files (defaults to True on Windows, required on other OS)."""

    save_to_csv: bool | None = None
    """Determines if completions are saved to CSV files (defaults to True on Windows, required on other OS)."""

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""

        if self.load_from_csv is None:
            # Defaults to True on Windows, required on other OS
            if OsUtil.is_windows():
                self.load_from_csv = True
            else:
                raise RuntimeError(
                    "Setting CL_CONVINCE_COMPLETION_LOAD_FROM_CSV is required on non-Windows platforms.\n"
                    "Specify in settings.yaml or as an environment variable."
                )

        # Save completions to a local file on Windows only
        if self.save_to_csv is None:
            # Defaults to True on Windows, required on other OS
            if OsUtil.is_windows():
                self.save_to_csv = True
            else:
                raise RuntimeError(
                    "Setting CL_CONVINCE_COMPLETION_SAVE_TO_CSV is required on non-Windows platforms.\n"
                    "Specify in settings.yaml or as an environment variable."
                )
