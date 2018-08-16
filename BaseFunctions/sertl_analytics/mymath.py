"""
Description: This module contains the math classes for sertl-analytics
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-07-24
"""

import numpy as np


class MyMath:
    @staticmethod
    def divide(dividend: float, divisor: float, round_decimals = 2, return_value_on_error = 0):
        if divisor == 0:
            return return_value_on_error
        return round(dividend/divisor, round_decimals)

    @staticmethod
    def get_change_in_percentage(value_from: float, value_to: float, decimal_round=1) -> float:
        value_change = value_to - value_from
        value_mean = (value_from + value_to)/2
        return round(value_change/value_mean * 100, decimal_round)

    @staticmethod
    def get_change_in_pct(value_from: float, value_to: float, decimal_round=3) -> float:
        value_change = value_to - value_from
        value_mean = (value_from + value_to) / 2
        return round(value_change / value_mean, decimal_round)


class MyPoly1d:
    @staticmethod
    def get_slope_in_decimal_percentage(func: np.poly1d, set_off: int, length: int) -> float:
        """
        Gets the changes of the values for the input function WITHIN the range
        """
        mean_value = np.mean([func(set_off), func(set_off + length)])
        return_value = round((func(set_off + length) - func(set_off))/mean_value, 3)
        return return_value

    @staticmethod
    def get_poly1d(ind_left, value_left, ind_right, value_right) -> np.poly1d:
        """
        Gets the function parameter for the linear function which connects both points on the x-y-diagram
        """
        x = np.array([ind_left, ind_right])
        y = np.array([value_left, value_right])
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        # p[0] = round(p[0], 3)
        # p[1] = round(p[1], 2)
        return p

    @staticmethod
    def get_parallel_through_point(func: np.poly1d, x: float, y: float):
        diff = func(x) - y
        return np.poly1d([func[1], func[0] - diff])


class ToleranceCalculator:
    @staticmethod
    def are_values_in_tolerance_range(val_1: float, val_2: float, tolerance_pct: float):
        test = abs((val_1 - val_2)/np.mean([val_1, val_2]))
        return True if 0 == val_1 == val_2 else abs((val_1 - val_2)/np.mean([val_1, val_2])) < tolerance_pct

    @staticmethod
    def are_values_in_function_tolerance_range(x: list, y: list, f, tolerance_pct: float):
        for k in range(len(x)):
            y_k = y[k]
            f_k = f(x[k])
            if not ToleranceCalculator.are_values_in_tolerance_range(y_k, f_k, tolerance_pct):
                return False
        return True