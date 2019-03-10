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
from sertl_analytics.constants.pattern_constants import WAVEST, DC, INDICES, PRD
import pandas as pd


class FibonacciWaveHandler:
    def __init__(self, db_stock: StockDatabase):
        self._retrospective_ticks = 0
        self._access_layer_wave = AccessLayer4Wave(db_stock)
        self._for_dash = False
        self._period = ''
        self._aggregation = 0
        self._limit = 0
        self._wave_types = WAVEST.get_waves_types_for_processing(self._period)
        self._index_list = INDICES.get_index_list_for_waves_tab()
        self._index_config = IndexConfiguration(db_stock, self._index_list)
        self._seconds_unit = 0
        self._df_fetched_date_str = ''
        self._tick_key_list_for_retrospection = []  # either date_str from Daily or timestamp for Intraday
        self._daily_index_wave_type_number_dict = {}  # contains itself a dictionary {date: number, ..}
        self._intraday_index_wave_type_number_dict = {}  # contains itself a dictionary {ts: number, ..}
        self._df_wave = None

    def load_data(self, period=PRD.ALL, aggregation=1):  # with group by data frames
        print('Fibonacci_load_handler.load_data...')
        period = PRD.DAILY
        self._for_dash = True if period == PRD.ALL else False
        self._period = period
        self._aggregation = aggregation
        self._seconds_unit = self.__get_seconds_for_unit__()
        self._df_wave = self._access_layer_wave.get_grouped_by_for_wave_peak_plotting(self._period)
        self.__fill_waves_into_index_wave_type_number_dict__()
        self._df_fetched_date_str = MyDate.get_date_as_string_from_date_time()
        print('END Fibonacci_load_handler.load_data...')

    def __fill_waves_into_index_wave_type_number_dict__(self):
        self._daily_index_wave_type_number_dict = {}
        self._intraday_index_wave_type_number_dict = {}
        period_list = [PRD.INTRADAY, PRD.DAILY] if self._for_dash else [self._period]
        for wave_type in self._wave_types:
            df = self.__get_df_wave_for_wave_type__(wave_type)
            for index in self._index_list:
                key = '{}_{}'.format(index, wave_type)
                for period in period_list:
                    if period == PRD.INTRADAY:
                        self._intraday_index_wave_type_number_dict[key] = \
                            self.__get_key_number_dict_for_index_and_wave_type__(df, index, period)
                    else:
                        self._daily_index_wave_type_number_dict[key] = \
                            self.__get_key_number_dict_for_index_and_wave_type__(df, index, period)

    @staticmethod
    def __get_key_number_dict_for_index_and_wave_type__(df: pd.DataFrame, index: str, period: str):
        key_entry_number_dict = {}
        df_index = df[df[DC.INDEX] == index]
        for row_index, row in df_index.iterrows():
            key_entry = row[DC.WAVE_END_DATE] if period == PRD.DAILY else row[DC.WAVE_END_TS]
            key_entry_number_dict[key_entry] = row[DC.TICKER_ID]
        return key_entry_number_dict

    def __get_df_wave_for_wave_type__(self, wave_type: str) -> pd.DataFrame:
        period, direction = WAVEST.get_period_and_direction_for_wave_type(wave_type)
        df = self._df_wave[self._df_wave[DC.PERIOD] == period]
        return df[df[DC.WAVE_TYPE] == direction]

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
        return self._tick_key_list_for_retrospection

    def reload_data(self):
        self.load_data(period=self._period, aggregation=self._aggregation)

    def set_retrospective_tick_number(self, retrospective_ticks: int):
        self._retrospective_ticks = retrospective_ticks
        offset_time_stamp = MyDate.get_offset_timestamp(days=-retrospective_ticks)
        self._tick_key_list_for_retrospection = []
        while offset_time_stamp < MyDate.time_stamp_now():
            offset_time_stamp += self._seconds_unit
            date_str = str(MyDate.get_date_from_epoch_seconds(offset_time_stamp))
            self._tick_key_list_for_retrospection.append(date_str)

    def __get_seconds_for_unit__(self):
        return MyDate.get_seconds_for_period(days=1) if self._period == PRD.DAILY \
            else MyDate.get_seconds_for_period(min=self._aggregation)

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
        return self._daily_index_wave_type_number_dict[key]

    def get_waves_number_list_for_wave_type_and_index(self, wave_type: str, index: str):
        key = '{}_{}'.format(index, wave_type)
        unit_number_dict = self._daily_index_wave_type_number_dict[key]
        key_list = self.__get_key_list_for_retrospective_number__()
        return [unit_number_dict[tick_key] if tick_key in unit_number_dict else 0 for tick_key in key_list ]

    def __get_key_list_for_retrospective_number__(self):
        return self._tick_key_list_for_retrospection

    def get_waves_numbers_for_wave_tick(self, wave_type: str, index: str, wave_tick: WaveTick):
        if wave_tick.date_str in self.date_list:
            key = '{}_{}'.format(index, wave_type)
            date_number_dict = self._daily_index_wave_type_number_dict[key]
            return date_number_dict[wave_tick.date_str]
        return 0

    def fill_wave_type_number_dict_for_ticks_in_wave_tick_list(
            self, wave_tick_list: WaveTickList, index: str, period: str):
        for wave_type in self._wave_types:
            key = '{}_{}'.format(index, wave_type)
            index_wave_type_number_dict = self.__get_index_wave_type_number_dict_for_period__(period)
            if key in index_wave_type_number_dict:
                number_dict = index_wave_type_number_dict[key]
                for wave_tick in wave_tick_list.tick_list:
                    wave_tick_key = wave_tick.time_stamp if period == PRD.INTRADAY else wave_tick.date_str
                    if wave_tick_key in number_dict:
                        number = number_dict[wave_tick_key]
                        if number > 0:
                            wave_tick.add_to_wave_type_number_dict(wave_type, number)
        wave_tick_list.fill_wave_type_number_dicts()  # we need some min max values for the wave numbers

    def __get_index_wave_type_number_dict_for_period__(self, period: str):
        if period == PRD.INTRADAY:
            return self._intraday_index_wave_type_number_dict
        return self._daily_index_wave_type_number_dict
