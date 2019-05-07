"""
Description: This module contains the dash tab for recommendations from various sources, e.g. bitfinex, Nasdaq...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""

from dash.dependencies import Input, Output, State
from calculation.outlier import Outlier
from sertl_analytics.mydash.my_dash_base_tab import MyDashBaseTab
from sertl_analytics.mydash.my_dash_components import MyDCC, MyHTML
from salesman_dash.header_tables.my_tab_header_table_4_sales import MyHTMLTabSalesHeaderTable
from salesman_dash.my_dash_tab_dd_for_sales import SaleTabDropDownHandler, SLDD
from dash import Dash
from sertl_analytics.my_text import MyText
from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_dash.grid_tables.my_grid_table_4_sales_base import GridTableSelectionApi
from salesman_dash.grid_tables.my_grid_table_4_sales import MySaleTable4MyFile
from salesman_dash.grid_tables.my_grid_table_4_sales import MySaleTable4MySales, MySaleTable4SimilarSales
from salesman_system_configuration import SystemConfiguration
from salesman_tutti.tutti import Tutti
from salesman_tutti.tutti_categorizer import ProductCategorizer, RegionCategorizer


class MyDashTab4Sales(MyDashBaseTab):
    _data_table_name = 'my_sales_grid_table'
    _data_table_div = '{}_div'.format(_data_table_name)

    def __init__(self, app: Dash, sys_config: SystemConfiguration, tutti: Tutti):
        MyDashBaseTab.__init__(self, app)
        self.sys_config = sys_config
        self.tutti = tutti
        self._sale_table = self.sys_config.sale_table
        self._refresh_button_clicks = 0
        self._search_button_clicks = 0
        self._dd_handler = SaleTabDropDownHandler(self.sys_config)
        self._header_table = MyHTMLTabSalesHeaderTable()
        self._selection_api = GridTableSelectionApi()
        self._sale_grid_table = MySaleTable4MySales(self.sys_config)
        self._sale_file_grid_table = MySaleTable4MyFile(self.sys_config)
        self._similar_sale_grid_table = MySaleTable4SimilarSales(self.sys_config)
        self._selected_my_sale_row = None
        self._selected_similar_sale_row = None
        self._online_title = None
        self._online_rows = None
        self._region_categorizer = RegionCategorizer()
        self._product_categorizer = ProductCategorizer()

    def __init_dash_element_ids__(self):
        self._my_sales_filter_button = 'my_sales_filter_button'
        self._my_sales_search_similar_button = 'my_sales_search_similar_button'
        self._my_sales_link = 'my_sales_link'
        self._my_sales_similar_sale_link = 'my_sales_similar_sale_link'
        self._my_sales_graph_div = 'my_sales_graph_div'
        self._my_sales_div = 'my_sales_div'
        self._my_sales_sale_entry_markdown = 'my_sales_sale_entry_markdown'
        self._my_sales_similar_sale_grid_table = 'my_sales_similar_sale_grid_table'
        self._my_sales_similar_sale_entry_markdown = 'my_sales_similar_sale_entry_markdown'
        self._my_sales_similar_sale_grid_table_div = '{}_div'.format(self._my_sales_similar_sale_grid_table)

    def get_div_for_tab(self):
        children_list = [
            self._header_table.get_table(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SLDD.SALE_SOURCE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SLDD.SALE_REGION)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SLDD.SALE_CATEGORY)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SLDD.SALE_SUB_CATEGORY)),
            MyHTML.div_with_html_button_submit(self._my_sales_filter_button, children='Filter', hidden=''),
            MyHTML.div_with_html_button_submit(
                self._my_sales_search_similar_button, children='Search similar', hidden='hidden'),
            MyHTML.div_with_button_link(self._my_sales_link, href='', title='', hidden='hidden'),
            MyHTML.div(self._data_table_div, self.__get_sale_grid_table__(), False),  # ERROR
            MyDCC.markdown(self._my_sales_sale_entry_markdown),
            MyHTML.div_with_button_link(self._my_sales_similar_sale_link, href='', title='', hidden='hidden'),
            MyHTML.div(self._my_sales_similar_sale_grid_table_div, self.__get_similar_sale_grid_table__(''), False),
            MyDCC.markdown(self._my_sales_similar_sale_entry_markdown),
        ]
        return MyHTML.div(self._my_sales_div, children_list)

    def init_callbacks(self):
        self.__init_callback_for_sales_markdown__()
        self.__init_callbacks_for_my_sales_link__()
        self.__init_callbacks_for_my_search_similar_button__()
        self.__init_callback_for_sale_grid_table__()
        self.__init_callbacks_for_selected_sale_entry__()
        self.__init_callbacks_for_similar_sales_link__()
        self.__init_callback_for_similar_sale_grid_table__()
        self.__init_callback_for_similar_sale_entry_markdown__()

    def __init_callbacks_for_my_sales_link__(self):
        @self.app.callback(
            Output(self._my_sales_link, 'hidden'),
            [Input(self._data_table_name, 'rows'),
             Input(self._data_table_name, 'selected_row_indices')])
        def handle_callback_for_my_sales_link_visibility(rows: list, selected_row_indices: list):
            self._selected_my_sale_row = None if len(selected_row_indices) == 0 else rows[selected_row_indices[0]]
            if self._selected_my_sale_row is None or self._dd_handler.selected_sale_source == SLSRC.FILE:
                return 'hidden'
            return ''

        @self.app.callback(
            Output(self._my_sales_link, 'children'),
            [Input(self._my_sales_link, 'hidden')])
        def handle_callback_for_my_sales_link_title(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            button_text = MyText.get_next_best_abbreviation(self._selected_my_sale_row[SLDC.TITLE], 25)
            return MyHTML.button_submit('my_link_button', 'Open "{}"'.format(button_text), '')

        @self.app.callback(
            Output(self._my_sales_link, 'href'),
            [Input(self._my_sales_link, 'hidden')])
        def handle_callback_for_my_sales_link_href(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            return self._selected_my_sale_row[SLDC.HREF]

    def __init_callbacks_for_my_search_similar_button__(self):
        @self.app.callback(
            Output(self._my_sales_search_similar_button, 'hidden'),
            [Input(self._data_table_name, 'selected_row_indices')])
        def handle_callback_for_my_search_similar_button_visibility(selected_row_indices: list):
            return 'hidden' if len(selected_row_indices) == 0 else ''

        @self.app.callback(
            Output(self._my_sales_search_similar_button, 'children'),
            [Input(self._data_table_name, 'rows'),
             Input(self._data_table_name, 'selected_row_indices')])
        def handle_callback_for_my_search_similar_button_visibility(rows: list, selected_row_indices: list):
            if len(selected_row_indices) == 0:
                return 'Search similar'
            return 'Search on Tutti.ch for {}'.format(rows[selected_row_indices[0]][SLDC.SALE_ID])

    def __init_callbacks_for_similar_sales_link__(self):
        @self.app.callback(
            Output(self._my_sales_similar_sale_link, 'hidden'),
            [Input(self._my_sales_similar_sale_grid_table, 'rows'),
             Input(self._my_sales_similar_sale_grid_table, 'selected_row_indices')])
        def handle_callback_for_similar_sales_link_visibility(rows: list, selected_row_indices: list):
            if len(selected_row_indices) == 0:
                self._selected_similar_sale_row = None
                return 'hidden'
            self._selected_similar_sale_row = rows[selected_row_indices[0]]
            return ''

        @self.app.callback(
            Output(self._my_sales_similar_sale_link, 'children'),
            [Input(self._my_sales_similar_sale_link, 'hidden')])
        def handle_callback_for_similar_sales_link_text(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            button_text = MyText.get_next_best_abbreviation(self._selected_similar_sale_row[SLDC.TITLE], 30)
            return MyHTML.button_submit('my_link_button', 'Open "{}"'.format(button_text), '')

        @self.app.callback(
            Output(self._my_sales_similar_sale_link, 'href'),
            [Input(self._my_sales_similar_sale_link, 'hidden')])
        def handle_callback_for_similar_sales_link_href(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            return self._selected_similar_sale_row[SLDC.HREF]

    def __init_callback_for_sale_grid_table__(self):
        @self.app.callback(
            Output(self._data_table_div, 'children'),
            [Input(self._my_sales_filter_button, 'n_clicks'),
             Input(self._my_sales_search_similar_button, 'n_clicks')],
            [State(self._dd_handler.my_sale_source_dd, 'value'),
             State(self._dd_handler.my_sale_region_dd, 'value'),
             State(self._dd_handler.my_sale_category_dd, 'value'),
             State(self._dd_handler.my_sale_sub_category_dd, 'value'),
             State(self._data_table_name, 'rows'),
             State(self._data_table_name, 'selected_row_indices')]
            )
        def handle_callback_for_sale_grid_table(
                filter_n_clicks: int, refresh_n_clicks: int,
                source: str, region: str, category: str, sub_category: str, rows: list, selected_row_indices: list):
            self._selection_api.source = source
            self._selection_api.region = self._region_categorizer.get_category_for_value(region)
            self._selection_api.category = self._product_categorizer.get_category_for_value(category)
            self._selection_api.sub_category = \
                self._product_categorizer.get_sub_category_for_value(self._selection_api.category, sub_category)
            self._selected_my_sale_row = None if len(selected_row_indices) == 0 else rows[selected_row_indices[0]]
            self.__handle_refresh_click__(refresh_n_clicks)
            return self.__get_sale_grid_table__()

    def __handle_refresh_click__(self, refresh_n_clicks: int):
        if self._refresh_button_clicks == refresh_n_clicks:
            return
        self._refresh_button_clicks = refresh_n_clicks
        if self._dd_handler.selected_sale_source == SLSRC.DB:
            sale_id = self._selected_my_sale_row[SLDC.SALE_ID]
            if self.sys_config.access_layer_sale.is_sale_with_id_available(sale_id):
                sale_df = self.sys_config.access_layer_sale.get_sale_by_id(sale_id)
                sale_series = sale_df.iloc[0]
                title, description = sale_series[SLDC.TITLE], sale_series[SLDC.DESCRIPTION]
                print('__handle_refresh_click__: title={}, description={}'.format(title, description))
        else:
            title, description = self._selected_my_sale_row[SLDC.TITLE], self._selected_my_sale_row[SLDC.DESCRIPTION]
            print('__handle_refresh_click__: title={}, description={}'.format(title, description))
            results = self.tutti.get_search_results_from_online_inputs(title)
            print(results)

    def __init_callback_for_similar_sale_grid_table__(self):
        @self.app.callback(
            Output(self._my_sales_similar_sale_grid_table_div, 'children'),
            [Input(self._my_sales_search_similar_button, 'n_clicks'),
             Input(self._data_table_name, 'rows'),
             Input(self._data_table_name, 'selected_row_indices')
             ]
        )
        def handle_callback_for_similar_sale_grid_table(
                refresh_n_clicks: int,
                rows: list,
                selected_row_indices: list):
            if len(selected_row_indices) == 0 or len(rows) == len(selected_row_indices) != 1:
                self._sale_grid_table.reset_selected_row()
                return ''
            selected_row = rows[selected_row_indices[0]]
            sale_id = selected_row[SLDC.SALE_ID]
            return self.__get_similar_sale_grid_table__(sale_id)

    def __init_callbacks_for_selected_sale_entry__(self):
        @self.app.callback(
            Output(self._my_sales_sale_entry_markdown, 'children'),
            [Input(self._data_table_name, 'selected_row_indices')],
            [State(self._data_table_name, 'rows')])
        def handle_callback_for_selected_sale_entry_markdown(selected_row_indices: list, rows: list):
            if len(selected_row_indices) == 0 or len(rows) == len(selected_row_indices) != 1:
                self._sale_grid_table.reset_selected_row()
                return ''
            self._sale_grid_table.selected_row = rows[selected_row_indices[0]]
            column_value_list = ['_**{}**_: {}'.format(
                col, self._sale_grid_table.selected_row[col]) for col in self._sale_grid_table.columns]
            return '  \n'.join(column_value_list)

        @self.app.callback(
            Output(self._header_table.my_sales_id_value_div, 'children'),
            [Input(self._data_table_name, 'selected_row_indices')],
            [State(self._data_table_name, 'rows')])
        def handle_callback_for_selected_sale_entry_sale_id(selected_row_indices: list, rows: list):
            if len(selected_row_indices) == 0:
                return ''
            return rows[selected_row_indices[0]][SLDC.SALE_ID]

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

    def __init_callback_for_sales_markdown__(self):
        @self.app.callback(
            Output(self._header_table.my_sales_markdown, 'children'),
            [Input(self._my_sales_link, 'hidden')])
        def handle_callback_for_sales_markdown(sales_link_hidden: str):
            if self._selected_my_sale_row is None:
                return ''
            return self.__get_sales_markdown_for_selected_sale__()

    def __get_sales_markdown_for_selected_sale__(self):
        my_sale = '_**Title**_: {}'.format(self._selected_my_sale_row[SLDC.TITLE])
        outlier_similar_sales = self.__get_outlier_for_similar_sales__(self._selected_my_sale_row[SLDC.SALE_ID])
        return self.__get_sales_markdown_with_outlier__(my_sale, outlier_similar_sales)

    def __get_sales_markdown_with_outlier__(self, my_sale: str, outlier_similar_sales: Outlier):
        prices = '_**[min, bottom, mean, top, max]**_: [{:.2f}, {:.2f}, **{:.2f}**, {:.2f}, {:.2f}]'.format(
            outlier_similar_sales.min_values, outlier_similar_sales.bottom_threshold,
            outlier_similar_sales.mean_values, outlier_similar_sales.top_threshold,
            outlier_similar_sales.max_values)
        price_suggested = outlier_similar_sales.mean_values_without_outliers
        if self._selected_my_sale_row is None:
            my_price = 0
            pct_change = 0
        else:
            if self._dd_handler.selected_sale_source == SLSRC.FILE:
                my_price = self._selected_my_sale_row[SLDC.PRICE]
            else:
                my_price = self._selected_my_sale_row[SLDC.PRICE_SINGLE]
            pct_change = int(price_suggested - my_price) / my_price * 100
        my_price_suggested = '_**Price**_: {:.2f}  -->  _**Price suggested**_: {:.2f} ({:+.2f}%)'.format(
            my_price, price_suggested, pct_change)
        return '  \n'.join([my_sale, prices, my_price_suggested])

    def __get_outlier_for_similar_sales__(self, sale_id: str) -> Outlier:
        df_similar = self.sys_config.access_layer_sale.get_existing_sales_for_master_id(sale_id)
        price_single_list = [0] if df_similar.shape[0] == 0 else list(df_similar[SLDC.PRICE_SINGLE])
        outlier = Outlier(price_single_list, self.sys_config.outlier_threshold)
        # outlier.print_outlier_details()
        return outlier

    def __get_sale_grid_table__(self):
        if self._dd_handler.selected_sale_source == SLSRC.FILE:
            grid_table = self._sale_file_grid_table
        else:
            grid_table = self._sale_grid_table
        rows = grid_table.get_rows_for_selection(self._selection_api, False)
        min_height = self._sale_grid_table.height_for_display
        return MyDCC.data_table(self._data_table_name, rows, [], min_height=min_height)

    def __get_similar_sale_grid_table__(self, master_id: str):
        if master_id == '':
            return ''
        self._selection_api.master_id = master_id
        rows = self._similar_sale_grid_table.get_rows_for_selection(self._selection_api, True)
        min_height = self._similar_sale_grid_table.height_for_display
        return MyDCC.data_table(self._my_sales_similar_sale_grid_table, rows, [], min_height=min_height)

