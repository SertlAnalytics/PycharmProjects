"""
Description: This module contains the dash tab for actual or back-tested trades.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-26
"""

import plotly.graph_objs as go
from sertl_analytics.constants.my_constants import DSHVT
from dash.dependencies import Input, Output, State
import pandas as pd
from pattern_dash.my_dash_base_tab_for_pattern import MyPatternDashBaseTab
from pattern_dash.my_dash_replay_handler import ReplayHandler
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.mydash.my_dash_components import MyDCC, MyHTML, DccGraphApi
from pattern_dash.my_dash_header_tables import MyHTMLTabTradeHeaderTable
from pattern_dash.my_dash_tab_dd_for_trades import TradeDropDownHandler, TDD
from pattern_dash.my_dash_tab_button_for_trades import TradingButtonHandler, TBTN
from pattern_trade_handler import PatternTradeHandler
from pattern_database.stock_tables import TradeTable, PatternTable
from dash import Dash
from sertl_analytics.constants.pattern_constants import DC, TP
from sertl_analytics.mydates import MyDate
from pattern_news_handler import NewsHandler


class MyDashTab4Trading(MyPatternDashBaseTab):
    _data_table_name = 'actual_trade_table'

    def __init__(self, app: Dash, sys_config: SystemConfiguration, trade_handler_online: PatternTradeHandler):
        MyPatternDashBaseTab.__init__(self, app, sys_config)
        self.exchange_config = self.sys_config.exchange_config
        self._trade_handler_online = trade_handler_online
        self._df_trade = self.sys_config.db_stock.get_trade_records_for_replay_as_dataframe()
        self._df_trade_for_replay = self._df_trade[TradeTable.get_columns_for_replay()]
        self._trade_rows_for_data_table = MyDCC.get_rows_from_df_for_data_table(self._df_trade_for_replay)
        self._df_pattern = self.sys_config.db_stock.get_pattern_records_for_replay_as_dataframe()
        self._df_pattern_for_replay = self._df_pattern[PatternTable.get_columns_for_replay()]
        self._pattern_rows_for_data_table = MyDCC.get_rows_from_df_for_data_table(self._df_pattern_for_replay)
        self.__init_selected_row__()
        self.__init_trade_handler_for_replay__()
        self._selected_pattern_trade = None
        self._selected_buy_trigger = None
        self._selected_trade_strategy = None
        self._n_click_restart = 0
        self._n_click_cancel_trade = 0
        self._n_click_reset = 0
        self._replay_speed = 4
        self._trades_stored_number = 0
        self._trades_online_active_number = 0
        self._trades_online_all_number = 0
        self._pattern_stored_number = 0
        self._cached_trade_table = None
        self._time_stamp_last_ticker_refresh = MyDate.time_stamp_now()

    @staticmethod
    def __get_news_handler__():
        return NewsHandler('  \n', '')

    @staticmethod
    def __get_drop_down_handler__():
        return TradeDropDownHandler()

    @staticmethod
    def __get_button_handler__():
        return TradingButtonHandler()

    def __init_selected_row__(self, trade_type=''):
        self._selected_trade_type = trade_type
        self._selected_row_index = -1
        self._selected_row = None
        self._selected_pattern_trade = None

    def __init_trade_handler_for_replay__(self):
        self._trade_replay_handler = ReplayHandler(TP.TRADE_REPLAY, self.sys_config)
        self._pattern_replay_handler = ReplayHandler(TP.PATTERN_REPLAY, self.sys_config)
        self._trade_replay_handler_online = ReplayHandler(TP.ONLINE, self.sys_config)
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
            # MyHTML.div_with_html_button_submit('my_trades_cancel_trade_button', 'Cancel Trade'),
            MyHTML.div_with_button(**self._button_handler.get_button_parameters(TBTN.CANCEL_TRADE)),
            MyHTML.div_with_button(**self._button_handler.get_button_parameters(TBTN.RESTART_REPlAY)),
            MyHTML.div_with_button(**self._button_handler.get_button_parameters(TBTN.RESET_TRADE_SELECTION)),
            # MyHTML.div_with_html_button_submit('my_replay_restart_button', 'Restart Trade'),
            MyHTML.div_with_slider('my_replay_speed_slider', 0, 20, 1, self._replay_speed, show=False),
            MyHTML.div_with_table('my_trade_table_div', self.__get_table_for_trades__()),
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
        self.__init_callback_for_cancel_trade_button__()
        self.__init_callback_for_replay_restart_button__()
        self.__init_callback_for_reset_trade_button__()
        self.__init_callback_for_replay_speed_slider_style__()
        self.__init_callback_for_replay_speed_slider_value__()
        self.__init_callback_for_graph_trade__()

    def __init_callback_for_trade_markdown__(self):
        @self.app.callback(
            Output('my_trade_markdown', DSHVT.CHILDREN),
            [Input('my_graph_trade_replay_div', DSHVT.CHILDREN),
             Input('my_interval_timer', DSHVT.N_INTERVALS)])
        def handle_callback_for_ticket_markdown(children, n_intervals: int):
            if self._selected_row_index == -1 or self._selected_pattern_trade is None:
                return ''
            ticker_refresh_seconds = self.__get_ticker_refresh_seconds__()
            ticks_remaining = self.__get_remaining_tick_number__()
            return self._selected_pattern_trade.get_markdown_text(
                self._time_stamp_last_ticker_refresh, ticker_refresh_seconds, ticks_remaining)

    def __get_remaining_tick_number__(self):
        if self._selected_trade_type != TP.ONLINE:
            return self.__get_actual_replay_handler__().get_remaining_tick_number()
        return None

    def __init_callback_for_trade_news_markdown__(self):
        @self.app.callback(
            Output('my_trade_news_markdown', DSHVT.CHILDREN),
            [Input('my_graph_trade_replay_div', DSHVT.CHILDREN),
             Input('my_interval_timer', DSHVT.N_INTERVALS)])
        def handle_callback_for_ticket_markdown(children, n_intervals: int):
            if self._selected_row_index == -1 or self._selected_pattern_trade is None:
                return ''
            return self.__get_markdown_news__()

    def __get_markdown_news__(self):
        actual_replay_handler = self.__get_actual_replay_handler__()
        # collecting all news from dependent sources
        if actual_replay_handler is None:
            return ''
        if actual_replay_handler.pattern_trade is None:
            return ''
        self._news_handler.add_news_dict(actual_replay_handler.pattern_trade.news_handler.news_dict)
        self._news_handler.add_news_dict(actual_replay_handler.trade_handler.news_handler.news_dict)
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
            Output('my_online_trade_all_div', DSHVT.CHILDREN),
            [Input('my_interval_timer', DSHVT.N_INTERVALS)])
        def handle_callback_for_online_trade_all_numbers(n_intervals: int):
            return str(self._trade_replay_handler_online.trade_handler.trade_numbers)

        @self.app.callback(
            Output('my_online_trade_active_div', DSHVT.CHILDREN),
            [Input('my_interval_timer', DSHVT.N_INTERVALS)])
        def handle_callback_for_online_trade_active_numbers(n_intervals: int):
            return str(self._trade_replay_handler_online.trade_handler.trade_numbers_active)

        @self.app.callback(
            Output('my_stored_trade_div', DSHVT.CHILDREN),
            [Input('my_interval_refresh', DSHVT.N_INTERVALS)])
        def handle_callback_for_stored_trade_numbers(n_intervals: int):
            return str(len(self._trade_rows_for_data_table))

        @self.app.callback(
            Output('my_stored_pattern_div', DSHVT.CHILDREN),
            [Input('my_interval_refresh', DSHVT.N_INTERVALS)])
        def handle_callback_for_stored_pattern_numbers(n_intervals: int):
            return str(len(self._pattern_rows_for_data_table))

        @self.app.callback(
            Output('my_real_online_trade_div', DSHVT.CHILDREN),
            [Input('my_interval_timer', DSHVT.N_INTERVALS)])
        def handle_callback_for_real_online_trade_numbers(n_intervals: int):
            return self._trade_replay_handler_online.trade_handler.get_real_trade_numbers_active_for_dashboard()

        @self.app.callback(
            Output('my_simulation_online_trade_div', DSHVT.CHILDREN),
            [Input('my_interval_timer', DSHVT.N_INTERVALS)])
        def handle_callback_for_simulation_online_trade_numbers(n_intervals: int):
            return self._trade_replay_handler_online.trade_handler.get_simulation_trade_numbers_active_for_dashboard()

    def __init_callback_for_trade_table__(self):
        @self.app.callback(
            Output('my_trade_table_div', DSHVT.CHILDREN),
            [Input('my_trade_type_selection', DSHVT.VALUE),
             Input('my_trades_cancel_trade_button', DSHVT.N_CLICKS),
             Input('my_trades_reset_button', DSHVT.N_CLICKS),
             Input('my_interval_timer', DSHVT.N_INTERVALS)],
            [State('my_online_trade_active_div', DSHVT.CHILDREN),
             State('my_online_trade_all_div', DSHVT.CHILDREN),
             State('my_stored_trade_div', DSHVT.CHILDREN),
             State('my_stored_pattern_div', DSHVT.CHILDREN)
             ])
        def handle_callback_for_trade_table(trade_type: str, cancel_n_clicks: int, n_clicks_reset: int,
                                            n_intervals: int,
                                            online_active: int, online_all: int, trades: int, pattern: int):
            if n_clicks_reset != self._n_click_reset:
                self._n_click_reset = n_clicks_reset
                self._selected_row_index = -1
                self.__get_table_for_trades__()
            elif self._selected_trade_type != trade_type:
                self._trades_online_active_number = online_active
                self._trades_online_all_number = online_all
                self._trades_stored_number = trades
                self._pattern_stored_number = pattern
                self.__init_selected_row__(trade_type)
                self.__init_trade_handler_for_replay__()
                return self.__get_table_for_trades__()
            elif self._selected_trade_type == TP.ONLINE and self._n_click_cancel_trade != cancel_n_clicks:
                self._n_click_cancel_trade = cancel_n_clicks
                pattern_trade_id = self._selected_row[DC.ID]
                self._trade_handler_online.remove_trade_from_dash_data_table(pattern_trade_id)
                self.__init_selected_row__(trade_type)
                return self.__get_table_for_trades__()
            elif self._selected_trade_type == TP.ONLINE: # we refresh each time (since we calculate the result...
                    # and \
                    # (self._trades_online_active_number != online_active or self._trades_online_all_number != online_all):
                self._trades_online_active_number = online_active
                self._trades_online_all_number = online_all
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
            Output('my_trade_ticker_div', DSHVT.CHILDREN),
            [Input('my_graph_trade_replay_div', DSHVT.CHILDREN)])
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
            Output(self._data_table_name, DSHVT.SELECTED_ROW_INDICES),
            [Input(self._data_table_name, DSHVT.ROWS)])
        def handle_callback_for_selected_row_indices(rows):
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
            Output('my_replay_restart_button_div', DSHVT.STYLE),
            [Input('my_trade_type_selection', DSHVT.VALUE),
             Input(self._data_table_name, DSHVT.SELECTED_ROW_INDICES),
             Input('my_pattern_buy_trigger_selection', DSHVT.VALUE),
             Input('my_pattern_trade_strategy_selection', DSHVT.VALUE)])
        def handle_callback_for_replay_restart_button(
                trade_type: str, selected_row_indices: list, buy_trigger: str, trade_strategy: str):
            if trade_type in [TP.TRADE_REPLAY, TP.PATTERN_REPLAY] and \
                    selected_row_indices is not None and len(selected_row_indices) > 0:
                style_show = self._button_handler.get_style_display(TBTN.RESTART_REPlAY)
                if self._selected_buy_trigger != buy_trigger:
                    self._selected_buy_trigger = buy_trigger
                    return style_show
                elif self._selected_trade_strategy != trade_strategy:
                    self._selected_trade_strategy = trade_strategy
                    return style_show
            return {'display': 'none'}

    def __init_callback_for_cancel_trade_button__(self):
        @self.app.callback(
            Output('my_trades_cancel_trade_button_div', DSHVT.STYLE),
            [Input('my_trade_type_selection', DSHVT.VALUE),
             Input(self._data_table_name, DSHVT.SELECTED_ROW_INDICES)],
            [State(self._data_table_name, DSHVT.ROWS)])
        def handle_callback_for_trades_remove_button(trade_type: str, selected_row_indices: list, rows: list):
            if trade_type == TP.ONLINE and selected_row_indices is not None \
                    and len(selected_row_indices) > 0 and len(rows) > 0:
                return self._button_handler.get_style_display(TBTN.CANCEL_TRADE)
            return {'display': 'none'}

    def __init_callback_for_reset_trade_button__(self):
        @self.app.callback(
            Output('my_trades_reset_button_div', DSHVT.STYLE),
            [Input('my_trade_type_selection', DSHVT.VALUE),
             Input(self._data_table_name, DSHVT.SELECTED_ROW_INDICES)],
            [State(self._data_table_name, DSHVT.ROWS)])
        def handle_callback_for_trades_reset_button(trade_type: str, selected_row_indices: list, rows: list):
            if trade_type == TP.ONLINE and selected_row_indices is not None \
                    and len(selected_row_indices) > 0 and len(rows) > 0:
                return self._button_handler.get_style_display(TBTN.RESET_TRADE_SELECTION)
            return {'display': 'none'}

    def __init_callback_for_replay_speed_slider_style__(self):
        @self.app.callback(
            Output('my_replay_speed_slider_div', DSHVT.STYLE),
            [Input(self._data_table_name, DSHVT.SELECTED_ROW_INDICES),
             Input('my_trade_type_selection', DSHVT.VALUE)])
        def handle_callback_for_speed_slider_style(selected_row_indices: list, trade_type: str):
            if trade_type in [TP.TRADE_REPLAY, TP.PATTERN_REPLAY] \
                    and selected_row_indices is not None and len(selected_row_indices) > 0:
                return {'width': '20%', 'display': 'inline-block', 'vertical-align': 'bottom',
                        'padding-bottom': 20, 'padding-left': 10}
            else:
                return {'display': 'none'}

    def __init_callback_for_replay_speed_slider_value__(self):
        @self.app.callback(
            Output('my_replay_speed_slider', DSHVT.CHILDREN),
            [Input('my_replay_speed_slider', DSHVT.VALUE)])
        def handle_callback_for_speed_slider_value(value: float):
            self._replay_speed = value
            return value

    def __handle_trade_type_selection__(self, trade_type: str):
        if trade_type != self._selected_trade_type:
            self._selected_trade_type = trade_type
            self._cached_trade_table = None
            self.__init_selected_row__(trade_type)

    def __handle_trade_restart_selection__(self, n_clicks_restart: int):
        if n_clicks_restart != self._n_click_restart:
            self._n_click_restart = n_clicks_restart
            self.__init_selected_row__(self._selected_trade_type)

    def __init_callback_for_graph_trade__(self):
        @self.app.callback(
            Output('my_graph_trade_replay_div', DSHVT.CHILDREN),
            [Input(self._data_table_name, DSHVT.ROWS),
             Input(self._data_table_name, DSHVT.SELECTED_ROW_INDICES),
             Input('my_interval_timer', DSHVT.N_INTERVALS),
             Input('my_trade_type_selection', DSHVT.VALUE),
             Input('my_replay_restart_button', DSHVT.N_CLICKS)],
            [State('my_pattern_buy_trigger_selection', DSHVT.VALUE),
             State('my_pattern_trade_strategy_selection', DSHVT.VALUE)])
        def handle_callback_for_graph_trade(rows: list, selected_row_indices: list, n_intervals: int,
                                            trade_type: str, n_click_restart: int,
                                            buy_trigger: str, trade_strategy: str):
            self._time_stamp_last_refresh = MyDate.time_stamp_now()
            self.__handle_trade_type_selection__(trade_type)
            self.__handle_trade_restart_selection__(n_click_restart)
            self._selected_buy_trigger = buy_trigger
            self._selected_trade_strategy = trade_strategy
            self.__check_actual_trades_for_trade_handler_online__(n_intervals)
            if selected_row_indices is None or len(selected_row_indices) == 0:
                self._selected_row_index = -1
                return ''
            if self._selected_row_index == selected_row_indices[0]:
                if self._selected_trade_type == TP.ONLINE:
                    graph = self.__get_graph_for_trade_online_refreshed__(n_intervals)
                else:
                    graph = self.__get_graph_for_replay_refreshed__()
            else:
                self.__init_trade_handler_for_replay__()
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
        if self._replay_speed > 0:
            for k in range(0, self._replay_speed):
                if replay_handler.is_another_wave_tick_available():
                    wave_tick = replay_handler.get_next_wave_tick()
                    replay_handler.check_actual_trades_for_replay(wave_tick)
                else:
                    break
            replay_handler.graph = self.__get_dcc_graph_element__(replay_handler.detector, replay_handler.graph_api)
        return replay_handler.graph

    def __get_graph_for_trade_online_refreshed__(self, n_intervals: int):
        if self._trade_replay_handler_online.trade_test is None:
            return ''
        self._trade_replay_handler_online.refresh_api_df_from_pattern_trade()
        self._trade_replay_handler_online.graph_api.pattern_trade.calculate_wave_tick_values_for_trade_subprocess()
        self._trade_replay_handler_online.graph_api.pattern_trade.calculate_xy_for_replay()
        return self.__get_dcc_graph_element__(None, self._trade_replay_handler_online.graph_api)

    def __check_actual_trades_for_trade_handler_online__(self, n_intervals: int):
        if self._selected_trade_type == TP.ONLINE:
            if n_intervals % self.exchange_config.check_ticker_after_timer_intervals == 0:
                self._time_stamp_last_ticker_refresh = MyDate.get_epoch_seconds_from_datetime()
                self.trade_handler_online.check_actual_trades()

    def __get_graph_for_replay__(self):
        replay_handler = self.__get_trade_handler_for_selected_trade_type__()
        self.__adjust_selected_pattern_row_to_trade_row__()
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

    def __adjust_selected_pattern_row_to_trade_row__(self):
        """
        There are differences between the rows for pattern and trades - we need trades structure
        """
        if self._selected_trade_type == TP.TRADE_REPLAY:
            self._selected_row[DC.TRADE_ID] = self._selected_row[DC.ID]
            self._selected_row[DC.PATTERN_ID] = self.sys_config.db_stock.get_pattern_id_for_trade_id(
                self._selected_row[DC.TRADE_ID]
            )
        elif self._selected_trade_type == TP.PATTERN_REPLAY:
            self._selected_row[DC.TRADE_ID] = ''
            self._selected_row[DC.PATTERN_ID] = self._selected_row[DC.ID]
            self._selected_row[DC.BUY_TRIGGER] = self._selected_buy_trigger
            self._selected_row[DC.TRADE_STRATEGY] = self._selected_trade_strategy
            self._selected_row[DC.PATTERN_RANGE_BEGIN_DT] = self._selected_row[DC.PATTERN_BEGIN_DT]
            self._selected_row[DC.PATTERN_RANGE_END_DT] = self._selected_row[DC.PATTERN_END_DT]

    def __get_trade_handler_for_selected_trade_type__(self):
        if self._selected_trade_type == TP.TRADE_REPLAY:
            return self._trade_replay_handler
        elif self._selected_trade_type == TP.PATTERN_REPLAY:
            return self._pattern_replay_handler
        return self._trade_handler_online

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
        options = [{'label': '_df', 'value': '_df'}]
        return MyDCC.drop_down(drop_down_name, options)

    def __get_table_for_trades__(self, take_cached=False):
        selected_row_indices = [] if self._selected_row_index == -1 else [self._selected_row_index]
        if take_cached and self._cached_trade_table is not None:
            self._cached_trade_table.selected_row_indices = selected_row_indices
            return self._cached_trade_table
        rows = self.__get_table_rows_for_trades__()
        if len(rows) == 0:
            rows = self.__get_empty_data_row__()
        self._cached_trade_table = MyDCC.data_table(
            self._data_table_name,
            rows=rows,
            selected_row_indices=selected_row_indices,
            style_data_conditional=TradeTable.get_table_style_data_conditional(),
            columns=self.__get_columns_for_trading_table__())
        return self._cached_trade_table

    def __get_table_rows_for_trades__(self):
        if self._selected_trade_type == TP.TRADE_REPLAY:
            return self._trade_rows_for_data_table
        elif self._selected_trade_type == TP.PATTERN_REPLAY:
            return self._pattern_rows_for_data_table
        elif self._selected_trade_type == TP.ONLINE:
            return self._trade_replay_handler_online.trade_handler.get_rows_for_dash_data_table()
        return []

    def __get_empty_data_row__(self):
        columns = self.__get_columns_for_trading_table__()
        return [{column: '' for column in columns}]

    def __get_columns_for_trading_table__(self):
        if self._selected_trade_type in [TP.ONLINE, '']:
            return TradeTable.get_columns_for_online_trades()
        else:
            return TradeTable.get_columns_for_replay()

