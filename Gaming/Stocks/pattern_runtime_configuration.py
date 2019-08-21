"""
Description: This module contains the runtime configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, TP, EQUITY_TYPE


class RuntimeConfiguration:
    def __init__(self):
        self.actual_list = []
        self.actual_position = 0
        self.actual_tick_position = 0
        self.actual_ticker = ''
        self.actual_ticker_equity_type = EQUITY_TYPE.NONE
        self.actual_ticker_name = ''
        self.actual_and_clause = ''
        self.actual_expected_win_pct = 0  # pct in this case is 10 for 10%
        self.actual_trade_process = TP.ONLINE
        self.actual_pattern_range_from_time_stamp = 0
        self.actual_pattern_range_to_time_stamp = 0