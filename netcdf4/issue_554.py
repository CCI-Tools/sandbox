"""
See
* https://github.com/Unidata/netcdf4-python/issues/554
* https://github.com/pydata/xarray/issues/822
"""

import netCDF4
import numpy as np

ds = netCDF4.Dataset('../notebooks/norman/20100101120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_LT-v02.0-fv01.1.nc')
sst_var = ds.variables['analysed_sst']
new_dtype = np.dtype('<i2')
#sst_var.dtype = new_dtype
#sst_data = sst_var[:, :, :]
index = (slice(None, None), slice(None, None), slice(None, None))
sst_data = sst_var.__getitem__(index)
#sst_data = sst_data.astype('<i2')
sst_value = sst_data[0, 235, 0]
# prints 206.58 but should be 272.9 Kelvin
print(sst_value, 'Celsius')
