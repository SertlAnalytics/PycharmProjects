"""
Description: This module detects pattern from any kind of input stream.
In the first version we concentrate our target on identifying stock pattern by given formation types.
In the second version we allow the system to find own patterns or change existing pattern constraints.
The main algorithm is CSP (constraint satisfaction problems) with binary constraints.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


from sertl_analytics.datafetcher.data_fetcher_cache import DataFetcherCacheKey
from sertl_analytics.constants.pattern_constants import PRD, OPS, DC
from salesman_database.salesman_db import SalesmanDatabase

from sertl_analytics.mydates import MyDate


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

    def get_kw_args(self):
        return {
            'symbol': self.ticker_id,
            'period': self.period,
            'aggregation': self.aggregation,
            'section': 'hist',
            'limit': self.limit,
            'output_size': self.output_size
        }


class SalesmanDataProvider:
    def __init__(self, db_salesman: SalesmanDatabase):
        self._db_salesman = db_salesman
        self.index_used = ''
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

    @staticmethod
    def get_mixed_dic():
        return {"TSLA": "Tesla", "FCEL": "Full Cell", "ONVO": "Organovo", "MRAM": "MRAM"}

    def __get_df_from_original_source__(self, data_fetcher_cache_key: PatternDataFetcherCacheKey):
        kw_args = data_fetcher_cache_key.get_kw_args()
        ticker_id = data_fetcher_cache_key.ticker_id
        return None

    def __get_data_fetcher_cache_key__(self) -> PatternDataFetcherCacheKey:
        cache_key_obj = PatternDataFetcherCacheKey(self.ticker_id, self.period, self.aggregation)
        cache_key_obj.from_db = self.from_db
        cache_key_obj.output_size = self.output_size
        cache_key_obj.and_clause = self.and_clause
        cache_key_obj.limit = self.limit
        return cache_key_obj

