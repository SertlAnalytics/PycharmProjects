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
from salesman_dash.header_tables.my_tab_header_table_4_pricing import MyHTMLTabPricingHeaderTable
from salesman_dash.input_tables.my_online_sale_table import MyHTMLSaleOnlineInputTable
from salesman_dash.my_dash_tab_dd_for_pricing import PricingTabDropDownHandler, PRDD
from dash import Dash
from sertl_analytics.mydates import MyDate
from sertl_analytics.my_text import MyText
from sertl_analytics.constants.pattern_constants import PRD, INDICES
from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_dash.grid_tables.my_grid_table_sale_4_sales import MySaleTable
from salesman_dash.grid_tables.my_grid_table_similar_sale_4_sales import MySimilarSaleTable
from salesman_system_configuration import SystemConfiguration
from tutti import Tutti
import pandas as pd


class MyDashTab4Pricing(MyDashBaseTab):
    _data_table_name = 'my_pricing_grid_table'
    _data_table_div = '{}_div'.format(_data_table_name)

    def __init__(self, app: Dash, sys_config: SystemConfiguration, tutti: Tutti):
        MyDashBaseTab.__init__(self, app)
        self.sys_config = sys_config
        self.tutti = tutti
        self._sale_table = self.sys_config.sale_table
        self._refresh_button_clicks = 0
        self._search_button_clicks = 0
        self._dd_handler = PricingTabDropDownHandler()
        self._header_table = MyHTMLTabPricingHeaderTable()
        self._sale_grid_table = MySaleTable(self.sys_config)
        self._similar_sale_grid_table = MySimilarSaleTable(self.sys_config)
        self._sale_online_input_table = MyHTMLSaleOnlineInputTable()
        self._selected_my_sale_row = None
        self._selected_similar_sale_row = None
        self._online_title = None
        self._online_rows = None

    def __init_dash_element_ids__(self):
        self._my_pricing_refresh_button = 'my_pricing_refresh_button'
        self._my_pricing_similar_sale_link = 'my_pricing_similar_sale_link'
        self._my_pricing_graph_div = 'my_pricing_graph_div'
        self._my_pricing_div = 'my_pricing_div'
        self._my_pricing_similar_sale_grid_table = 'my_pricing_similar_sale_grid_table'
        self._my_pricing_similar_sale_entry_markdown = 'my_pricing_similar_sale_entry_markdown'
        self._my_pricing_similar_sale_grid_table_div = '{}_div'.format(self._my_pricing_similar_sale_grid_table)
        self._my_pricing_online_input_table = 'my_pricing_online_input_table'
        self._my_pricing_online_input_table_div = '{}_div'.format(self._my_pricing_online_input_table)

    def get_div_for_tab(self):
        children_list = [
            self._header_table.get_table(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(PRDD.SIMILAR_SALE_SOURCE)),
            MyHTML.div_with_html_button_submit(self._my_pricing_refresh_button, 'Refresh', hidden=''),
            MyHTML.div_with_html_element(self._my_pricing_online_input_table, self._sale_online_input_table.get_table()),
            MyHTML.div_with_button_link(self._my_pricing_similar_sale_link, href='', title='', hidden='hidden'),
            MyHTML.div(self._my_pricing_similar_sale_grid_table_div, '', False),
            MyDCC.markdown(self._my_pricing_similar_sale_entry_markdown),
        ]
        return MyHTML.div(self._my_pricing_div, children_list)

    def init_callbacks(self):
        self.__init_callback_for_pricing_markdown__()
        self.__init_callbacks_for_similar_pricing_link__()
        self.__init_callback_for_similar_sale_grid_table__()
        self.__init_callback_for_similar_sale_entry_markdown__()

    def __init_callbacks_for_similar_pricing_link__(self):
        @self.app.callback(
            Output(self._my_pricing_similar_sale_link, 'hidden'),
            [Input(self._my_pricing_similar_sale_grid_table, 'rows'),
             Input(self._my_pricing_similar_sale_grid_table, 'selected_row_indices')])
        def handle_callback_for_similar_pricing_link_visibility(rows: list, selected_row_indices: list):
            if len(selected_row_indices) == 0:
                self._selected_similar_sale_row = None
                return 'hidden'
            self._selected_similar_sale_row = rows[selected_row_indices[0]]
            return ''

        @self.app.callback(
            Output(self._my_pricing_similar_sale_link, 'children'),
            [Input(self._my_pricing_similar_sale_link, 'hidden')])
        def handle_callback_for_similar_pricing_link_text(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            button_text = MyText.get_next_best_abbreviation(self._selected_similar_sale_row[SLDC.TITLE], 30)
            return MyHTML.button_submit('my_link_button', 'Open "{}"'.format(button_text), '')

        @self.app.callback(
            Output(self._my_pricing_similar_sale_link, 'href'),
            [Input(self._my_pricing_similar_sale_link, 'hidden')])
        def handle_callback_for_similar_pricing_link_href(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            return self._selected_similar_sale_row[SLDC.HREF]

    def __handle_refresh_click__(self, refresh_n_clicks: int):
        if self._refresh_button_clicks == refresh_n_clicks:
            return
        self._refresh_button_clicks = refresh_n_clicks
        self._sale_grid_table = MySaleTable(self.sys_config)
        self._similar_sale_grid_table = MySimilarSaleTable(self.sys_config)

    def __init_callback_for_similar_sale_grid_table__(self):
        @self.app.callback(
            Output(self._my_pricing_similar_sale_grid_table_div, 'children'),
            [Input(self._dd_handler.my_pricing_similar_sales_source_dd, 'value'),
             Input(self._my_pricing_refresh_button, 'n_clicks'),
             Input(self._sale_online_input_table.my_sales_online_search_button, 'n_clicks')
             ],
            [State(self._sale_online_input_table.my_sales_title_input, 'value'),
             State(self._sale_online_input_table.my_sales_description_input, 'value')]
        )
        def handle_callback_for_similar_sale_grid_table(
                similar_sale_source: str,
                refresh_n_clicks: int,
                search_n_clicks: int,
                title: str,
                description: str):
            self._dd_handler.selected_similar_sale_source = similar_sale_source
            self._online_title = None
            self._online_rows = None
            if self._dd_handler.selected_similar_sale_source == SLSRC.DB:
                return ''
            if self._search_button_clicks != search_n_clicks:
                self._search_button_clicks = search_n_clicks
                return self.__get_similar_sale_grid_table_by_online_search__(title, description)
            return ''

    def __init_callback_for_similar_sale_entry_markdown__(self):
        @self.app.callback(
            Output(self._my_pricing_similar_sale_entry_markdown, 'children'),
            [Input(self._my_pricing_similar_sale_grid_table, 'selected_row_indices')],
            [State(self._my_pricing_similar_sale_grid_table, 'rows')]
        )
        def handle_callback_similar_sale_entry_markdown(selected_row_indices: list, rows):
            if len(selected_row_indices) == 0 or len(rows) == len(selected_row_indices) != 1:
                return ''
            selected_row = rows[selected_row_indices[0]]
            # print('selected_row={}/type={}'.format(selected_row, type(selected_row)))
            column_value_list = ['_**{}**_: {}'.format(col, selected_row[col]) for col in selected_row]
            return '  \n'.join(column_value_list)

    def __init_callback_for_pricing_markdown__(self):
        @self.app.callback(
            Output(self._header_table.my_pricing_markdown, 'children'),
            [Input(self._my_pricing_similar_sale_grid_table_div, 'children')])
        def handle_callback_for_pricing_markdown(similar_sale_grid):
            if self._dd_handler.selected_similar_sale_source == SLSRC.DB:
                return ''
            else:
                if self._online_rows is None:
                    return ''
                return self.__get_pricing_markdown_for_online_search__()

    def __get_pricing_markdown_for_online_search__(self):
        my_sale = '_**Title**_: {}'.format(self._online_title)
        outlier_online_search = self.__get_outlier_for_online_search__()
        return self.__get_pricing_markdown_with_outlier__(my_sale, outlier_online_search)

    def __get_pricing_markdown_with_outlier__(self, my_sale: str, outlier_similar_sales: Outlier):
        prices = '_**[min, bottom, mean, top, max]**_: [{:.2f}, {:.2f}, **{:.2f}**, {:.2f}, {:.2f}]'.format(
            outlier_similar_sales.min_values, outlier_similar_sales.bottom_threshold,
            outlier_similar_sales.mean_values, outlier_similar_sales.top_threshold,
            outlier_similar_sales.max_values)
        prices_iqr = '_**[min, bottom, mean, top, max]**_: [{:.2f}, {:.2f}, **{:.2f}**, {:.2f}, {:.2f}]'.format(
            outlier_similar_sales.min_values, outlier_similar_sales.bottom_threshold_iqr,
            outlier_similar_sales.mean_values, outlier_similar_sales.top_threshold_iqr,
            outlier_similar_sales.max_values)
        price_suggested = outlier_similar_sales.mean_values_without_outliers
        if self._selected_my_sale_row is None:
            my_price = 0
            pct_change = 0
        else:
            my_price = self._selected_my_sale_row[SLDC.PRICE_SINGLE]
            pct_change = int(price_suggested - my_price) / my_price * 100
        my_price_suggested = '_**Price**_: {:.2f}  -->  _**Price suggested**_: {:.2f} ({:+.2f}%)'.format(
            my_price, price_suggested, pct_change)
        return '  \n'.join([my_sale, prices, my_price_suggested])

    def __get_outlier_for_similar_pricing__(self, sale_id: str) -> Outlier:
        df_similar = self.sys_config.access_layer_sale.get_existing_pricing_for_master_id(sale_id)
        price_single_list = [0] if df_similar.shape[0] == 0 else list(df_similar[SLDC.PRICE_SINGLE])
        outlier = Outlier(price_single_list, self.sys_config.outlier_threshold)
        # outlier.print_outlier_details()
        return outlier

    def __get_outlier_for_online_search__(self) -> Outlier:
        df_similar = pd.DataFrame.from_dict(self._online_rows)
        price_single_list = [0] if df_similar.shape[0] == 0 else list(df_similar[SLDC.PRICE_SINGLE])
        outlier = Outlier(price_single_list, self.sys_config.outlier_threshold)
        # outlier.print_outlier_details()
        return outlier

    def __get_similar_sale_grid_table_by_online_search__(self, title: str, description: str):
        self._online_title = title
        self._online_rows = self.tutti.get_similar_sales_from_online_inputs(title, description)
        # rows = [{'Title': title, 'Description': description}]
        # rows = self._similar_sale_grid_table.get_rows_for_selected_source(master_id)
        min_height = self._similar_sale_grid_table.height_for_display
        return MyDCC.data_table(self._my_pricing_similar_sale_grid_table, self._online_rows, [], min_height=min_height)
