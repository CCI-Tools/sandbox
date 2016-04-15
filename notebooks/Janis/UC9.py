"""
A prototype implementation of Use Case 9
"""

import xarray as xr
import os
import matplotlib.pyplot as plt
import numpy as np


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

def deg_to_rad(dataset):
    """
    Convert the dataset's lat/lon coordinates from degrees to radians

    :param dataset: xr.Dataset to manipulate
    """
    dataset['lat'] = dataset['lat'] * np.pi / 180.
    dataset['lon'] = dataset['lon'] * np.pi / 180.

def remap_coords(dataset):
    """
    Remap the dataset's lat/lon coordinates frmo -pi-pi and -pi/2 - pi/2 to
    0 - 2pi and 0 - pi respectively.
    :param dataset: dataset to manipulate
    """
    dataset['lat'] = (dataset['lat']) % (2 * np.pi)
    dataset['lon'] = (dataset['lon']) % (2 * np.pi)


# Took this from Marco's code
def ect_adjust_geometry(master: xr.DataArray, slave: xr.DataArray) -> xr.DataArray:
    import scipy.ndimage

    lat_factor = len(master.coords['latitude']) / len(slave.coords['lat'])
    lon_factor = len(master.coords['longitude']) / len(slave.coords['lon'])

    def resample(x):
        y = scipy.ndimage.zoom(x, [lat_factor, lon_factor])
        return xr.DataArray(y)

    # Help! This is soooo slow... few minutes on Norman's PC
    temp_da = slave.groupby('time').apply(resample)
    temp_lon = scipy.ndimage.zoom(slave.lon, [lon_factor])
    temp_lat = scipy.ndimage.zoom(slave.lat, [lat_factor])
    return xr.DataArray(temp_da,
                        name=slave.name,
                        dims=['time', 'lat', 'lon'],
                        coords=dict(time=slave.time, lat=temp_lat, lon=temp_lon),
                        attrs=slave.attrs)

# Read in the data
ds_clouds = read_data(CLOUD_ECV_PATH)
ds_aerosol = read_data(AEROSOL_ECV_PATH)

# Rename the aerosol dataset's coordinates to correspond with clouds
ds_aerosol.rename({'latitude':'lat', 'longitude':'lon'},inplace=True)

# Convert the coordinates to radians
deg_to_rad(ds_clouds)
deg_to_rad(ds_aerosol)

# Change the radian intervals for lat/lon to 0-pi and 0-2pi
remap_coords(ds_clouds)
remap_coords(ds_aerosol)
# Roll the datasets
# Regrid one of the datasets to the grid of the other one.
# Select a spatial region of interest.
# Do correlation analysis on this region. (Do a scatter plot, fit a line to it)

# Select only the variables of interest
aod550 = ds_aerosol.AOD550_mean
cc_total = ds_clouds.cc_total

print(cc_total)
print(aod550)

cc_total.isel(time=0).plot()
plt.show()
