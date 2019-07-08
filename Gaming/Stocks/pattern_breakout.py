"""
Description: This module contains the PatternBreakoutApi class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_function_container import PatternFunctionContainer
from sertl_analytics.constants.pattern_constants import FD, TT, PRD
from sertl_analytics.mymath import MyMath


class PatternBreakoutApi:
    def __init__(self, function_cont: PatternFunctionContainer):
        self.sys_config = function_cont.sys_config
        self.function_cont = function_cont
        self.tick_previous = None
        self.tick_breakout = None
        self.volume_mean_for_breakout = 0
        self.volume_forecast = 0
        self.constraints = None


class PatternBreakout:
    def __init__(self, api: PatternBreakoutApi):
        self.sys_config = api.sys_config
        self.function_cont = api.function_cont
        self.constraints = api.constraints
        self.tick_previous = api.tick_previous
        self.tick_breakout = api.tick_breakout
        self.volume_mean_part_entry = api.volume_mean_for_breakout
        self.volume_forecast = api.volume_forecast
        self.breakout_date = self.tick_breakout.date
        self.volume_change_pct = MyMath.divide(self.tick_breakout.volume, self.tick_previous.volume, 2, 0)
        self.tolerance_pct = self.constraints.tolerance_pct
        self.bound_upper = MyMath.round_smart(self.function_cont.get_upper_value(self.tick_breakout.f_var))
        self.bound_lower = MyMath.round_smart(self.function_cont.get_lower_value(self.tick_breakout.f_var))
        self.pattern_breadth = MyMath.round_smart(self.bound_upper - self.bound_lower)
        self.tolerance_range = MyMath.round_smart(self.pattern_breadth * self.tolerance_pct)
        self.limit_upper = MyMath.round_smart(self.bound_upper + self.tolerance_range)
        self.limit_lower = MyMath.round_smart(self.bound_lower - self.tolerance_range)
        self.breakout_direction = self.__get_breakout_direction__()
        self.sign = 1 if self.breakout_direction == FD.ASC else -1
        self.check_dict = {}

    def is_breakout_a_signal(self) -> bool:  # ToDo is_breakout a signal by ML algorithm
        counter = 0
        if self.__is_breakout_over_limit__():
            counter += 1
        else:
            self.check_dict['Limit'] = False
        # if self.__is_breakout_in_allowed_range__():
        #     counter += 1
        if self.is_volume_rising(10):  # i.e. 10% more volume required
            counter += 2
        else:
            self.check_dict['Volume'] = False
        if self.__is_breakout_powerful__():
            counter += 1
        else:
            self.check_dict['Powerful'] = False
        return counter >= 3

    def is_volume_rising(self, min_percentage: int):
        # we check raising against mean volume and against last tick volume - either of both.
        # print('is_volume_rising: volume_forecast={}, volume_meanPart_entry={}, min_percentage={}, p_volume={}'.format(
        #     self.volume_forecast, self.volume_mean_part_entry, min_percentage, self.tick_previous.volume
        # ))
        if self.volume_mean_part_entry == 0:  # we don't have volume information like for FOREX
            return True
        against_mean = MyMath.divide(self.volume_forecast, self.volume_mean_part_entry) > (100 + min_percentage) / 100
        against_last = MyMath.divide(self.volume_forecast, self.tick_previous.volume) > (100 + min_percentage) / 100
        return against_mean or against_last

    def get_details_for_annotations(self):
        if self.sys_config.period == PRD.INTRADAY:
            date_str = self.tick_breakout.time_str_for_f_var
        else:
            date_str = self.tick_breakout.date_str_for_f_var
        vol_change = (MyMath.divide(self.volume_forecast, self.volume_mean_part_entry, 2) - 1) * 100
        return '{} ({}) - Volume change: {}%'.format(date_str, self.tick_breakout.position, round(vol_change, 0))

    def __get_breakout_direction__(self) -> str:
        return FD.ASC if self.tick_breakout.close > self.bound_upper else FD.DESC

    def __is_breakout_powerful__(self) -> bool:
        return self.tick_breakout.is_sustainable() or (
                self.tick_breakout.tick_type != TT.DOJI and self.tick_breakout.has_gap_to(self.tick_previous))

    def __is_breakout_over_limit__(self) -> bool:
        limit_range = self.pattern_breadth if self.sys_config.config.breakout_over_congestion_range \
            else self.pattern_breadth * self.sys_config.config.breakout_range_pct
        if self.breakout_direction == FD.ASC:
            return self.tick_breakout.close >= (self.bound_upper + limit_range)
        else:
            return self.tick_breakout.close <= (self.bound_lower - limit_range)

    def __is_breakout_in_allowed_range__(self) -> bool:
        if self.breakout_direction == FD.ASC:
            return self.tick_breakout.close < self.bound_upper + self.pattern_breadth / 2
        else:
            return self.tick_breakout.close > self.bound_lower - self.pattern_breadth / 2
