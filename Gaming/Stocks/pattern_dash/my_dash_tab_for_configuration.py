"""
Description: This module contains the dash tab for configurations.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-09
"""

from dash.dependencies import Input, Output, State
from sertl_analytics.exchanges.exchange_cls import ExchangeConfiguration
from sertl_analytics.exchanges.bitfinex import BitfinexConfiguration
from sertl_analytics.exchanges.interactive_broker import IBKRConfiguration
from pattern_dash.my_dash_base import MyDashBaseTab
from pattern_system_configuration import SystemConfiguration
from pattern_dash.my_dash_components import MyHTML
from pattern_dash.my_dash_tab_dd_for_configuration import ConfigurationTabDropDownHandler, CDD
from pattern_dash.my_dash_configuration_tables import MyHTMLRuntimeConfigurationTable, MyHTMLBitfinexConfigurationTable
from pattern_dash.my_dash_configuration_tables import MyHTMLSystemConfigurationTable, MyHTMLPatternConfigurationTable
from pattern_dash.my_dash_configuration_tables import MyIBRKConfigurationTable
from pattern_dash.my_dash_configuration_tables import MyHTMLTradeOptimizerTable
from pattern_trade_handler import PatternTradeHandler
from pattern_sound.pattern_sound_machine import PatternSoundMachine
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
        self._dd_handler = ConfigurationTabDropDownHandler(ExchangeConfiguration.buy_order_value_max,
                                                           PatternSoundMachine.is_active,
                                                           ExchangeConfiguration.small_profit_taking_active)

    @staticmethod
    def __get_news_handler__():
        return NewsHandler('  \n', '')

    def __init_selected_row__(self, trade_type=''):
        self._selected_trade_type = trade_type
        self._selected_row_index = -1
        self._selected_row = None
        self._selected_pattern_trade = None

    def get_div_for_tab(self):
        children_list = [
            MyHTML.div_with_html_button_submit('my_switch_trading_mode_button',
                                               self.__get_switch_mode_button_text__(), hidden=''),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(CDD.ORDER_MAXIMUM)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(CDD.SOUND_MACHINE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(CDD.SMALL_PROFIT)),
            self.get_div_for_tables()
        ]
        return MyHTML.div('my_configuration_div', children_list)

    def get_div_for_tables(self):
        return MyHTML.div('my_configuration_tables_div', self.__get_tables_for_div__())

    def __get_tables_for_div__(self):
        return [
            MyHTMLSystemConfigurationTable(self.sys_config).get_table(),
            MyHTMLBitfinexConfigurationTable(self.sys_config.exchange_config).get_table(),
            MyIBRKConfigurationTable(self.sys_config.shares_config).get_table(),
            MyHTMLPatternConfigurationTable(self.sys_config.config).get_table(),
            MyHTMLTradeOptimizerTable(self.sys_config.trade_strategy_optimizer).get_table(),
            MyHTMLRuntimeConfigurationTable(self.sys_config.runtime_config).get_table(),
        ]

    def init_callbacks(self):
        self.__init_callback_for_my_sound_div__()
        self.__init_callbacks_for_my_mode_div__()
        self.__init_callbacks_for_my_max_buy_div__()
        self.__init_callbacks_for_my_small_profit_div__()
        self.__init_callback_for_switch_trading_mode_button__()
        self.__init_callback_for_configuration_tables__()
        self.__init_callback_for_dash_board_sub_title__()
        # self.__init_callback_for_config_markdown__()

    def __get_switch_mode_button_text__(self):
        return SSBT.SWITCH_TO_TRADING if self._trade_handler_online.is_simulation else SSBT.SWITCH_TO_SIMULATION

    def __init_callback_for_dash_board_sub_title__(self):
        @self.app.callback(
            Output('my_dashboard_sub_title_div', 'children'),
            [Input('my_switch_trading_mode_button', 'children'),
             Input('my_configuration_order_maximum', 'value'),
             Input('my_configuration_sound_machine_state', 'value')])
        def handle_callback_for_dash_board_title(button_text: str, order_maximum: int, state_sound: str):
            sound_str = '' if state_sound == 'active' else ' (sound: inactive)'
            if self._trade_handler_online.is_simulation:
                return 'simulation{}'.format(sound_str)
            return 'active!!! - max. buy value: {:d}{}'.format(order_maximum, sound_str)

    def __init_callback_for_my_sound_div__(self):
        @self.app.callback(
            Output('my_sound_div', 'children'),
            [Input('my_configuration_sound_machine_state', 'value')])
        def handle_callback_for_dash_board_sound(state_sound: str):
            return state_sound

    def __init_callbacks_for_my_mode_div__(self):
        @self.app.callback(
            Output('my_mode_div', 'children'),
            [Input('my_switch_trading_mode_button', 'children')])
        def handle_callback_for_dash_board_mode_value(button_text: str):
            return 'simulation' if self._trade_handler_online.is_simulation else 'active (real trading)'

        @self.app.callback(
            Output('my_mode_div', 'style'),
            [Input('my_switch_trading_mode_button', 'children')])
        def handle_callback_for_dash_board_mode_style(button_text: str):
            return self.__get_style_for_mode_and_max_buy_values__()

    def __init_callbacks_for_my_max_buy_div__(self):
        @self.app.callback(
            Output('my_max_buy_div', 'children'),
            [Input('my_configuration_order_maximum', 'value')])
        def handle_callback_for_dash_board_max_buy_value(order_maximum: int):
            return '{:d}'.format(order_maximum)

        @self.app.callback(
            Output('my_max_buy_div', 'style'),
            [Input('my_switch_trading_mode_button', 'children')])
        def handle_callback_for_dash_board_max_buy_style(button_text: str):
            return self.__get_style_for_mode_and_max_buy_values__()

    def __init_callbacks_for_my_small_profit_div__(self):
        @self.app.callback(
            Output('my_small_profit_div', 'children'),
            [Input('my_configuration_small_profit_state', 'value')])
        def handle_callback_for_dash_board_small_profit_value(small_profit_state: str):
            ExchangeConfiguration.small_profit_taking_active = True if small_profit_state == 'active' else False
            return small_profit_state

        @self.app.callback(
            Output('my_small_profit_div', 'style'),
            [Input('my_configuration_small_profit_state', 'value')])
        def handle_callback_for_dash_board_small_profit_style(small_profit_state: str):
            if small_profit_state == 'active':
                return {'font-weight': 'bold', 'color': 'red', 'display': 'inline-block'}
            return {'font-weight': 'normal', 'color': 'black', 'display': 'inline-block'}

    def __get_style_for_mode_and_max_buy_values__(self):
        if self._trade_handler_online.is_simulation:
            return {'font-weight': 'normal', 'color': 'black', 'display': 'inline-block'}
        return {'font-weight': 'bold', 'color': 'red', 'display': 'inline-block'}

    def __init_callback_for_configuration_tables__(self):
        @self.app.callback(
            Output('my_configuration_tables_div', 'children'),
            [Input('my_switch_trading_mode_button', 'children'),
             Input('my_configuration_order_maximum', 'value'),
             Input('my_configuration_sound_machine_state', 'value'),
             Input('my_configuration_small_profit_state', 'value'),
             Input('my_refresh_button', 'n_clicks')])
        def handle_callback_for_configuration_tables(
                button_text: str, order_max: int, sound_machine: str, small_profit: str, n_clicks: int):
            PatternSoundMachine.is_active = True if sound_machine == 'active' else False
            BitfinexConfiguration.buy_order_value_max = order_max
            IBKRConfiguration.buy_order_value_max = order_max
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
                self.sys_config.exchange_config.deactivate_automatic_trading()
                self.sys_config.shares_config.deactivate_automatic_trading()
                return SSBT.SWITCH_TO_TRADING
            elif button_text == SSBT.SWITCH_TO_TRADING:
                self.sys_config.exchange_config.activate_automatic_trading()
                self.sys_config.shares_config.activate_automatic_trading()
                return SSBT.SWITCH_TO_SIMULATION
            return button_text






