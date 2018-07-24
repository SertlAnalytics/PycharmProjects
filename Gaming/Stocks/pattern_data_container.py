"""
Description: This module contains the PatternDataContainer class - central data container for stock data
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import pandas as pd
import numpy as np
import itertools
import matplotlib.dates as mdt
from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod
from sertl_analytics.constants.pattern_constants import CN
from sertl_analytics.mydates import MyDate
from pattern_wave_tick import WaveTick, ExtendedDictionary4WaveTicks, WaveTickList
from pattern_configuration import config
import matplotlib.dates as mdates


class PatternData:
    """
    This class has two purposes:
    1. Identify all extrema: global and local maximum and minimum which are used as checkpoint for pattern detections.
    2. Identify ranges which can be used for a thorough inspection in the further process
    """
    __length_for_global = config.length_for_global_min_max
    __length_for_local = config.length_for_local_min_max

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df_length = self.df.shape[0]
        self.max_value = self.df[CN.HIGH].max()
        self.min_value = self.df[CN.HIGH].min()
        self.height = self.max_value - self.min_value
        self.__add_columns__()
        self.__init_columns_for_ticks_distance__()
        self.df_min_max = self.df[np.logical_or(self.df[CN.IS_MIN], self.df[CN.IS_MAX])]
        self.tick_by_date_num_ext_dic = ExtendedDictionary4WaveTicks(self.df)
        self.tick_list = [self.tick_by_date_num_ext_dic.dic[index] for index in self.tick_by_date_num_ext_dic.index]
        self.tick_first = self.tick_list[0]
        self.tick_last = self.tick_list[-1]
        self.tick_f_var_distance = self.__get_tick_f_var_distance__()
        self.wave_tick_list_min_max = WaveTickList(self.df_min_max)
        self.tick_list_min = []
        self.tick_list_max = []
        self.__fill_tick_list_min_max__()
        self.tick_list_min_without_hidden_ticks = self.__get_hidden_tick_list__(self.tick_list_min, False)
        self.tick_list_max_without_hidden_ticks = self.__get_hidden_tick_list__(self.tick_list_max, True)

    def __get_tick_f_var_distance__(self):
        return self.tick_list[1].f_var - self.tick_list[0].f_var

    def get_tick_by_date_num(self, date_num: float):
        wave_tick = self.tick_by_date_num_ext_dic.get_value_by_dict_key(date_num)
        if wave_tick is not None:
            return wave_tick
        for wave_tick in self.tick_list:
            if wave_tick.date_num >= date_num:
                return wave_tick
        return self.tick_last

    def get_tick_by_pos(self, pos: int):
        if pos < len(self.tick_list):
            return self.tick_list[pos]
        else:
            return self.tick_last

    def __fill_tick_list_min_max__(self):
        for tick in self.wave_tick_list_min_max.tick_list:
            if tick.is_max:
                self.tick_list_max.append(tick)
            else:
                self.tick_list_min.append(tick)

    @staticmethod
    def __get_hidden_tick_list__(input_list: list, for_high: bool):
        wave_tick_list = WaveTickList(input_list)
        return wave_tick_list.get_list_without_hidden_ticks(for_high, 0.03)

    def __add_columns__(self):
        self.df = self.df.assign(MeanHL=round((self.df.High + self.df.Low) / 2, 2))
        self.df = self.df.assign(Date=self.df.index.map(MyDate.get_date_from_epoch_seconds))
        self.df = self.df.assign(Time=self.df.index.map(MyDate.get_time_from_epoch_seconds))
        self.df = self.df.assign(DateAsNumber=self.df.index.map(MyDate.get_date_as_number_from_epoch_seconds))
        self.df = self.df.assign(Position=self.df.index.map(self.df.index.get_loc))
        self.df[CN.POSITION] = self.df[CN.POSITION].apply(int)
        if CN.TIMESTAMP not in self.df.columns:
            self.df[CN.TIMESTAMP] = self.df.index
        self.df.reset_index(drop=True, inplace=True)  # get position index

    def __init_columns_for_ticks_distance__(self):
        self.__add_distance_columns__()
        self.__add_min_max_columns__()

    def __add_distance_columns__(self):
        self.tick_list = [WaveTick(rows) for ind, rows in self.df.iterrows()]
        for pos, high, before in itertools.product(range(0, self.df_length), (False, True), (False, True)):
            value = self.__get_distance__(pos, high, before)
            if high and before:
                self.df.loc[pos, CN.TICKS_BREAK_HIGH_BEFORE] = value
            elif high and not before:
                self.df.loc[pos, CN.TICKS_BREAK_HIGH_AFTER] = value
            elif not high and before:
                self.df.loc[pos, CN.TICKS_BREAK_LOW_BEFORE] = value
            elif not high and not before:
                self.df.loc[pos, CN.TICKS_BREAK_LOW_AFTER] = value

    def __add_min_max_columns__(self):
        self.df[CN.GLOBAL_MIN] = np.logical_and(self.df[CN.TICKS_BREAK_LOW_AFTER] > self.__length_for_global,
                                                self.df[CN.TICKS_BREAK_LOW_BEFORE] > self.__length_for_global)
        self.df[CN.GLOBAL_MAX] = np.logical_and(self.df[CN.TICKS_BREAK_HIGH_AFTER] > self.__length_for_global,
                                                self.df[CN.TICKS_BREAK_HIGH_BEFORE] > self.__length_for_global)
        self.df[CN.LOCAL_MIN] = np.logical_and(self.df[CN.TICKS_BREAK_LOW_AFTER] > self.__length_for_local,
                                               self.df[CN.TICKS_BREAK_LOW_BEFORE] > self.__length_for_local)
        self.df[CN.LOCAL_MAX] = np.logical_and(self.df[CN.TICKS_BREAK_HIGH_AFTER] > self.__length_for_local,
                                               self.df[CN.TICKS_BREAK_HIGH_BEFORE] > self.__length_for_local)
        self.df[CN.IS_MIN] = np.logical_or(self.df[CN.GLOBAL_MIN], self.df[CN.LOCAL_MIN])
        self.df[CN.IS_MAX] = np.logical_or(self.df[CN.GLOBAL_MAX], self.df[CN.LOCAL_MAX])

    def __get_distance__(self, row_pos: int, for_high: bool, for_before: bool) -> int:
        signature = -1 if for_before else 1
        pos_compare = row_pos + signature
        actual_value_pair = self.__get_value_pair_for_comparison__(self.tick_list[row_pos], for_high)
        while 0 <= pos_compare < self.df_length:
            if self.__is_new_value_a_break__(actual_value_pair, pos_compare, for_high):
                break
            pos_compare += signature
        return self.df_length + 1 if (pos_compare < 0 or pos_compare >= self.df_length) else abs(row_pos - pos_compare)

    def __is_new_value_a_break__(self, actual_value_pair: list, pos_compare: int, for_high: bool) -> bool:
        """
        We need a separate script for handling when values are different to avoid min/max neighbors with the same value
        The idea behind this algorithm is that the extrema is mostly not the longest tick.
        """
        value_pair_compare = self.__get_value_pair_for_comparison__(self.tick_list[pos_compare], for_high)
        if for_high:
            if value_pair_compare[0] > actual_value_pair[0]:
                return True
            if value_pair_compare[0] == actual_value_pair[0]:
                return value_pair_compare[1] > actual_value_pair[1]  # break if the compare has a greater low value
        else:
            if value_pair_compare[0] < actual_value_pair[0]:
                return True
            if value_pair_compare[0] == actual_value_pair[0]:
                return value_pair_compare[1] < actual_value_pair[1]  # break if the compare has a smaller high value
        return False

    @staticmethod
    def __get_value_pair_for_comparison__(tick: WaveTick, for_high: bool) -> list:
        value_first = tick.high if for_high else tick.low
        value_second = tick.low if for_high else tick.high
        return [value_first, value_second]


class PatternDataFibonacci(PatternData):
    __length_for_global = config.length_for_global_min_max_fibonacci
    __length_for_local = config.length_for_local_min_max_fibonacci


class PatternDataHandler:
    def __init__(self):
        self.pattern_data = None
        self.pattern_data_fibonacci = None

    def init_by_df(self, df: pd.DataFrame):
        self.pattern_data = PatternData(df)
        self.pattern_data_fibonacci = PatternDataFibonacci(df)


pattern_data_handler = PatternDataHandler()
