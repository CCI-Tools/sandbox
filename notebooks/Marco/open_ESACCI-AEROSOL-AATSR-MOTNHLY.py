from datetime import datetime
from glob import glob

import xarray as xr
import pandas as pd

'''
"*-ESACCI-L3C_AEROSOL-AER_PRODUCTS-AATSR-ENVISAT-ADV_MOTNHLY-v2.30.nc"

These product have only 2 dimensions 'latitude' and 'longitude'.
This script creates a dataset with a 3rd dimension covering the 'time' dimension.
The time information is extracted from the global attributes
'time_coverage_start' and 'time_coverage_end'
'''
DIR = "/hdd/home/marcoz/EOData/ccitbx/aerosol_all_monthly"
FILE_GLOB = "*-ESACCI-L3C_AEROSOL-AER_PRODUCTS-AATSR-ENVISAT-ADV_MOTNHLY-v2.30.nc"
file_paths = "%s/%s" % (DIR, FILE_GLOB)


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


def aerosol_open_mfdataset(paths, chunks=None):
    '''
     A special version of the xarray open_mfdataset function.
    '''
    paths = sorted(glob(paths))

    lock = xr.backends.api._default_lock(paths[0], None)
    t1 = datetime.now()
    datasets = [xr.open_dataset(p, lock=lock, chunks=chunks) for p in paths]
    print("num datasets: ", len(datasets))
    t2 = datetime.now()
    file_objs = [ds._file_obj for ds in datasets]
    print("time to open: ", t2-t1)

    t1 = datetime.now()
    time_index = [extract_time_index(ds) for ds in datasets]
    t2 = datetime.now()
    print("time to extract_time_index: ", t2-t1)

    t1 = datetime.now()
    combined = xr.concat(datasets, pd.Index(time_index, name='time'))
    combined._file_obj = xr.backends.api._MultiFileCloser(file_objs)
    t2 = datetime.now()
    print("time to combine: ", t2-t1)

    return combined




print("===================================================")
print("using xarray")
ds = aerosol_open_mfdataset(file_paths)
ds.close()
print("===================================================")
print("using xarray + dask")
ds = aerosol_open_mfdataset(file_paths, chunks={'latitude': 180, 'longitude': 360})
ds.close()
print("===================================================")
print("dimensions: ", ds.dims)

# print(ds)

'''
===================================================
using xarray
num datasets:  117
time to open:                0:00:00.961443
time to extract_time_index:  0:00:00.009316
time to combine:             0:00:06.431711
===================================================
using xarray + dask
num datasets:  117
time to open:                0:00:01.560262
time to extract_time_index:  0:00:00.006279
time to combine:             0:00:01.925776
===================================================
dimensions:  Frozen(SortedKeysDict({'time': 117, 'latitude': 180, 'longitude': 360}))
'''
