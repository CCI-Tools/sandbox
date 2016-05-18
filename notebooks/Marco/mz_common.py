from datetime import datetime
from glob import glob
from typing import Union
import xarray as xr


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


def ect_open_mfdataset(paths, chunks=None, concat_dim=None, preprocess=None, combine=None, engine=None, **kwargs):
    '''
        Adapted version of the xarray 'open_mfdataset' function.
    '''
    if isinstance(paths, str):
        paths = sorted(glob(paths))
    if not paths:
        raise IOError('no files to open')

    # open all datasets
    t1 = datetime.now()
    lock = xr.backends.api._default_lock(paths[0], None)
    datasets = [xr.open_dataset(p, engine=engine, chunks=chunks, lock=lock, **kwargs) for p in paths]
    print("num datasets: ", len(datasets))
    file_objs = [ds._file_obj for ds in datasets]
    t2 = datetime.now()
    print("TIME for open        : ", t2-t1)

    preprocessed_datasets = datasets
    if preprocess is not None:
        # pre-process datasets
        t1 = datetime.now()
        preprocessed_datasets = []
        file_objs = []
        for ds in datasets:
            pds = preprocess(ds)
            if (pds is not None):
                preprocessed_datasets.append(pds)
                file_objs.append(pds._file_obj)
            else:
                ds._file_obj.close()
        t2 = datetime.now()
        print("TIME for preprocess  : ", t2-t1)

    # combine datasets into a single
    t1 = datetime.now()
    if combine is not None:
        combined_ds = combine(datasets)
    else:
        combined_ds = xr.auto_combine(datasets, concat_dim=concat_dim)
    t2 = datetime.now()
    print("TIME for combine     : ", t2-t1)

    combined_ds._file_obj = xr.backends.api._MultiFileCloser(file_objs)
    return combined_ds
