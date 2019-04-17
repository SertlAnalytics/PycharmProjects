"""
Description: This module contains the dash tab for recommendations from various sources, e.g. bitfinex, Nasdaq...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""

from dash.dependencies import Input, Output, State
from sertl_analytics.mydash.my_dash_base_tab import MyDashBaseTab
from sertl_analytics.mydash.my_dash_components import MyDCC, MyHTML, DccGraphApi
from salesman_dash.header_tables.my_dash_header_tables import MyHTMLTabRecommenderHeaderTable
from salesman_dash.input_tables.my_online_sale_table import MyHTMLSaleOnlineInputTable
from salesman_dash.my_dash_tab_dd_for_sales import SalesTabDropDownHandler, SLDD
from dash import Dash
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import PRD, INDICES
from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_dash.grid_tables.my_grid_table_sale_4_sales import MySaleTable
from salesman_dash.grid_tables.my_grid_table_similar_sale_4_sales import MySimilarSaleTable
from salesman_system_configuration import SystemConfiguration


class MyDashTab4Sales(MyDashBaseTab):
    _data_table_name = 'my_sales_grid_table'
    _data_table_div = '{}_div'.format(_data_table_name)

    def __init__(self, app: Dash, sys_config: SystemConfiguration):
        MyDashBaseTab.__init__(self, app)
        self.sys_config = sys_config
        self._refresh_button_clicks = 0
        self._dd_handler = SalesTabDropDownHandler()
        self._sale_grid_table = MySaleTable(self.sys_config)
        self._similar_sale_grid_table = MySimilarSaleTable(self.sys_config)
        self._sale_online_input_table = MyHTMLSaleOnlineInputTable()

    def __init_dash_element_ids__(self):
        self._my_sales_refresh_button = 'my_sales_refresh_button'
        self._my_sales_active_manage_button = 'my_sales_active_manage_button'
        self._my_sales_graph_div = 'my_sales_graph_div'
        self._my_sales_div = 'my_sales_div'
        self._my_sales_sale_entry_markdown = 'my_sales_sale_entry_markdown'
        self._my_sales_similar_sale_grid_table = 'my_sales_similar_sale_grid_table'
        self._my_sales_similar_sale_entry_markdown = 'my_sales_similar_sale_entry_markdown'
        self._my_sales_similar_sale_grid_table_div = '{}_div'.format(self._my_sales_similar_sale_grid_table)
        self._my_sales_online_input_table = 'my_sales_online_input_table'
        self._my_sales_online_input_table_div = '{}_div'.format(self._my_sales_online_input_table)

    def get_div_for_tab(self):
        children_list = [
            MyHTMLTabRecommenderHeaderTable().get_table(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SLDD.MY_SALE_SOURCE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SLDD.SIMILAR_SALE_SOURCE)),
            MyHTML.div_with_html_button_submit(self._my_sales_refresh_button, 'Refresh', hidden=''),
            MyHTML.div_with_html_element(self._my_sales_online_input_table, self._sale_online_input_table.get_table()),
            MyHTML.div(self._data_table_div, self.__get_sale_grid_table__(), False),
            MyDCC.markdown(self._my_sales_sale_entry_markdown),
            MyHTML.div(self._my_sales_similar_sale_grid_table_div, self.__get_similar_sale_grid_table__(''), False),
            MyDCC.markdown(self._my_sales_similar_sale_entry_markdown),
            MyHTML.div(self._my_sales_graph_div),
        ]
        return MyHTML.div(self._my_sales_div, children_list)

    def init_callbacks(self):
        # self.__init_callbacks_for_position_manage_button__()
        # self.__init_callback_for_sales_markdown__()
        self.__init_callback_for_sale_grid_table__()
        self.__init_callback_for_similar_sale_grid_table__()
        self.__init_callback_for_sale_entry_markdown__()
        self.__init_callback_for_similar_sale_entry_markdown__()
        self.__init_callback_for_online_input_table_visibility__()
        # self.__init_callback_for_graph_for_selected_position__()
        # self.__init_callback_for_selected_row_indices__()

    def __init_callback_for_sale_grid_table__(self):
        @self.app.callback(
            Output(self._data_table_div, 'children'),
            [Input(self._dd_handler.my_sales_sales_source_dd, 'value'),
             Input(self._my_sales_refresh_button, 'n_clicks')]
            )
        def handle_callback_for_sale_grid_table(sale_source: str, refresh_n_clicks: int):
            self._dd_handler.selected_sale_source = sale_source
            self._sale_grid_table.selected_source = sale_source
            self.__handle_refresh_click__(refresh_n_clicks)
            if self._dd_handler.selected_sale_source == SLSRC.ONLINE:
                pass
            return self.__get_sale_grid_table__()

    def __handle_refresh_click__(self, refresh_n_clicks: int):
        if self._refresh_button_clicks == refresh_n_clicks:
            return
        self._refresh_button_clicks = refresh_n_clicks
        self._sale_grid_table = MySaleTable(self.sys_config)
        self._similar_sale_grid_table = MySimilarSaleTable(self.sys_config)

    def __init_callback_for_similar_sale_grid_table__(self):
        @self.app.callback(
            Output(self._my_sales_similar_sale_grid_table_div, 'children'),
            [Input(self._dd_handler.my_sales_similar_sales_source_dd, 'value'),
             Input(self._my_sales_refresh_button, 'n_clicks'),
             Input(self._data_table_name, 'rows'),
             Input(self._data_table_name, 'selected_row_indices'),
             Input(self._sale_online_input_table.my_sales_online_search_button, 'n_clicks')
             ],
            [State(self._sale_online_input_table.my_sales_title_input, 'value'),
             State(self._sale_online_input_table.my_sales_description_input, 'value')]
        )
        def handle_callback_for_similar_sale_grid_table(
                similar_sale_source: str,
                refresh_n_clicks: int,
                rows: list,
                selected_row_indices: list,
                search_n_clicks: int,
                title: str,
                description: str):
            print('handle_callback_for_similar_sale_grid_table')
            self._dd_handler.selected_similar_sale_source = similar_sale_source
            if self._dd_handler.selected_sale_source == SLSRC.ONLINE:
                if self._dd_handler.selected_similar_sale_source == SLSRC.DB:
                    return ''
                if self._sale_online_input_table.button_n_clicks != search_n_clicks:
                    self._sale_online_input_table.button_n_clicks = search_n_clicks
                    print('n_clicks={}, title={}'.format(search_n_clicks, title))
                    return self.__get_similar_sale_grid_table_by_online_search__(title, description)
                return ''
            if len(selected_row_indices) == 0 or len(rows) == len(selected_row_indices) != 1:
                self._sale_grid_table.reset_selected_row()
                return ''
            selected_row = rows[selected_row_indices[0]]
            sale_id = selected_row[SLDC.SALE_ID]
            self._similar_sale_grid_table.selected_source = similar_sale_source
            return self.__get_similar_sale_grid_table__(sale_id)

    def __init_callback_for_sale_entry_markdown__(self):
        @self.app.callback(
            Output(self._my_sales_sale_entry_markdown, 'children'),
            [Input(self._data_table_name, 'selected_row_indices')],
            [State(self._data_table_name, 'rows')])
        def handle_callback_for_sale_entry_markdown(selected_row_indices: list, rows: list):
            if len(selected_row_indices) == 0 or len(rows) == len(selected_row_indices) != 1:
                self._sale_grid_table.reset_selected_row()
                return ''
            self._sale_grid_table.selected_row = rows[selected_row_indices[0]]
            column_value_list = ['_**{}**_: {}'.format(
                col, self._sale_grid_table.selected_row[col]) for col in self._sale_grid_table.columns]
            return '  \n'.join(column_value_list)

    def __init_callback_for_similar_sale_entry_markdown__(self):
        @self.app.callback(
            Output(self._my_sales_similar_sale_entry_markdown, 'children'),
            [Input(self._my_sales_similar_sale_grid_table, 'selected_row_indices'),
             Input(self._my_sales_sale_entry_markdown, 'children')],
            [State(self._my_sales_similar_sale_grid_table, 'rows')]
        )
        def handle_callback_similar_sale_entry_markdown(selected_row_indices: list, children, rows):
            if len(selected_row_indices) == 0 or len(rows) == len(selected_row_indices) != 1 or len(children) == 0:
                return ''
            selected_row = rows[selected_row_indices[0]]
            column_value_list = ['_**{}**_: {}'.format(col, selected_row[col])
                                 for col in self._similar_sale_grid_table.columns]
            return '  \n'.join(column_value_list)

    def __init_callback_for_selected_row_indices__(self):
        @self.app.callback(
            Output(self._data_table_name, 'selected_row_indices'),
            [Input(self._data_table_div, 'children')],
            [State(self._data_table_name, 'rows')])
        def handle_callback_for_selected_row_indices(children, rows):
            if self._sale_grid_table.selected_row_index == -1 or len(rows) == 0:
                return []
            return [self._sale_grid_table.selected_row_index]

    def __init_callback_for_online_input_table_visibility__(self):
        @self.app.callback(
            Output(self._my_sales_online_input_table_div, 'style'),
            [Input(self._dd_handler.my_sales_sales_source_dd, 'value')])
        def handle_callback_for_online_input_table_visibility(sale_source: str):
            if sale_source == SLSRC.ONLINE:
                return {'width': '1225px', 'display': 'inline-block'}
            return {'display': 'none'}

    def __get_graph__(self, ticker_id: str, refresh_interval: int, limit: int = 0):
        period = PRD.DAILY
        aggregation = 15
        graph_cache_id = 1234
        return 'nothing so far'
        graph = self.sys_config.graph_cache.get_cached_object_by_key(graph_cache_id)
        if graph is not None:
            return graph, graph_cache_id

        if period == PRD.DAILY and self._recommender_table.selected_index != INDICES.CRYPTO_CCY:
            self.sys_config.data_provider.from_db = True
        else:
            self.sys_config.data_provider.from_db = False
        date_start = MyDate.adjust_by_days(MyDate.get_datetime_object().date(), -limit)
        and_clause = "Date > '{}'".format(date_start)
        graph_title = self.sys_config.graph_cache.get_cache_title(ticker_id, period, aggregation, limit)
        detector = self._pattern_controller.get_detector_for_fibonacci_and_pattern(
            self.sys_config, ticker_id, and_clause, limit)
        graph_api = DccGraphApi(graph_cache_id, graph_title)
        graph_api.ticker_id = ticker_id
        graph_api.df = detector.pdh.pattern_data.df
        graph = self.__get_dcc_graph_element__(detector, graph_api)
        cache_api = self.sys_config.graph_cache.get_cache_object_api(graph_cache_id, graph, period, refresh_interval)
        self.sys_config.graph_cache.add_cache_object(cache_api)
        return graph, graph_cache_id

    def __init_callback_for_graph_for_selected_position__(self):
        @self.app.callback(
            Output('my_graph_recommender_position_div', 'children'),
            [Input(self._data_table_name, 'rows'),
             Input(self._data_table_name, 'selected_row_indices')],
            [State('my_recommender_aggregation', 'value'),
             State('my_recommender_refresh_interval_selection', 'value')])
        def handle_callback_for_graph_first(
                rows: list, selected_row_indices: list, aggregation: int, refresh_interval: int):
            # print('selected_row_indices={}'.format(selected_row_indices))
            self._sales_table.init_selected_row(rows, selected_row_indices)
            if self._sales_table.selected_row_index == -1:
                return ''
            selected_ticker_id = self._sales_table.selected_symbol
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
            if self._sales_table.selected_row_index == -1 or len(range_list) == 0:
                return ''
            selected_ticker_id = self._sales_table.selected_symbol
            graph_list = []
            sorted_range_list = sorted(range_list)
            for graph_range in sorted_range_list:
                if graph_range == 1:
                    graph, key = self.__get_graph__(selected_ticker_id, refresh_interval)
                else:
                    graph, key = self.__get_graph__(selected_ticker_id, refresh_interval, graph_range)
                graph_list.append(graph)
            return graph_list

    def __init_callback_for_sales_markdown__(self):
        @self.app.callback(
            Output('my_recommender_markdown', 'children'),
            [Input('my_position_markdown', 'children')])
        def handle_callback_for_recommender_markdown(children):
            return self.__get_recommender_markdown__()

    def __get_recommender_markdown__(self):
        balances = None
        return ''
        text_list = ['_**{}**_: {:.2f} ({:.2f}): {:.2f}$'.format(
                b.asset, b.amount, b.amount_available, b.current_value) for b in balances]
        return '  \n'.join(text_list)

    def __get_sale_grid_table__(self):
        if self._sale_grid_table.selected_source == SLSRC.ONLINE and False:
            return ''
        rows = self._sale_grid_table.get_rows_for_selected_source()
        min_height = self._sale_grid_table.height_for_display
        return MyDCC.data_table(self._data_table_name, rows, [], min_height=min_height)

    def __get_similar_sale_grid_table_by_online_search__(self, title: str, description: str):
        rows = [{'Title': title, 'Description': description}]
        # rows = self._similar_sale_grid_table.get_rows_for_selected_source(master_id)
        min_height = self._similar_sale_grid_table.height_for_display
        return MyDCC.data_table(self._my_sales_similar_sale_grid_table, rows, [], min_height=min_height)

    def __get_similar_sale_grid_table__(self, master_id: str):
        if master_id == '':
            return ''
        rows = self._similar_sale_grid_table.get_rows_for_selected_source(master_id)
        min_height = self._similar_sale_grid_table.height_for_display
        return MyDCC.data_table(self._my_sales_similar_sale_grid_table, rows, [], min_height=min_height)

