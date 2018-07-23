"""
Description: This module contains the ValueCategorizer classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import CN, SVC
from pattern_function_container import PatternFunctionContainer
from pattern_wave_tick import WaveTick
import numpy as np


class ValueCategorizer:
    __index_column = CN.TIMESTAMP

    def __init__(self, function_cont: PatternFunctionContainer, tolerance_pct: float):
        self.function_cont = function_cont
        self.df = function_cont.df
        self.df_length = self.df.shape[0]
        self.__f_upper = function_cont.f_upper
        self.__f_lower = function_cont.f_lower
        self.__h_upper = function_cont.h_upper
        self.__h_lower = function_cont.h_lower
        self.index_list = []
        self.value_category_dic = {}  # list of value categories by position of each entry
        self.__tolerance_pct = tolerance_pct
        self.__tolerance_pct_equal = 0.001
        self.__set_f_upper_f_lower_values__()
        self.__set_h_upper_h_lower_values__()
        self.__calculate_value_categories__()

    def are_all_values_above_f_lower(self, with_tolerance: bool = False) -> bool:  # TODO with_tolerance
        tolerance = self.df[CN.LOW].mean() * self.__tolerance_pct
        df_local = self.df[self.df[CN.LOW] < self.df[CN.F_LOWER] - tolerance]
        return df_local.shape[0] == 0

    def are_all_values_in_value_category(self, value_category: SVC) -> bool:
        return self.df_length == self.get_number_of_rows_with_value_category(value_category)

    def are_all_values_in_value_category_list(self, value_categories: list) -> bool:
        for key in self.value_category_dic:
            if not set(self.value_category_dic[key]).issubset(set(value_categories)):
                return False
        return True

    def get_number_of_rows_with_value_category(self, value_category: SVC) -> bool:
        counter = 0
        for key in self.value_category_dic:
            if value_category in self.value_category_dic[key]:
                counter += 1
        return counter

    def print_data(self):
        print('\nValue categories for u=({}) and l=({}):'.format(self.__f_upper, self.__f_lower), end='\n')
        for ind, row in self.df.iterrows():
            tick = WaveTick(row)
            print('Pos: {}, Date: {}, H/L:{}/{}, Cat={}'.format(
                tick.position, tick.date_str, tick.high, tick.low, self.value_category_dic[tick.position]))

    def are_helper_functions_available(self):
        return self.__h_lower is not None and self.__h_upper is not None

    def __set_f_upper_f_lower_values__(self):
        self.df = self.df.assign(F_UPPER=(self.__f_upper(self.df[self.__index_column])))
        self.df = self.df.assign(F_LOWER=(self.__f_lower(self.df[self.__index_column])))

    def __set_h_upper_h_lower_values__(self):
        if self.are_helper_functions_available():
            self.df = self.df.assign(H_UPPER=(self.__h_upper(self.df[self.__index_column])))
            self.df = self.df.assign(H_LOWER=(self.__h_lower(self.df[self.__index_column])))

    def __calculate_value_categories__(self):
        for ind, row in self.df.iterrows():
            self.index_list.append(row[self.__index_column])
            self.value_category_dic[row[self.__index_column]] = self.__get_value_categories_for_df_row__(row)

    def __get_value_categories_for_df_row__(self, row) -> list:
        pass

    def __is_row_value_in_f_upper_range__(self, row):
        return abs(row[CN.HIGH] - row[CN.F_UPPER])/np.mean([row[CN.HIGH], row[CN.F_UPPER]]) <= self.__tolerance_pct

    def __is_row_value_in_f_lower_range__(self, row):
        return abs(row[CN.LOW] - row[CN.F_LOWER]) / np.mean([row[CN.LOW], row[CN.F_LOWER]]) <= self.__tolerance_pct

    @staticmethod
    def __is_row_value_between_f_lower_f_upper__(row):
        return row[CN.F_LOWER] < row[CN.LOW] <= row[CN.HIGH] < row[CN.F_UPPER]

    @staticmethod
    def __is_row_value_between_h_lower_h_upper__(row):
        return row[CN.H_LOWER] < row[CN.LOW] <= row[CN.HIGH] < row[CN.H_UPPER] and row[CN.CLOSE] > row[CN.F_UPPER]
        # the second condition is needed to get only the values which are in the tail of the TKE pattern.

    def __is_row_value_equal_f_upper__(self, row):
        return abs(row[CN.HIGH] - row[CN.F_UPPER]) / np.mean([row[CN.HIGH], row[CN.F_UPPER]]) \
               <= self.__tolerance_pct_equal

    def __is_row_value_larger_f_upper__(self, row):
        return row[CN.HIGH] > row[CN.F_UPPER] and not self.__is_row_value_in_f_upper_range__(row)

    @staticmethod
    def __is_row_value_smaller_f_upper__(row):
        return row[CN.HIGH] < row[CN.F_UPPER]

    def __is_row_value_equal_f_lower__(self, row):
        return abs(row[CN.LOW] - row[CN.F_LOWER]) / np.mean([row[CN.LOW], row[CN.F_LOWER]]) \
               <= self.__tolerance_pct_equal

    @staticmethod
    def __is_row_value_larger_f_lower__(row):
        return row[CN.LOW] > row[CN.F_LOWER]

    def __is_row_value_smaller_f_lower__(self, row):
        return row[CN.LOW] < row[CN.F_LOWER] and not self.__is_row_value_in_f_lower_range__(row)


class ChannelValueCategorizer(ValueCategorizer):
    def __get_value_categories_for_df_row__(self, row):  # the series is important
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
            if self.__is_row_value_between_h_lower_h_upper__(row):
                return_list.append(SVC.H_M_in)
        return return_list
