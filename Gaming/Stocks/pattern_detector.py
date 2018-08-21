"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
from sertl_analytics.constants.pattern_constants import FT, FD, PFC, CN, SVC
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_configuration import ApiPeriod
from pattern_wave_tick import WaveTick
from pattern_part import PatternPart
from pattern import Pattern, PatternFactory
from pattern_range import PatternRangeDetectorMax, PatternRangeDetectorMin, PatternRangeDetectorHeadShoulder\
    , PatternRangeDetectorHeadShoulderBottom
from pattern_breakout import PatternBreakoutApi, PatternBreakout
from pattern_statistics import PatternDetectorStatisticsApi
from fibonacci.fibonacci_wave_tree import FibonacciWaveTree
from pattern_constraints import ConstraintsFactory
from pattern_function_container import PatternFunctionContainerFactoryApi, PatternFunctionContainerFactory
from pattern_data_frame import PatternDataFrame
from pattern_value_categorizer import ValueCategorizer
from sertl_analytics.mymath import MyMath


class PatternDetector:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self.pattern_type_list = list(self.sys_config.config.pattern_type_list)
        self.df = self.sys_config.pdh.pattern_data.df
        self.df_length = self.df.shape[0]
        self.df_min_max = self.sys_config.pdh.pattern_data.df_min_max
        self.df_min_max_length = self.df_min_max.shape[0]
        self.range_detector_max = None
        self.range_detector_min = None
        self.range_detector_h_s = None  # Head_Shoulder
        self.range_detector_h_s_b = None  # Head_Shoulder_Bottom
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
        possible_pattern_range_list = self.get_combined_possible_pattern_ranges()
        for pattern_type in self.pattern_type_list:
            # print('parsing for pattern: {}'.format(pattern_type))
            pfcf_api = PatternFunctionContainerFactoryApi(self.sys_config, pattern_type)
            pfcf_api.constraints = ConstraintsFactory.get_constraints_by_pattern_type(pattern_type)
            self.sys_config.runtime.actual_pattern_type = pattern_type
            for pattern_range in possible_pattern_range_list:
                if pattern_range.dedicated_pattern_type in [FT.ALL, pattern_type]:
                    pfcf_api.pattern_range = pattern_range
                    self.sys_config.runtime.actual_pattern_range = pattern_range
                    # pattern_range.print_range_details()
                    debugger.check_range_position_list(pattern_range.position_list)
                    complementary_function_list = pattern_range.get_complementary_function_list(pattern_type)
                    for f_complementary in complementary_function_list:
                        pfcf_api.complementary_function = f_complementary
                        pfcf_api.function_container = PatternFunctionContainerFactory.get_function_container_by_api(pfcf_api)
                        if pfcf_api.constraints.are_constraints_fulfilled(pattern_range, pfcf_api.function_container):
                            pattern = PatternFactory.get_pattern(self.sys_config, pfcf_api)
                            self.__handle_single_pattern_when_parsing__(pattern)

    def parse_for_fibonacci_waves(self):
        df = self.sys_config.pdh.pattern_data_fibonacci.df
        min_max_tick_list = self.sys_config.pdh.pattern_data_fibonacci.wave_tick_list_min_max.tick_list
        self.fib_wave_tree = FibonacciWaveTree(df, min_max_tick_list,
                                               self.sys_config.config.max_pattern_range_length,
                                               self.sys_config.pdh.pattern_data.tick_f_var_distance)
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
                    pattern.available_fibonacci_end = 2 if fib_waves.wave_type == FD.ASC else 1
                    break

    def __handle_single_pattern_when_parsing__(self, pattern: Pattern):
        can_be_added = self.__can_pattern_be_added_to_list_after_checking_next_ticks__(pattern)
        if pattern.breakout is None and not can_be_added:
            return
        self.sys_config.runtime.actual_breakout = pattern.breakout
        pattern.add_part_main(PatternPart(self.sys_config, pattern.function_cont))
        if pattern.is_formation_established() and pattern.is_expected_win_sufficient(
                self.sys_config.runtime.actual_expected_win_pct):
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
        function_cont = PatternFunctionContainerFactory.get_function_container(self.sys_config, pattern.pattern_type,
                                                                               df, f_lower_trade, f_upper_trade)
        part = PatternPart(self.sys_config, function_cont)
        pattern.add_part_trade(part)
        pattern.fill_result_set()

    def __get_trade_df__(self, pattern: Pattern):
        left_pos = pattern.function_cont.tick_for_breakout.position
        right_pos_max = left_pos + int(pattern.get_maximal_trade_position_size()/2)
        right_pos = min(right_pos_max, self.df_length)
        if right_pos - left_pos <= 1:
            left_pos += -2 + (right_pos - left_pos)  # we need at least 2 ticks for the trade_df...
        return self.df.loc[left_pos:right_pos]

    def __can_pattern_be_added_to_list_after_checking_next_ticks__(self, pattern: Pattern):
        tick_last = pattern.function_cont.tick_last
        pos_start = tick_last.position + 1
        number_of_positions = pattern.function_cont.number_of_positions
        counter = 0
        can_pattern_be_added = True
        for pos in range(pos_start, self.df_length):
            counter += 1
            next_tick = WaveTick(self.df.loc[pos])
            break_loop = self.__check_for_loop_break__(pattern, counter, number_of_positions, next_tick)
            if break_loop:
                can_pattern_be_added = False
                tick_last = next_tick
                break
            if pattern.breakout is None:
                pattern.function_cont.adjust_functions_when_required(next_tick)
                pattern.breakout = self.__get_confirmed_breakout__(pattern, tick_last, next_tick)
            tick_last = next_tick
        pattern.function_cont.add_tick_from_main_df_to_df(self.df, tick_last)
        return can_pattern_be_added

    @staticmethod
    def __check_for_loop_break__(pattern: Pattern, counter: int, number_of_positions: int, tick: WaveTick) -> bool:
        if counter > number_of_positions:  # maximal number for the whole pattern after its building
            return True
        if pattern.function_cont.is_tick_breakout_on_wrong_side(tick):
            return True
        if pattern.constraints.is_breakout_required_after_certain_ticks:
            if counter > pattern.breakout_required_after_ticks:
                return True
        if tick.f_var > pattern.function_cont.f_var_cross_f_upper_f_lower > 0:
            return True
        # if not function_cont.is_regression_value_in_pattern_for_f_var(tick.f_var - 6):
        #     # check the last value !!! in some IMPORTANT cases is the breakout just on that day...
        #     return True
        if not pattern.function_cont.is_tick_inside_pattern_range(tick):
            return True
        return False

    def __get_confirmed_breakout__(self, pattern: Pattern, last_tick: WaveTick, next_tick: WaveTick):
        if pattern.function_cont.is_tick_breakout(next_tick):
            breakout = self.__get_pattern_breakout__(pattern, last_tick, next_tick)
            if breakout.is_breakout_a_signal() or True:  # ToDo is_breakout a signal by ML algorithm
                pattern.function_cont.tick_for_breakout = next_tick
                return breakout
        return None

    @staticmethod
    def __get_pattern_breakout__(pattern: Pattern, tick_previous: WaveTick, tick_breakout: WaveTick) -> PatternBreakout:
        breakout_api = PatternBreakoutApi(pattern.function_cont)
        breakout_api.tick_previous = tick_previous
        breakout_api.tick_breakout = tick_breakout
        breakout_api.constraints = pattern.constraints
        return PatternBreakout(breakout_api)

    def __fill_possible_pattern_ranges__(self):
        if self.__is_any_non_head_shoulder_pattern_type_selected__():
            self.range_detector_max = PatternRangeDetectorMax(self.sys_config, self.sys_config.pdh.pattern_data.tick_list_max_without_hidden_ticks)
            self.range_detector_min = PatternRangeDetectorMin(self.sys_config, self.sys_config.pdh.pattern_data.tick_list_min_without_hidden_ticks)
        tick_list_head_shoulder = self.sys_config.pdh.pattern_data.tick_list_min_max_without_hidden_ticks
        if FT.HEAD_SHOULDER in self.pattern_type_list:
            self.range_detector_h_s = PatternRangeDetectorHeadShoulder(self.sys_config, tick_list_head_shoulder)
        if FT.HEAD_SHOULDER_BOTTOM in self.pattern_type_list:
            self.range_detector_h_s = PatternRangeDetectorHeadShoulderBottom(self.sys_config, tick_list_head_shoulder)

    def __is_any_non_head_shoulder_pattern_type_selected__(self):
        head_shoulder_set = {FT.HEAD_SHOULDER, FT.HEAD_SHOULDER_BOTTOM}
        pattern_type_set = set(self.pattern_type_list)
        intersection_pt_head_shoulder = pattern_type_set.intersection(head_shoulder_set)
        return False if len(intersection_pt_head_shoulder) == len(pattern_type_set) else True

    def get_combined_possible_pattern_ranges(self) -> list:
        list_max = [] if self.range_detector_max is None else self.range_detector_max.get_pattern_range_list()
        list_min = [] if self.range_detector_min is None else self.range_detector_min.get_pattern_range_list()
        list_h_s = [] if self.range_detector_h_s is None else self.range_detector_h_s.get_pattern_range_list()
        list_h_s_i = [] if self.range_detector_h_s_b is None else self.range_detector_h_s_b.get_pattern_range_list()
        list_max_without_covered = self.__remove_entries_covered_by_second_list__(list_max, list_min)
        list_min_without_covered = self.__remove_entries_covered_by_second_list__(list_min, list_max)
        result_list = list_max + list_min + list_h_s + list_h_s_i
        return result_list

    @staticmethod
    def __remove_entries_covered_by_second_list__(list_change: list, list_master: list) -> list:
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
        return PatternDetectorStatisticsApi(self.pattern_list, self.sys_config.config.investment)

    def _get_feature_dict_for_pattern_(self, pattern: Pattern):
        feature_dict = {}
        pattern_range = pattern.pattern_range
        tick_first = pattern.part_main.tick_first
        tick_last = pattern.part_main.tick_last
        tick_breakout = pattern.part_main.breakout.tick_breakout
        pos_breakout = tick_breakout.position
        pattern_length = pos_breakout - tick_first.position
        print('tick_first={}, tick_breakout={}, pattern_length={}'.format(tick_first.position, pos_breakout, pattern_length))
        if tick_first.position < pattern_length or self.df_length < pos_breakout + pattern_length:
            return None
        value_categorizer = self._get_value_categorizer_for_pattern_(pattern, tick_first.position, pos_breakout)
        slope_upper, slope_lower, slope_regression = pattern.part_main.get_slope_values()
        feature_dict[PFC.TICKER_ID] = self.sys_config.runtime.actual_ticker
        feature_dict[PFC.TICKER_NAME] = self.sys_config.runtime.actual_ticker_name
        feature_dict[PFC.PATTERN_TYPE] = pattern.pattern_type
        feature_dict[PFC.PATTERN_TYPE_ID] = FT.get_type_id(pattern.pattern_type)
        feature_dict[PFC.TS_PATTERN_TICK_FIRST] = tick_first.time_stamp
        feature_dict[PFC.TS_PATTERN_TICK_LAST] = tick_last.time_stamp
        feature_dict[PFC.TS_BREAKOUT] = tick_breakout.time_stamp
        feature_dict[PFC.TICKS_TILL_PATTERN_FORMED] = pattern_range.length
        feature_dict[PFC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT] = tick_breakout.position - pattern_range.position_last
        feature_dict[PFC.DT_BEGIN] = tick_first.date
        feature_dict[PFC.TIME_BEGIN] = tick_first.time_str
        feature_dict[PFC.DT_END] = tick_last.date
        feature_dict[PFC.TIME_END] = tick_last.time_str
        feature_dict[PFC.TOLERANCE_PCT] = pattern.tolerance_pct
        feature_dict[PFC.BREAKOUT_RANGE_MIN_PCT] = self.sys_config.config.breakout_range_pct
        feature_dict[PFC.BEGIN_HIGH] = round(pattern.function_cont.f_upper(tick_first.f_var), 2)
        feature_dict[PFC.BEGIN_LOW] = round(pattern.function_cont.f_lower(tick_first.f_var), 2)
        feature_dict[PFC.END_HIGH] = round(pattern.function_cont.f_upper(tick_breakout.f_var), 2)
        feature_dict[PFC.END_LOW] = round(pattern.function_cont.f_lower(tick_breakout.f_var), 2)
        feature_dict[PFC.SLOPE_UPPER] = slope_upper
        feature_dict[PFC.SLOPE_LOWER] = slope_lower
        feature_dict[PFC.SLOPE_REGRESSION] = slope_regression
        feature_dict[PFC.SLOPE_BREAKOUT] = self._get_slope_breakout_(pos_breakout)
        vc = [SVC.U_on, SVC.L_on] if self.sys_config.config.api_period == ApiPeriod.INTRADAY else [SVC.U_in, SVC.L_in]
        feature_dict[PFC.TOUCH_POINTS_TILL_BREAKOUT_HIGH] = value_categorizer.count_value_categories(vc[0])
        feature_dict[PFC.TOUCH_POINTS_TILL_BREAKOUT_LOW] = value_categorizer.count_value_categories(vc[1])
        feature_dict[PFC.BREAKOUT_DIRECTION] = pattern.part_main.breakout.sign  # 1 = ASC, else -1
        feature_dict[PFC.VOLUME_CHANGE_AT_BREAKOUT_PCT] = round((pattern.part_main.breakout.volume_change_pct - 1) * 100, 2)
        feature_dict[PFC.SLOPE_VOLUME_REGRESSION] = self._get_slope_breakout_(pos_breakout, CN.VOL)
        feature_dict[PFC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED] = 0

        min_max_values_dict = self._get_min_max_value_dict_(tick_first, tick_breakout, pattern_length, feature_dict)

        feature_dict[PFC.PREVIOUS_PERIOD_HALF_UPPER_PCT] = min_max_values_dict['max_previous_half'][0]
        feature_dict[PFC.PREVIOUS_PERIOD_FULL_UPPER_PCT] = min_max_values_dict['max_previous_full'][0]
        feature_dict[PFC.PREVIOUS_PERIOD_HALF_LOWER_PCT] = min_max_values_dict['min_previous_half'][0]
        feature_dict[PFC.PREVIOUS_PERIOD_FULL_LOWER_PCT] = min_max_values_dict['min_previous_full'][0]
        feature_dict[PFC.NEXT_PERIOD_HALF_POSITIVE_PCT] = min_max_values_dict['positive_next_half'][0]
        feature_dict[PFC.NEXT_PERIOD_FULL_POSITIVE_PCT] = min_max_values_dict['positive_next_full'][0]
        feature_dict[PFC.NEXT_PERIOD_HALF_NEGATIVE_PCT] = min_max_values_dict['negative_next_half'][0]
        feature_dict[PFC.NEXT_PERIOD_FULL_NEGATIVE_PCT] = min_max_values_dict['negative_next_full'][0]
        feature_dict[PFC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF] = min_max_values_dict['positive_next_half'][1] - pos_breakout
        feature_dict[PFC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL] = min_max_values_dict['positive_next_full'][1] - pos_breakout
        feature_dict[PFC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF] = min_max_values_dict['negative_next_half'][1] - pos_breakout
        feature_dict[PFC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL] = min_max_values_dict['negative_next_full'][1] - pos_breakout
        feature_dict[PFC.AVAILABLE_FIBONACCI_END] = pattern.available_fibonacci_end
        feature_dict[PFC.EXPECTED_WIN] = round(pattern.trade_result.expected_win, 2)
        feature_dict[PFC.FALSE_BREAKOUT] = 0
        feature_dict[PFC.EXPECTED_WIN_REACHED] = 0
        return feature_dict

    def save_pattern_features_to_database(self):
        for pattern in self.pattern_list:
            if pattern.is_part_trade_available():
                feature_dict = self._get_feature_dict_for_pattern_(pattern)
                if feature_dict is not None:
                    for key, value in feature_dict.items():
                        print('{}: {}'.format(key, value))

    def _get_slope_breakout_(self, pos_breakout: int, df_col: str = CN.CLOSE):
        distance = 2
        df_part = self.df.iloc[pos_breakout - distance:pos_breakout + distance + 1]
        tick_first = WaveTick(df_part.iloc[0])
        tick_last = WaveTick(df_part.iloc[-1])
        stock_df = PatternDataFrame(df_part)
        func = stock_df.get_f_regression(df_col)
        return MyMath.get_change_in_percentage(func(tick_first.f_var), func(tick_last.f_var), 1)

    def _get_min_max_value_dict_(self, tick_first: WaveTick, tick_last: WaveTick, pattern_length: int, feature_dict):
        height_begin = feature_dict[PFC.BEGIN_HIGH] - feature_dict[PFC.BEGIN_LOW]
        height_end = feature_dict[PFC.END_HIGH] - feature_dict[PFC.END_LOW]
        pattern_length_half = int(pattern_length / 2)
        pos_first = tick_first.position
        pos_last = tick_last.position
        pos_previous_full = pos_first - pattern_length
        pos_previous_half = pos_first - pattern_length_half
        pos_next_full = pos_last + pattern_length
        pos_next_half = pos_last + pattern_length_half
        value_dict = {}
        value_dict['max_previous_half'] = self._get_df_max_values_(pos_previous_half, pos_first,
                                                                   tick_first.high, height_begin)
        value_dict['max_previous_full'] = self._get_df_max_values_(pos_previous_full, pos_first,
                                                                   tick_first.high, height_begin)
        value_dict['min_previous_half'] = self._get_df_min_values_(pos_previous_half, pos_first,
                                                                   tick_first.low, height_begin)
        value_dict['min_previous_full'] = self._get_df_min_values_(pos_previous_full, pos_first,
                                                                   tick_first.low, height_begin)

        if feature_dict[PFC.BREAKOUT_DIRECTION] == 1:  # ASC
            value_dict['positive_next_half'] = self._get_df_max_values_(pos_last, pos_next_half,
                                                                        tick_last.high, height_end)
            value_dict['positive_next_full'] = self._get_df_max_values_(pos_last, pos_next_full,
                                                                        tick_last.high, height_end)
            value_dict['negative_next_half'] = self._get_df_min_values_(pos_last, pos_next_half,
                                                                        tick_last.high, height_end)
            value_dict['negative_next_full'] = self._get_df_min_values_(pos_last, pos_next_full,
                                                                        tick_last.high, height_end)
        else:
            value_dict['positive_next_half'] = self._get_df_min_values_(pos_last, pos_next_half,
                                                                        tick_last.low, height_end)
            value_dict['positive_next_full'] = self._get_df_min_values_(pos_last, pos_next_full,
                                                                   tick_last.low, height_end)
            value_dict['negative_next_half'] = self._get_df_max_values_(pos_last, pos_next_half,
                                                                        tick_last.low, height_end)
            value_dict['negative_next_full'] = self._get_df_max_values_(pos_last, pos_next_full,
                                                                        tick_last.low, height_end)
        return value_dict

    def _get_df_min_values_(self, pos_begin: int, pos_end: int, ref_value: float, comp_range: float):
        df_part = self.df.iloc[pos_begin:pos_end + 1]
        min_value = df_part[CN.LOW].min()
        min_index = df_part[CN.LOW].idxmin()
        pct = 0 if min_value > ref_value else round((ref_value - min_value) / comp_range * 100, 2)
        return pct, min_index, min_value

    def _get_df_max_values_(self, pos_begin: int, pos_end: int, ref_value: float, comp_range: float):
        df_part = self.df.iloc[pos_begin:pos_end + 1]
        max_value = df_part[CN.LOW].max()
        max_index = df_part[CN.LOW].idxmax()
        pct = 0 if max_value < ref_value else round((max_value - ref_value)/comp_range * 100, 2)
        return pct, max_index, max_value

    def _get_value_categorizer_for_pattern_(self, pattern: Pattern, pos_begin: int, pos_end: int):
        df_part = self.df_min_max.loc[np.logical_and(self.df_min_max[CN.POSITION] >= pos_begin,
                                                     self.df_min_max[CN.POSITION] <= pos_end)]
        f = pattern.function_cont
        return ValueCategorizer(df_part, f.f_upper, f.f_lower, f.h_upper, f.h_lower, pattern.tolerance_pct)
