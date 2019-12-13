"""
Description: This module handles an index with all its number_members, like Q_FST, Nasdaq, Dow Jones
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-12-01
"""

from sertl_analytics.datafetcher.database_fetcher import DatabaseDataFrame
from pattern_database.stock_access_layer import AccessLayer4Stock
from sertl_analytics.mymath import MyMath
from sertl_analytics.mydates import MyDate
from statistics import mean
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentFetcher
from pattern_database.stock_database import StockDatabase, StockInsertHandler
from sertl_analytics.constants.pattern_constants import INDICES, PRD, CN
from sertl_analytics.my_pandas import MyPandas
import pandas as pd
import numpy as np
import statistics
import copy


class IndexMember:
    def __init__(self, symbol: str, name: str, df: pd.DataFrame, index_base_value: float):
        pass


class IndexHandler:
    def __init__(self, index: str, db_stock: StockDatabase, save_to_database=False):
        self._index = index
        self._db_stock = db_stock
        self._save_to_database = save_to_database
        self._access_layer = AccessLayer4Stock(db_stock)
        self._df_index = self._access_layer.get_all_as_data_frame(symbol=self._index, columns=self.columns)
        self._date_range_for_calculation = self.__get_date_range_for_index_calculation__()
        self._base_value_for_calculation = self.__get_index_base_value_for_calculation__()
        self._date_list = []
        self._date_timestamp_dict = {}
        self._member_symbol_list = []
        self._member_symbol_df_dict = {}
        self._adjusted_member_symbol_df_dict = {}

    @property
    def columns(self):
        return ['Symbol', 'Timestamp', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']

    @property
    def number_members(self) -> int:
        return len(self._member_symbol_list)

    @property
    def date_str_start(self):
        return self._date_range_for_calculation[0]

    @property
    def date_str_end(self):
        return self._date_range_for_calculation[1]

    def calculate_index_data_frame(self):
        if self.date_str_end < self.date_str_start:
            print('\n****The data for the index {} are already up-to-date. No calculation required.****'.format(
                self._index))
        else:
            self.__get_member_data__()
            self.__calculate_adjusted_member_symbol_df_dict__()
            self.__calculate_new_rows_for_df_index__()
            self._df_index.sort_values(CN.TIMESTAMP, inplace=True)
        self.print_df_index_details()

    def __calculate_new_rows_for_df_index__(self):
        for index, date_str in enumerate(self._date_list):
            counter = 0
            value_dict = {CN.OPEN: 0, CN.LOW: 0, CN.HIGH: 0, CN.CLOSE: 0, CN.VOL: 0}
            row_for_date = {}
            for symbol, df_adjusted in self._adjusted_member_symbol_df_dict.items():
                if counter == 0:
                    row_for_date = copy.deepcopy(df_adjusted.iloc[index])
                    row_for_date[CN.SYMBOL] = self._index
                row = df_adjusted.iloc[index]
                for value_index in value_dict:
                    value_dict[value_index] += row[value_index]
                counter += 1

            row_for_date[CN.TIMESTAMP] = int(row_for_date[CN.TIMESTAMP])
            for value_index, value in value_dict.items():
                row_for_date[value_index] = round(value, 0) if value_index == CN.VOL else MyMath.round_smart(value)

            if self._save_to_database:
                insert_handler = StockInsertHandler(self._index, PRD.DAILY, 1)
                insert_handler.add_data_frame_row(row_for_date[CN.TIMESTAMP], row_for_date)
                self._db_stock.insert_stocks_data(insert_handler.input_dict_list)
            self._df_index = self._df_index.append(row_for_date, ignore_index=True)
            print('Added to df_index: {}'.format(date_str))

    def __calculate_adjusted_member_symbol_df_dict__(self):
        self._adjusted_member_symbol_df_dict = {symbol: df.copy() for symbol, df in self._member_symbol_df_dict.items()}

        average_volume_dict = {symbol: int(df[CN.VOL].mean()) for symbol, df in self._member_symbol_df_dict.items()}
        total_volume = sum([average_volume for average_volume in average_volume_dict.values()])
        leverage_dict = {symbol: round(self._base_value_for_calculation / df.iloc[0][CN.CLOSE], 4)
                         for symbol, df in self._member_symbol_df_dict.items()}
        vol_prop_dict = {symbol: round(avg_vol / total_volume, 4) for symbol, avg_vol in average_volume_dict.items()}

        for symbol, df_adjusted in self._adjusted_member_symbol_df_dict.items():
            factor = leverage_dict[symbol] * vol_prop_dict[symbol]
            df_adjusted[CN.OPEN] = df_adjusted[CN.OPEN] * factor
            df_adjusted[CN.LOW] = df_adjusted[CN.LOW] * factor
            df_adjusted[CN.HIGH] = df_adjusted[CN.HIGH] * factor
            df_adjusted[CN.CLOSE] = df_adjusted[CN.CLOSE] * factor
            df_adjusted[CN.VOL] = df_adjusted[CN.VOL] * factor

    def __get_member_data__(self):
        self.__fill_date_iterables__()  # fills _date_list and _date_timestamp_dict
        self.__fill_member_symbol_list_for_date_range__()
        self.__fill_member_symbol_df_dict__()
        self.__fill_gaps_for_member_data_frames__()
        print('self._member_symbol_list ({}): {}'.format(len(self._member_symbol_list), self._member_symbol_list))
        print('self._date_list: {} - {}'.format(self.date_str_start, self.date_str_end))

    def print_df_index_details(self):
        print('')
        MyPandas.print_df_details(self._df_index)

    def __get_date_range_for_index_calculation__(self) -> list:
        date_range_values = self._access_layer.get_date_range_for_index(self._index)
        if self._df_index.shape[0] == 0:
            return date_range_values
        date_start = self._df_index.iloc[-1][CN.DATE]
        date_start = MyDate.get_date_str_from_datetime(MyDate.adjust_by_days(date_start, 1))
        return [date_start, date_range_values[1]]

    def __get_index_base_value_for_calculation__(self) -> float:
        if self._df_index.shape[0] == 0:
            return 1000
        return float(self._df_index.iloc[-1][CN.CLOSE])

    def __fill_date_iterables__(self):
        date_timestamp_list_all = self._access_layer.get_sorted_date_list_for_index(self._index)
        date_list_all, timestamp_list_all = date_timestamp_list_all[0], date_timestamp_list_all[1]
        for index, date_str in enumerate(date_list_all):
            if self.date_str_start <= date_str <= self.date_str_end:
                self._date_list.append(date_str)
                self._date_timestamp_dict[date_str] = timestamp_list_all[index]

    def __fill_member_symbol_df_dict__(self):
        df_dict = {}
        df_shape_list = []  # we need this to get the mean-we take only the symbols which have more ticks than the mean
        where_clause = "Date >= '{}' AND Date <= '{}'".format(self.date_str_start, self.date_str_end)
        for symbol in self._member_symbol_list:
            df_dict[symbol] = self._access_layer.get_all_as_data_frame(
                symbol=symbol, columns=self.columns, where_clause=where_clause)
            df_shape_list.append(df_dict[symbol].shape[0])
        mean_shape = statistics.mean(df_shape_list)
        self._member_symbol_df_dict = {symbol: df for symbol, df in df_dict.items() if df.shape[0] >= mean_shape}

    def __fill_member_symbol_list_for_date_range__(self):
        self._member_symbol_list = self._access_layer.get_symbol_list_for_index_in_date_range(
            self._index, self.date_str_start, self.date_str_end)

    def __get_df_index__(self) -> pd.DataFrame:
        return self._access_layer.get_all_as_data_frame(symbol=self._index, columns=self.columns)

    def __fill_gaps_for_member_data_frames__(self):
        print('Fill gaps for member data frames...')
        date_super_set = set(self._date_list)
        for symbol, df in self._member_symbol_df_dict.items():
            date_sub_set = set(df[CN.DATE])
            set_diff = date_super_set.difference(date_sub_set)
            print('Symbol: {} -> entries: {}'.format(symbol, df.shape[0]))
            if len(set_diff) > 0:
                self.__fill_gaps_for_member_data_frame__(df, set_diff, symbol)

    def __fill_gaps_for_member_data_frame__(self, df: pd.DataFrame, set_diff: set, symbol: str):
        insert_handler = StockInsertHandler(symbol, PRD.DAILY, 1)
        sorted_date_list = sorted(set_diff)
        row_new_list = []
        for date_str in sorted_date_list:
            index_date_str = self._date_list.index(date_str)
            date_str_previous = self._date_list[index_date_str - 1]
            df_truncated = df[df[CN.DATE] <= date_str_previous]  # we want the last valid row before this missing date
            row = copy.deepcopy(df_truncated.iloc[-1])
            row[CN.DATE] = date_str
            row[CN.TIMESTAMP] = self._date_timestamp_dict[date_str]
            row_new_list.append(row)
            print('Not available: {} for {}'.format(date_str, symbol))
        for row in row_new_list:
            df = df.append(row, ignore_index=True)
            insert_handler.add_data_frame_row(row[CN.TIMESTAMP], row)
        df.sort_values(CN.TIMESTAMP, inplace=True)
        if self._save_to_database:
            self._db_stock.insert_stocks_data(insert_handler.input_dict_list)

        print('...Symbol: {} (after filling gaps)-> entries: {}'.format(symbol, df.shape[0]))


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
