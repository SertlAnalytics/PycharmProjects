"""
Description: This module contains the PatternRange class - central for stock data management
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_constants import CN, FT
from pattern_wave_tick import WaveTick
from stock_data_frame import StockDataFrame
from sertl_analytics.functions.math_functions import ToleranceCalculator
import pandas as pd
import numpy as np


class PatternRange:
    def __init__(self, df_min_max: pd.DataFrame, tick: WaveTick, min_length: int):
        self.df_min_max = df_min_max
        self.df_min_max_final = None
        self.tick_list = [tick]
        self.tick_first = tick
        self.tick_last = None  # default
        self.tick_breakout_successor = None
        self.__min_length = min_length
        self.__f_param = None
        self.__f_param_parallel = None  # parallel function through low or high
        self.__f_param_const = None # constant through low or high
        self._f_param_list = []  # contains the possible f_params of the opposite side

    @property
    def f_param(self) -> np.poly1d:
        return self.__f_param

    @property
    def f_param_const(self) -> np.poly1d:
        return self.__f_param_const

    @property
    def f_param_parallel(self) -> np.poly1d:
        return self.__f_param_parallel

    @property
    def range_elements(self) -> int:
        return len(self.tick_list)

    @property
    def position_first(self) -> int:
        return self.tick_first.position

    @property
    def position_last(self) -> int:
        return self.tick_last.position

    @property
    def f_regression(self) -> np.poly1d:
        stock_df = StockDataFrame(self.__get_actual_df_min_max__())
        return stock_df.get_f_regression()

    def __get_actual_df_min_max__(self):
        df_range = self.df_min_max[np.logical_and(
            self.df_min_max[CN.POSITION] >= self.tick_first.position,
            self.df_min_max[CN.POSITION] <= self.tick_last.position)]
        return df_range

    @property
    def position_list(self) -> list:
        return self.__get_position_list__()

    def add_tick(self, tick: WaveTick, f_param):
        self.tick_list.append(tick)
        self.tick_last = tick
        self.__f_param = f_param

    def finalize_pattern_range(self):
        self.df_min_max_final = self.__get_actual_df_min_max__()
        self.__fill_f_param_list__()
        self.__f_param_parallel = self.__get_parallel_function__()
        self.__f_param_const = self.__get_const_function__()

    def get_maximal_trade_size_for_pattern_type(self, pattern_type: str) -> int:
        return self.tick_last.position - self.tick_first.position

    def get_complementary_functions(self, pattern_type: str) -> list:
        if pattern_type == FT.HEAD_SHOULDER:
            return [self.f_param_parallel]
        elif pattern_type == FT.TKE_DOWN:
            return [self.f_param_const]
        else:
            return [] if self._f_param_list is None else self._f_param_list

    def get_related_part_from_data_frame(self, df: pd.DataFrame):
        return df.loc[self.position_first:self.position_last]

    def __fill_f_param_list__(self):
        tick_list = self.__get_tick_list_for_param_list__()
        if len(tick_list) < 2:
            return
        for i in range(0, len(tick_list) - 1):
            for m in range(i + 1, len(tick_list)):
                f_param = self.__get_linear_f_params__(tick_list[i], tick_list[m])
                self.__append_f_param_to_param_list__(f_param, tick_list)

    def __get_parallel_function__(self) -> np.poly1d:
        pass

    def __get_const_function__(self) -> np.poly1d:
        pass

    def __append_f_param_to_param_list__(self, f_param: np.poly1d, tick_list):
        pass

    def __get_tick_list_for_param_list__(self) -> list:
        pass

    @staticmethod
    def __get_linear_f_params__(tick_i: WaveTick, tick_m: WaveTick) -> np.poly1d:
        pass

    @property
    def is_min_length_reached(self) -> bool:
        return self.range_elements >= self.__min_length

    def is_covering_all_positions(self, pos_list_input: list) -> bool:
        return len(set(pos_list_input) & set(self.__get_position_list__())) == len(pos_list_input)

    def print_range_details(self):
        print(self.get_range_details())

    def get_range_details(self):
        position_list = self.__get_position_list__()
        value_list = self.__get_value_list__()
        breakout_successor = self.__get_breakout_details__()
        date_str_list = self.__get_date_str_list__()
        return [position_list, value_list, breakout_successor, date_str_list]

    def are_values_in_function_tolerance_range(self, f_param: np.poly1d, tolerance_pct: float) -> bool:
        for ticks in self.tick_list:
            v_1 = self.__get_value__(ticks)
            v_2 = f_param(ticks.position)
            if not ToleranceCalculator.are_values_in_tolerance_range(v_1, v_2, tolerance_pct):
                return False
        return True

    @property
    def f_param_shape(self):
        stock_df = StockDataFrame(self.__get_actual_df_min_max__())
        return stock_df.get_f_param_shape(self.__f_param)

    @property
    def f_regression_shape(self):
        stock_df = StockDataFrame(self.__get_actual_df_min_max__())
        return stock_df.get_f_regression_shape()

    def __get_position_list__(self) -> list:
        return [tick.position for tick in self.tick_list]

    def __get_value_list__(self) -> list:
        return [self.__get_value__(tick) for tick in self.tick_list]

    def __get_date_str_list__(self) -> list:
        return [tick.date_str for tick in self.tick_list]

    def __get_breakout_details__(self):
        if self.tick_breakout_successor is None:  # extend the breakouts until the end....
            pos = self.df_min_max.iloc[-1][CN.POSITION]
        else:
            pos = self.tick_breakout_successor.position
        return [pos, round(self.__f_param(pos), 2)]

    @staticmethod
    def __get_value__(tick: WaveTick):
        return tick.high


class PatternRangeMax(PatternRange):
    @staticmethod
    def __get_value__(tick: WaveTick):
        return tick.high

    def __get_parallel_function__(self) -> np.poly1d:
        stock_df = StockDataFrame(self.df_min_max_final)
        return stock_df.get_parallel_to_function_by_low(self.f_param)

    def __get_const_function__(self) -> np.poly1d:
        return np.poly1d([0, self.df_min_max_final[CN.LOW].min()])

    def __get_tick_list_for_param_list__(self) -> list:
        df = self.df_min_max_final[self.df_min_max_final[CN.IS_MIN]]
        return [WaveTick(row) for ind, row in df.iterrows()]

    @staticmethod
    def __get_linear_f_params__(tick_i: WaveTick, tick_m: WaveTick) -> np.poly1d:
        return tick_i.get_linear_f_params_for_low(tick_m)

    def __append_f_param_to_param_list__(self, f_param: np.poly1d, tick_list):
        for ticks in tick_list:
            if ticks.low < f_param(ticks.position):
                return
        self._f_param_list.append(f_param)


class PatternRangeMin(PatternRange):
    @staticmethod
    def __get_value__(tick: WaveTick):
        return tick.low

    def __get_parallel_function__(self) -> np.poly1d:
        stock_df = StockDataFrame(self.df_min_max_final)
        return stock_df.get_parallel_to_function_by_high(self.f_param)

    def __get_const_function__(self) -> np.poly1d:
        return np.poly1d([0, self.df_min_max_final[CN.HIGH].max()])

    def __get_tick_list_for_param_list__(self) -> list:
        df = self.df_min_max_final[self.df_min_max_final[CN.IS_MAX]]
        return [WaveTick(row) for ind, row in df.iterrows()]

    @staticmethod
    def __get_linear_f_params__(tick_i: WaveTick, tick_m: WaveTick) -> np.poly1d:
        return tick_i.get_linear_f_params_for_high(tick_m)

    def __append_f_param_to_param_list__(self, f_param: np.poly1d, tick_list):
        for ticks in tick_list:
            if ticks.high > f_param(ticks.position):
                return
        self._f_param_list.append(f_param)


class PatternRangeDetector:
    def __init__(self, df_min_max: pd.DataFrame, tolerance_pct: float):
        self.df_min_max = df_min_max
        self.df = self.__get_df_for_processing__(df_min_max)  # only min or max ticks
        self.df_length = self.df.shape[0]
        self._number_required_ticks = 3
        self.__tolerance_pct = tolerance_pct
        self.__pattern_range_list = []
        self.__parse_data_frame__()

    def get_pattern_range_list(self) -> list:
        return self.__pattern_range_list

    def get_pattern_range_shape_list(self) -> list:
        return [p.f_param_shape for p in self.__pattern_range_list]

    def get_pattern_range_regression_shape_list(self) -> list:
        return [p.f_regression_shape for p in self.__pattern_range_list]

    def print_list_of_possible_pattern_ranges(self):
        for pattern_range in self.__pattern_range_list:
            print(pattern_range.print_range_details())

    def are_pattern_ranges_available(self) -> bool:
        return len(self.__pattern_range_list) > 0

    def __get_df_for_processing__(self, df_min_max: pd.DataFrame):
        pass

    def __add_pattern_range_to_list_after_check__(self, pattern_range: PatternRange):
        if self.__are_conditions_fulfilled_for_adding_to_pattern_range_list__(pattern_range):
            pattern_range.finalize_pattern_range()
            self.__pattern_range_list.append(pattern_range)

    def __are_conditions_fulfilled_for_adding_to_pattern_range_list__(self, pattern_range: PatternRange) -> bool:
        if pattern_range is None:
            return False
        if not pattern_range.is_min_length_reached:
            return False
        # check if this list is already a sublist of an earlier list
        for pattern_range_old in self.__pattern_range_list:
            if pattern_range_old.is_covering_all_positions(pattern_range.position_list):
                return False
        return True

    def __parse_data_frame__(self):
        for i in range(0, self.df_length - self._number_required_ticks):
            tick_i = WaveTick(self.df.iloc[i])
            pattern_range = self.__get_pattern_range_by_tick__(tick_i)
            for k in range(i+1, self.df_length):
                tick_k = WaveTick(self.df.iloc[k])
                if pattern_range.range_elements == 1:
                    pattern_range.add_tick(tick_k, None)
                elif self.__is_end_for_single_check_reached__(pattern_range, tick_i, tick_k):
                    pattern_range.tick_breakout_successor = tick_k
                    self.__add_pattern_range_to_list_after_check__(pattern_range)
                    pattern_range = self.__get_pattern_range_by_tick__(tick_i)
                    pattern_range.add_tick(tick_k, None)
            self.__add_pattern_range_to_list_after_check__(pattern_range)  # for the latest...

    def __get_linear_f_params__(self, tick_i: WaveTick, tick_k: WaveTick) -> np.poly1d:
        pass

    def __is_end_for_single_check_reached__(self, pattern_range: PatternRange, tick_i: WaveTick, tick_k: WaveTick):
        f_param_new = self.__get_linear_f_params__(tick_i, tick_k)
        if pattern_range.are_values_in_function_tolerance_range(f_param_new, self.__tolerance_pct):
            pattern_range.add_tick(tick_k, f_param_new)
        else:
            f_value_new_last_position_right = f_param_new(pattern_range.tick_last.position)
            if self.__is_new_tick_a_breakout__(pattern_range, f_value_new_last_position_right):
                return True
        return False

    def __is_new_tick_a_breakout__(self, pattern_range: PatternRange, f_value_new_last_position_right: float):
        pass

    def __get_pattern_range_by_tick__(self, tick: WaveTick) -> PatternRange:
        pass


class PatternRangeDetectorMax(PatternRangeDetector):
    def __get_df_for_processing__(self, df_min_max: pd.DataFrame):
        return df_min_max[df_min_max[CN.IS_MAX]]

    def __get_linear_f_params__(self, tick_i: WaveTick, tick_k: WaveTick) -> np.poly1d:
        return tick_i.get_linear_f_params_for_high(tick_k)

    def __is_new_tick_a_breakout__(self, pattern_range: PatternRange, f_value_new_last_position_right: float):
        return pattern_range.tick_last.high < f_value_new_last_position_right

    def __get_pattern_range_by_tick__(self, tick: WaveTick) -> PatternRange:
        return PatternRangeMax(self.df_min_max, tick, self._number_required_ticks)


class PatternRangeDetectorMin(PatternRangeDetector):
    def __get_df_for_processing__(self, df_min_max: pd.DataFrame):
        return df_min_max[df_min_max[CN.IS_MIN]]

    def __get_linear_f_params__(self, tick_i: WaveTick, tick_k: WaveTick) -> np.poly1d:
        return tick_i.get_linear_f_params_for_low(tick_k)

    def __is_new_tick_a_breakout__(self, pattern_range: PatternRange, f_value_new_last_position_right: float):
        return pattern_range.tick_last.low > f_value_new_last_position_right

    def __get_pattern_range_by_tick__(self, tick: WaveTick) -> PatternRange:
        return PatternRangeMin(self.df_min_max, tick, self._number_required_ticks)
