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

from abc import ABC
from dataclasses import dataclass
from cl.convince.entries.expert_key import ExpertKey
from cl.runtime.primitive.timestamp import Timestamp


@dataclass(slots=True, kw_only=True)
class Expert(ExpertKey, ABC):
    """Base class for the algorithms that perform entry comprehension."""

    def init(self) -> None:
        """Similar to __init__ but can use fields set after construction."""
        if self.expert_id is None:
            # Use timestamp for temporary objects where identifier is not specified
            self.expert_id = Timestamp.create()
