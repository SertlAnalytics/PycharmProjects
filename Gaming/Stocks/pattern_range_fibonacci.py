"""
Description: This module contains the PatternRange class - central for stock data management
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT
from pattern_wave_tick import WaveTick
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_range import PatternRangeMax, PatternRangeMin, PatternRangeDetectorMax, PatternRangeDetectorMin
import math


class FibonacciFormation:
    def __init__(self, pattern_type: str, tick_start: WaveTick, tick_end: WaveTick):
        self.pattern_type = pattern_type
        self.tick_shoulder_left = None
        self.tick_start = tick_start
        self.tick_end = tick_end
        self.f_neckline_param = None

    @property
    def expected_win(self):  # distance from neckline to first shoulder
        return 0  # ToDo

    @property
    def height(self):  # distance from start to end
        if self.pattern_type == FT.FIBONACCI_UP:
            return self.tick_start.low - self.tick_end.high
        else:
            return self.tick_start.high - self.tick_end.low


class PatternRangeFibonacciUp(PatternRangeMin):
    def __init__(self, sys_config: SystemConfiguration, fib_form: FibonacciFormation, min_length: int):
        self.fib_form = fib_form
        PatternRangeMin.__init__(self, sys_config, fib_form.tick_start, min_length)

    @staticmethod
    def _get_covered_pattern_types_() -> list:
        return [FT.FIBONACCI_UP]


class PatternRangeFibonacciDown(PatternRangeMax):
    def __init__(self, sys_config: SystemConfiguration, fib_form: FibonacciFormation, min_length: int):
        self.fib_form = fib_form
        PatternRangeMax.__init__(self, sys_config, fib_form.tick_start, min_length)

    @staticmethod
    def _get_covered_pattern_types_() -> list:
        return [FT.FIBONACCI_DOWN]


class PatternRangeDetectorFibonacciBase:
    def __init__(self, sys_config: SystemConfiguration, tick_list: list):
        self.sys_config = sys_config
        self.pdh = self.sys_config.pdh
        self.tick_list = tick_list
        self.global_max_tuple_list = [(i, tick) for i, tick in enumerate(self.tick_list) if tick.is_global_max]
        self.global_min_tuple_list = [(i, tick) for i, tick in enumerate(self.tick_list) if tick.is_global_min]

    def get_pattern_range(self, number_required_ticks: int, fib_form: FibonacciFormation):
        other_ticks = self._get_intermediate_ticks_(fib_form)

        if fib_form.pattern_type == FT.FIBONACCI_UP:
            pattern_range = PatternRangeFibonacciUp(self.sys_config, fib_form, number_required_ticks)
        else:
            pattern_range = PatternRangeFibonacciDown(self.sys_config, fib_form, number_required_ticks)

        pattern_range.add_tick(fib_form.tick_start, fib_form.f_neckline_param)
        pattern_range.add_tick(fib_form.tick_end, fib_form.f_neckline_param)
        return pattern_range

    def get_tick_range(self, set_off: int, for_left: bool):
        return range(set_off - 1, 0, -1) if for_left else range(set_off + 1, len(self.tick_list)-1)

    def _get_intermediate_ticks_(self, fib_form: FibonacciFormation) -> list:
        compare_value = - math.inf if fib_form.pattern_type == FT.HEAD_SHOULDER else math.inf
        ticks_return = []

        tick_position_start = fib_form.tick_start
        tick_position_end = fib_form.tick_start

        for tick in self.tick_list:
            if tick.position > tick_position_start:
                if tick.position < tick_position_end:
                    pass
                else:
                    return ticks_return
        return ticks_return

    def _get_min_tick_list_for_end_point_(self, off_set: int, for_left: bool):
        min_value = math.inf
        list_return = []
        for k in self.get_tick_range(off_set, for_left):
            tick_k = self.tick_list[k]
            if tick_k.is_min:
                if tick_k.low < min_value:
                    list_return.append(tick_k)
                    min_value = tick_k.low
            elif tick_k.is_global_min:
                break
        return list_return

    def _get_max_tick_list_for_end_point_(self, off_set: int, for_left: bool):
        max_value = -math.inf
        list_return = []
        for k in self.get_tick_range(off_set, for_left):
            tick_k = self.tick_list[k]
            if tick_k.is_max:
                if tick_k.high > max_value:
                    list_return.append(tick_k)
                    max_value = tick_k.high
            elif tick_k.is_global_max:
                break
        return list_return


class PatternRangeDetectorFibonacciDown(PatternRangeDetectorMin, PatternRangeDetectorFibonacciBase):
    def __init__(self, sys_config: SystemConfiguration, tick_list: list):
        PatternRangeDetectorFibonacciBase.__init__(self, sys_config, tick_list)
        PatternRangeDetectorMin.__init__(self, sys_config, tick_list)

    @property
    def pattern_type(self):
        return FT.FIBONACCI_DOWN

    def __parse_tick_list__(self):
        for entries in self.global_max_tuple_list:
            index = entries[0]
            tick_start = entries[1]
            tick_list_end = self._get_min_tick_list_for_end_point_(index, True)
            for tick_end in tick_list_end:
                fib_form = FibonacciFormation(self.pattern_type, tick_start, tick_end)
                fib_form.f_neckline_param = self.__get_linear_f_params__(tick_start, tick_end)
                pattern_range = self.get_pattern_range(self.number_required_ticks, fib_form)
                if pattern_range is not None:
                    self.__add_pattern_range_to_list_after_check__(pattern_range)


class PatternRangeDetectorFibonacciUp(PatternRangeDetectorMax, PatternRangeDetectorFibonacciBase):
    def __init__(self, sys_config: SystemConfiguration, tick_list: list):
        PatternRangeDetectorFibonacciBase.__init__(self, sys_config, tick_list)
        PatternRangeDetectorMax.__init__(self, sys_config, tick_list)

    @property
    def pattern_type(self):
        return FT.FIBONACCI_UP

    def __parse_tick_list__(self):
        for entries in self.global_min_tuple_list:
            index = entries[0]
            tick_start = entries[1]
            tick_list_end = self._get_max_tick_list_for_end_point_(index, True)
            for tick_end in tick_list_end:
                fib_form = FibonacciFormation(self.pattern_type, tick_start, tick_end)
                fib_form.f_neckline_param = self.__get_linear_f_params__(tick_start, tick_end)
                pattern_range = self.get_pattern_range(self.number_required_ticks, fib_form)
                if pattern_range is not None:
                    self.__add_pattern_range_to_list_after_check__(pattern_range)
