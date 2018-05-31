"""
Description: This module contains the PatternFunctionContainer class - central function calculations
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_constants import CN, FD, FT
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
        self.__breakout_direction = None
        self.__pattern_direction = FD.ASC if self.__f_regression[1] >= 0 else FD.DESC
        if self.is_valid():
            self.__init_tick_for_helper__()

    @property
    def number_of_positions(self):
        return self.__tick_last.position - self.__tick_first.position

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
    def f_upper_trade(self):
        if self.__breakout_direction == FD.DESC:
            return self.__h_lower
        else:
            return np.poly1d([0, self.__h_upper[0] + self.pattern_breadth])

    @property
    def f_lower_trade(self):
        if self.__breakout_direction == FD.DESC:
            return np.poly1d([0, self.__h_lower[0] - self.pattern_breadth])
        else:
            return self.__h_upper

    @property
    def f_regression(self):
        return self.__f_regression

    @property
    def pattern_breadth(self):
        breadth_left = self.__f_upper(self.tick_first.position) - self.__f_lower(self.tick_first.position)
        breadth_right = self.__f_upper(self.tick_for_helper.position) - self.__f_lower(self.tick_for_helper.position)
        if self.pattern_type in [FT.TKE_DOWN, FT.TKE_UP]:
            return round(breadth_right, 2)
        else:
            return round((breadth_left + breadth_right)/2, 2)

    def __set_breakout_direction__(self, breakout_direction: str):
        self.__breakout_direction = breakout_direction

    def __get_breakout_direction__(self):
        return self.__breakout_direction

    breakout_direction = property(__get_breakout_direction__, __set_breakout_direction__)

    def is_regression_value_in_pattern_for_position(self, pos):
        return self.__f_lower(pos) <= self.__f_regression(pos) <= self.__f_upper(pos)

    def is_valid(self):
        return not(self.__f_lower is None or self.__f_upper is None)

    def is_tick_breakout(self, tick: WaveTick):
        f_upper_value = self.get_upper_value_for_position(tick.position)
        f_lower_value = self.get_lower_value_for_position(tick.position)

        if self.pattern_type in [FT.TKE_UP, FT.TRIANGLE_UP, FT.CHANNEL_UP]:
            return tick.close < f_lower_value
        elif self.pattern_type in [FT.TKE_DOWN, FT.TRIANGLE_DOWN, FT.CHANNEL_DOWN]:
            return tick.close > f_upper_value
        else:
            return not (f_lower_value <= tick.close <= f_upper_value)

    def is_tick_inside_pattern_range(self, tick: WaveTick):
        if self.__pattern_direction == FD.ASC:
            h_upper_value = self.__h_upper(tick.position)
            f_lower_value = self.__f_lower(tick.position)
            return f_lower_value < h_upper_value
        else:
            h_lower_value = self.__h_lower(tick.position)
            f_upper_value = self.__f_upper(tick.position)
        return h_lower_value < f_upper_value

    def add_tick_from_main_df_to_df(self, df_main: pd.DataFrame, tick: WaveTick):
        if tick is not None:
            self.__tick_last = tick
            self.df = pd.concat([self.df, df_main.loc[tick.position:tick.position]])

    def __get_f_regression__(self) -> np.poly1d:
        np_array = np.polyfit(self.df[CN.POSITION], self.df[CN.CLOSE], 1)
        return np.poly1d([np_array[0], np_array[1]])

    def __get_tick_for_helper__(self):
        return self.__tick_for_helper

    def __set_tick_for_helper__(self, tick):
        self.__tick_for_helper = tick
        self.__h_upper = np.poly1d([0, self.__f_upper(tick.position)])
        self.__h_lower = np.poly1d([0, self.__f_lower(tick.position)])

    tick_for_helper = property(__get_tick_for_helper__, __set_tick_for_helper__)

    def set_tick_for_breakout(self, tick: WaveTick):
        if self.pattern_type != FT.TKE_DOWN:
            self.__set_tick_for_helper__(tick)

    def adjust_functions_when_required(self, tick: WaveTick):
        if self.pattern_type == FT.TKE_DOWN:
            if tick.low < self.__f_lower(tick.position):
                self.__f_lower = np.poly1d([0, tick.low])
                self.__set_tick_for_helper__(tick)
        elif self.pattern_type == FT.TKE_UP:
            if tick.high > self.__f_upper(tick.position):
                self.__f_upper = np.poly1d([0, tick.high])
                self.__set_tick_for_helper__(tick)

    @property
    def is_pattern_type_configured_for_helper_functions(self) -> bool:
        return self.pattern_type in [FT.TKE_DOWN, FT.TRIANGLE_UP]

    def get_upper_value_for_position(self, pos: int):
        if self.tick_for_helper is None or self.tick_for_helper.position > pos:
            return round(self.__f_upper(pos), 2)
        if self.pattern_direction == FD.ASC:
            return round(min(self.__f_upper(pos), self.__h_upper(pos)), 2)
        else:
            return round(max(self.__f_upper(pos), self.__h_upper(pos)), 2)

    def get_lower_value_for_position(self, pos: int):
        if self.tick_for_helper is None or self.tick_for_helper.position > pos:
            return round(self.__f_lower(pos), 2)
        if self.pattern_direction == FD.ASC:
            return round(min(self.__f_lower(pos), self.__h_lower(pos)), 2)
        else:
            return round(max(self.__f_lower(pos), self.__h_lower(pos)), 2)

    def __init_tick_for_helper__(self):
        if self.pattern_type == FT.TKE_UP:
            pos = self.df[CN.HIGH].idxmax(axis=0)
            tick = WaveTick(self.df.loc[pos])
            self.__set_tick_for_helper__(tick)
        elif self.pattern_type == FT.TKE_DOWN:
            pos = self.df[CN.LOW].idxmin(axis=0)
            tick = WaveTick(self.df.loc[pos])
            self.__set_tick_for_helper__(tick)