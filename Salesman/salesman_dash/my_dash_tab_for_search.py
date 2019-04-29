"""
Description: This module contains the dash tab for recommendations from various sources, e.g. bitfinex, Nasdaq...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""

from dash.dependencies import Input, Output, State
from calculation.outlier import Outlier
from sertl_analytics.mydash.my_dash_base_tab import MyDashBaseTab
from sertl_analytics.mydash.my_dash_components import MyDCC, MyHTML, DccGraphApi
from salesman_dash.header_tables.my_tab_header_table_4_search import MyHTMLTabSearchHeaderTable
from salesman_dash.input_tables.my_online_sale_table import MyHTMLSearchOnlineInputTable
from salesman_dash.my_dash_tab_dd_for_search import SearchTabDropDownHandler, SRDD
from dash import Dash
from sertl_analytics.my_pandas import MyPandas
from sertl_analytics.mydates import MyDate
from sertl_analytics.my_text import MyText
from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_dash.grid_tables.my_grid_table_sale_4_sales import MySaleTable
from salesman_dash.grid_tables.my_grid_table_sale_4_search_results import MySearchResultTable
from salesman_system_configuration import SystemConfiguration
from salesman_dash.plotting.my_dash_plotter_for_salesman_search import MyDashTabPlotter4Search
from salesman_dash.my_dash_colors import DashColorHandler
from tutti import Tutti
import pandas as pd
from printing.sale_printing import SalesmanPrint


class MyDashTab4Search(MyDashBaseTab):
    _data_table_name = 'my_search_result_grid_table'
    _data_table_div = '{}_div'.format(_data_table_name)

    def __init__(self, app: Dash, sys_config: SystemConfiguration, tutti: Tutti):
        MyDashBaseTab.__init__(self, app)
        self.sys_config = sys_config
        self.tutti = tutti
        self._sale_table = self.sys_config.sale_table
        self._dd_handler = SearchTabDropDownHandler()
        self._color_handler = self.__get_color_handler__()
        self._header_table = MyHTMLTabSearchHeaderTable()
        self._sale_grid_table = MySaleTable(self.sys_config)
        self._search_results_grid_table = MySearchResultTable(self.sys_config)
        self._search_online_input_table = MyHTMLSearchOnlineInputTable()
        self._selected_my_sale_row = None
        self._selected_search_result_row = None
        self._search_input = ''
        self._online_rows = None

    def __init_dash_element_ids__(self):
        self._my_search_result_entry_link = 'my_search_result_entry_link'
        self._my_search_result_graph_div = 'my_search_result_graph_div'
        self._my_search_div = 'my_search_div'
        self._my_search_result_grid_table = 'my_search_result_grid_table'
        self._my_search_result_entry_markdown = 'my_search_result_entry_markdown'
        self._my_search_result_grid_table_div = '{}_div'.format(self._my_search_result_grid_table)
        self._my_search_online_input_table = 'my_search_online_input_table'
        self._my_search_online_input_table_div = '{}_div'.format(self._my_search_online_input_table)

    def __get_color_handler__(self):
        return DashColorHandler()

    def get_div_for_tab(self):
        children_list = [
            self._header_table.get_table(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_SOURCE)),
            MyHTML.div_with_html_element(self._my_search_online_input_table, self._search_online_input_table.get_table()),
            MyHTML.div_with_button_link(self._my_search_result_entry_link, href='', title='', hidden='hidden'),
            MyHTML.div(self._my_search_result_grid_table_div, '', False),
            MyDCC.markdown(self._my_search_result_entry_markdown),
            MyHTML.div(self._my_search_result_graph_div, '', False),
        ]
        return MyHTML.div(self._my_search_div, children_list)

    def init_callbacks(self):
        self.__init_callback_for_search_markdown__()
        self.__init_callbacks_for_search_result_entry_link__()
        self.__init_callback_for_search_result_grid_table__()
        self.__init_callback_for_search_result_entry_markdown__()
        self.__init_callbacks_for_search_result_numbers__()
        self.__init_callback_for_search_result_graph__()

    def __init_callbacks_for_search_result_entry_link__(self):
        @self.app.callback(
            Output(self._my_search_result_entry_link, 'hidden'),
            [Input(self._my_search_result_grid_table, 'rows'),
             Input(self._my_search_result_grid_table, 'selected_row_indices')])
        def handle_callback_for_search_result_entry_link_visibility(rows: list, selected_row_indices: list):
            if len(selected_row_indices) == 0:
                self._selected_search_result_row = None
                return 'hidden'
            self._selected_search_result_row = rows[selected_row_indices[0]]
            return ''

        @self.app.callback(
            Output(self._my_search_result_entry_link, 'children'),
            [Input(self._my_search_result_entry_link, 'hidden')])
        def handle_callback_for_search_result_entry_link_text(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            button_text = MyText.get_next_best_abbreviation(self._selected_search_result_row[SLDC.TITLE], 30)
            return MyHTML.button_submit('my_link_button', 'Open "{}"'.format(button_text), '')

        @self.app.callback(
            Output(self._my_search_result_entry_link, 'href'),
            [Input(self._my_search_result_entry_link, 'hidden')])
        def handle_callback_for_search_result_entry_link_href(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            return self._selected_search_result_row[SLDC.HREF]

    def __init_callbacks_for_search_result_numbers__(self):
        @self.app.callback(
            Output(self._header_table.my_search_found_valid_value_div, 'children'),
            [Input(self._my_search_result_grid_table, 'rows')])
        def handle_callback_for_search_result_numbers_valid(rows: list):
            if len(rows) == 0:
                return 0
            rows_valid = [row for row in rows if not row[SLDC.IS_OUTLIER]]
            return len(rows_valid)

        @self.app.callback(
            Output(self._header_table.my_search_found_all_value_div, 'children'),
            [Input(self._my_search_result_grid_table, 'rows')])
        def handle_callback_for_search_result_numbers_all(rows: list):
            return len(rows)

    def __handle_refresh_click__(self, refresh_n_clicks: int):
        if self._refresh_button_clicks == refresh_n_clicks:
            return
        self._refresh_button_clicks = refresh_n_clicks
        self._sale_grid_table = MySaleTable(self.sys_config)
        self._search_results_grid_table = MySearchResultTable(self.sys_config)

    def __init_callback_for_search_result_grid_table__(self):
        @self.app.callback(
            Output(self._my_search_result_grid_table_div, 'children'),
            [Input(self._dd_handler.my_search_source_dd, 'value'),
             Input(self._search_online_input_table.my_search_input, 'n_blur'),
             Input(self._search_online_input_table.my_search_button, 'n_clicks')
             ],
            [State(self._search_online_input_table.my_search_input, 'value')]
        )
        def handle_callback_for_search_result_grid_table(
                search_source: str, n_blur: int, search_n_clicks: int, search_input: str):
            self._dd_handler.selected_search_source = search_source
            self._search_input = search_input
            self._online_rows = None
            if self._search_online_input_table.search_button_n_clicks != search_n_clicks:
                self._search_online_input_table.search_input_n_blur = n_blur
                self._search_online_input_table.search_button_n_clicks = search_n_clicks
                return self.__get_search_result_grid_table_by_online_search__()
            return ''

    def __init_callback_for_search_result_entry_markdown__(self):
        @self.app.callback(
            Output(self._my_search_result_entry_markdown, 'children'),
            [Input(self._my_search_result_grid_table, 'selected_row_indices')],
            [State(self._my_search_result_grid_table, 'rows')]
        )
        def handle_callback_for_search_result_entry_markdown(selected_row_indices: list, rows):
            if len(selected_row_indices) == 0 or len(rows) == len(selected_row_indices) != 1:
                return ''
            selected_row = rows[selected_row_indices[0]]
            # print('selected_row={}/type={}'.format(selected_row, type(selected_row)))
            column_value_list = ['_**{}**_: {}'.format(col, selected_row[col]) for col in selected_row]
            return '  \n'.join(column_value_list)

    def __init_callback_for_search_markdown__(self):
        @self.app.callback(
            Output(self._header_table.my_search_markdown, 'children'),
            [Input(self._my_search_result_grid_table_div, 'children'),
             Input(self._header_table.my_search_found_valid_value_div, 'children')])
        def handle_callback_for_search_markdown(search_result_grid_table, children):
            print('handle_callback_for_search_markdown for {}'.format(self._search_input))
            if self._search_input == '':
                return '**Please enter search string**'
            return self.__get_search_markdown_for_online_search__()

    def __init_callback_for_search_result_graph__(self):
        @self.app.callback(
            Output(self._my_search_result_graph_div, 'children'),
            [Input(self._my_search_result_grid_table_div, 'children')])
        def handle_callback_for_search_result_graph(children):
            if self._online_rows is None:
                return ''
            return self.__get_scatter_plot__()

    def __get_scatter_plot__(self):
        df_search_result = self.tutti.printing.df_sale
        # MyPandas.print_df_details(df_search_result)
        plotter = MyDashTabPlotter4Search(df_search_result, self._color_handler)
        scatter_chart = plotter.get_chart_type_scatter()
        return scatter_chart

    def __get_search_markdown_for_online_search__(self):
        my_sale = '_**Searching for**_: {}'.format(self._search_input)
        if self._online_rows is None or len(self._online_rows) == 0:
            return '  \n'.join([my_sale, '**NO RESULTS FOUND**'])
        outlier_online_search = self.__get_outlier_for_online_search__()
        return self.__get_search_markdown_with_outlier__(my_sale, outlier_online_search)

    def __get_search_markdown_with_outlier__(self, my_sale: str, outlier_online_search: Outlier):
        prices = '_**[min, bottom, mean, top, max]**_: [{:.2f}, {:.2f}, **{:.2f}**, {:.2f}, {:.2f}]'.format(
            outlier_online_search.min_values, outlier_online_search.bottom_threshold,
            outlier_online_search.mean_values, outlier_online_search.top_threshold,
            outlier_online_search.max_values)
        prices_iqr = '_**[min, bottom, mean, top, max]**_: [{:.2f}, {:.2f}, **{:.2f}**, {:.2f}, {:.2f}]'.format(
            outlier_online_search.min_values, outlier_online_search.bottom_threshold_iqr,
            outlier_online_search.mean_values, outlier_online_search.top_threshold_iqr,
            outlier_online_search.max_values)
        price_suggested = outlier_online_search.mean_values_without_outliers
        if self._selected_my_sale_row is None:
            my_price = 0
            pct_change = 0
        else:
            my_price = self._selected_my_sale_row[SLDC.PRICE_SINGLE]
            pct_change = int(price_suggested - my_price) / my_price * 100
        start_search_labels = '_**Search labels**_: {}'.format(self.tutti.start_search_label_lists)
        my_price_suggested = '_**Price**_: {:.2f}  -->  _**Price suggested**_: {:.2f} ({:+.2f}%)'.format(
            my_price, price_suggested, pct_change)
        return '  \n'.join([my_sale, prices, my_price_suggested, start_search_labels])

    def __get_outlier_for_online_search__(self) -> Outlier:
        df_results = pd.DataFrame.from_dict(self._online_rows)
        price_single_list = [0] if df_results.shape[0] == 0 else list(df_results[SLDC.PRICE_SINGLE])
        outlier = Outlier(price_single_list, self.sys_config.outlier_threshold)
        return outlier

    def __get_search_result_grid_table_by_online_search__(self):
        self._online_rows = self.tutti.get_search_results_from_online_inputs(self._search_input)
        min_height = self._search_results_grid_table.height_for_display
        return MyDCC.data_table(self._my_search_result_grid_table, self._online_rows, [], min_height=min_height)
