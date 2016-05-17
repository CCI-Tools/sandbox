from datetime import datetime
import xarray as xr
from typing import Union


def extract_time_index(ds: xr.Dataset) -> datetime:
    time_coverage_start = ds.attrs['time_coverage_start']
    time_coverage_end = ds.attrs['time_coverage_end']
    try:
        #print(time_coverage_start, time_coverage_end)
        time_start = datetime.strptime(time_coverage_start, "%Y%m%dT%H%M%SZ")
        time_end = datetime.strptime(time_coverage_end, "%Y%m%dT%H%M%SZ")
        return time_end
    except ValueError:
        return None


def get_lon_dim_name(xarray: Union[xr.DataArray,xr.Dataset]) -> str:
    return get_dim_name(xarray, ['lon', 'longitude', 'long'])


def get_lat_dim_name(xarray: Union[xr.DataArray,xr.Dataset]) -> str:
    return get_dim_name(xarray, ['lat', 'latitude'])


def get_dim_name(xarray: Union[xr.DataArray,xr.Dataset], possible_names) -> str:
    for name in possible_names:
        if name in xarray.dims:
            return name
    return None


def timeseries(xarray: Union[xr.DataArray, xr.Dataset], lat: float, lon: float) -> Union[xr.DataArray, xr.Dataset]:
    lat_dim = get_lat_dim_name(xarray)
    lon_dim = get_lon_dim_name(xarray)
    indexers = {lat_dim : lat, lon_dim :lon}
    return xarray.sel(method='nearest', **indexers)


def subset(xarray: Union[xr.DataArray,xr.Dataset],
           lat_min: float=None, lat_max: float=None,
           lon_min: float=None, lon_max: float=None,
           time_min: datetime=None, time_max: datetime=None):
    indexers = {}

    if lat_min is not None and lat_max is not None:
        lat_dim = get_lat_dim_name(xarray)
        if xarray.coords[lat_dim].to_index().is_monotonic_increasing:
            lat_slice = slice(lat_min, lat_max)
        else:
            lat_slice = slice(lat_max, lat_min)
        indexers[lat_dim] = lat_slice

    if lon_min is not None and lon_max is not None:
        lon_dim = get_lon_dim_name(xarray)
        if xarray.coords[lon_dim].to_index().is_monotonic_increasing:
            lon_slice = slice(lon_min, lon_max)
        else:
            lon_slice = slice(lon_max, lon_min)
        indexers[lon_dim] = lon_slice

    if time_min is not None and time_max is not None:
        indexers['time'] = slice(time_min, time_max)

    return xarray.sel(**indexers)