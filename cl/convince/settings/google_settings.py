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
from cl.runtime.records.typename import typename
from cl.runtime.settings.settings import Settings


@dataclass(slots=True, kw_only=True)
@final
class GoogleSettings(Settings):
    """Google Gemini settings."""

    google_api_key: str | None = None
    """The key for making REST API calls, ensure this key is stored in .secrets.yaml rather than settings.yaml."""

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""

        if self.google_api_key is not None and not isinstance(self.google_api_key, str):
            raise RuntimeError(f"{typename(self)} field 'api_key' must be a string.")
