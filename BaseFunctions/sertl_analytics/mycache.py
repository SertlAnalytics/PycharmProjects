"""
Description: This module is the central cache module: Base classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-07
"""

from sertl_analytics.mydates import MyDate


class MyCacheObjectApi:
    def __init__(self):
        self.key = None
        self.object = None
        self.valid_until_ts = None


class MyCacheObject:
    def __init__(self, cache_api: MyCacheObjectApi):
        self.id = cache_api.key
        self.object = cache_api.object
        self.valid_until_ts = cache_api.valid_until_ts
        self.valid_until_time = MyDate.get_time_from_epoch_seconds(self.valid_until_ts)

    def is_valid(self):
        if self.valid_until_ts is None:
            return True
        # print('{}: valid until {}'.format(self.id, self.valid_until_time))
        return MyDate.time_stamp_now() < self.valid_until_ts

    def print(self):
        now_t = MyDate.get_time_from_epoch_seconds(MyDate.time_stamp_now())
        # print('\nCached {}: valid_until={}, now={}'.format(self.id, self.valid_until_time, now_t))


class MyCache:
    def __init__(self):
        self._cached_object_dict = {}

    def add_cache_object(self, cache_api: MyCacheObjectApi):
        self._cached_object_dict[cache_api.key] = MyCacheObject(cache_api)
        self._cached_object_dict[cache_api.key].print()

    def get_cached_object_by_key(self, cache_key):
        if cache_key in self._cached_object_dict:
            if self._cached_object_dict[cache_key].is_valid():
                # print('Object from cache: {}'.format(cache_key))
                return self._cached_object_dict[cache_key].object
            else:
                del self._cached_object_dict[cache_key]
        return None

    def clear(self):
        self._cached_object_dict = {}