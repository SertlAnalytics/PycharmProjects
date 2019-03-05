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
from pattern_dash.my_dash_header_tables import MyHTMLTabWavesHeaderTable
from pattern_dash.my_dash_tab_dd_for_waves import WaveTabDropDownHandler, WAVEDD
from pattern_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter4Waves
from pattern_detection_controller import PatternDetectionController
from pattern_dash.my_dash_colors import DashColorHandler
from dash import Dash
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import WAVEST, DC, PRD, INDICES
from fibonacci.fibonacci_wave_handler import FibonacciWaveHandler
from pattern_news_handler import NewsHandler


class MyDashTab4Waves(MyDashBaseTab):
    _data_table_name = 'my_waves_table'
    _data_table_div = '{}_div'.format(_data_table_name)

    def __init__(self, app: Dash, sys_config: SystemConfiguration, color_handler: DashColorHandler):
        MyDashBaseTab.__init__(self, app, sys_config)
        self.sys_config = self.__get_adjusted_sys_config_copy__(sys_config)
        self.__init_dash_element_ids__()
        self._retrospective_days_selected = 100
        self._index_selected = INDICES.DOW_JONES
        self._threshold_index_selected = 10
        self._threshold_single_selected = 1
        self._fibonacci_wave_handler = FibonacciWaveHandler(self._retrospective_days_selected)
        self._dash_color_handler = color_handler
        self._pattern_controller = PatternDetectionController(self.sys_config)
        self._dd_handler = WaveTabDropDownHandler()
        # self._wave_table = WaveTabTable(self._waves_data_frame_dict, 'log_type', 'date_range')

    @staticmethod
    def __get_adjusted_sys_config_copy__(sys_config: SystemConfiguration) -> SystemConfiguration:
        sys_config_copy = sys_config.get_semi_deep_copy()  # we need some adjustments (_period, etc...)
        sys_config_copy.data_provider.from_db = True
        sys_config_copy.data_provider.period = PRD.DAILY
        sys_config_copy.data_provider.aggregation = 1
        return sys_config_copy

    def __init_dash_element_ids__(self):
        self._my_waves_retrospective_days_selection = 'my_waves_retrospective_days_selection'
        self._my_waves_threshold_index_selection = 'my_waves_threshold_index_selection'
        self._my_waves_threshold_single_selection = 'my_waves_threshold_single_selection'
        self._my_waves_index_selection = 'my_waves_index_selection'
        self._my_waves_heatmap_div = 'my_waves_heatmap_div'
        self._my_waves_index_chart_div = 'my_waves_index_chart_div'
        self._my_waves_entry_markdown = 'my_waves_entry_markdown'

    @staticmethod
    def __get_news_handler__():
        return NewsHandler('  \n', '')

    def get_div_for_tab(self):
        children_list = [
            # MyHTMLTabWavesHeaderTable().get_table(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(
                WAVEDD.RETROSPECTIVE_DAYS, default_value=self._retrospective_days_selected)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(
                WAVEDD.THRESHOLD_INDEX, default_value=self._threshold_index_selected)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(
                WAVEDD.THRESHOLD_SINGLE, default_value=self._threshold_single_selected)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(
                WAVEDD.INDICES, default_value=self._index_selected)),
            MyHTML.div(self._my_waves_heatmap_div, self.__get_heatmap__()),
            MyHTML.div(self._my_waves_index_chart_div, self.__get_graph_for_index__(self._index_selected)),
            MyDCC.markdown(self._my_waves_entry_markdown)
        ]
        return MyHTML.div('my_waves_div', children_list)

    def __get_heatmap__(self):
        plotter = MyDashTabStatisticsPlotter4Waves(
            self._fibonacci_wave_handler, self._dash_color_handler, self._retrospective_days_selected)
        return plotter.get_chart_list()

    def init_callbacks(self):
        # self.__init_callback_for_waves_header_table__()
        self.__init_callbacks_for_waves_heatmap__()
        self.__init_callbacks_for_waves_index_chart__()

    def __init_callbacks_for_waves_heatmap__(self):
        @self.app.callback(
            Output(self._my_waves_heatmap_div, 'children'),
            [Input('my_interval_refresh', 'n_intervals'),
             Input(self._my_waves_retrospective_days_selection, 'value')],
            [State(self._my_waves_heatmap_div, 'children')])
        def handle_callback_for_position_manage_button_hidden(n_intervals: int, days: int, children):
            if self._fibonacci_wave_handler.are_data_actual and self._retrospective_days_selected == days:
                print('Return old heatmap...')
                return children
            if not self._fibonacci_wave_handler.are_data_actual:
                self._fibonacci_wave_handler.reload_data()
            self._retrospective_days_selected = days
            self._fibonacci_wave_handler.init_list_and_dictionaries_for_retrospective_days(days)
            return self.__get_heatmap__()

    def __init_callbacks_for_waves_index_chart__(self):
        @self.app.callback(
            Output(self._my_waves_index_chart_div, 'children'),
            [Input(self._my_waves_index_selection, 'value')],
            [State(self._my_waves_index_chart_div, 'children')])
        def handle_callback_for_waves_index_chart(index: str, children):
            if self._index_selected == index:
                print('Return old index chart...')
                return children
            self._index_selected = index
            return self.__get_graph_for_index__(index)

    def __get_graph_for_index__(self, index: str):
        ticker = INDICES.get_ticker_for_index(index)
        graph, graph_key = self.__get_graph__(ticker, limit=self._retrospective_days_selected)
        return graph

    def __get_graph__(self, ticker_id: str, limit=400):
        period = self.sys_config.period
        aggregation = self.sys_config.period_aggregation
        graph_cache_id = self.sys_config.graph_cache.get_cache_id(ticker_id, period, aggregation, limit)
        graph = self.sys_config.graph_cache.get_cached_object_by_key(graph_cache_id)
        if graph is not None:
            return graph, graph_cache_id
        self.sys_config.data_provider.from_db = True
        date_start = MyDate.adjust_by_days(MyDate.get_datetime_object().date(), -limit)
        and_clause = "Date > '{}'".format(date_start)
        graph_title = self.sys_config.graph_cache.get_cache_title(ticker_id, period, aggregation, limit)
        detector = self._pattern_controller.get_detector_for_fibonacci_and_pattern(
            self.sys_config, ticker_id, and_clause, limit)
        graph_api = DccGraphApi(graph_cache_id, graph_title)
        graph_api.ticker_id = ticker_id
        graph_api.df = detector.pdh.pattern_data.df
        graph = self.__get_dcc_graph_element__(detector, graph_api)
        cache_api = self.sys_config.graph_cache.get_cache_object_api(graph_cache_id, graph, period, refresh_interval=100)
        self.sys_config.graph_cache.add_cache_object(cache_api)
        return graph, graph_cache_id

    def create_callback_for_numbers_in_header_table(self, index: str, wave_type: str):
        def callback(n_intervals: int):
            return self._fibonacci_wave_handler.get_waves_numbers_with_dates_for_wave_type_and_index_for_days(
                wave_type, index)
        return callback

    def __init_callback_for_waves_header_table__(self):
        column = 1
        for wave_type in WAVEST.get_waves_types_for_processing():
            column += 1
            row = 1
            for index in INDICES.get_index_list_for_waves_tab():
                row += 1
                output_element = 'my_waves_{}_{}_value_div'.format(row, column)
                dynamically_generated_function = self.create_callback_for_numbers_in_header_table(index, wave_type)
                self.app.callback(Output(output_element, 'children'), [Input('my_interval_refresh', 'n_intervals')])\
                    (dynamically_generated_function)
