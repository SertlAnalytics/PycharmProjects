"""
Description: This module contains the dash tab for recommendations from various sources, e.g. bitfinex, Nasdaq...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""

from dash.dependencies import Input, Output, State
from sertl_analytics.constants.my_constants import DSHVT
from calculation.outlier import Outlier
from sertl_analytics.mydash.my_dash_base_tab import MyDashBaseTab
from salesman_tutti.tutti_constants import PRCAT, PRSUBCAT
from sertl_analytics.mydash.my_dash_components import MyDCC, MyHTML
from salesman_dash.header_tables.my_tab_header_table_4_search import MyHTMLTabSearchHeaderTable
from salesman_dash.input_tables.my_online_sale_table import MyHTMLSearchOnlineInputTable
from salesman_dash.my_dash_tab_dd_for_search import SearchTabDropDownHandler, SRDD
from dash import Dash
from sertl_analytics.my_text import MyText
from sertl_analytics.my_pandas import MyPandas
from sertl_analytics.constants.salesman_constants import SLDC
from salesman_dash.grid_tables.my_grid_table_sale_4_search_results import MySearchResultTable
from salesman_system_configuration import SystemConfiguration
from salesman_dash.plotting.my_dash_plotter_for_salesman_search import MyDashTabPlotter4Search
from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_dash.my_dash_colors import DashColorHandler
from salesman_tutti.tutti import Tutti
from salesman_tutti.tutti_categorizer import ProductCategorizer
from factories.salesman_sale_factory import SalesmanSaleFactory
from salesman_dash.callbacks.callbacks_for_search import CallbackForSearchInput, CallbackForResultGrid
from salesman_search import SalesmanSearchApi
import pandas as pd
from caching.salesman_cache import CKEY
from salesman_dash.my_dash_tab_elements import MyDashTabElements4Search


class MyDashTab4Search(MyDashBaseTab):
    def __init__(self, app: Dash, sys_config: SystemConfiguration, tutti: Tutti):
        MyDashBaseTab.__init__(self, app)
        self.sys_config = sys_config
        self.tutti = tutti
        self._salesman_spacy = self.tutti.salesman_spacy
        self._sale_table = self.sys_config.sale_table
        self._sale_factory = SalesmanSaleFactory(self.sys_config, self._salesman_spacy)
        self._dd_handler = SearchTabDropDownHandler(self.sys_config)
        self._color_handler = self.__get_color_handler__()
        self._header_table = MyHTMLTabSearchHeaderTable()
        self._search_results_grid_table = MySearchResultTable(self.sys_config)
        self._search_online_input_table = MyHTMLSearchOnlineInputTable(self._dd_handler)
        self._selected_search_result_row = None
        self._search_input = ''
        self._online_rows = None
        self._entity_search_lists = []
        self._product_categorizer = ProductCategorizer()
        self._plot_category_list = []
        self._plot_category_options = []
        self._elements = MyDashTabElements4Search(self._dd_handler, self._search_online_input_table)
        self._callback_for_search_input = CallbackForSearchInput(self._elements, self._sale_factory)
        # self._callback_for_search_input.print_details()
        self._callback_for_search_input_markdown = CallbackForSearchInput(self._elements, self._sale_factory)
        self._callback_for_result_grid = CallbackForResultGrid(self._elements, self._sale_factory)

    def __get_color_handler__(self):
        return DashColorHandler()

    def get_div_for_tab(self):
        children_list = [
            self._header_table.get_table(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_SOURCE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_REGION)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_CATEGORY)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_SUB_CATEGORY)),
            MyHTML.div_with_html_button_submit(self._elements.my_search_refresh_button, children='Refresh', hidden=''),
            MyHTML.div_with_html_element(
                self._elements.my_search_online_input_table, self._search_online_input_table.get_table()),
            MyDCC.markdown(self._elements.my_search_input_markdown),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_ENTITIES)),
            MyHTML.div_with_button_link(self._elements.my_search_result_entry_link, href='', title='', hidden='hidden'),
            MyDCC.markdown(self._elements.my_search_test_markdown),
            MyHTML.div_with_table(self._elements.my_search_result_grid_table_div, ''),
            MyDCC.markdown(self._elements.my_search_result_entry_markdown),
            MyHTML.div(self._elements.my_search_result_graph_div, '', False),
        ]
        return MyHTML.div(self._elements.my_search_div, children_list)

    def init_callbacks(self):
        self.__init_callback_for_search_markdown__()
        self.__init_callback_for_search_input__()
        self.__init_callback_for_search_input_markdown__()
        self.__init_callback_for_search_result_grid_table__()
        self.__init_callbacks_for_search_result_entry_link__()
        self.__init_callback_for_search_result_entry_markdown__()
        self.__init_callbacks_for_search_result_numbers__()
        self.__init_callback_for_search_result_graph__()
        self.__init_callback_for_product_sub_categories__()
        self.__init_callbacks_for_filter_by_entities__()
        self.__init_callbacks_for_drop_down_values__()

    def __init_callbacks_for_filter_by_entities__(self):
        @self.app.callback(
            Output(self._dd_handler.get_embracing_div_id(SRDD.SEARCH_ENTITIES), DSHVT.STYLE),
            [Input(self._elements.my_search_result_graph_div, DSHVT.CHILDREN)])
        def handle_callback_for_search_filter_by_entities_visibility(children):
            # print('children={}'.format(children))
            if len(children) == 0:
                return {'display': 'none'}
            return self._dd_handler.get_style_display(SRDD.SEARCH_ENTITIES)

        @self.app.callback(
            Output(self._dd_handler.my_search_entities_dd, DSHVT.OPTIONS),
            [Input(self._elements.my_search_result_grid_table_div, DSHVT.CHILDREN)])
        def handle_callback_for_search_filter_by_entities_options(children):
            if len(children) == 0:
                return []
            self._plot_category_list = self.tutti.printing.plot_category_list
            if len(self._plot_category_options) == 0:
                self._plot_category_options = [{'label': PRCAT.ALL, 'value': PRCAT.ALL}]
                for category in self._plot_category_list:
                    label = category.replace('_', ' (') + ')'
                    value = category
                    self._plot_category_options.append({'label': label, 'value': value})
            return self._plot_category_options

        @self.app.callback(
            Output(self._elements.my_search_test_markdown, DSHVT.CHILDREN),
            [Input(self._dd_handler.my_search_entities_dd, DSHVT.VALUE)])
        def handle_callback_for_search_print_category_markdown(category: str):
            return category

    def __init_callbacks_for_search_result_entry_link__(self):
        @self.app.callback(
            Output(self._elements.my_search_result_entry_link, DSHVT.HIDDEN),
            [Input(self._elements.my_search_result_grid_table, DSHVT.ROWS),
             Input(self._elements.my_search_result_grid_table, DSHVT.SELECTED_ROW_INDICES)])
        def handle_callback_for_search_result_entry_link_visibility(rows: list, selected_row_indices: list):
            if selected_row_indices is None or len(selected_row_indices) == 0:
                self._selected_search_result_row = None
                return 'hidden'
            self._selected_search_result_row = rows[selected_row_indices[0]]
            return ''

        @self.app.callback(
            Output(self._elements.my_search_result_entry_link, DSHVT.CHILDREN),
            [Input(self._elements.my_search_result_entry_link, DSHVT.HIDDEN)])
        def handle_callback_for_search_result_entry_link_text(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            button_text = MyText.get_next_best_abbreviation(self._selected_search_result_row[SLDC.TITLE], 30)
            return MyHTML.button_submit('my_link_button', 'Open "{}"'.format(button_text), '')

        @self.app.callback(
            Output(self._elements.my_search_result_entry_link, DSHVT.HREF),
            [Input(self._elements.my_search_result_entry_link, DSHVT.HIDDEN)])
        def handle_callback_for_search_result_entry_link_href(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            return self._selected_search_result_row[SLDC.HREF]

    def __init_callbacks_for_search_result_numbers__(self):
        @self.app.callback(
            Output(self._header_table.my_search_found_valid_value_div, DSHVT.CHILDREN),
            [Input(self._elements.my_search_result_grid_table, DSHVT.ROWS)])
        def handle_callback_for_search_result_numbers_valid(rows: list):
            if len(rows) == 0:
                return 0
            rows_valid = [row for row in rows if not row[SLDC.IS_OUTLIER]]
            return len(rows_valid)

        @self.app.callback(
            Output(self._header_table.my_search_found_all_value_div, DSHVT.CHILDREN),
            [Input(self._elements.my_search_result_grid_table, DSHVT.ROWS)])
        def handle_callback_for_search_result_numbers_all(rows: list):
            return len(rows)

    def __handle_refresh_click__(self, refresh_n_clicks: int):
        if self._refresh_button_clicks == refresh_n_clicks:
            return
        self._refresh_button_clicks = refresh_n_clicks
        self._search_results_grid_table = MySearchResultTable(self.sys_config)

    def __init_callback_for_product_sub_categories__(self):
        @self.app.callback(
            Output(self._dd_handler.my_search_sub_category_dd, DSHVT.OPTIONS),
            [Input(self._dd_handler.my_search_category_dd, DSHVT.VALUE)])
        def handle_callback_for_product_sub_categories(value: str):
            category = self._product_categorizer.get_category_for_value(value)
            self._dd_handler.selected_search_category = category
            return self._product_categorizer.get_sub_category_lists_for_category_as_option_list(category)

    def __init_callback_for_search_result_grid_table__(self):
        @self.app.callback(
            Output(self._elements.my_search_result_grid_table_div, DSHVT.CHILDREN),
            [Input(self._elements.my_search_button, DSHVT.N_CLICKS),
             Input(self._elements.my_search_db_button, DSHVT.N_CLICKS),
             Input(self._elements.my_search_file_button, DSHVT.N_CLICKS),
             Input(self._elements.my_search_entities_dd, DSHVT.VALUE),
             ],
            [State(self._elements.my_search_source_dd, DSHVT.VALUE),
             State(self._elements.my_search_region_dd, DSHVT.VALUE),
             State(self._elements.my_search_category_dd, DSHVT.VALUE),
             State(self._elements.my_search_sub_category_dd, DSHVT.VALUE),
             State(self._elements.my_search_input, DSHVT.VALUE),
             State(self._elements.my_search_db_dd, DSHVT.VALUE),
             State(self._elements.my_search_file_dd, DSHVT.VALUE),
             ]
        )
        def handle_callback_for_search_result_grid_table(*params):
            self._callback_for_result_grid.set_values(*params)
            if not self.sys_config.is_http_connection_ok:  # this parameter is updated during the set_values...
                return 'SORRY - no internet connection at the moment - please check your WLAN'
            self._online_rows = None
            clicked_button = self._callback_for_result_grid.get_clicked_button()
            if clicked_button is None:
                if self._callback_for_result_grid.has_value_been_changed_for_parameter(
                        self._elements.my_search_entities_dd):
                    return self.__get_search_result_grid_table_by_selected_entities__(
                        self._callback_for_result_grid.get_parameter_value(self._elements.my_search_entities_dd)
                    )
            else:
                search_input = self._callback_for_result_grid.get_actual_search_value()
                self._plot_category_list = []
                self._plot_category_options = []
                self._selected_entities_as_list = []
                if clicked_button.name == self._elements.my_search_button:
                    return self.__get_search_result_grid_table_by_online_search__(search_input)
                elif clicked_button.name == self._elements.my_search_db_button:
                    return self.__get_search_result_grid_table_by_db_search__(
                        self._callback_for_result_grid.get_selected_db_row_id())
                elif clicked_button.name == self._elements.my_search_file_button:
                    return self.__get_search_result_grid_table_by_file_search__(
                        self._callback_for_result_grid.get_selected_file_row_number()
                    )
            return ''

    def __init_callback_for_search_result_entry_markdown__(self):
        @self.app.callback(
            Output(self._elements.my_search_result_entry_markdown, DSHVT.CHILDREN),
            [Input(self._elements.my_search_result_grid_table, DSHVT.SELECTED_ROW_INDICES)],
            [State(self._elements.my_search_result_grid_table, DSHVT.ROWS)]
        )
        def handle_callback_for_search_result_entry_markdown(selected_row_indices: list, rows):
            if selected_row_indices is None or len(selected_row_indices) == 0:
                return ''
            selected_row = rows[selected_row_indices[0]]
            # print('selected_row={}/type={}'.format(selected_row, type(selected_row)))
            column_value_list = ['_**{}**_: {}'.format(col, selected_row[col]) for col in selected_row]
            return '  \n'.join(column_value_list)

    def __init_callback_for_search_markdown__(self):
        @self.app.callback(
            Output(self._header_table.my_search_markdown, DSHVT.CHILDREN),
            [Input(self._elements.my_search_result_grid_table_div, DSHVT.CHILDREN)])
        def handle_callback_for_search_markdown(search_result_grid_table):
            if self._search_input == '':
                return '**Please enter search string**'
            return self.__get_search_markdown_for_online_search__()

    def __init_callback_for_search_input__(self):
        @self.app.callback(
            Output(self._search_online_input_table.my_search_input, DSHVT.VALUE),
            [Input(self._elements.my_search_input, DSHVT.N_BLUR),
             Input(self._elements.my_search_button, DSHVT.N_CLICKS),
             Input(self._elements.my_search_db_button, DSHVT.N_CLICKS),
             Input(self._elements.my_search_file_button, DSHVT.N_CLICKS)],
            [State(self._elements.my_search_input, DSHVT.VALUE),
             State(self._elements.my_search_db_dd, DSHVT.VALUE),
             State(self._elements.my_search_file_dd, DSHVT.VALUE)]
        )
        def handle_callback_for_search_input(*params):
            self._callback_for_search_input.set_values(*params)
            # self._callback_for_search_input.print_details()
            actual_search_value = self._callback_for_search_input.get_actual_search_value()
            if actual_search_value == '':
                return self.sys_config.shelve_cache.get_value(CKEY.SEARCH_INPUT)
            else:
                self.sys_config.shelve_cache.set_value(CKEY.SEARCH_INPUT, actual_search_value)
            return actual_search_value

    def __init_callback_for_search_input_markdown__(self):
        @self.app.callback(
            Output(self._elements.my_search_input_markdown, DSHVT.CHILDREN),
            [Input(self._elements.my_search_input, DSHVT.N_BLUR),
             Input(self._elements.my_search_button, DSHVT.N_CLICKS),
             Input(self._elements.my_search_db_button, DSHVT.N_CLICKS),
             Input(self._elements.my_search_file_button, DSHVT.N_CLICKS)],
            [State(self._elements.my_search_input, DSHVT.VALUE),
             State(self._elements.my_search_db_dd, DSHVT.VALUE),
             State(self._elements.my_search_file_dd, DSHVT.VALUE)]
            )
        def handle_callback_for_search_markdown(*params):
            self._callback_for_search_input_markdown.set_values(*params)
            actual_search_value = self._callback_for_search_input_markdown.get_actual_search_value()
            if actual_search_value == '':
                return ''
            prefix_doc_dict = {'Original': self._salesman_spacy.nlp_sm(actual_search_value),
                               'Modified': self._salesman_spacy.nlp(actual_search_value)}
            value_list_dict = {prefix: SalesmanSpacy.get_sorted_entity_label_values_for_doc(doc)
                               for prefix, doc in prefix_doc_dict.items()}
            value_joined_list = ['**{}**: {}'.format(prefix, values) for prefix, values in value_list_dict.items()]
            return '  \n'.join(value_joined_list)

    def __init_callback_for_search_result_graph__(self):
        @self.app.callback(
            Output(self._elements.my_search_result_graph_div, DSHVT.CHILDREN),
            [Input(self._elements.my_search_result_grid_table_div, DSHVT.CHILDREN)])
        def handle_callback_for_search_result_graph(children):
            if self._online_rows is None or len(self._online_rows) == 0:
                return ''
            return self.__get_scatter_plot__()

    def __init_callbacks_for_drop_down_values__(self):
        @self.app.callback(
            Output(self._elements.my_search_db_dd, DSHVT.OPTIONS),
            [Input(self._elements.my_search_refresh_button, DSHVT.N_CLICKS)])
        def handle_callback_for_search_result_graph(n_clicks: int):
            return self.sys_config.access_layer_sale.get_my_sales_as_dd_options()

        @self.app.callback(
            Output(self._elements.my_search_file_dd, DSHVT.OPTIONS),
            [Input(self._elements.my_search_refresh_button, DSHVT.N_CLICKS)])
        def handle_callback_for_search_result_graph(n_clicks: int):
            return self.sys_config.access_layer_file.get_my_sales_as_dd_options(with_refresh=True)

    def __get_scatter_plot__(self):
        df_search_result = self.tutti.printing.df_sale
        # MyPandas.print_df_details(df_search_result)
        plotter = MyDashTabPlotter4Search(df_search_result, self._color_handler)
        chart_title = self._callback_for_search_input.get_actual_search_value()
        scatter_chart = plotter.get_chart_type_scatter(chart_title)
        return scatter_chart

    def __get_search_markdown_for_online_search__(self):
        my_sale = '**Searching for**: {}'.format(self._search_input)
        searching_by = '{}'.format(self._entity_search_lists)
        my_entity_search_lists = '**Searching by**: {}'.format(MyText.get_text_for_markdown(searching_by))
        if self._online_rows is None or len(self._online_rows) == 0:
            return '  \n'.join([my_sale, my_entity_search_lists, '**NO RESULTS FOUND**'])
        outlier_online_search = self.__get_outlier_for_online_search__()
        return self.__get_search_markdown_with_outlier__(my_sale, my_entity_search_lists, outlier_online_search)

    @staticmethod
    def __get_search_markdown_with_outlier__(my_sale: str, my_entity_search_lists: str, outlier_online_search: Outlier):
        prices = outlier_online_search.get_markdown_text()
        price_suggested = outlier_online_search.mean_values_without_outliers
        my_price_suggested = '**Price suggested**: {:.2f}'.format(price_suggested)
        return '  \n'.join([my_sale, my_entity_search_lists, prices, my_price_suggested])

    def __get_outlier_for_online_search__(self) -> Outlier:
        df_results = pd.DataFrame.from_dict(self._online_rows)
        price_single_list = [0] if df_results.shape[0] == 0 else list(df_results[SLDC.PRICE_SINGLE])
        outlier = Outlier(price_single_list, self.sys_config.outlier_threshold)
        return outlier

    def __get_search_result_grid_table_by_selected_entities__(self, selected_entity_values: list):
        self._online_rows = self.tutti.get_search_results_by_selected_entities(selected_entity_values)
        return self.__get_search_result_grid_table__()

    def __get_search_result_grid_table_by_online_search__(self, search_input: str):
        self._search_input = search_input
        return self.__get_search_result_table_by_api__()

    def __get_search_result_table_by_api__(self):
        api = SalesmanSearchApi(self._search_input)
        region_value = self._callback_for_result_grid.get_parameter_value(
            self._elements.my_search_region_dd)
        category_value = self._callback_for_result_grid.get_parameter_value(
            self._elements.my_search_category_dd)
        sub_category_value = self._callback_for_result_grid.get_parameter_value(
            self._elements.my_search_sub_category_dd)
        api.region_value = '' if region_value == 'ganze-schweiz' else region_value
        api.category_value = '' if category_value == PRCAT.ALL else category_value
        api.sub_category_value = '' if api.category_value == '' or sub_category_value == PRSUBCAT.ALL \
            else sub_category_value
        self._online_rows = self.tutti.get_search_results_by_search_api(api)
        self._entity_search_lists = self.tutti.get_entity_based_search_lists()
        return self.__get_search_result_grid_table__()

    def __get_search_result_grid_table_by_db_search__(self, row_id: int):
        sale = self._sale_factory.get_sale_from_db_by_row_id(row_id)
        self._search_input = sale.title
        return self.__get_search_result_table_by_api__()

    def __get_search_result_grid_table_by_file_search__(self, file_row_number: int):
        sale = self._sale_factory.get_sale_from_file_by_row_number(file_row_number)
        self._search_input = sale.title
        return self.__get_search_result_table_by_api__()

    def __get_search_result_grid_table__(self):
        if len(self._online_rows) == 0:
            return 'Nothing found - please adjust your query...'
        columns = SLDC.get_columns_for_search_results()
        return MyDCC.data_table(self._elements.my_search_result_grid_table, self._online_rows, columns=columns)
