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
from sertl_analytics.mycache import MyCacheObjectApi, MyCache
from pattern_dash.my_dash_tab_dd_for_waves import WaveTabDropDownHandler, WAVEDD
from pattern_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter4Waves
from pattern_detection_controller import PatternDetectionController
from pattern_dash.my_dash_colors import DashColorHandler
from dash import Dash
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import WAVEST, PRD, INDICES
from pattern_news_handler import NewsHandler


class MyDashTab4Waves(MyDashBaseTab):
    _data_table_name = 'my_waves_table'
    _data_table_div = '{}_div'.format(_data_table_name)

    def __init__(self, app: Dash, sys_config: SystemConfiguration, color_handler: DashColorHandler):
        MyDashBaseTab.__init__(self, app, sys_config)
        self._dd_handler = WaveTabDropDownHandler()
        self.sys_config = self.__get_adjusted_sys_config_copy__(sys_config)
        self.__init_dash_element_ids__()
        self._dash_color_handler = color_handler
        self._pattern_controller = PatternDetectionController(self.sys_config)
        self._heat_map_was_updated = False
        self._head_map_cache = MyCache()
        self._index_chart_cache = MyCache()

        # self._wave_table = WaveTabTable(self._waves_data_frame_dict, 'log_type', 'date_range')

    @staticmethod
    def __get_adjusted_sys_config_copy__(sys_config: SystemConfiguration) -> SystemConfiguration:
        sys_config_copy = sys_config.get_semi_deep_copy()  # we need some adjustments (_period, etc...)
        sys_config_copy.data_provider.from_db = True
        sys_config_copy.data_provider.period = PRD.DAILY
        sys_config_copy.data_provider.aggregation = 1
        sys_config_copy.data_provider.and_clause = ''
        sys_config_copy.data_provider.limit = WaveTabDropDownHandler.get_max_retrospective_ticks()
        return sys_config_copy

    def __init_dash_element_ids__(self):
        self._my_waves_period_selection = self._dd_handler.my_waves_period_selection_id
        self._my_waves_aggregation_selection = self._dd_handler.my_waves_aggregation_selection_id
        self._my_waves_retrospective_ticks_selection = self._dd_handler.my_waves_retrospective_ticks_selection_id
        self._my_waves_index_selection = self._dd_handler.my_waves_index_selection_id
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
                WAVEDD.PERIOD, default_value=self._dd_handler.selected_period)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(
                WAVEDD.AGGREGATION, default_value=self._dd_handler.selected_aggregation)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(
                WAVEDD.RETROSPECTIVE_TICKS, default_value=self._dd_handler.selected_retrospective_ticks)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(
                WAVEDD.INDICES, default_value=self._dd_handler.selected_index)),
            MyHTML.div(self._my_waves_heatmap_div, self.__get_heatmap__()),
            MyHTML.div(self._my_waves_index_chart_div, self.__get_graph_for_index__(self._dd_handler.selected_index)),
            MyDCC.markdown(self._my_waves_entry_markdown)
        ]
        return MyHTML.div('my_waves_div', children_list)

    def __get_heatmap__(self):
        cache_key = self.__get_id_for_caches__()
        heat_map = self._head_map_cache.get_cached_object_by_key(cache_key)
        if heat_map is None:
            plotter = MyDashTabStatisticsPlotter4Waves(
                wave_handler=self._fibonacci_wave_handler,
                color_handler=self._dash_color_handler,
                retrospective_ticks=self._dd_handler.selected_retrospective_ticks,
                index=self._dd_handler.selected_index)
            heat_map = plotter.get_chart_list()
            self.__add_element_to_cache__(self._head_map_cache, cache_key, heat_map)
        return heat_map

    def init_callbacks(self):
        # self.__init_callback_for_waves_header_table__()
        self.__init_callbacks_for_waves_heatmap__()
        self.__init_callbacks_for_waves_index_chart__()

    def __init_callbacks_for_waves_heatmap__(self):
        @self.app.callback(
            Output(self._my_waves_heatmap_div, 'children'),
            [Input('my_interval_refresh', 'n_intervals'),
             Input(self._my_waves_period_selection, 'value'),
             Input(self._my_waves_aggregation_selection, 'value'),
             Input(self._my_waves_retrospective_ticks_selection, 'value'),
             Input(self._my_waves_index_selection, 'value')],
            [State(self._my_waves_heatmap_div, 'children')])
        def handle_callback_for_position_manage_button_hidden(n_intervals: int, period: str, aggregation: int,
                                                              ticks: int, index: str, children):
            if self._fibonacci_wave_handler.are_data_actual and not self._dd_handler.was_any_value_changed(
                    period, aggregation, ticks, index):
                self._heat_map_was_updated = False
                print('Return old heatmap...')
                return children
            if not self._fibonacci_wave_handler.are_data_actual:
                self._fibonacci_wave_handler.reload_data()
            self._heat_map_was_updated = True
            self._fibonacci_wave_handler.set_retrospective_tick_number(ticks)
            return self.__get_heatmap__()

    def __init_callbacks_for_waves_index_chart__(self):
        @self.app.callback(
            Output(self._my_waves_index_chart_div, 'children'),
            [Input(self._my_waves_heatmap_div, 'children')],
            [State(self._my_waves_index_chart_div, 'children')])
        def handle_callback_for_waves_index_chart(heatmap, children):
            if not self._heat_map_was_updated:
                print('Return old index chart...')
                return children
            return self.__get_graph_for_index__(self._dd_handler.selected_index)

    def __get_graph_for_index__(self, index: str):
        if index in ['', INDICES.ALL]:
            return ''
        ticker = INDICES.get_ticker_for_index(index)
        cache_key = self.__get_id_for_caches__()
        graph = self._index_chart_cache.get_cached_object_by_key(cache_key)
        if graph is None:
            graph, graph_key = self.__get_graph__(ticker, limit=self._dd_handler.selected_retrospective_ticks)
            self.__add_element_to_cache__(self._index_chart_cache, cache_key, graph)
        return graph

    @staticmethod
    def __add_element_to_cache__(cache, cache_key, element):
        cache_api = MyCacheObjectApi()
        cache_api.object = element
        cache_api.key = cache_key
        cache_api.valid_until_ts = MyDate.get_offset_timestamp(hours=6)
        cache.add_cache_object(cache_api)

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
            return self.sys_config.fibonacci_wave_handler.\
                get_waves_numbers_with_dates_for_wave_type_and_index_for_days(wave_type, index)
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

    def __get_id_for_caches__(self):
        return '{}-{}-{}-{}'.format(self._dd_handler.selected_period,
                                    self._dd_handler.selected_aggregation,
                                    self._dd_handler.selected_retrospective_ticks,
                                    self._dd_handler.selected_index)
