from datetime import datetime
from typing import List
import xarray as xr

from ect.core.op import op, op_input, op_return, op_output


def _get_lon_dim_name(xarray: xr.Dataset) -> str:
    return _get_dim_name(xarray, ['lon', 'longitude', 'long'])


def _get_lat_dim_name(xarray: xr.Dataset) -> str:
    return _get_dim_name(xarray, ['lat', 'latitude'])


def _get_dim_name(xarray: xr.Dataset, possible_names: List[str]) -> str:
    for name in possible_names:
        if name in xarray.dims:
            return name
    return None


@op_input('dataset', not_none=True)
@op_input('lat_min', value_range=[-90, 90])
@op_input('lat_max', value_range=[-90, 90])
@op_input('lon_min', value_range=[-180, 180])
@op_input('lon_max', value_range=[-180, 180])
@op_input('time_min')
@op_input('time_max')
def subset(dataset: xr.Dataset,
           lat_min: float=None, lat_max: float=None,
           lon_min: float=None, lon_max: float=None,
           time_min: datetime=None, time_max: datetime=None)-> xr.Dataset:

    indexers = {}

    if lat_min is not None and lat_max is not None:
        lat_dim_name = _get_lat_dim_name(dataset)
        if lat_dim_name is None:
            raise ValueError("Can not identify 'lat' dimension")
        if dataset.coords[lat_dim_name].to_index().is_monotonic_increasing:
            lat_slice = slice(lat_min, lat_max)
        else:
            lat_slice = slice(lat_max, lat_min)
        indexers[lat_dim_name] = lat_slice

    if lon_min is not None and lon_max is not None:
        lon_dim_name = _get_lon_dim_name(dataset)
        if lon_dim_name is None:
            raise ValueError("Can not identify 'lon' dimension")
        if dataset.coords[lon_dim_name].to_index().is_monotonic_increasing:
            lon_slice = slice(lon_min, lon_max)
        else:
            lon_slice = slice(lon_max, lon_min)
        indexers[lon_dim_name] = lon_slice

    if time_min is not None and time_max is not None and 'time' in dataset.dims:
        indexers['time'] = slice(time_min, time_max)

    sub = dataset.sel(**indexers)
    return sub

from ect.core.util import extend

ss = subset
@extend(xr.Dataset, 'gridtools')
class Subset:
    def __init__(self, dataset: xr.Dataset):
        self.dataset = dataset

    def subset(self,lat_min: float=None, lat_max: float=None,
               lon_min: float=None, lon_max: float=None,
               time_min: datetime=None, time_max: datetime=None):
        return ss(self.dataset)


####
xrds = xr.open_dataset("")
xrds_sub = xrds.gridttools.subset()
