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


class PatternFunctionContainer:
    def __init__(self, pattern_type: str, df: pd.DataFrame, f_lower: np.poly1d = None, f_upper: np.poly1d = None):
        self.pattern_type = pattern_type
        self.df = df
        self.__tick_for_helper = None
        self.__tick_first = WaveTick(self.df.iloc[0])
        self.__tick_last = WaveTick(self.df.iloc[-1])
        self.__f_lower = f_lower
        self.__f_upper = f_upper
        self.__h_lower = f_lower
        self.__h_upper = f_upper
        self.__f_regression = self.__get_f_regression__()
        self.__f_var_cross_f_upper_f_lower = 0
        self.__breakout_direction = None
        self.__pattern_direction = self.__get_pattern_direction__()
        if self.is_valid():
            self.__init_tick_for_helper__()
            self.__set_f_var_cross_f_upper_f_lower__()

    def __get_pattern_direction__(self):
        if self.is_valid():
            return FD.ASC if self.__f_upper[1] + self.__f_lower[1] > 0 else FD.DESC
        else:
            return FD.ASC if self.__f_regression[1] >= 0 else FD.DESC

    @property
    def number_of_positions(self):
        return self.__tick_last.position - self.__tick_first.position

    @property
    def position_first(self):
        return self.__tick_first.position

    @property
    def position_last(self):
        return self.__tick_last.position

    @property
    def tick_first(self):
        return self.__tick_first

    @property
    def tick_last(self):
        return self.__tick_last

    @property
    def pattern_direction(self):
        return self.__pattern_direction

    @property
    def f_var_cross_f_upper_f_lower(self):
        return self.__f_var_cross_f_upper_f_lower

    @property
    def f_lower(self):
        return self.__f_lower

    @property
    def f_upper(self):
        return self.__f_upper

    @property
    def h_lower(self):
        return self.__h_lower

    @property
    def h_upper(self):
        return self.__h_upper

    @property
    def f_regression(self):
        return self.__f_regression

    @property
    def f_upper_pct(self):
        return self.__get_slope_in_decimal_percentage__(self.__f_upper)

    @property
    def f_lower_pct(self):
        return self.__get_slope_in_decimal_percentage__(self.__f_lower)

    @property
    def f_regression_pct(self):
        return self.__get_slope_in_decimal_percentage__(self.__f_regression)

    def __get_slope_in_decimal_percentage__(self, func: np.poly1d):
        off_set = self.__tick_first.f_var
        length = self.number_of_positions
        return math_functions.MyPoly1d.get_slope_in_decimal_percentage(func, off_set, length)

    def __set_breakout_direction__(self, breakout_direction: str):
        self.__breakout_direction = breakout_direction

    def __get_breakout_direction__(self):
        return self.__breakout_direction

    breakout_direction = property(__get_breakout_direction__, __set_breakout_direction__)

    def is_regression_value_in_pattern_for_f_var(self, f_var: int):
        return self.__f_lower(f_var) <= self.__f_regression(f_var) <= self.__f_upper(f_var)

    def is_valid(self):
        return not(self.__f_lower is None or self.__f_upper is None)

    def is_tick_breakout(self, tick: WaveTick):
        upper_boundary_value = self.get_upper_value(tick.f_var)
        lower_boundary_value = self.get_lower_value(tick.f_var)

        if self.pattern_type == FT.TKE_UP:
            return tick.close < lower_boundary_value
        elif self.pattern_type == FT.TKE_DOWN:
            return tick.close < lower_boundary_value
        elif self.pattern_type in [FT.TRIANGLE_UP, FT.CHANNEL_UP]:
            return tick.close < lower_boundary_value
        elif self.pattern_type in [FT.TRIANGLE_DOWN, FT.CHANNEL_DOWN]:
            return tick.close > upper_boundary_value
        else:
            return not (lower_boundary_value <= tick.close <= upper_boundary_value)

    def is_tick_inside_pattern_range(self, tick: WaveTick):
        if self.__pattern_direction == FD.ASC:
            h_upper_value = self.__h_upper(tick.f_var)
            f_lower_value = self.__f_lower(tick.f_var)
            return f_lower_value < h_upper_value
        else:
            h_lower_value = self.__h_lower(tick.f_var)
            f_upper_value = self.__f_upper(tick.f_var)
        return h_lower_value < f_upper_value

    def add_tick_from_main_df_to_df(self, df_main: pd.DataFrame, tick: WaveTick):
        if tick is not None:
            self.__tick_last = tick
            self.df = pd.concat([self.df, df_main.loc[tick.position:tick.position]])

    def __get_f_regression__(self) -> np.poly1d:
        np_array = np.polyfit(self.df[CN.DATEASNUM], self.df[CN.CLOSE], 1)
        return np.poly1d([np_array[0], np_array[1]])

    def __set_f_var_cross_f_upper_f_lower__(self):
        if self.__f_upper[1] < self.__f_lower[1]:
            for n in range(self.__tick_last.f_var, self.__tick_last.f_var + 3 * self.number_of_positions):
                u = self.__f_upper(n)
                l = self.__f_lower(n)
                if self.__f_upper(n) < self.__f_lower(n):
                    self.__f_var_cross_f_upper_f_lower = n - 1
                    break

    def __get_tick_for_helper__(self):
        return self.__tick_for_helper

    def __set_tick_for_helper__(self, tick):
        self.__tick_for_helper = tick
        self.__h_upper = np.poly1d([0, self.__f_upper(tick.f_var)])
        self.__h_lower = np.poly1d([0, self.__f_lower(tick.f_var)])

    tick_for_helper = property(__get_tick_for_helper__, __set_tick_for_helper__)

    def set_tick_for_breakout(self, tick: WaveTick):
        if self.pattern_type not in [FT.TKE_DOWN, FT.TKE_UP]:
            self.__set_tick_for_helper__(tick)

    def adjust_functions_when_required(self, tick: WaveTick):
        if self.pattern_type == FT.TKE_DOWN:
            if tick.low < self.__f_lower(tick.f_var):
                self.__f_lower = np.poly1d([0, tick.low])
                self.__set_f_var_cross_f_upper_f_lower__()
        elif self.pattern_type == FT.TKE_UP:
            if tick.high > self.__f_upper(tick.f_var):
                self.__f_upper = np.poly1d([0, tick.high])
                self.__set_f_var_cross_f_upper_f_lower__()
        self.__adjust_tick_for_helper_when_required__(tick)

    def __adjust_tick_for_helper_when_required__(self, tick: WaveTick):
        if self.__tick_for_helper is None:
            return

        if self.pattern_type == FT.TKE_DOWN:
            if tick.low < self.__tick_for_helper.low:
                self.__set_tick_for_helper__(tick)
        elif self.pattern_type == FT.TKE_UP:
            if tick.high > self.__tick_for_helper.high:
                self.__set_tick_for_helper__(tick)

    @property
    def is_pattern_type_configured_for_helper_functions(self) -> bool:
        return self.pattern_type in [FT.TKE_DOWN, FT.TRIANGLE_UP]

    def get_upper_value(self, f_var: int):
        if self.tick_for_helper is None or self.tick_for_helper.f_var > f_var:
            return round(self.__f_upper(f_var), 2)
        if self.pattern_type not in [FT.TKE_UP, FT.TKE_DOWN]:
            return round(self.__f_upper(f_var), 2)
        if self.pattern_direction == FD.ASC:
            return round(min(self.__f_upper(f_var), self.__h_upper(f_var)), 2)
        else:
            return round(max(self.__f_upper(f_var), self.__h_upper(f_var)), 2)

    def get_lower_value(self, f_var: int):
        if self.tick_for_helper is None or self.tick_for_helper.f_var > f_var:
            return round(self.__f_lower(f_var), 2)
        if self.pattern_type not in [FT.TKE_UP, FT.TKE_DOWN]:
            return round(self.__f_lower(f_var), 2)
        elif self.pattern_type == FT.TKE_UP:
            return round(min(self.__f_lower(f_var), self.__h_lower(f_var)), 2)
        else:
            return round(max(self.__f_lower(f_var), self.__h_lower(f_var)), 2)

    def __init_tick_for_helper__(self):
        if self.pattern_type == FT.TKE_UP:
            pos = self.df[CN.HIGH].idxmax(axis=0)
            tick = WaveTick(self.df.loc[pos])
            self.__set_tick_for_helper__(tick)
        elif self.pattern_type == FT.TKE_DOWN:
            pos = self.df[CN.LOW].idxmin(axis=0)
            tick = WaveTick(self.df.loc[pos])
            self.__set_tick_for_helper__(tick)