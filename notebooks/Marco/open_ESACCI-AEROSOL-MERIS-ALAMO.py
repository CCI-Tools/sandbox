from mz_common import extract_time_index, ect_open_mfdataset
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


def preprocess(ds: xr.Dataset) -> xr.Dataset:
    for var in ds.data_vars:
        attrs = ds[var].attrs
        if '_FillValue' in attrs and 'missing_value' in attrs:
            del attrs['missing_value']
    return ds


def combine(datasets):
    time_index = [extract_time_index(ds) for ds in datasets]
    return xr.concat(datasets, pd.Index(time_index, name='time'))


print("===================================================")
print("using xarray")
ds = ect_open_mfdataset(file_paths, decode_cf=False, preprocess=preprocess, combine=combine)

# print(ds)

'''
===================================================
using xarray
num datasets:  2
TIME for open        :  0:00:00.035506
TIME for preprocess  :  0:00:00.000928
TIME for combine     :  0:00:00.048516
===================================================
dimensions:  Frozen(SortedKeysDict({'time': 2, 'longitude': 360, 'latitude': 180}))
'''