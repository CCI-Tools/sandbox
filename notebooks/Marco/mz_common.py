from datetime import datetime
import xarray as xr



def extract_time_index(ds: xr.Dataset):
    time_coverage_start = ds.attrs['time_coverage_start']
    time_coverage_end = ds.attrs['time_coverage_end']
    try:
        #print(time_coverage_start, time_coverage_end)
        time_start = datetime.strptime(time_coverage_start, "%Y%m%dT%H%M%SZ")
        time_end = datetime.strptime(time_coverage_end, "%Y%m%dT%H%M%SZ")
        return time_end
    except ValueError:
        return None


def get_lon_dim_name(da: xr.DataArray):
    return get_dim_name(da, ['lon', 'longitude', 'long'])


def get_lat_dim_name(da: xr.DataArray):
    return get_dim_name(da, ['lat', 'latitude'])


def get_dim_name(da: xr.DataArray, possible_names):
    for name in possible_names:
        if name in da.dims:
            return name
    return None


def get_timeseries(da: xr.DataArray, lat: float, lon: float):
    lat_dim = get_lat_dim_name(da)
    lon_dim = get_lon_dim_name(da)
    indexers = {lat_dim : lat, lon_dim :lon}
    return da.sel(method='nearest', **indexers)