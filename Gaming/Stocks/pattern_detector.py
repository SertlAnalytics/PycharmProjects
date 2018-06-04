"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_configuration import PatternConfiguration
from pattern_data_container import PatternDataContainer
from pattern_wave_tick import WaveTick
from pattern_function_container import PatternFunctionContainer
from pattern_part import PatternPart
from pattern import Pattern, PatternHelper
from pattern_range import PatternRangeDetectorMax, PatternRangeDetectorMin
from pattern_breakout import PatternBreakoutApi, PatternBreakout
from pattern_statistics import PatternDetectorStatisticsApi


class PatternDetector:
    def __init__(self, data_container: PatternDataContainer, config: PatternConfiguration):
        self.data_container = data_container
        self.config = config
        self.pattern_type_list = list(config.pattern_type_list)
        self.df = data_container.df
        self.df_length = self.df.shape[0]
        self.df_min_max = data_container.df_min_max
        self.df_min_max_length = self.df_min_max.shape[0]
        self.range_detector_max = None
        self.range_detector_min = None
        self.pattern_list = []

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
            self.config.runtime.actual_pattern_type = pattern_type
            for pattern_range in possible_pattern_range_list:
                # pattern_range.print_range_details()
                pattern = PatternHelper.get_pattern_for_pattern_type(pattern_type, self.df, self.df_min_max,
                                                                     pattern_range, self.config)
                if pattern.function_cont.is_valid():
                    self.__handle_single_pattern_when_parsing__(pattern)

    def __handle_single_pattern_when_parsing__(self, pattern: Pattern):
        can_be_added = self.__can_pattern_be_added_to_list_after_checking_next_ticks__(pattern)
        if pattern.breakout is None and not can_be_added:
            return
        self.config.runtime.actual_breakout = pattern.breakout
        pattern.add_part_main(PatternPart(self.data_container, pattern.function_cont, self.config))
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
        part = PatternPart(self.data_container, function_cont, self.config)
        pattern.add_part_trade(part)
        pattern.fill_result_set()

    def __get_trade_df__(self, pattern: Pattern):
        left_pos = pattern.function_cont.tick_for_helper.position
        right_pos = left_pos + pattern.pattern_range.get_maximal_trade_size_for_pattern_type(pattern.pattern_type)
        # right_pos += right_pos - left_pos  # double length
        return self.df.loc[left_pos:min(right_pos, self.df_length)]

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
            pattern.function_cont.adjust_functions_when_required(next_tick)
            if pattern.breakout is None:
                pattern.breakout = self.__get_confirmed_breakout__(pattern, tick_last, next_tick)
            tick_last = next_tick
        pattern.function_cont.add_tick_from_main_df_to_df(self.df, tick_last)
        return can_be_added

    @staticmethod
    def __check_for_break__(function_cont, counter: int, number_of_positions: int, tick: WaveTick) -> bool:
        if counter > number_of_positions:  # maximal number for the whole pattern after its building
            return True
        if not function_cont.is_regression_value_in_pattern_for_position(tick.position):
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
        breakout_api = PatternBreakoutApi(pattern.function_cont, self.config)
        breakout_api.tick_previous = tick_previous
        breakout_api.tick_breakout = tick_breakout
        breakout_api.constraints = pattern.constraints
        return PatternBreakout(breakout_api)

    def __fill_possible_pattern_ranges__(self):
        self.range_detector_max = PatternRangeDetectorMax(self.df_min_max, self.config.range_detector_tolerance_pct)
        # self.range_detector_max.print_list_of_possible_pattern_ranges()
        self.range_detector_min = PatternRangeDetectorMin(self.df_min_max, self.config.range_detector_tolerance_pct)
        # self.range_detector_min.print_list_of_possible_pattern_ranges()
        # TODO get rid of print statements

    def __get_combined_possible_pattern_ranges__(self) -> list:
        return self.range_detector_min.get_pattern_range_list()

    def print_statistics(self):
        api = self.get_statistics_api()
        print(
            'Investment change: {} -> {}, Diff: {}%'.format(api.investment_start, api.investment_working, api.diff_pct))
        print('counter_stop_loss = {}, counter_formation_OK = {}, counter_formation_NOK = {}, ticks = {}'.format(
            api.counter_stop_loss, api.counter_formation_OK, api.counter_formation_NOK, api.counter_actual_ticks
        ))

    def get_statistics_api(self):
        return PatternDetectorStatisticsApi(self.pattern_list, self.config.investment)
