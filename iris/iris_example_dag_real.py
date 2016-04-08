"""
Quickplot of a 2d cube on a map
===============================

This example demonstrates a contour plot of global air temperature.
The plot title and the labels for the axes are automatically derived from the metadata.

"""
import copy

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

import iris
import iris.plot as iplt
import iris.quickplot as qplt

import numpy as np

def main():
    fname = iris.sample_data_path('air_temp.pp')

    temperature_orig = iris.load_cube(fname)

    temperature_noisy = copy.deepcopy(temperature_orig)
    sx = (temperature_orig.data.shape)[0]
    sy = (temperature_orig.data.shape)[1]
    gaussian_noise = np.random.normal(loc=0.0, scale=5, size=(sx, sy))
    gaussian_noise[:sx/4, :] = 0
    gaussian_noise[(3*sx)/4:, :] = 0
    gaussian_noise[:, sy/4:(3*sy)/4] = 0
    temperature_noisy.data =  -temperature_noisy.data + gaussian_noise

    #Original data
    plt.figure(figsize=(12, 5))
    plt.subplot(221)
    qplt.contourf(temperature_orig, 15)
    plt.gca().coastlines()

    #Noisy data
    plt.subplot(222)
    qplt.contourf(temperature_noisy, 15)
    plt.gca().coastlines()

    # Plot scatter
    scatter_x = temperature_orig.data.flatten()
    scatter_y = temperature_noisy.data.flatten()
    plt.subplot(223)
    plt.plot(scatter_x, scatter_y, '.', label="scatter")
    coeffs = np.polyfit(scatter_x, scatter_y, 1)
    print(coeffs)
    plt.title("Scatter plot")
    plt.xlabel("orig [K]")
    plt.ylabel("noisy [K]")
    fitted_y = np.polyval(coeffs, scatter_x)
    plt.plot(scatter_x, fitted_y, 'k', label="fit")
    plt.text(np.min(scatter_x), np.max(fitted_y), "\nax+b\na=%f3\nb=%g4" % (coeffs[0], coeffs[1]))

    #Plot
    diff_y = scatter_y - fitted_y
    temperature_diff = copy.deepcopy(temperature_orig)
    temperature_diff.data = diff_y.reshape(temperature_noisy.data.shape)
    temperature_diff.standard_name = None
    temperature_diff.long_name = "Residual from fitted curve"
    temperature_diff.var_name = "Hello_World"


    plt.subplot(224)
    qplt.contourf(temperature_diff, 15)
    plt.gca().coastlines()



    iplt.show()

if __name__ == '__main__':
    main()
