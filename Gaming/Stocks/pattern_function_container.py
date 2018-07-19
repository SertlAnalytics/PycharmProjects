"""
Description: This module contains the PatternFunctionContainer class - central function calculations
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import CN, FD, FT
from sertl_analytics.functions import math_functions
from pattern_wave_tick import WaveTick
import numpy as np
import pandas as pd
from pattern_data_container import pattern_data_handler as pdh


class PatternFunctionContainer:
    def __init__(self, df: pd.DataFrame, f_lower: np.poly1d = None, f_upper: np.poly1d = None):
        self.df = df
        self._tick_for_helper = None
        self._tick_first = WaveTick(self.df.iloc[0])
        self._tick_last = WaveTick(self.df.iloc[-1])
        self._tick_distance = pdh.pattern_data.tick_f_var_distance
        self._f_lower = f_lower
        self._f_upper = f_upper
        self._h_lower = f_lower
        self._h_upper = f_upper
        self._f_regression = self.__get_f_regression__()
        self._f_var_cross_f_upper_f_lower = 0
        self._position_cross_f_upper_f_lower = 0
        self._breakout_direction = None
        self._pattern_direction = self.__get_pattern_direction__()
        if self.is_valid():
            self.__init_tick_for_helper__()
            self.__set_f_var_cross_f_upper_f_lower__()

    @property
    def is_pattern_type_configured_for_helper_functions(self) -> bool:
        return False

    def __get_pattern_direction__(self):
        if self.is_valid():
            return FD.ASC if self._f_upper[1] + self._f_lower[1] > 0 else FD.DESC
        else:
            return FD.ASC if self._f_regression[1] >= 0 else FD.DESC

    @property
    def number_of_positions(self):
        return self._tick_last.position - self._tick_first.position

    @property
    def position_first(self):
        return self._tick_first.position

    @property
    def position_last(self):
        return self._tick_last.position

    @property
    def tick_first(self):
        return self._tick_first

    @property
    def tick_last(self):
        return self._tick_last

    @property
    def pattern_direction(self):
        return self._pattern_direction

    @property
    def f_var_cross_f_upper_f_lower(self):
        return self._f_var_cross_f_upper_f_lower

    @property
    def position_cross_f_upper_f_lower(self):
        return self._position_cross_f_upper_f_lower

    @property
    def f_lower(self):
        return self._f_lower

    @property
    def f_upper(self):
        return self._f_upper

    @property
    def h_lower(self):
        return self._h_lower

    @property
    def h_upper(self):
        return self._h_upper

    @property
    def f_regression(self):
        return self._f_regression

    @property
    def f_upper_pct(self):
        return self.__get_slope_in_decimal_percentage__(self._f_upper)

    @property
    def f_lower_pct(self):
        return self.__get_slope_in_decimal_percentage__(self._f_lower)

    @property
    def f_regression_pct(self):
        return self.__get_slope_in_decimal_percentage__(self._f_regression)

    def __get_slope_in_decimal_percentage__(self, func: np.poly1d):
        off_set = self._tick_first.f_var
        length = self.number_of_positions * self._tick_distance
        return math_functions.MyPoly1d.get_slope_in_decimal_percentage(func, off_set, length)

    def __set_breakout_direction__(self, breakout_direction: str):
        self._breakout_direction = breakout_direction

    def __get_breakout_direction__(self):
        return self._breakout_direction

    breakout_direction = property(__get_breakout_direction__, __set_breakout_direction__)

    def is_regression_value_in_pattern_for_f_var(self, f_var: int):
        return self._f_lower(f_var) <= self._f_regression(f_var) <= self._f_upper(f_var)

    def is_valid(self):
        return not(self._f_lower is None or self._f_upper is None)

    def is_tick_breakout(self, tick: WaveTick):
        upper_boundary_value = self.get_upper_value(tick.f_var)
        lower_boundary_value = self.get_lower_value(tick.f_var)
        return not (lower_boundary_value <= tick.close <= upper_boundary_value)

    def is_tick_inside_pattern_range(self, tick: WaveTick):
        return self.get_upper_value(tick.f_var) >= self.get_lower_value(tick.f_var)

    def add_tick_from_main_df_to_df(self, df_main: pd.DataFrame, tick: WaveTick):
        if tick is not None:
            self._tick_last = tick
            self.df = pd.concat([self.df, df_main.loc[tick.position:tick.position]])

    def __get_f_regression__(self) -> np.poly1d:
        np_array = np.polyfit(self.df[CN.DATEASNUM], self.df[CN.CLOSE], 1)
        return np.poly1d([np_array[0], np_array[1]])

    def __set_f_var_cross_f_upper_f_lower__(self):
        if self._f_upper[1] < self._f_lower[1]:
            # for n in range(self._tick_last.f_var, self._tick_last.f_var + 3 * self.number_of_positions):
            #     u = self._f_upper(n)
            #     l = self._f_lower(n)
            #     if self._f_upper(n) < self._f_lower(n):
            #         self._f_var_cross_f_upper_f_lower = n - 1
            #         print('OLD: self._f_var_cross_f_upper_f_lower = {}'.format(n - 1))
            #         break

            for n in range(self._tick_last.position, self._tick_last.position + 3 * self.number_of_positions):
                f_var = self._tick_last.f_var + (n - self._tick_last.position) * pdh.pattern_data.tick_f_var_distance
                u = self._f_upper(f_var)
                l = self._f_lower(f_var)
                if self._f_upper(f_var) < self._f_lower(f_var):
                    self._f_var_cross_f_upper_f_lower = f_var - pdh.pattern_data.tick_f_var_distance
                    self._position_cross_f_upper_f_lower = n - 1
                    break

    def __get_tick_for_helper__(self):
        return self._tick_for_helper

    def __set_tick_for_helper__(self, tick):
        self._tick_for_helper = tick
        self._h_upper = np.poly1d([0, self._f_upper(tick.f_var)])
        self._h_lower = np.poly1d([0, self._f_lower(tick.f_var)])

    tick_for_helper = property(__get_tick_for_helper__, __set_tick_for_helper__)

    def set_tick_for_breakout(self, tick: WaveTick):
        self.__set_tick_for_helper__(tick)

    def adjust_functions_when_required(self, tick: WaveTick):
        pass

    def get_upper_value(self, f_var: int):
        return round(self._f_upper(f_var), 2)

    def get_lower_value(self, f_var: int):
        return round(self._f_lower(f_var), 2)

    def get_tick_function_list_for_xy_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        f_upper_extended = self.get_upper_value
        f_lower_extended = self.get_lower_value

        if self.tick_for_helper is None or not self.is_pattern_type_configured_for_helper_functions:
            tick_list = [tick_first, tick_first, tick_last, tick_last]
            function_list = [self.f_upper, self.f_lower, self.f_lower, self.f_upper]
        else:
            if self.f_var_cross_f_upper_f_lower > 0:
                if self.f_var_cross_f_upper_f_lower <= pdh.pattern_data.tick_last.f_var:
                    tick_last = pdh.pattern_data.get_tick_by_date_num(self.f_var_cross_f_upper_f_lower)
                    tick_list = [tick_first, tick_last, tick_first]
                    if self.pattern_direction == FD.ASC:
                        function_list = [self.f_upper, self.f_upper, self.f_lower]
                    else:
                        function_list = [self.f_lower, self.f_lower, self.f_upper]
                else:
                    tick_last = pdh.pattern_data.tick_last
                    tick_list = [tick_first, tick_last, tick_last, tick_first]
                    if self.pattern_direction == FD.ASC:
                        function_list = [self.f_upper, self.f_upper, self.f_lower, self.f_lower]
                    else:
                        function_list = [self.f_lower, self.f_lower, self.f_upper, self.f_upper]
            else:
                tick_list = [tick_first, self.tick_for_helper, tick_last, tick_last, tick_first]
                if self.breakout_direction == FD.ASC:
                    function_list = [f_upper_extended, f_upper_extended, f_upper_extended, self.f_lower, self.f_lower]
                else:
                    function_list = [f_lower_extended, f_lower_extended, f_lower_extended, self.f_upper, self.f_upper]
        return tick_list, function_list

    def __init_tick_for_helper__(self):
        pass


class ChannelPatternFunctionContainer(PatternFunctionContainer):
    def get_tick_function_list_for_xy_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        tick_list = [tick_first, tick_first, tick_last, tick_last]
        function_list = [self.f_upper, self.f_lower, self.f_lower, self.f_upper]
        return tick_list, function_list


class ChannelUpPatternFunctionContainer(ChannelPatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close < self.get_lower_value(tick.f_var)


class ChannelDownPatternFunctionContainer(ChannelPatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close > self.get_upper_value(tick.f_var)


class TKEUpPatternFunctionContainer(PatternFunctionContainer):
    @property
    def is_pattern_type_configured_for_helper_functions(self) -> bool:
        return True

    def get_tick_function_list_for_xy_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        tick_list = [tick_first, tick_last, tick_last, self.tick_for_helper, tick_first]
        function_list = [self.h_upper, self.h_upper, self.h_lower, self.h_lower, self.f_lower]
        return tick_list, function_list

    def __init_tick_for_helper__(self):
        pos = self.df[CN.HIGH].idxmax(axis=0)
        tick = WaveTick(self.df.loc[pos])
        self.__set_tick_for_helper__(tick)

    def is_tick_breakout(self, tick: WaveTick):
        return tick.close < self.get_lower_value(tick.f_var)

    def get_lower_value(self, f_var: int):
        return round(min(self._f_lower(f_var), self._h_lower(f_var)), 2)

    def set_tick_for_breakout(self, tick: WaveTick):
        pass  # must overwrite this function

    def adjust_functions_when_required(self, tick: WaveTick):
        if tick.high > self._f_upper(tick.f_var):
            self._f_upper = np.poly1d([0, tick.high])
            self.__set_f_var_cross_f_upper_f_lower__()
        self.__adjust_tick_for_helper_when_required__(tick)

    def __adjust_tick_for_helper_when_required__(self, tick: WaveTick):
        if tick.high > self._tick_for_helper.high:
            self.__set_tick_for_helper__(tick)


class TKEDownPatternFunctionContainer(PatternFunctionContainer):
    @property
    def is_pattern_type_configured_for_helper_functions(self) -> bool:
        return True

    def get_tick_function_list_for_xy_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        tick_list = [tick_first, self.tick_for_helper, tick_last, tick_last, tick_first]
        function_list = [self.f_upper, self.h_upper, self.h_upper, self.f_lower, self.f_lower]
        return tick_list, function_list

    def __init_tick_for_helper__(self):
        pos = self.df[CN.LOW].idxmin(axis=0)
        tick = WaveTick(self.df.loc[pos])
        self.__set_tick_for_helper__(tick)

    def is_tick_breakout(self, tick: WaveTick):
        return tick.close > self.get_upper_value(tick.f_var)

    def get_upper_value(self, f_var: int):
        return round(max(self._f_upper(f_var), self._h_upper(f_var)), 2)

    def set_tick_for_breakout(self, tick: WaveTick):
        pass  # must overwrite this function

    def adjust_functions_when_required(self, tick: WaveTick):
        if tick.low < self._f_lower(tick.f_var):
            self._f_lower = np.poly1d([0, tick.low])
            self.__set_f_var_cross_f_upper_f_lower__()
        self.__adjust_tick_for_helper_when_required__(tick)

    def __adjust_tick_for_helper_when_required__(self, tick: WaveTick):
        if tick.low < self._tick_for_helper.low:
            self.__set_tick_for_helper__(tick)


class TriangleUpPatternFunctionContainer(PatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close < self.get_lower_value(tick.f_var)


class TriangleDownPatternFunctionContainer(PatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close > self.get_upper_value(tick.f_var)


class TriangleTopPatternFunctionContainer(PatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close < self.get_lower_value(tick.f_var)


class TriangleBottomPatternFunctionContainer(PatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close > self.get_upper_value(tick.f_var)



