"""
Description: This module contains the JobRuntime class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-23
"""

from sertl_analytics.mydates import MyDate


class JobRuntime:
    def __init__(self):
        self._start_date_time = ''
        self._start_ts = 0
        self._end_date_time = ''
        self._end_ts = 0

    @property
    def runtime_seconds(self) -> int:
        return self._end_ts - self._start_ts

    @property
    def runtime_minutes(self):
        return round((self._end_ts - self._start_ts)/60, 2)

    @property
    def start_date(self):
        return self._start_date_time.split(' ')[0]

    @property
    def start_time(self):
        return self._start_date_time.split(' ')[1]

    @property
    def end_date(self):
        return self._end_date_time.split(' ')[0]

    @property
    def end_time(self):
        return self._end_date_time.split(' ')[1]

    def start(self):
        self._start_date_time = MyDate.get_date_time_as_string_from_date_time()
        self._start_ts = MyDate.get_epoch_seconds_from_datetime()

    def stop(self):
        self._end_date_time = MyDate.get_date_time_as_string_from_date_time()
        self._end_ts = MyDate.get_epoch_seconds_from_datetime()

