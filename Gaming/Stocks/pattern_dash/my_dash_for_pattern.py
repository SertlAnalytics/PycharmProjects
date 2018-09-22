"""
Description: This module is the main module for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import numpy as np
import colorlover as cl
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event
from datetime import datetime, timedelta
import pandas as pd
import json
from playsound import playsound
from pattern_dash.pattern_shapes import MyPolygonShape, MyPolygonLineShape, MyLineShape
from sertl_analytics.myconstants import MyAPPS
from pattern_dash.my_dash_base import MyDashBase
from pattern_detection_controller import PatternDetectionController
from pattern_detector import PatternDetector
from sertl_analytics.constants.pattern_constants import CN, FD, BT, ST, TSTR, TBT
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod
from sertl_analytics.mydates import MyDate
from sertl_analytics.mycache import MyCache, MyCacheObject, MyCacheObjectApi
from pattern import Pattern
from pattern_part import PatternPart
from pattern_range import PatternRange
from pattern_wave_tick import WaveTickList
from pattern_colors import PatternColorHandler
from pattern_dash.my_dash_components import MyDCC, MyHTML, DccGraphApi, DccGraphSecondApi, MyHTMLHeaderTable
from fibonacci.fibonacci_wave import FibonacciWave
from pattern_bitfinex import BitfinexConfiguration
from pattern_trade_handler import PatternTradeHandler
from copy import deepcopy
from textwrap import dedent


class MyGraphCacheObjectApi(MyCacheObjectApi):
    def __init__(self, sys_config: SystemConfiguration):
        MyCacheObjectApi.__init__(self)
        self.sys_config = sys_config
        self.detector = None
        self.pattern_data = None
        self.last_refresh_ts = None
        self.period_aggregation_ts = self.sys_config.config.api_period_aggregation * 60


class MyGraphCacheObject(MyCacheObject):
    def __init__(self, cache_api: MyGraphCacheObjectApi):
        MyCacheObject.__init__(self, cache_api)
        self.sys_config = cache_api.sys_config
        self.detector = cache_api.detector
        self.pattern_data = cache_api.pattern_data
        self.last_refresh_ts = cache_api.last_refresh_ts
        self.period_aggregation_ts = self.sys_config.config.api_period_aggregation * 60
        self.adjusted_last_refresh_ts = \
            self.sys_config.config.get_time_stamp_before_one_period_aggregation(self.last_refresh_ts)
        self.cached_before_breakout = self.__was_cached_before_breakout__()
        self.breakout_since_last_data_update = self.__was_breakout_since_last_data_update__()
        self.fibonacci_finished_since_last_data_update = self.__was_fibonacci_finished_since_last_data_update__()
        self.touch_since_last_data_update = self.__was_any_touch_since_last_data_update__()

    def is_under_observation(self):
        return self.cached_before_breakout or self.breakout_since_last_data_update or \
               self.fibonacci_finished_since_last_data_update

    def __was_any_touch_since_last_data_update__(self):
        return self.detector.was_any_touch_since_time_stamp(self.adjusted_last_refresh_ts, True)

    def __was_breakout_since_last_data_update__(self):
        return self.detector.was_any_breakout_since_time_stamp(self.adjusted_last_refresh_ts, self.id, True)

    def __was_fibonacci_finished_since_last_data_update__(self):
        return self.detector.fib_wave_tree.was_any_wave_finished_since_time_stamp(self.adjusted_last_refresh_ts)

    def __was_cached_before_breakout__(self) -> bool:
        return self.detector.is_any_pattern_without_breakout()


class MyGraphCache(MyCache):
    def __init__(self):
        MyCache.__init__(self)
        self.__cached_and_under_observation_play_sound_list = []

    @property
    def number_of_finished_fibonacci_waves_since_last_refresh(self) -> int:
        number_return = 0
        for cache_object in self._cached_object_dict.values():
            if cache_object.fibonacci_finished_since_last_data_update:
                number_return += 1
        return number_return

    @staticmethod
    def get_cache_key(graph_id: str, ticker: str, days: int = 0):
        return '{}_{}_{}'.format(graph_id, ticker, days)

    def add_cache_object(self, cache_api: MyGraphCacheObjectApi):
        self._cached_object_dict[cache_api.key] = MyGraphCacheObject(cache_api)
        self._cached_object_dict[cache_api.key].print()

    def get_detector(self, cache_key: str):
        return self._cached_object_dict[cache_key].detector

    def get_pattern_data(self, cache_key):
        return self._cached_object_dict[cache_key].pattern_data

    def was_breakout_since_last_data_update(self, cache_key: str):
        return self._cached_object_dict[cache_key].breakout_since_last_data_update

    def was_touch_since_last_data_update(self, cache_key: str):
        return self._cached_object_dict[cache_key].touch_since_last_data_update

    def get_graph_list_for_observation(self, key_not: str) -> list:
        play_sound = False
        graphs = []
        for key, cache_object in self._cached_object_dict.items():
            if key != key_not and cache_object.is_under_observation():
                if key not in self.__cached_and_under_observation_play_sound_list:
                    self.__cached_and_under_observation_play_sound_list.append(key)
                    play_sound = True
                graphs.append(self.__change_to_observation_graph__(cache_object.object, len(graphs)))
            elif not cache_object.is_under_observation():
                if key in self.__cached_and_under_observation_play_sound_list:
                    self.__cached_and_under_observation_play_sound_list.remove(key)
        if play_sound:
            playsound('ring08.wav')  # C:/Windows/media/...
        return graphs

    def get_pattern_list_for_buy_trigger(self, buy_trigger: str) -> list:
        pattern_list = []
        for key, cache_object in self._cached_object_dict.items():
            if cache_object.is_under_observation():
                pattern_list += cache_object.detector.get_pattern_list_for_buy_trigger(buy_trigger)
        return pattern_list

    @staticmethod
    def __change_to_observation_graph__(graph_old, number: int):
        graph = deepcopy(graph_old)
        graph.id = 'my_new_key_{}'.format(number)
        graph.figure['layout']['height'] = graph.figure['layout']['height']/2
        return graph


class MyDashStateHandler:
    def __init__(self, ticker_list: list):
        self._my_refresh_button_clicks = 0
        self._my_interval_n_intervals = 0
        self._my_interval_selection = 0
        self._ticker_dict = {dict_element['value']: 0 for dict_element in ticker_list}

    def change_for_my_interval_selection(self, interval_selection: int) -> bool:
        if interval_selection != self._my_interval_selection:
            self._my_interval_selection = interval_selection
            return True
        return False

    def change_for_my_refresh_button(self, n_clicks: int) -> bool:
        if n_clicks > self._my_refresh_button_clicks:
            self._my_refresh_button_clicks = n_clicks
            return True
        return False

    def change_for_my_interval(self, n_intervals: int) -> bool:
        if n_intervals > self._my_interval_n_intervals:
            self._my_interval_n_intervals = n_intervals
            return True
        return False

    def add_selected_ticker(self, ticker: str):
        if ticker in self._ticker_dict:
            self._ticker_dict[ticker] += 1

    def get_next_most_selected_ticker(self, ticker_selected: str):
        max_count = 0
        max_ticker = ''
        for key, number in self._ticker_dict.items():
            if key != ticker_selected and number > max_count:
                max_ticker = key
                max_count = number
        return max_ticker


class MyDash4Pattern(MyDashBase):
    def __init__(self, sys_config: SystemConfiguration, bitfinex_config: BitfinexConfiguration):
        MyDashBase.__init__(self, MyAPPS.PATTERN_DETECTOR_DASH())
        self.sys_config = sys_config
        self.bitfinex_config = bitfinex_config
        self.trade_handler = PatternTradeHandler(sys_config, bitfinex_config)
        self.sys_config_second = sys_config.get_semi_deep_copy()
        self._color_handler = PatternColorHandler()
        self._pattern_controller = PatternDetectionController(self.sys_config)
        self.detector = None
        self._ticker_options = []
        self._interval_options = []
        self._graph_second_days_options = []
        self._current_symbol = ''
        self.__fill_ticker_options__()
        self.__fill_interval_options__()
        self.__fill_graph_second_days_options__()
        self._time_stamp_last_refresh = MyDate.time_stamp_now()
        self._time_stamp_next_refresh = None
        self._graph_first_cache = MyGraphCache()
        self._graph_second_cache = MyGraphCache()
        self._state_handler = MyDashStateHandler(self._ticker_options)
        self._graph_key_first = ''
        self._detector_first = None
        self._pattern_data_first = None

    def get_pattern(self):
        self.__set_app_layout__()
        self.__init_interval_callback_for_user_name__()
        self.__init_interval_callback_for_interval_details__()
        self.__init_interval_callback_for_timer__()
        self.__init_interval_setting_callback__()
        self.__init_callback_for_ticket_markdown__()
        self.__init_callback_for_graph_first__()
        self.__init_callback_for_graph_second__()
        self.__init_callback_for_graphs_before_breakout__()
        self.__init_hover_over_callback__()
        self.__init_selection_callback__()
        self.__init_ticker_selection_callback__()

    def __get_ticker_label__(self, ticker_value: str):
        for elements in self._ticker_options:
            if elements['value'] == ticker_value:
                return elements['label']
        return ticker_value

    def __init_callback_for_ticket_markdown__(self):
        @self.app.callback(
            Output('my_ticket_markdown', 'children'),
            [Input('my_graph_first_div', 'children')])
        def handle_callback_for_ticket_markdown(children):
            annotation = ''
            tick = self._pattern_data_first.tick_last
            for pattern in self._detector_first.pattern_list:
                if not pattern.was_breakout_done():
                    annotation = pattern.get_annotation_parameter().text

            if annotation == '':
                text = '**Last tick:** open:{} - **close = {}**'.format(tick.open, tick.close)
            else:
                text = dedent('''
                        **Last tick:** open:{} - **close = {}**

                        **Annotations (next breakout)**: {}
                        ''').format(tick.open, tick.close, annotation)
            return text

    def __init_selection_callback__(self):
        @self.app.callback(
            Output('my_submit_button', 'hidden'),
            [Input('my_ticker_selection', 'value'),
             Input('my_interval_selection', 'value'),
             Input('my_interval', 'n_intervals'),
             Input('my_submit_button', 'n_clicks')],
            [State('my_interval_timer', 'n_intervals')])
        def handle_selection_callback(ticker_selected, interval_selected: int, n_intervals, n_clicks, n_intervals_sec):
            if self._state_handler.change_for_my_interval_selection(interval_selected):
                self._graph_first_cache.clear()
            if self._state_handler.change_for_my_interval(n_intervals):  # hide button after interval refresh
                return 'hidden'
            if self._state_handler.change_for_my_refresh_button(n_clicks):  # hide button after refresh button click
                return 'hidden'
            return 'hidden' if n_intervals_sec == 0 else ''

        @self.app.callback(
            Output('my_ticker_div', 'children'),
            [Input('my_ticker_selection', 'value')])
        def handle_ticker_selection_callback_for_ticker_label(ticker_selected):
            return self.__get_ticker_label__(ticker_selected)

    def __fill_ticker_options__(self):
        for symbol, name in self.sys_config.config.ticker_dic.items():
            if self._current_symbol == '':
                self._current_symbol = symbol
            self._ticker_options.append({'label': '{}'.format(name), 'value': symbol})

    def __fill_interval_options__(self):
        self._interval_options.append({'label': '15 min', 'value': 900}) # this one is the default
        self._interval_options.append({'label': '5 min', 'value': 300})
        self._interval_options.append({'label': '2 min', 'value': 120})
        self._interval_options.append({'label': '1 min', 'value': 60})
        self._interval_options.append({'label': '30 sec.', 'value': 30})
        self._interval_options.append({'label': '15 sec.', 'value': 15})
        self._interval_options.append({'label': '10 sec.', 'value': 10})

    def __fill_graph_second_days_options__(self):
        self._graph_second_days_options.append({'label': 'NONE', 'value': 0})
        self._graph_second_days_options.append({'label': '400 days', 'value': 400})
        self._graph_second_days_options.append({'label': '200 days', 'value': 200})
        self._graph_second_days_options.append({'label': '100 days', 'value': 100})
        self._graph_second_days_options.append({'label': '60 days', 'value': 60})
        self._graph_second_days_options.append({'label': 'Intraday', 'value': 1})

    def __init_hover_over_callback__(self):
        @self.app.callback(
            Output('my_hover_data', 'children'),
            [Input('my_graph_first', 'hoverData'), Input('my_graph_second', 'hoverData')])
        def handle_hover_over_callback(hover_data_graph_1, hover_data_graph_2):
            return json.dumps(hover_data_graph_1, indent=2) + '\n' + json.dumps(hover_data_graph_2, indent=2)

    @staticmethod
    def __create_callback__():
        def callback_hover_data(hoverData):
            return json.dumps(hoverData, indent=2)
        return callback_hover_data

    def __init_interval_setting_callback__(self):
        @self.app.callback(
            Output('my_interval', 'interval'),
            [Input('my_interval_selection', 'value')])
        def handle_interval_setting_callback(interval_selected):
            print('Interval set to: {}'.format(interval_selected))
            return interval_selected * 1000

    def __init_ticker_selection_callback__(self):
        @self.app.callback(
            Output('my_graph_second_days_selection', 'value'),
            [Input('my_ticker_selection', 'value')],
            [State('my_graph_second_days_selection', 'value')])
        def handle_ticker_selection_callback_for_days_selection(ticker_selected, second_days_selection):
            return second_days_selection if second_days_selection == 1 else 0  # we want to keep Intraday

    def __init_interval_callback_with_date_picker__(self):
        @self.app.callback(
            Output('my_graph_main_div', 'children'),
            [Input('my_interval', 'n_intervals'),
             Input('my_submit_button', 'n_clicks')],
            [State('my_ticker_selection', 'value'),
             State('my_date_picker', 'start_date'),
             State('my_date_picker', 'end_date')])
        def handle_interval_callback_with_date_picker(n_intervals, n_clicks, ticker, dt_start, dt_end):
            self.__play_sound__(n_intervals)
            return self.__get_graph_first__(ticker, self.__get_and_clause__(dt_start, dt_end))

    @staticmethod
    def __get_and_clause__(dt_start, dt_end):
        date_start = MyDate.get_date_from_datetime(dt_start)
        date_end = MyDate.get_date_from_datetime(dt_end)
        return "Date BETWEEN '{}' AND '{}'".format(date_start, date_end)

    def __init_callback_for_graph_first__(self):
        @self.app.callback(
            Output('my_graph_first_div', 'children'),
            [Input('my_interval', 'n_intervals'),
             Input('my_submit_button', 'n_clicks')],
            [State('my_ticker_selection', 'value')])
        def handle_callback_for_graph_first(n_intervals, n_clicks, ticker):
            graph, graph_key = self.__get_graph_first__(ticker)
            self._graph_key_first = graph_key
            self.__cache_others_ticker_values__(n_intervals, ticker)
            if self._graph_first_cache.was_breakout_since_last_data_update(graph_key):
                print('Breakout since last data update !!!!')
                playsound('alarm01.wav')
            elif self._graph_first_cache.was_touch_since_last_data_update(graph_key):
                print('Touch since last data update !!!!')
                playsound('alarm01.wav')
            return graph

    def __init_callback_for_graph_second__(self):
        @self.app.callback(
            Output('my_graph_second_div', 'children'),
            [Input('my_graph_second_days_selection', 'value'),
             Input('my_graph_first_div', 'children')],
            [State('my_ticker_selection', 'value')])
        def handle_callback_for_graph_second(days_selected, graph_first_div, ticker_selected):
            if days_selected == 0 or ticker_selected is None:
                return ''
            return self.__get_graph_second__(ticker_selected, days_selected)[0]

    def __init_callback_for_graphs_before_breakout__(self):
        @self.app.callback(
            Output('my_graphs_before_breakout_div', 'children'),
            [Input('my_graph_first_div', 'children')])
        def handle_callback_for_graphs_before_breakout(graph_first_div):
            graphs = self._graph_first_cache.get_graph_list_for_observation(self._graph_key_first)
            pattern_list = self._graph_first_cache.get_pattern_list_for_buy_trigger(BT.BREAKOUT)
            self.trade_handler.add_pattern_list_for_trade(pattern_list)
            if len(graphs) > 0:
                print('\n...handle_callback_for_graphs_before_breakout: {}'.format(len(graphs)))
            if self._graph_first_cache.number_of_finished_fibonacci_waves_since_last_refresh > 2:
                print('\n...finished_fibonacci_waves_since_last_refresh > 2')
                playsound('Ring08.wav')
            return graphs

    def __init_interval_callback_for_user_name__(self):
        @self.app.callback(
            Output('my_user_name_div', 'children'),
            [Input('my_interval', 'n_intervals')])
        def handle_interval_callback_for_last_refresh(n_intervals):
            if self._user_name == '':
                self._user_name = self._get_user_name_()
            return self._user_name

    def __init_interval_callback_for_interval_details__(self):
        @self.app.callback(
            Output('my_last_refresh_time_div', 'children'),
            [Input('my_interval', 'n_intervals')])
        def handle_interval_callback_for_last_refresh(n_intervals):
            self._time_stamp_last_refresh = MyDate.time_stamp_now()
            last_refresh_dt = MyDate.get_time_from_datetime(datetime.now())
            return '{} ({})'.format(last_refresh_dt, n_intervals)

        @self.app.callback(
            Output('my_next_refresh_time_div', 'children'),
            [Input('my_interval', 'n_intervals'), Input('my_interval', 'interval')])
        def handle_interval_callback_for_next_refresh(n_intervals, interval_ms):
            dt_next = datetime.now() + timedelta(milliseconds=interval_ms)
            self._time_stamp_next_refresh = int(dt_next.timestamp())
            return '{}'.format(MyDate.get_time_from_datetime(dt_next))

    def __init_interval_callback_for_timer__(self):
        @self.app.callback(
            Output('my_time_div', 'children'),
            [Input('my_interval_timer', 'n_intervals')])
        def handle_interval_callback_for_timer(n_intervals):
            if n_intervals % self.bitfinex_config.check_ticker_after_timer_intervals == 0:
                self.trade_handler.check_actual_trades()
            return '{}'.format(MyDate.get_time_from_datetime(datetime.now()))

    @staticmethod
    def __play_sound__(n_intervals):
        if n_intervals % 10 == 0:
            playsound('ring08.wav')  # C:/Windows/media/...

    def __cache_others_ticker_values__(self, n_intervals: int, ticker_selected: str):
        if n_intervals > 0:
            for element_dict in self._ticker_options:
                ticker = element_dict['value']
                if ticker != ticker_selected:
                    self.__get_graph_first__(ticker, '', True)

    def __get_graph_first__(self, ticker: str, and_clause='', for_caching=False):
        graph_id = 'my_graph_first'
        graph_title = '{} {}'.format(ticker, self.sys_config.config.api_period)
        graph_key = MyGraphCache.get_cache_key(graph_id, ticker, 0)
        cached_graph = self._graph_first_cache.get_cached_object_by_key(graph_key)
        if cached_graph is not None:
            if not for_caching:
                self._detector_first = self._graph_first_cache.get_detector(graph_key)
                self._pattern_data_first = self._graph_first_cache.get_pattern_data(graph_key)
            # print('...return cached graph_first: {}'.format(graph_key))
            return cached_graph, graph_key

        detector = self._pattern_controller.get_detector_for_dash(self.sys_config, ticker, and_clause)
        pattern_data = self.sys_config.pdh.pattern_data
        if not for_caching:
            self._detector_first = detector
            self._pattern_data_first = self.sys_config.pdh.pattern_data
        graph_api = DccGraphApi(graph_id, graph_title)
        graph = self.__get_dcc_graph_element__(detector, graph_api, ticker)
        cache_api = self.__get_cache_api__(graph_key, graph, detector, pattern_data)
        self._graph_first_cache.add_cache_object(cache_api)
        return graph, graph_key

    def __get_graph_second__(self, ticker: str, days: int):
        graph_id = 'my_graph_second'
        graph_title = '{} {} days'.format(ticker, days if days > 1 else 'Intraday')
        graph_key = MyGraphCache.get_cache_key(graph_id, ticker, days)
        cached_graph = self._graph_second_cache.get_cached_object_by_key(graph_key)
        if cached_graph is not None:
            # print('...return cached graph_second: {}'.format(graph_key))
            return cached_graph, graph_key
        if days == 1:
            self.sys_config_second.config.api_period_aggregation = 15
            self.sys_config_second.config.api_period = ApiPeriod.INTRADAY
            self.sys_config_second.config.get_data_from_db = False
            detector = self._pattern_controller.get_detector_for_dash(self.sys_config_second, ticker, '')
            graph_api = DccGraphSecondApi(graph_id, graph_title)
            graph = self.__get_dcc_graph_element__(detector, graph_api, ticker)
            cache_api = self.__get_cache_api__(graph_key, graph, detector, None)
            self._graph_second_cache.add_cache_object(cache_api)
        else:
            self.sys_config_second.config.api_period = ApiPeriod.DAILY
            self.sys_config_second.config.get_data_from_db = True
            date_from = datetime.today() - timedelta(days=days)
            date_to = datetime.today() + timedelta(days=5)
            and_clause = self.__get_and_clause__(date_from, date_to)
            detector = self._pattern_controller.get_detector_for_dash(self.sys_config_second, ticker, and_clause)
            graph_api = DccGraphSecondApi(graph_id, graph_title)
            graph = self.__get_dcc_graph_element__(detector, graph_api, ticker)
            cache_api = self.__get_cache_api__(graph_key, graph, detector, None)
            self._graph_second_cache.add_cache_object(cache_api)
        return graph, graph_key

    def __get_cache_api__(self, graph_key, graph, detector, pattern_data):
        cache_api = MyGraphCacheObjectApi(self.sys_config)
        cache_api.key = graph_key
        cache_api.object = graph
        cache_api.detector = detector
        cache_api.pattern_data = pattern_data
        cache_api.valid_until_ts = self._time_stamp_next_refresh
        cache_api.last_refresh_ts = self._time_stamp_last_refresh
        return cache_api

    def __get_dcc_graph_element__(self, detector, graph_api, ticker: str):
        pattern_df = detector.sys_config.pdh.pattern_data.df
        candlestick = self.__get_candlesticks_trace__(pattern_df, ticker)
        bollinger_traces = self.__get_bollinger_band_trace__(pattern_df, ticker)
        shapes = self.__get_pattern_shape_list__(detector)
        shapes += self.__get_pattern_regression_shape_list__(detector)
        shapes += self.__get_fibonacci_shape_list__(detector)
        graph_api.figure_layout_shapes = [my_shapes.shape_parameters for my_shapes in shapes]
        graph_api.figure_layout_annotations = [my_shapes.annotation_parameters for my_shapes in shapes]
        graph_api.figure_data = [candlestick]
        return MyDCC.graph(graph_api)

    def __get_pattern_shape_list__(self, detector: PatternDetector):
        return_list = []
        for pattern in detector.pattern_list:
            colors = self._color_handler.get_colors_for_pattern(pattern)
            return_list.append(DashInterface.get_pattern_part_main_shape(pattern, colors[0]))
            if pattern.was_breakout_done() and pattern.is_part_trade_available():
                return_list.append(DashInterface.get_pattern_part_trade_shape(pattern, colors[1]))
        return return_list

    @staticmethod
    def __get_pattern_regression_shape_list__(detector: PatternDetector):
        return_list = []
        for pattern in detector.pattern_list:
            return_list.append(DashInterface.get_f_regression_shape(pattern.part_main, 'skyblue'))
        return return_list

    @staticmethod
    def __get_fibonacci_shape_list__(detector: PatternDetector):
        return_list = []
        for fib_waves in detector.fib_wave_tree.fibonacci_wave_list:
            color = 'green' if fib_waves.wave_type == FD.ASC else 'red'
            return_list.append(DashInterface.get_fibonacci_wave_shape(detector.sys_config, fib_waves, color))
            # print('Fibonacci: {}'.format(return_list[-1].shape_parameters))
        return return_list

    def __get_candlesticks_trace__(self, df: pd.DataFrame, ticker: str):
        if self.sys_config.config.api_period == ApiPeriod.INTRADAY:
            x_value = df[CN.DATETIME]
        else:
            x_value = df[CN.DATE]
        candlestick = {
            'x': x_value,
            'open': df[CN.OPEN],
            'high': df[CN.HIGH],
            'low': df[CN.LOW],
            'close': df[CN.CLOSE],
            'type': 'candlestick',
            'name': ticker,
            'legendgroup': ticker,
            'hoverover': 'skip',
            'increasing': {'line': {'color': 'g'}},
            'decreasing': {'line': {'color': 'r'}}
        }
        return candlestick

    def __get_bollinger_band_trace__(self, df: pd.DataFrame, ticker: str):
        color_scale = cl.scales['9']['qual']['Paired']
        bb_bands = self.__get_bollinger_band_values__(df[CN.CLOSE])

        bollinger_traces = [{
            'x': df[CN.TIME] if self.sys_config.config.api_period == ApiPeriod.INTRADAY else df[CN.DATE],
            'y': y,
            'type': 'scatter', 'mode': 'lines',
            'line': {'width': 1, 'color': color_scale[(i * 2) % len(color_scale)]},
            'hoverinfo': 'none',
            'legendgroup': ticker + ' - Bollinger',
            'showlegend': True if i == 0 else False,
            'name': '{} - bollinger bands'.format(ticker)
        } for i, y in enumerate(bb_bands)]

        return bollinger_traces

    def __set_app_layout__(self):
        self.app.layout = self.__get_div_for_tab_pattern_detection__()
        # self.app.layout = self.__get_div_for_app_layout__()

    def __get_div_for_app_layout__(self):
        # see also https://github.com/plotly/dash-core-components/pull/213
        header = self.__get_header_for_app_layout__()
        tabs = self.__get_tabs_for_app_layout__()
        return MyHTML.div('my_app', [header, tabs])

    @staticmethod
    def __get_header_for_app_layout__():
        style = {'textAlign': 'center', 'margin': '20px 0', 'fontFamily': 'system-ui'}
        return MyHTML.h1('Pattern Detection by Sertl Analytics', style)

    def __get_tabs_for_app_layout__(self):
        tab_01 = MyDCC.tab('Pattern Detector', [self.__get_div_for_tab_pattern_detection__()])
        tab_02 = MyDCC.tab('Trades', [self.__get_div_for_trades__()])
        tab_03 = MyDCC.tab('Statistics', [self.__get_div_for_statistics__()])
        return MyDCC.tabs('my_app_tabs', [tab_01, tab_02, tab_03])

    def __get_div_for_tab_pattern_detection__(self):
        # print('MyHTMLHeaderTable.get_table={}'.format(MyHTMLHeaderTable().get_table()))
        li = [MyHTMLHeaderTable().get_table()]
        li.append(MyDCC.interval('my_interval', 100))
        li.append(MyDCC.interval('my_interval_timer', self.bitfinex_config.ticker_refresh_rate_in_seconds))
        li.append(MyHTML.div_with_dcc_drop_down(
            'Stock symbol', 'my_ticker_selection', self._ticker_options, 200))
        li.append(MyHTML.div_with_dcc_drop_down(
            'Refresh interval', 'my_interval_selection', self._interval_options, 200))
        li.append(MyHTML.div_with_dcc_drop_down(
            'Second graph', 'my_graph_second_days_selection', self._graph_second_days_options, 200))
        if self.sys_config.config.get_data_from_db:
            li.append(self.__get_html_div_with_date_picker_range__())
        li.append(MyHTML.div_with_html_button_submit('my_submit_button', 'Refresh'))
        li.append(MyHTML.div('my_graph_first_div'))
        li.append(MyHTML.div('my_graph_second_div'))
        li.append(MyHTML.div('my_graphs_before_breakout_div'))
        # li.append(MyHTML.div_embedded('my_graphs_before_breakout_div'))
        li.append(MyHTML.div_with_html_pre('my_hover_data'))
        return MyHTML.div('', li)

    def __get_div_for_trades__(self):
        header = MyHTML.h1('This is the content in tab 2: Trade data - from back testing and online trades')
        paragraph = MyHTML.p('A graph here would be nice!')
        drop_down = self.__get_drop_down_for_trades__()
        table = self.__get_table_for_trades__()
        return MyHTML.div('my_trades', [header, paragraph, drop_down, table])

    def __get_drop_down_for_trades__(self):
        df = self.sys_config.db_stock.get_trade_records_as_dataframe()
        options = [{'label': 'df', 'value': 'df'}]
        return MyDCC.drop_down('trades-selection', options)

    def __get_table_for_trades__(self):
        df = self.sys_config.db_stock.get_trade_records_as_dataframe()
        df_dict = df.to_dict()
        # {'ID': {0: 'Breakout-Expected_win-Trailing_stop_Crypto_Currencies_DAILY_1_ETH_USD_Triangle down_2...
        rows = []
        columns = [column for column in df_dict]
        row_numbers = [number for number in df_dict[columns[0]]]
        for row_number in row_numbers:
            rows.append({column: df_dict[column][row_number] for column in columns})
        return MyDCC.data_table('trade_table', rows)

    def __get_div_for_statistics__(self):
        header = MyHTML.h1('This is the content in tab 3: Statistics data - from features and trades')
        paragraph = MyHTML.p('A graph here would be nice!')
        drop_down = self.__get_drop_down_for_features__()
        table = self.__get_table_for_features__()
        return MyHTML.div('my_statistics', [header, paragraph, drop_down, table])

    def __get_drop_down_for_features__(self):
        df = self.sys_config.db_stock.get_features_records_as_dataframe()
        options = [{'label': 'df', 'value': 'df'}]
        return MyDCC.drop_down('features-selection', options)

    def __get_table_for_features__(self):
        df = self.sys_config.db_stock.get_features_records_as_dataframe()
        df_dict = df.to_dict()
        # {'ID': {0: 'Breakout-Expected_win-Trailing_stop_Crypto_Currencies_DAILY_1_ETH_USD_Triangle down_2...
        rows = []
        columns = [column for column in df_dict]
        row_numbers = [number for number in df_dict[columns[0]]]
        for row_number in row_numbers:
            rows.append({column: df_dict[column][row_number] for column in columns})
        return MyDCC.data_table('features_table', rows)

    def __set_app_layout_old__(self):
        # print('MyHTMLHeaderTable.get_table={}'.format(MyHTMLHeaderTable().get_table()))
        li = [MyHTMLHeaderTable().get_table()]
        li.append(MyDCC.interval('my_interval', 100))
        li.append(MyDCC.interval('my_interval_timer', 1))
        li.append(MyHTML.div_with_dcc_drop_down(
            'Stock symbol', 'my_ticker_selection', self._ticker_options, 200))
        li.append(MyHTML.div_with_dcc_drop_down(
            'Refresh interval', 'my_interval_selection', self._interval_options, 200))
        li.append(MyHTML.div_with_dcc_drop_down(
            'Second graph', 'my_graph_second_days_selection', self._graph_second_days_options, 200))
        if self.sys_config.config.get_data_from_db:
            li.append(self.__get_html_div_with_date_picker_range__())
        li.append(MyHTML.div_with_html_button_submit('my_submit_button', 'Refresh'))
        li.append(MyHTML.div('my_graph_first_div'))
        li.append(MyHTML.div('my_graph_second_div'))
        li.append(MyHTML.div('my_graphs_before_breakout_div'))
        # li.append(MyHTML.div_embedded('my_graphs_before_breakout_div'))
        li.append(MyHTML.div_with_html_pre('my_hover_data'))
        self.app.layout = MyHTML.div('', li)

    @staticmethod
    def __get_html_div_with_date_picker_range__():
        return html.Div(
            [
                MyHTML.h3('Select start and end dates:'),
                MyDCC.get_date_picker_range('my_date_picker', datetime.today() - timedelta(days=160))
            ],
            style={'display': 'inline-block', 'vertical-align': 'bottom', 'height': 20}
        )


class DashInterface:
    @staticmethod
    def get_x_y_separated_for_shape(xy):
        xy_array = np.array(xy)
        x = xy_array[:, 0]
        y = xy_array[:, 1]
        # print('get_x_y_separated_for_shape:')
        # print(x)
        return x, y

    @staticmethod
    def get_tick_distance_in_date_as_number(sys_config: SystemConfiguration):
        if sys_config.config.api_period == ApiPeriod.INTRADAY:
            return MyDate.get_date_as_number_difference_from_epoch_seconds(0, sys_config.config.api_period_aggregation * 60)
        return 1

    @staticmethod
    def get_tolerance_range_for_extended_dict(sys_config: SystemConfiguration):
        return DashInterface.get_tick_distance_in_date_as_number(sys_config)/2

    @staticmethod
    def get_ellipse_width_height_for_plot_min_max(sys_config: SystemConfiguration, wave_tick_list: WaveTickList):
        if sys_config.config.api_period == ApiPeriod.DAILY:
            width_value = 0.6
        else:
            width_value = 0.6 / (sys_config.config.api_period_aggregation * 60)
        height_value = wave_tick_list.value_range / 100
        return width_value, height_value

    @staticmethod
    def get_xy_from_timestamp_to_date_str(xy):
        if type(xy) == list:
            return [(str(MyDate.get_date_from_epoch_seconds(t_val[0])), t_val[1]) for t_val in xy]
        return str(MyDate.get_date_from_epoch_seconds(xy[0])), xy[1]

    @staticmethod
    def get_xy_from_timestamp_to_time_str(xy):
        if type(xy) == list:
            return [(str(MyDate.get_time_from_epoch_seconds(t_val[0])), t_val[1]) for t_val in xy]
        return str(MyDate.get_time_from_epoch_seconds(xy[0])), xy[1]

    @staticmethod
    def get_xy_from_timestamp_to_date_time_str(xy):
        if type(xy) == list:
            return [(str(MyDate.get_date_time_from_epoch_seconds(t_val[0])), t_val[1]) for t_val in xy]
        return str(MyDate.get_date_time_from_epoch_seconds(xy[0])), xy[1]

    @staticmethod
    def get_annotation_param(pattern: Pattern):
        annotation_param = pattern.get_annotation_parameter('blue')
        annotation_param.xy = DashInterface.get_xy_from_timestamp_to_date(annotation_param.xy)
        annotation_param.xy_text = DashInterface.get_xy_from_timestamp_to_date(annotation_param.xy_text)
        return annotation_param

    @staticmethod
    def get_pattern_part_main_shape(pattern: Pattern, color: str):
        x, y = DashInterface.get_xy_separated_from_timestamp(pattern.sys_config, pattern.xy)
        # print('get_pattern_part_main_shape: {}'.format(x))
        # Todo: format for values in x have to be changed to dtype: datetime64[ns]
        return MyPolygonShape(x, y, color)

    @staticmethod
    def get_pattern_part_trade_shape(pattern: Pattern, color: str):
        x, y = DashInterface.get_xy_separated_from_timestamp(pattern.sys_config, pattern.xy_trade)
        return MyPolygonShape(x, y, color)

    @staticmethod
    def get_fibonacci_wave_shape(sys_config: SystemConfiguration, fib_wave: FibonacciWave, color: str):
        x, y = DashInterface.get_xy_separated_from_timestamp(sys_config, fib_wave.get_xy_parameter())
        return MyPolygonLineShape(x, y, color)

    @staticmethod
    def get_f_regression_shape(pattern_part: PatternPart, color: str):
        x, y = DashInterface.get_xy_separated_from_timestamp(pattern_part.sys_config, pattern_part.xy_regression)
        return MyLineShape(x, y, color)

    @staticmethod
    def get_xy_separated_from_timestamp(sys_config: SystemConfiguration, xy):
        if sys_config.config.api_period == ApiPeriod.INTRADAY:
            xy_new = DashInterface.get_xy_from_timestamp_to_date_time_str(xy)
        else:
            xy_new = DashInterface.get_xy_from_timestamp_to_date_str(xy)
        return DashInterface.get_x_y_separated_for_shape(xy_new)

    @staticmethod
    def get_pattern_center_shape(sys_config: SystemConfiguration, pattern: Pattern):
        if sys_config.config.api_period == ApiPeriod.DAILY:
            ellipse_breadth = 10
        else:
            ellipse_breadth = 2 / (sys_config.config.api_period_aggregation * 60)
        ellipse_height = pattern.part_main.height / 6
        xy_center = DashInterface.get_xy_from_timestamp_to_date(pattern.xy_center)
        return Ellipse(np.array(xy_center), ellipse_breadth, ellipse_height)

    @staticmethod
    def get_f_upper_shape(pattern_part: PatternPart):
        return pattern_part.stock_df.get_f_upper_shape(pattern_part.function_cont)

    @staticmethod
    def get_f_lower_shape(pattern_part: PatternPart):
        return pattern_part.stock_df.get_f_lower_shape(pattern_part.function_cont)

    @staticmethod
    def get_range_f_param_shape(pattern_range: PatternRange):
        xy_f_param = DashInterface.get_xy_from_timestamp_to_date_str(pattern_range.xy_f_param)
        return MyPolygonShape(np.array(xy_f_param), True)

    @staticmethod
    def get_range_f_param_shape_list(pattern_range: PatternRange):
        return_list = []
        for xy_f_param in pattern_range.xy_f_param_list:
            xy_f_param = DashInterface.get_xy_from_timestamp_to_date(xy_f_param)
            return_list.append(MyPolygonShape(np.array(xy_f_param), True))
        return return_list