"""
Description: This module contains the dash tab for recommendations from various sources, e.g. bitfinex, Nasdaq...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""

from dash.dependencies import Input, Output, State
from sertl_analytics.constants.my_constants import DSHVT
from salesman_tutti.tutti_constants import PRCAT
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
        self._selected_sale = None
        self._selected_similar_sale = None
        self._online_title = None
        self._selected_row_indices = []
        self._show_button_details_n_clicks = 0
        self._reset_button_n_clicks = 0

    def __get_color_handler__(self):
        return DashColorHandler()

    def __init_dash_element_ids__(self):
        self._my_sales_filter_input = 'my_sales_filter_input'
        self._my_sales_show_detail_button = 'my_sales_show_detail_button'
        self._my_sales_reset_button = 'my_sales_reset_button'
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
            MyHTML.div_with_html_button_submit(self._my_sales_show_detail_button, children='Details', hidden='hidden'),
            MyHTML.div_with_html_button_submit(self._my_sales_reset_button, children='Reset', hidden='hidden'),
            MyHTML.div_with_table(self._data_table_div, self.__get_sale_grid_table__()),
            MyDCC.markdown(self._my_sales_sale_entry_markdown),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SLDD.SALE_ENTITIES)),
            MyHTML.div(self._my_sales_regression_chart, self.__get_sales_regression_chart__(), inline=False),
            MyHTML.div_with_button_link(self._my_sales_similar_sale_link, href='', title='', hidden='hidden'),
            MyHTML.div_with_table(self._my_sales_similar_sale_grid_table_div, self.__get_similar_sale_grid_table__('')),
            MyDCC.markdown(self._my_sales_similar_sale_entry_markdown),
        ]
        return MyHTML.div(self._my_sales_div, children_list)

    def init_callbacks(self):
        self.__init_callback_for_sales_markdown__()
        self.__init_callbacks_for_sales_result_numbers__()
        self.__init_callbacks_for_my_sales_link__()
        self.__init_callback_for_my_sales_show_detail_button__()
        self.__init_callback_for_my_sales_reset_button__()
        self.__init_callback_for_sale_grid_table__()
        self.__init_callbacks_for_selected_sale_entry_markdown__()
        self.__init_callbacks_for_similar_sales_link__()
        self.__init_callback_for_similar_sale_grid_table__()
        self.__init_callback_for_similar_sale_entry_markdown__()
        self.__init_callback_for_sales_regression_chart__()
        self.__init_callbacks_for_filter_by_entities__()

    def __init_callback_for_my_sales_show_detail_button__(self):
        @self.app.callback(
            Output(self._my_sales_show_detail_button, DSHVT.HIDDEN),
            [Input(self._my_sales_link, DSHVT.HIDDEN)])
        def handle_callback_for_my_sales_show_detail_button_visibility(hidden: str):
            return 'hidden' if self._selected_sale is None else ''

    def __init_callback_for_my_sales_reset_button__(self):
        @self.app.callback(
            Output(self._my_sales_reset_button, DSHVT.HIDDEN),
            [Input(self._my_sales_link, DSHVT.HIDDEN)])
        def handle_callback_for_my_sales_reset_button_visibility(hidden: str):
            return 'hidden' if self._selected_sale is None else ''

    def __init_callbacks_for_sales_result_numbers__(self):
        @self.app.callback(
            Output(self._header_table.my_sales_found_valid_value_div, DSHVT.CHILDREN),
            [Input(self._my_sales_similar_sale_grid_table, DSHVT.ROWS)])
        def handle_callback_for_sales_result_numbers_valid(rows: list):
            return 0 if rows is None or len(rows) == 0 else len([row for row in rows if not row[SLDC.IS_OUTLIER]])

        @self.app.callback(
            Output(self._header_table.my_sales_found_all_value_div, DSHVT.CHILDREN),
            [Input(self._my_sales_similar_sale_grid_table, DSHVT.ROWS)])
        def handle_callback_for_sales_result_numbers_all(rows: list):
            return len(rows)

    def __init_callbacks_for_my_sales_link__(self):
        @self.app.callback(
            Output(self._my_sales_link, DSHVT.HIDDEN),
            [Input(self._data_table_name, DSHVT.SELECTED_ROW_INDICES)],
            [State(self._data_table_name, DSHVT.ROWS)])
        def handle_callback_for_my_sales_link_visibility(selected_row_indices: list, rows: list):
            if selected_row_indices is None or len(selected_row_indices) == 0:
                self._selected_sale = None
            else:
                selected_row = rows[selected_row_indices[0]]
                self._selected_sale = self._sale_factory.get_sale_from_db_by_sale_id(selected_row[SLDC.SALE_ID])
            return 'hidden' if self._selected_sale is None else ''

        @self.app.callback(
            Output(self._my_sales_link, DSHVT.CHILDREN),
            [Input(self._my_sales_link, DSHVT.HIDDEN)])
        def handle_callback_for_my_sales_link_title(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            button_text = MyText.get_next_best_abbreviation(self._selected_sale.title, 25)
            return MyHTML.button_submit('my_link_button', 'Open "{}"'.format(button_text), '')

        @self.app.callback(
            Output(self._my_sales_link, 'href'),
            [Input(self._my_sales_link, DSHVT.HIDDEN)])
        def handle_callback_for_my_sales_link_href(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            return self._selected_sale.get_value(SLDC.HREF)

    def __init_callbacks_for_filter_by_entities__(self):
        @self.app.callback(
            Output(self._dd_handler.get_embracing_div_id(SLDD.SALE_ENTITIES), DSHVT.STYLE),
            [Input(self._my_sales_similar_sale_grid_table_div, DSHVT.CHILDREN)])
        def handle_callback_for_sale_filter_by_entities_visibility(children):
            # print('children={}'.format(children))
            if len(children) == 0:
                return {'display': 'none'}
            return self._dd_handler.get_style_display(SLDD.SALE_ENTITIES)

        @self.app.callback(
            Output(self._dd_handler.my_sale_entities_dd, DSHVT.OPTIONS),
            [Input(self._my_sales_similar_sale_grid_table_div, DSHVT.CHILDREN)])
        def handle_callback_for_sale_filter_by_entities_options(children):
            if len(children) == 0 or len(self._similar_sale_grid_table.plot_categories) == 0:
                return []
            print_category_options = [{'label': PRCAT.ALL, 'value': PRCAT.ALL}]
            print('self._similar_sale_grid_table.plot_categories={}'.format(self._similar_sale_grid_table.plot_categories))
            for category in self._similar_sale_grid_table.plot_categories:
                label = category.replace('#', ' - ')
                value = category
                print_category_options.append({'label': label, 'value': value})
            return print_category_options

    def __init_callbacks_for_similar_sales_link__(self):
        @self.app.callback(
            Output(self._my_sales_similar_sale_link, DSHVT.HIDDEN),
            [Input(self._my_sales_similar_sale_grid_table, DSHVT.ROWS),
             Input(self._my_sales_similar_sale_grid_table, DSHVT.SELECTED_ROW_INDICES)])
        def handle_callback_for_similar_sales_link_visibility(rows: list, selected_row_indices: list):
            if len(selected_row_indices) == 0:
                self._selected_similar_sale = None
                return 'hidden'
            selected_similar_sale_id = rows[selected_row_indices[0]][SLDC.SALE_ID]
            self._selected_similar_sale = self._sale_factory.get_sale_from_db_by_sale_id(selected_similar_sale_id)
            return ''

        @self.app.callback(
            Output(self._my_sales_similar_sale_link, DSHVT.CHILDREN),
            [Input(self._my_sales_similar_sale_link, DSHVT.HIDDEN)])
        def handle_callback_for_similar_sales_link_text(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            button_text = MyText.get_next_best_abbreviation(self._selected_similar_sale.title, 30)
            return MyHTML.button_submit('my_link_button', 'Open "{}"'.format(button_text), '')

        @self.app.callback(
            Output(self._my_sales_similar_sale_link, DSHVT.HREF),
            [Input(self._my_sales_similar_sale_link, DSHVT.HIDDEN)])
        def handle_callback_for_similar_sales_link_href(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            return self._selected_similar_sale.get_value(SLDC.HREF)

    def __init_callback_for_sale_grid_table__(self):
        @self.app.callback(
            Output(self._data_table_div, DSHVT.CHILDREN),
            [Input(self._my_sales_filter_input, DSHVT.N_BLUR),
             Input(self._my_sales_reset_button, DSHVT.N_CLICKS)],
            [State(self._my_sales_filter_input, DSHVT.VALUE),
             State(self._data_table_name, DSHVT.ROWS),
             State(self._data_table_name, DSHVT.SELECTED_ROW_INDICES)]
            )
        def handle_callback_for_sale_grid_table(
                filter_n_blurs: int, reset_n_clicks: int, filter_input: str,
                rows: list, selected_row_indices: list):
            if self._reset_button_n_clicks != reset_n_clicks:
                self._reset_button_n_clicks = reset_n_clicks
                self._selected_row_indices = []
            else:
                if selected_row_indices is None or len(selected_row_indices) == 0:
                    self._selected_my_sale_row = None
                else:
                    self._selected_my_sale_row = rows[selected_row_indices[0]]
            self._selection_api.input = filter_input
            return self.__get_sale_grid_table__()

    def __init_callback_for_similar_sale_grid_table__(self):
        @self.app.callback(
            Output(self._my_sales_similar_sale_grid_table_div, DSHVT.CHILDREN),
            [Input(self._data_table_name, DSHVT.ROWS),
             Input(self._data_table_name, DSHVT.SELECTED_ROW_INDICES),
             Input(self._dd_handler.my_sale_entities_dd, DSHVT.VALUE)
             ]
        )
        def handle_callback_for_similar_sale_grid_table(rows: list, selected_row_indices: list, entity_values: list):
            if selected_row_indices is None or len(selected_row_indices) == 0:
                self._sale_grid_table.reset_selected_row()
                return ''
            if set(selected_row_indices) != set(self._selected_row_indices):
                self._selected_row_indices = selected_row_indices
                self._print_category_list = []
                self._print_category_options = []
                selected_entities_as_list = []
            else:
                selected_entities_as_list = entity_values
            selected_row = rows[selected_row_indices[0]]
            sale_id = selected_row[SLDC.SALE_ID]
            return self.__get_similar_sale_grid_table__(sale_id, selected_entities_as_list)

    def __init_callbacks_for_selected_sale_entry_markdown__(self):
        @self.app.callback(
            Output(self._my_sales_sale_entry_markdown, DSHVT.CHILDREN),
            [Input(self._my_sales_show_detail_button, DSHVT.N_CLICKS),
             Input(self._data_table_name, DSHVT.SELECTED_ROW_INDICES)],
            [State(self._my_sales_sale_entry_markdown, DSHVT.CHILDREN)])
        def handle_callback_for_selected_sale_entry_markdown(n_clicks: int, selected_indices: list, markdown_old: str):
            if self._selected_sale is None or len(selected_indices) == 0 or markdown_old != '' \
                    or self._show_button_details_n_clicks == n_clicks:
                return ''
            self._show_button_details_n_clicks = n_clicks
            columns = self._sale_grid_table.columns
            column_value_list = ['_**{}**_: {}'.format(col, self._selected_sale.get_value(col)) for col in columns]
            return '  \n'.join(column_value_list)

        @self.app.callback(
            Output(self._header_table.my_sales_id_value_div, DSHVT.CHILDREN),
            [Input(self._my_sales_link, DSHVT.HIDDEN)])
        def handle_callback_for_selected_sale_entry_sale_id(hidden: str):
            return '' if self._selected_sale is None else self._selected_sale.sale_id

    def __init_callback_for_sales_regression_chart__(self):
        @self.app.callback(
            Output(self._my_sales_regression_chart, DSHVT.CHILDREN),
            [Input(self._my_sales_similar_sale_grid_table_div, DSHVT.CHILDREN)],
            [State(self._data_table_name, DSHVT.SELECTED_ROW_INDICES)]
        )
        def handle_callback_sales_regression_chart(children, selected_row_indices: list):
            return self.__get_sales_regression_chart__(selected_row_indices)

    def __init_callback_for_similar_sale_entry_markdown__(self):
        @self.app.callback(
            Output(self._my_sales_similar_sale_entry_markdown, DSHVT.CHILDREN),
            [Input(self._my_sales_similar_sale_link, DSHVT.HIDDEN)]
        )
        def handle_callback_similar_sale_entry_markdown(*params):
            if self._selected_similar_sale is None:
                return ''
            column_value_list = ['_**{}**_: {}'.format(col, self._selected_similar_sale.get_value(col))
                                 for col in self._similar_sale_grid_table.columns]
            return '  \n'.join(column_value_list)

    def __init_callback_for_sales_markdown__(self):
        @self.app.callback(
            Output(self._header_table.my_sales_markdown, DSHVT.CHILDREN),
            [Input(self._my_sales_similar_sale_grid_table, DSHVT.ROWS)])
        def handle_callback_for_sales_markdown(similar_grid_rows: list):
            if self._selected_sale is None:
                return ''
            return self.__get_sales_markdown_for_selected_sale__()

    def __get_sales_markdown_for_selected_sale__(self):
        data_handler = self._similar_sale_grid_table.result_data_handler
        title = '**Selected Sale**: {}'.format(self._selected_sale.title)
        main_entities = '{}'.format(self._selected_sale.get_entity_label_main_values_dict_as_string())
        prices = data_handler.outlier_for_selection.get_markdown_text()
        price_suggested = data_handler.outlier_for_selection.mean_values_without_outliers
        my_price = self._selected_sale.price_single
        pct_change = int(price_suggested - my_price) / my_price * 100
        my_price_suggested = '**Price**: {:.2f}  -->  **Price suggested**: {:.2f} ({:+.2f}%)'.format(
            my_price, price_suggested, pct_change)
        return '  \n'.join([title, main_entities, prices, my_price_suggested])

    def __get_sale_grid_table__(self):
        if self._dd_handler.selected_sale_source == SLSRC.FILE:
            grid_table = self._sale_file_grid_table
        else:
            grid_table = self._sale_grid_table
        rows = grid_table.get_rows_for_selection(self._selection_api, False)
        min_height = grid_table.height_for_display
        return MyDCC.data_table(
            self._data_table_name,
            rows=rows,
            selected_row_indices=self._selected_row_indices,
            style_cell_conditional=grid_table.get_table_style_cell_conditional(),
            style_data_conditional=grid_table.get_table_style_data_conditional(rows),
            columns=grid_table.columns,
            min_height=min_height)

    def __get_sales_regression_chart__(self, selected_row_indices=None):
        if selected_row_indices is None or len(selected_row_indices) == 0:
            return ''
        df_similar_without_outliers = self._similar_sale_grid_table.df_for_plot
        if df_similar_without_outliers is None:
            return ''
        plotter = MyDashTabPlotter4Sales(
            df_similar_without_outliers, self._color_handler, self.sys_config.entity_handler)
        regression_chart = plotter.get_chart_type_regression(self._similar_sale_grid_table.sale_master)
        return regression_chart

    def __get_similar_sale_grid_table__(self, master_id: str, selected_entity_values: list=None):
        if master_id == '':
            return ''
        self._selection_api.master_id = master_id
        self._selection_api.entity_values = selected_entity_values
        self._selection_api.master_sale = self._sale_factory.get_sale_from_db_by_sale_id(master_id)
        rows = self._similar_sale_grid_table.get_rows_for_selection(self._selection_api, True)
        if len(rows) == 0:
            return 'Nothing found'
        return MyDCC.data_table(
            self._my_sales_similar_sale_grid_table,
            rows=rows,
            style_cell_conditional=self._similar_sale_grid_table.get_table_style_cell_conditional(),
            style_data_conditional=self._similar_sale_grid_table.get_table_style_data_conditional(rows),
            columns=self._similar_sale_grid_table.columns
        )

