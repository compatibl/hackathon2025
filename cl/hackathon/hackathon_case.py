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
from cl.runtime.records.for_dataclasses.extensions import required
from cl.runtime.records.typename import typenameof
from cl.runtime.stat.case import Case


@dataclass(slots=True, kw_only=True)
class HackathonCase(Case):
    """Condition under which the hackathon classifier experiment is performed."""

    bias_prompt: str | None = None
    """Text creating a cognitive bias."""

    business_prompt: str = required()
    """Query affected by the bias."""

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

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""

        if self.expected_value is None and self.expected_min is None:
            raise RuntimeError(f"{typenameof(self)}.expected_value and expected_min are both None.")
        if self.expected_value is not None and self.expected_min is not None:
            raise RuntimeError(f"{typenameof(self)}.expected_value and expected_min are both set.")

        if self.response_type is None:
            if self.response_enum is not None:
                self.response_type = "str"
            else:
                raise RuntimeError(f"{typenameof(self)}.response_type and response_enum are both None.")
        elif self.response_type == "str":
            # Allow response_enum to be set or None
            pass
        elif self.response_type in ("int", "float"):
            if self.response_enum is not None:
                raise RuntimeError(
                    f"{typenameof(self)}.response_enum must be None for response_type '{self.response_type}'."
                )
