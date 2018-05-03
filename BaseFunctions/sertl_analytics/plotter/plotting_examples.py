import numpy as np
import matplotlib.pyplot as plt

x = np.array([0.0, 1.0, 2.0, 3.0,  4.0,  5.0])
y = np.array([0.0, 0.8, 0.9, 0.1, -0.8, -1.0])
z_1 = np.polyfit(x, y, 1)  # linear asymptotically
z_2 = np.polyfit(x, y, 2)  # quadratic asymptotically
z_3 = np.polyfit(x, y, 3)  # cubic asymptotically

p_1 = np.poly1d(z_1)
p_2 = np.poly1d(z_2)
p_3 = np.poly1d(z_3)

plt.plot(x, y, 'r', label = 'orig')
plt.plot(x, p_1(x), 'g', label = 'linear')
plt.plot(x, p_2(x), 'y', label = 'quadratic')
plt.plot(x, p_3(x), 'k', label = 'cubic')

print(p_1(2))
print(p_1(5))
# plt.plot(x, z, 'r')
plt.legend(loc=0)
plt.show()
