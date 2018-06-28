"""
Description: This module contains the pattern classes - central for stock data management
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, FCC, FD
from pattern_data_container import pattern_data_handler as pdh
from matplotlib.patches import Ellipse, Polygon
import pandas as pd
import numpy as np
from pattern_range import PatternRange
from pattern_configuration import config
from pattern_function_container import PatternFunctionContainer
from pattern_trade_result import TradeResult
from pattern_part import PatternPart
import pattern_constraints as cstr
from pattern_value_categorizer import ChannelValueCategorizer
from sertl_analytics.pybase.exceptions import MyException
from pattern_wave_tick import WaveTick


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
    def __init__(self, pattern_type: str, pattern_range: PatternRange, complementary_function: np.poly1d):
        self.pattern_type = pattern_type
        self.df = pdh.pattern_data.df
        self.df_min_max = pdh.pattern_data.df_min_max
        self.complementary_function = complementary_function
        self.constraints = self.__get_constraint__()
        self.pattern_range = pattern_range
        self.ticks_initial = 0
        self.check_length = 0
        self.function_cont = self.__get_pattern_function_container__()
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

    @property
    def part_main(self) -> PatternPart:
        return self._part_main

    @property
    def part_trade(self) -> PatternPart:
        return self._part_trade

    def add_part_main(self, part_main: PatternPart):
        self._part_main = part_main
        self.xy = self._part_main.xy
        self.xy_center = self._part_main.xy_center
        self.date_first = self._part_main.date_first
        self.date_last = self._part_main.date_last

    def add_part_trade(self, part_trade: PatternPart):
        self._part_trade = part_trade
        self.xy_trade = self._part_trade.xy

    def get_f_upper_trade(self):
        if self.breakout.breakout_direction == FD.DESC:
            return self.function_cont.h_lower
        else:
            return np.poly1d([0, self.function_cont.h_upper[0] + self.__get_expected_win__()])

    def get_f_lower_trade(self):
        if self.breakout.breakout_direction == FD.DESC:
            return np.poly1d([0, self.function_cont.h_lower[0] - self.__get_expected_win__()])
        else:
            return self.function_cont.h_upper

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
    def type(self):
        return FT.NONE  # is overwritten

    @property
    def mean(self):
        return 0

    @property
    def ticks(self):
        return self._part_main.ticks

    def is_formation_established(self):  # this is the main check whether a formation is ready for a breakout
        return True

    def get_annotation_parameter(self, color: str = 'blue'):
        return self._part_main.get_annotation_parameter(color)

    def get_shape_part_main(self):
        return Polygon(np.array(self.xy), True)

    def get_shape_part_trade(self):
        return Polygon(np.array(self.xy_trade), True)

    def get_center_shape(self):
        ellipse_breadth = self.part_main.breadth/6
        return Ellipse(np.array(self.xy_center), 5, ellipse_breadth)

    def fill_result_set(self):
        if self.is_part_trade_available():
            self.__fill_trade_result__()

    def get_maximal_trade_size(self) -> int:
        if self.pattern_type in [FT.TKE_UP, FT.TKE_DOWN] and self.function_cont.f_var_cross_f_upper_f_lower != 0:
            return self.function_cont.f_var_cross_f_upper_f_lower - self.function_cont.tick_for_helper.f_var
        else:
            return self.pattern_range.position_last - self.pattern_range.position_first

    @staticmethod
    def __get_constraint__():
        return cstr.Constraints()

    def is_part_trade_available(self):
        return self._part_trade is not None

    def __get_pattern_function_container__(self) -> PatternFunctionContainer:
        df_check = self.pattern_range.get_related_part_from_data_frame(self.df_min_max)
        if self.pattern_range.__class__.__name__ == 'PatternRangeMin':
            f_upper = self.complementary_function
            f_lower = self.pattern_range.f_param
        else:
            f_lower = self.complementary_function
            f_upper = self.pattern_range.f_param
        f_container = PatternFunctionContainer(self.pattern_type, df_check, f_lower, f_upper)
        if self.constraints.are_f_lower_f_upper_pct_compliant(f_container.f_lower_pct, f_container.f_upper_pct):
            if self.constraints.is_f_regression_pct_compliant(f_container.f_regression_pct):
                value_categorizer = ChannelValueCategorizer(f_container, self.constraints.tolerance_pct)
                if self.constraints.are_global_constraints_satisfied(value_categorizer):
                    return f_container
        return PatternFunctionContainer(self.pattern_type, df_check)

    def __fill_trade_result__(self):
        tolerance_range = self._part_main.breadth * self.constraints.tolerance_pct
        self.trade_result.expected_win = self.__get_expected_win__()
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

    def __get_expected_win__(self):
        return round(self._part_main.breadth, 2)

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


class ChannelPattern(Pattern):
    @staticmethod
    def __get_constraint__():
        return cstr.ChannelConstraints()


class ChannelUpPattern(ChannelPattern):
    @staticmethod
    def __get_constraint__():
        return cstr.ChannelUpConstraints()


class ChannelDownPattern(ChannelPattern):
    @staticmethod
    def __get_constraint__():
        return cstr.ChannelDownConstraints()


class HeadShoulderPattern(Pattern):
    @staticmethod
    def __get_constraint__():
        return cstr.HeadShoulderConstraints()


class InverseHeadShoulderPattern(Pattern):
    @staticmethod
    def __get_constraint__():
        return cstr.InverseHeadShoulderConstraints()


class TrianglePattern(Pattern):
    @staticmethod
    def __get_constraint__():
        return cstr.TriangleConstraints()
    # TODO: Most triangles take their first tick (e.g. min) before the 3 ticks on the other side => enhance range

    def __get_expected_win__(self):
        return round(self._part_main.distance_min, 2)


class TriangleBottomPattern(TrianglePattern):
    @staticmethod
    def __get_constraint__():
        return cstr.TriangleBottomConstraints()


class TriangleTopPattern(TrianglePattern):
    @staticmethod
    def __get_constraint__():
        return cstr.TriangleTopConstraints()


class TriangleUpPattern(TrianglePattern):
    @staticmethod
    def __get_constraint__():
        return cstr.TriangleUpConstraints()


class TriangleDownPattern(TrianglePattern):
    @staticmethod
    def __get_constraint__():
        return cstr.TriangleDownConstraints()


class TKEPattern(Pattern):
    def is_formation_established(self):  # this is the main check whether a formation is ready for a breakout
        return self._part_main.breadth / self._part_main.breadth_first < 0.4


class TKEDownPattern(TKEPattern):
    @staticmethod
    def __get_constraint__():
        return cstr.TKEDownConstraints()


class TKEUpPattern(TKEPattern):
    @staticmethod
    def __get_constraint__():
        return cstr.TKEUpConstraints()


class PatternHelper:
    @staticmethod
    def get_pattern_for_pattern_type(pattern_type: str, pattern_range: PatternRange, complementary_function: np.poly1d):
        if pattern_type == FT.CHANNEL:
            return ChannelPattern(pattern_type, pattern_range, complementary_function)
        elif pattern_type == FT.CHANNEL_DOWN:
            return ChannelDownPattern(pattern_type, pattern_range, complementary_function)
        elif pattern_type == FT.CHANNEL_UP:
            return ChannelUpPattern(pattern_type, pattern_range, complementary_function)
        elif pattern_type == FT.HEAD_SHOULDER:
            return HeadShoulderPattern(pattern_type, pattern_range, complementary_function)
        elif pattern_type == FT.HEAD_SHOULDER_INVERSE:
            return InverseHeadShoulderPattern(pattern_type, pattern_range, complementary_function)
        elif pattern_type == FT.TRIANGLE:
            return TrianglePattern(pattern_type, pattern_range, complementary_function)
        elif pattern_type == FT.TRIANGLE_TOP:
            return TriangleTopPattern(pattern_type, pattern_range, complementary_function)
        elif pattern_type == FT.TRIANGLE_BOTTOM:
            return TriangleBottomPattern(pattern_type, pattern_range, complementary_function)
        elif pattern_type == FT.TRIANGLE_UP:
            return TriangleUpPattern(pattern_type, pattern_range, complementary_function)
        elif pattern_type == FT.TRIANGLE_DOWN:
            return TriangleDownPattern(pattern_type, pattern_range, complementary_function)
        elif pattern_type == FT.TKE_DOWN:
            return TKEDownPattern(pattern_type, pattern_range, complementary_function)
        elif pattern_type == FT.TKE_UP:
            return TKEUpPattern(pattern_type, pattern_range, complementary_function)
        else:
            raise MyException('No pattern defined for pattern type "{}"'.format(pattern_type))
