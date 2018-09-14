"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from scipy import stats
import numpy as np

max_value_list = []
value_summary_list = []
stop_loss_summary_list = []
result_list = []

for k in range(0, 10):
    stop_loss_list = []
    x = np.random.random(10)
    x = x.round(2)
    value_summary_list.append(list(x))
    dist_bottom = 1
    stop_loss = - dist_bottom
    max_value_list.append(x.max())
    for m in range(2, 10):
        stop_loss_list.append(stop_loss)
        x_short = x[:m]
        x_short_sorted_reverse = sorted(x_short, reverse=True)
        current_value = x_short[-1]
        if current_value < stop_loss:
            break
        else:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_short, x_short_sorted_reverse)
            stop_loss = round(max(stop_loss, current_value - dist_bottom * (1 - std_err)), 2)
    stop_loss_summary_list.append(stop_loss_list)
    result_list.append(stop_loss)

print('Max_value_list: {}'.format(max_value_list))
print('Result_list: {}'.format(result_list))
for k in range(0, 10):
    print(' value_list: {}'.format(value_summary_list[k]))
    print(' stop_loss_list: {}'.format(stop_loss_summary_list[k]))



