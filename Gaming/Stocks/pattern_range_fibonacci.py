"""
Description: This module contains the PatternRange class - central for stock data management
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, CN, FD
from pattern_wave_tick import WaveTick
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_range import PatternRangeMax, PatternRangeMin, PatternRangeDetectorMax, PatternRangeDetectorMin
from fibonacci.fibonacci_wave_tree import FibonacciWaveTree, FibonacciWave
import math
import pandas as pd
import numpy as np


class FibonacciFormation:
    def __init__(self, pattern_type: str, tick_start: WaveTick, tick_end: WaveTick, fibonacci_tree: FibonacciWaveTree):
        self.pattern_type = pattern_type
        self.tick_start = tick_start
        self.tick_end = tick_end
        self.fibonacci_tree = fibonacci_tree
        self.valid_wave_list = self.__get_valid_wave_list__()
        self.valid_wave = self.valid_wave_list[0] if self.valid_wave_list else None

    @property
    def are_valid_waves_available(self):
        return len(self.valid_wave_list) > 0

    @property
    def f_upper(self):
        return self.valid_wave.f_upper

    @property
    def f_lower(self):
        return self.valid_wave.f_lower

    @property
    def max_positions_after_tick_for_helper(self):
        return self.valid_wave.w_5.duration

    @property
    def expected_win(self):
        return 0  # ToDo

    @property
    def height(self):  # distance from start to end
        if self.pattern_type == FT.FIBONACCI_ASC:
            return self.tick_start.low - self.tick_end.high
        else:
            return self.tick_start.high - self.tick_end.low

    def get_minimal_retracement_range_after_wave_finishing(self):
        return self.valid_wave.get_minimal_retracement_range_after_finishing()

    def __get_valid_wave_list__(self):
        return_list = []  # we need waves where the neckline does not intersect the fibonacci wave
        for fib_wave in self.fibonacci_tree.fibonacci_wave_list:
            check_dict = {'neckline_without_intersection': fib_wave.is_neckline_criteria_fulfilled(),
                          'triangle_formation': fib_wave.is_closing_triangle_criteria_fulfilled()}
            if False not in check_dict.values():
                    return_list.append(fib_wave)
        return return_list


class PatternRangeFibonacciAsc(PatternRangeMin):
    def __init__(self, sys_config: SystemConfiguration, fib_form: FibonacciFormation):
        self.fib_form = fib_form
        PatternRangeMin.__init__(self, sys_config, fib_form.tick_start, 2)

    @staticmethod
    def _get_covered_pattern_types_() -> list:
        return [FT.FIBONACCI_ASC]

    def __fill_f_param_list__(self):
        self._f_param_list = [self.fib_form.f_upper]


class PatternRangeFibonacciDesc(PatternRangeMax):
    def __init__(self, sys_config: SystemConfiguration, fib_form: FibonacciFormation):
        self.fib_form = fib_form
        PatternRangeMax.__init__(self, sys_config, fib_form.tick_start, 2)

    @staticmethod
    def _get_covered_pattern_types_() -> list:
        return [FT.FIBONACCI_DESC]

    def __fill_f_param_list__(self):
        self._f_param_list = [self.fib_form.f_lower]


class PatternRangeDetectorFibonacciBase:
    def __init__(self, sys_config: SystemConfiguration, tick_list: list):
        self.sys_config = sys_config
        self.pdh = self.sys_config.pdh
        self.df = self.pdh.pattern_data_fibonacci.df
        self.tick_list = tick_list
        self.global_max_tuple_list = [(i, tick) for i, tick in enumerate(self.tick_list) if tick.is_global_max]
        self.global_min_tuple_list = [(i, tick) for i, tick in enumerate(self.tick_list) if tick.is_global_min]

    def get_pattern_range(self, fib_form: FibonacciFormation):
        if fib_form.pattern_type == FT.FIBONACCI_ASC:
            pattern_range = PatternRangeFibonacciAsc(self.sys_config, fib_form)
            f_param = fib_form.f_lower
        else:
            pattern_range = PatternRangeFibonacciDesc(self.sys_config, fib_form)
            f_param = fib_form.f_upper

        pattern_range.add_tick(fib_form.tick_end, f_param)
        pattern_range.finalize_pattern_range()
        return pattern_range

    def get_tick_range(self, off_set: int):
        return range(off_set + 1, len(self.tick_list))

    def __get_fibonacci_wave_tree_for_formation__(self, tick_start: WaveTick, tick_end: WaveTick, direction: str) -> \
            FibonacciWaveTree:
        df_part = self.df.loc[np.logical_and(self.df[CN.POSITION] >= tick_start.position,
                                             self.df[CN.POSITION] <= tick_end.position)]
        min_max_list = [tick for tick in self.tick_list if tick_start.position <= tick.position <= tick_end.position]
        wave_tree = FibonacciWaveTree(df_part, min_max_list, tick_end.position - tick_start.position, 3)
        wave_tree.parse_tree(direction)
        return wave_tree

    def _get_min_tick_list_for_end_point_(self, index_start: int, tick_start: WaveTick):
        min_value = math.inf
        list_return = []
        for k in self.get_tick_range(index_start):
            tick_k = self.tick_list[k]
            if tick_k.is_global_min and tick_k.low < min_value:
                list_return.append(tick_k)
                min_value = tick_k.low
            elif tick_k.is_max and tick_k.high > tick_start.high:
                break
        return list_return

    def _get_max_tick_list_for_end_point_(self, index_start: int, tick_start: WaveTick):
        max_value = -math.inf
        list_return = []
        for k in self.get_tick_range(index_start):
            tick_k = self.tick_list[k]
            if tick_k.is_global_max and tick_k.high > max_value:
                list_return.append(tick_k)
                max_value = tick_k.high
            elif tick_k.is_min and tick_k.low < tick_start.low:
                break
        return list_return


class PatternRangeDetectorFibonacciDesc(PatternRangeDetectorMin, PatternRangeDetectorFibonacciBase):
    def __init__(self, sys_config: SystemConfiguration):
        tick_list = sys_config.pdh.pattern_data_fibonacci.wave_tick_list_min_max.tick_list
        PatternRangeDetectorFibonacciBase.__init__(self, sys_config, tick_list)
        PatternRangeDetectorMin.__init__(self, sys_config, tick_list)

    @property
    def pattern_type(self):
        return FT.FIBONACCI_DESC

    def __parse_tick_list__(self):
        for entries in self.global_max_tuple_list:
            index_start, tick_start = entries[0], entries[1]
            tick_list_end = self._get_min_tick_list_for_end_point_(index_start, tick_start)
            for tick_end in tick_list_end:
                fibonacci_wave_tree = self.__get_fibonacci_wave_tree_for_formation__(tick_start, tick_end, FD.DESC)
                if len(fibonacci_wave_tree.fibonacci_wave_list) > 0:
                    fib_form = FibonacciFormation(self.pattern_type, tick_start, tick_end, fibonacci_wave_tree)
                    if fib_form.are_valid_waves_available:
                        pattern_range = self.get_pattern_range(fib_form)
                        if pattern_range is not None:
                            self.__add_pattern_range_to_list_after_check__(pattern_range)


class PatternRangeDetectorFibonacciAsc(PatternRangeDetectorMax, PatternRangeDetectorFibonacciBase):
    def __init__(self, sys_config: SystemConfiguration):
        tick_list = sys_config.pdh.pattern_data_fibonacci.wave_tick_list_min_max.tick_list
        PatternRangeDetectorFibonacciBase.__init__(self, sys_config, tick_list)
        PatternRangeDetectorMax.__init__(self, sys_config, tick_list)

    @property
    def pattern_type(self):
        return FT.FIBONACCI_ASC

    def __parse_tick_list__(self):
        for entries in self.global_min_tuple_list:
            index_start, tick_start = entries[0], entries[1]
            tick_list_end = self._get_max_tick_list_for_end_point_(index_start, tick_start)
            for tick_end in tick_list_end:
                fibonacci_wave_tree = self.__get_fibonacci_wave_tree_for_formation__(tick_start, tick_end, FD.ASC)
                if len(fibonacci_wave_tree.fibonacci_wave_list) > 0:
                    fib_form = FibonacciFormation(self.pattern_type, tick_start, tick_end, fibonacci_wave_tree)
                    if fib_form.are_valid_waves_available:
                        pattern_range = self.get_pattern_range(fib_form)
                        if pattern_range is not None:
                            self.__add_pattern_range_to_list_after_check__(pattern_range)
