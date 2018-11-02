"""
Description: This module contains the PatternRange class - central for stock data management
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import CN, FT
from sertl_analytics.plotter.my_plot import MyPlotHelper
from pattern_wave_tick import WaveTick, WaveTickList
from pattern_data_frame import PatternDataFrame
from sertl_analytics.mymath import ToleranceCalculator
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_data_container import PatternDataHandler
import math
import pandas as pd
import numpy as np


class PatternRange:
    def __init__(self, sys_config: SystemConfiguration, tick: WaveTick, min_length: int):
        self.sys_config = sys_config
        self.pdh = self.sys_config.pdh
        self.df_min_max_final = None
        self.tick_list = [tick]
        self.tick_first = tick
        self.tick_last = None
        self.tick_breakout_successor = None
        self._min_length = min_length
        self._f_param = None
        self._f_param_parallel = None  # parallel function through low or high
        self._f_param_const = None  # constant through low or high
        self._f_param_list = []  # contains the possible f_params of the opposite side
        self._covered_pattern_types = self._get_covered_pattern_types_()

    @property
    def id(self) -> str:
        return '{}_{}_{}_{}'.format(self.tick_first.date_str, self.tick_first.time_str,
                                    self.tick_last.date_str, self.tick_last.time_str)

    @property
    def f_param(self) -> np.poly1d:
        return self._f_param

    @property
    def f_param_const(self) -> np.poly1d:
        return self._f_param_const

    @property
    def f_param_parallel(self) -> np.poly1d:
        return self._f_param_parallel

    @property
    def range_elements(self) -> int:
        return len(self.tick_list)

    @property
    def volume_mean(self):
        return np.mean([tick.volume for tick in self.tick_list])

    @property
    def length(self) -> int:
        return self.tick_last.position - self.tick_first.position

    @property
    def position_first(self) -> int:
        return self.tick_first.position

    @property
    def position_last(self) -> int:
        return self.tick_last.position

    @property
    def f_regression(self) -> np.poly1d:
        stock_df = PatternDataFrame(self.__get_actual_df_min_max__())
        return stock_df.get_f_regression()

    @property
    def is_minimum_pattern_range(self) -> bool:
        return False  # is overwritten

    def covers_pattern_type(self, pattern_type: str) -> bool:  # for head shoulder we have dedicated classes
        return pattern_type in self._covered_pattern_types

    @staticmethod
    def _get_covered_pattern_types_() -> list:
        return FT.get_normal_types()

    def __get_actual_df_min_max__(self):
        if self.tick_breakout_successor is None:
            df_range = self.pdh.pattern_data.df_min_max[np.logical_and(
                self.pdh.pattern_data.df_min_max[CN.POSITION] >= self.tick_first.position,
                self.pdh.pattern_data.df_min_max[CN.POSITION] <= self.tick_last.position)]
        else:
            df_range = self.pdh.pattern_data.df_min_max[np.logical_and(
                self.pdh.pattern_data.df_min_max[CN.POSITION] >= self.tick_first.position,
                self.pdh.pattern_data.df_min_max[CN.POSITION] <= self.tick_breakout_successor.position)]
        return df_range

    @property
    def position_list(self) -> list:
        return self.__get_position_list__()

    def add_tick(self, tick: WaveTick, f_param):
        self.tick_list.append(tick)
        self.tick_last = tick
        self._f_param = f_param

    def finalize_pattern_range(self):
        self.df_min_max_final = self.__get_actual_df_min_max__()
        self.__fill_f_param_list__()
        self._f_param_parallel = self.__get_parallel_function__()
        self._f_param_const = self.__get_const_function__()

    def get_complementary_function_list(self, pattern_type: str) -> list:
        if FT.is_pattern_type_any_head_shoulder(pattern_type):
            return [self.f_param_parallel]
        elif pattern_type in [FT.TKE_BOTTOM, FT.TKE_TOP]:
            return [self.f_param_const]
        else:
            return [] if self._f_param_list is None else self._f_param_list

    def get_related_part_from_data_frame(self, df: pd.DataFrame):
        return df.loc[self.position_first:self.position_last]

    def __fill_f_param_list__(self):
        pass

    def __get_parallel_function__(self) -> np.poly1d:
        pass

    def __get_const_function__(self) -> np.poly1d:
        pass

    def __get_tick_list_for_param_list__(self) -> WaveTickList:
        pass

    @property
    def is_min_length_reached(self) -> bool:
        return self.range_elements >= self._min_length

    def is_covering_all_positions(self, pos_list_input: list) -> bool:
        return len(set(pos_list_input) & set(self.__get_position_list__())) == len(pos_list_input)

    def print_range_details(self):
        print(self.get_range_details())

    def get_range_details(self):
        position_list = self.__get_position_list__()
        value_list = self.__get_value_list__()
        breakout_successor = self.__get_breakout_details__()
        date_str_list = self.__get_date_str_list__()
        return [position_list, value_list, breakout_successor, date_str_list]

    def are_values_in_function_tolerance_range(self, f_param: np.poly1d, tolerance_pct: float) -> bool:
        for ticks in self.tick_list:
            v_1 = self.__get_value__(ticks)
            v_2 = f_param(ticks.f_var)
            if not ToleranceCalculator.are_values_in_tolerance_range(v_1, v_2, tolerance_pct):
                return False
        return True

    @property
    def xy_f_param(self) -> list:
        tick_list = [self.tick_first, self.tick_last]
        return MyPlotHelper.get_xy_for_tick_list_and_function(tick_list, self._f_param)

    @property
    def xy_f_param_list(self) -> list:
        tick_list = [self.tick_first, self.tick_last]
        return [MyPlotHelper.get_xy_for_tick_list_and_function(tick_list, f_param) for f_param in self._f_param_list]

    def __get_position_list__(self) -> list:
        return [tick.position for tick in self.tick_list]

    def __get_value_list__(self) -> list:
        return [self.__get_value__(tick) for tick in self.tick_list]

    def __get_date_str_list__(self) -> list:
        return [tick.date_str for tick in self.tick_list]

    def __get_breakout_details__(self):
        if self.tick_breakout_successor is None:  # extend the breakouts until the end....
            pos = self.pdh.pattern_data.df_min_max.iloc[-1][CN.POSITION]
        else:
            pos = self.tick_breakout_successor.position
        return [pos, round(self._f_param(pos), 2)]

    @staticmethod
    def __get_value__(tick: WaveTick):
        return tick.high


class PatternRangeMax(PatternRange):
    @property
    def is_minimum_pattern_range(self) -> bool:
        return False

    @staticmethod
    def __get_value__(tick: WaveTick):
        return tick.high

    def __fill_f_param_list__(self):
        wave_tick_list = WaveTickList(self.df_min_max_final[self.df_min_max_final[CN.IS_MIN]])
        self._f_param_list = wave_tick_list.get_boundary_f_param_list(self.f_param, False)

    def __get_parallel_function__(self) -> np.poly1d:
        stock_df = PatternDataFrame(self.df_min_max_final)
        return stock_df.get_parallel_to_function_by_low(self.f_param)

    def __get_const_function__(self) -> np.poly1d:
        return np.poly1d([0, self.df_min_max_final[CN.LOW].min()])


class PatternRangeMin(PatternRange):
    @property
    def is_minimum_pattern_range(self) -> bool:
        return True

    @staticmethod
    def __get_value__(tick: WaveTick):
        return tick.low

    def __fill_f_param_list__(self):
        wave_tick_list = WaveTickList(self.df_min_max_final[self.df_min_max_final[CN.IS_MAX]])
        self._f_param_list = wave_tick_list.get_boundary_f_param_list(self.f_param, True)

    def __get_parallel_function__(self) -> np.poly1d:
        stock_df = PatternDataFrame(self.df_min_max_final)
        return stock_df.get_parallel_to_function_by_high(self.f_param)

    def __get_const_function__(self) -> np.poly1d:
        return np.poly1d([0, self.df_min_max_final[CN.HIGH].max()])


class HeadShoulderFormation:
    def __init__(self, pattern_type: str, tick_neckline_left: WaveTick, tick_head: WaveTick,
                 tick_neckline_right: WaveTick):
        self.pattern_type = pattern_type
        self.tick_previous_breakout = None
        self.tick_shoulder_left = None
        self.tick_neckline_left = tick_neckline_left
        self.tick_head = tick_head
        self.tick_neckline_right = tick_neckline_right
        self.tick_shoulder_right = None
        self.f_neckline_param = None

    @property
    def distance_start_to_tick_left_neckline(self) -> int:
        return int(self.tick_neckline_left.position - self.tick_previous_breakout.position)

    @property
    def distance_neckline(self) -> int:
        return int(self.tick_neckline_right.position - self.tick_neckline_left.position)

    @property
    def expected_win(self):  # distance from neckline to first shoulder
        return self.value_distance_from_neckline_to_left_shoulder

    @property
    def value_distance_from_neckline_to_left_shoulder(self) -> float:  # distance from neckline to first shoulder
        if self.pattern_type == FT.HEAD_SHOULDER:
            return self.tick_shoulder_left.high - self.tick_neckline_left.low
        else:
            return self.tick_neckline_left.high - self.tick_shoulder_left.low

    @property
    def height(self):  # distance from neckline to head
        if self.pattern_type == FT.HEAD_SHOULDER:
            return self.tick_head.high - self.tick_neckline_left.low
        else:
            return self.tick_neckline_left.high - self.tick_head.low

    def is_left_shoulder_height_compliant(self) -> bool:
        required_relation = 0.2
        return self.value_distance_from_neckline_to_left_shoulder/self.height > required_relation

    def is_neckline_distance_compliant(self) -> bool:
        allowed_relation = 2.5
        distance_left = self.tick_head.position - self.tick_neckline_left.position
        distance_right = self.tick_neckline_right.position - self.tick_head.position
        relation = round(distance_left/distance_right, 2)
        return_value = 1/allowed_relation < relation < allowed_relation
        return return_value

    def is_previous_breakout_distance_compliant(self) -> bool:
        allowed_relation = 1
        distance_to_previous_breakout = self.tick_neckline_left.position - self.tick_previous_breakout.position
        relation = round(distance_to_previous_breakout/self.distance_neckline, 2)
        return relation < allowed_relation

    def is_neckline_not_too_large(self, df_length: int) -> bool:
        allowed_relation = 0.3
        relation = round(self.distance_neckline/df_length, 2)
        return relation <= allowed_relation


class PatternRangeHeadShoulder(PatternRangeMin):
    def __init__(self, sys_config: SystemConfiguration, hsf: HeadShoulderFormation, min_length: int):
        self.hsf = hsf
        PatternRangeMin.__init__(self, sys_config, hsf.tick_previous_breakout, min_length)

    @staticmethod
    def _get_covered_pattern_types_() -> list:
        return FT.get_head_shoulder_types()


class PatternRangeHeadShoulderBottom(PatternRangeMax):
    def __init__(self, sys_config: SystemConfiguration, hsf: HeadShoulderFormation, min_length: int):
        self.hsf = hsf
        PatternRangeMax.__init__(self, sys_config, hsf.tick_previous_breakout, min_length)

    @staticmethod
    def _get_covered_pattern_types_() -> list:
        return FT.get_head_shoulder_bottom_types()


class PatternRangeDetector:
    def __init__(self, sys_config: SystemConfiguration, tick_list: list):
        self.sys_config = sys_config
        self.pdh = self.sys_config.pdh
        self.tick_list = tick_list
        self._elements = len(self.tick_list)
        self._tolerance_pct = self.sys_config.get_value_categorizer_tolerance_pct()
        self._max_pattern_range_length = self.sys_config.config.max_pattern_range_length
        self._pattern_range_list = []
        self.__parse_tick_list__()

    @property
    def number_required_ticks(self) -> int:
        return 3

    def get_pattern_range_list(self) -> list:
        return self._pattern_range_list

    def get_pattern_range_shape_list(self) -> list:
        return [p.f_param_shape for p in self._pattern_range_list]

    def print_list_of_possible_pattern_ranges(self):
        print('List for {}:'.format(self.__class__.__name__))
        for pattern_range in self._pattern_range_list:
            pattern_range.print_range_details()

    def are_pattern_ranges_available(self) -> bool:
        return len(self._pattern_range_list) > 0

    def __add_pattern_range_to_list_after_check__(self, pattern_range: PatternRange):
        if self.__are_conditions_fulfilled_for_adding_to_pattern_range_list__(pattern_range):
            pattern_range.finalize_pattern_range()
            self._pattern_range_list.append(pattern_range)

    def __are_conditions_fulfilled_for_adding_to_pattern_range_list__(self, pattern_range: PatternRange) -> bool:
        if pattern_range is None:
            return False
        if not pattern_range.is_min_length_reached:
            return False
        # check if this list is already a sublist of an earlier list
        for pattern_range_old in self._pattern_range_list:
            if pattern_range_old.is_covering_all_positions(pattern_range.position_list):
                return False
        return True

    def __parse_tick_list__(self):
        range_start, range_end = self.__get_tick_list_start_end_for_parsing__()
        for i in range(range_start, range_end):
            tick_i = self.tick_list[i]
            pattern_range = self.__get_pattern_range_by_tick__(tick_i)
            next_list, next_linear_f_params, pos_list = self.__get_pattern_range_next_position_candidates__(i, tick_i)
            if len(next_list) < 2:
                continue
            for k in range(0, len(next_list)):
                tick_k = self.tick_list[next_list[k]]
                f_param_i_k = next_linear_f_params[k]
                if pattern_range.range_elements == 1:
                    pattern_range.add_tick(tick_k, None)
                elif self.__is_end_for_single_check_reached__(pattern_range, tick_i, tick_k, f_param_i_k):
                    pattern_range.tick_breakout_successor = tick_k
                    self.__add_pattern_range_to_list_after_check__(pattern_range)
                    pattern_range = self.__get_pattern_range_by_tick__(tick_i)
                    pattern_range.add_tick(tick_k, None)
            self.__add_pattern_range_to_list_after_check__(pattern_range)  # for the latest...

    def __get_tick_list_start_end_for_parsing__(self):
        ts_start = self.sys_config.runtime_config.actual_pattern_range_from_time_stamp
        if ts_start > 0:  # we have to find a dedicated ranges for a specific pattern
            li = [index for index, tick in enumerate(self.tick_list) if tick.time_stamp == ts_start]
            if len(li) == 0:
                return -1, 0  # we don't want to loop in the next step
            return li[0], li[0] + 1
        else:
            return 0, self._elements - self.number_required_ticks + 1

    def __get_pattern_range_next_position_candidates__(self, i: int, tick_i: WaveTick):
        f_param = None
        next_position_candidates_list = []
        next_position_list = []
        next_position_linear_f_params = []
        range_end = self.__get_next_position_candidates_range_end__()
        for k in range(i + 1, range_end):
            tick_k = self.tick_list[k]
            if tick_k.position - tick_i.position > self._max_pattern_range_length:
                break
            f_param_i_k = self.__get_linear_f_params__(tick_i, tick_k)
            # ToDo next position not too close - wyh is this possible? The max-min have some distance by construction...
            last_added_position = next_position_list[-1] if len(next_position_list) > 0 else 0
            next_tick_too_close = tick_k.position - last_added_position < 3
            if not next_tick_too_close:
                if f_param is None or self.__is_slope_correctly_changing__(f_param, tick_k, f_param_i_k):
                    f_param = f_param_i_k
                    next_position_candidates_list.append(k)
                    next_position_linear_f_params.append(f_param)
                    next_position_list.append(tick_k.position)
                else:
                    last_tick = self.tick_list[next_position_candidates_list[-1]]
                    last_tick_f_param = next_position_linear_f_params[-1]
                    # if self.__is_last_tick_in_tolerance_range__(last_tick, f_param_i_k):
                    if self.__is_next_tick_in_tolerance_range__(tick_k, last_tick_f_param):
                        next_position_candidates_list.append(k)
                        next_position_linear_f_params.append(f_param)
                        next_position_list.append(tick_k.position)
        return next_position_candidates_list, next_position_linear_f_params, next_position_list

    def __get_next_position_candidates_range_end__(self):
        ts_end = self.sys_config.runtime_config.actual_pattern_range_to_time_stamp
        if ts_end > 0:  # we have to find a dedicated ranges for a specific pattern
            li = [index for index, tick in enumerate(self.tick_list) if tick.time_stamp == ts_end]
            if len(li) == 0:
                return -1  # we don't want to loop in the next step
            return li[0] + 1
        else:
            return self._elements

    def __is_slope_correctly_changing__(self, f_param: np.poly1d, tick_new: WaveTick, f_param_new_tick: np.poly1d):
        pass

    def __is_last_tick_in_tolerance_range__(self, tick_last: WaveTick, f_param_new_tick: np.poly1d):
        pass

    def __is_next_tick_in_tolerance_range__(self, tick_next: WaveTick, f_param_last_tick: np.poly1d):
        pass

    def __get_linear_f_params__(self, tick_i: WaveTick, tick_k: WaveTick) -> np.poly1d:
        pass

    def __is_end_for_single_check_reached__(self, pattern_range: PatternRange, tick_i: WaveTick,
                                            tick_k: WaveTick, f_param_new: np.poly1d):
        if pattern_range.are_values_in_function_tolerance_range(f_param_new, self._tolerance_pct):
            pattern_range.add_tick(tick_k, f_param_new)
        else:
            f_value_new_last_position_right = f_param_new(pattern_range.tick_last.f_var)
            if self.__is_new_tick_a_breakout__(pattern_range, f_value_new_last_position_right):
                return True
        return False

    def __is_new_tick_a_breakout__(self, pattern_range: PatternRange, f_value_new_last_position_right: float):
        pass

    def __get_pattern_range_by_tick__(self, tick: WaveTick) -> PatternRange:
        pass


class PatternRangeDetectorMax(PatternRangeDetector):
    def __init__(self, sys_config: SystemConfiguration, tick_list=None):
        if tick_list is None:
            tick_list = sys_config.pdh.pattern_data.tick_list_max_without_hidden_ticks
        PatternRangeDetector.__init__(self, sys_config, tick_list)

    def __get_linear_f_params__(self, tick_i: WaveTick, tick_k: WaveTick) -> np.poly1d:
        return tick_i.get_linear_f_params_for_high(tick_k)

    def __is_new_tick_a_breakout__(self, pattern_range: PatternRange, f_value_new_last_position_right: float):
        return pattern_range.tick_last.high < f_value_new_last_position_right

    def __get_pattern_range_by_tick__(self, tick: WaveTick) -> PatternRangeMax:
        return PatternRangeMax(self.sys_config, tick, self.number_required_ticks)

    def __is_slope_correctly_changing__(self, f_param: np.poly1d, tick_new: WaveTick, f_param_new_tick: np.poly1d):
        return True if f_param_new_tick[1] > f_param[1] else False

    def __is_last_tick_in_tolerance_range__(self, tick_last: WaveTick, f_param_new_tick: np.poly1d):
        v_1 = tick_last.high
        v_2 = f_param_new_tick(tick_last.f_var)
        return ToleranceCalculator.are_values_in_tolerance_range(v_1, v_2, self._tolerance_pct)

    def __is_next_tick_in_tolerance_range__(self, tick_next: WaveTick, f_param_last_tick: np.poly1d):
        v_1 = tick_next.high
        v_2 = f_param_last_tick(tick_next.f_var)
        return ToleranceCalculator.are_values_in_tolerance_range(v_1, v_2, self._tolerance_pct)


class PatternRangeDetectorMin(PatternRangeDetector):
    def __init__(self, sys_config: SystemConfiguration, tick_list=None):
        if tick_list is None:
            tick_list = sys_config.pdh.pattern_data.tick_list_min_without_hidden_ticks
        PatternRangeDetector.__init__(self, sys_config, tick_list)

    def __get_linear_f_params__(self, tick_i: WaveTick, tick_k: WaveTick) -> np.poly1d:
        return tick_i.get_linear_f_params_for_low(tick_k)

    def __is_new_tick_a_breakout__(self, pattern_range: PatternRange, f_value_new_last_position_right: float):
        return pattern_range.tick_last.low > f_value_new_last_position_right

    def __get_pattern_range_by_tick__(self, tick: WaveTick) -> PatternRangeMin:
        return PatternRangeMin(self.sys_config, tick, self.number_required_ticks)

    def __is_slope_correctly_changing__(self, f_param: np.poly1d, tick_new: WaveTick, f_param_new_tick: np.poly1d):
        return True if f_param_new_tick[1] < f_param[1] else False

    def __is_last_tick_in_tolerance_range__(self, tick_last: WaveTick, f_param_new_tick: np.poly1d):
        v_1 = tick_last.low
        v_2 = f_param_new_tick(tick_last.f_var)
        return ToleranceCalculator.are_values_in_tolerance_range(v_1, v_2, self._tolerance_pct)

    def __is_next_tick_in_tolerance_range__(self, tick_next: WaveTick, f_param_last_tick: np.poly1d):
        v_1 = tick_next.low
        v_2 = f_param_last_tick(tick_next.f_var)
        return ToleranceCalculator.are_values_in_tolerance_range(v_1, v_2, self._tolerance_pct)


class PatternRangeDetectorHeadShoulderBase:
    def __init__(self, sys_config: SystemConfiguration, tick_list: list):
        self.sys_config = sys_config
        self.pdh = self.sys_config.pdh
        self.tick_list = tick_list
        self.global_max_tuple_list = [(i, tick) for i, tick in enumerate(self.tick_list) if tick.is_global_max]
        self.global_min_tuple_list = [(i, tick) for i, tick in enumerate(self.tick_list) if tick.is_global_min]

    def get_pattern_range(self, number_required_ticks: int, hsf: HeadShoulderFormation):
        if not hsf.is_neckline_not_too_large(self.pdh.pattern_data.df_length):
            return None
        hsf.tick_previous_breakout = self.pdh.pattern_data.get_previous_breakout_for_pattern_type(
            hsf.f_neckline_param, hsf.tick_neckline_left, hsf.tick_neckline_right, hsf.pattern_type)
        if hsf.tick_previous_breakout is None:
            return None
        if not hsf.is_previous_breakout_distance_compliant():
            return None

        hsf.tick_shoulder_left = self._get_shoulder_tick_(hsf, True)
        hsf.tick_shoulder_right = self._get_shoulder_tick_(hsf, False)
        if hsf.tick_shoulder_left is None or hsf.tick_shoulder_right is None:
            return None

        if not hsf.is_left_shoulder_height_compliant():
            return None

        if hsf.pattern_type == FT.HEAD_SHOULDER:
            pattern_range = PatternRangeHeadShoulder(self.sys_config, hsf, number_required_ticks)
        else:
            pattern_range = PatternRangeHeadShoulderBottom(self.sys_config, hsf, number_required_ticks)

        pattern_range.add_tick(hsf.tick_shoulder_left, hsf.f_neckline_param)
        pattern_range.add_tick(hsf.tick_neckline_left, hsf.f_neckline_param)
        pattern_range.add_tick(hsf.tick_head, hsf.f_neckline_param)
        pattern_range.add_tick(hsf.tick_neckline_right, hsf.f_neckline_param)
        pattern_range.add_tick(hsf.tick_shoulder_right, hsf.f_neckline_param)
        return pattern_range

    def get_tick_range(self, set_off: int, for_left: bool):
        return range(set_off - 1, 0, -1) if for_left else range(set_off + 1, len(self.tick_list)-1)

    def _get_shoulder_tick_(self, hsf: HeadShoulderFormation, for_left: bool):
        compare_value = - math.inf if hsf.pattern_type == FT.HEAD_SHOULDER else math.inf
        tick_return = None

        if for_left:
            tick_position_start = hsf.tick_previous_breakout.position
            tick_position_end = hsf.tick_neckline_left.position
        else:
            tick_position_start = hsf.tick_neckline_right.position
            tick_position_end = hsf.tick_neckline_right.position + hsf.distance_neckline

        for tick in self.tick_list:
            if tick.position > tick_position_start:
                if tick.position < tick_position_end:
                    # check for exit if a tick is outside the pattern
                    if hsf.pattern_type == FT.HEAD_SHOULDER:
                        if tick.high > hsf.tick_head.high:
                            return None
                        elif not for_left and tick.low < hsf.tick_neckline_left.low:
                            return tick_return
                    elif hsf.pattern_type == FT.HEAD_SHOULDER_BOTTOM:
                        if tick.low < hsf.tick_head.low:
                            return None
                        elif not for_left and tick.high > hsf.tick_neckline_left.high:
                            return tick_return

                    if hsf.pattern_type == FT.HEAD_SHOULDER:
                        if tick.is_max and tick.high > compare_value:
                            tick_return = tick
                            compare_value = tick.high
                    else:
                        if tick.is_min and tick.low < compare_value:
                            tick_return = tick
                            compare_value = tick.low
                else:
                    return tick_return
        return tick_return

    def _get_min_tick_list_for_neckline_(self, set_off: int, for_left: bool):
        min_value = math.inf
        list_return = []
        for k in self.get_tick_range(set_off, for_left):
            tick_k = self.tick_list[k]
            if tick_k.is_min:
                if tick_k.low < min_value:
                    list_return.append(tick_k)
                    min_value = tick_k.low
            elif tick_k.is_global_min:
                break
        return list_return

    def _get_max_tick_list_for_neckline_(self, set_off: int, for_left: bool):
        max_value = -math.inf
        list_return = []
        for k in self.get_tick_range(set_off, for_left):
            tick_k = self.tick_list[k]
            if tick_k.is_max:
                if tick_k.high > max_value:
                    list_return.append(tick_k)
                    max_value = tick_k.high
            elif tick_k.is_global_max:
                break
        return list_return


class PatternRangeDetectorHeadShoulder(PatternRangeDetectorMin, PatternRangeDetectorHeadShoulderBase):
    def __init__(self, sys_config: SystemConfiguration):
        tick_list = sys_config.pdh.pattern_data.tick_list_min_max_for_head_shoulder
        PatternRangeDetectorHeadShoulderBase.__init__(self, sys_config, tick_list)
        PatternRangeDetectorMin.__init__(self, sys_config, tick_list)

    @property
    def pattern_type(self):
        return FT.HEAD_SHOULDER

    def __parse_tick_list__(self):
        for entries in self.global_max_tuple_list:
            index = entries[0]
            tick_head = entries[1]
            tick_list_left = self._get_min_tick_list_for_neckline_(index, True)
            tick_list_right = self._get_min_tick_list_for_neckline_(index, False)
            for tick_left in tick_list_left:
                for tick_right in tick_list_right:
                    hsf = HeadShoulderFormation(self.pattern_type, tick_left, tick_head, tick_right)
                    if hsf.is_neckline_distance_compliant():
                        hsf.f_neckline_param = self.__get_linear_f_params__(tick_left, tick_right)
                        pattern_range = self.get_pattern_range(self.number_required_ticks, hsf)
                        if pattern_range is not None:
                            self.__add_pattern_range_to_list_after_check__(pattern_range)


class PatternRangeDetectorHeadShoulderBottom(PatternRangeDetectorMax, PatternRangeDetectorHeadShoulderBase):
    def __init__(self, sys_config: SystemConfiguration):
        tick_list = sys_config.pdh.pattern_data.tick_list_min_max_for_head_shoulder
        PatternRangeDetectorHeadShoulderBase.__init__(self, sys_config, tick_list)
        PatternRangeDetectorMax.__init__(self, sys_config, tick_list)

    @property
    def pattern_type(self):
        return FT.HEAD_SHOULDER_BOTTOM

    def __parse_tick_list__(self):
        for entries in self.global_min_tuple_list:
            index = entries[0]
            tick_head = entries[1]
            tick_list_left = self._get_max_tick_list_for_neckline_(index, True)
            tick_list_right = self._get_max_tick_list_for_neckline_(index, False)
            for tick_left in tick_list_left:
                for tick_right in tick_list_right:
                    hsf = HeadShoulderFormation(self.pattern_type, tick_left, tick_head, tick_right)
                    if hsf.is_neckline_distance_compliant():
                        hsf.f_neckline_param = self.__get_linear_f_params__(tick_left, tick_right)
                        pattern_range = self.get_pattern_range(self.number_required_ticks, hsf)
                        if pattern_range is not None:
                            self.__add_pattern_range_to_list_after_check__(pattern_range)