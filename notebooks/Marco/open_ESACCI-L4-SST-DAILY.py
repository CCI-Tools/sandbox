from datetime import datetime
from mz_common import timeseries, subset, ect_open_mfdataset

DIR = "/hdd/home/marcoz/EOData/ccitbx/sst_many"
YEAR_FILE_GLOB = "2000*120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_LT-v02.0-fv01.1.nc"
SOME_DAYS_FILE_GLOB = "2000010[1,2,3]120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_LT-v02.0-fv01.1.nc"

print("===================================================")
print("using xarray (3 days)")
ds = ect_open_mfdataset("%s/%s" % (DIR, SOME_DAYS_FILE_GLOB), engine='h5netcdf', concat_dim="time")
ts = timeseries(ds['analysed_sst'], lat=0, lon=0)
sub = subset(ds,
             lat_min=30., lat_max=45.,
             lon_min=-60., lon_max=-45.,
             )
ds.close()

print("===================================================")
print("using xarray + dask (3 days)")
ds = ect_open_mfdataset("%s/%s" % (DIR, SOME_DAYS_FILE_GLOB), chunks={'lat': 900, 'lon': 1800}, engine='h5netcdf',
                        concat_dim="time")
ts = timeseries(ds['analysed_sst'], lat=0, lon=0)
sub = subset(ds,
             lat_min=30., lat_max=45.,
             lon_min=-60., lon_max=-45.,
             )
ds.close()

print("===================================================")
print("using xarray + dask (1 year)")
ds = ect_open_mfdataset("%s/%s" % (DIR, YEAR_FILE_GLOB), chunks={'lat': 900, 'lon': 1800}, engine='h5netcdf',
                        concat_dim="time")
ts = timeseries(ds['analysed_sst'], lat=0, lon=0)
sub = subset(ds,
             lat_min=30., lat_max=45.,
             lon_min=-60., lon_max=-45.,
             time_min=datetime(2003, 1, 1), time_max=datetime(2004, 1, 1),
             )
ds.close()

'''
===================================================
using xarray (3 days)
num datasets:  3
TIME for open        :  0:00:00.202182
TIME for combine     :  0:00:04.096742
===================================================
using xarray + dask (3 days)
num datasets:  3
TIME for open        :  0:00:00.119849
TIME for combine     :  0:00:00.060847
===================================================
using xarray + dask (1 year)
num datasets:  366
TIME for open        :  0:00:15.474201
TIME for combine     :  0:00:07.600017
===================================================
dimensions:  Frozen(SortedKeysDict({'lat': 3600, 'lon': 7200, 'bnds': 2, 'time': 366}))
===================================================
              time series (lat/lon)
===================================================
TIME for time_series:  0:00:00.575770

<xarray.DataArray 'analysed_sst' (time: 366)>
dask.array<getitem..., shape=(366,), dtype=float64, chunksize=(1,)>
Coordinates:
    lon      float32 0.025
    lat      float32 0.025
  * time     (time) datetime64[ns] 2000-01-01T12:00:00 2000-01-02T12:00:00 ...
Attributes:
    long_name: analysed sea surface temperature
    valid_max: [4500]
    depth: 20 cm
    standard_name: sea_water_temperature
    source: ATSR<1,2>-ESACCI-L3U-v1.0, AATSR-ESACCI-L3U-v1.0, AVHRR<12,14,15,16,17,18>_G-ESACCI-L2P-v1.0, AVHRRMTA-ESACCI-L2P-v1.0
    comment: SST analysis produced for ESA SST CCI project using the OSTIA system in reanalysis mode.
    units: kelvin
    valid_min: [-300]

TIME for ts_load     :  0:00:09.502877
===================================================
               subset (lat/lon/time)
===================================================
TIME for subset      :  0:00:00.015677
TIME for subset load :  0:00:00.187682

dimensions:  Frozen(SortedKeysDict({'lat': 300, 'lon': 300, 'bnds': 2, 'time': 0}))
===================================================
'''
