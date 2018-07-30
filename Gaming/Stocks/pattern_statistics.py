"""
Description: This module contains the statitics classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import PSC, FD
from pattern_configuration import config, runtime
from pattern import Pattern
from sertl_analytics.mydates import MyDate
import pandas as pd


class PatternStatistics:
    def __init__(self):
        self.list = []
        self.column_list = []

        self.column_list.append(PSC.NUMBER)
        self.column_list.append(PSC.TICKER)
        self.column_list.append(PSC.NAME)
        self.column_list.append(PSC.STATUS)
        self.column_list.append(PSC.PATTERN)
        self.column_list.append(PSC.BEGIN_PREVIOUS)
        self.column_list.append(PSC.BEGIN)
        self.column_list.append(PSC.END)

        self.column_list.append(PSC.C_BOUND_UPPER_VALUE)
        self.column_list.append(PSC.C_BOUND_LOWER_VALUE)
        self.column_list.append(PSC.C_CHECK_PREVIOUS_PERIOD)
        self.column_list.append(PSC.C_BREAKOUT_OVER_CONGESTION)
        self.column_list.append(PSC.C_TOLERANCE_PCT)
        self.column_list.append(PSC.C_BREAKOUT_RANGE_PCT)
        self.column_list.append(PSC.C_AND_CLAUSE)

        self.column_list.append(PSC.CON_PREVIOUS_PERIOD_CHECK_OK)
        self.column_list.append(PSC.CON_COMBINED_PARTS_APPLICABLE)
        self.column_list.append(PSC.CON_BREAKOUT_WITH_BUY_SIGNAL)

        self.column_list.append(PSC.LOWER)
        self.column_list.append(PSC.UPPER)
        self.column_list.append(PSC.SLOPE_UPPER)
        self.column_list.append(PSC.SLOPE_LOWER)
        self.column_list.append(PSC.SLOPE_RELATION)
        self.column_list.append(PSC.TICKS)
        self.column_list.append(PSC.BREAKOUT_DATE)
        self.column_list.append(PSC.BREAKOUT_DIRECTION)
        self.column_list.append(PSC.VOLUME_CHANGE)
        self.column_list.append(PSC.EXPECTED)
        self.column_list.append(PSC.RESULT)
        self.column_list.append(PSC.EXT)
        self.column_list.append(PSC.VAL)
        self.column_list.append(PSC.BOUGHT_AT)
        self.column_list.append(PSC.SOLD_AT)
        self.column_list.append(PSC.BOUGHT_ON)
        self.column_list.append(PSC.SOLD_ON)
        self.column_list.append(PSC.T_NEEDED)

        self.column_list.append(PSC.LIMIT)
        self.column_list.append(PSC.STOP_LOSS_AT)
        self.column_list.append(PSC.STOP_LOSS_TRIGGERED)

        self.column_list.append(PSC.RESULT_DF_MAX)
        self.column_list.append(PSC.RESULT_DF_MIN)
        self.column_list.append(PSC.FIRST_LIMIT_REACHED)
        self.column_list.append(PSC.STOP_LOSS_MAX_REACHED)

        self.dic = {}

    def __init_dic__(self):
        for entries in self.column_list:
            self.dic[entries] = ''

    def add_entry(self, pattern: Pattern):
        self.__init_dic__()

        self.dic[PSC.C_BOUND_UPPER_VALUE] = config.bound_upper_value
        self.dic[PSC.C_BOUND_LOWER_VALUE] = config.bound_lower_value
        self.dic[PSC.C_CHECK_PREVIOUS_PERIOD] = config.check_previous_period
        self.dic[PSC.C_BREAKOUT_OVER_CONGESTION] = config.breakout_over_congestion_range
        self.dic[PSC.C_TOLERANCE_PCT] = pattern.tolerance_pct
        self.dic[PSC.C_BREAKOUT_RANGE_PCT] = config.breakout_range_pct
        self.dic[PSC.C_AND_CLAUSE] = config.and_clause

        self.dic[PSC.CON_PREVIOUS_PERIOD_CHECK_OK] = pattern.condition_handler.previous_period_check_ok
        self.dic[PSC.CON_COMBINED_PARTS_APPLICABLE] = pattern.condition_handler.combined_parts_applicable
        self.dic[PSC.CON_BREAKOUT_WITH_BUY_SIGNAL] = pattern.condition_handler.breakout_with_buy_signal

        self.dic[PSC.STATUS] = 'Finished' if pattern.was_breakout_done() else 'Open'
        self.dic[PSC.NUMBER] = runtime.actual_number
        self.dic[PSC.TICKER] = runtime.actual_ticker
        self.dic[PSC.NAME] = runtime.actual_ticker_name
        self.dic[PSC.PATTERN] = pattern.pattern_type
        self.dic[PSC.BEGIN_PREVIOUS] = 'TODO'
        self.dic[PSC.BEGIN] = MyDate.get_date_from_datetime(pattern.date_first)
        self.dic[PSC.END] = MyDate.get_date_from_datetime(pattern.date_last)
        self.dic[PSC.LOWER] = round(0, 2)
        self.dic[PSC.UPPER] = round(0, 2)  # TODO Lower & Upper bound for statistics
        slope_upper, slope_lower, slope_relation, slow_regression = pattern.part_main.get_slope_values()
        self.dic[PSC.SLOPE_UPPER] = slope_upper
        self.dic[PSC.SLOPE_LOWER] = slope_lower
        self.dic[PSC.SLOPE_RELATION] = slope_relation
        self.dic[PSC.TICKS] = pattern.part_main.ticks
        if pattern.was_breakout_done():
            self.dic[PSC.BREAKOUT_DATE] = MyDate.get_date_from_datetime(pattern.breakout.breakout_date)
            self.dic[PSC.BREAKOUT_DIRECTION] = pattern.breakout.breakout_direction
            self.dic[PSC.VOLUME_CHANGE] = pattern.breakout.volume_change_pct
            if pattern.is_part_trade_available():
                self.dic[PSC.EXPECTED] = pattern.trade_result.expected_win
                self.dic[PSC.RESULT] = pattern.trade_result.actual_win
                self.dic[PSC.VAL] = pattern.trade_result.formation_consistent
                self.dic[PSC.EXT] = pattern.trade_result.limit_extended_counter
                self.dic[PSC.BOUGHT_AT] = round(pattern.trade_result.bought_at, 2)
                self.dic[PSC.SOLD_AT] = round(pattern.trade_result.sold_at, 2)
                self.dic[PSC.BOUGHT_ON] = MyDate.get_date_from_datetime(pattern.trade_result.bought_on)
                self.dic[PSC.SOLD_ON] = MyDate.get_date_from_datetime(pattern.trade_result.sold_on)
                self.dic[PSC.T_NEEDED] = pattern.trade_result.actual_ticks
                self.dic[PSC.LIMIT] = round(pattern.trade_result.limit, 2)
                self.dic[PSC.STOP_LOSS_AT] = round(pattern.trade_result.stop_loss_at, 2)
                self.dic[PSC.STOP_LOSS_TRIGGERED] = pattern.trade_result.stop_loss_reached
                if pattern.part_trade is not None:
                    self.dic[PSC.RESULT_DF_MAX] = pattern.part_trade.max
                    self.dic[PSC.RESULT_DF_MIN] = pattern.part_trade.min
                self.dic[PSC.FIRST_LIMIT_REACHED] = False  # default
                self.dic[PSC.STOP_LOSS_MAX_REACHED] = False  # default
                if pattern.breakout_direction == FD.ASC \
                        and (pattern.part_main.bound_upper + pattern.part_main.height < self.dic[PSC.RESULT_DF_MAX]):
                    self.dic[PSC.FIRST_LIMIT_REACHED] = True
                if pattern.breakout_direction == FD.DESC \
                        and (pattern.part_main.bound_lower - pattern.part_main.height > self.dic[PSC.RESULT_DF_MIN]):
                    self.dic[PSC.FIRST_LIMIT_REACHED] = True
                if pattern.breakout_direction == FD.ASC \
                        and (pattern.part_main.bound_lower > self.dic[PSC.RESULT_DF_MIN]):
                    self.dic[PSC.STOP_LOSS_MAX_REACHED] = True
                if pattern.breakout_direction == FD.DESC \
                        and (pattern.part_main.bound_upper < self.dic[PSC.RESULT_DF_MAX]):
                    self.dic[PSC.STOP_LOSS_MAX_REACHED] = True

        new_entry = [self.dic[column] for column in self.column_list]
        self.list.append(new_entry)

    def get_frame_set(self) -> pd.DataFrame:
        df = pd.DataFrame(self.list)
        df.columns = self.column_list
        return df

    def print_overview(self):
        if len(self.list) == 0:
            print('No formations found')
        else:
            df = self.get_frame_set()
            print(df.head(df.shape[0]))
            print('\n')

    def write_to_excel(self, excel_writer, sheet):
        if len(self.list) == 0:
            print('No formations found')
        else:
            df = self.get_frame_set()
            df.to_excel(excel_writer, sheet)


class PatternDetectorStatisticsApi:
    def __init__(self, pattern_list, investment: float):
        self.pattern_list = pattern_list
        self.counter_actual_ticks = 0
        self.counter_ticks = 0
        self.counter_stop_loss = 0
        self.counter_formation_OK = 0
        self.counter_formation_NOK = 0
        self.investment_working = investment
        self.investment_start = investment
        self.__fill_parameter__()
        self.diff_pct = round(100 * (self.investment_working - self.investment_start) / self.investment_start, 2)

    def __fill_parameter__(self):
        for pattern in self.pattern_list:
            if pattern.was_breakout_done() and pattern.is_part_trade_available():
                result = pattern.trade_result
                self.counter_actual_ticks += result.actual_ticks
                self.counter_ticks += result.max_ticks
                self.counter_stop_loss = self.counter_stop_loss + 1 if result.stop_loss_reached else self.counter_stop_loss
                self.counter_formation_OK = self.counter_formation_OK + 1 if result.formation_consistent \
                    else self.counter_formation_OK
                self.counter_formation_NOK = self.counter_formation_NOK + 1 if not result.formation_consistent \
                    else self.counter_formation_NOK
                traded_entities = int(self.investment_working / result.bought_at)
                self.investment_working = round(self.investment_working + (traded_entities * result.actual_win), 2)


class DetectorStatistics:
    def __init__(self):
        self.list = []
        self.column_list = ['Number', 'Ticker', 'Name', 'Investment', 'Result', 'Change%', 'SL', 'F_OK', 'F_NOK', 'Ticks']

    def add_entry(self, api: PatternDetectorStatisticsApi):
        new_entry = [runtime.actual_number, runtime.actual_ticker, runtime.actual_ticker_name
            , api.investment_start, api.investment_working, api.diff_pct
            , api.counter_stop_loss, api.counter_formation_OK, api.counter_formation_NOK, api.counter_actual_ticks]
        self.list.append(new_entry)

    def get_frame_set(self) -> pd.DataFrame:
        df = pd.DataFrame(self.list)
        df.columns = self.column_list
        return df

    def print_overview(self):
        df = self.get_frame_set()
        print(df.head(df.shape[0]))

    def write_to_excel(self, excel_writer, sheet):
        df = self.get_frame_set()
        df.to_excel(excel_writer, sheet)


class ConstraintsStatistics:
    def __init__(self):
        self.list = []
        self.constraint_value_list = ['tolerance_pct',
                                      'f_upper_percentage_bounds',
                                      'f_lower_percentage_bounds', 'height_end_start_relation_bounds',
                                      'f_regression_percentage_bounds', 'breakout_required_after_ticks',
                                      'global_all_in', 'global_count', 'global_series'
                                      ]
        self.column_list = ['Constraint'] + [items for items in self.constraint_value_list]

    def add_entry(self, patter_type: str, value_dict: dict):
        new_entry = [patter_type] + [value_dict[key] for key in self.constraint_value_list]
        self.list.append(new_entry)

    def get_frame_set(self) -> pd.DataFrame:
        df = pd.DataFrame(self.list)
        df.columns = self.column_list
        return df

    def print_overview(self):
        df = self.get_frame_set()
        print(df.head(df.shape[0]))

    def write_to_excel(self, excel_writer, sheet):
        df = self.get_frame_set()
        df.to_excel(excel_writer, sheet)

