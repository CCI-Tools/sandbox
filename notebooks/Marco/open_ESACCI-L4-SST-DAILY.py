from datetime import datetime
from glob import glob

import xarray as xr

DIR = "/hdd/home/marcoz/EOData/ccitbx/sst_many"
YEAR_FILE_GLOB = "2000*120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_LT-v02.0-fv01.1.nc"
SOME_DAYS_FILE_GLOB = "2000010[1,2,3]120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_LT-v02.0-fv01.1.nc"


def sst_open_mfdataset(paths, engine=None, chunks=None):
    '''
     A special version of the xarray open_mfdataset function.
    '''
    paths = sorted(glob(paths))

    lock = xr.backends.api._default_lock(paths[0], None)
    t1 = datetime.now()
    datasets = [xr.open_dataset(p, lock=lock, engine=engine, chunks=chunks) for p in paths]
    print("num datasets: ", len(datasets))
    t2 = datetime.now()
    file_objs = [ds._file_obj for ds in datasets]
    print("time to open: ", t2-t1)

    t1 = datetime.now()
    combined = xr.auto_combine(datasets, concat_dim="time")
    combined._file_obj = xr.backends.api._MultiFileCloser(file_objs)
    t2 = datetime.now()
    print("time to combine: ", t2-t1)

    return combined


print("===================================================")
print("using xarray (3 days)")
ds = sst_open_mfdataset("%s/%s" % (DIR, SOME_DAYS_FILE_GLOB), engine='h5netcdf')
ds.close()
print("===================================================")
print("using xarray + dask (3 days)")
ds = sst_open_mfdataset("%s/%s" % (DIR, SOME_DAYS_FILE_GLOB), chunks={'lat': 900, 'lon': 1800}, engine='h5netcdf')
ds.close()
print("===================================================")
print("using xarray + dask (1 year)")
ds = sst_open_mfdataset("%s/%s" % (DIR, YEAR_FILE_GLOB), chunks={'lat': 900, 'lon': 1800}, engine='h5netcdf')
print("===================================================")
print("dimensions: ", ds.dims)

# print(ds)

'''
===================================================
using xarray (3 days)
num datasets:  3
time to open:     0:00:00.222461
time to combine:  0:00:05.687535
===================================================
using xarray + dask (3 days)
num datasets:  3
time to open:     0:00:00.133154
time to combine:  0:00:00.062160
===================================================
using xarray + dask (1 year)
num datasets:  366
time to open:     0:00:16.738448
time to combine:  0:00:06.852269
===================================================
dimensions:  Frozen(SortedKeysDict({'lon': 7200, 'bnds': 2, 'time': 366, 'lat': 3600}))
'''

