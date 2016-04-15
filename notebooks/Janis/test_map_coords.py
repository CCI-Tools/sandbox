import numpy as np
from scipy import ndimage

a = np.arange(12).reshape((4,3))

# Construct a mesh grid for look-up coordinates
coords = np.array([[[ 0.0,  0.0,  0.0],
                   [ 1.0,  1.0,  1.0],
                   [ 2.0,  2.0,  2.0],
                   [ 3.0,  3.0,  3.0]],

                  [[ 0.0,  1.0,  2.0],               
                   [ 0.0,  1.0,  2.0],
                   [ 0.0,  1.0,  2.0],
                   [ 0.0,  1.0,  2.0]]])

mapped = ndimage.map_coordinates(a, coords, mode='nearest')
print(mapped)
