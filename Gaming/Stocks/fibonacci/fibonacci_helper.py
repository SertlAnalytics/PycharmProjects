"""
Description: This module contains the constants used mainly for pattern detections - but can be used elsewhere.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
from sertl_analytics.constants.pattern_constants import FR, FD
from pattern_wave_tick import WaveTick


class FibonacciHelperApi:
    def __init__(self, wave_type: str, tick_start: WaveTick):
        self.wave_type = wave_type
        self.tick_start = tick_start
        self.comp_reg_ret_pct_list = None
        self.comp_reg_ret_value_list = None
        self.comp_duration_list = None


class FibonacciHelper:
    def __init__(self):
        self.base_retracement_array = np.array([FR.R_236, FR.R_382, FR.R_618, FR.R_764])
        self.retracement_array_for_plotting = np.array([FR.R_000, FR.R_236, FR.R_382, FR.R_618, FR.R_764, FR.R_100])

    def is_value_a_fibonacci_relation(self, value: float, tolerance_pct: float = 0.1):
        min_distance, fib_value = self.get_distance_to_closest_fibonacci_relation(value)
        return min_distance < fib_value * tolerance_pct

    def get_forecast_candidate_list(self, api: FibonacciHelperApi) -> list:
        duration_previous_reg = api.comp_duration_list[2]
        return_list = []

        if api.comp_reg_ret_value_list[0] > api.comp_reg_ret_value_list[2]:  # first regression is biggest
            possible_fib_relations = self.__get_smaller_equal_fibonacci_relation_list__(api.comp_reg_ret_pct_list[2])
        else:
            possible_fib_relations = self.__get_other_fibonacci_relation_list__(api)

        for fib_relations in possible_fib_relations:
            forecast_value = api.comp_reg_ret_value_list[2] * fib_relations
            if api.wave_type == FD.ASC:
                forecast_value = api.tick_start.low + forecast_value
            else:
                forecast_value = api.tick_start.high - forecast_value

            if forecast_value > 0:
                forecast_pos = int(api.tick_start.position + duration_previous_reg * fib_relations)
                single_entry = [fib_relations, round(forecast_value, 2), forecast_pos]
                return_list.append(single_entry)
        return return_list

    def __get_smaller_equal_fibonacci_relation_list__(self, value):
        return_list = []
        integer_part = int(value)
        for k in range(integer_part, integer_part-1, -1):
            for fib_number in self.base_retracement_array:
                if fib_number + k <= value:
                    return_list.append(fib_number + k)
        return return_list

    def __get_other_fibonacci_relation_list__(self, api: FibonacciHelperApi):
        """
        Handles the case where the second regression component is bigger than the first.
        => the last one is either of the same length as the first or a fib_relation > 1
        """
        last_retracement_pct = api.comp_reg_ret_pct_list[3]
        if last_retracement_pct > FR.R_618 + 0.1:
            return []
        fib_value = api.comp_reg_ret_pct_list[2]
        integer_part = int(fib_value)
        fib_decimal = fib_value - integer_part
        # 1. Since by default the second regression is a fibonacci regression - we take the first the reciprocal value
        return_list = [1/fib_value]
        # 2. Append some other values
        return_list.append(integer_part + 1 - fib_decimal)
        return_list.append(fib_value + 1)
        return [round(value, 3) for value in return_list]

    def get_closest_fibonacci_relation(self, value: float) -> float:
        min_distance, fib_value = self.get_distance_to_closest_fibonacci_relation(value)
        return fib_value

    def get_distance_to_closest_fibonacci_relation(self, value: float) -> float:
        integer_part = int(value)
        decimal_part = value - integer_part
        modified_retracement_array = np.abs(self.base_retracement_array - decimal_part)
        arg_min = np.argmin(modified_retracement_array)
        return modified_retracement_array[arg_min], self.base_retracement_array[arg_min]


fibonacci_helper = FibonacciHelper()