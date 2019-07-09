"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


from sertl_analytics.datafetcher.database_fetcher import MyView
from sertl_analytics.constants.pattern_constants import SVW, DC


class WaveView(MyView):
    @staticmethod
    def __get_name__():
        return SVW.V_WAVE

    @staticmethod
    def __get_select_statement__():
        index_column = "CASE WHEN E.Exchange = 'Bitfinex' THEN 'Crypto Currencies' ELSE E.Exchange END as Equity_Index"
        wave_end_date_column = "substr(W.Wave_End_Datetime, 1, 10) AS Wave_End_Date"
        return "SELECT {}, {}, W.* FROM Wave as W JOIN Equity AS E ON E.KEY = W.Ticker_ID".format(
            index_column, wave_end_date_column
        )


class PatternView(MyView):
    @staticmethod
    def __get_name__():
        return SVW.V_PATTERN

    @staticmethod
    def __get_select_statement__():
        tick_columns_dict = DC.get_column_dict_for_tick_columns()
        divisor = '({} + {})'.format(DC.TICKS_TILL_PATTERN_FORMED, DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT)
        # we round down to 5er steps
        tick_pct_columns = ['round({}*20/{}) * 5 AS {}'.format(tick_col, divisor, pct_col)
                            for tick_col, pct_col in tick_columns_dict.items()]
        return "SELECT P.*, {} FROM Pattern as P WHERE {} > 0 AND {} > 0".format(
            ', '.join(tick_pct_columns), divisor, DC.TICKS_TILL_PATTERN_FORMED)

