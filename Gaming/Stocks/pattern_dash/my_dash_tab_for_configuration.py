"""
Description: This module contains the dash tab for configurations.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-09
"""

from dash.dependencies import Input, Output, State
from pattern_dash.my_dash_base import MyDashBaseTab
from pattern_system_configuration import SystemConfiguration
from pattern_dash.my_dash_components import MyHTML
from pattern_dash.my_dash_configuration_tables import MyHTMLRuntimeConfigurationTable, MyHTMLBitfinexConfigurationTable
from pattern_dash.my_dash_configuration_tables import MyHTMLSystemConfigurationTable, MyHTMLPatternConfigurationTable
from pattern_dash.my_dash_configuration_tables import MyHTMLTradeOptimizerTable, MyHTMLConfigurationTable
from pattern_trade_handler import PatternTradeHandler
from dash import Dash
from sertl_analytics.constants.pattern_constants import DC, TP, PRD, RST
from pattern_news_handler import NewsHandler


class SSBT:  # SwitchSimulationButtonText
    SWITCH_TO_SIMULATION = 'Start simulation mode'
    SWITCH_TO_TRADING = 'Start automatic trading'
    

class MyDashTab4Configuration(MyDashBaseTab):
    def __init__(self, app: Dash, sys_config: SystemConfiguration, trade_handler_online: PatternTradeHandler):
        MyDashBaseTab.__init__(self, app, sys_config)
        self._trade_handler_online = trade_handler_online

    @staticmethod
    def __get_news_handler__():
        return NewsHandler('  \n', '')

    def __init_dd_handler__(self):
        # self._dd_handler = TradeDropDownHandler()
        pass

    def __init_selected_row__(self, trade_type=''):
        self._selected_trade_type = trade_type
        self._selected_row_index = -1
        self._selected_row = None
        self._selected_pattern_trade = None

    def get_div_for_tab(self):
        children_list = [
            MyHTML.div_with_html_button_submit('my_switch_trading_mode_button',
                                               self.__get_switch_mode_button_text__(), hidden=''),
            self.get_div_for_tables()
        ]
        return MyHTML.div('my_configuration_div', children_list)

    def get_div_for_tables(self):
        return MyHTML.div('my_configuration_tables_div', self.__get_tables_for_div__())

    def __get_tables_for_div__(self):
        return [
            MyHTMLSystemConfigurationTable(self.sys_config).get_table(),
            MyHTMLBitfinexConfigurationTable(self.sys_config.exchange_config).get_table(),
            MyHTMLPatternConfigurationTable(self.sys_config.config).get_table(),
            MyHTMLTradeOptimizerTable(self.sys_config.trade_strategy_optimizer).get_table(),
            MyHTMLRuntimeConfigurationTable(self.sys_config.runtime_config).get_table(),
        ]

    def init_callbacks(self):
        self.__init_callback_for_switch_trading_mode_button__()
        self.__init_callback_for_configuration_tables__()
        self.__init_callback_for_dash_board_sub_title__()
        # self.__init_callback_for_config_markdown__()

    def __get_switch_mode_button_text__(self):
        return SSBT.SWITCH_TO_TRADING if self._trade_handler_online.is_simulation else SSBT.SWITCH_TO_SIMULATION

    def __init_callback_for_dash_board_sub_title__(self):
        @self.app.callback(
            Output('my_dashboard_sub_title_div', 'children'),
            [Input('my_switch_trading_mode_button', 'children')])
        def handle_callback_for_dash_board_title(button_text: str):
            if self._trade_handler_online.is_simulation:
                return 'simulation'
            return 'active!!!'

    def __init_callback_for_configuration_tables__(self):
        @self.app.callback(
            Output('my_configuration_tables_div', 'children'),
            [Input('my_switch_trading_mode_button', 'children'),
             Input('my_refresh_button', 'hidden')])
        def handle_callback_for_configuration_tables(button_text: str, hidden: str):
            return self.__get_tables_for_div__()

    def __init_callback_for_switch_trading_mode_button__(self):
        @self.app.callback(
            Output('my_switch_trading_mode_button', 'children'),
            [Input('my_switch_trading_mode_button', 'n_clicks')],
            [State('my_switch_trading_mode_button', 'children')])
        def handle_callback_for_switch_trading_mode_button(n_clicks: int, button_text: str):
            if n_clicks == 0:
                return button_text
            if button_text == SSBT.SWITCH_TO_SIMULATION:
                self._trade_handler_online.deactivate_trading_mode()
                self._trade_handler_online.trade_client.exchange_config.print_actual_mode()
                return SSBT.SWITCH_TO_TRADING
            elif button_text == SSBT.SWITCH_TO_TRADING:
                self._trade_handler_online.activate_trading_mode()
                self._trade_handler_online.trade_client.exchange_config.print_actual_mode()
                return SSBT.SWITCH_TO_SIMULATION
            return button_text






