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
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageForexFetcher, StooqIntradayFetcher
from sertl_analytics.datafetcher.financial_data_fetcher import BitfinexCryptoFetcher, CryptoCompareCryptoFetcher
from sertl_analytics.datafetcher.data_fetcher_cache import DataFetcherCacheKey
from sertl_analytics.user_input.confirmation import UserInput
from sertl_analytics.constants.pattern_constants import CN, PRD, OPS, INDICES, DC
from pattern_database import stock_database
from sertl_analytics.mycache import MyCacheObjectApi
from sertl_analytics.mydates import MyDate
from sertl_analytics.mymath import MyMath
from pattern_database.stock_database import StockDatabase
from sertl_analytics.pybase.df_base import PyBaseDataFrame
from sertl_analytics.datafetcher.database_fetcher import DatabaseDataFrame
from pattern_data_handler import PatternDataHandler
from pattern_configuration import PatternConfiguration
from pattern_index_configuration import IndexConfiguration
from pattern_dash.my_dash_caches import MyDataFrameCache
from pattern_logging.pattern_log import PatternLog
import copy


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
        self.offset = 0

    @property
    def key(self):
        return 'from_db={}_ticker={}_period={}_aggregation={}_output_size={}_limit={}_and_clause={}_offset={}'.format(
            self.from_db, self.ticker_id, self.period,
            self.aggregation, self.output_size, self.limit, self.and_clause, self.offset)

    def get_kw_args(self):
        return {
            'symbol': self.ticker_id,
            'period': self.period,
            'aggregation': self.aggregation,
            'section': 'hist',
            'limit': self.limit,
            'output_size': self.output_size,
            'offset': self.offset
        }


class PatternDataProvider:
    def __init__(self, config: PatternConfiguration, index_config: IndexConfiguration,
                 db_stock: StockDatabase, df_cache: MyDataFrameCache):
        self.config = config
        self.index_config = index_config
        self.provider_crypto = DP.BITFINEX
        self.provider_stocks = DP.ALPHAVANTAGE
        self._db_stock = db_stock
        self._df_cache = df_cache
        self.index_used = ''
        self.from_db = True
        self.period = PRD.DAILY
        self.aggregation = 1
        self.output_size = OPS.COMPACT
        self.limit = 400
        self.offset = 0
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
        return self.index_config.get_equity_type_for_symbol(self.ticker_id)

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

    def init_and_clause(self):
        if self.period == PRD.INTRADAY:
            minutes = self.aggregation * self.limit
            days = int(minutes / (60 * 24)) + 1
            dt_start = MyDate.get_date_from_datetime()
            dt_start = MyDate.adjust_by_days(dt_start, -days)
            dt_end = MyDate.get_date_from_datetime()
            dt_end = MyDate.adjust_by_days(dt_end, 1)
            self._and_clause = self.get_and_clause(dt_start, dt_end)
            # print('data_provider.and_clause={}'.format(self.and_clause))

    def use_index(self, index: str):
        self.index_used = index
        if index == INDICES.ALL_DATABASE:
            self.ticker_dict = self.get_all_in_database()
        elif index == INDICES.MIXED:
            self.ticker_dict = self.get_mixed_dic()
        elif index == INDICES.INDICES:
            self.ticker_dict = {"DJI": "Dow"}  # , "NDX": "Nasdaq"
        else:
            self.ticker_dict = self.index_config.get_ticker_dict_for_index(index, self.period)

    def use_indices(self, indices: list):
        self.index_used = ''
        self.ticker_dict = {}
        for index in indices:
            self.ticker_dict.update(self.index_config.get_ticker_dict_for_index(index))

    def use_own_dic(self, dic: dict):
        self.index_used = ''
        self.ticker_dict = dic
        for symbol in self.ticker_dict:
            name_from_db = self._db_stock.get_name_for_symbol(symbol)
            if name_from_db != '':
                self.ticker_dict[symbol] = name_from_db

    def start_after(self, ticker: str):  # to restart after an error
        ticker_dict_new = {}
        add_ticker = False
        for symbol in self.ticker_dict:
            if add_ticker:
                ticker_dict_new[symbol] = self.ticker_dict[symbol]
            else:
                if symbol == ticker:
                    add_ticker = True
        self.ticker_dict = ticker_dict_new

    def get_index_members_as_dict(self, index: str):
        return self.index_config.get_ticker_dict_for_index(index)

    @staticmethod
    def get_mixed_dic():
        return {"TSLA": "Tesla", "FCEL": "Full Cell", "ONVO": "Organovo", "MRAM": "MRAM"}

    def get_all_in_database(self):
        query = 'SELECT Symbol, count(*) FROM Stocks GROUP BY Symbol HAVING count(*) > 4000'
        db_data_frame = DatabaseDataFrame(self._db_stock, query=query)
        return PyBaseDataFrame.get_rows_as_dictionary(db_data_frame.df, 'Symbol', ['Symbol'])

    def init_pattern_data_handler_for_ticker_id(self, ticker_id: str, and_clause: str, limit=400, offset: int=0):
        df = None
        try:
            df = self.__get_df_for_ticker_id__(ticker_id, and_clause, limit, offset=offset)
            if self.period == PRD.INTRADAY:
                df = self.__get_df_adjusted_to_aggregation__(df)
        except IndexError:
            PatternLog().log_message('Error with ticker_id={}'.format(ticker_id),
                                     'init_pattern_data_handler_for_ticker_id')
            PatternLog().log_error()
        finally:
            if df is None:
                PatternLog().log_message('Error with ticker_id={}'.format(ticker_id),
                                         'init_pattern_data_handler_for_ticker_id')
                self.pdh = None
            else:
                self.pdh = PatternDataHandler(self.config, df)

    def __get_df_for_ticker_id__(self, ticker_id: str, and_clause: str, limit: int, offset: int=0):
        self.ticker_id = ticker_id
        self.ticker_name = self.__get_ticker_name__()
        self.and_clause = and_clause
        self.limit = limit
        self.offset = offset
        data_fetcher_cache_key = self.__get_data_fetcher_cache_key__()  # ToDo replace this kind of cache key...
        df_from_cache = self._df_cache.get_cached_object_by_key(data_fetcher_cache_key.key)
        if df_from_cache is not None:
            return df_from_cache
        df = self.__get_df_from_original_source__(data_fetcher_cache_key)
        if df is not None:
            self.__add_data_frame_to_cache__(df, data_fetcher_cache_key)
        return df

    def __get_df_adjusted_to_aggregation__(self, df: pd.DataFrame):  # is called only for PRD.INTRADAY
        source_aggregation = int((df.index[1] - df.index[0])/60)
        if source_aggregation == self.aggregation:
            return df
        source_rows_per_aggregation = int(self.aggregation/source_aggregation)
        row_list = []
        value_dict = {CN.OPEN: 0, CN.LOW: 0, CN.HIGH: 0, CN.CLOSE: 0, CN.VOL: 0}
        row_for_aggregation = {}
        row_counter_per_aggregation = 0
        for index, row in df.iterrows():
                if row_counter_per_aggregation == 0:
                    row_for_aggregation = copy.deepcopy(row)
                    for value_index in value_dict:
                        value_dict[value_index] = row[value_index]  # default values for new aggretation
                else:
                    value_dict[CN.LOW] = min(value_dict[CN.LOW], row[CN.LOW])
                    value_dict[CN.HIGH] = max(value_dict[CN.HIGH], row[CN.HIGH])
                    value_dict[CN.CLOSE] = row[CN.CLOSE]
                    value_dict[CN.VOL] += row[CN.VOL]
                row_counter_per_aggregation += 1
                if row_counter_per_aggregation == source_rows_per_aggregation or index == df.index[-1]:
                    for value_index, value in value_dict.items():
                        row_for_aggregation[value_index] = round(value, 0) \
                            if value_index == CN.VOL else MyMath.round_smart(value)
                    row_list.append(row_for_aggregation)
                    row_counter_per_aggregation = 0
        df_new = pd.DataFrame(row_list)
        return df_new

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
        kw_args = data_fetcher_cache_key.get_kw_args()
        ticker_id = data_fetcher_cache_key.ticker_id
        # print('__get_df_from_original_source__: ticker={}'.format(ticker))
        if self.from_db:
            and_clause = data_fetcher_cache_key.and_clause
            self.__handle_not_available_symbol__(ticker_id)
            stock_db_df_obj = stock_database.StockDatabaseDataFrame(self._db_stock, ticker_id, and_clause)
            return stock_db_df_obj.df_data
        elif self.index_config.is_symbol_crypto(ticker_id):
            if self.provider_crypto == DP.BITFINEX:
                fetcher = BitfinexCryptoFetcher()
            elif self.provider_crypto == DP.CRYPTO_COMPARE:
                fetcher = CryptoCompareCryptoFetcher()
            else:
                fetcher = AlphavantageCryptoFetcher()
            fetcher.retrieve_data(**kw_args)
            return fetcher.df_data
        else:
            if self.index_config.get_index_for_symbol(ticker_id) == INDICES.Q_FSE and self.period==PRD.INTRADAY:
                offset = data_fetcher_cache_key.offset
                fetcher = StooqIntradayFetcher()
                kw_args = fetcher.get_kw_args(self.period, self.aggregation, ticker_id, offset=offset)
            elif self.index_config.is_symbol_currency(ticker_id):
                fetcher = AlphavantageForexFetcher()
            else:
                fetcher = AlphavantageStockFetcher()
            fetcher.retrieve_data(**kw_args)
            if self.period == PRD.INTRADAY:
                return self.__get_with_concatenated_intraday_data__(fetcher.df_data)
            return fetcher.df_data

    def __get_data_fetcher_cache_key__(self) -> PatternDataFetcherCacheKey:
        cache_key_obj = PatternDataFetcherCacheKey(self.ticker_id, self.period, self.aggregation)
        cache_key_obj.from_db = self.from_db
        cache_key_obj.output_size = self.output_size
        cache_key_obj.and_clause = self.and_clause
        cache_key_obj.limit = self.limit
        cache_key_obj.offset = self.offset
        return cache_key_obj

    def __handle_not_available_symbol__(self, ticker):
        if not self._db_stock.is_symbol_loaded(ticker):
            if UserInput.get_confirmation('{} is not available. Do you want to load it'.format(ticker)):
                name = UserInput.get_input('Please enter the name for the _symbol {}'.format(ticker))
                if name == 'x':
                    exit()
                self._db_stock.update_stock_data_for_symbol(ticker, name)
            else:
                exit()

    @staticmethod
    def __get_with_concatenated_intraday_data__(df: pd.DataFrame):
        # _df['time'] = _df['time'].apply(datetime.fromtimestamp)
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

