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
from sertl_analytics.constants.pattern_constants import WAVEST, DC, WPDT, PRD, INDICES
import pandas as pd
import statistics
import math
import numpy as np


class FibonacciWaveDataHandler:
    def __init__(self, db_stock: StockDatabase):
        self._access_layer_wave = AccessLayer4Wave(db_stock)
        self._index_list = INDICES.get_index_list_for_waves_tab()
        self._index_config = IndexConfiguration(db_stock, self._index_list)
        self._tick_key_list_for_retrospection = []
        self._period_for_retrospection = ''
        self._aggregation_for_retrospection = 1

    def __init_by_period_and_aggregation__(self, period=PRD.ALL, aggregation=1):
        self._period = period
        self._aggregation = aggregation
        self._period_list = [PRD.INTRADAY, PRD.DAILY] if period == PRD.ALL else [period]
        self._wave_types = WAVEST.get_waves_types_for_processing(self._period_list)
        self._fibonacci_wave_data_dict = self.__get_fibonacci_wave_data_dict__()

    @property
    def df_wave(self):
        for fibonacci_wave_data in self._fibonacci_wave_data_dict.values():
            return fibonacci_wave_data.df_wave

    @property
    def wave_types(self) -> list:
        return self._wave_types

    @property
    def tick_key_list_for_retrospection(self):
        return self._tick_key_list_for_retrospection

    @property
    def period_for_retrospection(self):
        return self._period_for_retrospection

    def load_data(self, period=PRD.ALL, aggregation=1):
        self.__init_by_period_and_aggregation__(period, aggregation)
        for fibonacci_wave_data in self._fibonacci_wave_data_dict.values():
            if fibonacci_wave_data.is_defined_for_period_and_aggregation(period, aggregation):
                fibonacci_wave_data.load_data()

    def reload_data_when_outdated(self, enforce_reload=False) -> bool:
        data_reloaded = False
        for fibonacci_wave_data in self._fibonacci_wave_data_dict.values():
            if fibonacci_wave_data.reload_data_when_outdated(enforce_reload):
                data_reloaded = True
        return data_reloaded

    def init_tick_key_list_for_retrospection(self, retrospective_ticks: int, period: str, aggregation=1):
        self._tick_key_list_for_retrospection = []
        self._period_for_retrospection = period
        self._aggregation_for_retrospection = aggregation
        offset_ts = self.__get_offset_time_stamp__(retrospective_ticks, period, aggregation)
        seconds_aggregation = MyDate.get_seconds_for_period_aggregation(period, aggregation)
        while offset_ts < MyDate.time_stamp_now():
            offset_ts += seconds_aggregation
            key = str(MyDate.get_date_from_epoch_seconds(offset_ts)) if period == PRD.DAILY else offset_ts
            self._tick_key_list_for_retrospection.append(key)

    def fill_wave_type_number_dict_for_ticks_in_wave_tick_list(
            self, wave_tick_list: WaveTickList, index: str, period: str):
        for wave_peak_date_type in WPDT.get_types_for_period(period):
            self._fibonacci_wave_data_dict[wave_peak_date_type].\
                fill_wave_type_number_dict_for_ticks_in_wave_tick_list(wave_tick_list, index)
        wave_tick_list.fill_wave_type_number_dicts()  # we need some min max values for the wave numbers

    def get_waves_number_list_for_wave_type_and_index(self, wave_type: str, index: str):
        for wave_period_key in WPDT.get_types_for_period(self._period_for_retrospection):
            fibonacci_wave_data = self._fibonacci_wave_data_dict[wave_period_key]
            index_wave_type_key = '{}_{}'.format(index, wave_type)
            if index_wave_type_key in fibonacci_wave_data.index_wave_type_number_dict:
                number_dict = fibonacci_wave_data.index_wave_type_number_dict[index_wave_type_key]
                return [number_dict[key] if key in number_dict else 0 for key in self._tick_key_list_for_retrospection]

    @staticmethod
    def get_color_for_wave_type_and_period(wave_type: str, period: str):
        if period == PRD.DAILY:
            color = {WAVEST.DAILY_ASC: 'red', WAVEST.INTRADAY_ASC: 'magenta',
                     WAVEST.DAILY_DESC: 'yellowgreen', WAVEST.INTRADAY_DESC: 'cyan'}
        else:
            color = {WAVEST.INTRADAY_ASC: 'red', WAVEST.INTRADAY_DESC: 'yellowgreen'}
        return color.get(wave_type)

    def __get_fibonacci_wave_data_for_period__(self, period: str):
        if period == PRD.DAILY:
            return self._fibonacci_wave_data_dict[WPDT.DAILY_DATE]
        else:
            return self._fibonacci_wave_data_dict[WPDT.INTRADAY_30_TS]

    @staticmethod
    def __get_offset_time_stamp__(ticks: int, period: str, aggregation: int):
        offset_time_stamp = MyDate.get_offset_timestamp_for_period_aggregation(ticks, period, aggregation)
        if period == PRD.INTRADAY:
            offset_time_stamp = MyDate.get_time_stamp_rounded_to_previous_hour(offset_time_stamp)
        return offset_time_stamp

    def __get_fibonacci_wave_data_dict__(self):
        return {key: self.__get_new_fibonacci_wave_data_by_key__(key) for key in WPDT.get_types_for_period(self._period)}

    def __get_new_fibonacci_wave_data_by_key__(self, wave_peak_date_type: str):
        if wave_peak_date_type == WPDT.INTRADAY_DATE:
            return FibonacciWaveDataIntradayDate(self._access_layer_wave, self._index_config)
        elif wave_peak_date_type == WPDT.INTRADAY_15_TS:
            return FibonacciWaveDataIntraday15Timestamp(self._access_layer_wave, self._index_config)
        elif wave_peak_date_type == WPDT.INTRADAY_30_TS:
            return FibonacciWaveDataIntraday30Timestamp(self._access_layer_wave, self._index_config)
        return FibonacciWaveDataDailyDate(self._access_layer_wave, self._index_config)


class FibonacciWaveDataBase:
    def __init__(self, access_layer_wave: AccessLayer4Wave, index_config: IndexConfiguration):
        self._access_layer_wave = access_layer_wave
        self._index_config = index_config
        self._aggregation = self.__get_aggregation__()
        self._period = WPDT.get_period_for_wave_period_key(self.wave_peak_date_type)
        self._wave_types = WAVEST.get_waves_types_for_period(self._period)
        self._index_list = index_config.index_list
        self._data_last_fetched_time_stamp = 0
        self._index_wave_type_number_dict = {}  # contains itself a dictionary {wave_period_key: number, ..}
        self._df_wave = {}
        self._tick_key_list_for_retrospection = []

    @property
    def wave_peak_date_type(self):
        return WPDT.DAILY_DATE

    @property
    def index_wave_type_number_dict(self):
        return self._index_wave_type_number_dict

    @property
    def df_wave(self):
        return self._df_wave

    def load_data(self):  # with group by data frames
        self._df_wave = self._access_layer_wave.get_grouped_by_for_wave_peak_plotting(
            self.wave_peak_date_type, self._aggregation)
        if not self._df_wave.empty:
            self.__fill_waves_into_index_wave_type_number_dict__()
        self._data_last_fetched_time_stamp = MyDate.time_stamp_now()

    def is_defined_for_period_and_aggregation(self, period: str, aggregation: int) -> bool:
        if period == PRD.ALL:
            return True
        elif period == PRD.DAILY and self.wave_peak_date_type in [WPDT.DAILY_DATE, WPDT.INTRADAY_DATE]:
            return True
        elif period == PRD.INTRADAY == self._period and self._aggregation == aggregation:
            return True
        return False

    def reload_data_when_outdated(self, enforce_reload=False) -> bool:
        if not self.__are_wave_data_actual__() or enforce_reload:
            print('Reload wave data for {}'.format(self.wave_peak_date_type))
            self.load_data()
            return True
        return False

    def __fill_waves_into_index_wave_type_number_dict__(self):
        self._daily_index_wave_type_number_dict = {}
        self._intraday_index_wave_type_number_dict = {}
        for wave_type in self._wave_types:
            period, direction = WAVEST.get_period_and_direction_for_wave_type(wave_type)
            for index in self._index_list:
                key = '{}_{}'.format(index, wave_type)
                df = self.__get_df_wave_for_period_and_direction__(period, direction)
                self._index_wave_type_number_dict[key] =\
                    self.__get_key_number_dict_for_index_and_wave_type__(df, index, period)

    def __get_key_number_dict_for_index_and_wave_type__(self, df: pd.DataFrame, index: str, period: str):
        key_entry_number_dict = {}
        df_index = df[df[DC.EQUITY_INDEX] == index]
        for row_index, row in df_index.iterrows():
            key_entry = self.__get_wave_tick_key_for_number_dict__(row)
            key_entry_number_dict[key_entry] = row[DC.TICKER_ID]
        return key_entry_number_dict

    def __get_df_wave_for_period_and_direction__(self, period: str, direction: str) -> pd.DataFrame:
        df = self._df_wave[self._df_wave[DC.PERIOD] == period]
        return df[df[DC.WAVE_TYPE] == direction]

    def fill_wave_type_number_dict_for_ticks_in_wave_tick_list(self, wave_tick_list: WaveTickList, index: str):
        for wave_type in self._wave_types:
            key = '{}_{}'.format(index, wave_type)
            if key in self._index_wave_type_number_dict:
                number_dict = self._index_wave_type_number_dict[key]
                threshold = self.__get_threshold_for_index_and_wave_type_number_dict__(number_dict)
                for wave_tick in wave_tick_list.tick_list:
                    wave_tick_key = self.__get_wave_tick_key_for_number_dict__(wave_tick)
                    if wave_tick_key in number_dict:
                        number = number_dict[wave_tick_key]
                        if number > threshold:
                            wave_tick.add_to_wave_type_number_dict(wave_type, number)
        wave_tick_list.fill_wave_type_number_dicts()  # we need some min max values for the wave numbers

    @staticmethod
    def __get_threshold_for_index_and_wave_type_number_dict__(number_dict: dict):
        number_list = [number for number in number_dict.values()]
        threshold_mean = math.ceil(statistics.mean(number_list))
        threshold_p_80 = math.ceil(np.percentile(number_list, 80))
        threshold_p_85 = math.ceil(np.percentile(number_list, 85))
        threshold_p_90 = math.ceil(np.percentile(number_list, 90))
        return threshold_p_85

    def __are_wave_data_actual__(self) -> bool:
        return not self._access_layer_wave.is_wave_available_after_wave_end_ts(
            self._data_last_fetched_time_stamp, self._period)

    @staticmethod
    def __get_wave_tick_key_for_number_dict__(wave_object):
        if type(wave_object) is WaveTick:
            return wave_object.date_str
        return wave_object[DC.WAVE_END_DATE]

    @staticmethod
    def __get_aggregation__():
        return 1


class FibonacciWaveDataDailyDate(FibonacciWaveDataBase):
    @property
    def wave_peak_date_type(self):
        return WPDT.DAILY_DATE


class FibonacciWaveDataIntradayDate(FibonacciWaveDataBase):
    @property
    def wave_peak_date_type(self):
        return WPDT.INTRADAY_DATE


class FibonacciWaveDataIntradayTimestamp(FibonacciWaveDataBase):
    @staticmethod
    def __get_wave_tick_key_for_number_dict__(wave_object):
        if type(wave_object) is WaveTick:
            return wave_object.time_stamp
        return wave_object[DC.WAVE_END_TS]


class FibonacciWaveDataIntraday15Timestamp(FibonacciWaveDataIntradayTimestamp):
    @property
    def wave_peak_date_type(self):
        return WPDT.INTRADAY_15_TS

    @staticmethod
    def __get_aggregation__():
        return 15


class FibonacciWaveDataIntraday30Timestamp(FibonacciWaveDataIntradayTimestamp):
    @property
    def wave_peak_date_type(self):
        return WPDT.INTRADAY_30_TS

    @staticmethod
    def __get_aggregation__():
        return 30

