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

import pytest

from cl.hackathon.hackathon_trade_entry_experiment import HackathonTradeEntryExperiment
from cl.runtime.settings.preload_settings import PreloadSettings
from cl.runtime.stats.condition import Condition
from cl.runtime.stats.condition_key import ConditionKey
from stubs.cl.runtime.stats.stub_classifier_experiment import StubClassifierExperiment


def test_smoke(default_db_fixture):
    """Test for ClassifierExperiment."""
    # Initialize preloads
    PreloadSettings.instance().save_and_configure()

    # Create and run the experiment
    experiment = HackathonTradeEntryExperiment(
        experiment_id="test_hackathon_trade_entry_experiment.test_smoke",
        max_trials=5,
        conditions=[
            ConditionKey(condition_id="TradeEntry.Baseline").build(),
            ConditionKey(condition_id="TradeEntry.EmbeddedOption").build(),
        ],
    )
    experiment.run_launch_all_trials()
    experiment.get_plot("test_hackathon_trade_entry_experiment.results").save(format_="svg")

if __name__ == "__main__":
    pytest.main([__file__])
