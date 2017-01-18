from cate.core.ds import DATA_STORE_REGISTRY
from cate.core.monitor import ConsoleMonitor
import cate.ops as ops
import xarray as xr
from datetime import datetime
import time

# Open with chunks
t = time.time()
monitor = ConsoleMonitor()
data_store = DATA_STORE_REGISTRY.get_data_store('esa_cci_odp')

print('1')
# sst = xr.open_mfdataset('/home/ccitbx/Desktop/sst/*.nc', chunks = {'lat':36,
#                                                             'lon':72,
#                                                             'time':31},
#                       concat_dim = 'time')
sst = xr.open_mfdataset('/home/ccitbx/Desktop/sst/*.nc', concat_dim = 'time')
print(sst.nbytes * (2 ** -30))
print('2')

# sm = xr.open_mfdataset('/home/ccitbx/Desktop/sm/*.nc', chunks = {'lat':72,
#                                                           'lon':144,
#                                                           'time':31},
#                      concat_dim = 'time')
sm = xr.open_mfdataset('/home/ccitbx/Desktop/sm/*.nc', concat_dim = 'time')
print(sm.nbytes * (2 ** -30))
print('3')

sm_mean = sm.mean('time', keep_attrs=True, skipna=True)
print('4')
sst_mean = sst.mean('time', keep_attrs=True, skipna=True)
print('5')

t_dim = xr.DataArray([datetime(2000,1,1)], name='time')
print('6')

sm_mean_time = xr.concat([sm_mean], t_dim)
print('7')
sst_mean_time = xr.concat([sst_mean], t_dim)
print('8')

# ops.save_dataset(sm_mean_time, '/home/ccitbx/Desktop/sm_mean.nc')
sm_mean_time.load()
print('8.1')
sm_mean_time.to_netcdf('/home/ccitbx/Desktop/sm_mean.nc')
print('9')
# ops.save_dataset(sst_mean_time, '/home/ccitbx/Desktop/sst_mean.nc')
sst_mean_time.load()
print('9.1')
sst_mean_time.to_netcdf('/home/ccitbx/Desktop/sst_mean.nc')
print('10')
print('Elapsed time: {}'.format(time.time()-t))

# Read in as usual and rechunk
t = time.time()
monitor = ConsoleMonitor()
data_store = DATA_STORE_REGISTRY.get_data_store('esa_cci_odp')

sst = ops.open_dataset('esacci.SST.day.L4.SSTdepth.multi-sensor.multi-platform.OSTIA.1-1.r1',
                       '2000-01-01',
                       '2000-01-31', sync=True, monitor=monitor)

sm = ops.open_dataset('esacci.SOILMOISTURE.day.L3S.SSMV.multi-sensor.multi-platform.COMBINED.02-2.r1',
                       '2000-01-01',
                       '2000-01-31', sync=True, monitor=monitor)

sm = sm.chunk(chunks={'lat':72, 'lon':144, 'time':31})
sst = sst.chunk(chunks={'lat':36, 'lon':72, 'time':31})

sm_mean = sm.mean('time', keep_attrs=True, skipna=True)
sst_mean = sst.mean('time', keep_attrs=True, skipna=True)

t_dim = xr.DataArray([datetime(2000,1,1)], name='time')

sm_mean_time = xr.concat([sm_mean], t_dim)
sst_mean_time = xr.concat([sst_mean], t_dim)

ops.save_dataset(sm_mean_time, '/home/ccitbx/Desktop/sm_mean.nc')
ops.save_dataset(sst_mean_time, '/home/ccitbx/Desktop/sst_mean.nc')
print('Elapsed time: {}'.format(time.time()-t))

# Running without chunking fills up system memory, as the default chunking
# is one chunk is one file, in our case there's a full lat/lon chunk per time
# slice. Doing 'mean' tries to access all chunks -> loads them into memory.

#t = time.time()
#monitor = ConsoleMonitor()
#data_store = DATA_STORE_REGISTRY.get_data_store('esa_cci_odp')

#sst = ops.open_dataset('esacci.SST.day.L4.SSTdepth.multi-sensor.multi-platform.OSTIA.1-1.r1',
#                      '2000-01-01',
#                      '2000-01-31', sync=True, monitor=monitor)

#sm = ops.open_dataset('esacci.SOILMOISTURE.day.L3S.SSMV.multi-sensor.multi-platform.COMBINED.02-2.r1',
#                      '2000-01-01',
#                      '2000-01-31', sync=True, monitor=monitor)

#sm_mean = sm.mean('time', keep_attrs=True, skipna=True)
#sst_mean = sst.mean('time', keep_attrs=True, skipna=True)

#t_dim = xr.DataArray([datetime(2000,1,1)], name='time')

#sm_mean_time = xr.concat([sm_mean], t_dim)
#sst_mean_time = xr.concat([sst_mean], t_dim)

#ops.save_dataset(sm_mean_time, '/home/ccitbx/Desktop/sm_mean.nc')
#ops.save_dataset(sst_mean_time, '/home/ccitbx/Desktop/sst_mean.nc')
#print('Elapsed time: {}'.format(time.time()-t))
