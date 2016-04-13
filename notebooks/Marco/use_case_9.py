import os
import xarray as xr


ecv_base = '/home/marcoz/EOData/ccitbx/'
ecv_dirs = {'oc': 'oc', 'sst': 'sst'}


def ect_load_ds(name) -> xr.Dataset:
    pattern = os.path.join(ecv_base, ecv_dirs[name], '*.nc')
    return xr.open_mfdataset(pattern)


def match_slice_order_to_index(data_array_coord: xr.DataArray, slice_index: slice) -> slice:
    if not data_array_coord.to_index().is_monotonic_increasing:
        return slice(slice_index.stop, slice_index.start)
    else:
        return slice_index


def ect_regional_subset(da: xr.DataArray, lat_slice: slice, lon_slice: slice) -> xr.DataArray:
    new_lat_slice = match_slice_order_to_index(da.coords['lat'], lat_slice)
    new_lon_slice = match_slice_order_to_index(da.coords['lon'], lon_slice)
    return da.sel(lat=new_lat_slice, lon=new_lon_slice)


def ect_adjust_geometry(master: xr.DataArray, slave: xr.DataArray) -> xr.DataArray:
    import scipy.ndimage

    lat_factor = len(master.coords['lat']) / len(slave.coords['lat'])
    lon_factor = len(master.coords['lon']) / len(slave.coords['lon'])

    def resample(x):
        y = scipy.ndimage.zoom(x, [lat_factor, lon_factor])
        return xr.DataArray(y)

    # Help! This is soooo slow... few minutes on Norman's PC
    temp_da = slave.groupby('time').apply(resample)
    print(temp_da)
    temp_lon = scipy.ndimage.zoom(slave.lon, [lon_factor])
    print(temp_lon)
    temp_lat = scipy.ndimage.zoom(slave.lat, [lat_factor])
    return xr.DataArray(temp_da,
                        name=slave.name,
                        dims=['time', 'lat', 'lon'],
                        coords=dict(time=slave.time, lat=temp_lat, lon=temp_lon),
                        attrs=slave.attrs)


## Step 1 - Read two ECVs
sst_ds = ect_load_ds('sst')
oc_ds = ect_load_ds('oc')

# select one Variable from each ECV
chla_da = oc_ds.chlor_a.isel(time=slice(0,1))
sst_da = sst_ds.analysed_sst.isel(time=slice(0,1))

print("DONE: Step 1 - Read two ECVs")
#========================================================

## Step 2 - Geometric Adjustments
# We make the OC data apply to spatial resolution of SST, because the latter is lower.
chla_da_low = ect_adjust_geometry(master=sst_da, slave=chla_da)

print("DONE: Step 2 - Geometric Adjustments")
#========================================================

## Step 3 - Spatial Subsetting
lat_slice = slice(30., 45.)
lon_slice = slice(-60., -45.)

chla_da_sub = ect_regional_subset(chla_da_low, lat_slice=lat_slice, lon_slice=lon_slice)
sst_da_sub = ect_regional_subset(sst_da, lat_slice=lat_slice, lon_slice=lon_slice)

print("DONE: Step 3 - Spatial Subsetting")
#========================================================

print(chla_da_sub)
print(sst_da_sub)




