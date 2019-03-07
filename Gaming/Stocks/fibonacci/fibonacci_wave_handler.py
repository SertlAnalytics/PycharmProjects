"""
Description: This module contains some function for Fibonacci waves
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_database.stock_access_layer import AccessLayer4Wave
from pattern_database.stock_database import StockDatabase
from pattern_wave_tick import WaveTick, WaveTickList
from pattern_index_configuration import IndexConfiguration
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import WAVEST, DC, INDICES
import numpy as np


class FibonacciWaveHandler:
    def __init__(self, retrospective_days=0):
        self._db_stock = StockDatabase()
        self._index_list = [INDICES.CRYPTO_CCY, INDICES.DOW_JONES, INDICES.NASDAQ100]
        self._index_config = IndexConfiguration(self._db_stock, self._index_list)
        self._seconds_day = MyDate.get_seconds_for_period(days=1)
        self._retrospective_days = 0
        self._offset_timestamp_start = 0
        self._retrospective_date_list = []
        self._retrospective_date_range_dict = {}
        self._retrospective_index_wave_type_number_dict = {}  # this dictionary contains a dictionary {date: number, ..}
        self.__init_wave_variables__()
        self.__fill_variables_according_to_retrospective_days__(retrospective_days)

    @property
    def df_wave(self):
        return self._df_wave

    @property
    def are_data_actual(self) -> bool:
        return self._df_fetched_date_str == MyDate.get_date_as_string_from_date_time()

    @property
    def date_list(self):
        return self._retrospective_date_list

    def reload_data(self):
        self.__init_wave_variables__()

    def init_list_and_dictionaries_for_retrospective_days(self, retrospective_days: int):
        self.__fill_variables_according_to_retrospective_days__(retrospective_days)

    def get_df_dict_by_wave_types_in_retrospective(self, retrospective_days: int):
        offset_timestamp = MyDate.get_offset_timestamp(days=-retrospective_days)
        return {wave_type: self._df_dict_by_wave_types[self._df_dict_by_wave_types[DC.WAVE_END_TS] >= offset_timestamp]
                for wave_type in self._df_dict_by_wave_types}

    def __init_wave_variables__(self):
        self._df_wave = self.__get_df_wave__()
        self._df_dict_by_wave_types = self.__get_df_dict_by_wave_types__()
        self._df_fetched_date_str = MyDate.get_date_as_string_from_date_time()
        self.__init_retrospective_variables__(0)

    def __get_df_dict_by_wave_types__(self) -> dict:
        return_dict = {}
        df_base = self._df_wave
        for wave_type in WAVEST.get_waves_types_for_processing():
            period, direction = WAVEST.get_period_and_direction_for_wave_type(wave_type)
            df = df_base[df_base[DC.PERIOD] == period]
            df = df[df[DC.WAVE_TYPE] == direction]
            return_dict[wave_type] = df
        return return_dict

    def get_waves_numbers_with_dates_for_wave_type_and_index_for_days(self, wave_type: str, index: str):
        date_number_dict = self.get_waves_date_number_dict_for_wave_type_and_index(wave_type, index)
        count_list = []
        for date_str in self._retrospective_date_list:
            if index == INDICES.CRYPTO_CCY or MyDate.is_monday_till_friday(date_str):
                count_list.append('{}: {}'.format(date_str, date_number_dict[date_str]))
        return '\n'.join(count_list)

    def get_waves_date_number_dict_for_wave_type_and_index(self, wave_type: str, index: str):
        key = '{}_{}'.format(index, wave_type)
        return self._retrospective_index_wave_type_number_dict[key]

    def get_waves_number_list_for_wave_type_and_index(self, wave_type: str, index: str):
        key = '{}_{}'.format(index, wave_type)
        date_number_dict = self._retrospective_index_wave_type_number_dict[key]
        return [date_number_dict[date_str] for date_str in self._retrospective_date_list]

    def get_waves_numbers_for_wave_tick(self, wave_type: str, index: str, wave_tick: WaveTick):
        if wave_tick.date_str in self.date_list:
            key = '{}_{}'.format(index, wave_type)
            date_number_dict = self._retrospective_index_wave_type_number_dict[key]
            return date_number_dict[wave_tick.date_str]
        return 0

    def fill_wave_type_number_dict_for_ticks_in_wave_tick_list(self, wave_tick_list: WaveTickList, index: str):
        for wave_type in WAVEST.get_waves_types_for_processing():
            key = '{}_{}'.format(index, wave_type)
            if key in self._retrospective_index_wave_type_number_dict:
                date_number_dict = self._retrospective_index_wave_type_number_dict[key]
                for wave_tick in wave_tick_list.tick_list:
                    if wave_tick.date_str in date_number_dict:
                        number = date_number_dict[wave_tick.date_str]
                        if number > 0:
                            wave_tick.add_to_wave_type_number_dict(wave_type, number)
        wave_tick_list.fill_wave_type_number_dicts()  # we need some min max values for the wave numbers

    def __fill_variables_according_to_retrospective_days__(self, retrospective_days: int):
        if self._retrospective_days == retrospective_days:
            return  # nothing to do
        self.__init_retrospective_variables__(retrospective_days)
        self.__fill_retrospective_date_range_dict__()
        self.__fill_retrospective_index_wave_type_number_dict__()

    def __init_retrospective_variables__(self, retrospective_days):
        self._retrospective_days = retrospective_days
        self._offset_timestamp_start = MyDate.get_offset_timestamp(days=-self._retrospective_days)
        self._retrospective_date_list = []
        self._retrospective_date_range_dict = {}
        self._retrospective_index_wave_type_number_dict = {}

    def __fill_retrospective_date_range_dict__(self):
        self._retrospective_date_range_dict = {}
        for days in range(0, self._retrospective_days):
            ts_start = self._offset_timestamp_start + days * self._seconds_day
            ts_end = ts_start + self._seconds_day
            date_str = str(MyDate.get_date_from_epoch_seconds(ts_start))
            self._retrospective_date_list.append(date_str)
            self._retrospective_date_range_dict[date_str] = [ts_start, ts_end]

    def __fill_retrospective_index_wave_type_number_dict__(self):
        for wave_type in WAVEST.get_waves_types_for_processing():
            df_base = self._df_dict_by_wave_types[wave_type]
            df_base = df_base[df_base[DC.WAVE_END_TS] >= self._offset_timestamp_start]
            for index in self._index_list:
                key = '{}_{}'.format(index, wave_type)
                df_index = df_base[df_base[DC.INDEX] == index]
                date_number_dict = {}
                for date_str in self._retrospective_date_list:
                    ts_range = self._retrospective_date_range_dict[date_str]
                    df_final = df_index[np.logical_and(
                                    df_index[DC.WAVE_END_TS] >= ts_range[0],
                                    df_index[DC.WAVE_END_TS] < ts_range[1])]
                    date_number_dict[date_str] = df_final.shape[0]
                self._retrospective_index_wave_type_number_dict[key] = date_number_dict

    def __get_df_wave__(self):
        access_layer_wave = AccessLayer4Wave(self._db_stock)
        df = access_layer_wave.get_all_as_data_frame()
        df[DC.INDEX] = df[DC.TICKER_ID].apply(self.__get_index_for_symbol__)
        return df

    def __get_index_for_symbol__(self, ticker_id: str):
        return self._index_config.get_index_for_symbol(ticker_id)