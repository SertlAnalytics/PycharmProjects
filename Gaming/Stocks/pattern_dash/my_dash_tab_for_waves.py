"""
Description: This module contains the dash tab for recommendations from various sources, e.g. bitfinex, Nasdaq...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""

from dash.dependencies import Input, Output, State
from pattern_dash.my_dash_base_tab_for_pattern import MyPatternDashBaseTab
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.mydash.my_dash_components import MyDCC, MyHTML, DccGraphApi, MyDCCGraph
from sertl_analytics.mycache import MyCacheObjectApi, MyCache
from pattern_dash.my_dash_tab_dd_for_waves import WaveTabDropDownHandler, WAVEDD
from pattern_dash.plotter_dash.my_dash_plotter_for_statistics_waves import MyDashTabStatisticsPlotter4Waves
from pattern_detection_controller import PatternDetectionController
from pattern_dash.my_dash_colors import DashColorHandler
from dash import Dash
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import WAVEST, PRD, INDICES, CHT, PPR
from pattern_news_handler import NewsHandler
from sertl_analytics.test.my_test_abc import TestInterface
import plotly.io as pio


class MyDashTab4Waves(MyPatternDashBaseTab):
    _data_table_name = 'my_waves_table'
    _data_table_div = '{}_div'.format(_data_table_name)

    def __init__(self, app: Dash, sys_config: SystemConfiguration, color_handler: DashColorHandler):
        MyPatternDashBaseTab.__init__(self, app, sys_config)
        self._process_for_head_map = sys_config.process_manager.get_process_by_name(PPR.UPDATE_HEATMAP_IN_WAVE_TAB)
        self.sys_config = self.__get_adjusted_sys_config_copy__(sys_config)
        self._dash_color_handler = color_handler
        self._pattern_controller = PatternDetectionController(self.sys_config)
        self._heat_map_was_updated = False
        self._index_chart_cache = MyCache()

    @staticmethod
    def __get_drop_down_handler__():
        return WaveTabDropDownHandler()

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
        self._my_waves_mood_chart_div = 'my_waves_mood_chart_div'
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
            MyHTML.div(self._my_waves_mood_chart_div, self.__get_mood_chart__()),
            MyHTML.div(self._my_waves_index_chart_div, self.__get_graph_for_index__()),
            MyDCC.markdown(self._my_waves_entry_markdown)
        ]
        return MyHTML.div('my_waves_div', children_list)

    def __get_heatmap__(self):
        @self._process_for_head_map.process_decorator
        def __get_heatmap_with_process__(process=None):
            ticks = self._dd_handler.selected_retrospective_ticks
            period = self._dd_handler.selected_period
            aggregation = self._dd_handler.selected_aggregation
            self._fibonacci_wave_data_handler.init_tick_key_list_for_retrospection(ticks, period, aggregation)
            plotter = MyDashTabStatisticsPlotter4Waves(
                wave_handler=self._fibonacci_wave_data_handler,
                color_handler=self._dash_color_handler,
                index=self._dd_handler.selected_index)
            heat_map = plotter.get_chart_list()
            return heat_map
        return __get_heatmap_with_process__()

    def __get_mood_chart__(self):
        ticks = self._dd_handler.selected_retrospective_ticks
        period = self._dd_handler.selected_period
        aggregation = self._dd_handler.selected_aggregation
        self._fibonacci_wave_data_handler.init_tick_key_list_for_retrospection(ticks, period, aggregation)
        plotter = MyDashTabStatisticsPlotter4Waves(
            wave_handler=self._fibonacci_wave_data_handler,
            color_handler=self._dash_color_handler,
            index=self._dd_handler.selected_index)
        mood_chart = plotter.get_chart_list_by_chart_type(CHT.MOOD_CHART)
        return mood_chart

    def init_callbacks(self):
        # self.__init_callback_for_waves_header_table__()
        self.__init_callback_for_waves_heatmap__()
        self.__init_callback_for_waves_mood_chart__()
        self.__init_callback_for_waves_index_chart__()

    def __init_callback_for_waves_heatmap__(self):
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
            enforce_reload = self._process_for_head_map.was_triggered_by_another_process()
            data_updated = self._fibonacci_wave_data_handler.reload_data_when_outdated(enforce_reload)
            if not data_updated and not self._dd_handler.was_any_value_changed(
                    period, aggregation, ticks, index):
                self._heat_map_was_updated = False
                return children
            self._heat_map_was_updated = True
            self._fibonacci_wave_data_handler.init_tick_key_list_for_retrospection(ticks, period, aggregation)
            print('Return updated heatmap...')
            return self.__get_heatmap__()

    def __init_callback_for_waves_mood_chart__(self):
        @self.app.callback(
            Output(self._my_waves_mood_chart_div, 'children'),
            [Input(self._my_waves_heatmap_div, 'children')],
            [State(self._my_waves_mood_chart_div, 'children')])
        def handle_callback_for_waves_mood_chart(heat_map, children):
            if self._heat_map_was_updated:
                return self.__get_mood_chart__()
            return children

    def __init_callback_for_waves_index_chart__(self):
        @self.app.callback(
            Output(self._my_waves_index_chart_div, 'children'),
            [Input(self._my_waves_heatmap_div, 'children')],
            [State(self._my_waves_index_chart_div, 'children')])
        def handle_callback_for_waves_index_chart(heatmap, children):
            if not self._heat_map_was_updated:
                return children
            print('Return updated index chart...')
            return self.__get_graph_for_index__()

    def __get_graph_for_index__(self):
        index = self._dd_handler.selected_index
        if index in ['', INDICES.ALL]:
            return ''
        ticks = self._dd_handler.selected_retrospective_ticks
        period = self._dd_handler.selected_period
        aggregation = self._dd_handler.selected_aggregation
        ticker = INDICES.get_ticker_for_index(index)
        cache_key = self.__get_id_for_caches__()
        graph = self._index_chart_cache.get_cached_object_by_key(cache_key)
        if graph is None:
            graph, graph_key = self.__get_graph__(ticker, period=period, aggregation=aggregation, limit=ticks)
            self.__add_element_to_cache__(self._index_chart_cache, cache_key, graph)
        return graph

    @staticmethod
    def __add_element_to_cache__(cache, cache_key, element):
        cache_api = MyCacheObjectApi()
        cache_api.object = element
        cache_api.key = cache_key
        cache_api.valid_until_ts = MyDate.get_offset_timestamp(hours=6)
        cache.add_cache_object(cache_api)

    def __get_graph__(self, ticker_id: str, period: str, aggregation: int, limit=400):
        graph_cache_id = self.sys_config.graph_cache.get_cache_id(ticker_id, period, aggregation, limit)
        graph = self.sys_config.graph_cache.get_cached_object_by_key(graph_cache_id)
        if graph is not None:
            return graph, graph_cache_id
        self.sys_config.data_provider.period = period
        self.sys_config.data_provider.aggregation = aggregation
        if period == PRD.INTRADAY:
            self.sys_config.data_provider.from_db = False
            and_clause = ''
        else:
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
            return self.sys_config.fibonacci_wave_data_handler.\
                get_waves_numbers_with_dates_for_wave_type_and_index_for_days(wave_type, index)
        return callback

    def __init_callback_for_waves_header_table__(self):
        column = 1
        for wave_type in WAVEST.get_waves_types_for_processing([]):
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

    def init_parameters_for_testing(self, period: str, aggregation: int, ticks: int, index: str):
        self._dd_handler._selected_value_dict[WAVEDD.PERIOD] = period
        self._dd_handler._selected_value_dict[WAVEDD.AGGREGATION] = aggregation
        self._dd_handler._selected_value_dict[WAVEDD.RETROSPECTIVE_TICKS] = ticks
        self._dd_handler._selected_value_dict[WAVEDD.INDICES] = index


class MyDashTab4WavesTest(TestInterface):
    GET_HEATMAP = '__get_heatmap__'

    def __init__(self, print_all_test_cases_for_units=False):
        TestInterface.__init__(self, print_all_test_cases_for_units)
        self._sys_config = SystemConfiguration()
        self._sys_config.fibonacci_wave_data_handler.load_data(PRD.ALL)
        self._color_handler = DashColorHandler()
        pio.orca.config.executable = 'D:\Programs\Miniconda3\orca_app'
        pio.orca.config.save()
        print('plotly.io.orca.config.executable={}'.format(pio.orca.config.executable))
        self._dash_tab_for_waves = MyDashTab4Waves(
            app=None, sys_config=self._sys_config, color_handler=self._color_handler)

    def test_get_heatmap(self):
        test_case_parameter_lists = [
            [PRD.DAILY, 1, 100, INDICES.ALL],
            # [PRD.DAILY, 1, 200, INDICES.CRYPTO_CCY],
            # [PRD.INTRADAY, 30, 100, INDICES.ALL],
            # [PRD.INTRADAY, 30, 100, INDICES.DOW_JONES],
        ]
        test_case_dict = {}
        for params in test_case_parameter_lists:
            key = '{}-{}-{}-{}'.format(params[0], params[1], params[2], params[3])
            self._dash_tab_for_waves.init_parameters_for_testing(params[0], params[1], params[2], params[3])
            heat_map_graph_list = self._dash_tab_for_waves.__get_heatmap__()
            my_graph = MyDCCGraph(heat_map_graph_list[0])
            my_graph.save_figure()
            test_case_dict[key] = [heat_map_graph_list, '']
        return self.__verify_test_cases__(self.GET_HEATMAP, test_case_dict)

    def __get_class_name_tested__(self):
        return MyDashTab4Waves.__name__

    def __run_test_for_unit__(self, unit: str) -> bool:
        if unit == self.GET_HEATMAP:
            return self.test_get_heatmap()

    def __get_test_unit_list__(self):
        return [self.GET_HEATMAP]