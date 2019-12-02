"""
Description: This module calculates some indices which are not available as concrete index
Examples: Index Q_FSE (Quandle and Frankfurt Stock Exchange)
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-12-01
"""

from sertl_analytics.datafetcher.database_fetcher import DatabaseDataFrame
from pattern_database.stock_access_layer import AccessLayer4Stock
from sertl_analytics.mydates import MyDate
from statistics import mean
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentFetcher
from pattern_database.stock_database import StockDatabase
from sertl_analytics.constants.pattern_constants import INDICES, PRD, CN
import pandas as pd
import numpy as np


class IndexElement:
    def __init__(self, symbol: str, name: str, df: pd.DataFrame, index_base_value: float):
        self._symbol = symbol
        self._name = name
        self._df = df
        self._df_adjusted = df.copy()
        self._base_value = self.__get_base_value__()
        self._average_volume = int(self._df[CN.VOL].mean())
        self._leverage_factor = 0 if self._base_value == 0 else round(index_base_value/self._base_value, 2)
        self._index_total_average_volume = 0
        self._proportion_in_index = 0

    @property
    def average_volume(self) -> float:
        return self._average_volume

    def adjust_to_total_average_volume(self, index_total_average_volume: float):
        self._index_total_average_volume = index_total_average_volume
        self._proportion_in_index = round(self._average_volume/self._index_total_average_volume, 2)
        self._df_adjusted[CN.OPEN] = self._df_adjusted[CN.OPEN] * self._leverage_factor
        self._df_adjusted[CN.LOW] = self._df_adjusted[CN.LOW] * self._leverage_factor
        self._df_adjusted[CN.HIGH] = self._df_adjusted[CN.HIGH] * self._leverage_factor
        self._df_adjusted[CN.CLOSE] = self._df_adjusted[CN.CLOSE] * self._leverage_factor
        self._df_adjusted[CN.VOL] = self._df_adjusted[CN.VOL] * self._leverage_factor

    def print_element_detail(self):
        print('{}: Average volume={} (total={}), Proportion={}, Leverage={}'.format(
            self._symbol, self._average_volume, self._index_total_average_volume,
            self._proportion_in_index, self._leverage_factor))
        print(self._df.head())
        print(self._df_adjusted.head())

    def __get_base_value__(self) -> float:
        first_row = self._df.iloc[0]
        return mean([first_row[CN.OPEN], first_row[CN.LOW], first_row[CN.HIGH], first_row[CN.CLOSE]])


class IndexDataFrame:
    def __init__(self, stock_db: StockDatabase=None):
        self._base_value = 1000.0
        self._stock_db = StockDatabase() if stock_db is None else stock_db
        self._access_layer_stocks = AccessLayer4Stock(self._stock_db)
        self._columns = ['Symbol', 'Timestamp', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        self._index = self.__get_index__()
        self._period = PRD.DAILY
        self._aggregation = 1
        self._total_volume_average = 0
        self._index_elements = 0
        self._index_element_dict = {}
        self.__fill_ticker_element_dict__()
        self.__adjust_to_total_average_volume__()

    def print_details(self):
        print('Loaded details (loaded equities: {})'.format(len(self._index_element_dict)))
        for ticker, index_element in self._index_element_dict.items():
            index_element.print_element_detail()

    def get_index_data_frame_for_date_range(self, date_start: str, date_end: str):
        df_ticker_dict_within_range = {}
        for ticker, df in self._index_element_dict.items():
            df = df[np.logical_and(df[CN.DATE] >= date_start, df[CN.DATE] <= date_end)]
            if df.shape[0] > 0:
                df_ticker_dict_within_range[ticker] = df
        print('Dataframes with data in range: {}'.format(len(df_ticker_dict_within_range)))

    def __fill_ticker_element_dict__(self):
        ticker_dict = IndicesComponentFetcher.get_ticker_name_dic(self._index)
        for ticker in ticker_dict:
            name = ticker_dict[ticker]
            where_clause = "Symbol='{}' and Period='{}'".format(ticker, self._period)
            df = self._access_layer_stocks.get_all_as_data_frame(columns=self._columns, where_clause=where_clause)
            if df.shape[0] > 100:
                self._index_element_dict[ticker] = IndexElement(ticker, name, df, self._base_value)
                self._total_volume_average += self._index_element_dict[ticker].average_volume
                self._index_elements += 1
                print('Added: {}'.format(ticker))
                if len(self._index_element_dict) > 5:
                    break

    def __adjust_to_total_average_volume__(self):
        for ticker, index_element in self._index_element_dict.items():
            index_element.adjust_to_total_average_volume(self._total_volume_average)

    @staticmethod
    def __get_index__() -> str:
        return INDICES.Q_FSE
