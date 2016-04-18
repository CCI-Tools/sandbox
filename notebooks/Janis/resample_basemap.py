"""
Testing geospatial data resampler using matplotlib basemap interp.
"""

import xarray as xr
import os
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import basemap
import time


# This is just a prototype, hence the hard coded paths
CLOUD_ECV_PATH = '/home/ccitbx/cci_data/cloud/2008/'
AEROSOL_ECV_PATH = '/home/ccitbx/cci_data/aerosol/2008_monthly/'


def read_data(path):
    """
    Read in multiple netCDF files and combine them in an xarray dataset.

    :rtype: xr.Dataset
    :param path: Path to the folder
    :return: The resulting dataset
    """
    path = path + os.sep + '*.nc'
    print(path)
    dataset = xr.open_mfdataset(path, concat_dim='time')
    return dataset

def resample_slice(slice, grid_lon, grid_lat, order=1):
    """
    Resample a single time slice of a larger xr.DataArray

    :param slice: xr.DataArray single slice
    :param grid_lon: meshgrid of longitudes for the new grid
    :param grid_lat: meshgrid of latitudes for the new grid
    :param order: Interpolation method 0 - nearest neighbour, 1 - bilinear (default), 3 - cubic spline
    :return: xr.DataArray, resampled slice
    """
    result = basemap.interp(slice.values, slice['lon'].data, slice['lat'].data, grid_lon, grid_lat)
    return xr.DataArray(result)


def resample_array(array, lon, lat, order=1):
    """
    Resample the given xr.DataArray to a new grid defined by grid_lat and grid_lon

    :param array: xr.DataArray with lat,lon and time coordinates
    :param lat: 'lat' xr.DataArray attribute for the new grid
    :param lon: 'lon' xr.DataArray attribute for the new grid
    :param order: 0 for nearest-neighbor interpolation, 1 for bilinear interpolation,
    3 for cubic spline (default 1). order=3 requires scipy.ndimage.
    :return: None, changes 'array' in place.
    """
    # Don't do anything if this DataArray has different dims than expected
    if 'time' not in array.dims or 'lat' not in array.dims or 'lon' not in array.dims:
        return array

    #if array.dims != (('time','lat','lon')):
    #    return array

    print(array.name)
    print(array.dims)

    grid_lon, grid_lat = np.meshgrid(lon.data, lat.data)
    kwargs = {'grid_lon':grid_lon, 'grid_lat':grid_lat}
    temp_array = array.groupby('time').apply(resample_slice, **kwargs)
    chunks = list(temp_array.shape[1:])
    chunks.insert(0,1)
    return xr.DataArray(temp_array.values,
                        name = array.name,
                        dims = array.dims,
                        coords = {'time':array.time, 'lat':lat, 'lon':lon},
                        attrs = array.attrs).chunk(chunks=chunks)

def resample_dataset(master, slave, order=1):
    """
    Resample slave onto the grid of the master.
    This does spatial resampling the whole dataset, e.g., all
    variables in the slave dataset that have (time, lat, lon) dimensions.

    :param master: xr.Dataset whose lat/lon coordinates are used as the resampling grid
    :param slave: xr.Dataset that will be resampled on the masters' grid
    :param order: Interpolation method to use. 0 - nearest neighbour, 1 - bilinear, 3 - cubic spline
    :return: xr.Dataset The resampled slave
    """
    lon = master['lon']
    lat = master['lat']
    kwargs = {'lon':lon, 'lat':lat, 'order':order}
    return slave.apply(resample_array, **kwargs)


# Read in the data
ds_clouds = read_data(CLOUD_ECV_PATH)
ds_aerosol = read_data(AEROSOL_ECV_PATH)
print(ds_clouds)

# Rename the aerosol dataset's coordinates to correspond with clouds
ds_aerosol.rename({'latitude':'lat', 'longitude':'lon'},inplace=True)

# Select only the variables of interest
aod550 = ds_aerosol.AOD550_mean
cc_total = ds_clouds.cc_total

print('Resampling the monthly cloud cover cc_total variable from a 0.5 degree global lat/lon grid to a 1 degree grid.')
t0 = time.time()
cc_total_resampled = resample_array(cc_total, aod550['lon'], aod550['lat'], order=0)
t1 = time.time()
print('Resampling using Nearest Neighbour interpolation took ' + str(t1-t0) + ' seconds.')

t0 = time.time()
cc_total_resampled = resample_array(cc_total, aod550['lon'], aod550['lat'], order=1)
t1 = time.time()
print('Resampling using Bilinear interpolation took ' + str(t1-t0) + ' seconds.')

t0 = time.time()
cc_total_resampled = resample_array(cc_total, aod550['lon'], aod550['lat'], order=3)
t1 = time.time()
print('Resampling using Cubic Spline interpolation took ' + str(t1-t0) + ' seconds.')

#ds_clouds_resampled = resample_dataset(ds_aerosol, ds_clouds)
#print(ds_clouds_resampled)
#print(ds_clouds.cot_ctp_hist2d)
#cot_resampled =resample_array(ds_clouds.cot_ctp_hist2d, aod550['lon'], aod550['lat'], order=3)
#print(cot_resampled)

print(cc_total)
plt.figure(1)
plt.subplot(211)
cc_total.isel(time=0).plot()
cc_total_resampled = resample_array(cc_total, aod550['lon'], aod550['lat'], order=3)
print(cc_total_resampled)
plt.subplot(212)
cc_total_resampled.isel(time=0).plot()
plt.show()

