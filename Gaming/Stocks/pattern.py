"""
Description: This module contains the pattern classes - central for stock data management
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, FCC, FD, DC, CN, SVC, EXTREMA, BT, PT, PRD
import numpy as np
import math
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_trade_result import TradeResult
from pattern_part import PatternPart
import pattern_constraints as cstr
from sertl_analytics.myexceptions import MyException
from sertl_analytics.mydates import MyDate
from pattern_wave_tick import WaveTick
from pattern_function_container import PatternFunctionContainerFactoryApi
from pattern_value_categorizer import ValueCategorizer
from pattern_data_dictionary import PatternDataDictionary


class PatternApi:
    def __init__(self, sys_config: SystemConfiguration, pattern_type: str):
        self.sys_config = sys_config
        self.pattern_type = pattern_type
        self.df_min_max = sys_config.pdh.pattern_data.df_min_max
        self.pattern_range = None
        self.constraints = None
        self.function_container = None


class PatternConditionHandler:
    def __init__(self):
        self.dic = {FCC.BREAKOUT_WITH_BUY_SIGNAL: False,
                    FCC.PREVIOUS_PERIOD_CHECK_OK: False,
                    FCC.COMBINED_PARTS_APPLICABLE: False}

    def __set_breakout_with_buy_signal__(self, value: bool):
        self.dic[FCC.BREAKOUT_WITH_BUY_SIGNAL] = value

    def __get_breakout_with_buy_signal__(self):
        return self.dic[FCC.BREAKOUT_WITH_BUY_SIGNAL]

    breakout_with_buy_signal = property(__get_breakout_with_buy_signal__, __set_breakout_with_buy_signal__)

    def __set_previous_period_check_ok__(self, value: bool):
        self.dic[FCC.PREVIOUS_PERIOD_CHECK_OK] = value

    def __get_previous_period_check_ok__(self):
        return self.dic[FCC.PREVIOUS_PERIOD_CHECK_OK]

    previous_period_check_ok = property(__get_previous_period_check_ok__, __set_previous_period_check_ok__)

    def __set_combined_parts_applicable__(self, value: bool):
        self.dic[FCC.COMBINED_PARTS_APPLICABLE] = value

    def __get_combined_parts_applicable__(self):
        return self.dic[FCC.COMBINED_PARTS_APPLICABLE]

    combined_parts_applicable = property(__get_combined_parts_applicable__, __set_combined_parts_applicable__)


class Pattern:
    def __init__(self, api: PatternApi):
        self.sys_config = api.sys_config
        self.pattern_type = api.pattern_type
        self.data_dict_obj = PatternDataDictionary(self.sys_config)
        self.ticker_id = self.sys_config.runtime.actual_ticker.replace('_', '')
        self.df = self.sys_config.pdh.pattern_data.df
        self.df_length = self.df.shape[0]
        self.df_min_max = self.sys_config.pdh.pattern_data.df_min_max
        # self.tick_distance = api.sys_config.pdh.pattern_data.tick_f_var_distance
        self.constraints = api.constraints
        self.pattern_range = api.pattern_range
        self.ticks_initial = 0
        self.check_length = 0
        self.function_cont = api.function_container
        self._part_predecessor = None
        self._part_main = None
        self._part_trade = None
        self.tolerance_pct = self.constraints.tolerance_pct
        self.condition_handler = PatternConditionHandler()
        self.xy = None
        self.xy_center = None
        self.xy_trade = None
        self.date_first = None
        self.date_last = None
        self.breakout = None
        self.trade_result = TradeResult()
        self.intersects_with_fibonacci_wave = False
        self._available_fibonacci_end_type = None  #  Min, Max
        self.breakout_required_after_ticks = self.__breakout_required_after_ticks__()
        self.y_predict_touch_points = None
        self.y_predict_before_breakout = None
        self.y_predict_after_breakout = None
        self.value_categorizer = None

    @property
    def id(self) -> str:
        equity_type_id = self.data_dict_obj.get(DC.EQUITY_TYPE_ID)
        period_id = self.data_dict_obj.get(DC.PERIOD_ID)
        aggregation = self.data_dict_obj.get(DC.PERIOD_AGGREGATION)
        ticker_id = self.data_dict_obj.get(DC.TICKER_ID)
        pattern_type_id = FT.get_id(self.pattern_type)
        range_id = self.pattern_range.id
        return '{}_{}_{}_{}_{}_{}'.format(equity_type_id, period_id, aggregation, ticker_id, pattern_type_id, range_id)

    @property
    def id_readable(self) -> str:
        period = self.data_dict_obj.get(DC.PERIOD)
        ticker_id = self.data_dict_obj.get(DC.TICKER_ID)
        pattern_type = self.pattern_type
        range_id = self.pattern_range.id
        return '{}_{}_{}_{}'.format(period, ticker_id, pattern_type, range_id)

    def __get_available_fibonacci_end_type__(self):
        return self._available_fibonacci_end_type

    def __set_available_fibonacci_end_type__(self, value):
        self.data_dict_obj.add(DC.AVAILABLE_FIBONACCI_TYPE, value)
        self.data_dict_obj.add(DC.AVAILABLE_FIBONACCI_TYPE_ID, EXTREMA.get_id(value))
        self._available_fibonacci_end_type = value

    available_fibonacci_end_type = property(__get_available_fibonacci_end_type__, __set_available_fibonacci_end_type__)

    @property
    def part_main(self) -> PatternPart:
        return self._part_main

    @property
    def part_trade(self) -> PatternPart:
        return self._part_trade

    @property
    def length(self):
        pos_first = self.part_main.tick_first.position
        if self.part_main.breakout:
            pos_last = self.part_main.breakout.tick_breakout.position
        else:
            pos_last = self.part_main.tick_last.position
        return pos_last - pos_first

    def add_part_main(self, part_main: PatternPart):
        self._part_main = part_main
        self.value_categorizer = self._get_value_categorizer_for_main_part_()
        self.xy = self._part_main.xy
        self.xy_center = self._part_main.xy_center
        self.date_first = self._part_main.date_first
        self.date_last = self._part_main.date_last
        self.__add_data_dict_entries_after_part_main__()
        self.__calculate_predictions_after_part_main__()
        self.__add_predictions_before_breakout_to_data_dict__()
        # The next call is done to have the necessary columns for a online trading predicton
        self.__calculate_predictions_after_breakout__()

    def __calculate_predictions_after_part_main__(self):
        self.__calculate_y_predict__(PT.TOUCH_POINTS)
        self.__calculate_y_predict__(PT.BEFORE_BREAKOUT)

    def add_part_trade(self, part_trade: PatternPart):
        self._part_trade = part_trade
        self.xy_trade = self._part_trade.xy
        self.__calculate_predictions_after_breakout__()

    def is_ready_for_back_testing(self):
        pos_start, pos_last = self.__get_first_last_position_for_back_testing_data__()
        return self.df_length > pos_last and FT.is_pattern_type_long_trade_able(self.pattern_type)

    def get_back_testing_value_pairs(self):
        pos_start, pos_last = self.__get_first_last_position_for_back_testing_data__()
        return_list = []
        for tick in self.sys_config.pdh.pattern_data.tick_list:
            if pos_start < tick.position < pos_last:
                return_list.append([tick.time_stamp, tick.open])
                return_list.append([tick.time_stamp, tick.high])
                return_list.append([tick.time_stamp, tick.low])
                return_list.append([tick.time_stamp, tick.close])
            if tick.position >= pos_last:
                break
        return return_list

    def __get_first_last_position_for_back_testing_data__(self):
        pos_start = self.pattern_range.position_last
        pos_last = pos_start + self.get_maximal_trade_position_size()
        return pos_start, pos_last

    def __calculate_predictions_after_breakout__(self):
        self.__calculate_y_predict__(PT.AFTER_BREAKOUT)
        self.__add_predictions_after_breakout_to_data_dict__()

    def was_any_touch_since_time_stamp(self, time_stamp_since: float, for_print=False):
        if self.was_breakout_done():
            return False
        number_upper_touches = self.value_categorizer.get_number_upper_touches(time_stamp_since)
        number_lower_touches = self.value_categorizer.get_number_lower_touches(time_stamp_since)
        return number_upper_touches + number_lower_touches > 0

    def is_value_in_category(self, value: float, time_stamp: float, value_category: str, print_range: False):
        return self.value_categorizer.is_value_in_category(value, time_stamp, value_category, print_range)

    def __calculate_y_predict__(self, prediction_type: str):
        if prediction_type == PT.TOUCH_POINTS:
            self.__calculate_y_predict_touch_points__()
            # self.__print__prediction__(self.y_predict_touch_points, prediction_type)
        elif prediction_type == PT.BEFORE_BREAKOUT:
            self.__calculate_y_predict_before_breakout__()
            # self.__print__prediction__(self.y_predict_before_breakout, prediction_type)
        elif prediction_type == PT.AFTER_BREAKOUT:
            self.__calculate_y_predict_after_breakout__()
            # self.__print__prediction__(self.y_predict_after_breakout, prediction_type)

    def __calculate_y_predict_touch_points__(self):
        x_data = self.get_x_data_for_prediction_touch_points()
        if x_data is not None:
            self.y_predict_touch_points = self.sys_config.predictor_touch_points.predict_for_label_columns(x_data)

    def __calculate_y_predict_before_breakout__(self):
        x_data = self.get_x_data_for_prediction_before_breakout()
        if x_data is not None:
            self.y_predict_before_breakout = self.sys_config.predictor_before_breakout.predict_for_label_columns(x_data)

    def __calculate_y_predict_after_breakout__(self):
        x_data = self.get_x_data_for_prediction_after_breakout()
        if x_data is not None:
            self.y_predict_after_breakout = self.sys_config.predictor_after_breakout.predict_for_label_columns(x_data)

    def __print__prediction__(self, prediction_dict: dict, prediction_type: str):
        pos_breakout = '-' if self.breakout is None else self.breakout.tick_breakout.position
        print('pattern.add_parts.. {}/{}: {} = {}'.format(
            self.pattern_range.position_list, pos_breakout, prediction_type, prediction_dict))

    def get_f_upper_trade(self):
        if self.breakout.breakout_direction == FD.DESC:
            return self.function_cont.f_breakout
        else:
            return np.poly1d([0, self.function_cont.f_breakout[0] + self.get_expected_win()])

    def get_f_lower_trade(self):
        if self.breakout.breakout_direction == FD.DESC:
            return np.poly1d([0, self.function_cont.f_breakout[0] - self.get_expected_win()])
        else:
            return self.function_cont.f_breakout

    def was_breakout_done(self):
        return True if self.breakout.__class__.__name__ == 'PatternBreakout' else False

    def buy_after_breakout(self):
        if self.was_breakout_done() and self.breakout.is_breakout_a_signal():
            self.condition_handler.breakout_with_buy_signal = True
            return True
        return False

    @property
    def breakout_direction(self):
        if self.was_breakout_done():
            return self.breakout.breakout_direction
        return FD.NONE

    @property
    def expected_breakout_direction(self):
        return self.data_dict_obj.get(DC.FC_BREAKOUT_DIRECTION)

    @property
    def type(self):
        return FT.NONE  # is overwritten

    @property
    def mean(self):
        return 0

    @property
    def ticks(self):
        return self._part_main.ticks

    def get_upper_value(self, time_stamp: float):
        return self.function_cont.get_upper_value(time_stamp)

    def get_lower_value(self, time_stamp: float):
        return self.function_cont.get_lower_value(time_stamp)

    def are_pre_conditions_fulfilled(self):
        check_dict = {
            'Pre_constraints': self.__are_pre_constraints_fulfilled__(),
            'Established': self.__is_formation_established__(),
            'Expected_win': self.__is_expected_win_sufficient__()
        }
        return False if False in [check_dict[key] for key in check_dict] else True

    def are_pre_conditions_for_a_trade_fulfilled(self) -> bool:
        check_dict = {
            'Long_trade_able': FT.is_pattern_type_long_trade_able(self.pattern_type),
            'Breakout_direction': self.expected_breakout_direction in [FD.ASC, FD.DESC],
            'Expected_win_sufficient': self.__is_expected_win_sufficient__()
        }
        if not check_dict['Long_trade_able']:
            print('\n{}: Pattern is not long trade-able.'.format(self.id))
        elif not check_dict['Breakout_direction']:
            print('\n{}: No trade possible: expected_breakout_direction: {}'.format(
                self.id, self.expected_breakout_direction))
        elif not check_dict['Expected_win_sufficient']:
            print('\n{}: No trade possible: expected win {:.2f} not sufficient ({:.2f} required)'.format(
                self.id, self.get_expected_win(), self.sys_config.runtime.actual_expected_win_pct))
        return False if False in [check_dict[key] for key in check_dict] else True

    def are_conditions_for_buy_trigger_fulfilled(self, buy_trigger: str) -> bool:
        if buy_trigger == BT.TOUCH_POINT and not self.__are_conditions_for_a_touch_point_buy_fulfilled__():
            return False
        return True

    def __are_conditions_for_a_touch_point_buy_fulfilled__(self) -> bool:
        check_dict = {
            'No_breakout': not self.is_part_trade_available(),
            'Pattern_type': self.pattern_type in [FT.CHANNEL, FT.TRIANGLE_UP, FT.TRIANGLE_DOWN],
            'Breakout_direction': self.data_dict_obj.get(DC.FC_BREAKOUT_DIRECTION) == FD.ASC,
            'False_breakout': self.data_dict_obj.get(DC.FC_FALSE_BREAKOUT_ID) == 0
        }
        return False if False in check_dict else True

    def __is_formation_established__(self):  # this is the main check whether a formation is ready for a breakout
        return True

    def __are_pre_constraints_fulfilled__(self):
        return self.constraints.are_pre_constraints_fulfilled(self.data_dict_obj.data_dict)

    def get_annotation_parameter(self, color: str = 'blue'):
        annotation_text_for_prediction = self.__get_annotation_text_for_prediction__()
        return self._part_main.get_annotation_parameter(annotation_text_for_prediction, color)

    def __get_annotation_text_for_prediction_OLD__(self):  # ToDo remove after check
        if self.was_breakout_done() and self.y_predict_after_breakout is not None:
            h_pos = self.y_predict_after_breakout[DC.NEXT_PERIOD_HALF_POSITIVE_PCT]
            f_pos = self.y_predict_after_breakout[DC.NEXT_PERIOD_FULL_POSITIVE_PCT]
            h_neg = self.y_predict_after_breakout[DC.NEXT_PERIOD_HALF_NEGATIVE_PCT]
            f_neg = self.y_predict_after_breakout[DC.NEXT_PERIOD_FULL_NEGATIVE_PCT]
            ticks_h_pos = self.y_predict_after_breakout[DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF]
            ticks_f_pos = self.y_predict_after_breakout[DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL]
            ticks_h_neg = self.y_predict_after_breakout[DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF]
            ticks_f_neg = self.y_predict_after_breakout[DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL]
            false_breakout = self.y_predict_before_breakout[DC.FALSE_BREAKOUT]
            false_breakout_str = 'false !!!' if false_breakout == 1 else 'true - GO'
            return 'Prediction: +{}%/-{}% after {} / {} ticks - {}'.format(
                max(h_pos, f_pos), max(h_neg, f_neg), max(ticks_h_pos, ticks_f_pos), max(ticks_h_neg, ticks_f_neg),
                false_breakout_str)
        elif not self.was_breakout_done() and self.y_predict_before_breakout is not None:
            points_top = self.y_predict_touch_points[DC.TOUCH_POINTS_TILL_BREAKOUT_TOP]
            points_bottom = self.y_predict_touch_points[DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM]
            ticks = self.y_predict_before_breakout[DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT]
            direction = self.y_predict_before_breakout[DC.BREAKOUT_DIRECTION_ID]
            direction_str = 'ASC' if direction == 1 else 'DESC'
            false_breakout = self.y_predict_before_breakout[DC.FALSE_BREAKOUT]
            false_breakout_str = 'false !!!' if false_breakout == 1 else 'true - GO'
            return 'Prediction: {}-Breakout after {} ticks and {}/{} touches - {}'.format(
                direction_str, ticks, points_top, points_bottom, false_breakout_str)
        return 'Prediction: sorry - not enough previous data'

    def __get_annotation_text_for_prediction__(self):
        if self.was_breakout_done() and self.y_predict_after_breakout is not None:
            pos_pct_half = self.data_dict_obj.get(DC.FC_HALF_POSITIVE_PCT)
            pos_pct_full = self.data_dict_obj.get(DC.FC_FULL_POSITIVE_PCT)
            pos_pct = max(pos_pct_full, pos_pct_half)
            neg_pct_half = self.data_dict_obj.get(DC.FC_HALF_NEGATIVE_PCT)
            neg_pct_full = self.data_dict_obj.get(DC.FC_FULL_NEGATIVE_PCT)
            neg_pct = max(neg_pct_full, neg_pct_half)
            pos_ticks_half = self.data_dict_obj.get(DC.FC_TICKS_TO_POSITIVE_HALF)
            pos_ticks_full = self.data_dict_obj.get(DC.FC_TICKS_TO_POSITIVE_FULL)
            pos_ticks = pos_ticks_half if pos_pct == pos_pct_half else pos_ticks_full
            neg_ticks_half = self.data_dict_obj.get(DC.FC_TICKS_TO_NEGATIVE_HALF)
            neg_ticks_full = self.data_dict_obj.get(DC.FC_TICKS_TO_NEGATIVE_FULL)
            neg_ticks = neg_ticks_half if neg_pct == neg_pct_half else neg_ticks_full
            false_breakout = self.data_dict_obj.get(DC.FC_FALSE_BREAKOUT_ID)
            false_breakout_str = 'FALSE !!!' if false_breakout == 1 else 'GO !!!'
            return 'Prediction: +{}-{}% / -{}-{}% after {}-{} / {}-{} ticks - {}'.format(
                pos_pct_half, pos_pct_full, neg_pct_half, neg_pct_full,
                pos_ticks_half, pos_ticks_full, neg_ticks_half, neg_ticks_full, false_breakout_str)
        elif not self.was_breakout_done() and self.y_predict_before_breakout is not None:
            points_top = self.data_dict_obj.get(DC.FC_TOUCH_POINTS_TILL_BREAKOUT_TOP)
            points_bottom = self.data_dict_obj.get(DC.FC_TOUCH_POINTS_TILL_BREAKOUT_BOTTOM)
            ticks = self.data_dict_obj.get(DC.FC_TICKS_TILL_BREAKOUT)
            direction = self.data_dict_obj.get(DC.FC_BREAKOUT_DIRECTION_ID)
            direction_str = 'ASC' if direction == 1 else 'DESC'
            false_breakout = self.data_dict_obj.get(DC.FC_FALSE_BREAKOUT_ID)
            false_breakout_str = 'false !!!' if false_breakout == 1 else 'true - GO'
            return 'Prediction: {}-Breakout after {} ticks and {}/{} touches - {}'.format(
                direction_str, ticks, points_top, points_bottom, false_breakout_str)
        return 'Prediction: sorry - not enough previous data'

    def __add_predictions_before_breakout_to_data_dict__(self):
        if self.y_predict_touch_points is None:
            return
        self.data_dict_obj.add(DC.FC_TOUCH_POINTS_TILL_BREAKOUT_TOP,
                               self.y_predict_touch_points[DC.TOUCH_POINTS_TILL_BREAKOUT_TOP])
        self.data_dict_obj.add(DC.FC_TOUCH_POINTS_TILL_BREAKOUT_BOTTOM,
                               self.y_predict_touch_points[DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM])
        self.data_dict_obj.add(DC.FC_TICKS_TILL_BREAKOUT,
                               self.y_predict_before_breakout[DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT])
        self.data_dict_obj.add(DC.FC_BREAKOUT_DIRECTION_ID, self.y_predict_before_breakout[DC.BREAKOUT_DIRECTION_ID])
        self.data_dict_obj.add(DC.FC_BREAKOUT_DIRECTION,
                               FD.ASC if self.data_dict_obj.get(DC.FC_BREAKOUT_DIRECTION_ID) == 1 else FD.DESC)
        self.data_dict_obj.add(DC.FC_FALSE_BREAKOUT_ID, self.y_predict_before_breakout[DC.FALSE_BREAKOUT])
        ts = self.sys_config.config.get_time_stamp_after_ticks(self.data_dict_obj.get(DC.FC_TICKS_TILL_BREAKOUT))
        self.data_dict_obj.add(DC.FC_BUY_DT, MyDate.get_date_from_epoch_seconds(ts))
        self.data_dict_obj.add(DC.FC_BUY_TIME, str(MyDate.get_time_from_epoch_seconds(ts)))

    def __add_predictions_after_breakout_to_data_dict__(self):
        self.data_dict_obj.add(DC.FC_HALF_POSITIVE_PCT, self.y_predict_after_breakout[DC.NEXT_PERIOD_HALF_POSITIVE_PCT])
        self.data_dict_obj.add(DC.FC_FULL_POSITIVE_PCT, self.y_predict_after_breakout[DC.NEXT_PERIOD_FULL_POSITIVE_PCT])
        self.data_dict_obj.add(DC.FC_HALF_NEGATIVE_PCT, self.y_predict_after_breakout[DC.NEXT_PERIOD_HALF_NEGATIVE_PCT])
        self.data_dict_obj.add(DC.FC_FULL_NEGATIVE_PCT, self.y_predict_after_breakout[DC.NEXT_PERIOD_FULL_NEGATIVE_PCT])
        self.data_dict_obj.add(DC.FC_TICKS_TO_POSITIVE_HALF,
                               self.y_predict_after_breakout[DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF])
        self.data_dict_obj.add(DC.FC_TICKS_TO_POSITIVE_FULL,
                               self.y_predict_after_breakout[DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL])
        self.data_dict_obj.add(DC.FC_TICKS_TO_NEGATIVE_HALF,
                               self.y_predict_after_breakout[DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF])
        self.data_dict_obj.add(DC.FC_TICKS_TO_NEGATIVE_FULL,
                               self.y_predict_after_breakout[DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL])
        ts = self.sys_config.config.get_time_stamp_after_ticks(self.data_dict_obj.get(DC.FC_TICKS_TO_POSITIVE_FULL))
        self.data_dict_obj.add(DC.FC_SELL_DT, MyDate.get_date_from_epoch_seconds(ts))
        self.data_dict_obj.add(DC.FC_SELL_TIME, str(MyDate.get_time_from_epoch_seconds(ts)))

    def fill_result_set(self):
        if self.is_part_trade_available():
            self.__fill_trade_result__()
            self.__add_data_dict_entries_after_filling_trade_result__()

    def get_maximal_trade_position_size(self) -> int:
        if self.pattern_type in [FT.TKE_TOP, FT.TKE_BOTTOM] and self.function_cont.f_var_cross_f_upper_f_lower != 0:
            return self.function_cont.position_cross_f_upper_f_lower - self.function_cont.tick_for_helper.position
        else:
            return self.pattern_range.length

    def __get_constraint__(self):
        return cstr.Constraints(self.sys_config)

    def __breakout_required_after_ticks__(self):
        return math.inf

    def is_part_trade_available(self):
        return self._part_trade is not None

    def is_pattern_ready_for_features_table(self):
        enough_distance = self._has_pattern_enough_distance_for_features_table_()
        all_columns = self.data_dict_obj.is_data_dict_ready_for_features_table()
        return enough_distance and all_columns

    def _has_pattern_enough_distance_for_features_table_(self) -> bool:
        if self.part_main.breakout is None:
            return False
        pos_first = self.part_main.tick_first.position
        pos_last = self.part_main.breakout.tick_breakout.position
        return self.length <= pos_first and pos_last <= self.df_length - self.length

    def __fill_trade_result__(self):
        tolerance_range = self._part_main.height * self.constraints.tolerance_pct
        self.trade_result.expected_win = self.get_expected_win()
        self.trade_result.bought_at = round(self.breakout.tick_breakout.close, 2)
        self.trade_result.bought_on = self.breakout.tick_breakout.date
        self.trade_result.max_ticks = self._part_trade.df.shape[0]
        if self.breakout_direction == FD.ASC:
            self.trade_result.stop_loss_at = self._part_main.bound_lower
            self.trade_result.limit = self._part_main.bound_upper + self.trade_result.expected_win
        else:
            self.trade_result.stop_loss_at = self._part_main.bound_upper
            self.trade_result.limit = self._part_main.bound_lower - self.trade_result.expected_win

        for tick in self._part_trade.tick_list:
            self.trade_result.actual_ticks += 1
            if not self.__fill_trade_results_for_breakout_direction__(tick):
                break

    def __is_expected_win_sufficient__(self) -> bool:
        ref_value = self._part_main.tick_last.close
        min_expected_win_pct = self.sys_config.runtime.actual_expected_win_pct
        expected_win_pct = round(((self.get_expected_win() + ref_value) / ref_value - 1)*100, 1)
        return expected_win_pct >= min_expected_win_pct

    def get_expected_win(self):
        return round(self._part_main.height, 4)

    def __fill_trade_results_for_breakout_direction__(self, tick: WaveTick):
        sig = 1 if self.breakout_direction == FD.ASC else -1

        self.trade_result.sold_at = round(tick.close, 2)  # default
        self.trade_result.sold_on = tick.date  # default
        self.trade_result.actual_win = sig * round(tick.close - self.trade_result.bought_at, 2)  # default

        if (self.breakout_direction == FD.ASC and tick.low < self.trade_result.stop_loss_at) \
                or (self.breakout_direction == FD.DESC and tick.high > self.trade_result.stop_loss_at):
            self.trade_result.stop_loss_reached = True
            if self.breakout_direction == FD.ASC:
                self.trade_result.sold_at = min(tick.open, self.trade_result.stop_loss_at)
            else:
                self.trade_result.sold_at = max(tick.open, self.trade_result.stop_loss_at)
            self.trade_result.actual_win = sig * round(self.trade_result.sold_at - self.trade_result.bought_at, 2)
            return False

        if (self.breakout_direction == FD.ASC and tick.high > self.trade_result.limit) \
                or (self.breakout_direction == FD.DESC and tick.low < self.trade_result.limit):
            if self.__is_row_trigger_for_extension__(tick):  # extend the limit (let the win run)
                self.trade_result.stop_loss_at += sig * self.trade_result.expected_win
                self.trade_result.limit += sig * self.trade_result.expected_win
                self.trade_result.limit_extended_counter += 1
                self.trade_result.formation_consistent = True
            else:
                self.trade_result.sold_at = tick.close
                self.trade_result.actual_win = sig * round(self.trade_result.sold_at - self.trade_result.bought_at, 2)
                self.trade_result.formation_consistent = True
                return False
        return True

    def __is_row_trigger_for_extension__(self, tick: WaveTick):
        threshold = 0.005
        if self.breakout_direction == FD.ASC:
            return tick.close > self.trade_result.limit and (tick.high - tick.close)/tick.close < threshold
        else:
            return tick.close < self.trade_result.limit and (tick.close - tick.low)/tick.close < threshold

    def get_x_data_for_prediction_touch_points(self):
        return self.__get_x_data_for_prediction__(PT.TOUCH_POINTS)

    def get_x_data_for_prediction_before_breakout(self):
        return self.__get_x_data_for_prediction__(PT.BEFORE_BREAKOUT)

    def get_x_data_for_prediction_after_breakout(self):
        return self.__get_x_data_for_prediction__(PT.AFTER_BREAKOUT)

    def __get_x_data_for_prediction__(self, prediction_type: str):
        if prediction_type == PT.TOUCH_POINTS:
            feature_columns = self.sys_config.features_table.feature_columns_touch_points
        elif prediction_type == PT.BEFORE_BREAKOUT:
            feature_columns = self.sys_config.features_table.features_columns_before_breakout
        else:
            feature_columns = self.sys_config.features_table.features_columns_after_breakout
        if self.data_dict_obj.is_data_dict_ready_for_columns(feature_columns):
            data_list = self.data_dict_obj.get_data_list_for_columns(feature_columns)
            np_array = np.array(data_list).reshape(1, len(data_list))
            # print('{}: np_array.shape={}'.format(prediction_type, np_array.shape))
            return np_array
        return None

    def _get_value_categorizer_for_main_part_(self) -> ValueCategorizer:
        pos_begin = self._part_main.tick_first.position
        pos_end = self._part_main.tick_last.position
        df_part = self.df_min_max.loc[np.logical_and(self.df_min_max[CN.POSITION] >= pos_begin,
                                                     self.df_min_max[CN.POSITION] <= pos_end)]
        f_cnt = self.function_cont
        tolerance_pct_list = [self.sys_config.config.value_categorizer_tolerance_pct,  # self.tolerance_pct
                              self.sys_config.config.value_categorizer_tolerance_pct_equal]
        return ValueCategorizer(df_part, f_cnt.f_upper, f_cnt.f_lower, f_cnt.h_upper, f_cnt.h_lower, tolerance_pct_list)

    def __add_data_dict_entries_after_part_main__(self):
        tick_first = self.part_main.tick_first
        pos_first = tick_first.position
        time_stamp_first = tick_first.time_stamp
        tick_last = self.part_main.tick_last
        time_stamp_last = tick_last.time_stamp
        if self.part_main.breakout:
            tick_breakout = self.part_main.breakout.tick_breakout
        else:
            tick_breakout = tick_last

        pos_brk = tick_breakout.position
        time_stamp_brk = tick_breakout.time_stamp

        slope_upper, slope_lower, slope_regression = self.part_main.get_slope_values()
        self.data_dict_obj.add(DC.ID, self.id)
        self.data_dict_obj.add(DC.PATTERN_TYPE, self.pattern_type)
        self.data_dict_obj.add(DC.PATTERN_TYPE_ID, FT.get_id(self.pattern_type))
        self.data_dict_obj.add(DC.TS_PATTERN_TICK_FIRST, time_stamp_first)
        self.data_dict_obj.add(DC.TS_PATTERN_TICK_LAST, time_stamp_last)
        self.data_dict_obj.add(DC.TICKS_TILL_PATTERN_FORMED, self.pattern_range.length)
        self.data_dict_obj.add(DC.TS_BREAKOUT, time_stamp_brk)
        self.data_dict_obj.add(DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT,
                               int(tick_breakout.position - self.pattern_range.position_last))
        self.data_dict_obj.add(DC.PATTERN_BEGIN_DT, tick_first.date)
        self.data_dict_obj.add(DC.PATTERN_BEGIN_TIME, tick_first.time_str)
        self.data_dict_obj.add(DC.BREAKOUT_DT, tick_breakout.date)
        self.data_dict_obj.add(DC.BREAKOUT_TIME, tick_breakout.time_str)
        self.data_dict_obj.add(DC.PATTERN_END_DT, tick_last.date)
        self.data_dict_obj.add(DC.PATTERN_END_TIME, tick_last.time_str)
        self.data_dict_obj.add(DC.PATTERN_TOLERANCE_PCT, self.tolerance_pct)
        self.data_dict_obj.add(DC.BREAKOUT_RANGE_MIN_PCT, self.sys_config.config.breakout_range_pct)
        self.data_dict_obj.add(DC.PATTERN_HEIGHT, self.part_main.diff_max_min_till_breakout)
        self.data_dict_obj.add(DC.PATTERN_BEGIN_HIGH, self.function_cont.f_upper(tick_first.f_var))
        self.data_dict_obj.add(DC.PATTERN_BEGIN_LOW, self.function_cont.f_lower(tick_first.f_var))
        self.data_dict_obj.add(DC.PATTERN_END_HIGH, self.function_cont.f_upper(tick_breakout.f_var))
        self.data_dict_obj.add(DC.PATTERN_END_LOW, self.function_cont.f_lower(tick_breakout.f_var))
        self.data_dict_obj.add(DC.SLOPE_UPPER_PCT, slope_upper)
        self.data_dict_obj.add(DC.SLOPE_LOWER_PCT, slope_lower)
        self.data_dict_obj.add(DC.SLOPE_REGRESSION_PCT, slope_regression)
        self.data_dict_obj.add(DC.SLOPE_VOLUME_REGRESSION_PCT,
                               self.data_dict_obj.get_slope(pos_first, tick_breakout.position, CN.VOL))
        self.data_dict_obj.add(DC.SLOPE_BREAKOUT_PCT, self.data_dict_obj.get_slope_breakout(pos_brk))
        self.data_dict_obj.add(DC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED_PCT,
                                   self.data_dict_obj.get_slope_breakout(pos_brk, CN.VOL))
        vc = [SVC.U_on, SVC.L_on] if self.sys_config.config.api_period == PRD.INTRADAY else [SVC.U_in, SVC.L_in]
        time_stamp_end = time_stamp_brk if tick_breakout else time_stamp_last
        touches_top = self.value_categorizer.count_value_category(vc[0], time_stamp_first, time_stamp_end)
        touches_bottom = self.value_categorizer.count_value_category(vc[1], time_stamp_first, time_stamp_end)
        self.data_dict_obj.add(DC.TOUCH_POINTS_TILL_BREAKOUT_TOP, touches_top)
        self.data_dict_obj.add(DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM, touches_bottom)
        if self.part_main.breakout:
            self.data_dict_obj.add(DC.BREAKOUT_DIRECTION, self.part_main.breakout.breakout_direction)
            self.data_dict_obj.add(DC.BREAKOUT_DIRECTION_ID, self.part_main.breakout.sign)  # 1 = ASC, else -1
            self.data_dict_obj.add(DC.VOLUME_CHANGE_AT_BREAKOUT_PCT,
                                   round((self.part_main.breakout.volume_change_pct - 1) * 100, 2))
        else:
            self.data_dict_obj.add(DC.BREAKOUT_DIRECTION, 'None')
            self.data_dict_obj.add(DC.BREAKOUT_DIRECTION_ID, 0)
            self.data_dict_obj.add(DC.VOLUME_CHANGE_AT_BREAKOUT_PCT, 0)
        min_max_dict = self.data_dict_obj.get_min_max_value_dict(tick_first, tick_breakout, self.length)
        self.data_dict_obj.add(DC.PREVIOUS_PERIOD_HALF_TOP_OUT_PCT, float(min_max_dict['max_previous_half'][0]))
        self.data_dict_obj.add(DC.PREVIOUS_PERIOD_FULL_TOP_OUT_PCT, float(min_max_dict['max_previous_full'][0]))
        self.data_dict_obj.add(DC.PREVIOUS_PERIOD_HALF_BOTTOM_OUT_PCT, float(min_max_dict['min_previous_half'][0]))
        self.data_dict_obj.add(DC.PREVIOUS_PERIOD_FULL_BOTTOM_OUT_PCT, float(min_max_dict['min_previous_full'][0]))
        self.data_dict_obj.add(DC.NEXT_PERIOD_HALF_POSITIVE_PCT, float(min_max_dict['positive_next_half'][0]))
        self.data_dict_obj.add(DC.NEXT_PERIOD_FULL_POSITIVE_PCT, float(min_max_dict['positive_next_full'][0]))
        self.data_dict_obj.add(DC.NEXT_PERIOD_HALF_NEGATIVE_PCT, float(min_max_dict['negative_next_half'][0]))
        self.data_dict_obj.add(DC.NEXT_PERIOD_FULL_NEGATIVE_PCT, float(min_max_dict['negative_next_full'][0]))
        self.data_dict_obj.add(DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF,
                               int(min_max_dict['positive_next_half'][1] - pos_brk))
        self.data_dict_obj.add(DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL,
                               int(min_max_dict['positive_next_full'][1] - pos_brk))
        self.data_dict_obj.add(DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF,
                               int(min_max_dict['negative_next_half'][1] - pos_brk))
        self.data_dict_obj.add(DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL,
                               int(min_max_dict['negative_next_full'][1] - pos_brk))
        self.data_dict_obj.add(DC.AVAILABLE_FIBONACCI_TYPE, self.available_fibonacci_end_type)
        self.data_dict_obj.add(DC.AVAILABLE_FIBONACCI_TYPE_ID, EXTREMA.get_id(self.available_fibonacci_end_type))
        self.data_dict_obj.add(DC.EXPECTED_WIN, self.get_expected_win())

    def __add_data_dict_entries_after_filling_trade_result__(self):
        self.data_dict_obj.add(DC.EXPECTED_WIN, self.trade_result.expected_win)
        self.data_dict_obj.add(DC.FALSE_BREAKOUT, self.data_dict_obj.get_flag_for_false_breakout())
        self.data_dict_obj.add(DC.EXPECTED_WIN_REACHED, self.__get_expected_win_reached_flag__())

    def __get_expected_win_reached_flag__(self):
        tick_breakout = self.part_main.breakout.tick_breakout
        df_part = self.df.iloc[tick_breakout.position:min(self.df_length, tick_breakout.position + self.length)]
        win_expected = self.data_dict_obj.get(DC.EXPECTED_WIN)
        if self.breakout_direction == FD.ASC:
            f_value_breakout = self.function_cont.get_upper_value(tick_breakout.f_var)
            max_value = df_part[CN.HIGH].max()
            expected_win_reached = max_value >= f_value_breakout + win_expected
        else:
            f_value_breakout = self.function_cont.get_lower_value(tick_breakout.f_var)
            min_value = df_part[CN.LOW].min()
            expected_win_reached = min_value <= f_value_breakout - win_expected
        return 1 if expected_win_reached else 0


class ChannelPattern(Pattern):
    pass


class ChannelUpPattern(ChannelPattern):
    pass


class ChannelDownPattern(ChannelPattern):
    pass


class HeadShoulderPattern(Pattern):
    def __breakout_required_after_ticks__(self):
        value_01 = self.pattern_range.hsf.distance_start_to_tick_left_neckline
        value_02 = int(self.pattern_range.hsf.distance_neckline/1.5)
        return max(value_01, value_02)

    def get_expected_win(self):
        return self.pattern_range.hsf.expected_win


class HeadShoulderAscPattern(HeadShoulderPattern):
    pass


class HeadShoulderBottomPattern(Pattern):
    def __breakout_required_after_ticks__(self):
        value_01 = self.pattern_range.hsf.distance_start_to_tick_left_neckline
        value_02 = int(self.pattern_range.hsf.distance_neckline /1.5)
        return max(value_01, value_02)

    def get_expected_win(self):
        return self.pattern_range.hsf.expected_win


class HeadShoulderBottomDescPattern(HeadShoulderBottomPattern):
    pass


class TrianglePattern(Pattern):
    def get_expected_win(self):
        return round(self._part_main.height/2, 2)


class TriangleBottomPattern(TrianglePattern):
    pass


class TriangleTopPattern(TrianglePattern):
    pass


class TriangleUpPattern(TrianglePattern):
    pass


class TriangleDownPattern(TrianglePattern):
    pass


class TKEPattern(Pattern):
    def __is_formation_established__(self):  # this is the main check whether a formation is ready for a breakout
        return self._part_main.height / self._part_main.height_at_first_position < 0.5


class TKEDownPattern(TKEPattern):
    pass


class TKEUpPattern(TKEPattern):
    pass


class FibonacciPattern(Pattern):
    def get_expected_win(self):
        # we have to calculate the difference between the last value and the expected minimal retracement
        last_value = self.function_cont.height_end
        expected_retracement = self.pattern_range.fib_form.get_minimal_retracement_range_after_wave_finishing()
        return round(max(expected_retracement - last_value, last_value), 4)


class FibonacciAscPattern(FibonacciPattern):
    pass


class FibonacciDescPattern(FibonacciPattern):
    pass


class PatternFactory:
    @staticmethod
    def get_pattern(sys_config: SystemConfiguration, api: PatternFunctionContainerFactoryApi):
        pattern_type = api.pattern_type
        pattern_api = PatternApi(sys_config, pattern_type)
        pattern_api.df_min_max = api.df_min_max
        pattern_api.pattern_range = api.pattern_range
        pattern_api.constraints = api.constraints
        pattern_api.function_container = api.function_container
        if pattern_type == FT.CHANNEL:
            return ChannelPattern(pattern_api)
        elif pattern_type == FT.CHANNEL_DOWN:
            return ChannelDownPattern(pattern_api)
        elif pattern_type == FT.CHANNEL_UP:
            return ChannelUpPattern(pattern_api)
        elif pattern_type == FT.HEAD_SHOULDER:
            return HeadShoulderPattern(pattern_api)
        elif pattern_type == FT.HEAD_SHOULDER_ASC:
            return HeadShoulderAscPattern(pattern_api)
        elif pattern_type == FT.HEAD_SHOULDER_BOTTOM:
            return HeadShoulderBottomPattern(pattern_api)
        elif pattern_type == FT.HEAD_SHOULDER_BOTTOM_DESC:
            return HeadShoulderBottomDescPattern(pattern_api)
        elif pattern_type == FT.TRIANGLE:
            return TrianglePattern(pattern_api)
        elif pattern_type == FT.TRIANGLE_TOP:
            return TriangleTopPattern(pattern_api)
        elif pattern_type == FT.TRIANGLE_BOTTOM:
            return TriangleBottomPattern(pattern_api)
        elif pattern_type == FT.TRIANGLE_UP:
            return TriangleUpPattern(pattern_api)
        elif pattern_type == FT.TRIANGLE_DOWN:
            return TriangleDownPattern(pattern_api)
        elif pattern_type == FT.TKE_BOTTOM:
            return TKEDownPattern(pattern_api)
        elif pattern_type == FT.TKE_TOP:
            return TKEUpPattern(pattern_api)
        elif pattern_type == FT.FIBONACCI_ASC:
            return FibonacciAscPattern(pattern_api)
        elif pattern_type == FT.FIBONACCI_DESC:
            return FibonacciDescPattern(pattern_api)
        else:
            raise MyException('No pattern defined for pattern type "{}"'.format(pattern_type))
