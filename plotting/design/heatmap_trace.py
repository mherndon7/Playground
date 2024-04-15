import inspect
from decimal import Decimal, getcontext
from typing import Optional, TypedDict

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objs.scatter as s
from plotly.basedatatypes import BaseTraceType

from .colorscales import additional_colorscales
from .trace_line import Trace2D


class LevelDict(TypedDict):
    """Structure of a level item"""

    start: float
    stop: float
    step: float


class HeatMapTrace(Trace2D):
    def __init__(self, variable_template: dict) -> None:
        super().__init__(variable_template)
        self.heatmap: HeatMap | None = None

    def add_trace(
        self,
        fig: go.Figure,
        data: pd.DataFrame,
        grids: list[dict],
        row: int | None = None,
        col: int | None = None,
        legendgroup: str | None = None,
    ) -> list[pd.Series]:
        grid = grids[self.variable_template["subplot"] - 1]
        color = data[self.variable_template["colorVariable"]]

        # Create data
        data_dict: dict[str, pd.Series] = {}
        for axis in grid["axes"]:
            data_dict.update(self.get_axis_data(data, axis))

        # Heatmap for this trace
        self.heatmap = HeatMap(
            self.variable_template["colorVariable"],
            data[self.variable_template["colorVariable"]],
            max(d.max() for d in data_dict.values()),
            len(color),
            None,
            None,
            grid["colorBarTitle"],
            grid["colorScale"],
            grid["showColorBar"],
        )

        # Add trace
        fig.add_trace(
            self.build_scatter(data_dict, grid, legendgroup),
            row=row,
            col=col,
        )

        return list(data_dict.values())

    def build_scatter(
        self, data: dict[str, pd.Series], grid: dict, legendgroup: str | None = None
    ) -> BaseTraceType:
        if self.heatmap is None:
            raise ValueError("Heatmap is undefined")

        scatter = super().build_scatter(data, grid, legendgroup)
        scatter.update(self.heatmap.get_marker_text())

        return scatter

    def get_marker(self) -> s.Marker:
        if self.heatmap is None:
            raise ValueError("Heatmap is undefined")

        marker = self.heatmap.get_marker()
        marker.update(
            {
                "size": self.variable_template["markerSize"],
                "symbol": self.variable_template["markerType"].lower(),
            }
        )
        return marker


class HeatMap:
    """
    A specialized trace data variable the creates a Plotly heatmap
    """

    def __init__(
        self,
        name: str,
        colors: Optional[pd.Series] = None,
        default_max: Optional[float] = None,
        default_length: Optional[int] = None,
        colorscale_file: Optional[str] = None,
        contours: Optional[list[LevelDict]] = None,
        colorBarTitle: Optional[str] = None,
        colorScale: str = "",
        color: bool = False,
        **kwargs,
    ) -> None:
        """Creates a heatmap variable

        Parameters
        ----------
        name : str
            Name of the color variable the data originate from
        colors : Optional[pd.Series], optional
            Heatmap values for each point, by default None
        default_max : Optional[float], optional
            Max value for the default heatmap levels, by default None
        default_length : Optional[int], optional
            Size of the default heatmap, by default None
        colorscale_file : Optional[str], optional
            Custom colorscale file containing Parula, by default None
        contours : Optional[list[LevelDict]], optional
            User defined heatmap levels, by default None
        colorBarTitle : Optional[str], optional
            Color bar totle, by default None
        colorScale : str, optional
            Color scale to apply, by default ""
        color : bool, optional
            Show the colorbar, by default False
        """
        self.data = self.__create_colors(colors, default_max, default_length)
        self.colors = self.data.copy()

        self.color_variable = name
        self.title = colorBarTitle
        self.color_scale = colorScale
        self.show_colorbar = color

        # User defined heatmap bins
        self.levels = [] if contours is None else contours

        # Plotly heatmap properties
        self.__tickvals: list[float] = []
        self.__cmin: Optional[float] = None
        self.__cmax: Optional[float] = None
        self.__color_scale_values: list[str] = []

        self.__create_color_scale(colorscale_file)

    def data_to_dict(self) -> dict:
        if len(self.data) <= 1:
            return {}

        marker = s.Marker(
            cmin=self.__cmin,
            cmax=self.__cmax,
            color=self.colors,
            colorbar=s.marker.ColorBar(
                title={
                    "text": f"<b>{self.title}</b>",
                    "side": "right",
                    "font": {"size": 12},
                },
                thickness=20,
                tickmode="array",
                tickvals=self.__tickvals if len(self.__tickvals) > 0 else None,
                # tickfont=10,
            ),
            colorscale=list(self.__color_scale_values),
            showscale=self.show_colorbar,
        )

        return {
            "marker": marker.to_plotly_json(),
            "text": [f"{self.color_variable}: {c:.3f}" for c in self.colors.to_list()],
        }

    def get_marker(self) -> s.Marker:
        if len(self.data) <= 1:
            return s.Marker()

        return s.Marker(
            cmin=self.__cmin,
            cmax=self.__cmax,
            color=self.colors,
            colorbar=s.marker.ColorBar(
                title={
                    "text": f"<b>{self.title}</b>",
                    "side": "right",
                    "font": {"size": 12},
                },
                thickness=20,
                tickmode="array",
                tickvals=self.__tickvals if len(self.__tickvals) > 0 else None,
                # tickfont=10,
            ),
            colorscale=list(self.__color_scale_values),
            showscale=self.show_colorbar,
        )

    def get_marker_text(self) -> dict[str, list[str]]:
        return {
            "text": [f"{self.color_variable}: {c:.3f}" for c in self.colors.to_list()]
        }

    def __create_colors(
        self,
        colors: Optional[pd.Series],
        default_max: Optional[float],
        default_length: Optional[int],
    ) -> pd.Series:
        """
        Checks and provides colors for the heatmap

        Parameters
        ----------
        colors : Optional[np.ndarray]
            Colors chosen for heatmap
        default_max : Optional[float]
            Maximum color for default color levels
        default_length : Optional[int]
            Default length for the auto-generated heatmap colors

        Returns
        -------
        pd.Series
            Heatmap color values
        """
        if colors is not None:
            return colors

        if default_max is not None and default_length is not None:
            return pd.Series(np.linspace(0, default_max, default_length))

        return pd.Series([])

    def __create_color_scale(self, colorscale_file: Optional[str] = None) -> None:
        """
        Creates color scales for the heatmap

        Raises
        ------
        ValueError
            Invalid color scales
        """
        supported_scales = self.supported_colorscales(colorscale_file)
        if self.color_scale not in supported_scales:
            raise ValueError(
                f"{self.color_scale} is not a supported color scale."
                f" Please choose from {supported_scales}"
            )

        # Converts bin ranges into a single, sorted numpy array
        bins = self.__generate_bins()

        # Digitize the heatmap data into user defined levels
        if len(bins) > 0:
            self.__digitize(bins)

        # Limits set to avoid auto-scaling
        self.__cmin = bins[0] if len(bins) > 0 else None
        self.__cmax = bins[-1] if len(bins) > 0 else None

        # Apply the colorscale
        custom_colors = additional_colorscales()
        scale = (
            custom_colors[self.color_scale]
            if self.color_scale in custom_colors
            else getattr(px.colors.sequential, self.color_scale)
        )
        self.__color_scale_values = px.colors.make_colorscale(scale)

    def __generate_bins(self) -> np.ndarray:
        """
        The levels define individual breakpoints for the color gradient.
        Heatmap bins are created for mapping the actual color data to the
        coarser user-defined gradient

        Returns
        -------
        np.ndarray
            Color container bins
        """
        getcontext().prec = 15

        bins = np.array([])
        for level in self.levels:
            # Convert level values into tick marks
            ticks = [
                float(value)
                # Decimals help with the floating point percision
                for value in np.arange(
                    Decimal(level["start"]),
                    Decimal(level["stop"]),
                    Decimal(level["step"]),
                )
            ]
            ticks.append(float(Decimal(level["stop"])))
            self.__tickvals += ticks

            # Create color bins
            bins = np.append(
                bins, np.arange(level["start"], level["stop"], level["step"])
            )
            bins = np.append(bins, level["stop"])

        return np.sort(bins)

    def __digitize(self, bins: np.ndarray) -> None:
        """Converts the individual color data in bins

        Parameters
        ----------
        bins : np.ndarray
            Color container bins
        """
        bin_idx = np.searchsorted(bins, self.colors, side="right")
        bin_idx[self.colors < bins[0]] = 1
        self.data = pd.Series(bins[bin_idx - 1])

    @staticmethod
    def supported_colorscales(
        _custom_colorscale_file: Optional[str] = None,
    ) -> list[str]:
        """
        List of supported heatmap colorscales

        Returns
        -------
        list[str]
            Supported color scales
        """
        names = list(additional_colorscales())
        for name, body in inspect.getmembers(getattr(px.colors, "sequential")):
            if isinstance(body, list) and name[-2:] != "_r" and name[0] != "_":
                names.append(name)

        return sorted(names)
