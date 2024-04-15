import numpy as np
import pandas as pd


def unit_transformation(data: pd.Series, unit_conversion: str) -> pd.Series:
    """
    Converts data to a specified unit of measurement

    Parameters
    ----------
    data : ndarray
        Data being transformed
    unit_conversion : str
        Unit conversion being applied

    Returns
    -------
    Series
        Pandas Series of transformed data

    Raises
    ------
    ValueError
        Invalid scale factor
    """
    if unit_conversion is None or unit_conversion == "None":
        return data
    elif unit_conversion == "m to km":
        return data * 0.001
    elif unit_conversion == "m to kft":
        return data * 0.0032808
    elif unit_conversion == "m to NMI":
        return data * 0.00053996
    elif unit_conversion == "km to m":
        return data * 1000
    elif unit_conversion == "km to kft":
        return data * 3.28084
    elif unit_conversion == "km to NMI":
        return data * 0.539957
    elif unit_conversion == "ft to km":
        return data * 0.0003048
    elif unit_conversion == "ft to kft":
        return data * 0.001
    elif unit_conversion == "ft to NMI":
        return data * 0.00016458
    elif unit_conversion == "mps to kts":
        return data * 1.9438
    elif unit_conversion == "kts to mps":
        return data * 0.51444
    elif unit_conversion == "m^2 to dBsm":
        return 10 * np.log10(data + np.spacing(0))
    elif unit_conversion == "dBsm to m^2":
        return pd.Series(np.power(10, data / 10))
    elif unit_conversion == "rad to deg":
        return data * 180 / np.pi
    elif unit_conversion == "deg to rad":
        return data * np.pi / 180
    else:
        raise ValueError(f"Invalid scaling factor: {unit_conversion}")
