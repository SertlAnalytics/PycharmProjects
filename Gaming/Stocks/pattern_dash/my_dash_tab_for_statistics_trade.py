"""
Description: This module contains the tab for Dash for trade statistics.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-26
"""

from dash.dependencies import Input, Output
from sertl_analytics.constants.pattern_constants import DC
from pattern_dash.my_dash_header_tables import MyHTMLTabTradeStatisticsHeaderTable
from pattern_dash.my_dash_drop_down import TradeStatisticsDropDownHandler
from pattern_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter4Trades
from pattern_dash.my_dash_tab_for_statistics_base import MyDashTab4StatisticsBase
import pandas as pd


class MyDashTab4TradeStatistics(MyDashTab4StatisticsBase):
    def __fill_tab__(self):
        self._tab = 'trade'

    @staticmethod
    def __get_html_tab_header_table__():
        return MyHTMLTabTradeStatisticsHeaderTable().get_table()

    def __get_df_base__(self) -> pd.DataFrame:
        return self.sys_config.db_stock.get_trade_records_for_statistics_as_dataframe()

    def __init_dd_handler__(self):
        self._dd_handler = TradeStatisticsDropDownHandler()

    def __init_plotter__(self):
        self._plotter = MyDashTabStatisticsPlotter4Trades(self._df_base, self._color_handler)

    def __init_callback_for_numbers__(self):
        @self.app.callback(
            Output(self._my_statistics_div, 'children'),
            [Input('my_interval_timer', 'n_intervals')])
        def handle_callback_for_numbers(n_intervals: int):
            self.__fill_df_base__()
            number_all = self._df_base.shape[0]
            number_pos = self._df_base[self._df_base[DC.TRADE_RESULT_ID] == 1].shape[0]
            number_neg = self._df_base[self._df_base[DC.TRADE_RESULT_ID] == -1].shape[0]
            return '{} (+{}/-{})'.format(number_all, number_pos, number_neg)
