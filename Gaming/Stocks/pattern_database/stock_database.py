"""
Description: This module contains the configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, Date, DateTime, Time
from sertl_analytics.datafetcher.database_fetcher import BaseDatabase, DatabaseDataFrame
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, AlphavantageCryptoFetcher
from sertl_analytics.mydates import MyDate
from pattern_database.stock_tables import FeaturesTable, TradeTable, StocksTable, CompanyTable, STBL
import pandas as pd
import math
from datetime import datetime
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList
from sertl_analytics.constants.pattern_constants import Indices, CN, DC, PRD, OPS
import os
import time


class StockInsertData:
    def __init__(self):
        self.time_stamp = 0
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.volume = 0
        self._big_move = False
        self._direction = 0

    def set_direction_big_move(self, close_previous: float):
        if self.close != 0:
            if abs((close_previous - self.close) / self.close) > 0.03:
                self._big_move = True
                self._direction = math.copysign(1, self.close - close_previous)

    def get_dict_for_input(self, symbol: str, period: str, aggregation: int):
        if math.isnan(self.high):
            return {}
        date_time = MyDate.get_date_time_from_epoch_seconds(self.time_stamp)
        return {CN.PERIOD: period, CN.AGGREGATION: aggregation, CN.SYMBOL: symbol,
                CN.TIMESTAMP: self.time_stamp, CN.DATE: date_time.date(), CN.TIME: date_time.time(),
                CN.OPEN: self.open, CN.HIGH: self.high, CN.LOW: self.low, CN.CLOSE: self.close,
                CN.VOL: self.volume, CN.BIG_MOVE: self._big_move, CN.DIRECTION: self._direction}


class StockInsertHandler:
    def __init__(self, symbol: str, period: str, aggregation: int):
        self._symbol = symbol
        self._period = period
        self._aggregation = aggregation
        self._previous_close = 0
        self._input_dict_list = []

    @property
    def input_dict_list(self):
        return self._input_dict_list

    def add_data_frame_row(self, time_stamp: int, row):
        insert_data = StockInsertData()
        insert_data.time_stamp = time_stamp
        insert_data.open = float(row[CN.OPEN])
        insert_data.high = float(row[CN.HIGH])
        insert_data.low = float(row[CN.LOW])
        insert_data.close = float(row[CN.CLOSE])
        insert_data.volume = float(row[CN.VOL])
        self.__add_insert_data_to_list__(insert_data)

    def add_wave_tick(self, wave_tick):
        insert_data = StockInsertData()
        insert_data.time_stamp = wave_tick.time_stamp
        insert_data.open = wave_tick.open
        insert_data.high = wave_tick.high
        insert_data.low = wave_tick.low
        insert_data.close = wave_tick.close
        insert_data.volume = wave_tick.volume
        self.__add_insert_data_to_list__(insert_data)

    def __add_insert_data_to_list__(self, insert_data):
        insert_data.set_direction_big_move(self._previous_close)
        self._previous_close = insert_data.close
        input_dict = insert_data.get_dict_for_input(self._symbol, self._period, self._aggregation)
        if len(input_dict) > 0:
            self._input_dict_list.append(input_dict)


class StockDatabase(BaseDatabase):
    def __init__(self):
        BaseDatabase.__init__(self)
        self._crypto_ccy_dic = IndicesComponentList.get_ticker_name_dic(Indices.CRYPTO_CCY)
        self._sleep_seconds = 20
        self._dt_now_time_stamp = int(datetime.now().timestamp())
        self._stocks_table = StocksTable()
        self._company_table = CompanyTable()
        self._features_table = FeaturesTable()
        self._trade_table = TradeTable()

    def is_symbol_loaded(self, symbol: str):
        last_loaded_time_stamp_dic = self.__get_last_loaded_time_stamp_dic__(symbol)
        return len(last_loaded_time_stamp_dic) == 1

    def get_name_for_symbol(self, symbol: str):
        company_dic = self.__get_company_dict__(symbol)
        return '' if len(company_dic) == 0 else company_dic[symbol].Name

    def __get_engine__(self):
        db_path = self.__get_db_path__()
        return create_engine('sqlite:///' + db_path)

    def __get_db_name__(self):
        return 'MyStocks.sqlite'

    def __get_db_path__(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, self.__get_db_name__())

    def import_stock_data_by_deleting_existing_records(self, symbol: str, period=PRD.DAILY, output_size=OPS.COMPACT):
        self.delete_records("DELETE from Stocks WHERE Symbol = '" + str(symbol) + "'")
        input_dic = self.get_input_values_for_stock_table(period, symbol, output_size)
        self.__insert_data_into_table__('Stocks', input_dic)

    def update_stock_data_by_index(self, index: str, period=PRD.DAILY, aggregation=1):
        company_dict = self.__get_company_dict__()
        self.__check_company_dic_against_web__(index, company_dict)
        last_loaded_date_stamp_dic = self.__get_last_loaded_time_stamp_dic__()
        index_list = self.__get_index_list__(index)
        for index in index_list:
            print('\nUpdating {}...\n'.format(index))
            ticker_dic = IndicesComponentList.get_ticker_name_dic(index)
            for ticker in ticker_dic:
                self.__update_stock_data_for_single_value__(period, aggregation, ticker, ticker_dic[ticker],
                                                            company_dict, last_loaded_date_stamp_dic)
        self.__handle_error_cases__()

    def __check_company_dic_against_web__(self, index: str, company_dict: dict):
        company_dict_by_web = IndicesComponentList.get_ticker_name_dic(index)
        for key in company_dict_by_web:
            if key not in company_dict:
                name = company_dict_by_web[key]
                self.__insert_company_in_company_table__(key, name, True)
                new_dict = self.__get_company_dict__(key)
                company_dict[key] = new_dict[key]

    def update_crypto_currencies(self, period=PRD.DAILY, aggregation=1):
        company_dic = self.__get_company_dict__(like_input='USD')
        last_loaded_date_stamp_dic = self.__get_last_loaded_time_stamp_dic__(like_input='USD')
        print('\nUpdating {}...\n'.format(Indices.CRYPTO_CCY))
        ticker_dic = IndicesComponentList.get_ticker_name_dic(Indices.CRYPTO_CCY)
        for ticker in ticker_dic:
            self.__update_stock_data_for_single_value__(period, aggregation, ticker, ticker_dic[ticker],
                                                        company_dic, last_loaded_date_stamp_dic)
        self.__handle_error_cases__()

    def __handle_error_cases__(self):
        while len(self.error_handler.retry_dic) > 0:
            retry_dic = dict(self.error_handler.retry_dic)
            self.error_handler.retry_dic = {}
            for ticker in retry_dic:
                print('Handle error case for {}'.format(ticker))
                time.sleep(self._sleep_seconds)
                li = retry_dic[ticker]
                self.update_stock_data_for_symbol(ticker, li[0], li[1])

    def update_stock_data_for_symbol(self, symbol: str, name_input='', period=PRD.DAILY, aggregation=1):
        company_dic = self.__get_company_dict__(symbol)
        name = company_dic[symbol] if symbol in company_dic else name_input
        last_loaded_dict = self.__get_last_loaded_time_stamp_dic__(symbol)
        self.__update_stock_data_for_single_value__(period, aggregation, symbol, name, company_dic, last_loaded_dict)

    def insert_pattern_features(self, input_dict_list: list):
        self.__insert_data_into_table__('Features', input_dict_list)

    def insert_trade_data(self, input_dict_list: list):
        self.__insert_data_into_table__('Trade', input_dict_list)

    def __update_stock_data_for_single_value__(self, period: str, aggregation: int, ticker: str, name: str,
                                               company_dic: dict, last_loaded_date_stamp_dic: dict):
        name = self._company_table.get_alternate_name(ticker, name)
        last_loaded_time_stamp = last_loaded_date_stamp_dic[ticker] if ticker in last_loaded_date_stamp_dic else 100000
        process_type = self._stocks_table.get_process_type_for_update(
            period, aggregation, self._dt_now_time_stamp, last_loaded_time_stamp)
        if process_type == 'NONE':
            print('{} - {} is already up-to-date - no load required.'.format(ticker, name))
            return
        if ticker not in company_dic or company_dic[ticker].ToBeLoaded:
            output_size = OPS.FULL if process_type == 'FULL' else OPS.COMPACT
            try:
                if ticker in self._crypto_ccy_dic:
                    stock_fetcher = AlphavantageCryptoFetcher(ticker, period, aggregation)
                else:
                    stock_fetcher = AlphavantageStockFetcher(ticker, period, aggregation, output_size)
            except KeyError:
                self.error_handler.catch_known_exception(__name__, 'Ticker={}. Continue with next...'.format(ticker))
                self.error_handler.add_to_retry_dic(ticker, [name, period])
                time.sleep(self._sleep_seconds)
                return
            except:
                self.error_handler.catch_exception(__name__, 'Ticker={}. Continue with next...'.format(ticker))
                self.error_handler.add_to_retry_dic(ticker, [name, period])
                time.sleep(self._sleep_seconds)
                return
            df = stock_fetcher.df
            if ticker not in company_dic:
                to_be_loaded = df[CN.VOL].mean() > 10000
                self.__insert_company_in_company_table__(ticker, name, to_be_loaded)
                company_dic[ticker] = to_be_loaded
                if not to_be_loaded:
                    time.sleep(self._sleep_seconds)
                    return
            if ticker in last_loaded_date_stamp_dic:
                df = df.loc[last_loaded_time_stamp:].iloc[1:]
            if df.shape[0] > 0:
                input_list = self.__get_df_data_for_insert_statement__(df, period, ticker)
                self.__insert_data_into_table__('Stocks', input_list)
                print('{} - {}: inserted {} new ticks.'.format(ticker, name, df.shape[0]))
            time.sleep(self._sleep_seconds)

    def __get_company_dict__(self, symbol_input: str = '', like_input: str = ''):
        company_dict = {}
        query = self._company_table.get_select_query(symbol_input, like_input)
        db_df = DatabaseDataFrame(self, query)
        for index, rows in db_df.df.iterrows():
            company_dict[rows.Symbol] = rows
        return company_dict

    def __get_last_loaded_time_stamp_dic__(self, symbol_input: str = '', like_input: str = ''):
        last_loaded_time_stamp_dic = {}
        query = self._stocks_table.get_distinct_symbol_query(symbol_input, like_input)
        db_df = DatabaseDataFrame(self, query)
        loaded_symbol_list = [rows.Symbol for index, rows in db_df.df.iterrows()]
        for symbol in loaded_symbol_list:
            query = 'SELECT * FROM Stocks WHERE Symbol = "' + symbol + '" ORDER BY Timestamp Desc LIMIT 1'
            db_df = DatabaseDataFrame(self, query)
            try:
                last_loaded_time_stamp_dic[symbol] = db_df.df[CN.TIMESTAMP].values[0]
            except:
                print('Problem with __get_last_loaded_time_stamp_dic__ for {}'.format(symbol))
        return last_loaded_time_stamp_dic

    def __insert_company_in_company_table__(self, ticker: str, name: str, to_be_loaded: bool):
        input_dic = self._company_table.get_insert_dict_for_company(ticker, name, to_be_loaded)
        try:
            self.__insert_data_into_table__('Company', [input_dic])
        except Exception:
            self.error_handler.catch_exception(__name__)
            print('{} - {}: problem inserting into Company table.'.format(ticker, name))

    @staticmethod
    def __get_index_list__(index: str):
        return [Indices.DOW_JONES, Indices.NASDAQ100, Indices.SP500] if index == Indices.ALL else [index]

    def get_input_values_for_stock_table(self, period, symbol: str, output_size: OPS):
        stock_fetcher = AlphavantageStockFetcher(symbol, period, output_size)
        df = stock_fetcher.__get_data_frame__()
        return self.__get_df_data_for_insert_statement__(df, period, symbol)

    @staticmethod
    def __get_df_data_for_insert_statement__(df: pd.DataFrame, period: str, symbol: str, aggregation=1):
        insert_handler = StockInsertHandler(symbol, period, aggregation)
        for time_stamp, row in df.iterrows():
            insert_handler.add_data_frame_row(time_stamp, row)
        return insert_handler.input_dict_list

    def save_tick_list(self, tick_list: list, symbol: str, period: str, aggregation: int):
        insert_handler = StockInsertHandler(symbol, period, aggregation)
        for wave_tick in tick_list:
            if not self.is_stock_data_already_available(symbol, wave_tick.time_stamp, period, aggregation):
                insert_handler.add_wave_tick(wave_tick)
        self.__insert_data_into_table__(STBL.STOCKS, insert_handler.input_dict_list)

    def create_stocks_table(self):
        self.__create_table__(STBL.STOCKS)

    def create_company_table(self):
        self.__create_table__(STBL.COMPANY)

    def create_features_table(self):
        self.__create_table__(STBL.FEATURES)

    def create_trade_table(self):
        self.__create_table__(STBL.TRADE)

    def __insert_feature_in_feature_table__(self, ticker: str, input_dic: dict):
        try:
            self.__insert_data_into_table__('Features', [input_dic])
        except Exception:
            self.error_handler.catch_exception(__name__)
            print('{}: problem inserting into Features table.'.format(ticker))

    def is_stock_data_already_available(self, symbol: str, time_stamp: int, period: str, aggregation: int) -> bool:
        query = self._stocks_table.get_query_for_unique_record(symbol, time_stamp, period, aggregation)
        db_df = DatabaseDataFrame(self, query)
        return db_df.df.shape[0] > 0

    def are_features_already_available(self, features_id: str) -> bool:
        query = self._features_table.get_query_for_unique_record_by_id(features_id)
        db_df = DatabaseDataFrame(self, query)
        return db_df.df.shape[0] > 0

    def get_features_records_as_dataframe(self) -> pd.DataFrame:
        query = self._features_table.get_query_for_records()
        db_df = DatabaseDataFrame(self, query)
        return db_df.df

    def is_trade_already_available(self, trade_id: str) -> bool:
        query = self._trade_table.get_query_for_unique_record_by_id(trade_id)
        db_df = DatabaseDataFrame(self, query)
        return db_df.df.shape[0] > 0

    def get_trade_records_as_dataframe(self) -> pd.DataFrame:
        query = self._trade_table.get_query_for_records()
        db_df = DatabaseDataFrame(self, query)
        return db_df.df

    def delete_existing_trade(self, trade_id: str):
        if self.is_trade_already_available(trade_id):
            self.delete_records(self._trade_table.get_query_for_delete_by_id(trade_id))

    def get_features_differences_to_saved_version(self, features_dict: dict) -> dict:
        query = self._features_table.get_query_for_unique_record_by_id(features_dict[DC.ID])
        db_df = DatabaseDataFrame(self, query)
        df_first = db_df.df.iloc[0]
        return {key: [str(df_first[key]), str(features_dict[key])] for key, values in features_dict.items()
                if str(df_first[key]) != str(features_dict[key])}

    def __create_table__(self, table_name: str):
        metadata = MetaData()
        table = self.__get_table_by_name__(table_name)
        exec(table.description)
        self.create_database_elements(metadata)
        table_obj = metadata.tables.get(table_name)
        print(repr(table_obj))

    def __get_table_by_name__(self, table_name: str):
        return {STBL.STOCKS: self._stocks_table, STBL.COMPANY: self._company_table,
                STBL.FEATURES: self._features_table, STBL.TRADE: self._trade_table}.get(table_name, None)


class StockDatabaseDataFrame(DatabaseDataFrame):
    def __init__(self, db: StockDatabase, symbol='', and_clause='', period=PRD.DAILY, aggregation=1):
        self.symbol = symbol
        self.statement = "SELECT * from Stocks WHERE Symbol = '{}' and Period = '{}' and Aggregation = {}".format(
            symbol, period, aggregation)
        if and_clause != '':
            self.statement += ' and ' + and_clause
        DatabaseDataFrame.__init__(self, db, self.statement)
        if self.df.shape[0] == 0:
            self.df_data = None
        else:
            self.df.set_index(CN.TIMESTAMP, drop=False, inplace=True)
            self.column_data = [CN.CLOSE]
            self.df_data = self.df[[CN.OPEN, CN.HIGH, CN.LOW, CN.CLOSE, CN.VOL, CN. TIMESTAMP, CN.BIG_MOVE, CN.DIRECTION]]


