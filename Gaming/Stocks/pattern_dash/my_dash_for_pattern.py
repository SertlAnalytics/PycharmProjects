"""
Description: This module is the main module for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

from dash.dependencies import Input, Output
from datetime import datetime
import json
from sertl_analytics.myconstants import MyAPPS
from pattern_dash.my_dash_base import MyDashBase
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.mydates import MyDate
from pattern_dash.my_dash_components import MyDCC, MyHTML
from pattern_dash.my_dash_components import MyHTMLHeaderTable
from pattern_dash.my_dash_tab_for_pattern import MyDashTab4Pattern
from pattern_dash.my_dash_tab_for_trades import MyDashTab4Trades
from pattern_dash.my_dash_tab_for_trade_statistics import MyDashTab4TradeStatistics
from pattern_dash.my_dash_tab_for_pattern_statistics import MyDashTab4PatternStatistics
from pattern_bitfinex import BitfinexConfiguration


class MyDash4Pattern(MyDashBase):
    def __init__(self, sys_config: SystemConfiguration, bitfinex_config: BitfinexConfiguration):
        MyDashBase.__init__(self, MyAPPS.PATTERN_DETECTOR_DASH())
        self.sys_config = sys_config
        self.bitfinex_config = bitfinex_config
        self.tab_pattern = MyDashTab4Pattern(self.app, self.sys_config, self.bitfinex_config)
        self.tab_trades = MyDashTab4Trades(self.app, self.sys_config, self.bitfinex_config)
        self.tab_trade_statistics = MyDashTab4TradeStatistics(self.app, self.sys_config)
        self.tab_pattern_statistics = MyDashTab4PatternStatistics(self.app, self.sys_config)

    def get_pattern(self):
        self.__set_app_layout__()
        self.__init_interval_callback_for_user_name__()
        self.__init_interval_callback_for_timer__()
        self.tab_pattern.init_callbacks()
        self.tab_trades.init_callbacks()
        self.tab_trade_statistics.init_callbacks()
        self.tab_pattern_statistics.init_callbacks()

    @staticmethod
    def __create_callback__():
        def callback_hover_data(hoverData):
            return json.dumps(hoverData, indent=2)
        return callback_hover_data

    def __init_interval_callback_for_user_name__(self):
        @self.app.callback(
            Output('my_user_name_div', 'children'),
            [Input('my_interval_timer', 'n_intervals')])
        def handle_interval_callback_for_user_name(n_intervals):
            if self._user_name == '':
                self._user_name = self._get_user_name_()
            return self._user_name

    def __init_interval_callback_for_timer__(self):
        @self.app.callback(
            Output('my_time_div', 'children'),
            [Input('my_interval_timer', 'n_intervals')])
        def handle_interval_callback_for_timer(n_intervals):
            if n_intervals % self.bitfinex_config.check_ticker_after_timer_intervals == 0:
                self.tab_trades.trade_handler.check_actual_trades()
            return '{}'.format(MyDate.get_time_from_datetime(datetime.now()))

    def __set_app_layout__(self):
        # self.app.layout = self.__get_div_for_tab_pattern_detection__()
        self.app.layout = self.__get_div_for_app_layout__()

    def __get_div_for_app_layout__(self):
        # see also https://github.com/plotly/dash-core-components/pull/213
        header = self.__get_header_for_app__()
        timer = MyDCC.interval('my_interval_timer', self.bitfinex_config.ticker_refresh_rate_in_seconds)
        tabs = self.__get_tabs_for_app__()
        return MyHTML.div('my_app', [header, timer, tabs])

    @staticmethod
    def __get_header_for_app__():
        return MyHTMLHeaderTable().get_table()

    def __get_tabs_for_app__(self):
        tab_01 = MyDCC.tab('Pattern Detector', [self.tab_pattern.get_div_for_tab()])
        tab_02 = MyDCC.tab('Trades', [self.tab_trades.get_div_for_tab()])
        tab_03 = MyDCC.tab('Trade statistics', [self.tab_trade_statistics.get_div_for_tab()])
        tab_04 = MyDCC.tab('Pattern statistics', [self.tab_pattern_statistics.get_div_for_tab()])
        return MyDCC.tabs('my_app_tabs', [tab_01, tab_02, tab_03, tab_04])
