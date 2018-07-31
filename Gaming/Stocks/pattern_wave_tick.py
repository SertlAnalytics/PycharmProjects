"""
Description: This module contains the wave tick class - central for stoock data management
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import pandas as pd
import numpy as np
from sertl_analytics.constants.pattern_constants import CN, TT, DIR
from sertl_analytics.mymath import MyMath, MyPoly1d
from sertl_analytics.pybase.loop_list import ExtendedDictionary
from sertl_analytics.mydates import MyDate


class WaveTick:
    def __init__(self, tick):
        self.tick = tick

    @property
    def date(self):
        return self.tick[CN.DATE]

    @property
    def time_stamp(self) -> int:
        return int(self.tick[CN.TIMESTAMP])

    @property
    def f_var(self):
        return int(self.tick[CN.TIMESTAMP])
        # return self.tick[CN.DATEASNUM]

    @property
    def direction(self):
        return DIR.UP if self.open < self.close else DIR.DOWN

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
    def is_global_max(self):
        return self.tick[CN.GLOBAL_MAX]

    @property
    def is_global_min(self):
        return self.tick[CN.GLOBAL_MIN]

    @property
    def open(self):
        return round(self.tick[CN.OPEN], 2)

    @property
    def high(self):
        return round(self.tick[CN.HIGH], 2)

    @property
    def low(self):
        return round(self.tick[CN.LOW], 2)

    @property
    def close(self):
        return round(self.tick[CN.CLOSE], 2)

    @property
    def mean(self):
        return round((self.high + self.low)/2, 2)

    @property
    def volume(self):
        return self.tick[CN.VOL]

    @property
    def tick_type(self):
        if abs((self.open - self.close) / (self.high - self.low)) < 0.2:
            return TT.DOJI
        return TT.NONE

    @property
    def date_str_for_f_var(self):
        return str(MyDate.get_date_from_epoch_seconds(self.f_var))
        # return str(MyPyDate.get_datetime_from_epoch_number(self.f_var).date())

    @property
    def time_str_for_f_var(self):
        return str(MyDate.get_time_from_epoch_seconds(self.f_var))[:5]
        # return str(MyPyDate.get_datetime_from_epoch_number(self.f_var).time())[:5]

    def print(self):
        print('Pos: {}, Date: {}, High: {}, Low: {}'.format(self.position, self.date, self.high, self.low))

    def get_date_or_time_for_f_var(self, for_time: False):
        if for_time:
            return MyDate.get_datetime_from_epoch_number(self.f_var).time()
        else:
            return MyDate.get_datetime_from_epoch_number(self.f_var).date()

    def get_linear_f_params_for_high(self, tick):
        return MyPoly1d.get_poly1d(self.f_var, self.high, tick.f_var, tick.high)

    def get_linear_f_params_for_low(self, tick):
        return MyPoly1d.get_poly1d(self.f_var, self.low, tick.f_var, tick.low)

    def is_sustainable(self):
        return abs((self.open - self.close) / (self.high - self.low)) > 0.6

    def is_volume_rising(self, tick_comp, min_percentage: int):
        return MyMath.divide(self.volume, tick_comp.volume) > (100 + min_percentage) / 100

    def has_gap_to(self, tick_comp):
        return self.low > tick_comp.high or self.high < tick_comp.low


class WaveTickList:
    def __init__(self, df_or_list):  # input = pd.DataFrame or tick_list[]
        self.df = None
        self.tick_list = []
        if df_or_list.__class__.__name__ == 'DataFrame':
            self.__init_by_df__(df_or_list)
        else:
            self.__init_by_tick_list__(df_or_list)
        self.elements = len(self.tick_list)

    @property
    def length(self):
        return self.tick_list[-1].f_var - self.tick_list[0].f_var

    @property
    def mean(self):
        return round(self.min + self.value_range/2, 2)

    @property
    def max(self):
        return round(np.max([tick.close for tick in self.tick_list]), 2)

    @property
    def min(self):
        return round(np.min([tick.close for tick in self.tick_list]), 2)

    @property
    def value_range(self):
        return round(self.max - self.min, 2)

    def get_list_without_hidden_ticks(self, for_high: bool, tolerance_pct: float):
        """
        removes all ticks which ara hidden by their neighbors.
        """
        remove_index_list = []
        for n in range(1, self.elements - 2):
            if self.__is_tick_hidden_by_neighbors__(for_high, n, tolerance_pct):
                remove_index_list.append(n)
        for index in reversed(remove_index_list):
            del self.tick_list[index]
        return self.tick_list

    def __is_tick_hidden_by_neighbors__(self, for_high: bool, n: int, tolerance_pct: float):
        tick_left, tick, tick_right = self.tick_list[n - 1], self.tick_list[n], self.tick_list[n + 1]
        if for_high:
            f_param_left = tick_left.get_linear_f_params_for_high(tick)
            f_param_right = tick.get_linear_f_params_for_high(tick_right)
            for m in range(n - 1):
                if self.tick_list[m].high > f_param_left(self.tick_list[m].f_var):
                    return False
            for m in range(n + 1, self.elements - 1):
                if self.tick_list[m].high > f_param_right(self.tick_list[m].f_var):
                    return False
        else:
            f_param_left = tick_left.get_linear_f_params_for_low(tick)
            f_param_right = tick.get_linear_f_params_for_low(tick_right)
            for m in range(n - 1):
                if self.tick_list[m].low < f_param_left(self.tick_list[m].f_var):
                    return False
            for m in range(n + 1, self.elements - 1):
                if self.tick_list[m].low < f_param_right(self.tick_list[m].f_var):
                    return False
        return True

    def get_boundary_f_param_list(self, f_param: np.poly1d, for_high: bool):
        """
        gets all function parameters (np.poly1d) which are boundaries for the ticks.
        """
        f_param_list = []
        tick_list_without_valleys = self.__get_tick_list_without_valleys__(self.tick_list, for_high)
        for n in range(len(tick_list_without_valleys) - 1):
            tick_left = tick_list_without_valleys[n]
            tick_right = tick_list_without_valleys[n + 1]
            if for_high:
                f_param_boundary = tick_left.get_linear_f_params_for_high(tick_right)
            else:
                f_param_boundary = tick_left.get_linear_f_params_for_low(tick_right)
            if self.__is_f_param_boundary_compliant__(f_param, f_param_boundary):
                f_param_list.append(f_param_boundary)
        return f_param_list

    def __init_by_df__(self, df: pd.DataFrame):
        self.df = df
        self.tick_list = [WaveTick(row) for ind, row in self.df.iterrows()]

    def __init_by_tick_list__(self, tick_list: list):
        self.tick_list = list(tick_list)

    def __is_f_param_boundary_compliant__(self, f_param: np.poly1d, f_param_boundary: np.poly1d) -> bool:
        offset = self.tick_list[0].f_var
        slope_dec_main = MyPoly1d.get_slope_in_decimal_percentage(f_param, offset, self.length)
        slope_dec_bound = MyPoly1d.get_slope_in_decimal_percentage(f_param_boundary, offset, self.length)
        if f_param(offset) > f_param_boundary(offset):
            slope_main_bound = round(slope_dec_main - slope_dec_bound, 4)
        else:
            slope_main_bound = round(slope_dec_bound - slope_dec_main, 4)
        return slope_main_bound < 0.04  # we don't accept wide opening patterns

    def __get_tick_list_without_valleys__(self, tick_list, for_high: bool):
        """
        get the tick list without any valley (i.e. the middle of three ticks is not smaller than the others for high)
        recursive call !!!
        """
        len_tick_list = len(tick_list)
        if len_tick_list <= 2:
            return tick_list
        remove_index_list = []
        for n in range(len_tick_list - 2):
            tick_left, tick_middle, tick_right = tick_list[n], tick_list[n + 1], tick_list[n + 2]
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
        return self.__get_tick_list_without_valleys__(tick_list, for_high)  # recursive call !!!


class ExtendedDictionary4WaveTicks(ExtendedDictionary):
    def __init__(self, df: pd.DataFrame, column: str = CN.DATEASNUM):
        ExtendedDictionary.__init__(self)
        self.df = df
        self.__process_df__(column)

    def __process_df__(self, column: str):
        for ind, rows in self.df.iterrows():
            tick = WaveTick(rows)
            self.append(rows[column], tick)