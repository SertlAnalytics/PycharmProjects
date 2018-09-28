"""
Description: This module contains the dash tab for actual or back-tested trades.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-26
"""

import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
from pattern_dash.my_dash_base import MyDashBase, MyDashBaseTab
from pattern_system_configuration import SystemConfiguration
from pattern_dash.my_dash_components import MyDCC, MyHTML, DccGraphApi
from sertl_analytics.exchanges.exchange_cls import ExchangeConfiguration
from pattern_trade_handler import PatternTradeHandler
from pattern_database.stock_tables import TradeTable
from pattern_database.stock_database import StockDatabaseDataFrame
from dash import Dash
from sertl_analytics.constants.pattern_constants import DC, TP
from pattern_test.trade_test_cases import TradeTestCaseFactory
from pattern_test.trade_test import TradeTest, TradeTestApi
from pattern_dash.my_dash_tools import MyGraphCache, MyDashStateHandler, MyGraphCacheObjectApi
from pattern_data_container import PatternData


class MyDashTab4Trades(MyDashBaseTab):
    def __init__(self, app: Dash, sys_config: SystemConfiguration, exchange_config: ExchangeConfiguration):
        MyDashBaseTab.__init__(self, app, sys_config)
        self.sys_config.runtime.actual_trade_process = TP.TRADE_REPLAY
        self.exchange_config = exchange_config
        self.trade_handler = PatternTradeHandler(sys_config, exchange_config)
        self._df_trade = self.sys_config.db_stock.get_trade_records_for_replay_as_dataframe()
        self._df_trade_for_replay = self._df_trade[TradeTable.get_columns_for_replay()]
        self._trade_rows_for_data_table = MyDCC.get_rows_from_df_for_data_table(self._df_trade_for_replay)
        self._trade_test = TradeTest(TP.TRADE_REPLAY, self.sys_config, self.exchange_config)
        self._selected_row_index = -1
        self._detector_for_replay = None
        self._graph_api_for_replay = None
        self._trade_handler_for_replay = None
        self._test_case_for_replay = None
        self._test_case_value_pair_index = -1
        self._graph_for_replay = None

    def init_callbacks(self):
        self.__init_callback_for_trade_selection__()
        self.__init_callback_for_graph_trade_replay__()

    def __init_callback_for_trade_selection__(self):
        @self.app.callback(
            Output('my_temp_result_div', 'children'),
            [Input('actual_trade_table', 'selected_row_indices')])
        def handle_callback_for_trade_selection(selected_row_indices: list):
            if len(selected_row_indices) == 0:
                return ''
            return self.__handle_selected_trade__(selected_row_indices[0])

    def __init_callback_for_graph_trade_replay__(self):
        @self.app.callback(
            Output('my_graph_trade_replay_div', 'children'),
            [Input('actual_trade_table', 'selected_row_indices'),
             Input('my_interval_timer', 'n_intervals')])
        def handle_callback_for_graph_trade_replay(selected_row_indices: list, n_intervals: int):
            print('selected_row_indices={}'.format(selected_row_indices))
            if len(selected_row_indices) == 0:
                self._selected_row_index = -1
                return ''
            current_selected_row_index = selected_row_indices[0]
            if self._selected_row_index == current_selected_row_index:
                if self._test_case_for_replay is None:
                    return ''
                graph = self.__get_graph_trade_replay_refreshed__()
                print('handle_callback_for_graph_trade_replay...: get_refreshed graph')
            else:
                self._selected_row_index = current_selected_row_index
                graph, graph_key = self.__get_graph_trade_replay__(current_selected_row_index)
                print('handle_callback_for_graph_trade_replay...: get_new_graph')
            return graph

    def __get_graph_trade_replay_refreshed__(self):
        if self._test_case_value_pair_index < len(self._test_case_for_replay.value_pair_list) - 1:
            self._test_case_value_pair_index += 1
            value_pair = self._test_case_for_replay.value_pair_list[self._test_case_value_pair_index]
            print('New value pair to check: {}'.format(value_pair))
            self._trade_handler_for_replay.check_actual_trades_for_replay(value_pair)
            self._graph_api_for_replay.df = self._trade_handler_for_replay.get_pattern_trade_data_frame_for_replay()
            return self.__get_dcc_graph_element__(self._detector_for_replay, self._graph_api_for_replay)
        return self._graph_for_replay

    def __get_graph_trade_replay__(self, selected_row_index: int):
        graph_id = 'my_graph_trade_reply'
        trade_test_api = self.__get_trade_test_api_for_selected_row_index__(selected_row_index)
        graph_title = '{} {}'.format(trade_test_api.symbol, self.sys_config.config.api_period)
        graph_key = MyGraphCache.get_cache_key(graph_id, trade_test_api.symbol, 0)
        self._detector_for_replay = self._trade_test.get_pattern_detector_for_replay(trade_test_api)
        trade_test_api.pattern = self._detector_for_replay.get_pattern_for_replay()
        if not trade_test_api.pattern:
            return 'Nothing found', ''
        trade_test_api.tick_list_for_replay = self.__get_tick_list_for_replay__(trade_test_api)
        self._test_case_for_replay = TradeTestCaseFactory.get_test_case_from_pattern(trade_test_api)
        self._trade_handler_for_replay = PatternTradeHandler(self.sys_config, self.exchange_config)
        self._trade_handler_for_replay.add_pattern_list_for_trade([trade_test_api.pattern])
        self._test_case_value_pair_index = -1
        self._graph_api_for_replay = DccGraphApi(graph_id, graph_title)
        self._graph_api_for_replay.pattern_trade = self._trade_handler_for_replay.pattern_trade_for_replay
        self._graph_api_for_replay.ticker_id = trade_test_api.symbol
        self._graph_api_for_replay.df = self._detector_for_replay.sys_config.pdh.pattern_data.df
        self._graph_for_replay = self.__get_dcc_graph_element__(self._detector_for_replay, self._graph_api_for_replay)
        return self._graph_for_replay, graph_key

    def __get_tick_list_for_replay__(self, api: TradeTestApi):
        stock_db_df_obj = StockDatabaseDataFrame(self.sys_config.db_stock, api.symbol, api.and_clause_unlimited)
        pattern_data = PatternData(self.sys_config.config, stock_db_df_obj.df_data)
        return pattern_data.tick_list

    def __handle_selected_trade__(self, selected_row_index: int):
        api = self.__get_trade_test_api_for_selected_row_index__(selected_row_index)
        detector = self._trade_test.get_pattern_detector_for_replay(api)
        api.pattern = detector.get_pattern_for_replay()
        if not api.pattern:
            return
        tc = TradeTestCaseFactory.get_test_case_from_pattern(api)
        return 'tc.pattern_type={}, tc.value_pair_list={}'.format(tc.pattern_type, tc.value_pair_list)
        # trade_handler = PatternTradeHandler(self.sys_config, self.exchange_config)
        # trade_handler.add_pattern_list_for_trade([api.pattern])
        # for value_pair in tc.value_pair_list:
        #     trade_handler.check_actual_trades(value_pair)

    def __get_trade_test_api_for_selected_row_index__(self, selected_row_index: int) -> TradeTestApi:
        row = self._df_trade.iloc[selected_row_index]
        return self._trade_test.get_trade_test_api_by_selected_trade_row(row)

    def __get_pattern_detector_by_trade_test_api__(self, api: TradeTestApi):
        return self._trade_test.get_pattern_detector_for_replay(api)

    def get_div_for_tab(self):
        header = MyHTML.h2('This is the content in tab 2: Trade data - from back testing and online trades')
        paragraph = MyHTML.p('A graph here would be nice!')
        drop_down = self.__get_drop_down_for_trades__('trades-selection')
        table = self.__get_table_for_trades__('actual_trade_table', 3)
        temp_result_div = MyHTML.div('my_temp_result_div', '', False)
        graph_reply = MyHTML.div('my_graph_trade_replay_div', '', False)
        # scatter_graph = self.__get_scatter_graph_for_trades__('trade_scatter_graph')
        return MyHTML.div('my_trades', [header, paragraph, drop_down, table, graph_reply, temp_result_div])

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

    def __get_table_for_trades__(self, table_name='trade_table', number=5):
        return MyDCC.data_table(table_name, self._trade_rows_for_data_table[:number], min_height=200)
