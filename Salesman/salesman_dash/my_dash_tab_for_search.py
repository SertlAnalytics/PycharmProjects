"""
Description: This module contains the dash tab for recommendations from various sources, e.g. bitfinex, Nasdaq...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""

from dash.dependencies import Input, Output, State
from calculation.outlier import Outlier
from sertl_analytics.mydash.my_dash_base_tab import MyDashBaseTab
from salesman_tutti.tutti_constants import PRCAT, PRSUBCAT
from sertl_analytics.mydash.my_dash_components import MyDCC, MyHTML
from salesman_dash.header_tables.my_tab_header_table_4_search import MyHTMLTabSearchHeaderTable
from salesman_dash.input_tables.my_online_sale_table import MyHTMLSearchOnlineInputTable
from salesman_dash.my_dash_tab_dd_for_search import SearchTabDropDownHandler, SRDD
from dash import Dash
from sertl_analytics.my_text import MyText
from sertl_analytics.constants.salesman_constants import SLDC
from salesman_dash.grid_tables.my_grid_table_sale_4_search_results import MySearchResultTable
from salesman_system_configuration import SystemConfiguration
from salesman_dash.plotting.my_dash_plotter_for_salesman_search import MyDashTabPlotter4Search
from salesman_dash.my_dash_colors import DashColorHandler
from salesman_tutti.tutti import Tutti
from salesman_tutti.tutti_categorizer import ProductCategorizer
from salesman_sale_factory import SalesmanSaleFactory
from salesman_dash.callbacks.callbacks_for_search import CallbackForSearchInput
from salesman_search import SalesmanSearchApi
import pandas as pd
from caching.salesman_cache import CKEY
from salesman_dash.my_dash_tab_elements import MyDashTabElements4Search


class SearchHandler:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self._print_category_list = []
        self._print_category_options = []
        self._print_category_selected_as_list = []


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
        self._product_categorizer = ProductCategorizer()
        self._print_category_list = []
        self._print_category_options = []
        self._selected_entities_as_list = []
        self._elements = MyDashTabElements4Search(self._dd_handler, self._search_online_input_table)
        self._callback_for_search_input = CallbackForSearchInput(self._elements, self._sale_factory)

    def __get_color_handler__(self):
        return DashColorHandler()

    def get_div_for_tab(self):
        children_list = [
            self._header_table.get_table(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_SOURCE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_REGION)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_CATEGORY)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_SUB_CATEGORY)),
            MyHTML.div_with_html_element(
                self._elements.my_search_online_input_table, self._search_online_input_table.get_table()),
            MyDCC.markdown(self._elements.my_search_input_markdown),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_ENTITIES)),
            MyHTML.div_with_button_link(self._elements.my_search_result_entry_link, href='', title='', hidden='hidden'),
            MyDCC.markdown(self._elements.my_search_test_markdown),
            MyHTML.div(self._elements.my_search_result_grid_table_div, '', False),
            MyDCC.markdown(self._elements.my_search_result_entry_markdown),
            MyHTML.div(self._elements.my_search_result_graph_div, '', False),
        ]
        return MyHTML.div(self._elements.my_search_div, children_list)

    def init_callbacks(self):
        self.__init_callback_for_search_markdown__()
        self.__init_callback_for_search_input_markdown__()
        self.__init_callback_for_search_result_grid_table__()
        self.__init_callback_for_search_input__()  # this has to be AFTER search_result_grid_table !!!! it is the first
        self.__init_callbacks_for_search_result_entry_link__()
        self.__init_callback_for_search_result_entry_markdown__()
        self.__init_callbacks_for_search_result_numbers__()
        self.__init_callback_for_search_result_graph__()
        self.__init_callback_for_product_sub_categories__()
        self.__init_callbacks_for_search_print_category__()

    def __init_callbacks_for_search_print_category__(self):
        @self.app.callback(
            Output(self._dd_handler.get_embracing_div_id(self._dd_handler.my_search_entities_dd), 'style'),
            [Input(self._elements.my_search_result_graph_div, 'children')])
        def handle_callback_for_search_print_category_visibility(children):
            print('children={}'.format(children))
            if len(children) == 0:
                return {'display': 'none'}
            return self._dd_handler.get_style_display(self._dd_handler.my_search_entities_dd)

        @self.app.callback(
            Output(self._dd_handler.my_search_entities_dd, 'options'),
            [Input(self._elements.my_search_result_graph_div, 'children')])
        def handle_callback_for_search_print_category_options(children):
            if len(children) == 0:
                return []
            if len(self._print_category_options) == 0:
                self._print_category_options = [{'label': PRCAT.ALL, 'value': PRCAT.ALL}]
                for idx, category in enumerate(self._print_category_list):
                    self._print_category_options.append(
                        {'label': '{}-{}'.format(idx + 1, MyText.get_option_label(category)), 'value': '{}'.format(idx)}
                    )
            return self._print_category_options

        @self.app.callback(
            Output(self._elements.my_search_test_markdown, 'children'),
            [Input(self._dd_handler.my_search_entities_dd, 'value')])
        def handle_callback_for_search_print_category_markdown(category: str):
            return category

    def __init_callbacks_for_search_result_entry_link__(self):
        @self.app.callback(
            Output(self._elements.my_search_result_entry_link, 'hidden'),
            [Input(self._elements.my_search_result_grid_table, 'rows'),
             Input(self._elements.my_search_result_grid_table, 'selected_row_indices')])
        def handle_callback_for_search_result_entry_link_visibility(rows: list, selected_row_indices: list):
            if len(selected_row_indices) == 0:
                self._selected_search_result_row = None
                return 'hidden'
            self._selected_search_result_row = rows[selected_row_indices[0]]
            return ''

        @self.app.callback(
            Output(self._elements.my_search_result_entry_link, 'children'),
            [Input(self._elements.my_search_result_entry_link, 'hidden')])
        def handle_callback_for_search_result_entry_link_text(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            button_text = MyText.get_next_best_abbreviation(self._selected_search_result_row[SLDC.TITLE], 30)
            return MyHTML.button_submit('my_link_button', 'Open "{}"'.format(button_text), '')

        @self.app.callback(
            Output(self._elements.my_search_result_entry_link, 'href'),
            [Input(self._elements.my_search_result_entry_link, 'hidden')])
        def handle_callback_for_search_result_entry_link_href(button_hidden: str):
            if button_hidden == 'hidden':
                return ''
            return self._selected_search_result_row[SLDC.HREF]

    def __init_callbacks_for_search_result_numbers__(self):
        @self.app.callback(
            Output(self._header_table.my_search_found_valid_value_div, 'children'),
            [Input(self._elements.my_search_result_grid_table, 'rows')])
        def handle_callback_for_search_result_numbers_valid(rows: list):
            if len(rows) == 0:
                return 0
            rows_valid = [row for row in rows if not row[SLDC.IS_OUTLIER]]
            return len(rows_valid)

        @self.app.callback(
            Output(self._header_table.my_search_found_all_value_div, 'children'),
            [Input(self._elements.my_search_result_grid_table, 'rows')])
        def handle_callback_for_search_result_numbers_all(rows: list):
            return len(rows)

    def __handle_refresh_click__(self, refresh_n_clicks: int):
        if self._refresh_button_clicks == refresh_n_clicks:
            return
        self._refresh_button_clicks = refresh_n_clicks
        self._search_results_grid_table = MySearchResultTable(self.sys_config)

    def __init_callback_for_product_sub_categories__(self):
        @self.app.callback(
            Output(self._dd_handler.my_search_sub_category_dd, 'options'),
            [Input(self._dd_handler.my_search_category_dd, 'value')])
        def handle_callback_for_product_sub_categories(value: str):
            category = self._product_categorizer.get_category_for_value(value)
            self._dd_handler.selected_search_category = category
            return self._product_categorizer.get_sub_category_lists_for_category_as_option_list(category)

    def __init_callback_for_search_result_grid_table__(self):
        @self.app.callback(
            Output(self._elements.my_search_result_grid_table_div, 'children'),
            [Input(self._elements.my_search_button, 'n_clicks'),
             Input(self._elements.my_search_db_button, 'n_clicks'),
             Input(self._elements.my_search_file_button, 'n_clicks'),
             Input(self._elements.my_search_entities_dd, 'value'),
             ],
            [State(self._elements.my_search_source_dd, 'value'),
             State(self._elements.my_search_region_dd, 'value'),
             State(self._elements.my_search_category_dd, 'value'),
             State(self._elements.my_search_sub_category_dd, 'value'),
             State(self._elements.my_search_input, 'value'),
             State(self._elements.my_search_db_dd, 'value'),
             State(self._elements.my_search_file_dd, 'value'),
             ]
        )
        def handle_callback_for_search_result_grid_table(*params):
            print('TEST (second??): handle_callback_for_search_result_grid_table')
            self._online_rows = None
            clicked_button = self._callback_for_search_input.get_clicked_button()
            if clicked_button is None:
                if self._callback_for_search_input.has_value_been_changed_for_parameter(
                        self._elements.my_search_entities_dd):
                    self._selected_entities_as_list = self.__get_entities_by_selected_entity_indices__(
                        self._callback_for_search_input.get_parameter_value(self._elements.my_search_entities_dd))
                    return self.__get_search_result_grid_table_by_selected_entities__()
            else:
                search_input = self._callback_for_search_input.get_actual_search_value()
                self._print_category_list = []
                self._print_category_options = []
                self._selected_entities_as_list = []
                if clicked_button.name == self._elements.my_search_button:
                    return self.__get_search_result_grid_table_by_online_search__(search_input)
                elif clicked_button.name == self._elements.my_search_db_button:
                    return self.__get_search_result_grid_table_by_db_search__(
                        self._callback_for_search_input.get_selected_db_row_id())
                elif clicked_button.name == self._elements.my_search_file_button:
                    return self.__get_search_result_grid_table_by_file_search__(
                        self._callback_for_search_input.get_selected_file_row_number()
                    )
            return ''

    def __init_callback_for_search_result_entry_markdown__(self):
        @self.app.callback(
            Output(self._elements.my_search_result_entry_markdown, 'children'),
            [Input(self._elements.my_search_result_grid_table, 'selected_row_indices')],
            [State(self._elements.my_search_result_grid_table, 'rows')]
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
            [Input(self._elements.my_search_result_grid_table_div, 'children'),
             Input(self._header_table.my_search_found_valid_value_div, 'children')])
        def handle_callback_for_search_markdown(search_result_grid_table, children):
            if self._search_input == '':
                return '**Please enter search string**'
            return self.__get_search_markdown_for_online_search__()

    def __init_callback_for_search_input__(self):
        @self.app.callback(
            Output(self._search_online_input_table.my_search_input, 'value'),
            [Input(self._elements.my_search_button, 'n_clicks'),
             Input(self._elements.my_search_db_button, 'n_clicks'),
             Input(self._elements.my_search_file_button, 'n_clicks'),
             Input(self._elements.my_search_entities_dd, 'value'),
             ],
            [State(self._elements.my_search_source_dd, 'value'),
             State(self._elements.my_search_region_dd, 'value'),
             State(self._elements.my_search_category_dd, 'value'),
             State(self._elements.my_search_sub_category_dd, 'value'),
             State(self._elements.my_search_input, 'value'),
             State(self._elements.my_search_db_dd, 'value'),
             State(self._elements.my_search_file_dd, 'value'),
             ]
        )
        def handle_callback_for_search_input(*params):
            print('TEST: (first?) handle_callback_for_search_input: {}'.format(params))
            self._callback_for_search_input.set_values(*params)
            self._callback_for_search_input.print_details()
            actual_search_value = self._callback_for_search_input.get_actual_search_value()
            if actual_search_value == '':
                return self.sys_config.shelve_cache.get_value(CKEY.SEARCH_INPUT)
            else:
                self.sys_config.shelve_cache.set_value(CKEY.SEARCH_INPUT, actual_search_value)
            return actual_search_value

    def __init_callback_for_search_input_markdown__(self):
        @self.app.callback(
            Output(self._elements.my_search_input_markdown, 'children'),
            [Input(self._search_online_input_table.my_search_button, 'n_clicks'),
             Input(self._search_online_input_table.my_search_db_button, 'n_clicks'),
             Input(self._search_online_input_table.my_search_file_button, 'n_clicks')],
            )
        def handle_callback_for_search_markdown(n_clicks, n_clics_db, n_clicks_file):
            doc_nlp = self._salesman_spacy.nlp_sm(self._callback_for_search_input.get_actual_search_value())
            ent_list = ['{} ({})'.format(ent.text, ent.label_) for ent in doc_nlp.ents]
            return 'Entities (original): {}'.format(', '.join(ent_list))

    def __init_callback_for_search_result_graph__(self):
        @self.app.callback(
            Output(self._elements.my_search_result_graph_div, 'children'),
            [Input(self._elements.my_search_result_grid_table_div, 'children')])
        def handle_callback_for_search_result_graph(children):
            if self._online_rows is None:
                return ''
            return self.__get_scatter_plot__()

    def __get_entities_by_selected_entity_indices__(self, selected_entity_indices: list):
        if len(self._print_category_list) == 0 or len(selected_entity_indices) == 0 \
                or PRCAT.ALL in selected_entity_indices:
            return []
        return_list = []
        for selected_index in selected_entity_indices:
            print_category_string = self._print_category_list[int(selected_index)]
            return_list.append(print_category_string.split(': '))
        return return_list

    def __get_scatter_plot__(self):
        df_search_result = self.tutti.printing.df_sale
        # MyPandas.print_df_details(df_search_result)
        plotter = MyDashTabPlotter4Search(df_search_result, self._color_handler)
        scatter_chart = plotter.get_chart_type_scatter(self._callback_for_search_input.get_actual_search_value())
        if len(self._print_category_list) == 0:
            self._print_category_list = plotter.category_list
        return scatter_chart

    def __get_search_markdown_for_online_search__(self):
        my_sale_obj = self.tutti.current_source_sale
        my_sale = '**Searching for**: {}'.format(self._search_input)
        my_sale_obj_text = '**Found entities:** {}'.format(my_sale_obj.get_value(SLDC.ENTITY_LABELS_DICT))
        if self._online_rows is None or len(self._online_rows) == 0:
            return '  \n'.join([my_sale, my_sale_obj_text, '**NO RESULTS FOUND**'])
        outlier_online_search = self.__get_outlier_for_online_search__()
        return self.__get_search_markdown_with_outlier__(my_sale, my_sale_obj_text, outlier_online_search)

    def __get_search_markdown_with_outlier__(self, my_sale: str, my_sale_obj_text: str, outlier_online_search: Outlier):
        iqr = '- **IQR:** [{:.2f}, {:.2f}]'.format(
            outlier_online_search.bottom_threshold_iqr, outlier_online_search.top_threshold_iqr)
        prices = '**[min, bottom, mean, top, max]:** [{:.2f}, {:.2f}, **{:.2f}**, {:.2f}, {:.2f}] {}'.format(
            outlier_online_search.min_values, outlier_online_search.bottom_threshold,
            outlier_online_search.mean_values, outlier_online_search.top_threshold,
            outlier_online_search.max_values, iqr)
        price_suggested = outlier_online_search.mean_values_without_outliers
        start_search_labels = '**Search labels**: {}'.format(self.tutti.search_label_lists)
        my_price_suggested = '**Price suggested**: {:.2f}'.format(price_suggested)
        return '  \n'.join([my_sale, my_sale_obj_text, prices, my_price_suggested, start_search_labels])

    def __get_outlier_for_online_search__(self) -> Outlier:
        df_results = pd.DataFrame.from_dict(self._online_rows)
        price_single_list = [0] if df_results.shape[0] == 0 else list(df_results[SLDC.PRICE_SINGLE])
        outlier = Outlier(price_single_list, self.sys_config.outlier_threshold)
        return outlier

    def __get_search_result_grid_table_by_selected_entities__(self):
        self._online_rows = self.tutti.get_search_results_by_selected_entities(self._selected_entities_as_list)
        return self.__get_search_result_grid_table__()

    def __get_search_result_grid_table_by_online_search__(self, search_input: str):
        self._search_input = search_input
        return self.__get_search_result_table_by_api__()

    def __get_search_result_table_by_api__(self):
        api = SalesmanSearchApi(self._search_input)
        region_value = self.__get_callback_value__(self._elements.my_search_region_dd)
        category_value = self.__get_callback_value__(self._elements.my_search_category_dd)
        sub_category_value = self.__get_callback_value__(self._elements.my_search_sub_category_dd)
        api.region_value = '' if region_value == 'ganze-schweiz' else region_value
        api.category_value = '' if category_value == PRCAT.ALL else category_value
        api.sub_category_value = '' if api.category_value == '' or sub_category_value == PRSUBCAT.ALL \
            else sub_category_value
        self._online_rows = self.tutti.get_search_results_by_search_api(api)
        return self.__get_search_result_grid_table__()

    def __get_callback_value__(self, element_name: str):
        return self._callback_for_search_input.get_parameter_value(element_name)

    def __get_search_result_grid_table_by_db_search__(self, row_id: int):
        sale = self._sale_factory.get_sale_from_db_by_row_id(row_id)
        self._search_input = sale.title
        return self.__get_search_result_table_by_api__()

    def __get_search_result_grid_table_by_file_search__(self, file_row_number: int):
        sale = self._sale_factory.get_sale_from_file_by_row_number(file_row_number)
        self._search_input = sale.title
        return self.__get_search_result_table_by_api__()

    def __get_search_result_grid_table__(self):
        min_height = self._search_results_grid_table.height_for_display
        return MyDCC.data_table(self._elements.my_search_result_grid_table, self._online_rows, [], min_height=min_height)
