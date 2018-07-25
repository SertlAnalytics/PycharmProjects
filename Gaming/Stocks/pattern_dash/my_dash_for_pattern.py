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
from pattern_data_container import pattern_data_handler as pdh
from datetime import datetime
import pandas as pd
import json
from playsound import playsound
from pattern_dash.pattern_shapes import MyPolygonShape, MyPolygonLineShape, MyLineShape
from sertl_analytics.myconstants import MyAPPS
from pattern_dash.my_dash_base import MyDashBase
from pattern_detection_controller import PatternDetectionController
from sertl_analytics.constants.pattern_constants import CN, FD
from pattern_configuration import config
from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod
from sertl_analytics.mydates import MyDate
from pattern import Pattern
from pattern_part import PatternPart
from pattern_range import PatternRange
from pattern_wave_tick import WaveTickList
from pattern_colors import PatternColorHandler
from pattern_dash.my_dash_components import MyDCC, MyHTML
from fibonacci.fibonacci_wave import FibonacciWave


class MyDash4Pattern(MyDashBase):
    def __init__(self):
        MyDashBase.__init__(self, MyAPPS.PATTERN_DETECTOR_DASH)
        self._color_handler = PatternColorHandler()
        self._pattern_controller = PatternDetectionController()
        self.detector = None
        self._ticker_options = []
        self._interval_options = []
        self._current_symbol = ''
        self.__fill_ticker_options__()
        self.__fill_interval_options__()

    def get_pattern(self):
        self.__set_app_layout__()
        self.__init_interval_setting_callback__()
        self.__init_interval_callback__()
        self.__init_interval_callback_for_text__()
        self.__init_hover_over_callback__()

    def __fill_ticker_options__(self):
        for symbol, name in config.ticker_dic.items():
            if self._current_symbol == '':
                self._current_symbol = symbol
            self._ticker_options.append({'label': '{} {}'.format(symbol, name), 'value': symbol})

    def __fill_interval_options__(self):
        self._interval_options.append({'label': 'Refresh Chart', 'value': 'run'})
        self._interval_options.append({'label': 'Keep Chart', 'value': 'stop'})

    def __init_hover_over_callback__(self):
        self.app.callback(
            Output('my_hover_data', 'children'),
            [Input(self._current_symbol, 'hoverData')])(self.__create_callback__())

    def __init_interval_setting_callback__(self):
        @self.app.callback(
            Output('my_interval', 'interval'),
            [Input('my_interval_option', 'value')])
        def update_interval_period(value):
            print('__init_interval_setting_callback__: {}'.format(value))
            return 10 * 1000 if value == 'run' else 100 * 1000

    def __init_interval_callback__(self):
        if config.get_data_from_db:
            self.__init_interval_callback_with_date_picker__()
        else:
            self.__init_interval_callback_without_date_picker__()

    def __init_interval_callback_with_date_picker__(self):
        @self.app.callback(
            Output('graphs', 'children'),
            [Input('my_interval', 'n_intervals')],
            [State('my_ticker_symbol', 'value'),
             State('my_date_picker', 'start_date'),
             State('my_date_picker', 'end_date')])
        def update_graph(n_intervals, ticker, start_date, end_date):
            start_date = datetime.strptime(start_date[:10], '%Y-%m-%d')
            date_end = datetime.strptime(end_date[:10], '%Y-%m-%d')
            and_clause = "Date BETWEEN '{}' AND '{}'".format(start_date, date_end)
            self.__play_sound__(n_intervals)
            return self.__append_graphs__(ticker, and_clause)

    def __init_interval_callback_without_date_picker__(self):
        @self.app.callback(
            Output('graphs', 'children'),
            [Input('my_interval', 'n_intervals')],
            [State('my_ticker_symbol', 'value')])
        def update_graph(n_intervals, ticker):
            return self.__append_graphs__(ticker)

    def __init_interval_callback_for_text__(self):
        @self.app.callback(
            Output('my_interval_data', 'children'),
            [Input('my_interval', 'n_intervals')])
        def write_interval_details(n_intervals):
            return 'Last refresh: {} ({})'.format(datetime.now(), n_intervals)

    @staticmethod
    def __play_sound__(n_intervals):
        if n_intervals % 5 == 0:
            playsound('alarm01.wav')  # C:/Windows/media/...

    @staticmethod
    def __create_callback__():
        def callback_hover_data(hoverData):
            return json.dumps(hoverData, indent=2)
        return callback_hover_data

    def __append_graphs__(self, ticker: str, and_clause='', interval_option='run'):
        graphs = []
        if interval_option == 'run':
            self.detector = self._pattern_controller.get_detector_for_dash(ticker, and_clause)
            self.df = pdh.pattern_data.df
        candlestick = self.__get_candlesticks_trace__(self.df, ticker)
        bollinger_traces = self.__get_boolinger_band_trace__(self.df, ticker)
        shape_list = self.__get_pattern_shape_list__()
        shape_list += self.__get_pattern_regression_shape_list__()
        shape_list += self.__get_fibonacci_shape_list__()
        shapes = [my_shapes.shape_parameters for my_shapes in shape_list]
        annotations = [my_shapes.annotation_parameters for my_shapes in shape_list]
        graph_data = [candlestick]
        graphs.append(MyDCC.get_graph(ticker, graph_data, shapes, annotations))
        return graphs

    def __get_pattern_shape_list__(self):
        return_list = []
        for pattern in self.detector.pattern_list:
            colors = self._color_handler.get_colors_for_pattern(pattern)
            return_list.append(DashInterface.get_pattern_part_main_shape(pattern, colors[0]))
            # print('Pattern: {}'.format(return_list[-1].shape_parameters))
            if pattern.was_breakout_done() and pattern.is_part_trade_available():
                return_list.append(DashInterface.get_pattern_part_trade_shape(pattern, colors[1]))
        return return_list

    def __get_pattern_regression_shape_list__(self):
        return_list = []
        for pattern in self.detector.pattern_list:
            return_list.append(DashInterface.get_f_regression_shape(pattern.part_main, 'skyblue'))
        return return_list

    def __get_fibonacci_shape_list__(self):
        return_list = []
        for fib_waves in self.detector.fib_wave_tree.fibonacci_wave_list:
            color = 'green' if fib_waves.wave_type == FD.ASC else 'red'
            return_list.append(DashInterface.get_fibonacci_wave_shape(fib_waves, color))
            # print('Fibonacci: {}'.format(return_list[-1].shape_parameters))
        return return_list

    @staticmethod
    def __get_candlesticks_trace__(df: pd.DataFrame, ticker: str):
        candlestick = {
            'x': df[CN.TIME] if config.api_period == ApiPeriod.INTRADAY else df[CN.DATE],
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

    def __get_boolinger_band_trace__(self, df: pd.DataFrame, ticker: str):
        color_scale = cl.scales['9']['qual']['Paired']
        bb_bands = self.__get_bollinger_band_values__(df[CN.CLOSE])

        bollinger_traces = [{
            'x': df[CN.TIME] if config.api_period == ApiPeriod.INTRADAY else df[CN.DATE],
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
        html_element_list = [html.H1('Pattern Detection Dashboard')]
        html_element_list.append(MyDCC.get_interval('my_interval', 10))
        html_element_list.append(self.__get_html_div_with_ticker_drop_down__())
        html_element_list.append(MyDCC.get_radio_items_inline('my_interval_option', self._interval_options))
        if config.get_data_from_db:
            html_element_list.append(self.__get_html_div_with_date_picker_range__())
        html_element_list.append(html.Div(id='graphs'))
        html_element_list.append(self.__get_html_div_for_hover_data__())
        html_element_list.append(self.__get_html_div_for_interval_data__())
        self.app.layout = html.Div(html_element_list)

    def __get_html_div_with_ticker_drop_down__(self):
        return html.Div(
            [
                html.H3('Select stock symbols:', style={'paddingRight': '30px'}),
                MyDCC.get_drop_down('my_ticker_symbol', self._ticker_options, False)
            ],
            style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '30%'}
        )

    @staticmethod
    def __get_html_div_with_date_picker_range__():
        return html.Div(
            [
                html.H3('Select start and end dates:'),
                MyDCC.get_date_picker_range('my_date_picker', datetime(2018, 1, 1))
            ],
            style={'display': 'inline-block'}
        )

    @staticmethod
    def __get_html_div_with_submit__():
        return html.Div(
            [MyHTML.get_submit_button()],
            style={'display': 'inline-block'})

    @staticmethod
    def __get_html_div_for_hover_data__():
        return html.Div(
            [MyHTML.get_pre('my_hover_data')],
            style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}
        )

    @staticmethod
    def __get_html_div_for_interval_data__():
        return html.Div(
            [MyHTML.get_pre('my_interval_data')],
            style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}
        )


class DashInterface:
    @staticmethod
    def get_x_y_separated_for_shape(xy):
        xy_array = np.array(xy)
        x = xy_array[:, 0]
        y = xy_array[:, 1]
        return x, y

    @staticmethod
    def get_tick_distance_in_date_as_number():
        if config.api_period == ApiPeriod.INTRADAY:
            return MyDate.get_date_as_number_difference_from_epoch_seconds(0, config.api_period_aggregation * 60)
        return 1

    @staticmethod
    def get_tolerance_range_for_extended_dict():
        return DashInterface.get_tick_distance_in_date_as_number()/2

    @staticmethod
    def get_ellipse_width_height_for_plot_min_max(wave_tick_list: WaveTickList):
        if config.api_period == ApiPeriod.DAILY:
            width_value = 0.6
        else:
            width_value = 0.6 / (config.api_period_aggregation * 60)
        height_value = wave_tick_list.value_range / 100
        return width_value, height_value

    @staticmethod
    def get_xy_from_timestamp_to_date_str(xy):
        if type(xy) == list:
            return [(str(MyDate.get_date_from_epoch_seconds(t_val[0])), t_val[1]) for t_val in xy]
        return str(MyDate.get_date_from_epoch_seconds(xy[0])), xy[1]

    @staticmethod
    def get_annotation_param(pattern: Pattern):
        annotation_param = pattern.get_annotation_parameter('blue')
        annotation_param.xy = DashInterface.get_xy_from_timestamp_to_date(annotation_param.xy)
        annotation_param.xy_text = DashInterface.get_xy_from_timestamp_to_date(annotation_param.xy_text)
        return annotation_param

    @staticmethod
    def get_pattern_part_main_shape(pattern: Pattern, color: str):
        xy = DashInterface.get_xy_from_timestamp_to_date_str(pattern.xy)
        x, y = DashInterface.get_x_y_separated_for_shape(xy)
        return MyPolygonShape(x, y, color)

    @staticmethod
    def get_pattern_part_trade_shape(pattern: Pattern, color: str):
        xy = DashInterface.get_xy_from_timestamp_to_date_str(pattern.xy_trade)
        x, y = DashInterface.get_x_y_separated_for_shape(xy)
        return MyPolygonShape(x, y, color)

    @staticmethod
    def get_fibonacci_wave_shape(fib_wave: FibonacciWave, color: str):
        xy = fib_wave.get_xy_parameter()
        xy = DashInterface.get_xy_from_timestamp_to_date_str(xy)
        x, y = DashInterface.get_x_y_separated_for_shape(xy)
        return MyPolygonLineShape(x, y, color)

    @staticmethod
    def get_pattern_center_shape(pattern: Pattern):
        if config.api_period == ApiPeriod.DAILY:
            ellipse_breadth = 10
        else:
            ellipse_breadth = 2 / (config.api_period_aggregation * 60)
        ellipse_height = pattern.part_main.height / 6
        xy_center = DashInterface.get_xy_from_timestamp_to_date(pattern.xy_center)
        return Ellipse(np.array(xy_center), ellipse_breadth, ellipse_height)

    @staticmethod
    def get_f_regression_shape(pattern_part: PatternPart, color: str):
        xy_regression = DashInterface.get_xy_from_timestamp_to_date_str(pattern_part.xy_regression)
        x, y = DashInterface.get_x_y_separated_for_shape(xy_regression)
        return MyLineShape(x, y, color)

    @staticmethod
    def get_f_upper_shape(pattern_part: PatternPart):
        return pattern_part.stock_df.get_f_upper_shape(pattern_part.function_cont)

    @staticmethod
    def get_f_lower_shape(pattern_part: PatternPart):
        return pattern_part.stock_df.get_f_lower_shape(pattern_part.function_cont)

    @staticmethod
    def get_range_f_param_shape(pattern_range: PatternRange):
        xy_f_param = DashInterface.get_xy_from_timestamp_to_date(pattern_range.xy_f_param)
        return MyPolygonShape(np.array(xy_f_param), True)

    @staticmethod
    def get_range_f_param_shape_list(pattern_range: PatternRange):
        return_list = []
        for xy_f_param in pattern_range.xy_f_param_list:
            xy_f_param = DashInterface.get_xy_from_timestamp_to_date(xy_f_param)
            return_list.append(MyPolygonShape(np.array(xy_f_param), True))
        return return_list