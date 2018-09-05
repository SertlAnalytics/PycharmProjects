"""
Description: This module contains the ValueCategorizer classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import pandas as pd
from sertl_analytics.constants.pattern_constants import CN, SVC
from pattern_wave_tick import WaveTick
import numpy as np
import math


class ValueCategorizer:
    __index_column = CN.TIMESTAMP

    def __init__(self, df: pd.DataFrame, f_upper, f_lower, h_upper, h_lower, tolerance_pct_list: list):
        self.df = df
        self.df_length = self.df.shape[0]
        self._f_upper = f_upper
        self._f_lower = f_lower
        self._h_upper = h_upper
        self._h_lower = h_lower
        self.value_category_dic_key_list = []
        self.value_category_dic = {}  # list of value categories by position of each entry
        self._tolerance_pct = tolerance_pct_list[0]
        self._tolerance_pct_equal = tolerance_pct_list[1]
        self.__set_f_upper_f_lower_values__()
        self.__set_h_upper_h_lower_values__()
        self.__calculate_value_categories__()

    def get_number_upper_touches(self, ts_start=0, ts_end=math.inf) -> int:
        return self.count_value_category(SVC.U_on, ts_start, ts_end)

    def get_number_lower_touches(self, ts_start=0, ts_end=math.inf) -> int:
        return self.count_value_category(SVC.L_on, ts_start, ts_end)

    def are_all_values_above_f_lower(self, with_tolerance: bool = False) -> bool:  # TODO with_tolerance
        tolerance = self.df[CN.LOW].mean() * self._tolerance_pct
        df_local = self.df[self.df[CN.LOW] < self.df[CN.F_LOWER] - tolerance]
        return df_local.shape[0] == 0

    def are_all_values_in_value_category(self, value_category: str) -> bool:
        return self.df_length == self.count_value_category(value_category)

    def are_all_values_in_value_category_list(self, value_categories: list) -> bool:
        for key in self.value_category_dic:
            if not set(self.value_category_dic[key]).issubset(set(value_categories)):
                return False
        return True

    def print_data(self):
        print('\nValue categories for u=({}) and l=({}):'.format(self._f_upper, self._f_lower), end='\n')
        for ind, row in self.df.iterrows():
            tick = WaveTick(row)
            print('Pos: {}, Date: {}, H/L:{}/{}, Cat={}'.format(
                tick.position, tick.date_str, tick.high, tick.low, self.value_category_dic[tick.position]))

    def are_helper_functions_available(self):
        return self._h_lower is not None and self._h_upper is not None

    def __set_f_upper_f_lower_values__(self):
        self.df = self.df.assign(F_UPPER=(self._f_upper(self.df[self.__index_column])))
        self.df = self.df.assign(F_LOWER=(self._f_lower(self.df[self.__index_column])))

    def __set_h_upper_h_lower_values__(self):
        if self.are_helper_functions_available():
            self.df = self.df.assign(H_UPPER=(self._h_upper(self.df[self.__index_column])))
            self.df = self.df.assign(H_LOWER=(self._h_lower(self.df[self.__index_column])))

    def count_value_category(self, category: str, ts_start=0, ts_end=math.inf) -> int:
        counter = 0
        filtered_list = [self.value_category_dic[key] for key in self.value_category_dic_key_list
                         if ts_start <= key <= ts_end]
        for category_list in filtered_list:
                if category in category_list:
                    counter += 1
        return counter

    def __calculate_value_categories__(self):
        for ind, row in self.df.iterrows():
            self.value_category_dic_key_list.append(row[self.__index_column])
            self.value_category_dic[row[self.__index_column]] = self.__get_value_categories_for_df_row__(row)

    def __get_value_categories_for_df_row__(self, row) -> list:  # the series is important
        return_list = []
        if self.__is_row_value_equal_f_upper__(row):
            return_list.append(SVC.U_on)
        if self.__is_row_value_in_f_upper_range__(row):
            return_list.append(SVC.U_in)
        if self.__is_row_value_larger_f_upper__(row):
            return_list.append(SVC.U_out)
        if self.__is_row_value_equal_f_lower__(row):
            return_list.append(SVC.L_on)
        if self.__is_row_value_in_f_lower_range__(row):
            return_list.append(SVC.L_in)
        if self.__is_row_value_between_f_lower_f_upper__(row):
            return_list.append(SVC.M_in)
        if self.__is_row_value_smaller_f_lower__(row):
            return_list.append(SVC.L_out)

        if self.are_helper_functions_available():
            self.__get_helper_values_categories_for_df_row__(return_list, row)
        return return_list

    def __get_helper_values_categories_for_df_row__(self, return_list, row):
        if self.__is_row_value_between_h_lower_h_upper__(row):
            return_list.append(SVC.H_M_in)

    def __is_row_value_in_f_upper_range__(self, row):
        return abs(row[CN.HIGH] - row[CN.F_UPPER])/np.mean([row[CN.HIGH], row[CN.F_UPPER]]) <= self._tolerance_pct

    def __is_row_value_in_f_lower_range__(self, row):
        return abs(row[CN.LOW] - row[CN.F_LOWER]) / np.mean([row[CN.LOW], row[CN.F_LOWER]]) <= self._tolerance_pct

    @staticmethod
    def __is_row_value_between_f_lower_f_upper__(row):
        return row[CN.F_LOWER] < row[CN.LOW] <= row[CN.HIGH] < row[CN.F_UPPER]

    @staticmethod
    def __is_row_value_between_h_lower_h_upper__(row):
        return row[CN.H_LOWER] < row[CN.LOW] <= row[CN.HIGH] < row[CN.H_UPPER] and row[CN.CLOSE] > row[CN.F_UPPER]
        # the second condition is needed to get only the values which are in the tail of the TKE pattern.

    def __is_row_value_equal_f_upper__(self, row):
        value_pct = abs(row[CN.HIGH] - row[CN.F_UPPER]) / np.mean([row[CN.HIGH], row[CN.F_UPPER]])
        return value_pct <= self._tolerance_pct_equal

    def __is_row_value_larger_f_upper__(self, row):
        return row[CN.HIGH] > row[CN.F_UPPER] and not self.__is_row_value_in_f_upper_range__(row)

    @staticmethod
    def __is_row_value_smaller_f_upper__(row):
        return row[CN.HIGH] < row[CN.F_UPPER]

    def __is_row_value_equal_f_lower__(self, row):
        value_pct = abs(row[CN.LOW] - row[CN.F_LOWER]) / np.mean([row[CN.LOW], row[CN.F_LOWER]])
        return value_pct <= self._tolerance_pct_equal

    @staticmethod
    def __is_row_value_larger_f_lower__(row):
        return row[CN.LOW] > row[CN.F_LOWER]

    def __is_row_value_smaller_f_lower__(self, row):
        return row[CN.LOW] < row[CN.F_LOWER] and not self.__is_row_value_in_f_lower_range__(row)


class ValueCategorizerHeadShoulder(ValueCategorizer):  # currently we don't need a separate for ...Bottom
    def __init__(self, pattern_range, df: pd.DataFrame, f_upper, f_lower, h_upper, h_lower, tolerance_pct_list: list):
        self._pattern_range = pattern_range
        self._shoulder_timestamps = [self._pattern_range.hsf.tick_shoulder_left.time_stamp,
                                     self._pattern_range.hsf.tick_shoulder_right.time_stamp]
        ValueCategorizer.__init__(self, df, f_upper, f_lower, h_upper, h_lower, tolerance_pct_list)

    def __get_helper_values_categories_for_df_row__(self, return_list, row):
        if row[CN.TIMESTAMP] in self._shoulder_timestamps:
            if self.__is_row_value_equal_h__(row):
                return_list.append(SVC.H_on)
            if self.__is_row_value_in_h_range__(row):
                return_list.append(SVC.H_in)

    def __is_row_value_equal_h__(self, row): # used for HEAD_SHOULDER - both helper are identical
        return self.__are_distance_values_in_tolerance_range__(row, self._tolerance_pct_equal)

    def __is_row_value_in_h_range__(self, row): # used for HEAD_SHOULDER - both helper are identical
        return self.__are_distance_values_in_tolerance_range__(row, self._tolerance_pct * 2.5)

    def __are_distance_values_in_tolerance_range__(self, row, tolerance_pct):
        distance_to_low, distance_to_high = self.__get_distance_values__(row)
        return distance_to_low <= tolerance_pct or distance_to_high <= tolerance_pct

    @staticmethod
    def __get_distance_values__(row):
        distance_to_low = round(abs(row[CN.LOW] - row[CN.H_LOWER]) / np.mean([row[CN.LOW], row[CN.H_LOWER]]), 4)
        distance_to_high = round(abs(row[CN.HIGH] - row[CN.H_LOWER]) / np.mean([row[CN.HIGH], row[CN.H_LOWER]]), 4)
        return distance_to_low, distance_to_high


