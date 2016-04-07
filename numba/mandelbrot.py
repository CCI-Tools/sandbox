#!/usr/bin/env python
"""
Compute and plot the Mandelbrot set using matplotlib.
"""

import time

import numpy as np
import pylab

from numba import jit


@jit
def mandel(x, y, max_iters):
    """
    Given the real and imaginary parts of a complex number,
    determine if it is a candidate for membership in the Mandelbrot
    set given a fixed number of iterations.
    """
    c = complex(x, y)
    z = 0j
    for i in range(max_iters):
        z = z * z + c
        if z.real * z.real + z.imag * z.imag >= 4:
            return 255 * i // max_iters

    return 255


@jit(nopython=True)
def create_fractal(min_x, max_x, min_y, max_y, image, iters):
    height = image.shape[0]
    width = image.shape[1]

    pixel_size_x = (max_x - min_x) / width
    pixel_size_y = (max_y - min_y) / height
    for x in range(width):
        real = min_x + x * pixel_size_x
        for y in range(height):
            imag = min_y + y * pixel_size_y
            color = mandel(real, imag, iters)
            image[y, x] = color

    return image


image = np.zeros((1400, 2800), dtype=np.uint8)

t0 = time.time()
create_fractal(-2.5, 1.5, -1.0, 1.0, image, 200)
t1 = time.time()

print(t1 - t0, 'seconds')

pylab.imshow(image)
pylab.gray()
pylab.show()
