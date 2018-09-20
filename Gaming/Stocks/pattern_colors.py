"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern import Pattern
from sertl_analytics.constants.pattern_constants import FT


class PatternColorHandler:
    def get_colors_for_pattern(self, pattern: Pattern):
        return self.__get_pattern_color__(pattern), self.__get_trade_color__(pattern)

    @staticmethod
    def __get_pattern_color__(pattern: Pattern):
        is_trade_able = FT.is_pattern_type_long_trade_able(pattern.pattern_type)
        if pattern.was_breakout_done():
            return 'green' if is_trade_able else 'lightgreen'
        else:
            return 'yellow' if is_trade_able else 'khaki'

    @staticmethod
    def __get_trade_color__(pattern: Pattern):
        if pattern.was_breakout_done():
            if pattern.trade_result.actual_win > 0:
                return 'lime'
            else:
                return 'orangered'
        else:
            return 'white'
