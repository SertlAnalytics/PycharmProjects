"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern import Pattern
from pattern_trade import PatternTrade
from sertl_analytics.constants.pattern_constants import FT, PTS
from sertl_analytics.constants.my_constants import COLOR


class PatternColors:
    def __init__(self):
        self.for_main_part = COLOR.GREEN_LIGHT
        self.for_buy_part = COLOR.GREEN_LIGHT
        self.for_buy_box = COLOR.GREEN
        self.for_sell_part = COLOR.RED_ORANGE
        self.for_sell_box = COLOR.RED
        self.for_after_selling = COLOR.GREEN
        self.for_retracement = COLOR.YELLOW


class PatternColorHandler:
    @staticmethod
    def get_colors_for_pattern_trade(pattern_trade: PatternTrade) -> PatternColors:
        # if pattern_trade.is_winner:
        #     return 'salmon', 'orangered', 'lightgreen', 'green'  # for watching, buying, selling, after_selling
        # else:
        #     return 'salmon', 'orangered', 'lightgreen', 'red' # for watching, buying, selling, after_selling

        colors = PatternColors()
        if pattern_trade.is_winner:   # 'salmon', 'orangered', 'lightgreen', 'green'  # for watching, buying, selling, after_selling
            colors.for_main_part = COLOR.SALMON
            colors.for_buy_part = COLOR.RED_ORANGE
            colors.for_sell_part = COLOR.GREEN_LIGHT
            colors.for_after_selling = COLOR.GREEN
            colors.for_retracement = PatternColorHandler.__get_retracement_color__()
        else:  # 'salmon', 'orangered', 'lightgreen', 'red' # for watching, buying, selling, after_selling
            colors.for_main_part = COLOR.SALMON
            colors.for_buy_part = COLOR.RED_ORANGE
            colors.for_sell_part = COLOR.GREEN_LIGHT
            colors.for_after_selling = COLOR.RED
            colors.for_retracement = PatternColorHandler.__get_retracement_color__()
        return colors

    def get_colors_for_pattern(self, pattern: Pattern) -> PatternColors:
        colors = PatternColors()
        colors.for_main_part = self.__get_pattern_color__(pattern)
        colors.for_buy_part = self.__get_buy_color__(pattern)
        colors.for_sell_part = self.__get_trade_color__(pattern)
        colors.for_retracement = self.__get_retracement_color__()
        return colors

    @staticmethod
    def __get_pattern_color__(pattern: Pattern):
        is_trade_able = FT.is_pattern_type_long_trade_able(pattern.pattern_type)
        if pattern.was_breakout_done():
            return 'green' if is_trade_able else 'lightgreen'
        else:
            return 'yellow' if is_trade_able else 'khaki'

    @staticmethod
    def __get_buy_color__(pattern: Pattern):
        return 'orangered'

    @staticmethod
    def __get_trade_color__(pattern: Pattern):
        if pattern.was_breakout_done():
            if pattern.trade_result.actual_win > 0:
                return 'lime'
            else:
                return 'orangered'
        else:
            return 'white'

    @staticmethod
    def __get_retracement_color__():
       return 'yellow'
