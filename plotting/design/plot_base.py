from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objs.layout import Legend

from .annotations import Classification, get_miss_distance, get_missile_info
from .grid import update_2d_grid, update_3d_grid
from .trace_line import TraceBase

Trace = TypeVar("Trace", bound=TraceBase)


class PlotBase(ABC, Generic[Trace]):
    def __init__(
        self,
        template: dict,
        output_data: pd.DataFrame,
        is_3d: bool,
        show_info_annotations: bool = True,
    ) -> None:
        self.template = template
        self.data = output_data

        # Allow constructor override
        self.show_info_annotations = (
            show_info_annotations and template["layout"]["showInfo"]
        )

        self.is_3d = is_3d
        self.show_legend = any(grid["showLegend"] for grid in template["grids"])

        self.classification = Classification(**template["classification"])

        # Create the Plotly Figure
        self.figure: go.Figure = self.inititialize_figure()
        self._initialize_layout()
        self._build_axes(self._build_traces())

    def show_plot(self, renderer: str | None = None) -> None:
        self.figure.show(renderer=renderer)

    def to_dict(self) -> dict:
        return self.figure.to_plotly_json()

    def to_json(self) -> str:
        return self.figure.to_json()

    def generate_images(self):
        pass

    def _build_traces(self) -> list[list[pd.Series]]:
        traces = []
        for variable in self.template["variables"]:
            # Disable legend groups for single plots
            # This allows for individual traces to be disabled
            legendgroup = (
                None
                if len(self.template["grids"]) <= 1
                else f"{variable['row']}-{variable['column']}"
            )

            trace = self.trace_handle(variable)
            traces += trace.add_trace(
                self.figure,
                self.data,
                self.template["grids"],
                variable["row"],
                variable["column"],
                legendgroup,
            )
        return traces

    def _initialize_layout(self) -> None:
        # Add annotations
        annotations = self.classification.get_classifications(
            self.is_3d, self.show_legend
        )

        if self.show_info_annotations:
            annotations.append(get_miss_distance(20.1))
            annotations.append(get_missile_info("MSL_1"))

        # Add base layout
        layout = go.Layout(
            title=self._get_title_dict(self.template["title"]),
            template=self.template["layout"]["theme"],
            height=self.template["layout"]["height"],
            width=self.template["layout"]["width"],
            legend=Legend(title=self.template["layout"]["legendTitle"]),
            margin=self._margin_dict(),
            annotations=annotations,
        )

        self.figure.update_layout(layout)

    def _get_title_dict(self, title: str) -> dict:
        return {
            "text": "<b>" + title.strip() + "</b>",
            "font": {"size": 13},
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }

    def _build_axes(self, trace_data: list[pd.Series]):
        axes_dict: dict = {}
        num_2d = 1
        num_3d = 1
        for grid_item in self.template["grids"]:
            if grid_item["plotType"] == "2d":
                update_2d_grid(trace_data, axes_dict, grid_item, num_2d)
                num_2d += 1
            else:
                update_3d_grid(trace_data, axes_dict, grid_item, num_3d)
                num_3d += 1

        self.figure.update_layout(axes_dict)

    def _margin_dict(self):
        bottom_margin = 40
        if self.show_info_annotations:
            bottom_margin += 20
        if self.classification.bottom_left or self.classification.bottom_right:
            bottom_margin += 10
        # if is_3d:
        #     bottom_margin -= 40

        return {
            "t": (
                40
                if self.classification.top_left or self.classification.top_right
                else 30
            ),
            "l": 20,
            "r": 1,
            "b": bottom_margin,
        }

    @abstractmethod
    def inititialize_figure(self) -> go.Figure:
        pass

    @abstractmethod
    def trace_handle(self, variable_template: dict) -> Trace:
        pass
