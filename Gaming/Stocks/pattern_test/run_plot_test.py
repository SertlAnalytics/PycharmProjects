"""
Description: This module contains  a test case for class variables compared with instance variables
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

np.random.seed(12345678)
# x = np.random.random(10)
x = np.array([1 + k for k in range(0, 36)])
# y = np.random.random(10)
y = np.array([7364, 6704, 6503, 6446, 6203, 6260, 6317, 6289, 6339, 6498, 6492, 6524, 6501, 6273, 6353, 6400, 6512, 6754, 6721, 6702, 6601, 6439, 6474, 6684, 6635, 6604, 6630, 6581, 6542, 6490, 6557, 6626, 6589, 6591, 6656, 6617])
# slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

np_array = np.polyfit(x, y, 1)
intercept = np_array[1]
slope = np_array[0]
y_reg = np.array([intercept + x_value*slope for x_value in x])
y_changed_by_reg = y - y_reg

slope, intercept, r_value, p_value, std_err = stats.linregress(y, y_reg)

std_y_reg = y_reg.std()
std_y = y.std()
std_y_changed_by_reg = y_changed_by_reg.std()

print('slope={}, intercept={}, str_err={}'.format(slope, intercept, std_err))

print("r-squared:", r_value**2)  # r-squared: 0.08040226853902833
# Plot the data along with the fitted line

plt.plot(x, y, 'o', label='original data')
plt.plot(x, intercept + slope*x, 'r', label='fitted line')
plt.legend()
plt.show()


