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
from cl.runtime.stat.binary_trial import BinaryTrial


@dataclass(slots=True, kw_only=True)
class HackathonTrial(BinaryTrial):
    """Hackathon trial."""

    response: str | None = None
    """Response value if parsing did not fail, or raw response if it did."""

    rationale: str | None = None
    """Rationale for the response if available."""

    mitigation_prompt: str | None = None
    """Text creating a cognitive bias."""

    bias_prompt: str | None = None
    """Text creating a cognitive bias."""

    business_prompt: str | None = None
    """Query affected by the bias."""

    llm_input: str | None = None
    """Complete LLM input string including mitigation prompt (if any), bias prompt (if any), and business prompt."""

    expected_value: str | None = None
    """Expected (correct) value."""

    expected_min: int | None = None
    """Expected (correct) minimum value for response_type=int or float."""

    response_type: str | None = None
    """Response type from PRIMITIVE_TYPES, can omit if response_enum is set. """

    response_enum: list[str] | None = None
    """Response enumeration, the model will not output values outside this set."""

    include_rationale: bool | None = None
    """If True, rationale for the response is requested along with the response."""
