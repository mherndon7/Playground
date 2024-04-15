import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .heatmap_trace import HeatMapTrace
from .plot_base import PlotBase
from .trace_line import Trace2D, Trace3D


class Plot2D(PlotBase[Trace2D]):
    def __init__(self, template: dict, output_data: pd.DataFrame) -> None:
        super().__init__(template, output_data, False)

    def inititialize_figure(self) -> go.Figure:
        return go.Figure()

    def trace_handle(self, variable_template: dict) -> Trace2D:
        return Trace2D(variable_template)


class Plot3D(PlotBase[Trace3D]):
    def __init__(self, template: dict, output_data: pd.DataFrame) -> None:
        super().__init__(template, output_data, True)

    def inititialize_figure(self) -> go.Figure:
        return go.Figure()

    def trace_handle(self, variable_template: dict) -> Trace3D:
        return Trace3D(variable_template)


class PlotHeatmap(PlotBase[HeatMapTrace]):
    def __init__(self, template: dict, output_data: pd.DataFrame) -> None:
        super().__init__(template, output_data, False, False)

    def inititialize_figure(self) -> go.Figure:
        return go.Figure()

    def trace_handle(self, variable_template: dict) -> HeatMapTrace:
        return HeatMapTrace(variable_template)


# class PlotDiscrete(PlotBase[Trace2D]):
#     def __init__(self, template: dict, output_data: pd.DataFrame) -> None:
#         super().__init__(template, output_data, False, False)

#     def inititialize_figure(self) -> go.Figure:
#         return go.Figure()


class Subplots(PlotBase[Trace2D | Trace3D]):
    def __init__(self, template: dict, output_data: pd.DataFrame) -> None:
        is_3d = any([len(grid["axes"]) == 3 for grid in template["grids"]])
        super().__init__(template, output_data, is_3d)

    def inititialize_figure(self) -> go.Figure:
        # https://github.com/plotly/plotly.js/issues/2746
        num_rows = len(set(variable["row"] for variable in self.template["variables"]))
        num_columns = len(
            set(variable["column"] for variable in self.template["variables"])
        )

        specs = [[{"is_3d": len(grid["axes"]) == 3}] for grid in self.template["grids"]]

        return make_subplots(
            num_rows,
            num_columns,
            vertical_spacing=self.template["layout"]["verticalSpacing"],
            shared_xaxes=self.template["layout"]["sharedXAxes"],
            shared_yaxes=self.template["layout"]["sharedYAxes"],
            subplot_titles=[grid["title"] for grid in self.template["grids"]],
            specs=specs,
        )

    def trace_handle(self, variable_template: dict) -> Trace2D | Trace3D:
        if variable_template["plotType"] == "2d":
            return Trace2D(variable_template)
        elif variable_template["plotType"] == "3d":
            return Trace3D(variable_template)
        else:
            raise ValueError(
                f"Invalid plot type '{variable_template['plotType']}'. Must be '2d' or '3d'."
            )
