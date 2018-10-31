"""
Description: This module contains the configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, TP, CN, EQUITY_TYPE, PRD
from sertl_analytics.mydates import MyDate


class PatternDebugger:
    def __init__(self):
        self.__process_dic = {}
        self.pattern_range_position_list = []

    @property
    def is_active(self):
        for process in self.__process_dic:
            if self.__process_dic[process]:
                return True
        return False

    def check_range_position_list(self, position_list: list):
        process = 'position_list'
        self.__init_process__(process)
        min_len = min(len(position_list), len(self.pattern_range_position_list))
        if min_len > 0:
            intersect = set(position_list).intersection(set(self.pattern_range_position_list))
            if len(intersect) == len(self.pattern_range_position_list):
                self.__activate_process__(process)

    def __init_process__(self, process: str):
        self.__process_dic[process] = False

    def __activate_process__(self, process: str):
        self.__process_dic[process] = True


class RuntimeConfiguration:
    actual_list = []
    actual_position = 0
    actual_tick_position = 0
    actual_ticker = ''
    actual_ticker_equity_type = EQUITY_TYPE.NONE
    actual_ticker_name = ''
    actual_and_clause = ''
    actual_pattern_type = FT.NONE
    actual_breakout = None
    actual_pattern_range = None
    actual_expected_win_pct = 0  # pct in this case is 10 for 10%
    actual_trade_process = TP.ONLINE
    actual_pattern_range_from_time_stamp = 0
    actual_pattern_range_to_time_stamp = 0


class PatternConfiguration:
    def __init__(self):
        self.with_trade_part = True  # we need this configuration for testing touch strategy
        self.pattern_type_list = [FT.CHANNEL]
        self.pattern_ids_to_find = []
        self.simple_moving_average_number = 10
        self.save_pattern_data = True
        self.save_trade_data = True
        self.show_differences_to_stored_features = False
        self.bound_upper_value = CN.HIGH
        self.bound_lower_value = CN.LOW
        self.plot_data = True
        self.plot_min_max = False
        self.plot_only_pattern_with_fibonacci_waves = True
        self.plot_volume = False
        self.plot_close = False
        self.length_for_global_min_max = 50  # a global minimum or maximum must have at least this number as distance
        self.length_for_global_min_max_fibonacci = 10  # ...for fibonacci
        self.length_for_local_min_max = 2  # a local minimum or maximum must have at least this number as distance
        self.length_for_local_min_max_fibonacci = self.length_for_local_min_max  # fibonacci
        self.fibonacci_tolerance_pct = 0.20  # it works great for 0.20 = 20% tolerance for retracement and regression
        self.fibonacci_detail_print = False
        self.check_previous_period = False   # default
        self.breakout_over_congestion_range = False
        self.breakout_range_pct = 0.05
        self.investment = 1000
        self.max_pattern_range_length = 50
        self.show_final_statistics = True
        self.statistics_excel_file_name = ''
        self.statistics_constraints_excel_file_name = 'pattern_statistics/constraints.xlsx'
        self.__previous_period_length = 0

    def __get_previous_period_length__(self):
        return self.__previous_period_length

    def __set_previous_period_length__(self, value: int):
        self.__previous_period_length = value

    previous_period_length = property(__get_previous_period_length__, __set_previous_period_length__)