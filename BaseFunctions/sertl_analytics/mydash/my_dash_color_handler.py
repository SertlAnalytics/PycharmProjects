"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


class DashColorHandler:
    @staticmethod
    def get_colors_for_winner(is_winner: bool):
        if is_winner:
            return 'salmon', 'orangered', 'lightgreen', 'green'  # for watching, buying, selling, after_selling
        else:
            return 'salmon', 'orangered', 'lightgreen', 'red' # for watching, buying, selling, after_selling

    @staticmethod
    def __get_color_for_breakout__(was_breakout_done: bool, is_trade_able: bool):
        if was_breakout_done:
            return 'green' if is_trade_able else 'lightgreen'
        else:
            return 'yellow' if is_trade_able else 'khaki'

    @staticmethod
    def __get_color_for_actual_win_color__(actual_win: float):
        if actual_win > 0:
            return 'lime'
        else:
            return 'orangered'

    @staticmethod
    def __get_retracement_color__():
       return 'yellow'
