"""
Description: This module contains the configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, CN, PDP


class PatternConfiguration:
    def __init__(self):
        self.detection_process = PDP.ALL
        self.with_trade_part = True  # we need this configuration for testing touch strategy
        self.with_trading = False
        self.trading_last_price_mean_aggregation = 16  # the number of ticker.last_price which are used for stop loss
        self.pattern_type_list = [FT.CHANNEL]
        self.pattern_ids_to_find = []
        self.simple_moving_average_number = 10
        self.save_pattern_data = True
        self.save_trade_data = True
        self.replace_existing_trade_data_on_db = False
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
        self.show_final_statistics = False
        self.statistics_excel_file_name = ''
        self.statistics_constraints_excel_file_name = ''  # ''../pattern_statistics/constraints.xlsx'
        self.__previous_period_length = 0

    def __get_previous_period_length__(self):
        return self.__previous_period_length

    def __set_previous_period_length__(self, value: int):
        self.__previous_period_length = value

    previous_period_length = property(__get_previous_period_length__, __set_previous_period_length__)