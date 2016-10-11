"""
Testing geospatial data resampler using ndimage map_coords
"""

import xarray as xr
import os
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

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

def resample_slice_mc(slice_, grid_lon, grid_lat, order=1):
    """
    Resample a single time slice of a larger xr.DataArray. The slice can be
    multidimensional.

    :param slice_: xr.DataArray single time slice
    :param grid_lon: meshgrid of longitudes for the new grid
    :param grid_lat: meshgrid of latitudes for the new grid
    :param order: Interpolation method 0 - nearest neighbour, 1 - bilinear (default), 3 - cubic spline
    :return: xr.DataArray, resampled slice
    """
    # For now do this only for lat,lon
    # I have a set of new lat/lon values and I have a set of old lat/lon values, I have to resample to the new lat/lon values,
    # but map_coords takes in float indices of the 'old' grid and interpolate the values on those. Hence, I have to 
    # interpolate the new desired lat/lons with respect to the old values in order to find the corresponding indices.

    # Get the indices that correspond to lat/lon values. Because map_coords works with indices only.
    interpolator_lon = interp1d(slice_['lon'], np.arange(0,len(slice_['lon'])), fill_value="extrapolate")
    interpolator_lat = interp1d(slice_['lat'], np.arange(0,len(slice_['lat'])), fill_value="extrapolate")

    # Create the coordinates' meshgrid
    coords = np.meshgrid(interpolator_lat(grid_lat.values), interpolator_lon(grid_lon.values))
    mapped = ndimage.map_coordinates(slice_.values, coords, mode='nearest', order=1)
    return xr.DataArray(mapped)

# Read in the data
ds_clouds = read_data(CLOUD_ECV_PATH)
ds_aerosol = read_data(AEROSOL_ECV_PATH)

# Rename the aerosol dataset's coordinates to correspond with clouds
ds_aerosol.rename({'latitude':'lat', 'longitude':'lon'},inplace=True)

# Select only the variables of interest
aod550 = ds_aerosol.AOD550_mean
cc_total = ds_clouds.cc_total

aer_slice = aod550.isel(time=0)
cc_slice = cc_total.isel(time=0)

aer_resampled = resample_slice_mc(aer_slice, cc_slice['lon'], cc_slice['lat'])
cc_resampled = resample_slice_mc(cc_slice, aer_slice['lon'], aer_slice['lat'])

cc_resampled.plot()
plt.show()

aer_resampled.plot()
plt.show()
