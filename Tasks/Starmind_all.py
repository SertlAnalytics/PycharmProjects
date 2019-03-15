"""
Guten Tag Herr Sertl

Die Firma Starmind wünscht, dass Sie die folgende Aufgabe lösen.
Given are two groups of 2-dimensional (x,y) coordinates.

group1 = [[0.067, 0.21], [0.092, 0.21],
  [0.294, 0.445], [0.227, 0.521], [0.185, 0.597],
  [0.185, 0.689], [0.235, 0.748], [0.319, 0.773],
  [0.387, 0.739], [0.437, 0.672], [0.496, 0.739],
  [0.571, 0.773], [0.639, 0.765], [0.765, 0.924],
  [0.807, 0.933], [0.849, 0.941]]

group2 = [[0.118, 0.143], [0.118, 0.176],
  [0.345, 0.378], [0.395, 0.319], [0.437, 0.261],
  [0.496, 0.328], [0.546, 0.395], [0.605, 0.462],
  [0.655, 0.529], [0.697, 0.597], [0.706, 0.664],
  [0.681, 0.723], [0.849, 0.798], [0.857, 0.849],
  [0.866, 0.899]]

Please determine an equation for a linear separator for these two groups of points. Attach your solution, preferably as a Jupyter notebook.

Ich bitte Sie, mir die Lösung zwecks Weiterleitung zuzustellen.

Freundliche Grüsse
Lucas Baldauf

IT-Personalberater
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
import math


xy_1 = np.array([[0.067, 0.21], [0.092, 0.21],
  [0.294, 0.445], [0.227, 0.521], [0.185, 0.597],
  [0.185, 0.689], [0.235, 0.748], [0.319, 0.773],
  [0.387, 0.739], [0.437, 0.672], [0.496, 0.739],
  [0.571, 0.773], [0.639, 0.765], [0.765, 0.924],
  [0.807, 0.933], [0.849, 0.941]])

# Now we generate the labels for these values, all=1
z_1 = np.ones(xy_1.shape[0])

xy_2 = np.array([[0.118, 0.143], [0.118, 0.176],
  [0.345, 0.378], [0.395, 0.319], [0.437, 0.261],
  [0.496, 0.328], [0.546, 0.395], [0.605, 0.462],
  [0.655, 0.529], [0.697, 0.597], [0.706, 0.664],
  [0.681, 0.723], [0.849, 0.798], [0.857, 0.849],
  [0.866, 0.899]])

# Now we generate the labels for these values, all=0
z_2 = np.zeros(xy_2.shape[0])

# Let's plot the points
x_1 = xy_1[:, 0]
y_1 = xy_1[:, 1]

x_2 = xy_2[:, 0]
y_2 = xy_2[:, 1]

plt.scatter(x_1, y_1, marker='^')
plt.scatter(x_2, y_2, marker='o')

# combine them into one X and label vector y
X = np.concatenate((xy_1, xy_2), axis=0)
y = np.concatenate((z_1, z_2), axis=0)

# get the range for the x-axis for the plot
ls_min = math.floor(np.min(X, axis=0)[0])
ls_max = math.ceil(np.max(X, axis=0)[0])

# use linear regression
reg = linear_model.LinearRegression()
reg.fit(X, y)
print('reg.intercept_ = {}, reg.coef_ = {}'.format(reg.intercept_, reg.coef_))
# result: reg.intercept_ = 0.22208241206874768, reg.coef_ = [-1.99798784  2.13941823]

# calculate the parameters (constant and slope) for the linear regression function
w = reg.coef_
slope = -w[0] / w[1]
constant = reg.intercept_ / w[1]
print('function: y = {:.4f} + {:.4f} * x'.format(constant, slope))  # result: function: y = 0.1038 + 0.9339 * x
xx = np.linspace(ls_min, ls_max)
yy = constant + slope * xx

# now plot the linear regression function values
plt.plot(xx, yy, 'k-')
plt.show()

# C = 1  # SVM regularization parameter
# clf = svm.SVC(kernel='linear', gamma=0.7, C=C )
# clf.fit(X, y)

# w = clf.coef_[0]
# a = -w[0] / w[1]
# xx = np.linspace(ls_min, ls_max)
# yy = a * xx - (clf.intercept_[0]) / w[1]

# x = np.array([0.0, 1.0, 2.0, 3.0,  4.0,  5.0])
# y = np.array([0.0, 0.8, 0.9, 0.1, -0.8, -1.0])
# z_1 = np.polyfit(x, y, 1)  # linear asymptotically
# z_2 = np.polyfit(x, y, 2)  # quadratic asymptotically
# z_3 = np.polyfit(x, y, 3)  # cubic asymptotically
#
# p_1 = np.poly1d(z_1)
# p_2 = np.poly1d(z_2)
# p_3 = np.poly1d(z_3)
#
# plt.plot(x, y, 'r', label = 'orig')
# plt.plot(x, p_1(x), 'g', label = 'linear')
# plt.plot(x, p_2(x), 'y', label = 'quadratic')
# plt.plot(x, p_3(x), 'k', label = 'cubic')
#
# print(p_1(2))
# print(p_1(5))
# # plt.plot(x, z, 'r')
# plt.legend(loc=0)
# plt.show()


