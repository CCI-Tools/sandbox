from datetime import datetime
from glob import glob
from mz_common import extract_time_index

import xarray as xr
import pandas as pd


'''
These products have both the 'missing_value' attribute and the '_FillValue'
 attribute. Both are set to NaN and a bug in xarray leads to an error.

 So removing one of the attributes work around that problem.
'''
DIR = "/hdd/home/marcoz/EOData/ccitbx/aerosol"
FILE_GLOB = "200801*-ESACCI-L3C_AEROSOL-AOD-MERIS_ENVISAT-ALAMO-fv2.2.nc"
file_paths = "%s/%s" % (DIR, FILE_GLOB)


def aerosol_open_mfdataset(paths, chunks=None):
    '''
     A special version of the xarray open_mfdataset function.
    '''
    paths = sorted(glob(paths))

    lock = xr.backends.api._default_lock(paths[0], None)
    t1 = datetime.now()
    datasets = [xr.open_dataset(p, lock=lock, chunks=chunks, decode_cf=False) for p in paths]
    print("num datasets: ", len(datasets))
    t2 = datetime.now()
    file_objs = [ds._file_obj for ds in datasets]
    print("time to open: ", t2-t1)

    t1 = datetime.now()
    time_index = [extract_time_index(ds) for ds in datasets]
    t2 = datetime.now()
    print("time to extract_time_index: ", t2-t1)

    t1 = datetime.now()
    for ds in datasets:
        for var in ds.data_vars:
            attrs = ds[var].attrs
            if '_FillValue' in attrs and 'missing_value' in attrs:
                del attrs['missing_value']
    t2 = datetime.now()
    print("time to fix attributes: ", t2-t1)

    t1 = datetime.now()
    combined = xr.concat(datasets, pd.Index(time_index, name='time'))
    combined._file_obj = xr.backends.api._MultiFileCloser(file_objs)
    t2 = datetime.now()
    print("time to combine: ", t2-t1)

    return combined

print("===================================================")
print("using xarray")
ds = aerosol_open_mfdataset(file_paths)
print("===================================================")
print("dimensions: ", ds.dims)

# print(ds)

'''
===================================================
using xarray
num datasets:  2
time to open:                0:00:00.024482
time to extract_time_index:  0:00:00.002655
time to fix attributes:      0:00:00.001082
time to combine:             0:00:00.047702
===================================================
dimensions:  Frozen(SortedKeysDict({'time': 2, 'latitude': 180, 'longitude': 360}))
'''