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
from sertl_analytics.datafetcher.financial_data_fetcher import BitfinexCryptoFetcher
from sertl_analytics.datafetcher.data_fetcher_cache import DataFetcherCacheKey
from sertl_analytics.user_input.confirmation import UserInput
from sertl_analytics.pybase.loop_list import LL
from sertl_analytics.constants.pattern_constants import CN, PRD, OPS
from pattern_database import stock_database
from sertl_analytics.mycache import MyCacheObjectApi
from pattern_database.stock_database import StockDatabase
from sertl_analytics.mycache import MyCache


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


class PatternDataProviderApi:
    def __init__(self, from_db: bool, period: str, aggregation=1, output_size=OPS.COMPACT, limit=400):
        self.from_db = from_db
        self.period = period
        self.period_aggregation = aggregation
        self.output_size = output_size
        self.limit = limit


class PatternDataProvider:
    def __init__(self, db_stock: StockDatabase, crypto_ccy_dic: dict, api: PatternDataProviderApi):
        self._db_stock = db_stock
        self._crypto_ccy_dic = crypto_ccy_dic
        self._df_source_cache = MyCache()
        self._api = api

    def get_df_for_ticker(self, ticker: str, and_clause: str, limit=400):
        data_fetcher_cache_key = self.__get_data_fetcher_cache_key__(ticker, and_clause, limit)
        df_from_cache = self._df_source_cache.get_cached_object_by_key(data_fetcher_cache_key.key)
        if df_from_cache is not None:
            print('df_source from cache: {}'.format(data_fetcher_cache_key.key))
            return df_from_cache
        df = self.__get_df_from_original_source__(data_fetcher_cache_key)
        self.__add_data_frame_to_cache__(df, data_fetcher_cache_key)
        return df

    def __add_data_frame_to_cache__(self, df: pd.DataFrame, data_fetcher_cache_key: PatternDataFetcherCacheKey):
        cache_api = MyCacheObjectApi()
        cache_api.key = data_fetcher_cache_key.key
        cache_api.object = df
        cache_api.valid_until_ts = data_fetcher_cache_key.valid_until_ts
        self._df_source_cache.add_cache_object(cache_api)

    def __get_df_from_original_source__(self, data_fetcher_cache_key: PatternDataFetcherCacheKey):
        ticker = data_fetcher_cache_key.ticker_id
        period = data_fetcher_cache_key.period
        aggregation = data_fetcher_cache_key.aggregation
        and_clause = data_fetcher_cache_key.and_clause
        limit = data_fetcher_cache_key.limit
        output_size = data_fetcher_cache_key.output_size
        if self._api.from_db:
            self.__handle_not_available_symbol__(data_fetcher_cache_key.ticker_id)
            stock_db_df_obj = stock_database.StockDatabaseDataFrame(self._db_stock, ticker, and_clause)
            return stock_db_df_obj.df_data
        elif ticker in self._crypto_ccy_dic:
            if period == PRD.INTRADAY:
                # fetcher = CryptoCompareCryptoFetcher(ticker, period, aggregation, run_on_dash)
                fetcher = BitfinexCryptoFetcher(ticker, period, aggregation, 'hist', limit)
                # fetcher_last = BitfinexCryptoFetcher(ticker, period, aggregation, 'last')
                # self.__handle_difference_of_exchanges(fetcher.df_data, fetcher_bit.df_data)
                return fetcher.df_data
            else:
                fetcher = AlphavantageCryptoFetcher(ticker, period, aggregation)
                return fetcher.df_data
        else:
            fetcher = AlphavantageStockFetcher(ticker, period, aggregation, output_size)
            if self._api.period == PRD.INTRADAY:
                return self.__get_with_concatenated_intraday_data__(fetcher.df_data)
            return fetcher.df_data

    def __get_data_fetcher_cache_key__(self, ticker: str, and_clause: str, limit: int) -> PatternDataFetcherCacheKey:
        cache_key_obj = PatternDataFetcherCacheKey(ticker, self._api.period, self._api.period_aggregation)
        cache_key_obj.from_db = self._api.from_db
        cache_key_obj.output_size = self._api.output_size
        cache_key_obj.and_clause = and_clause
        cache_key_obj.limit = limit
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