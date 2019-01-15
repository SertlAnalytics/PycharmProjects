"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, FD, DC, BT, EQUITY_TYPE, EXTREMA, PRD
from sertl_analytics.mydates import MyDate
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_wave_tick import WaveTick
from pattern_part import PatternPart, PatternEntryPart, PatternWatchPart, PatternTradePart
from pattern import Pattern, PatternFactory
from pattern_range import PatternRangeDetectorMax, PatternRangeDetectorMin, PatternRangeDetectorHeadShoulder\
    , PatternRangeDetectorHeadShoulderBottom, PatternRange
from pattern_range_fibonacci import PatternRangeDetectorFibonacciAsc, PatternRangeDetectorFibonacciDesc
from pattern_breakout import PatternBreakoutApi, PatternBreakout
from pattern_statistics import PatternDetectorStatisticsApi
from fibonacci.fibonacci_wave_tree import FibonacciWaveTree
from pattern_constraints import ConstraintsFactory
from pattern_function_container import PatternFunctionContainerFactoryApi, PatternFunctionContainerFactory


class PatternDetector:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self.pdh = sys_config.pdh
        self.with_trade_part = True
        self.pattern_type_list = list(self.sys_config.config.pattern_type_list)
        self.df = self.pdh.pattern_data.df
        self.df_length = self.df.shape[0]
        self.df_min_max = self.pdh.pattern_data.df_min_max
        self.df_min_max_length = self.df_min_max.shape[0]
        self.range_detector_max = None
        self.range_detector_min = None
        self.range_detector_h_s = None  # Head_Shoulder
        self.range_detector_h_s_b = None  # Head_Shoulder_Bottom
        self.range_detector_fib_asc = None  # Fibonacci ascending
        self.range_detector_fib_desc = None  # Fibonacci descending
        self.pattern_list = []
        self.fib_wave_tree = None
        self.trade_handler = None
        self.data_dict = {}
        self._set_data_dict_()

    @property
    def possible_pattern_ranges_available(self):
        return self.range_detector_max.are_pattern_ranges_available \
               or self.range_detector_min.are_pattern_ranges_available

    def _set_data_dict_(self):
        self.data_dict[DC.EQUITY_TYPE] = self.sys_config.runtime_config.actual_ticker_equity_type
        self.data_dict[DC.EQUITY_TYPE_ID] = EQUITY_TYPE.get_id(self.data_dict[DC.EQUITY_TYPE])
        self.data_dict[DC.PERIOD] = self.sys_config.period
        self.data_dict[DC.PERIOD_ID] = PRD.get_id(self.sys_config.period)
        self.data_dict[DC.PERIOD_AGGREGATION] = self.sys_config.period_aggregation
        self.data_dict[DC.TICKER_ID] = self.sys_config.runtime_config.actual_ticker
        self.data_dict[DC.TICKER_NAME] = self.sys_config.runtime_config.actual_ticker_name

    def parse_for_pattern(self):
        possible_pattern_range_list_dict = self.__get_possible_pattern_range_list_dict__()
        for pattern_type in self.pattern_type_list:
            for pattern_range in possible_pattern_range_list_dict[pattern_type]:
                # print('parsing for pattern: {}'.format(pattern_type))
                self.__check_pattern_range_for_pattern_type__(pattern_type, pattern_range)

    def __get_possible_pattern_range_list_dict__(self) -> dict:
        self.__fill_possible_pattern_ranges__()
        self.__adjust_possible_pattern_ranges_to_constraints__()
        possible_pattern_range_list = self.__get_combined_possible_pattern_ranges__()
        return self.__get_pattern_range_list_dict__(possible_pattern_range_list)

    def __check_pattern_range_for_pattern_type__(self, pattern_type: str, pattern_range: PatternRange):
        self.sys_config.runtime_config.actual_pattern_type = pattern_type
        self.sys_config.runtime_config.actual_pattern_range = pattern_range

        pfcf_api = PatternFunctionContainerFactoryApi(self.sys_config, pattern_type)
        pfcf_api.pattern_type = pattern_type
        pfcf_api.pattern_range = pattern_range
        pfcf_api.constraints = ConstraintsFactory.get_constraints_by_pattern_type(pattern_type, self.sys_config)
        # pattern_range.print_range_details()
        debugger.check_range_position_list(pattern_range.position_list)
        complementary_function_list = pattern_range.get_complementary_function_list(pattern_type)
        for f_complementary in complementary_function_list:
            pfcf_api.complementary_function = f_complementary
            pfcf_api.function_container = PatternFunctionContainerFactory.get_function_container_by_api(pfcf_api)
            if pfcf_api.constraints.are_constraints_fulfilled(pfcf_api.pattern_range, pfcf_api.function_container):
                pattern = PatternFactory.get_pattern(self.sys_config, pfcf_api)
                if len(self.sys_config.config.pattern_ids_to_find) == 0 \
                        or pattern.id in self.sys_config.config.pattern_ids_to_find:
                    self.__handle_single_pattern_when_parsing__(pattern)

    def __adjust_possible_pattern_ranges_to_constraints__(self):
        pass

    def parse_for_fibonacci_waves(self):
        df = self.pdh.pattern_data_fibonacci.df
        min_max_tick_list = self.pdh.pattern_data_fibonacci.wave_tick_list_min_max.tick_list
        self.fib_wave_tree = FibonacciWaveTree(df, min_max_tick_list,
                                               self.sys_config.config.max_pattern_range_length,
                                               self.pdh.pattern_data.tick_f_var_distance, self.data_dict)
        self.fib_wave_tree.parse_tree()

    def check_for_intersections_and_endings(self):
        # fib_wave_list = self.fib_wave_tree.fibonacci_wave_forecast_collector.get_forecast_wave_list()
        fib_wave_list = self.fib_wave_tree.fibonacci_wave_list
        pattern_list_filtered = [pattern for pattern in self.pattern_list if pattern.was_breakout_done()]
        for pattern in pattern_list_filtered:
            pattern_start_pos = pattern.part_entry.tick_first.position
            pattern_end_pos = pattern.breakout.tick_breakout.position
            for fib_wave in fib_wave_list:
                fib_start_pos = fib_wave.position_start
                fib_end_pos = fib_wave.position_end
                if pattern_start_pos <= fib_start_pos <= pattern_end_pos or \
                        pattern_start_pos <= fib_end_pos <= pattern_end_pos or \
                        (fib_start_pos <= pattern_start_pos and fib_end_pos >= pattern_end_pos):
                    pattern.intersects_with_fibonacci_wave = True
                if pattern.available_fibonacci_end_type is None and pattern_start_pos <= fib_end_pos <= pattern_end_pos:
                    pattern.available_fibonacci_end_type = EXTREMA.MAX if fib_wave.wave_type == FD.ASC else EXTREMA.MIN

    def was_any_breakout_since_time_stamp(self, ts_since: float, print_id: str, for_print=False):
        for pattern in self.pattern_list:
            if pattern.was_breakout_done() and pattern.breakout.tick_breakout.time_stamp > ts_since:
                if for_print:
                    self.__print_breakout_details__(print_id, pattern.breakout.tick_breakout.time_stamp, ts_since)
                return True
        return False

    def was_any_touch_since_time_stamp(self, time_stamp_since: float, for_print=False):
        for pattern in self.pattern_list:
            if pattern.was_any_touch_since_time_stamp(time_stamp_since, for_print):
                return True
        return False

    def is_any_pattern_without_breakout(self) -> bool:
        for pattern in self.pattern_list:
            if not pattern.was_breakout_done():
                return True
        return False

    def was_massive_movement_since_last_tick(self) -> bool:
        symbol = self.sys_config.runtime_config.actual_ticker
        tick_previous = self.pdh.pattern_data.tick_list[-2]
        tick_last = self.pdh.pattern_data.tick_list[-1]
        if tick_previous.high == 0:  # ToDo - why can this happen?
            return False
        massive_movement_pct = self.sys_config.exchange_config.massive_breakout_pct
        movement_up_pct = (tick_last.high - tick_previous.high) / tick_previous.high * 100
        movement_down_pct = (tick_last.low - tick_previous.low) / tick_previous.low * 100
        if movement_up_pct > massive_movement_pct or movement_down_pct < -massive_movement_pct:
            print('Massive movement for {}: up={:.2f}%, down={:.2f}% (allowed - abs.: {:.2f})%'.format(
                symbol, movement_up_pct, movement_down_pct, massive_movement_pct))
            return True
        return False

    def get_pattern_list_for_buy_trigger(self, buy_trigger: str) -> list:
        pattern_list = []
        for pattern in self.pattern_list:
            if buy_trigger == BT.BREAKOUT and not pattern.is_part_trade_available():
                pattern_list.append(pattern)
            elif buy_trigger == BT.TOUCH_POINT and pattern.__are_conditions_for_a_touch_point_buy_fulfilled__():
                    pattern_list.append(pattern)
            elif buy_trigger == BT.FIBONACCI_CLUSTER:
                pass
        return pattern_list

    def get_pattern_list_for_back_testing(self) -> list:
        pattern_list = [pattern for pattern in self.pattern_list if pattern.is_ready_for_back_testing()]
        return pattern_list

    def get_pattern_for_replay(self) -> list:
        if len(self.pattern_list) == 0:
            return []
        return self.pattern_list[0]

    @staticmethod
    def __print_breakout_details__(print_id: str, breakout_ts: float, time_stamp_since: float):
        brk_t = MyDate.get_time_from_epoch_seconds(int(breakout_ts))
        data_t = MyDate.get_time_from_epoch_seconds(int(time_stamp_since))
        print('{}: breakout since last data update: breakout={}/{}=last_data_update'.format(print_id, brk_t, data_t))

    def __handle_single_pattern_when_parsing__(self, pattern: Pattern):
        if self.sys_config.config.with_trade_part:
            can_be_added = self.__can_pattern_be_added_to_list_after_checking_next_ticks__(pattern)
            if pattern.breakout is None and not can_be_added:
                return
        self.sys_config.runtime_config.actual_breakout = pattern.breakout
        pattern.add_part_entry(PatternEntryPart(self.sys_config, pattern.function_cont))
        pattern.add_data_dict_entries_after_part_entry()
        if pattern.are_pre_conditions_fulfilled():
            pattern.calculate_predictions_after_part_entry()
            if pattern.breakout is not None:
                pattern.function_cont.breakout_direction = pattern.breakout.breakout_direction
                self.__add_part_trade__(pattern)
            # pattern.print_nearest_neighbor_collection()
            # for nn_entry in pattern.nearest_neighbor_entry_list:
            #     pattern_id = self.pattern_id_factory.get_pattern_id_from_pattern_id_string(nn_entry.id)
            self.pattern_list.append(pattern)

    def __add_part_trade__(self, pattern: Pattern):
        if not pattern.was_breakout_done():
            return None
        df = self.__get_trade_df__(pattern)
        f_upper_trade = pattern.get_f_upper_trade()
        f_lower_trade = pattern.get_f_lower_trade()
        function_cont = PatternFunctionContainerFactory.get_function_container(
            self.sys_config, pattern.pattern_type, df, f_lower_trade, f_upper_trade)
        part = PatternTradePart(self.sys_config, function_cont)
        pattern.add_part_trade(part)
        pattern.fill_result_set()

    def __get_trade_df__(self, pattern: Pattern):
        left_pos = pattern.function_cont.tick_for_breakout.position
        if FT.is_pattern_type_any_fibonacci(pattern.pattern_type):
            right_pos_max = left_pos + pattern.function_cont.max_positions_after_tick_for_helper
        else:
            right_pos_max = left_pos + int(pattern.get_maximal_trade_position_size() / 2)
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
                pattern.set_breakout_after_checks(tick_last, next_tick)
            tick_last = next_tick
        pattern.function_cont.add_tick_from_main_df_to_df(self.df, tick_last)
        return can_pattern_be_added

    @staticmethod
    def __check_for_loop_break__(pattern: Pattern, counter: int, number_of_positions: int, tick: WaveTick) -> bool:
        if pattern.breakout is not None:
            return True
        if counter > number_of_positions:  # maximal number for the whole pattern (from start)
            return True
        if pattern.function_cont.is_tick_breakout_on_wrong_side(tick):
            return True
        if counter > pattern.breakout_required_after_ticks:
            return True
        if tick.f_var > pattern.function_cont.f_var_cross_f_upper_f_lower > 0:
            if not FT.is_pattern_type_any_fibonacci(pattern.pattern_type):
                return True
        # if not function_cont.is_regression_value_in_pattern_for_f_var(tick.f_var - 6):
        #     # check the last value !!! in some IMPORTANT cases is the breakout just on that day...
        #     return True
        if not pattern.function_cont.is_tick_inside_pattern_range(tick):
            return True
        return False

    def __fill_possible_pattern_ranges__(self):
        pattern_type_set = set(self.pattern_type_list)
        if len(pattern_type_set.intersection(set(FT.get_normal_types()))) > 0:
            self.range_detector_max = PatternRangeDetectorMax(self.sys_config)
            self.range_detector_min = PatternRangeDetectorMin(self.sys_config)
        if len(pattern_type_set.intersection(set(FT.get_head_shoulder_types()))) > 0:
            self.range_detector_h_s = PatternRangeDetectorHeadShoulder(self.sys_config)
        if len(pattern_type_set.intersection(set(FT.get_head_shoulder_bottom_types()))) > 0:
            self.range_detector_h_s_b = PatternRangeDetectorHeadShoulderBottom(self.sys_config)
        if FT.FIBONACCI_ASC in self.pattern_type_list:
            wave_list = [wave for wave in self.fib_wave_tree.fibonacci_wave_list if wave.wave_type == FD.ASC]
            self.range_detector_fib_asc = PatternRangeDetectorFibonacciAsc(self.sys_config, wave_list)
        if FT.FIBONACCI_DESC in self.pattern_type_list:
            wave_list = [wave for wave in self.fib_wave_tree.fibonacci_wave_list if wave.wave_type == FD.DESC]
            self.range_detector_fib_desc = PatternRangeDetectorFibonacciDesc(self.sys_config, wave_list)

    def __get_combined_possible_pattern_ranges__(self) -> list:
        list_max = [] if self.range_detector_max is None else self.range_detector_max.get_pattern_range_list()
        list_min = [] if self.range_detector_min is None else self.range_detector_min.get_pattern_range_list()
        list_h_s = [] if self.range_detector_h_s is None else self.range_detector_h_s.get_pattern_range_list()
        list_h_s_b = [] if self.range_detector_h_s_b is None else self.range_detector_h_s_b.get_pattern_range_list()
        list_f_asc = [] if self.range_detector_fib_asc is None else self.range_detector_fib_asc.get_pattern_range_list()
        list_f_desc = [] if self.range_detector_fib_desc is None else self.range_detector_fib_desc.get_pattern_range_list()
        list_max_without_covered = self.__remove_entries_covered_by_second_list__(list_max, list_min)
        list_min_without_covered = self.__remove_entries_covered_by_second_list__(list_min, list_max)
        result_list = list_max + list_min + list_h_s + list_h_s_b + list_f_asc + list_f_desc
        return result_list

    def __get_pattern_range_list_dict__(self, possible_pattern_range_list: list):
        return_dict = {}
        for pattern_type in self.pattern_type_list:
            return_dict[pattern_type] = []
            for pattern_range in possible_pattern_range_list:
                if pattern_range.covers_pattern_type(pattern_type):
                    return_dict[pattern_type].append(pattern_range)
        return return_dict

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

    def save_pattern_data(self):
        if not self.sys_config.config.save_pattern_data:
            return
        input_list = []
        for pattern in self.pattern_list:
            if pattern.is_pattern_ready_for_pattern_table():
                pattern_dict = pattern.data_dict_obj.get_data_dict_for_features_table()
                if pattern_dict is not None:
                    # print('save_pattern_data: {}'.format(feature_dict))
                    if self.sys_config.db_stock.is_pattern_already_available(pattern_dict[DC.ID]):
                        self.__print_difference_to_stored_version__(pattern_dict)
                    else:
                        input_list.append(pattern_dict)
        if len(input_list) > 0:
            self.sys_config.db_stock.insert_pattern_data(input_list)

    def save_wave_data(self):
        if not self.sys_config.config.save_wave_data:
            return
        input_list = []
        for fib_wave in self.fib_wave_tree.fibonacci_wave_list:
            if fib_wave.is_wave_ready_for_wave_table():
                data_dict = fib_wave.data_dict_obj.get_data_dict_for_target_table()
                if data_dict is not None:
                    self.sys_config.db_stock.delete_existing_wave(data_dict)
                    input_list.append(data_dict)
        if len(input_list) > 0:
            self.sys_config.db_stock.insert_wave_data(input_list)

    def __print_difference_to_stored_version__(self, feature_dict: dict):
        if not self.sys_config.config.show_differences_to_stored_features:
            return
        dict_diff = self.sys_config.db_stock.get_pattern_differences_to_saved_version(feature_dict)
        if len(dict_diff) > 0:
            print('Difference for Pattern {} [{}, {}]:'.format(
                feature_dict[DC.PATTERN_TYPE],
                feature_dict[DC.PATTERN_BEGIN_TIME] if self.sys_config.period == PRD.INTRADAY
                else feature_dict[DC.PATTERN_BEGIN_DT],
                feature_dict[DC.PATTERN_END_TIME] if self.sys_config.period == PRD.INTRADAY
                else feature_dict[DC.PATTERN_END_DT]
            ))
            for key, values in dict_diff.items():
                print('Different {}: old = {} <> {} = new'.format(key, values[0], values[1]))
            print('')
