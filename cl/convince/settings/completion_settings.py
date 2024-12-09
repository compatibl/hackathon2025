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

import os
from dataclasses import dataclass
from typing import Tuple
from typing_extensions import Self
from cl.runtime.exceptions.error_util import ErrorUtil
from cl.runtime.settings.settings import Settings


@dataclass(slots=True, kw_only=True)
class CompletionSettings(Settings):
    """Settings that apply to the entire Convince package."""

    load_completions_from_csv: bool | None = None
    """Completions are loaded from CSV files by default, use this field to change."""

    save_completions_to_csv: bool | None = None
    """Completions are saved to CSV files by default on Windows only, use this field to change."""

    @classmethod
    def get_prefix(cls) -> str:
        return "convince"
