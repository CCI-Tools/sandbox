#!/usr/bin/env python
"""
Examples of xarray data sub-setting, using local and remote resources, internal and custom sub-setting method
"""

import time

import xarray as xr


_REMOTE_RESOURCE_ = 'http://esgf-data1.ceda.ac.uk/thredds/dodsC/esg_esacci/sst/data/lt/Analysis/L4/v01.0/1991/09/17/19910917120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_LT-v02.0-fv01.0.nc'
# http download for local resource, http://esgf-data1.ceda.ac.uk/thredds/fileServer/esg_esacci/sst/data/lt/Analysis/L4/v01.0/1991/09/17/19910917120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_LT-v02.0-fv01.0.nc
_LOCAL_RESOURCE_ = '/home/dev/19910917120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_LT-v02.0-fv01.0.nc'


def timeit(method):
    """
    Decorator function, measure and display funtion execution time
    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print ('%r %2.2f sec' % (method.__name__, te-ts))
              
        return result

    return timed


def open_opendap(url: str, vars : [], **kwargs) -> xr.Dataset: # : type = value
    """
    Customize url and opens xarray dataset 
    """
    
    dim_url_template = '[{}:{}:{}]'
    
    #TODO: cache coordinates
    #ds = xr.open_dataset(url)
    #dims = ds.coords.dims;
    
    url_vdim_parmas_dict = dict()
    url_var_params_list = list()
    
    for var in vars:
        url_vdim_parmas_dict[var] = list()
        vdims = ['time', 'lat', 'lon'] #ds[var].coords.dims
        for vdim in vdims: #kwargs:
            if vdim in kwargs and kwargs[vdim] is not None:
                step = kwargs[vdim].step 
                if step is None:
                    step = 1
                dim_url_param = dim_url_template.format(kwargs[vdim].start, step, kwargs[vdim].stop-1)
            else:
                dim_url_param = dim_url_template.format(0, 1, 0)#dims[vdim]-1)
            url_vdim_parmas_dict[var].append(dim_url_param)

        url_var_params_list.append(''.join([var, ''.join(url_vdim_parmas_dict[var])]))

    url_params = ','.join(url_var_params_list)
    #ds.close()
    #print(url_params)
    return xr.open_dataset('?'.join([url, url_params]))
        



@timeit
def read_directly(path: str, variable: str, **args):
    """
    Reads variable values from any netcdf location
    """
    ds = xr.open_dataset(path)
    v = ds[variable]
    a = v[args] 
    a.load()
    
    return a


@timeit
def read_custom_opendap(path: str, variable: str, **args) -> xr.DataArray:
    """
    Reads data from remote location using opendap protocol and data slicing
    """
    ds = open_opendap(path, [variable], **args)
    a = ds[variable]
    a.load()
        
    return a

    
remote_data = read_custom_opendap(_REMOTE_RESOURCE_, 'sea_ice_fraction', time=slice(0,1,1), lat=slice(0, 3600, 10), lon=slice(0, 3600,10))
local_data = read_directly(_LOCAL_RESOURCE_, 'sea_ice_fraction', time=slice(0,1,1), lat=slice(0, 3600, 10), lon=slice(0, 3600, 10))
remote2_data = read_directly(_REMOTE_RESOURCE_, 'sea_ice_fraction', time=slice(0,1,1),lon=slice(0, 3600, 10), lat=slice(0, 3600, 10))


print(remote_data.coords)
print(local_data.coords)
print(remote2_data.coords)



remote_data = read_custom_opendap(_REMOTE_RESOURCE_, 'sea_ice_fraction', time=slice(0,1), lat=slice(1200, 1560), lon=slice(1200, 1560))
local_data = read_directly(_LOCAL_RESOURCE_, 'sea_ice_fraction', time=slice(0,1), lat=slice(1200, 1560), lon=slice(1200, 1560))
remote2_data = read_directly(_REMOTE_RESOURCE_, 'sea_ice_fraction', time=slice(0,1), lat=slice(1200, 1560), lon=slice(1200, 1560))


print(remote_data.coords)
print(local_data.coords)
print(remote2_data.coords)

