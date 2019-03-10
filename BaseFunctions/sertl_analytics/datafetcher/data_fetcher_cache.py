"""
Description: This module contains the data fetcher cache classes for stock dataframes (either by DB or requests).
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-24
"""

from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import PRD


class DataFetcherCacheKey:
    def __init__(self, ticker: str, period: str, aggregation: int):
        self.ticker_id = ticker
        self.period = period
        self.aggregation = aggregation

    @property
    def key(self):
        return 'ticker={}_period={}_aggregation={}'.format(self.ticker_id, self.period, self.aggregation)

    @property
    def valid_until_ts(self) -> int:
        time_stamp_now = MyDate.time_stamp_now()
        if self.period == PRD.DAILY:
            return time_stamp_now + int(MyDate.get_seconds_for_period_aggregation(PRD.DAILY, 1)/2)
        return time_stamp_now + self.__get_intraday_cache_seconds__()

    @staticmethod
    def __get_intraday_cache_seconds__():
        return 20  # we want just to avoid too many requests within some seconds