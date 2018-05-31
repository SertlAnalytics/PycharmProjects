"""
Description: This module contains the pattern classes - central for stock data management
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_constants import FT, FCC, FD
from matplotlib.patches import Ellipse, Polygon
import pandas as pd
import numpy as np
from pattern_range import PatternRange
from pattern_configuration import PatternConfiguration
from pattern_function_container import PatternFunctionContainer
from pattern_trade_result import TradeResult
from pattern_part import PatternPart
import pattern_constraints as cstr
from pattern_value_categorizer import ChannelValueCategorizer
from sertl_analytics.pybase.exceptions import MyException


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
    def __init__(self, pattern_type: str, df: pd.DataFrame, df_min_max: pd.DataFrame,
                 pattern_range: PatternRange, config: PatternConfiguration):
        self.pattern_type = pattern_type
        self.df = df
        self.df_min_max = df_min_max
        self.constraints = self.__get_constraint__()
        self.pattern_range = pattern_range
        self.config = config
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

    def add_part_main(self, part_main: PatternPart):
        self._part_main = part_main
        self.xy = self._part_main.xy
        self.xy_center = self._part_main.xy_center
        self.date_first = self._part_main.date_first
        self.date_last = self._part_main.date_last

    def add_part_trade(self, part_trade: PatternPart):
        self._part_trade = part_trade
        self.xy_trade = self._part_trade.xy

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

    def get_annotation_parameter(self, for_max: bool = True, color: str = 'blue'):
        return self._part_main.get_annotation_parameter(for_max, color)

    def get_shape_part_main(self):
        return Polygon(np.array(self.xy), True)

    def get_shape_part_trade(self):
        return Polygon(np.array(self.xy_trade), True)

    def get_center_shape(self):
        return Ellipse(np.array(self.xy_center), 4, 1)

    def fill_result_set(self):
        if self.is_part_trade_available():
            self.__fill_trade_result__()

    @staticmethod
    def __get_constraint__():
        return cstr.Constraints()

    def is_part_trade_available(self):
        return self._part_trade is not None

    def __get_pattern_function_container__(self) -> PatternFunctionContainer:
        f_lower_list = self.pattern_range.get_complementary_functions(self.pattern_type)
        df_check = self.pattern_range.get_related_part_from_data_frame(self.df_min_max)
        for f_lower in f_lower_list:
            f_upper = self.pattern_range.f_param
            if self.constraints.are_f_lower_f_upper_compliant(f_lower, f_upper):
                function_container = PatternFunctionContainer(self.pattern_type, df_check, f_lower, f_upper)
                value_categorizer = ChannelValueCategorizer(function_container, self.constraints.tolerance_pct)
                if self.constraints.are_global_constraints_satisfied(value_categorizer):
                    return function_container
        return PatternFunctionContainer(self.pattern_type, df_check)

    def __fill_trade_result__(self):
        tolerance_range = self._part_main.breadth * self.constraints.tolerance_pct
        self.trade_result.expected_win = round(self._part_main.breadth, 2)
        self.trade_result.bought_at = round(self.breakout.tick_breakout.close, 2)
        self.trade_result.bought_on = self.breakout.tick_breakout.date
        self.trade_result.max_ticks = self._part_trade.df.shape[0]
        if self.breakout_direction == FD.ASC:
            self.trade_result.stop_loss_at = self._part_main.bound_upper - tolerance_range
            self.trade_result.limit = self._part_main.bound_upper + self.trade_result.expected_win
        else:
            self.trade_result.stop_loss_at = self._part_main.bound_lower + tolerance_range
            self.trade_result.limit = self._part_main.bound_lower - self.trade_result.expected_win

        for ind, rows in self._part_trade.df.iterrows():
            self.trade_result.actual_ticks += 1
            cont = self.__fill_trade_results_for_breakout_direction__(ind, rows)
            if not cont:
                break

    def __fill_trade_results_for_breakout_direction__(self, date, row):
        sig = 1 if self.breakout_direction == FD.ASC else -1

        self.trade_result.sold_at = round(row.Close, 2)  # default
        self.trade_result.sold_on = date  # default
        self.trade_result.actual_win = sig * round(row.Close - self.trade_result.bought_at, 2)  # default

        if (self.breakout_direction == FD.ASC and row.Low < self.trade_result.stop_loss_at) \
                or (self.breakout_direction == FD.DESC and row.High > self.trade_result.stop_loss_at):
            self.trade_result.stop_loss_reached = True
            if self.breakout_direction == FD.ASC:
                self.trade_result.sold_at = min(row.Open, self.trade_result.stop_loss_at)
            else:
                self.trade_result.sold_at = max(row.Open, self.trade_result.stop_loss_at)
            self.trade_result.actual_win = sig * round(self.trade_result.sold_at - self.trade_result.bought_at, 2)
            return False

        if (self.breakout_direction == FD.ASC and row.High > self.trade_result.limit) \
                or (self.breakout_direction == FD.DESC and row.Low < self.trade_result.limit):
            if self.__is_row_trigger_for_extension__(row):  # extend the limit (let the win run)
                self.trade_result.stop_loss_at += sig * self.trade_result.expected_win
                self.trade_result.limit += sig * self.trade_result.expected_win
                self.trade_result.limit_extended_counter += 1
                self.trade_result.formation_consistent = True
            else:
                self.trade_result.sold_at = row.Close
                self.trade_result.actual_win = sig * round(self.trade_result.sold_at - self.trade_result.bought_at, 2)
                self.trade_result.formation_consistent = True
                return False
        return True

    def __is_row_trigger_for_extension__(self, row):
        threshold = 0.005
        if self.breakout_direction == FD.ASC:
            return row.Close > self.trade_result.limit or (row.Close - row.High)/row.Close < threshold
        else:
            return row.Close < self.trade_result.limit or (row.Close - row.Low)/row.Close < threshold


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


class TrianglePattern(Pattern):
    @staticmethod
    def __get_constraint__():
        return cstr.TriangleConstraints()
    # TODO: Most triangles take their first tick (e.g. min) before the 3 ticks on the other side => enhance range


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
    def get_pattern_for_pattern_type(pattern_type: str, df: pd.DataFrame, df_min_max: pd.DataFrame,
                                     pattern_range: PatternRange, config: PatternConfiguration):
        if pattern_type == FT.CHANNEL:
            return ChannelPattern(pattern_type, df, df_min_max, pattern_range, config)
        elif pattern_type == FT.CHANNEL_DOWN:
            return ChannelDownPattern(pattern_type, df, df_min_max, pattern_range, config)
        elif pattern_type == FT.CHANNEL_UP:
            return ChannelUpPattern(pattern_type, df, df_min_max, pattern_range, config)
        elif pattern_type == FT.HEAD_SHOULDER:
            return HeadShoulderPattern(pattern_type, df, df_min_max, pattern_range, config)
        elif pattern_type == FT.TRIANGLE:
            return TrianglePattern(pattern_type, df, df_min_max, pattern_range, config)
        elif pattern_type == FT.TRIANGLE_TOP:
            return TriangleTopPattern(pattern_type, df, df_min_max, pattern_range, config)
        elif pattern_type == FT.TRIANGLE_BOTTOM:
            return TriangleBottomPattern(pattern_type, df, df_min_max, pattern_range, config)
        elif pattern_type == FT.TRIANGLE_UP:
            return TriangleUpPattern(pattern_type, df, df_min_max, pattern_range, config)
        elif pattern_type == FT.TRIANGLE_DOWN:
            return TriangleDownPattern(pattern_type, df, df_min_max, pattern_range, config)
        elif pattern_type == FT.TKE_DOWN:
            return TKEDownPattern(pattern_type, df, df_min_max, pattern_range, config)
        elif pattern_type == FT.TKE_UP:
            return TKEUpPattern(pattern_type, df, df_min_max, pattern_range, config)
        else:
            raise MyException('No pattern defined for pattern type "{}"'.format(pattern_type))
