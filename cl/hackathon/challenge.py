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
from cl.runtime.contexts.context_manager import active
from cl.runtime.db.data_source import DataSource
from cl.runtime.primitive.timestamp import Timestamp
from cl.runtime.records.for_dataclasses.extensions import required
from cl.runtime.records.record_mixin import RecordMixin
from cl.runtime.records.typename import typename
from cl.runtime.stat.case_key import CaseKey
from cl.hackathon.challenge_key import ChallengeKey
from cl.hackathon.hackathon_experiment import HackathonExperiment


@dataclass(slots=True, kw_only=True)
class Challenge(ChallengeKey, RecordMixin):
    """A collection of cases that can be used to create experiments."""

    mitigation_prompt: str | None = None
    """Prompt that will counteract the cognitive bias."""

    cases: list[CaseKey] = required()
    """Cases (conditions) for which the experiment is performed (optional)."""

    num_trials: int = required()
    """Number of trials to run per condition (optional)."""

    max_retries: int = 10
    """Maximum number of retries for throttled requests."""

    default_retry_delay_sec: int = 2
    """Initial retry delay for throttled requests when recommended delay cannot be extracted from the message."""

    max_retry_delay_sec: int = 120
    """Limit retry delay for throttled requests to this value in seconds when set by rule or extracted from message."""

    def get_key(self) -> ChallengeKey:
        return ChallengeKey(challenge_id=self.challenge_id).build()

    def view_cases(self) -> tuple[CaseKey, ...]:
        """View cases of the experiment."""
        return tuple(self.cases)

    def __init(self) -> None:
        """Use instead of __init__ in the builder pattern, invoked by the build method in base to derived order."""
        if self.num_trials is None:
            raise RuntimeError(f"{typename(type(self))}.num_trials is None.")
        elif self.num_trials <= 0:
            raise RuntimeError(f"{typename(type(self))}.num_trials={self.num_trials} is not a positive number.")

    def run_create_experiment(self) -> None:
        """Create an experiment using the settings from this record."""

        # Append timestamp to experiment ID
        experiment = HackathonExperiment(
            experiment_id=f"{self.challenge_id}.{Timestamp.create()}",
            cases=self.cases,
            num_trials=self.num_trials,
            mitigation_prompt=self.mitigation_prompt,
            max_retries=self.max_retries,
            default_retry_delay_sec=self.default_retry_delay_sec,
            max_retry_delay_sec=self.max_retry_delay_sec,
        )

        # Build and save
        experiment.build()
        active(DataSource).insert_one(experiment, commit=True)
