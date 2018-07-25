"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern import Pattern


class PatternColorHandler:
    def get_colors_for_pattern(self, pattern: Pattern):
        return self.__get_pattern_color__(pattern), self.__get_trade_color__(pattern)

    @staticmethod
    def __get_pattern_color__(pattern: Pattern):
        if pattern.was_breakout_done():
            return 'green'
        else:
            return 'yellow'

    @staticmethod
    def __get_trade_color__(pattern: Pattern):
        if pattern.was_breakout_done():
            if pattern.trade_result.actual_win > 0:
                return 'lime'
            else:
                return 'orangered'
        else:
            return 'white'