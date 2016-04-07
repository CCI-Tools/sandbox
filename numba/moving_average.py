#!/usr/bin/env python
"""
A moving average function using @guvectorize.
"""

import time

import numpy as np

from numba import guvectorize


@guvectorize(['void(float64[:], intp[:], float64[:])'], '(n),()->(n)')
def move_mean(a, window_arr, out):
    window_width = window_arr[0]
    asum = 0.0
    count = 0
    for i in range(window_width):
        asum += a[i]
        count += 1
        out[i] = asum / count
    for i in range(window_width, len(a)):
        asum += a[i] - a[i - window_width]
        out[i] = asum / count


iarr = np.arange(2000000, dtype=np.float64).reshape(2000, 1000)

t0 = time.time()
oarr = move_mean(iarr, 4)
t1 = time.time()
print(t1 - t0, 'seconds')

print(iarr)
print(oarr)
