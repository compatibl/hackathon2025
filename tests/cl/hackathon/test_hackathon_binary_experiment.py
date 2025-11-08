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
from more_itertools import consume
from cl.runtime.contexts.context_manager import active
from cl.runtime.db.data_source import DataSource
from cl.runtime.settings.preload_settings import PreloadSettings
from cl.runtime.stat.experiment_key import ExperimentKey


@pytest.mark.skip("Temporarily skipped.")
def test_smoke(default_db_fixture):
    """Test for ClassifierExperiment."""
    # Initialize preloads
    PreloadSettings.instance().save_and_configure()

    # Create and run the experiment
    experiment_keys = [
        ExperimentKey("TradeEntry.0"),
        ExperimentKey("TradeEntry.1"),
    ]
    experiments = active(DataSource).load_many(tuple(x.build() for x in experiment_keys))
    consume(x.run_launch_all_trials() for x in experiments)
    consume(x.get_plot(x.experiment_id).save(format_="svg") for x in experiments)


if __name__ == "__main__":
    pytest.main([__file__])
