"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
from pattern_configuration import config, runtime, debugger
from pattern_data_container import pattern_data_handler as pdh
from pattern_wave_tick import WaveTick
from pattern_function_container import PatternFunctionContainer
from pattern_part import PatternPart
from pattern import Pattern, PatternHelper
from pattern_range import PatternRangeDetectorMax, PatternRangeDetectorMin
from pattern_breakout import PatternBreakoutApi, PatternBreakout
from pattern_statistics import PatternDetectorStatisticsApi
from fibonacci.fibonacci_wave_tree import FibonacciWaveTree


class PatternDetector:
    def __init__(self):
        self.pattern_type_list = list(config.pattern_type_list)
        self.df = pdh.pattern_data.df
        self.df_length = self.df.shape[0]
        self.df_min_max = pdh.pattern_data.df_min_max
        self.df_min_max_length = self.df_min_max.shape[0]
        self.range_detector_max = None
        self.range_detector_min = None
        self.pattern_list = []
        self.fib_wave_tree = None

    @property
    def possible_pattern_ranges_available(self):
        return self.range_detector_max.are_pattern_ranges_available \
               or self.range_detector_min.are_pattern_ranges_available

    def parse_for_pattern(self):
        """
        We parse only over the actual known min-max-dataframe
        """
        self.__fill_possible_pattern_ranges__()
        possible_pattern_range_list = self.__get_combined_possible_pattern_ranges__()
        for pattern_type in self.pattern_type_list:
            runtime.actual_pattern_type = pattern_type
            for pattern_range in possible_pattern_range_list:
                runtime.actual_pattern_range = pattern_range
                # pattern_range.print_range_details()
                debugger.check_range_position_list(pattern_range.position_list)
                complementary_function_list = pattern_range.get_complementary_function_list(pattern_type)
                for f_comp in complementary_function_list:
                    pattern = PatternHelper.get_pattern_for_pattern_type(pattern_type, pattern_range, f_comp)
                    if pattern.function_cont.is_valid():
                        self.__handle_single_pattern_when_parsing__(pattern)

    def parse_for_fibonacci_waves(self):
        pdh.pattern_data.adjust_min_max_for_fibonacci()
        min_max_tick_list = pdh.pattern_data.wave_tick_list_min_max.tick_list
        self.fib_wave_tree = FibonacciWaveTree(pdh.pattern_data.df, min_max_tick_list, config.max_pattern_range_length)
        self.fib_wave_tree.parse_tree()

    def check_for_intersections(self):
        fib_wave_list = self.fib_wave_tree.fibonacci_wave_forecast_collector.get_forecast_wave_list()
        fib_wave_list = list(fib_wave_list + self.fib_wave_tree.fibonacci_wave_list)
        for pattern in self.pattern_list:
            start_pos = pattern.part_main.tick_first.position
            end_pos = pattern.part_main.tick_last.position
            pattern_position_set = set(range(start_pos, end_pos + 1))
            for fib_waves in fib_wave_list:
                start_pos = fib_waves.comp_position_list[0]
                end_pos = fib_waves.comp_position_list[-1]
                fib_waves_position_set = set(range(start_pos, end_pos + 1))
                intersection_set = pattern_position_set.intersection(fib_waves_position_set)
                if len(intersection_set) > 0:
                    pattern.intersects_with_fibonacci_wave = True
                    break

    def __handle_single_pattern_when_parsing__(self, pattern: Pattern):
        can_be_added = self.__can_pattern_be_added_to_list_after_checking_next_ticks__(pattern)
        if pattern.breakout is None and not can_be_added:
            return
        runtime.actual_breakout = pattern.breakout
        pattern.add_part_main(PatternPart(pattern.function_cont))
        if pattern.is_formation_established():
            if pattern.breakout is not None:
                pattern.function_cont.breakout_direction = pattern.breakout.breakout_direction
                self.__add_part_trade__(pattern)
            self.pattern_list.append(pattern)

    def __add_part_trade__(self, pattern: Pattern):
        if not pattern.was_breakout_done():
            return None
        df = self.__get_trade_df__(pattern)
        f_upper_trade = pattern.get_f_upper_trade()
        f_lower_trade = pattern.get_f_lower_trade()
        function_cont = PatternFunctionContainer(pattern.pattern_type, df, f_lower_trade, f_upper_trade)
        part = PatternPart(function_cont)
        pattern.add_part_trade(part)
        pattern.fill_result_set()

    def __get_trade_df__(self, pattern: Pattern):
        left_pos = pattern.function_cont.tick_for_helper.position
        right_pos_max = left_pos + pattern.get_maximal_trade_size()
        right_pos = min(right_pos_max, self.df_length)
        if right_pos - left_pos==1:
            left_pos += -1  # we need at least 2 ticks for the trade_df...
        return self.df.loc[left_pos:right_pos]

    def __can_pattern_be_added_to_list_after_checking_next_ticks__(self, pattern: Pattern):
        tick_last = pattern.function_cont.tick_last
        pos_start = tick_last.position + 1
        number_of_positions = pattern.function_cont.number_of_positions
        counter = 0
        can_be_added = True
        for pos in range(pos_start, self.df_length):
            counter += 1
            next_tick = WaveTick(self.df.loc[pos])
            break_loop = self.__check_for_break__(pattern.function_cont, counter, number_of_positions, next_tick)
            if break_loop:
                can_be_added = False
                tick_last = next_tick
                break
            if pattern.breakout is None:
                pattern.function_cont.adjust_functions_when_required(next_tick)
                pattern.breakout = self.__get_confirmed_breakout__(pattern, tick_last, next_tick)
            tick_last = next_tick
        pattern.function_cont.add_tick_from_main_df_to_df(self.df, tick_last)
        return can_be_added

    @staticmethod
    def __check_for_break__(function_cont, counter: int, number_of_positions: int, tick: WaveTick) -> bool:
        if counter > number_of_positions:  # maximal number for the whole pattern after its building
            return True
        if not function_cont.is_regression_value_in_pattern_for_f_var(tick.f_var - 6):
            # check the last value !!! in some IMPORTANT cases is the breakout just on that day...
            return True
        if not function_cont.is_tick_inside_pattern_range(tick):
            return True
        return False

    def __get_confirmed_breakout__(self, pattern: Pattern, last_tick: WaveTick, next_tick: WaveTick):
        if pattern.function_cont.is_tick_breakout(next_tick):
            breakout = self.__get_pattern_breakout__(pattern, last_tick, next_tick)
            if breakout.is_breakout_a_signal():
                pattern.function_cont.set_tick_for_breakout(next_tick)
                return breakout
        return None

    def __get_pattern_breakout__(self, pattern: Pattern, tick_previous: WaveTick, tick_breakout: WaveTick) \
            -> PatternBreakout:
        breakout_api = PatternBreakoutApi(pattern.function_cont)
        breakout_api.tick_previous = tick_previous
        breakout_api.tick_breakout = tick_breakout
        breakout_api.constraints = pattern.constraints
        return PatternBreakout(breakout_api)

    def __fill_possible_pattern_ranges__(self):
        self.range_detector_max = PatternRangeDetectorMax(pdh.pattern_data.tick_list_max_without_hidden_ticks)
        self.range_detector_min = PatternRangeDetectorMin(pdh.pattern_data.tick_list_min_without_hidden_ticks)

    def __get_combined_possible_pattern_ranges__(self) -> list:
        # return self.range_detector_min.get_pattern_range_list()
        list_max = self.range_detector_max.get_pattern_range_list()
        list_min = self.range_detector_min.get_pattern_range_list()
        list_max_without_covered = self.__remove_entries_covered_by_second_list__(list_max, list_min)
        list_min_without_covered = self.__remove_entries_covered_by_second_list__(list_min, list_max)
        result_list = list_max + list_min
        return result_list

    def __remove_entries_covered_by_second_list__(self, list_change: list, list_master: list) -> list:
        result_list = []
        for pattern_range_change in list_change:
            covered = False
            range_change = range(pattern_range_change.position_first, pattern_range_change.position_last)
            for pattern_range_master in list_master:
                range_master = range(pattern_range_master.position_first, pattern_range_master.position_last)
                intersection = set(range_change).intersection(range_master)
                if len(intersection) > max(len(range_change),len(range_master))/2 \
                        and len(range_change) < len(range_master):
                    covered = True
                    break
            if not covered:
                result_list.append(pattern_range_change)
        return result_list

    def print_statistics(self):
        api = self.get_statistics_api()
        print(
            'Investment change: {} -> {}, Diff: {}%'.format(api.investment_start, api.investment_working, api.diff_pct))
        print('counter_stop_loss = {}, counter_formation_OK = {}, counter_formation_NOK = {}, ticks = {}'.format(
            api.counter_stop_loss, api.counter_formation_OK, api.counter_formation_NOK, api.counter_actual_ticks
        ))

    def get_statistics_api(self):
        return PatternDetectorStatisticsApi(self.pattern_list, config.investment)
