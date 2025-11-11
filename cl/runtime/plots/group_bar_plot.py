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
import pandas as pd
from matplotlib import pyplot as plt
from cl.runtime.plots.bar_plot import BarPlot


@dataclass(slots=True, kw_only=True)
class GroupBarPlot(BarPlot):
    """Base class for the 2D group bar plot."""

    def _create_figure(self) -> plt.Figure:

        data = (
            pd.DataFrame.from_records([self.values, self.bar_labels, self.group_labels], index=["Value", "Col", "Row"])
            .T.pivot_table(index="Row", columns="Col", values="Value", sort=False)
            .astype(float)
        )

        fig, axes, x_ticks = self._prepare_common_plot_elements(data=data)

        num_bars = data.shape[1]
        if num_bars % 2 != 0:
            bar_shifts_positive = list(range(1, num_bars // 2 + 1))
        else:
            bar_shifts_positive = [x + 0.5 for x in range(num_bars // 2)]

        bar_shifts = [-x for x in reversed(bar_shifts_positive)]
        if num_bars % 2 != 0:
            bar_shifts += [0]

        bar_shifts += bar_shifts_positive

        space = 1 / (num_bars + 1)

        for i, (bar_label, bar_shift) in enumerate(zip(data.columns, bar_shifts)):
            axes.bar(x_ticks + space * bar_shift, data[bar_label].values, space, label=bar_label)
        axes.legend()
        return fig
