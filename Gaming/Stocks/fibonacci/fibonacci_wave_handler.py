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
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import WAVEST, DC, INDICES, PRD
import numpy as np


class FibonacciWaveHandler:
    def __init__(self, sys_config: SystemConfiguration, period=''):
        self._sys_config = sys_config
        self._wave_types = WAVEST.get_waves_types_for_processing(period)
        self._and_clause = self.__get_and_clause_for_waves__()
        self._db_stock = self._sys_config.db_stock
        self._limit = self._sys_config.data_provider.limit
        self._retrospective_ticks = 0
        self._range_timestamp_start = self.__get_range_timestamp_start__()
        self._range_timestamp_end = self.__get_range_timestamp_end__()
        self._period = self._sys_config.period
        self._aggregation = self._sys_config.period_aggregation
        self._index_list = [INDICES.CRYPTO_CCY, INDICES.DOW_JONES, INDICES.NASDAQ100]
        self._index_config = IndexConfiguration(self._db_stock, self._index_list)
        self._seconds_unit = self.__get_seconds_for_unit__()
        self._tick_key_list = []  # either date_str from Daily or timestamp for Intraday
        self._tick_key_timestamp_range_dict = {}
        # the following dictionary contains a dictionary {unit: number, ..}
        self._index_wave_type_number_dict = {}
        # self.__init_df_wave_related_variables__()
        # self.__fill_variables_according_to_ticks__()
        self._df_wave = None
        self.__fill_waves_into_number_dictionary__()
        self._df_fetched_date_str = MyDate.get_date_as_string_from_date_time()

    def __fill_waves_into_number_dictionary__(self):
        print('__fill_waves_into_number_dictionary__ Start at: {}'.format(MyDate.time_stamp_now()))
        access_layer_wave = AccessLayer4Wave(self._db_stock)
        self._df_wave = access_layer_wave.get_all_as_data_frame()
        self._df_wave[DC.INDEX] = self._df_wave[DC.TICKER_ID].apply(self.__get_index_for_symbol__)
        for wave_type in self._wave_types:
            period, direction = WAVEST.get_period_and_direction_for_wave_type(wave_type)
            df = self._df_wave[self._df_wave[DC.PERIOD] == period]
            df = df[df[DC.WAVE_TYPE] == direction]
            for index in self._index_list:
                key_index_wave_type = '{}_{}'.format(index, wave_type)
                df_index = df[df[DC.INDEX] == index]
                key_entry_number_dict = {}
                for row_index, row in df_index.iterrows():
                    key_entry = row[DC.WAVE_END_DT][:10]
                    if key_entry in key_entry_number_dict:
                        key_entry_number_dict[key_entry] += 1
                    else:
                        key_entry_number_dict[key_entry] = 1
                self._index_wave_type_number_dict[key_index_wave_type] = key_entry_number_dict
        print('__fill_waves_into_number_dictionary__ end at: {}'.format(MyDate.time_stamp_now()))

    def __get_range_timestamp_start__(self):
        # Example:  Wave_End_Datetime BETWEEN '2018-07-03' AND '2019-12-01'
        if self._and_clause == '':
            return MyDate.get_offset_timestamp(days=-self._limit)
        and_clause_array = self._and_clause.split(' ')
        date_from_str = and_clause_array[2][1:-1]
        return MyDate.get_epoch_seconds_from_datetime(date_from_str)

    def __get_range_timestamp_end__(self):
        # Example:  Wave_End_Datetime BETWEEN '2018-07-03' AND '2019-12-01'
        if self._and_clause == '':
            return MyDate.time_stamp_now()
        and_clause_array = self._and_clause.split(' ')
        date_from_str = and_clause_array[4][1:-1]
        return min(MyDate.time_stamp_now(), MyDate.get_epoch_seconds_from_datetime(date_from_str))

    @property
    def df_wave(self):
        return self._df_wave

    @property
    def are_data_actual(self) -> bool:
        if self._period == PRD.INTRADAY:
            return False
        return self._df_fetched_date_str == MyDate.get_date_as_string_from_date_time()

    @property
    def date_list(self):
        return self._tick_key_list

    def reload_data(self):
        self.__init_df_wave_related_variables__()

    def set_retrospective_tick_number(self, retrospective_ticks: int):
        offset_time_stamp = MyDate.get_offset_timestamp(days=-retrospective_ticks)
        self._tick_key_list = []
        while offset_time_stamp < MyDate.time_stamp_now():
            offset_time_stamp += self._seconds_unit
            date_str = str(MyDate.get_date_from_epoch_seconds(offset_time_stamp))
            self._tick_key_list.append(date_str)
        self._retrospective_ticks = retrospective_ticks

    def __init_df_wave_related_variables__(self):
        self._df_wave = self.__get_df_wave__()
        if not self._df_wave.empty:
            self._df_dict_by_wave_types = self.__get_df_dict_by_wave_types__()
            self._df_fetched_date_str = MyDate.get_date_as_string_from_date_time()

    def __get_and_clause_for_waves__(self):
        # Date BETWEEN '2018-07-03' AND '2019-12-01' -> Wave_End_Datetime BETWEEN '2018-07-03' AND '2019-12-01'
        return self._sys_config.data_provider.and_clause.replace('Date', 'Wave_End_Datetime')

    def __get_seconds_for_unit__(self):
        return MyDate.get_seconds_for_period(days=1) if self._period == PRD.DAILY \
            else MyDate.get_seconds_for_period(min=self._aggregation)

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
        key_list = self.__get_key_list_for_retrospective_number__()
        for tick_key in key_list:
            if index == INDICES.CRYPTO_CCY or MyDate.is_monday_till_friday(tick_key):
                count_list.append('{}: {}'.format(tick_key, date_number_dict[tick_key]))
        return '\n'.join(count_list)

    def get_waves_date_number_dict_for_wave_type_and_index(self, wave_type: str, index: str):
        key = '{}_{}'.format(index, wave_type)
        return self._index_wave_type_number_dict[key]

    def get_waves_number_list_for_wave_type_and_index(self, wave_type: str, index: str):
        key = '{}_{}'.format(index, wave_type)
        unit_number_dict = self._index_wave_type_number_dict[key]
        key_list = self.__get_key_list_for_retrospective_number__()
        return [unit_number_dict[tick_key] if tick_key in unit_number_dict else 0 for tick_key in key_list ]

    def __get_key_list_for_retrospective_number__(self):
        return self._tick_key_list

    def get_waves_numbers_for_wave_tick(self, wave_type: str, index: str, wave_tick: WaveTick):
        if wave_tick.date_str in self.date_list:
            key = '{}_{}'.format(index, wave_type)
            date_number_dict = self._index_wave_type_number_dict[key]
            return date_number_dict[wave_tick.date_str]
        return 0

    def fill_wave_type_number_dict_for_ticks_in_wave_tick_list(self, wave_tick_list: WaveTickList, index: str):
        for wave_type in self._wave_types:
            key = '{}_{}'.format(index, wave_type)
            if key in self._index_wave_type_number_dict:
                date_number_dict = self._index_wave_type_number_dict[key]
                for wave_tick in wave_tick_list.tick_list:
                    if wave_tick.date_str in date_number_dict:
                        number = date_number_dict[wave_tick.date_str]
                        if number > 0:
                            wave_tick.add_to_wave_type_number_dict(wave_type, number)
        wave_tick_list.fill_wave_type_number_dicts()  # we need some min max values for the wave numbers

    def __fill_variables_according_to_ticks__(self):
        if not self._df_wave.empty:
            self.__fill_tick_key_range_dict__()
            self.__fill_retrospective_index_wave_type_number_dict__()

    def __fill_tick_key_range_dict__(self):
        self._tick_key_list = []
        self._tick_key_timestamp_range_dict = {}
        ts_start = self._range_timestamp_start
        while ts_start <= self._range_timestamp_end:
            ts_end = ts_start + self._seconds_unit
            if self._period == PRD.DAILY:
                key = str(MyDate.get_date_from_epoch_seconds(ts_start))
            else:
                key = ts_start
            self._tick_key_list.append(key)
            self._tick_key_timestamp_range_dict[key] = [ts_start, ts_end]
            ts_start = ts_start + self._seconds_unit

    def __fill_retrospective_index_wave_type_number_dict__(self):
        self._index_wave_type_number_dict = {}
        for wave_type in WAVEST.get_waves_types_for_processing():
            df_base = self._df_dict_by_wave_types[wave_type]
            df_base = df_base[df_base[DC.WAVE_END_TS] >= self._range_timestamp_start]
            for index in self._index_list:
                key = '{}_{}'.format(index, wave_type)
                df_index = df_base[df_base[DC.INDEX] == index]
                key_number_dict = {}
                for tick_key in self._tick_key_list:
                    ts_range = self._tick_key_timestamp_range_dict[tick_key]
                    df_final = df_index[np.logical_and(
                                    df_index[DC.WAVE_END_TS] >= ts_range[0],
                                    df_index[DC.WAVE_END_TS] < ts_range[1])]
                    key_number_dict[tick_key] = df_final.shape[0]
                self._index_wave_type_number_dict[key] = key_number_dict

    def __get_df_wave__(self):
        access_layer_wave = AccessLayer4Wave(self._db_stock)
        if self._period == PRD.DAILY:
            if self._and_clause == '':
                offset_timestamp = MyDate.get_offset_timestamp(days=-self._limit)
                where_clause = '{}>={}'.format(DC.WAVE_END_TS, offset_timestamp)
            else:
                where_clause = self._and_clause
            df = access_layer_wave.get_daily_wave_data_frame(where_clause)
        else:
            offset_timestamp = MyDate.get_offset_timestamp(min=-self._limit)
            where_clause = '{}={} AND {}>={}'.format(DC.PERIOD_AGGREGATION, self._aggregation,
                                                     DC.WAVE_END_TS, offset_timestamp)
            df = access_layer_wave.get_intraday_wave_data_frame(where_clause)
        if not df.empty:
            df[DC.INDEX] = df[DC.TICKER_ID].apply(self.__get_index_for_symbol__)
        return df

    def __get_index_for_symbol__(self, ticker_id: str):
        return self._index_config.get_index_for_symbol(ticker_id)