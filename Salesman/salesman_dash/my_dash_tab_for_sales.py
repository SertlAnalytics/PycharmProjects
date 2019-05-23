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
from sertl_analytics.constants.salesman_constants import SLDC, SLSRC, SMPR
from salesman_dash.grid_tables.my_grid_table_4_sales_base import GridTableSelectionApi
from salesman_dash.grid_tables.my_grid_table_4_sales import MySaleTable4MyFile
from salesman_dash.grid_tables.my_grid_table_4_sales import MySaleTable4MySales, MySaleTable4SimilarSales
from salesman_system_configuration import SystemConfiguration
from salesman_tutti.tutti import Tutti
from salesman_dash.plotting.my_dash_plotter_for_salesman_sales import MyDashTabPlotter4Sales
from factories.salesman_sale_factory import SalesmanSaleFactory
from salesman_dash.my_dash_colors import DashColorHandler
import pandas as pd
import numpy as np


class MyDashTab4Sales(MyDashBaseTab):
    _data_table_name = 'my_sales_grid_table'
    _data_table_div = '{}_div'.format(_data_table_name)

    def __init__(self, app: Dash, sys_config: SystemConfiguration, tutti: Tutti):
        MyDashBaseTab.__init__(self, app)
        self.sys_config = sys_config
        self._process_for_update_sales_data = sys_config.process_manager.get_process_by_name(
            SMPR.UPDATE_SALES_DATA_IN_STATISTICS_TAB)
        self.tutti = tutti
        self._salesman_spacy = self.tutti.salesman_spacy
        self._sale_table = self.sys_config.sale_table
        self._refresh_button_clicks = 0
        self._search_button_clicks = 0
        self._sale_factory = SalesmanSaleFactory(self.sys_config, self._salesman_spacy)
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

    def __get_color_handler__(self):
        return DashColorHandler()

    def __init_dash_element_ids__(self):
        self._my_sales_filter_input = 'my_sales_filter_input'
        self._my_sales_filter_button = 'my_sales_filter_button'
        self._my_sales_link = 'my_sales_link'
        self._my_sales_similar_sale_link = 'my_sales_similar_sale_link'
        self._my_sales_graph_div = 'my_sales_graph_div'
        self._my_sales_div = 'my_sales_div'
        self._my_sales_sale_entry_markdown = 'my_sales_sale_entry_markdown'
        self._my_sales_similar_sale_grid_table = 'my_sales_similar_sale_grid_table'
        self._my_sales_similar_sale_entry_markdown = 'my_sales_similar_sale_entry_markdown'
        self._my_sales_similar_sale_grid_table_div = '{}_div'.format(self._my_sales_similar_sale_grid_table)
        self._my_sales_regression_chart = 'my_sales_regression_chart'

    def get_div_for_tab(self):
        children_list = [
            self._header_table.get_table(),
            MyHTML.div_with_input(element_id=self._my_sales_filter_input,
                                  placeholder='Please enter filter for my sales...', size=500, height=27),
            MyHTML.div_with_button_link(self._my_sales_link, href='', title='', hidden='hidden'),
            MyHTML.div(self._data_table_div, self.__get_sale_grid_table__(), False),
            MyDCC.markdown(self._my_sales_sale_entry_markdown),
            MyHTML.div(self._my_sales_regression_chart, self.__get_sales_regression_chart__(), False),
            MyHTML.div_with_button_link(self._my_sales_similar_sale_link, href='', title='', hidden='hidden'),
            MyHTML.div(self._my_sales_similar_sale_grid_table_div, self.__get_similar_sale_grid_table__(''), False),
        ]
        return MyHTML.div(self._my_sales_div, children_list)

    def init_callbacks(self):
        self.__init_callback_for_sales_markdown__()
        self.__init_callbacks_for_my_sales_link__()
        self.__init_callback_for_sale_grid_table__()
        self.__init_callbacks_for_selected_sale_entry__()
        self.__init_callbacks_for_similar_sales_link__()
        self.__init_callback_for_similar_sale_grid_table__()
        self.__init_callback_for_similar_sale_entry_markdown__()
        self.__init_callback_for_sales_regression_chart__()

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
            selected_sale = self._sale_factory.get_sale_from_db_by_sale_id(self._selected_my_sale_row[SLDC.SALE_ID])
            return selected_sale.get_value(SLDC.HREF)

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
            [Input(self._my_sales_filter_input, 'n_blur')],
            [State(self._my_sales_filter_input, 'value'),
             State(self._data_table_name, 'rows'),
             State(self._data_table_name, 'selected_row_indices')]
            )
        def handle_callback_for_sale_grid_table(
                filter_n_blurs: int, filter_input: str,
                rows: list, selected_row_indices: list):
            self._selected_my_sale_row = None if len(selected_row_indices) == 0 else rows[selected_row_indices[0]]
            self._selection_api.input = filter_input
            return self.__get_sale_grid_table__()

    def __init_callback_for_similar_sale_grid_table__(self):
        @self.app.callback(
            Output(self._my_sales_similar_sale_grid_table_div, 'children'),
            [Input(self._data_table_name, 'rows'),
             Input(self._data_table_name, 'selected_row_indices')
             ]
        )
        def handle_callback_for_similar_sale_grid_table(
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

    def __init_callback_for_sales_regression_chart__(self):
        @self.app.callback(
            Output(self._my_sales_regression_chart, 'children'),
            [Input(self._data_table_name, 'selected_row_indices')],
            [State(self._data_table_name, 'rows')]
        )
        def handle_callback_sales_regression_chart(selected_row_indices: list, rows: list):
            print('selected_row_indices={}'.format(selected_row_indices))
            if len(selected_row_indices) == 0 or len(rows) == len(selected_row_indices) != 1:
                selected_row = None
            else:
                selected_row = rows[selected_row_indices[0]]
            return self.__get_sales_regression_chart__(selected_row)

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

    def __get_sales_regression_chart__(self, selected_row=None):
        if selected_row is None:
            return 'Nothing selected'
        selected_sale_id = selected_row[SLDC.SALE_ID]
        sale_from_db = self._sale_factory.get_sale_from_db_by_sale_id(selected_sale_id)
        df_similar = self.sys_config.access_layer_sale.get_sales_df_by_master_sale_id(selected_sale_id)
        df_similar_without_outliers = self.__get_df_without_outliers__(df_similar)
        plotter = MyDashTabPlotter4Sales(df_similar_without_outliers, self._color_handler)
        regression_chart = plotter.get_chart_type_regression(sale_from_db)
        return regression_chart

    def __get_df_without_outliers__(self, df: pd.DataFrame):
        price_single_list = [0] if df.shape[0] == 0 else list(df[SLDC.PRICE_SINGLE])
        outlier = Outlier(price_single_list, self.sys_config.outlier_threshold)
        outlier.print_outlier_details()
        return df[np.logical_and(df[SLDC.PRICE_SINGLE] >= outlier.bottom_threshold,
                                 df[SLDC.PRICE_SINGLE] <= outlier.top_threshold)]

    def __get_similar_sale_grid_table__(self, master_id: str):
        if master_id == '':
            return ''
        self._selection_api.master_id = master_id
        rows = self._similar_sale_grid_table.get_rows_for_selection(self._selection_api, True)
        min_height = self._similar_sale_grid_table.height_for_display
        return MyDCC.data_table(self._my_sales_similar_sale_grid_table, rows, [], min_height=min_height)

