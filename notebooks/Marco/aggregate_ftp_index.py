import sys
import os
from glob import glob
import re

YEAR_RE = re.compile("\d\d\d\d")
NETCDF_RE = re.compile(".+\.nc\.info")
SKIP_DIRS = ["png", "sinusoidal", "IMAGES", "ancillary", "L2"]

if len(sys.argv) == 2:
    top_data_dirs = glob(sys.argv[1] + "/*/data/")
elif len(sys.argv) == 3:
    top_data_dirs = glob(sys.argv[1] + "/" + sys.argv[2] + "/data/")
else:
    print("usage:")


def all_dirs_are_years(dnames: [str]):
    num_year_dirs = 0
    for dname in dnames:
        if not YEAR_RE.match(dname):
            return False
        else:
            num_year_dirs += 1
    return num_year_dirs > 0


def contains_only_netcdf(dnames, fnames):
    for fname in fnames:
        if not NETCDF_RE.match(fname):
            return False
    return len(dnames) == 0


class EcvInfo:
    def __init__(self, example):
        self._example = example
        self._pattern = list(example)
        self._count = 1

    def handle(self, name):
        self._count += 1
        for i, c in enumerate(name):
            if self._pattern[i] == "." or self._pattern[i] == c:
                pass
            else:
                self._pattern[i] = "."

    @property
    def count(self):
        return self._count

    @property
    def pattern(self):
        return ''.join(self._pattern)

    @property
    def len(self):
        return len(self._pattern)

    def __str__(self):
        return "{0}[{1}]".format(self.pattern, str(self.count))


def ecv_info(ecv_dir):
    dates = []
    ecv_patterns = {}
    num_netcdf_files = 0
    for dirpath, dnames, fnames in os.walk(ecv_dir):
        sub_dir = dirpath[len(ecv_dir) + 1:]
        if len(dnames) == 0:
            dates.append(sub_dir)
        for fname in fnames:
            if NETCDF_RE.match(fname):
                num_netcdf_files += 1
                if len(sub_dir) > 0:
                    sub_path = sub_dir + "/" + fname
                else:
                    sub_path = fname
                fnl = len(sub_path)
                if fnl in ecv_patterns:
                    if ecv_patterns[fnl].len == fnl:
                        ecv_patterns[fnl].handle(sub_path)
                    else:
                        ecv_patterns[fnl] = EcvInfo(sub_path)
                else:
                    ecv_patterns[fnl] = EcvInfo(sub_path)

    dates.sort()
    head, tail = os.path.split(ecv_dir)
    info_file_name = head + "/" + tail + ".info"
    if (os.path.exists(info_file_name)):
        with open(info_file_name, "r") as info_file:
            info_lines = info_file.readlines()
        size_in_bytes = info_lines[0].split(",")[1]
        size_in_MB = '{0:,}'.format(int(float(size_in_bytes) / 1024.0 / 1024.0))
    else:
        size_in_MB = '0'

    cci = ecv_dir.split("/")[1]
    dir = "/".join(ecv_dir.split("/")[3:])
    result = []
    for aECV in ecv_patterns:
        num_netcdf_files =  '{0:,}'.format(ecv_patterns[aECV].count)
        result.append([cci, dir, dates[0], dates[-1], num_netcdf_files, size_in_MB, ecv_patterns[aECV].pattern[:-5]])
        dir = dir+"*"
    return result


def pprintTable(header, lr, table):
    """Prints out a table of data, padded for alignment
    Each row must have the same number of columns. """

    def _get_max_width(table1, index1):
        """Get the maximum width of the given column index"""
        return max([len(str(row1[index1])) for row1 in table1])

    def _print_header(col_paddings, row):
        for i in range(len(row)):
            print(row[i].center(col_paddings[i] + 1), end=" |")
        print()

    def _print_sep(col_paddings, row):
        for i in range(len(row)):
            print('-' * (col_paddings[i] + 1), end=" |")
        print()

    def _print_row(col_paddings, col_lr, row):
        for col_index in range(len(row)):
            if col_lr[col_index] == 'l':
                print(str(row[col_index]).ljust(col_paddings[col_index] + 1), end=" |")
            else:
                print(str(row[col_index]).rjust(col_paddings[col_index] + 1), end=" |")
        print()

    col_paddings = []
    for col_index in range(len(header)):
        col_paddings.append(max([_get_max_width(table, col_index), len(str(header[col_index]))]))

    _print_header(col_paddings, header)
    _print_sep(col_paddings, header)
    for row in table[1:]:
        _print_row(col_paddings, lr, row)
    return


ECV_HEADER = ['cci', 'dir', 'start', 'end', '#netcdf', 'size MB', 'file pattern']
ECV_LR = ['l', 'l', 'r', 'r', 'r', 'r', 'l']
ECVs = []
special_dirs = []
for data_dir in top_data_dirs:
    for dirpath, dnames, fnames in os.walk(data_dir):
        for skip_dir in SKIP_DIRS:
            if skip_dir in dnames:
                dnames.remove(skip_dir)

        # check if dir above is already in, then remove that one
        for special_dir in special_dirs:
            if dirpath.startswith(special_dir):
                special_dirs.remove(special_dir)

        if all_dirs_are_years(dnames):
            ECVs.extend(ecv_info(dirpath))
            dnames.clear()
        elif contains_only_netcdf(dnames, fnames):
            ECVs.extend(ecv_info(dirpath))
        else:
            special_dirs.append(dirpath)

print("SPECIAL")
print("\n".join(special_dirs))
print("# special=" + str(len(special_dirs)))

# print("ECVs")
# ECVs.sort(key=lambda x: x[0])
# pprintTable(ECV_HEADER, ECV_LR, ECVs)
#
# print("# ECVs=" + str(len(ECVs) - 1))

