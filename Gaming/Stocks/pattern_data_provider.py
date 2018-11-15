"""
Description: This module detects pattern from any kind of input stream.
In the first version we concentrate our target on identifying stock pattern by given formation types.
In the second version we allow the system to find own patterns or change existing pattern constraints.
The main algorithm is CSP (constraint satisfaction problems) with binary constraints.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import pandas as pd
import numpy as np
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, AlphavantageCryptoFetcher
from sertl_analytics.datafetcher.financial_data_fetcher import BitfinexCryptoFetcher, CryptoCompareCryptoFetcher
from sertl_analytics.datafetcher.data_fetcher_cache import DataFetcherCacheKey
from sertl_analytics.user_input.confirmation import UserInput
from sertl_analytics.constants.pattern_constants import CN, PRD, OPS, EQUITY_TYPE, Indices, DC
from pattern_database import stock_database
from sertl_analytics.mycache import MyCacheObjectApi
from sertl_analytics.mydates import MyDate
from pattern_database.stock_database import StockDatabase
from sertl_analytics.mycache import MyCache
from sertl_analytics.pybase.df_base import PyBaseDataFrame
from sertl_analytics.datafetcher.database_fetcher import DatabaseDataFrame
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList
from pattern_data_container import PatternDataHandler
from pattern_configuration import PatternConfiguration
from pattern_dash.my_dash_caches import MyDataFrameCache
import time


class DP:  # DataProvider
    ALPHAVANTAGE = 'Alphavantage'
    BITFINEX = 'Bitfinex'
    CRYPTO_COMPARE = 'CryptoCompare'


class PatternDataFetcherCacheKey(DataFetcherCacheKey):
    def __init__(self, ticker: str, period: str, aggregation: int):
        DataFetcherCacheKey.__init__(self, ticker, period, aggregation)
        self.from_db = False
        self.output_size = ''
        self.limit = 0
        self.and_clause = ''

    @property
    def key(self):
        return 'from_db={}_ticker={}_period={}_aggregation={}_output_size={}_limit={}_and_clause={}'.format(
            self.from_db, self.ticker_id, self.period, self.aggregation, self.output_size, self.limit, self.and_clause)


class PatternDataProvider:
    def __init__(self, config: PatternConfiguration, db_stock: StockDatabase, crypto_ccy_dic: dict,
                 df_cache: MyDataFrameCache):
        self.config = config
        self.provider_crypto = DP.BITFINEX
        self.provider_stocks = DP.ALPHAVANTAGE
        self._db_stock = db_stock
        self._crypto_ccy_dic = crypto_ccy_dic
        self._df_cache = df_cache
        self.from_db = True
        self.period = PRD.DAILY
        self.aggregation = 1
        self.output_size = OPS.COMPACT
        self.limit = 400
        self._and_clause = ''
        self.ticker_id = ''
        self.ticker_name = ''
        self.ticker_dict = {}
        self.pdh = None  # for the pattern data handler - for a dedicated ticker_id later

    @property
    def and_clause(self):
        if self._and_clause == '':
            return self.get_and_clause()
        return self._and_clause

    @and_clause.setter
    def and_clause(self, value: str):
        self._and_clause = value

    @property
    def equity_type(self) -> str:
        return EQUITY_TYPE.CRYPTO if self.ticker_id in self._crypto_ccy_dic else EQUITY_TYPE.SHARE

    @property
    def and_clause_for_pattern(self):
        return self.and_clause.replace(DC.DATE, DC.PATTERN_BEGIN_DT)

    @property
    def and_clause_for_trade(self):
        return self.and_clause.replace(DC.DATE, DC.PATTERN_RANGE_BEGIN_DT)

    @staticmethod
    def get_and_clause(dt_start=None, dt_end=None):
        if dt_start is None:
            date_start = MyDate.get_date_from_datetime()
            date_start = MyDate.adjust_by_days(date_start, -1)
            dt_end = MyDate.get_date_from_datetime()
            dt_end = MyDate.adjust_by_days(dt_end, 1)
        else:
            date_start = MyDate.get_date_from_datetime(dt_start)
        if dt_end:
            date_end = MyDate.get_date_from_datetime(dt_end)
            return "Date BETWEEN '{}' AND '{}'".format(date_start, date_end)
        return "Date >= '{}'".format(date_start)

    def set_parameter_from_db_and_daily(self):
        self.from_db = True
        self.period = PRD.DAILY
        self.aggregation = 1

    def use_index(self, index: str):
        if index == Indices.ALL_DATABASE:
            self.ticker_dict = self.get_all_in_database()
        elif index == Indices.MIXED:
            self.ticker_dict = self.get_mixed_dic()
        else:
            self.ticker_dict = IndicesComponentList.get_ticker_name_dic(index)

    def use_own_dic(self, dic: dict):
        self.ticker_dict = dic
        for symbol in self.ticker_dict:
            name_from_db = self._db_stock.get_name_for_symbol(symbol)
            if name_from_db != '':
                self.ticker_dict[symbol] = name_from_db

    def get_index_members_as_dict(self, index: str):
        if index == Indices.CRYPTO_CCY:
            return IndicesComponentList.get_ticker_name_dic(Indices.CRYPTO_CCY)
        elif index == Indices.DOW_JONES:
            return IndicesComponentList.get_ticker_name_dic(Indices.DOW_JONES)
            # return {'MMM': '3M', 'KO': 'Coca Cola'}
        elif index == Indices.NASDAQ100:
            return IndicesComponentList.get_ticker_name_dic(Indices.NASDAQ100)
            # return {'TSLA': 'Tesla', 'FCEL': 'Full Cell'}

    @staticmethod
    def get_mixed_dic():
        return {"TSLA": "Tesla", "FCEL": "Full Cell", "ONVO": "Organovo", "MRAM": "MRAM"}

    def get_all_in_database(self):
        query = 'SELECT Symbol, count(*) FROM Stocks GROUP BY Symbol HAVING count(*) > 4000'
        db_data_frame = DatabaseDataFrame(self._db_stock, query=query)
        return PyBaseDataFrame.get_rows_as_dictionary(db_data_frame.df, 'Symbol', ['Symbol'])

    def init_pattern_data_handler_for_ticker_id(self, ticker_id: str, and_clause: str, limit=400):
        df = self.__get_df_for_ticker_id__(ticker_id, and_clause, limit)
        if df is None:
            self.pdh = None
        else:
            self.pdh = PatternDataHandler(self.config, df)

    def __get_df_for_ticker_id__(self, ticker_id: str, and_clause: str, limit: int):
        self.ticker_id = ticker_id
        self.ticker_name = self.__get_ticker_name__()
        self.and_clause = and_clause
        self.limit = limit
        data_fetcher_cache_key = self.__get_data_fetcher_cache_key__()  # ToDo replace this kind of cache key...
        df_from_cache = self._df_cache.get_cached_object_by_key(data_fetcher_cache_key.key)
        if df_from_cache is not None:
            return df_from_cache
        df = self.__get_df_from_original_source__(data_fetcher_cache_key)
        self.__add_data_frame_to_cache__(df, data_fetcher_cache_key)
        return df

    def __get_ticker_name__(self):
        ticker_name = self._db_stock.get_name_for_symbol(self.ticker_id)
        if ticker_name == '':
            if self.ticker_id in self.ticker_dict:
                return self.ticker_dict[self.ticker_id]
            return self.ticker_id
        return ticker_name

    def __add_data_frame_to_cache__(self, df: pd.DataFrame, data_fetcher_cache_key: DataFetcherCacheKey):
        cache_api = MyCacheObjectApi()
        cache_api.key = data_fetcher_cache_key.key
        cache_api.object = df
        cache_api.valid_until_ts = data_fetcher_cache_key.valid_until_ts
        self._df_cache.add_cache_object(cache_api)

    def __get_df_from_original_source__(self, data_fetcher_cache_key: PatternDataFetcherCacheKey):
        ticker = data_fetcher_cache_key.ticker_id
        period = data_fetcher_cache_key.period
        aggregation = data_fetcher_cache_key.aggregation
        and_clause = data_fetcher_cache_key.and_clause
        limit = data_fetcher_cache_key.limit
        output_size = data_fetcher_cache_key.output_size
        if self.from_db:
            self.__handle_not_available_symbol__(data_fetcher_cache_key.ticker_id)
            stock_db_df_obj = stock_database.StockDatabaseDataFrame(self._db_stock, ticker, and_clause)
            return stock_db_df_obj.df_data
        elif ticker in self._crypto_ccy_dic or ticker[-3:] == 'USD':
            if self.provider_crypto == DP.BITFINEX:
                fetcher = BitfinexCryptoFetcher(ticker, period, aggregation, 'hist', limit)
            elif self.provider_crypto == DP.CRYPTO_COMPARE:
                fetcher = CryptoCompareCryptoFetcher(ticker, period, aggregation, limit)
            else:
                fetcher = AlphavantageCryptoFetcher(ticker, period, aggregation)
                time.sleep(10)  # to avoid problems with the data provider restrictions (requests per minute)
            return fetcher.df_data
        else:
            fetcher = AlphavantageStockFetcher(ticker, period, aggregation, output_size)
            if self.period == PRD.INTRADAY:
                return self.__get_with_concatenated_intraday_data__(fetcher.df_data)
            return fetcher.df_data

    def __get_data_fetcher_cache_key__(self) -> PatternDataFetcherCacheKey:
        cache_key_obj = PatternDataFetcherCacheKey(self.ticker_id, self.period, self.aggregation)
        cache_key_obj.from_db = self.from_db
        cache_key_obj.output_size = self.output_size
        cache_key_obj.and_clause = self.and_clause
        cache_key_obj.limit = self.limit
        return cache_key_obj

    def __handle_not_available_symbol__(self, ticker):
        if not self._db_stock.is_symbol_loaded(ticker):
            if UserInput.get_confirmation('{} is not available. Do you want to load it'.format(ticker)):
                name = UserInput.get_input('Please enter the name for the symbol {}'.format(ticker))
                if name == 'x':
                    exit()
                self._db_stock.update_stock_data_for_symbol(ticker, name)
            else:
                exit()

    @staticmethod
    def __get_with_concatenated_intraday_data__(df: pd.DataFrame):
        # df['time'] = df['time'].apply(datetime.fromtimestamp)
        df[CN.TIMESTAMP] = df.index.map(int)
        epoch_seconds_number = df.shape[0]
        epoch_seconds_max = df[CN.TIMESTAMP].max()
        epoch_seconds_diff = df.iloc[-1][CN.TIMESTAMP] - df.iloc[-2][CN.TIMESTAMP]
        epoch_seconds_end = epoch_seconds_max
        epoch_seconds_start = epoch_seconds_end - (epoch_seconds_number - 1) * epoch_seconds_diff
        time_series = np.linspace(epoch_seconds_start, epoch_seconds_end, epoch_seconds_number)
        df[CN.TIMESTAMP] = time_series
        df.set_index(CN.TIMESTAMP, drop=True, inplace=True)
        return df

    @staticmethod
    def __handle_difference_of_exchanges(df_cc: pd.DataFrame, df_bitfinex: pd.DataFrame):
        df_diff = df_cc - df_bitfinex
        print(df_cc.head())
        print(df_bitfinex.head())
        print(df_diff.head())

    @staticmethod
    def __cut_intraday_df_to_one_day__(df: pd.DataFrame) -> pd.DataFrame:
        index_first_row = df.index[0]
        index_last_row = df.index[-1]
        timestamp_one_day_before = index_last_row - (23 * 60 * 60)  # 23 = to avoid problems with the last trade shape
        if index_first_row < timestamp_one_day_before:
            return df.loc[timestamp_one_day_before:]
        return df