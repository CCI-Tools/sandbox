from datetime import datetime
from mz_common import extract_time_index, timeseries, subset, ect_open_mfdataset
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


def combine(datasets):
    time_index = [extract_time_index(ds) for ds in datasets]
    return xr.concat(datasets, pd.Index(time_index, name='time'))


print("===================================================")
print("using xarray")
ds = ect_open_mfdataset(file_paths, combine=combine)
time_series = timeseries(ds['AOD550_mean'], lat=0, lon=0)
sub = subset(ds,
             lat_min=30., lat_max=45.,
             lon_min=-60., lon_max=-45.,
             time_min=datetime(2003, 1, 1), time_max=datetime(2004, 1, 1),
             )
ds.close()
print("===================================================")
print("using xarray + dask")
ds = ect_open_mfdataset(file_paths, chunks={'latitude': 180, 'longitude': 360}, combine=combine)
time_series = timeseries(ds['AOD550_mean'], lat=0, lon=0)
sub = subset(ds,
             lat_min=30., lat_max=45.,
             lon_min=-60., lon_max=-45.,
             time_min=datetime(2003, 1, 1), time_max=datetime(2004, 1, 1),
             )
ds.close()

# print(ds)

'''
===================================================
using xarray
num datasets:  116
TIME for open        :  0:00:00.916795
TIME for combine     :  0:00:02.849429
===================================================
using xarray + dask
num datasets:  116
TIME for open        :  0:00:01.523071
TIME for combine     :  0:00:02.081897
===================================================
dimensions:  Frozen(SortedKeysDict({'time': 116, 'longitude': 360, 'latitude': 180}))
===================================================
              time series (lat/lon)
===================================================
TIME for time_series:  0:00:00.005606

<xarray.DataArray 'AOD550_mean' (time: 116)>
dask.array<getitem..., shape=(116,), dtype=float64, chunksize=(1,)>
Coordinates:
    latitude   float32 0.5
    longitude  float32 0.5
  * time       (time) datetime64[ns] 2002-08-31T23:59:59 2002-09-30T23:59:59 ...
Attributes:
    long_name: mean aerosol optical density at 550 nm
    standard_name: atmosphere_optical_thickness_due_to_ambient_aerosol
    units: 1
    valid_range: [ 0.  4.]

TIME for ts_load     :  0:00:00.394161
===================================================
               subset (lat/lon/time)
===================================================
TIME for subset      :  0:00:00.014428
TIME for subset load :  0:00:00.704024

dimensions:  Frozen(SortedKeysDict({'time': 12, 'longitude': 15, 'latitude': 15}))
===================================================
'''
