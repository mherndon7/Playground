from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

import pandas as pd
import plotly.graph_objects as go
import plotly.graph_objs.scatter as s
import plotly.graph_objs.scatter3d as s3
from plotly.basedatatypes import BaseTraceType

from .unit_conversion import unit_transformation

Marker = TypeVar("Marker", bound=s.Marker | s3.Marker)
Line = TypeVar("Line", bound=s.Line | s3.Line)


class TraceBase(ABC, Generic[Marker, Line]):

    def __init__(self, variable_template: dict) -> None:
        self.variable_template = variable_template

    def add_trace(
        self,
        fig: go.Figure,
        data: pd.DataFrame,
        grids: list[dict],
        row: int | None = None,
        col: int | None = None,
        legendgroup: str | None = None,
    ) -> list[pd.Series]:

        # Grid corresponding to this trace
        grid = grids[self.variable_template["subplot"] - 1]

        # Create data
        data_dict: dict = {}
        for axis in grid["axes"]:
            data_dict.update(self.get_axis_data(data, axis))

        # Add trace
        fig.add_trace(
            self.build_scatter(data_dict, grid, legendgroup),
            row=row,
            col=col,
        )

        return list(data_dict.values())

    def get_axis_data(self, data: pd.DataFrame, axis: dict) -> dict[str, pd.Series]:
        return {
            axis["name"]: unit_transformation(
                data[self.variable_template[f"{axis['name']}Variable"]],
                axis["scaleFactor"],
            )
        }

    def build_scatter(
        self,
        data: dict[str, pd.Series],
        grid: dict,
        legendgroup: str | None = None,
    ) -> BaseTraceType:
        scatter = self.base_trace_type()
        return scatter(
            **data,
            name=self.variable_template["traceName"],
            connectgaps=self.variable_template["connectgaps"],
            mode=self.variable_template["mode"],
            marker=self.get_marker(),
            line=self.get_line(),
            legendgroup=legendgroup,
            legendgrouptitle_text=self.variable_template["legendGroupTitle"],
            showlegend=grid["showLegend"],
        )

    @abstractmethod
    def base_trace_type(self) -> Callable[..., BaseTraceType]:
        pass

    @abstractmethod
    def get_marker(self) -> Marker:
        pass

    @abstractmethod
    def get_line(self) -> Line:
        pass


class Trace2D(TraceBase[s.Marker, s.Line]):
    def base_trace_type(self) -> Callable[..., BaseTraceType]:
        return go.Scatter

    def get_marker(self) -> s.Marker:
        return s.Marker(
            color=self.variable_template["markerColor"],
            size=self.variable_template["markerSize"],
            symbol=self.variable_template["markerType"].lower(),
        )

    def get_line(self) -> s.Line:
        return s.Line(
            color=self.variable_template["lineColor"],
            width=self.variable_template["lineWidth"],
            dash=self.variable_template["lineType"],
            shape=self.variable_template["lineShape"],
        )


class Trace3D(TraceBase[s3.Marker, s3.Line]):
    def base_trace_type(self) -> Callable[..., BaseTraceType]:
        return go.Scatter3d

    def get_marker(self) -> s3.Marker:
        return s3.Marker(
            color=self.variable_template["markerColor"],
            size=self.variable_template["markerSize"],
            symbol=self.variable_template["markerType"].lower(),
        )

    def get_line(self) -> s3.Line:
        return s3.Line(
            color=self.variable_template["lineColor"],
            width=self.variable_template["lineWidth"],
            dash=self.variable_template["lineType"],
        )
