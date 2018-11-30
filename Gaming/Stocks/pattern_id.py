"""
Description: This module contains the pattern id classes (with factory)
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-29
"""

from sertl_analytics.constants.pattern_constants import FT, PRD
from sertl_analytics.mydates import MyDate


class PatternID:
    def __init__(self, **kwargs):
        if 'pattern_id' in kwargs:
            self.__init_by_pattern_id__(kwargs['pattern_id'])
        else:
            self.equity_type_id = kwargs['equity_type_id']
            self.period_id = PRD.get_id(kwargs['_period'])
            self.aggregation = kwargs['_aggregation']
            self.ticker_id = kwargs['ticker_id']
            self.pattern_type_id = FT.get_id(kwargs['pattern_type'])
            self.range_id = kwargs['pattern_range_id']
            self.__init_by_pattern_id__(self.id)

    def __old_init__(self, equity_type_id: int, period: str, aggregation: int,
                 ticker_id: str, pattern_type: str, pattern_range_id: str):
        self.equity_type_id = equity_type_id
        self.period_id = PRD.get_id(period)
        self.aggregation = aggregation
        self.ticker_id = ticker_id
        self.pattern_type_id = FT.get_id(pattern_type)
        self.range_id = pattern_range_id
        self.__init_by_pattern_id__(self.id)

    def init_by_pattern_id(self, pattern_id_str: str):
        self.init_by_pattern_id(self.id)

    def __init_by_pattern_id__(self, pattern_id_str: str):
        # Example: 1_1_1_AAPL_12_2015-12-03_00:00_2016-01-07_00:00
        parts = pattern_id_str.split('_')
        self.equity_type_id = int(parts[0])
        self.period_id = int(parts[1])
        self.period = PRD.get_period(self.period_id)
        self.aggregation = int(parts[2])
        self.ticker_id = parts[3]
        self.pattern_type_id = int(parts[4])
        self.pattern_type = FT.get_pattern_type(self.pattern_type_id)
        self.range_start_date_str = parts[5]
        self.range_start_time_str = parts[6]
        self.range_end_date_str = parts[7]
        self.range_end_time_str = parts[8]
        self.date_start = MyDate.get_datetime_object(self.range_start_date_str)
        self.date_end = MyDate.get_datetime_object(self.range_end_date_str)
        self.range_length = (self.date_end - self.date_start).days
        self.range_id = '{}_{}_{}_{}'.format(self.range_start_date_str, self.range_start_time_str,
                                             self.range_end_date_str, self.range_end_time_str)
        self.ts_from = MyDate.get_epoch_seconds_from_datetime(parts[5])
        self.ts_to = MyDate.get_epoch_seconds_from_datetime(parts[7])
        self.range_length_days = int((self.ts_to - self.ts_from)/(60*60*24))
        self.and_clause = self.__get_search_and_clause__()

    @property
    def id(self):
        return '{}_{}_{}_{}_{}_{}'.format(self.equity_type_id, self.period_id, self.aggregation, self.ticker_id,
                                          self.pattern_type_id, self.range_id)

    @property
    def id_readable(self):
        return '{}_{}_{}_{}'.format(self.period, self.ticker_id, self.pattern_type, self.range_id)

    def __get_search_and_clause__(self):
        date_from = MyDate.get_datetime_object(self.range_start_date_str)
        date_to = MyDate.get_datetime_object(self.range_end_date_str)
        date_from_adjusted = MyDate.adjust_by_days(date_from, -self.range_length_days)
        date_to_adjusted = MyDate.adjust_by_days(date_to, self.range_length_days)
        return "Date BETWEEN '{}' AND '{}'".format(date_from_adjusted, date_to_adjusted)

