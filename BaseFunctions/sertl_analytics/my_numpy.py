"""
Description: This module contains different numpy helper classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-14
"""

import numpy as np
from sertl_analytics.mydates import MyDate


class MyNumpy:
    @staticmethod
    def get_date_values_as_number_for_date_time_array(date_values: list) -> np.array:
        number_array = np.array(date_values).reshape(-1, 1)
        for i in range(len(number_array)):
            number_array[i] = MyDate.get_number_for_date_time(number_array[i][0])
        return number_array

