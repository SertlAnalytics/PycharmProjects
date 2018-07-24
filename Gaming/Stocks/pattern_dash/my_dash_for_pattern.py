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
from dash.dependencies import Input, Output, State
from pattern_data_container import pattern_data_handler as pdh
from datetime import datetime
import pandas as pd
import datetime as dt
import json
from playsound import playsound
from pattern_dash.pattern_shapes import MyPolygonShape, MyCircleShape, MyLineShape
from sertl_analytics.myconstants import MyAPPS
from pattern_dash.my_dash_base import MyDashBase
from pattern_detection_controller import PatternDetectionController
from sertl_analytics.constants.pattern_constants import CN
from pattern_configuration import config
from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod
from sertl_analytics.mydates import MyDate
from pattern import Pattern
from pattern_part import PatternPart
from pattern_range import PatternRange
from pattern_wave_tick import WaveTick, WaveTickList


class MyDash4Pattern(MyDashBase):
    def __init__(self):
        MyDashBase.__init__(self, MyAPPS.PATTERN_DETECTOR_DASH)
        self._pattern_controller = PatternDetectionController()
        self.detector = None
        self._options = []
        self._current_symbol = ''
        self.__fill_option_entries__()

    def get_stock_prices(self):
        print('get_stock_prices')
        # self.__fill_option_entries__()
        self.__set_app_layout__()
        self.__init_interval_callback__()
        self.__init_hover_over_callback__()
        self.__init_update_graph_callback__()

    def __fill_option_entries__(self):
        for symbol, name in config.ticker_dic.items():
            if self._current_symbol == '':
                self._current_symbol = symbol
            self._options.append({'label': '{} {}'.format(symbol, name), 'value': symbol})

    def __init_update_graph_callback__(self):
        if config.api_period == ApiPeriod.INTRADAY:
            @self.app.callback(
                Output('graphs', 'children'),
                [Input('submit-button', 'n_clicks')],
                [State('my_ticker_symbol', 'value')])
            def update_graph(n_clicks, ticker):
                return self.__append_graphs__(ticker)
        else:
            @self.app.callback(
                # Output('my_graph', 'figure'),
                Output('graphs', 'children'),
                [Input('submit-button', 'n_clicks')],
                [State('my_ticker_symbol', 'value'),
                 State('my_date_picker', 'start_date'),
                 State('my_date_picker', 'end_date')])
            def update_graph(n_clicks, ticker, start_date, end_date):
                start_date = datetime.strptime(start_date[:10], '%Y-%m-%d')
                date_end = datetime.strptime(end_date[:10], '%Y-%m-%d')
                and_clause = "Date BETWEEN '{}' AND '{}'".format(start_date, date_end)
                return self.__append_graphs__(ticker, and_clause)

    def __append_graphs__(self, ticker: str, and_clause=''):
        graphs = []
        self.detector = self._pattern_controller.get_detector_for_dash(ticker, and_clause)
        self.df = pdh.pattern_data.df
        candlestick = self.__get_candlesticks_trace__(self.df, ticker)
        bollinger_traces = self.__get_boolinger_band_trace__(self.df, ticker)
        shape_list = self.__get_shape__(self.df, 'line')
        shape_list += self.__get_pattern_shape_part_main_list__()
        shape_list += self.__get_shape__(self.df, 'circle')
        shapes = [my_shapes.shape_parameters for my_shapes in shape_list]
        annotations = [my_shapes.annotation_parameters for my_shapes in shape_list]
        graphs.append(self.__get_dcc_graphs__(ticker, candlestick, bollinger_traces, shapes, annotations))
        return graphs

    def __get_pattern_shape_part_main_list__(self):
        return_list = []
        for pattern in self.detector.pattern_list:
            return_list.append(DashInterface.get_pattern_shape_part_main(pattern))
        return return_list

    def __init_hover_over_callback__(self):
        self.app.callback(
            Output('hover-data', 'children'),
            [Input(self._current_symbol, 'hoverData')])(self.__create_callback__())

    def __init_interval_callback__(self):
        @self.app.callback(
            Output('interval-data', 'children'),
            [Input('interval-component', 'n_intervals')])
        def callback_interval(n_intervals):
            if n_intervals % 10 == 0:
                playsound('alarm01.wav')  # C:/Windows/media/...
            return 'Interval-updates: {} at {}'.format(n_intervals, dt.datetime.now())

    @staticmethod
    def __create_callback__():
        def callback_hover_data(hoverData):
            return json.dumps(hoverData, indent=2)
        return callback_hover_data

    @staticmethod
    def __get_shape__(df: pd.DataFrame, shape_type: str):
        range_value = df[CN.CLOSE].mean() / 100
        modulo_dict = {'line': 10, 'path': 8, 'circle': 3}
        shape_list = []
        row_start = None
        row_old = None
        for index, row in df.iterrows():
            if index % modulo_dict[shape_type] == 0:
                if row_start is None:
                    row_start = row
                else:
                    if shape_type == 'line':
                        shape_list.append(MyLineShape([str(row_start.Date), str(row.Date)], [row_start.Close, row.Close]))
                    elif shape_type == 'path':
                        x = [str(row_start.Date), str(row.Date), str(row.Date), str(row_start.Date)]
                        y = [row_start.High, row.High + range_value, row.Low - range_value, row_start.High]
                        shape_list.append(MyPolygonShape(x, y))
                    elif shape_type == 'circle':
                        shape_list.append(MyCircleShape(str(row_old.Date), row_old.High, range_value))
                    row_start = None
            row_old = row
        return shape_list

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
        html_element_list = [html.H1('Stock Ticker Dashboard')]
        html_element_list.append(self.__get_dcc_interval_element__())
        html_element_list.append(self.__get_html_div_with_ticker_drop_down__())
        if not config.api_period == ApiPeriod.INTRADAY:
            html_element_list.append(self.__get_html_div_with_date_picker_range__())
        html_element_list.append(self.__get_html_div_with_submit__())
        html_element_list.append(html.Div(id='graphs'))
        html_element_list.append(self.__get_html_div_for_hover_data__())
        html_element_list.append(self.__get_html_div_for_interval_data__())
        self.app.layout = html.Div(html_element_list)

    @staticmethod
    def __get_dcc_graphs__(ticker, candlestick, bollinger_traces, shapes, annotations):
        return dcc.Graph(
            id=ticker,
            figure={
                'data': [candlestick] + bollinger_traces,
                'layout': {
                    'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
                    'legend': {'x': 0},
                    'hovermode': 'closest',
                    'shapes': shapes,
                    'annotations': annotations
                }
            })

    @staticmethod
    def __get_dcc_interval_element__():
        return dcc.Interval(
                id='interval-component',
                interval=6000,  # 6000 milliseconds = 6 seconds
                n_intervals=0
            )

    def __get_html_div_with_ticker_drop_down__(self):
        return html.Div(
            [
                html.H3('Select stock symbols:', style={'paddingRight': '30px'}),
                dcc.Dropdown(id='my_ticker_symbol', options=self._options, value=self._current_symbol, multi=False)
            ],
            style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '30%'}
        )

    @staticmethod
    def __get_html_div_with_date_picker_range__():
        return html.Div(
            [
                html.H3('Select start and end dates:'),
                dcc.DatePickerRange(id='my_date_picker',
                                    min_date_allowed=datetime(2015, 1, 1), max_date_allowed=datetime.today(),
                                    start_date=datetime(2018, 1, 1), end_date=datetime.today())
            ],
            style={'display': 'inline-block'}
        )

    @staticmethod
    def __get_html_div_with_submit__():
        return html.Div(
            [
                html.Button(id='submit-button', n_clicks=0, children='Submit',
                            style={'fontSize': 24, 'marginLeft': '30px'})
            ],
            style={'display': 'inline-block'})

    @staticmethod
    def __get_html_div_for_hover_data__():
        return html.Div(
            [
                html.Pre(id='hover-data', style={'paddingTop': 35})
            ],
            style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}
        )

    @staticmethod
    def __get_html_div_for_interval_data__():
        return html.Div(
            [
                html.Pre(id='interval-data', style={'paddingTop': 35})
            ],
            style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}
        )


class DashInterface:
    @staticmethod
    def get_x_y_separated(xy):
        xy_array = np.array(xy)
        return xy_array[:, 0], xy_array[:, 1]

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
    def get_xy_from_timestamp_to_date(xy):
        if type(xy) == list:
            return [(MyDate.get_date_from_epoch_seconds(t_val[0]), t_val[1]) for t_val in xy]
        return str(MyDate.get_date_from_epoch_seconds(xy[0])), xy[1]

    @staticmethod
    def get_annotation_param(pattern: Pattern):
        annotation_param = pattern.get_annotation_parameter('blue')
        annotation_param.xy = DashInterface.get_xy_from_timestamp_to_date(annotation_param.xy)
        annotation_param.xy_text = DashInterface.get_xy_from_timestamp_to_date(annotation_param.xy_text)
        return annotation_param

    @staticmethod
    def get_pattern_shape_part_main(pattern: Pattern):
        xy = DashInterface.get_xy_from_timestamp_to_date(pattern.xy)
        print('get_pattern_shape_part_main: xy={}'.format(xy))
        x, y = DashInterface.get_x_y_separated(xy)
        return MyPolygonShape(x, y)

    @staticmethod
    def get_pattern_shape_part_trade(pattern: Pattern):
        xy_trade = DashInterface.get_xy_from_timestamp_to_date(pattern.xy_trade)
        return MyPolygonShape(np.array(xy_trade), True)

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
    def get_f_regression_shape(pattern_part: PatternPart):
        xy_regression = DashInterface.get_xy_from_timestamp_to_date(pattern_part.xy_regression)
        return MyPolygonShape(np.array(xy_regression), False)

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