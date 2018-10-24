"""
Description: This module contains the dash tab for actual or back-tested trades.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-26
"""

import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import pandas as pd
from pattern_dash.my_dash_base import MyDashBase, MyDashBaseTab
from pattern_system_configuration import SystemConfiguration
from pattern_dash.my_dash_components import MyDCC, MyHTML, DccGraphApi
from pattern_dash.my_dash_header_tables import MyHTMLTabTradeHeaderTable
from pattern_dash.my_dash_tab_dd_for_trades import TradeDropDownHandler, TDD
from sertl_analytics.exchanges.exchange_cls import ExchangeConfiguration
from pattern_trade_handler import PatternTradeHandler
from pattern_trade import PatternTrade
from pattern_database.stock_tables import TradeTable, PatternTable
from pattern_database.stock_database import StockDatabaseDataFrame
from dash import Dash
from sertl_analytics.constants.pattern_constants import DC, TP, BT, TSTR
from pattern_wave_tick import WaveTick, WaveTickList
from pattern_test.trade_test_cases import TradeTestCaseFactory
from pattern_test.trade_test import TradeTest
from pattern_data_container import PatternData
from sertl_analytics.mydates import MyDate
from copy import deepcopy
from pattern_news_handler import NewsHandler


class ReplayHandler:
    def __init__(self, trade_process: str, sys_config: SystemConfiguration, exchange_config: ExchangeConfiguration):
        self.trade_process = trade_process
        self.sys_config = sys_config.get_semi_deep_copy()
        self.sys_config.runtime.actual_trade_process = self.trade_process
        self.exchange_config = deepcopy(exchange_config)  # we change the simulation mode...
        self.trade_handler = PatternTradeHandler(self.sys_config, self.exchange_config)
        self.trade_test_api = None
        self.trade_test = None
        self.detector = None
        self.test_case = None
        self.test_case_wave_tick_list_index = -1
        self.graph_api = None
        self.graph = None

    @property
    def graph_id(self):
        if self.trade_process == TP.TRADE_REPLAY:
            return 'my_graph_trade_replay'
        if self.trade_process == TP.PATTERN_REPLAY:
            return 'my_graph_pattern_replay'
        return 'my_graph_trade_online'

    @property
    def graph_title(self):
        return '{}: {}-{}-{}-{}'.format(self.trade_test_api.symbol,
                                        self.trade_test_api.buy_trigger, self.trade_test_api.trade_strategy,
                                        self.trade_test_api.pattern_type, self.sys_config.config.api_period)

    @property
    def pattern_trade(self) -> PatternTrade:
        return self.graph_api.pattern_trade

    def set_trade_test_api_by_selected_trade_row(self, selected_row):
        self.trade_test_api = TradeTestCaseFactory.get_trade_test_api_by_selected_trade_row(
            selected_row, self.trade_process)
        if self.trade_process in [TP.TRADE_REPLAY, TP.PATTERN_REPLAY]:
            self.trade_test_api.get_data_from_db = True
            self.trade_test_api.period = selected_row[DC.PERIOD]
            self.trade_test_api.period_aggregation = selected_row[DC.PERIOD_AGGREGATION]
        else:
            self.trade_test_api.get_data_from_db = False
            self.trade_test_api.period = self.sys_config.config.api_period
            self.trade_test_api.period_aggregation = self.sys_config.config.api_period_aggregation
            self.trade_test_api.trade_id = selected_row[DC.ID]

    def is_another_wave_tick_available(self):
        return self.get_remaining_tick_number() > 0

    def get_remaining_tick_number(self):
        return len(self.test_case.wave_tick_list) - 1 - self.test_case_wave_tick_list_index

    def get_next_wave_tick(self) -> WaveTick:
        self.test_case_wave_tick_list_index += 1
        wave_tick = self.test_case.wave_tick_list[self.test_case_wave_tick_list_index]
        time_stamp = wave_tick.time_stamp
        date_time = MyDate.get_date_time_from_epoch_seconds(time_stamp)
        value = wave_tick.close
        print('{}: {}-new value pair to check: [{} ({}), {}]'.format(
            self.trade_process, self.trade_test_api.symbol, date_time, time_stamp, value))
        return wave_tick

    def set_trade_test(self):
        self.trade_test = TradeTest(self.trade_test_api, self.sys_config, self.exchange_config)

    def set_detector(self):
        self.detector = self.trade_test.get_pattern_detector_for_replay(self.trade_test_api)

    def set_pattern_to_api(self):
        self.trade_test_api.pattern = self.detector.get_pattern_for_replay()

    def set_tick_list_to_api(self):
        api = self.trade_test_api
        stock_db_df_obj = StockDatabaseDataFrame(self.sys_config.db_stock, api.symbol, api.and_clause_unlimited)
        # print('api.symbol={}, api.and_clause_unlimited={}, stock_db_df_obj.df_data.shape={}'.format(
        #     api.symbol, api.and_clause_unlimited, stock_db_df_obj.df_data.shape))
        pattern_data = PatternData(self.sys_config.config, stock_db_df_obj.df_data)
        self.trade_test_api.tick_list_for_replay = pattern_data.tick_list

    def set_test_case(self):
        self.test_case = TradeTestCaseFactory.get_test_case_from_pattern(self.trade_test_api)

    def add_pattern_list_for_trade(self):
        self.trade_handler.add_pattern_list_for_trade([self.trade_test_api.pattern])

    def set_graph_api(self):
        self.graph_api = DccGraphApi(self.graph_id, self.graph_title)
        if self.trade_process in [TP.TRADE_REPLAY, TP.PATTERN_REPLAY]:
            self.graph_api.pattern_trade = self.trade_handler.pattern_trade_for_replay
            self.graph_api.ticker_id = self.trade_test_api.symbol
            self.graph_api.df = self.detector.sys_config.pdh.pattern_data.df
        else:
            self.set_selected_trade_to_api()
            print('set_graph_api: trade_id={}, pattern_trade.id={}'.format(self.trade_test_api.trade_id,
                                                                           self.graph_api.pattern_trade.id))
            self.graph_api.ticker_id = self.trade_test_api.symbol
            self.graph_api.df = self.graph_api.pattern_trade.get_data_frame_for_replay()
        self.graph_api.period = self.trade_test_api.period

    def set_selected_trade_to_api(self):
        self.graph_api.pattern_trade = self.trade_handler.get_pattern_trade_by_id(self.trade_test_api.trade_id)

    def check_actual_trades_for_replay(self, wave_tick: WaveTick):
        self.trade_handler.check_actual_trades_for_replay(wave_tick)
        self.graph_api.df = self.trade_handler.get_pattern_trade_data_frame_for_replay()

    def refresh_api_df_from_pattern_trade(self):
        # self.set_selected_trade_to_api()
        self.graph_api.df = self.graph_api.pattern_trade.get_data_frame_for_replay()


class MyDashTab4Trades(MyDashBaseTab):
    _data_table_name = 'actual_trade_table'

    def __init__(self, app: Dash, sys_config: SystemConfiguration, exchange_config: ExchangeConfiguration,
                 trade_handler_online: PatternTradeHandler):
        MyDashBaseTab.__init__(self, app, sys_config)
        self.exchange_config = exchange_config
        self._trade_handler_online = trade_handler_online
        self._df_trade = self.sys_config.db_stock.get_trade_records_for_replay_as_dataframe()
        self._df_trade_for_replay = self._df_trade[TradeTable.get_columns_for_replay()]
        self._trade_rows_for_data_table = MyDCC.get_rows_from_df_for_data_table(self._df_trade_for_replay)
        self._df_pattern = self.sys_config.db_stock.get_pattern_records_for_replay_as_dataframe()
        self._df_pattern_for_replay = self._df_pattern[PatternTable.get_columns_for_replay()]
        self._pattern_rows_for_data_table = MyDCC.get_rows_from_df_for_data_table(self._df_pattern_for_replay)
        self.__init_selected_row__()
        self.__init_replay_handlers__()
        self.__init_dd_handler__()
        self._selected_pattern_trade = None
        self._selected_buy_trigger = None
        self._selected_trade_strategy = None
        self._n_click_restart = 0
        self._stop_trade = None
        self._replay_speed = None
        self._trades_stored_number = 0
        self._trades_online_number = 0
        self._pattern_stored_number = 0
        self._cached_trade_table = None

    @staticmethod
    def __get_news_handler__():
        return NewsHandler('  \n', '')

    def __init_dd_handler__(self):
        self._dd_handler = TradeDropDownHandler()

    def __init_selected_row__(self, trade_type=''):
        self._selected_trade_type = trade_type
        self._selected_row_index = -1
        self._selected_row = None
        self._selected_pattern_trade = None

    def __init_replay_handlers__(self):
        self._trade_replay_handler = ReplayHandler(TP.TRADE_REPLAY, self.sys_config, self.exchange_config)
        self._pattern_replay_handler = ReplayHandler(TP.PATTERN_REPLAY, self.sys_config, self.exchange_config)
        self._trade_replay_handler_online = ReplayHandler(TP.ONLINE, self.sys_config, self.exchange_config)
        self._trade_replay_handler_online.trade_handler = self._trade_handler_online

    @property
    def trade_handler_online(self):
        return self._trade_handler_online

    def get_div_for_tab(self):
        children_list = [
            MyHTMLTabTradeHeaderTable().get_table(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(TDD.TRADE_TYPE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(TDD.BUY_TRIGGER)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(TDD.TRADE_STRATEGY)),
            MyHTML.div_with_html_button_submit('my_replay_restart_button', 'Restart'),
            MyHTML.div_with_html_button_submit('my_replay_stop_button', 'Stop'),
            MyHTML.div_with_html_button_submit('my_replay_speed_button', 'Fast'),
            MyHTML.div('my_trade_table_div', self.__get_table_for_trades__(), False),
            MyHTML.div('my_graph_trade_replay_div', '', False)
        ]
        # scatter_graph = self.__get_scatter_graph_for_trades__('trade_scatter_graph')
        return MyHTML.div('my_trades', children_list)

    def init_callbacks(self):
        self.__init_callback_for_trade_table__()
        self.__init_callback_for_selected_row_indices__()
        self.__init_callback_for_trade_numbers__()
        self.__init_callback_for_trade_markdown__()
        self.__init_callback_for_trade_news_markdown__()
        self.__init_callbacks_for_drop_down_visibility__()
        self.__init_callback_for_trade_selection__()
        self.__init_callback_for_replay_restart_button__()
        self.__init_callback_for_replay_stop_button__()
        self.__init_callback_for_replay_speed_button__()
        self.__init_callback_for_graph_trade__()

    def __init_callback_for_trade_markdown__(self):
        @self.app.callback(
            Output('my_trade_markdown', 'children'),
            [Input('my_graph_trade_replay_div', 'children'),
             Input('my_interval_timer', 'n_intervals')])
        def handle_callback_for_ticket_markdown(children, n_intervals: int):
            if self._selected_row_index == -1 or self._selected_pattern_trade is None:
                return ''
            ticker_refresh_seconds = self.__get_ticker_refresh_seconds__()
            ticks_remaining = self.__get_remaining_tick_number__()
            return self._selected_pattern_trade.get_markdown_text(ticker_refresh_seconds, ticks_remaining)

    def __get_remaining_tick_number__(self):
        if self._selected_trade_type != TP.ONLINE:
            return self.__get_actual_replay_handler__().get_remaining_tick_number()
        return None

    def __init_callback_for_trade_news_markdown__(self):
        @self.app.callback(
            Output('my_trade_news_markdown', 'children'),
            [Input('my_graph_trade_replay_div', 'children'),
             Input('my_interval_timer', 'n_intervals')])
        def handle_callback_for_ticket_markdown(children, n_intervals: int):
            if self._selected_row_index == -1 or self._selected_pattern_trade is None:
                return ''
            return self.__get_markdown_news__()

    def __get_markdown_news__(self):
        actual_replay_handler = self.__get_actual_replay_handler__()
        self._news_handler.add_news_dict(actual_replay_handler.pattern_trade.news_handler.news_dict)
        return self._news_handler.get_news_for_markdown_since_last_refresh(self._time_stamp_last_refresh)

    def __get_actual_replay_handler__(self):
        if self._selected_trade_type == TP.ONLINE:
            return self._trade_replay_handler_online
        elif self._selected_trade_type == TP.PATTERN_REPLAY:
            return self._pattern_replay_handler
        return self._trade_replay_handler

    def __init_callback_for_trade_numbers__(self):
        """
        We need the following series since the call back should be done when all trades are calculated.
        This is done when the first graph and all the others before breakout are calculated.
        Detail: my_graphs_before_breakout_div is called by  'my_graph_first_div'.
        When my_graphs_before_breakout_div is calculated all new trades are known.
        """
        @self.app.callback(
            Output('my_online_trade_div', 'children'),
            # [Input('my_interval', 'n_intervals')])
            [Input('my_graphs_before_breakout_div', 'children')])
        def handle_callback_for_online_trade_numbers(children):
            return str(len(self._trade_replay_handler_online.trade_handler.pattern_trade_dict))

        @self.app.callback(
            Output('my_stored_trade_div', 'children'),
            [Input('my_interval', 'n_intervals')])
        def handle_callback_for_stored_trade_numbers(n_intervals: int):
            return str(len(self._trade_rows_for_data_table))

        @self.app.callback(
            Output('my_stored_pattern_div', 'children'),
            [Input('my_interval', 'n_intervals')])
        def handle_callback_for_stored_pattern_numbers(n_intervals: int):
            return str(len(self._pattern_rows_for_data_table))

    def __init_callback_for_trade_table__(self):
        @self.app.callback(
            Output('my_trade_table_div', 'children'),
            [Input('my_trade_type_selection', 'value'),
             Input('my_online_trade_div', 'children'),
             Input('my_stored_trade_div', 'children'),
             Input('my_stored_pattern_div', 'children')])
        def handle_callback_for_trade_table(trade_type: str, online: int, trades: int, pattern: int):
            if self._selected_trade_type != trade_type:
                self._trades_online_number = online
                self._trades_stored_number = trades
                self._pattern_stored_number = pattern
                self.__init_selected_row__(trade_type)
                self.__init_replay_handlers__()
                return self.__get_table_for_trades__()
            elif self._selected_trade_type == TP.ONLINE and self._trades_online_number != online:
                self._trades_online_number = online
                return self.__get_table_for_trades__()
            elif self._selected_trade_type == TP.TRADE_REPLAY and self._trades_stored_number != trades:
                self._trades_stored_number = trades
                return self.__get_table_for_trades__()
            elif self._selected_trade_type == TP.PATTERN_REPLAY and self._pattern_stored_number != pattern:
                self._pattern_stored_number = pattern
                return self.__get_table_for_trades__()
            return self.__get_table_for_trades__(True)

    def __init_callback_for_trade_selection__(self):
        @self.app.callback(
            Output('my_trade_ticker_div', 'children'),
            [Input('my_graph_trade_replay_div', 'children')])
        def handle_ticker_selection_callback_for_ticker_label(children):
            if self._selected_row_index == -1:
                return 'Please select one entry'
            return self._selected_row[DC.TICKER_ID]

    def __init_callbacks_for_drop_down_visibility__(self):
        for drop_down_type in [TDD.BUY_TRIGGER, TDD.TRADE_STRATEGY]:
            @self.app.callback(
                Output(self._dd_handler.get_embracing_div_id(drop_down_type), 'style'),
                [Input(self._dd_handler.get_element_id(TDD.TRADE_TYPE), 'value')],
                [State(self._dd_handler.get_embracing_div_id(drop_down_type), 'id')])
            def handle_selection_callback(trade_type: str, div_id: str):
                dd_type = self._dd_handler.get_drop_down_type_by_embracing_div_id(div_id)
                style_show = self._dd_handler.get_style_display(dd_type)
                if trade_type != TP.PATTERN_REPLAY:
                    return {'display': 'none'}
                return style_show

    def __init_callback_for_selected_row_indices__(self):
        @self.app.callback(
            Output(self._data_table_name, 'selected_row_indices'),
            [Input('my_trade_table_div', 'children')],
            [State(self._data_table_name, 'rows')])
        def handle_callback_for_selected_row_indices(children, rows):
            if self._selected_row_index == -1 or self._selected_row is None or len(rows) == 0:
                return []
            self.__update_selected_row_number_after_refresh__(rows)
            return [self._selected_row_index]

    def __update_selected_row_number_after_refresh__(self, trade_rows: list):
        selected_row_id = self._selected_row['ID']
        for index, row in enumerate(trade_rows):
            if row['ID'] == selected_row_id:
                if self._selected_row_index != index:
                    print('...updated selected row number: old={} -> {}=new'.format(self._selected_row_index, index))
                    self._selected_row_index = index
                return
        self.__init_selected_row__(self._selected_trade_type)  # we have to reset the selected row, but not the type

    def __init_callback_for_replay_restart_button__(self):
        @self.app.callback(
            Output('my_replay_restart_button', 'hidden'),
            [Input('my_trade_type_selection', 'value'),
             Input(self._data_table_name, 'selected_row_indices'),
             Input('my_pattern_buy_trigger_selection', 'value'),
             Input('my_pattern_trade_strategy_selection', 'value')])
        def handle_callback_for_stop_button(trade_type: str, selected_row_indices: list,
                                            buy_trigger: str, trade_strategy: str):
            if trade_type in [TP.TRADE_REPLAY, TP.PATTERN_REPLAY] and len(selected_row_indices) > 0:
                if self._selected_buy_trigger != buy_trigger:
                    self._selected_buy_trigger = buy_trigger
                    return ''
                elif self._selected_trade_strategy != trade_strategy:
                    self._selected_trade_strategy = trade_strategy
                    return ''
            return 'hidden'

    def __init_callback_for_replay_stop_button__(self):
        @self.app.callback(
            Output('my_replay_stop_button', 'hidden'),
            [Input(self._data_table_name, 'selected_row_indices'),
             Input('my_trade_type_selection', 'value')])
        def handle_callback_for_stop_button(selected_row_indices: list, trade_type: str):
            if trade_type in [TP.TRADE_REPLAY, TP.PATTERN_REPLAY] and len(selected_row_indices) > 0:
                return ''
            else:
                return 'hidden'

        @self.app.callback(
            Output('my_replay_stop_button', 'children'),
            [Input('my_replay_stop_button', 'n_clicks')],
            [State('my_replay_stop_button', 'children')])
        def handle_callback_for_stop_button(n_clicks: int, button_text: str):
            if self._stop_trade is None:
                self._stop_trade = False
                return 'Stop'
            else:
                self._stop_trade = True if button_text == 'Stop' else False
                return 'Continue' if button_text == 'Stop' else 'Stop'

    def __init_callback_for_replay_speed_button__(self):
        @self.app.callback(
            Output('my_replay_speed_button', 'hidden'),
            [Input(self._data_table_name, 'selected_row_indices'),
             Input('my_trade_type_selection', 'value')])
        def handle_callback_for_stop_button(selected_row_indices: list, trade_type: str):
            if trade_type in [TP.TRADE_REPLAY, TP.PATTERN_REPLAY] and len(selected_row_indices) > 0:
                return ''
            else:
                return 'hidden'

        @self.app.callback(
            Output('my_replay_speed_button', 'children'),
            [Input('my_replay_speed_button', 'n_clicks')],
            [State('my_replay_speed_button', 'children')])
        def handle_callback_for_stop_button(n_clicks: int, button_text: str):
            if self._replay_speed is None:
                self._replay_speed = 'Slow'
                return 'Fast'
            else:
                self._replay_speed = 'Slow' if button_text == 'Slow' else 'Fast'
                return 'Slow' if button_text == 'Fast' else 'Fast'

    def __handle_trade_type_selection__(self, trade_type: str):
        if trade_type != self._selected_trade_type:
            self._selected_trade_type = trade_type
            self.__init_selected_row__(trade_type)

    def __handle_trade_restart_selection__(self, n_clicks_restart: int):
        if n_clicks_restart != self._n_click_restart:
            self._n_click_restart = n_clicks_restart
            self.__init_selected_row__(self._selected_trade_type)

    def __init_callback_for_graph_trade__(self):
        @self.app.callback(
            Output('my_graph_trade_replay_div', 'children'),
            [Input(self._data_table_name, 'rows'),
             Input(self._data_table_name, 'selected_row_indices'),
             Input('my_interval_timer', 'n_intervals'),
             Input('my_trade_type_selection', 'value'),
             Input('my_replay_restart_button', 'n_clicks')],
            [State('my_pattern_buy_trigger_selection', 'value'),
             State('my_pattern_trade_strategy_selection', 'value')])
        def handle_callback_for_graph_trade(rows: list, selected_row_indices: list, n_intervals: int,
                                            trade_type: str, n_click_restart: int,
                                            buy_trigger: str, trade_strategy: str):
            self._time_stamp_last_refresh = MyDate.time_stamp_now()
            self.__handle_trade_type_selection__(trade_type)
            self.__handle_trade_restart_selection__(n_click_restart)
            self._selected_buy_trigger = buy_trigger
            self._selected_trade_strategy = trade_strategy
            if len(selected_row_indices) == 0:
                self._selected_row_index = -1
                return ''
            if self._selected_row_index == selected_row_indices[0]:
                if self._selected_trade_type == TP.ONLINE:
                    graph = self.__get_graph_for_trade_online_refreshed__()
                else:
                    graph = self.__get_graph_for_replay_refreshed__()
            else:
                self.__init_replay_handlers__()
                self._selected_row_index = selected_row_indices[0]
                self._selected_row = rows[self._selected_row_index]
                if self._selected_trade_type == TP.ONLINE:
                    graph, graph_key = self.__get_graph_for_trade_online__()
                else:
                    graph, graph_key = self.__get_graph_for_replay__()
            return graph

    def __get_graph_for_replay_refreshed__(self):
        replay_handler = self.__get_trade_handler_for_selected_trade_type__()
        if replay_handler.test_case is None:
            return ''
        if replay_handler.is_another_wave_tick_available() and not self._stop_trade:
            if self._replay_speed == 'Fast':
                for k in range(0, 4):
                    wave_tick = replay_handler.get_next_wave_tick()
                    replay_handler.check_actual_trades_for_replay(wave_tick)
            else:
                wave_tick = replay_handler.get_next_wave_tick()
                replay_handler.check_actual_trades_for_replay(wave_tick)
            replay_handler.graph = self.__get_dcc_graph_element__(replay_handler.detector, replay_handler.graph_api)
        return replay_handler.graph

    def __get_graph_for_trade_online_refreshed__(self):
        if self._trade_replay_handler_online.trade_test is None:
            return ''
        self._trade_replay_handler_online.refresh_api_df_from_pattern_trade()
        self._trade_replay_handler_online.graph_api.pattern_trade.calculate_xy_for_replay()
        return self.__get_dcc_graph_element__(None, self._trade_replay_handler_online.graph_api)

    def __get_graph_for_replay__(self):
        replay_handler = self.__get_trade_handler_for_selected_trade_type__()
        self.__adjust_selected_row_to_pattern_replay__()
        replay_handler.set_trade_test_api_by_selected_trade_row(self._selected_row)
        replay_handler.set_trade_test()
        replay_handler.set_detector()
        replay_handler.set_pattern_to_api()
        if not replay_handler.trade_test_api.pattern:
            return 'Nothing found', ''
        replay_handler.set_tick_list_to_api()
        replay_handler.set_test_case()
        replay_handler.add_pattern_list_for_trade()
        replay_handler.test_case_wave_tick_list_index = -1
        replay_handler.set_graph_api()
        self._selected_pattern_trade = replay_handler.pattern_trade
        replay_handler.graph = self.__get_dcc_graph_element__(replay_handler.detector, replay_handler.graph_api)
        return replay_handler.graph, replay_handler.graph_id

    def __get_trade_handler_for_selected_trade_type__(self):
        if self._selected_trade_type == TP.TRADE_REPLAY:
            return self._trade_replay_handler
        elif self._selected_trade_type == TP.PATTERN_REPLAY:
            return self._pattern_replay_handler
        return self._trade_handler_online

    def __adjust_selected_row_to_pattern_replay__(self):
        """
        There are differences between the rows for pattern and trades - we need trades structure
        """
        if self._selected_trade_type == TP.PATTERN_REPLAY:
            self._selected_row[DC.BUY_TRIGGER] = self._selected_buy_trigger
            self._selected_row[DC.TRADE_STRATEGY] = self._selected_trade_strategy
            self._selected_row[DC.PATTERN_RANGE_BEGIN_DT] = self._selected_row[DC.PATTERN_BEGIN_DT]
            self._selected_row[DC.PATTERN_RANGE_END_DT] = self._selected_row[DC.PATTERN_END_DT]
            print('Selected_row_after: {}'.format(self._selected_row))

    def __get_graph_for_trade_online__(self):
        self._trade_replay_handler_online.set_trade_test_api_by_selected_trade_row(self._selected_row)
        self._trade_replay_handler_online.set_trade_test()
        self._trade_replay_handler_online.set_graph_api()
        self._selected_pattern_trade = self._trade_replay_handler_online.pattern_trade
        self._trade_replay_handler_online.graph = self.__get_dcc_graph_element__(
            None, self._trade_replay_handler_online.graph_api)
        return self._trade_replay_handler_online.graph, self._trade_replay_handler_online.graph_id

    def __get_ticker_refresh_seconds__(self):
        if self._selected_trade_type == TP.TRADE_REPLAY:
            return self.exchange_config.ticker_refresh_rate_in_seconds
        else:
            return self.exchange_config.check_ticker_after_timer_intervals * \
                   self.exchange_config.ticker_refresh_rate_in_seconds

    def __get_scatter_graph_for_trades__(self, scatter_graph_id='trade_statistics_scatter_graph'):
        graph_api = DccGraphApi(scatter_graph_id, 'My Trades')
        graph_api.figure_data = self.__get_scatter_figure_data_for_trades__(self._df_trade)
        return MyDCC.graph(graph_api)

    @staticmethod
    def __get_scatter_figure_data_for_trades__(df: pd.DataFrame):
        return [
            go.Scatter(
                x=df[df['Pattern_Type'] == i]['Forecast_Full_Positive_PCT'],
                y=df[df['Pattern_Type'] == i]['Trade_Result_ID'],
                text=df[df['Pattern_Type'] == i]['Trade_Strategy'],
                mode='markers',
                opacity=0.7,
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name=i
            ) for i in df.Pattern_Type.unique()
        ]

    @staticmethod
    def __get_drop_down_for_trades__(drop_down_name='trades-selection_statistics'):
        options = [{'label': 'df', 'value': 'df'}]
        return MyDCC.drop_down(drop_down_name, options)

    def __get_table_for_trades__(self, take_cached=False):
        if take_cached and self._cached_trade_table:
            print('Returned cached trade table...')
            return self._cached_trade_table
        rows = self.__get_table_rows_for_trades__()
        if len(rows) == 0:
            rows = self.__get_empty_data_row__()
        self._cached_trade_table = MyDCC.data_table(self._data_table_name, rows, min_height=300)
        return self._cached_trade_table

    def __get_table_rows_for_trades__(self):
        if self._selected_trade_type == TP.TRADE_REPLAY:
            return self._trade_rows_for_data_table
        elif self._selected_trade_type == TP.PATTERN_REPLAY:
            return self._pattern_rows_for_data_table
        elif self._selected_trade_type == TP.ONLINE:
            return self._trade_replay_handler_online.trade_handler.get_rows_for_dash_data_table()
        return []

    @staticmethod
    def __get_empty_data_row__():
        columns = TradeTable.get_columns_for_replay()
        return [{column: '' for column in columns}]

