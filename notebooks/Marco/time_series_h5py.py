import h5py
import os
import numpy
import datetime


file_path = "" # TODO
var_name = "" # TODO
longitude = 0
latitude = 0



def is_y_flipped(variable):
    lat_var = get_lat_var(variable)
    if lat_var is not None:
        return lat_var[0] < lat_var[1]
    return False


def is_lat_lon_image_variable(variable):
    lon_var = get_lon_var(variable)
    if lon_var is not None and lon_var.shape[0] >= 2:
        lat_var = get_lat_var(variable)
        return lat_var is not None and lat_var.shape[0] >= 2
    return False


def get_lon_var(variable):
    return get_dim_var(variable, ['lon', 'longitude', 'long'], -1)


def get_lat_var(variable):
    return get_dim_var(variable, ['lat', 'latitude'], -2)


def get_dim_var(variable, names, pos):
    if len(variable.dims) >= -pos:
        dim = variable.dims[len(variable.dims) + pos]
        for name in names:
            if name in dim:
                dim_var = dim[name]
                if dim_var is not None and len(dim_var.shape) == 1 and dim_var.shape[0] >= 1:
                    return dim_var
    return None

def _get_time_string_from_file_name(file_name):
    base_name, ext = os.path.splitext(file_name)
    if ext != '.nc':
        return None
    name_parts = base_name.split('-')
    # ESACCI-OC-L3S-CHLOR_A-MERGED-1M_MONTHLY_4km_GEO_PML_OC4v6-201312-fv2.0
    # ESACCI-OZONE-L3S-TC-MERGED-DLR_1M-20110401-fv0100
    # 20120101120000-ESACCI-L4_GHRSST-SSTfnd-OSTIA-GLOB_DM-v02.0-fv01.0
    time_part = None
    if len(name_parts) == 8 and name_parts[0] == 'ESACCI' and name_parts[1] == 'OC':
        time_part = name_parts[6]
    elif len(name_parts) == 8 and name_parts[0] == 'ESACCI' and name_parts[1] == 'OZONE':
        time_part = name_parts[6]
    elif len(name_parts) == 8 and name_parts[1] == 'ESACCI' and \
            (name_parts[3] == 'SSTfnd' or name_parts[3] == 'SSTdepth'):
        time_part = name_parts[0]
    # print('time_part =', time_part)
    if time_part:
        time_value = None
        if len(time_part) == 6:
            time_value = datetime.strptime(time_part, '%Y%m')
        elif len(time_part) == 8:
            time_value = datetime.strptime(time_part, '%Y%m%d')
        elif len(time_part) == 14:
            time_value = datetime.strptime(time_part, '%Y%m%d%H%M%S')
        if time_value:
            return datetime.strftime(time_value, '%Y-%m-%d %H:%M:%S')
    return None


time_series = []

dir_name = os.path.dirname(file_path)
file_paths = os.listdir(os.path.dirname(file_path))
for file_name in file_paths:
    var_time = _get_time_string_from_file_name(file_name)
    if not var_time:
        continue
    try:
        file_path = os.path.join(dir_name, file_name)
        print('Opening ', file_path)
        dataset = h5py.File(file_path, 'r')
        variable = dataset[var_name]
        w = variable.shape[-1]
        h = variable.shape[-2]
        x = int(w * (longitude + 180.) / 360. + 0.5)
        if is_y_flipped(variable):
            y = int(h * (latitude + 90.) / 180. + 0.5)
        else:
            y = int(h * (90. - latitude) / 180. + 0.5)
        if x < 0: x = 0
        if y < 0: y = 0
        if x >= w: y = w - 1
        if y >= h: y = h - 1
        print('FileTimeSeries:', x, y, w, h, variable.shape)
        # todo read multiple time values
        if len(variable.shape) == 3:
            var_value = float(variable[0, y, x])
        elif len(variable.shape) == 2:
            var_value = float(variable[y, x])
        elif len(variable.shape) == 4:
            var_value = float(variable[0, 0, y, x])
        else:
            var_value = None
        if var_value and (numpy.isnan(var_value) or var_value == float(variable.fillvalue)):
            var_value = None
        dataset.close()
    except Exception as e:
        print('FileTimeSeries: Error: ' + str(e))
        var_value = None
    time_series.append([var_time, var_value])

sorted(time_series, key=lambda item: item[0])
time_series = list(zip(*time_series))

print('time_series = ' + str(time_series))