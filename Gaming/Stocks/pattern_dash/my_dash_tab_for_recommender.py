"""
Description: This module contains the dash tab for recommendations from various sources, e.g. bitfinex, Nasdaq...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""

from dash.dependencies import Input, Output, State
from pattern_dash.my_dash_base import MyDashBaseTab
from pattern_system_configuration import SystemConfiguration
from pattern_dash.my_dash_components import MyDCC, MyHTML, DccGraphApi
from pattern_dash.my_dash_header_tables import MyHTMLTabRecommenderHeaderTable
from pattern_dash.my_dash_tab_dd_for_recommender import RecommenderTabDropDownHandler, REDD
from pattern_detection_controller import PatternDetectionController
from pattern_trade_handler import PatternTradeHandler
from dash import Dash
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import PRD, Indices
from pattern_news_handler import NewsHandler


class RMBT:  # RecommenderManageButtonText
    SWITCH_TO_ACTIVE_MANAGEMENT = 'Start active management'
    SWITCH_TO_NO_MANAGEMENT = 'Stop active management'


class RDC:  # RecommenderDataColumn
    INDEX = 'Index'
    SYMBOL = 'Symbol'
    NAME = 'Name'
    PRICE = 'Price'
    PRICE_CHANGE = 'Change (%)'
    FIBONACCI_SHORT = 'Fib. (30min)'
    FIBONACCI_MID = 'Fib. (200d)'
    FIBONACCI_LONG = 'Fib. (400d)'
    PORTFOLIO = 'Portfolio'


class RecommenderTable:
    def __init__(self):
        self._columns = [RDC.INDEX, RDC.SYMBOL, RDC.NAME, RDC.PRICE, RDC.PRICE_CHANGE,
                         RDC.FIBONACCI_SHORT, RDC.FIBONACCI_MID, RDC.FIBONACCI_LONG, RDC.PORTFOLIO]
        self._rows_all = []
        self._selected_indices = []
        self._rows_selected_indices = []
        self._symbols = []


    @property
    def rows_selected_indices(self):
        if self.len == 0:
            return self.__get_empty_data_row__()
        return self._rows_selected_indices

    @property
    def len(self):
        return len(self._rows_selected_indices)

    @property
    def height_for_display(self):
        if self.height > 400:
            return 400
        return max(100, self.height)

    @property
    def height(self):
        return max(100, 50 + len(self._rows_selected_indices) * 40)

    @property
    def columns(self):
        return self._columns

    def set_rows_for_selected_indices(self, selected_indices: list):
        self._rows_selected_indices = [row for row in self._rows_all if row[RDC.INDEX] in selected_indices]

    def append(self, row: dict):
        self._rows_all.append(row)
        self._symbols.append(row[RDC.SYMBOL])

    def get_selected_symbol(self, row_index: int):
        return self._rows_selected_indices[row_index][RDC.SYMBOL]

    def get_selected_exchange(self, row_index: int):
        return self._rows_selected_indices[row_index][RDC.INDEX]

    def __get_empty_data_row__(self) -> list:
        return [{column: '' for column in self._columns}]

    def is_row_for_symbol_available(self, symbol: str) -> bool:
        return symbol in self._symbols


class MyDashTab4Recommender(MyDashBaseTab):
    _data_table_name = 'my_recommender_table'
    _data_table_div = '{}_div'.format(_data_table_name)

    def __init__(self, app: Dash, sys_config: SystemConfiguration, trade_handler_online: PatternTradeHandler):
        MyDashBaseTab.__init__(self, app, sys_config)
        self.sys_config = self.__get_adjusted_sys_config_copy__(sys_config)
        self.exchange_config = self.sys_config.exchange_config
        self._pattern_controller = PatternDetectionController(self.sys_config)
        self._exchange_dict = self.__get_exchange_dict__()
        self._wave_counter_dict = self.__get_wave_counter_dict__()
        self._recommender_table = RecommenderTable()
        self._active_manage_button_clicks = 0
        self._refresh_button_clicks = 0
        self._selected_row_index = -1
        self._selected_indices = []
        self._trade_handler_online = trade_handler_online
        self._dd_handler = RecommenderTabDropDownHandler()

    def __get_wave_counter_dict__(self) -> dict:
        return {200: self.sys_config.db_stock.get_wave_counter_dict(PRD.DAILY, 200),
                400: self.sys_config.db_stock.get_wave_counter_dict(PRD.DAILY, 400),
                30: self.sys_config.db_stock.get_wave_counter_dict(PRD.INTRADAY),
                }

    def __get_exchange_dict__(self) -> dict:
        index_list = [Indices.CRYPTO_CCY, Indices.DOW_JONES, Indices.NASDAQ100]
        # index_list = [Indices.DOW_JONES]
        return {index: self.sys_config.data_provider.get_index_members_as_dict(index) for index in index_list}

    @staticmethod
    def __get_adjusted_sys_config_copy__(sys_config: SystemConfiguration) -> SystemConfiguration:
        sys_config_copy = sys_config.get_semi_deep_copy()  # we need some adjustments (period, etc...)
        sys_config_copy.data_provider.from_db = False
        sys_config_copy.data_provider.period = sys_config.period
        sys_config_copy.data_provider.aggregation = sys_config.period_aggregation
        return sys_config_copy

    def __init_selected_row__(self, selected_row_indices: list=None):
        if selected_row_indices is None or len(selected_row_indices) != 1:
            self._selected_row_index = -1
        else:
            self._selected_row_index = selected_row_indices[0]

    @staticmethod
    def __get_news_handler__():
        return NewsHandler('  \n', '')

    def get_div_for_tab(self):
        children_list = [
            MyHTMLTabRecommenderHeaderTable().get_table(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(REDD.INDEX)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(
                REDD.PERIOD_AGGREGATION, default_value=self.sys_config.period_aggregation)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(
                REDD.REFRESH_INTERVAL, default_value=900)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(
                REDD.SECOND_GRAPH_RANGE)),
            MyHTML.div_with_html_button_submit('my_recommender_refresh_button', 'Refresh', hidden=''),
            MyHTML.div_with_html_button_submit('my_recommender_active_manage_button',
                                               self.__get_position_manage_button_text__()),
            MyHTML.div(self._data_table_div, self.__get_table_for_recommender__(), False),
            MyHTML.div('my_graph_recommender_position_div'),
            MyHTML.div('my_graph_recommender_position_second_div')
        ]
        return MyHTML.div('my_recommender_div', children_list)

    def init_callbacks(self):
        self.__init_callbacks_for_position_manage_button__()
        self.__init_callback_for_recommender_markdown__()
        self.__init_callback_for_recommender_table__()
        self.__init_callback_for_graph_for_selected_position__()
        self.__init_callback_for_selected_row_indices__()

    def __init_callbacks_for_position_manage_button__(self):
        @self.app.callback(
            Output('my_recommender_active_manage_button', 'hidden'),
            [Input('my_graph_recommender_position_div', 'children')])
        def handle_callback_for_position_manage_button_hidden(graph):
            if graph == '':
                return 'hidden'
            return ''

        @self.app.callback(
            Output('my_recommender_active_manage_button', 'children'),
            [Input('my_graph_recommender_position_div', 'children')])
        def handle_callback_for_position_manage_button_text(graph):
            return self.__get_position_manage_button_text__()

    def __init_callback_for_graph_for_selected_position__(self):
        @self.app.callback(
            Output('my_graph_recommender_position_div', 'children'),
            [Input(self._data_table_name, 'rows'),
             Input(self._data_table_name, 'selected_row_indices')],
            [State('my_recommender_aggregation', 'value'),
             State('my_recommender_refresh_interval_selection', 'value')])
        def handle_callback_for_graph_first(rows: list, selected_row_indices: list, aggregation: int, refresh_interval: int):
            self.__init_selected_row__(selected_row_indices)
            if self._selected_row_index == -1:
                return ''
            self.sys_config.data_provider.period = PRD.INTRADAY
            self.sys_config.data_provider.aggregation = aggregation
            selected_ticker_id = self._recommender_table.get_selected_symbol(self._selected_row_index)
            graph, graph_key = self.__get_graph__(selected_ticker_id, refresh_interval)
            return graph

        @self.app.callback(
            Output('my_graph_recommender_position_second_div', 'children'),
            [Input('my_graph_recommender_position_div', 'children')],
            [State('my_recommender_aggregation', 'value'),
             State('my_recommender_refresh_interval_selection', 'value'),
             State('my_recommender_graph_second_days_selection', 'value')])
        def handle_callback_for_graph_second(graph_first, aggregation_first: int,
                                             refresh_interval: int, range_list: list):
            if self._selected_row_index == -1 or len(range_list) == 0:
                return ''
            selected_ticker_id = self._recommender_table.get_selected_symbol(self._selected_row_index)
            graph_list = []
            sorted_range_list = sorted(range_list)
            for graph_range in sorted_range_list:
                if graph_range == 1:
                    self.sys_config.data_provider.period = PRD.INTRADAY
                    self.sys_config.data_provider.aggregation = {5: 15, 15: 30, 30: 15}.get(aggregation_first, 30)
                    graph, key = self.__get_graph__(selected_ticker_id, refresh_interval)
                else:
                    self.sys_config.data_provider.period = PRD.DAILY
                    graph, key = self.__get_graph__(selected_ticker_id, refresh_interval, graph_range)
                graph_list.append(graph)
            return graph_list

    def __init_callback_for_recommender_markdown__(self):
        @self.app.callback(
            Output('my_recommender_markdown', 'children'),
            [Input('my_position_markdown', 'children')])
        def handle_callback_for_recommender_markdown(children):
            return self.__get_recommender_markdown__()

    def __init_callback_for_recommender_table__(self):
        @self.app.callback(
            Output(self._data_table_div, 'children'),
            [Input('my_position_markdown', 'children'),
             Input('my_recommender_active_manage_button', 'n_clicks'),
             Input('my_recommender_refresh_button', 'n_clicks')],
            [State('my_recommender_index', 'value')])
        def handle_callback_for_positions_options(
                children, manage_n_clicks: int, refresh_n_clicks: int, selected_indices: list):
            self._selected_indices = selected_indices
            if manage_n_clicks > self._active_manage_button_clicks:
                self._active_manage_button_clicks = manage_n_clicks
                self.__toggle_flag_for_active_managed__()
            elif refresh_n_clicks > self._refresh_button_clicks:
                self._refresh_button_clicks = refresh_n_clicks
                self._wave_counter_dict = self.__get_wave_counter_dict__()  # update date from database
                self.__check_selected_indices__()
                self._selected_row_index = -1
            self._recommender_table.set_rows_for_selected_indices(self._selected_indices)
            return self.__get_table_for_recommender__()

    def __init_callback_for_selected_row_indices__(self):
        @self.app.callback(
            Output(self._data_table_name, 'selected_row_indices'),
            [Input(self._data_table_div, 'children')],
            [State(self._data_table_name, 'rows')])
        def handle_callback_for_selected_row_indices(children, rows):
            if self._selected_row_index == -1 or len(rows) == 0:
                return []
            return [self._selected_row_index]

    def __get_graph__(self, ticker_id: str, refresh_interval: int, limit: int=0):
        period = self.sys_config.period
        aggregation = self.sys_config.period_aggregation
        graph_cache_id = self.sys_config.graph_cache.get_cache_id(ticker_id, period, aggregation, limit)
        graph = self.sys_config.graph_cache.get_cached_object_by_key(graph_cache_id)
        if graph is not None:
            return graph, graph_cache_id

        if period == PRD.DAILY and \
                self._recommender_table.get_selected_exchange(self._selected_row_index) != Indices.CRYPTO_CCY:
            self.sys_config.data_provider.from_db = True
        else:
            self.sys_config.data_provider.from_db = False
        date_start = MyDate.adjust_by_days(MyDate.get_datetime_object().date(), -limit)
        and_clause = "Date > '{}'".format(date_start)
        graph_title = self.sys_config.graph_cache.get_cache_title(ticker_id, period, aggregation, limit)
        detector = self._pattern_controller.get_detector_for_fibonacci(self.sys_config, ticker_id, and_clause, limit)
        graph_api = DccGraphApi(graph_cache_id, graph_title)
        graph_api.ticker_id = ticker_id
        graph_api.df = detector.pdh.pattern_data.df
        graph = self.__get_dcc_graph_element__(detector, graph_api)
        cache_api = self.sys_config.graph_cache.get_cache_object_api(graph_cache_id, graph, period, refresh_interval)
        self.sys_config.graph_cache.add_cache_object(cache_api)
        return graph, graph_cache_id

    def __get_recommender_markdown__(self):
        balances = self._trade_handler_online.balances
        text_list = ['_**{}**_: {:.2f} ({:.2f}): {:.2f}$'.format(
                b.asset, b.amount, b.amount_available, b.current_value) for b in balances]
        return '  \n'.join(text_list)

    def __get_position_manage_button_text__(self) -> str:
        return RMBT.SWITCH_TO_ACTIVE_MANAGEMENT
        # if self._selected_ticker_id_management == 'Yes':
        #     return RMBT.SWITCH_TO_NO_MANAGEMENT
        # return RMBT.SWITCH_TO_ACTIVE_MANAGEMENT

    def __check_selected_indices__(self):
        for index in self._selected_indices:
            index_member_dict = self._exchange_dict[index]
            for symbol, name in index_member_dict.items():
                if not self._recommender_table.is_row_for_symbol_available(symbol):
                    row_new = self.__get_new_row_for_data_table__(index, symbol, name)
                    self._recommender_table.append(row_new)

    def __get_new_row_for_data_table__(self, index: str, symbol: str, name: str) -> dict:
        return {col: self.__get_column_value__(index, symbol, name, col) for col in self._recommender_table.columns}

    def __get_column_value__(self, index: str, symbol: str, name: str, column: str):
        if column == RDC.INDEX: return index
        elif column == RDC.SYMBOL: return symbol
        elif column == RDC.NAME: return name
        elif column == RDC.PRICE: return 0
        elif column == RDC.PRICE_CHANGE: return 0
        elif column == RDC.FIBONACCI_SHORT:
            return self.__get_fibonacci_wave_numbers_from_online__(index, symbol, 30)
        elif column == RDC.FIBONACCI_MID:
            return self.__get_fibonacci_wave_numbers_based_on_database__(index, symbol, 200)
        elif column == RDC.FIBONACCI_LONG:
            return self.__get_fibonacci_wave_numbers_based_on_database__(index, symbol, 400)
        elif column == RDC.PORTFOLIO: return 'No'

    def __get_table_for_recommender__(self):
        rows = self._recommender_table.rows_selected_indices
        min_height = self._recommender_table.height_for_display
        return MyDCC.data_table(self._data_table_name, rows, min_height=min_height)

    def __toggle_flag_for_active_managed__(self):
        pass
        # value = 'No' if self._selected_ticker_id_management == 'Yes' else 'Yes'
        # self._selected_ticker_id_management = value
        # self._table_rows[self._selected_row_index][RDC.PORTFOLIO] = value

    def __get_fibonacci_wave_numbers_based_on_database__(self, index: str, symbol: str, limit: int) -> int:
        if symbol in self._wave_counter_dict[limit]:
            return self._wave_counter_dict[limit][symbol]
        return 0

    def __get_fibonacci_wave_numbers_from_online__(self, index: str, symbol: str, aggregation: int) -> int:
        if symbol in self._wave_counter_dict[aggregation]:
            return self._wave_counter_dict[aggregation][symbol]
        return 0

