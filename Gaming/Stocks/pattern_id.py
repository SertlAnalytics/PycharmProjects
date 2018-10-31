"""
Description: This module contains the pattern id classes (with factory)
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-29
"""

from sertl_analytics.constants.pattern_constants import FT, PRD
from pattern_system_configuration import SystemConfiguration, debugger
from sertl_analytics.mydates import MyDate
from pattern_wave_tick import WaveTick
from pattern_range import PatternRangeMax, PatternRangeMin, PatternRange


class PatternID:
    def __init__(self, equity_type_id: int, ticker_id: str, pattern_type: str, period: str,
                 aggregation: int, pattern_range: PatternRange):
        self.equity_type_id = equity_type_id
        self.ticker_id = ticker_id
        self.pattern_type = pattern_type
        self.pattern_type_id = FT.get_id(self.pattern_type)
        self.period = period
        self.period_id = PRD.get_id(period)
        self.aggregation = aggregation
        self.pattern_range = pattern_range
        self.range_id = pattern_range.id
        self.and_clause = self.__get_search_and_clause__()

    @property
    def id(self):
        return '{}_{}_{}_{}_{}_{}'.format(self.equity_type_id, self.period_id, self.aggregation, self.ticker_id,
                                          self.pattern_type_id, self.range_id)

    @property
    def id_readable(self):
        return '{}_{}_{}_{}'.format(self.period, self.ticker_id, self.pattern_type, self.range_id)

    def __get_search_and_clause__(self):
        date_from = MyDate.get_datetime_object(self.pattern_range.tick_first.date_str)
        date_to = MyDate.get_datetime_object(self.pattern_range.tick_last.date_str)
        date_from = MyDate.adjust_by_days(date_from, -self.pattern_range.length)
        date_to = MyDate.adjust_by_days(date_to, self.pattern_range.length)
        return "Date BETWEEN '{}' AND '{}'".format(date_from, date_to)


class PatternIdFactory:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self.pdh = self.sys_config.pdh

    def get_pattern_id_from_pattern_id_string(self, pattern_id_str: str):
        # Example: 1_1_1_AAPL_12_2015-12-03_00:00_2016-01-07_00:00
        parts = pattern_id_str.split('_')
        equity_type_id = int(parts[0])
        period = PRD.get_period(int(parts[1]))
        aggregation = int(parts[2])
        pattern_type = FT.get_pattern_type(int(parts[4]))
        ts_from = MyDate.get_epoch_seconds_from_datetime(parts[5])
        ts_to = MyDate.get_epoch_seconds_from_datetime(parts[7])
        wave_tick_start = self.__get_wave_tick_for_pattern_range__(ts_from)
        wave_tick_end = self.__get_wave_tick_for_pattern_range__(ts_to)
        if wave_tick_start.is_local_max:
            pattern_range = PatternRangeMax(self.sys_config, wave_tick_start, 2)
            f_params = wave_tick_start.get_linear_f_params_for_high(wave_tick_end)
        else:
            pattern_range = PatternRangeMin(self.sys_config, wave_tick_start, 2)
            f_params = wave_tick_start.get_linear_f_params_for_low(wave_tick_end)
        pattern_range.add_tick(wave_tick_end, f_params)
        pattern_range.finalize_pattern_range()
        return PatternID(equity_type_id, parts[3], pattern_type, period, aggregation, pattern_range)

    def __get_wave_tick_for_pattern_range__(self, ts: int):
        return [tick for tick in self.sys_config.pdh.pattern_data.tick_list if tick.time_stamp == ts][0]
