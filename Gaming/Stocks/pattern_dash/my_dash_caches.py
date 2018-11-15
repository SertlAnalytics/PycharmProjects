"""
Description: This module contains the dash caching classes, e.g. for dataframes and graphs
these positions.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""

from sertl_analytics.mycache import MyCache, MyCacheObjectApi
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import PRD


class MyTickerObjectCache(MyCache):
    def __init__(self, ):
        self._object_type = ''
        MyCache.__init__(self)

    def get_cache_id(self, ticker_id: str, period: str, minutes: int, days: int=1, **kwargs):
        base_id = 'my_{}_{}_{}'.format(self._object_type.lower(), ticker_id, period)
        if len(kwargs) == 0:
            return '{}_{}_days'.format(base_id, days) if period == PRD.DAILY else '{}_{}_min'.format(base_id, minutes)
        else:
            for key in kwargs:
                base_id = '{}_{}:{}'.format(base_id, key, kwargs[key])
            return base_id

    def get_cache_title(self, ticker_id: str, period: str, aggregation: int, days: int=1):
        if period == PRD.DAILY:
            return '{}: {} {} ({}days)'.format(self._object_type, ticker_id, period, days)
        return '{}: {} {} ({}min)'.format(self._object_type, ticker_id, period, aggregation)

    @staticmethod
    def get_cache_object_api(key: str, cache_object: object, period: str, refresh_interval: int) -> MyCacheObjectApi:
        api = MyCacheObjectApi()
        api.key = key
        api.object = cache_object
        if period == PRD.INTRADAY:
            api.valid_until_ts = MyDate.time_stamp_now() + refresh_interval
        else:
            api.valid_until_ts = MyDate.time_stamp_now() + 10 * 60 * 60  # 10 hours
        return api


class MyGraphCache(MyTickerObjectCache):
    def __init__(self, ):
        MyTickerObjectCache.__init__(self)
        self._object_type = 'Graph'


class MyDataFrameCache(MyTickerObjectCache):
    def __init__(self, ):
        MyTickerObjectCache.__init__(self)
        self._object_type = 'DataFrame'

