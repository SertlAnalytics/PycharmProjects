"""
Description: This module contains the wave tick class - central for stoock data management
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import pandas as pd
from sertl_analytics.constants.pattern_constants import CN, TT
from sertl_analytics.functions import math_functions
from sertl_analytics.pybase.loop_list import ExtendedDictionary


class WaveTick:
    def __init__(self, tick):
        self.tick = tick

    @property
    def date(self):
        return self.tick[CN.DATE]

    @property
    def f_var(self):
        return self.tick[CN.DATEASNUM]

    @property
    def date_num(self):
        return self.tick[CN.DATEASNUM]

    @property
    def date_str(self):
        return self.tick[CN.DATE].strftime("%Y-%m-%d")

    @property
    def position(self):
        return self.tick[CN.POSITION]

    @property
    def is_max(self):
        return self.tick[CN.IS_MAX]

    @property
    def is_min(self):
        return self.tick[CN.IS_MIN]

    @property
    def is_local_max(self):
        return self.tick[CN.LOCAL_MAX]

    @property
    def is_local_min(self):
        return self.tick[CN.LOCAL_MIN]

    @property
    def open(self):
        return self.tick[CN.OPEN]

    @property
    def high(self):
        return self.tick[CN.HIGH]

    @property
    def low(self):
        return self.tick[CN.LOW]

    @property
    def close(self):
        return self.tick[CN.CLOSE]

    @property
    def volume(self):
        return self.tick[CN.VOL]

    @property
    def tick_type(self):
        if abs((self.open - self.close) / (self.high - self.low)) < 0.2:
            return TT.DOJI
        return TT.NONE

    def print(self):
        print('Pos: {}, Date: {}, High: {}, Low: {}'.format(self.position, self.date, self.high, self.low))

    def get_linear_f_params_for_high(self, tick):
        return math_functions.get_function_parameters(self.f_var, self.high, tick.f_var, tick.high)

    def get_linear_f_params_for_low(self, tick):
        return math_functions.get_function_parameters(self.f_var, self.low, tick.f_var, tick.low)

    def is_sustainable(self):
        return abs((self.open - self.close) / (self.high - self.low)) > 0.6

    def is_volume_rising(self, tick_comp, min_percentage: int):
        return self.volume / tick_comp.volume > (100 + min_percentage) / 100

    def has_gap_to(self, tick_comp):
        return self.low > tick_comp.high or self.high < tick_comp.low


class WaveTickList:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.tick_list = [WaveTick(row) for ind, row in self.df.iterrows()]

    def get_boundary_f_param_list(self, for_high: bool):  # gets all functions which are boundaries for the ticks.
        f_param_list = []
        tick_list_without_valleys = self.__get_tick_list_without_valleys__(self.tick_list, for_high)
        for n in range(len(tick_list_without_valleys) - 1):
            tick_left = tick_list_without_valleys[n]
            tick_right = tick_list_without_valleys[n + 1]
            if for_high:
                f_param_list.append(tick_left.get_linear_f_params_for_high(tick_right))
            else:
                f_param_list.append(tick_left.get_linear_f_params_for_low(tick_right))
        return f_param_list

    def __get_tick_list_without_valleys__(self, tick_list, for_high: bool):
        len_tick_list = len(tick_list)
        if len_tick_list <= 2:
            return tick_list
        remove_index_list = []
        for n in range(len_tick_list - 2):
            tick_left = tick_list[n]
            tick_middle = tick_list[n + 1]
            tick_right = tick_list[n + 2]
            if for_high:
                f_param = tick_left.get_linear_f_params_for_high(tick_right)
                if tick_middle.high < f_param(tick_middle.f_var):
                    remove_index_list.append(n + 1)
            else:
                f_param = tick_left.get_linear_f_params_for_low(tick_right)
                if tick_middle.low > f_param(tick_middle.f_var):
                    remove_index_list.append(n + 1)
        if len(remove_index_list) == 0:
            return tick_list
        for index in reversed(remove_index_list):
            del tick_list[index]
        return self.__get_tick_list_without_valleys__(tick_list, for_high)


class ExtendedDictionary4WaveTicks(ExtendedDictionary):
    def __init__(self, df: pd.DataFrame):
        ExtendedDictionary.__init__(self)
        self.df = df
        self.__process_df__()

    def __process_df__(self):
        for ind, rows in self.df.iterrows():
            tick = WaveTick(rows)
            self.append(tick.date_num, tick)