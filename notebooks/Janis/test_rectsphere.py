"""
This is an example test for scipy RectSphereBivariateSpline interpolator.
It is meant to be used for approximation of a rectangular grid on a sphere,

e.g., for lat/lon interpolation.
"""
import numpy as np
from scipy.interpolate import RectSphereBivariateSpline
import matplotlib.pyplot as plt

lats = np.linspace(10, 170, 9) * np.pi / 180.
lons = np.linspace(0, 350, 18) * np.pi / 180.
data = np.dot(np.atleast_2d(90. - np.linspace(-80., 80., 18)).T,
               np.atleast_2d(180. - np.abs(np.linspace(0., 350., 9)))).T

new_lats = np.linspace(1, 180, 180) * np.pi / 180
new_lons = np.linspace(1, 360, 360) * np.pi / 180
new_lats, new_lons = np.meshgrid(new_lats, new_lons)

lut = RectSphereBivariateSpline(lats, lons, data)
data_interp = lut.ev(new_lats.ravel(),
                     new_lons.ravel()).reshape((360, 180)).T

fig = plt.figure()
ax1 = fig.add_subplot(211)
ax1.imshow(data, interpolation='nearest')
ax2 = fig.add_subplot(212)
ax2.imshow(data_interp, interpolation='nearest')
plt.show()
