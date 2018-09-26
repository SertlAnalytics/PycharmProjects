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
from dash import Dash
from sertl_analytics.constants.pattern_constants import DC, TP
from pattern_detection_controller import PatternDetectionController
from pattern_test.trade_test_cases import TradeTestCase, TradeTestCaseFactory, TradeTestApi
from pattern_test.trade_test_cases import TradeTestCase


class MyDashTab4Trades(MyDashBaseTab):
    def __init__(self, app: Dash, sys_config: SystemConfiguration, exchange_config: ExchangeConfiguration):
        MyDashBaseTab.__init__(self, app, sys_config)
        self.exchange_config = exchange_config
        self.trade_handler = PatternTradeHandler(sys_config, exchange_config)
        self._df_trade_records = self.sys_config.db_stock.get_trade_records_for_replay_as_dataframe()
        self._trade_rows_for_data_table = MyDCC.get_rows_from_df_for_data_table(self._df_trade_records)

    def init_callbacks(self):
        print('init callback...')
        self.__init_callback_for_trade_selection__()

    def __init_callback_for_trade_selection__(self):
        @self.app.callback(
            Output('my_temp_result_div', 'children'),
            [Input('actual_trade_table', 'selected_row_indices')])
        def handle_callback_for_trade_selection(selected_row_indices: list):
            if len(selected_row_indices) == 0:
                return
            self.__handle_selected_trade__(selected_row_indices[0])
            return 'Test'

    def __handle_selected_trade__(self, selected_row_index: int):
        api = self.__get_trade_test_api_by_selected_row_index__(selected_row_index)
        api.print_test_api()
        api.pattern = self.__get_pattern_for_replay__(api)
        if not api.pattern:
            return
        tc = TradeTestCaseFactory.get_test_case_from_pattern(api)
        print('tc.pattern_type={}, tc.value_pair_list={}'.format(tc.pattern_type, tc.value_pair_list))
        # trade_handler = PatternTradeHandler(self.sys_config, self.exchange_config)
        # trade_handler.add_pattern_list_for_trade([api.pattern])
        # for value_pair in tc.value_pair_list:
        #     trade_handler.check_actual_trades(value_pair)

    def __get_trade_test_api_by_selected_row_index__(self, selected_row_index: int) -> TradeTestApi:
        row = self._df_trade_records.iloc[selected_row_index]
        api = TradeTestApi()
        api.test_process = TP.TRADE_REPLAY
        api.pattern_type = row[DC.PATTERN_TYPE]
        self.sys_config.config.pattern_type_list = [api.pattern_type]
        self.sys_config.config.save_trade_data = False
        api.buy_trigger = row[DC.BUY_TRIGGER]
        api.trade_strategy = row[DC.TRADE_STRATEGY]
        api.symbol = row[DC.TICKER_ID]
        dt_start = str(row[DC.PATTERN_BEGIN_DT])
        dt_end = str(row[DC.PATTERN_END_DT])
        api.and_clause = self.sys_config.config.get_and_clause(dt_start, dt_end)
        return api

    def __get_pattern_for_replay__(self, api: TradeTestApi):
        pattern_controller = PatternDetectionController(self.sys_config)
        detector = pattern_controller.get_detector_for_dash(self.sys_config, api.symbol, api.and_clause)
        return detector.get_pattern_for_replay()

    def get_div_for_tab(self):
        header = MyHTML.h2('This is the content in tab 2: Trade data - from back testing and online trades')
        paragraph = MyHTML.p('A graph here would be nice!')
        drop_down = self.__get_drop_down_for_trades__('trades-selection')
        table = self.__get_table_for_trades__('actual_trade_table', 3)
        temp_result_div = MyHTML.div('my_temp_result_div', '', False)
        # scatter_graph = self.__get_scatter_graph_for_trades__('trade_scatter_graph')
        return MyHTML.div('my_trades', [header, paragraph, drop_down, table, temp_result_div])

    def __get_scatter_graph_for_trades__(self, scatter_graph_id='trade_statistics_scatter_graph'):
        graph_api = DccGraphApi(scatter_graph_id, 'My Trades')
        graph_api.figure_data = self.__get_scatter_figure_data_for_trades__(self._df_trade_records)
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
