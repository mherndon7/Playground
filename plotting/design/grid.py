from enum import Enum
from typing import Literal

import pandas as pd

from .unit_conversion import unit_transformation

AxisName = Literal["x", "y", "z"]


class AxisType(str, Enum):
    """Supported axis layout sizing"""

    AUTO = "Auto"
    EQUAL = "Equal"
    MANUAL = "Manual"


def update_2d_grid(
    trace_data: list[pd.Series], axes_dict: dict, grid: dict, plot_number: int
) -> None:
    # Visual bounds for an axis
    limits = __axis_limits(grid["axisType"], grid["axes"], trace_data)

    for index, axis in enumerate(grid["axes"]):
        # Plotly axis name
        name = f"{axis['name']}axis{plot_number}"
        if name not in axes_dict:
            axes_dict[name] = {}

        # Create axis info
        axes_dict[name] = __get_axis_layout(axis, limits[index])
        axes_dict[name]["title"]["standoff"] = 8 if "y" in name else 1

        # Set plot domain location within the grid
        if grid["overwriteDomain"]:
            axes_dict[name]["domain"] = [axis["domainMin"], axis["domainMax"]]


def update_3d_grid(
    trace_data: list[pd.Series], axes_dict: dict, grid: dict, plot_number: int
) -> None:
    # Visual bounds for an axis
    limits = __axis_limits(grid["axisType"], grid["axes"], trace_data)

    # Plotly scene name
    scene_name = f"scene{plot_number}"
    if scene_name not in axes_dict:
        axes_dict[scene_name] = {}

    for index, axis in enumerate(grid["axes"]):
        # Plotly axis name
        name = f"{axis['name']}axis"
        if name not in axes_dict[scene_name]:
            axes_dict[scene_name][name] = {}

        # Create axis info
        axes_dict[scene_name][name] = __get_axis_layout(axis, limits[index])

        # Set plot domain location within the grid
        if grid["overwriteDomain"] and axis["name"] in ["x", "y"]:
            axes_dict[scene_name]["domain"] = {
                axis["name"]: [
                    axis["domainMin"],
                    axis["domainMax"],
                ]
            }

    # Set camera fields
    axes_dict[scene_name]["camera"] = {
        "projection": {"type": "orthographic"},
        "eye": {"x": -1.25, "z": 0.8},
    }


def __axis_limits(
    axis_type: AxisType, axes: dict, data: list[pd.Series]
) -> pd.Series | list[None]:
    if axis_type == AxisType.MANUAL:
        return [
            unit_transformation(
                pd.Series([axis["min"], axis["max"]]), axis["scaleFactor"]
            )
            for axis in axes
        ]

    elif axis_type == AxisType.EQUAL:
        # TODO: Add unit transformation
        return [
            pd.Series(
                min(variable.min() for variable in data),
                max(variable.max() for variable in data),
            )
        ] * len(axes)

    elif axis_type == AxisType.AUTO:
        return [None] * len(axes)


def __get_axis_layout(axis: dict, limits: tuple[float, float] | None) -> dict:
    return {
        "range": limits,
        "showgrid": axis["enableGrid"],
        "title": {"text": axis["label"], "font": {"size": 12}},
        "linecolor": "black",
        "linewidth": 1,
        "mirror": axis["enableBox"],
        "tickmode": axis["tickMode"],
        "tickvals": axis["tickVals"],
        "ticktext": axis["tickText"],
    }
