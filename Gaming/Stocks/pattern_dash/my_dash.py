"""
Description: This module is the main module for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""


import sertl_analytics.environment  # init some environment variables during load - for security reasons
from dash import Dash
import colorlover as cl
import matplotlib
import matplotlib.pyplot as plt
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.figure_factory as ff
import dash_core_components as dcc
import dash_html_components as html
# from pattern_dash.my_dash_components import MyDCC as dcc
# from pattern_dash.my_dash_components import MyHTML as html
import numpy as np
from textwrap import dedent
from dash.dependencies import Input, Output, State
import base64
import json
from numpy import random
import pandas_datareader.data as web  # requires v0.6.0 or later
import dash_auth
from datetime import datetime
import pandas as pd
import requests
import datetime as dt
import json
from playsound import playsound


USERNAME_PASSWORD_PAIRS = [['JamesBond', '007'],['LouisArmstrong', 'satchmo']]


class MyShape:
    def __init__(self, x: list, y: list):
        self.x = x
        self.y = y
        self._visible = True

    @property
    def shape_parameters(self):
        return self.__get_shape_parameter_dict__()

    @property
    def annotation_parameters(self):
        return self.__get_annotation_parameter_dict__()

    def __get_svg_path__(self):
        length = len(self.x)
        svg_path = ''
        for k in range(0, length):
            if k == 0:
                svg_path = 'M {},{}'.format(self.x[k], self.y[k])
            elif k == length - 1:
                svg_path += ' Z'
            else:
                svg_path += ' L {},{}'.format(self.x[k], self.y[k])
        return svg_path

    def __get_shape_parameter_dict__(self) -> dict:
        pass

    def __get_annotation_parameter_dict__(self) -> dict:
        pass


class MyLineShape(MyShape):
    def __get_shape_parameter_dict__(self) -> dict:
        return {'type': 'line', 'visible': self._visible, 'line': {'color': 'k', 'width': 1},
                'x0': self.x[0], 'x1': self.x[1], 'y0': self.y[0], 'y1': self.y[1]}


class MyPolygonShape(MyShape):
    def __get_shape_parameter_dict__(self) -> dict:
        return {'type': 'path', 'visible': self._visible,
                'path': self.__get_svg_path__(), 'line': {'color': 'red', 'width': 1},
                'fillcolor': 'red', 'opacity': 0.3}

    def __get_annotation_parameter_dict__(self) -> dict:
        return {'x': self.x[0], 'y': self.y[0],
                'showarrow': False, 'xanchor': 'left',
                'text': 'Increase Period Begins'}


class MyCircleShape(MyShape):
    def __init__(self, x_center: float, y_center: float, radius: float):
        self.radius = radius
        MyShape.__init__(self, [x_center], [y_center])

    def __get_shape_parameter_dict__(self) -> dict:
        date_value = dt.datetime.strptime(self.x[0], '%Y-%m-%d')
        date_value = date_value + dt.timedelta(days=1)
        return {'type': 'circle', 'visible': self._visible, 'xref': 'x', 'yref': 'y',
                'x0': self.x[0], 'x1': date_value.strftime("%Y-%m-%d"),
                'y0': self.y[0], 'y1': self.y[0] + self.radius,
                'fillcolor': 'yellow',
                'line': {'color': 'yellow', 'width': 1}}


class MyDash:
    def __init__(self):
        self.app = Dash()
        self.app.config.supress_callback_exceptions = True
        self.auth = dash_auth.BasicAuth(self.app, USERNAME_PASSWORD_PAIRS)
        if __name__ != '__main__':
            self.server = self.app.server
        self.options = self.__get_option_entries__()
        self.df = None

    def run_on_server(self):
        if __name__ == '__main__':
            self.app.run_server()

    def __get_option_entries__(self) -> list:
        nsdq = pd.read_csv('NASDAQcompanylist.csv')
        nsdq.set_index('Symbol', inplace=True)
        options = []
        for tic in nsdq.index:
            options.append({'label': '{} {}'.format(tic, nsdq.loc[tic]['Name']), 'value': tic})
        return options

    def get_stock_prices(self):
        print('get_stock_prices')
        self.__set_app_layout__()
        self.__init_interval_callback__()
        self.__init_hover_over_callback__()
        self.__init_update_graph_callback__()

    def __init_update_graph_callback__(self):
        @self.app.callback(
            # Output('my_graph', 'figure'),
            Output('graphs', 'children'),
            [Input('submit-button', 'n_clicks')],
            [State('my_ticker_symbol', 'value'),
             State('my_date_picker', 'start_date'),
             State('my_date_picker', 'end_date')])
        def update_graph(n_clicks, tickers, start_date, end_date):
            self.tickers = tickers
            start = datetime.strptime(start_date[:10], '%Y-%m-%d')
            end = datetime.strptime(end_date[:10], '%Y-%m-%d')
            graphs = []
            for ticker in self.tickers:
                df = web.DataReader(ticker, 'iex', start, end).reset_index()
                print(df.head())
                print('n_clicks={}'.format(n_clicks))
                candlestick = self.__get_candlesticks_trace__(df, ticker)
                bollinger_traces = self.__get_boolinger_band_trace__(df, ticker)
                shape_list = self.__get_shape__(df, 'line') + self.__get_shape__(df, 'path') + self.__get_shape__(df, 'circle')
                shapes = [my_shapes.shape_parameters for my_shapes in shape_list]
                annotations = [my_shapes.annotation_parameters for my_shapes in shape_list]
                graphs.append(dcc.Graph(
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
                    }))
            return graphs

    def __init_hover_over_callback__(self):
        self.app.callback(
            Output('hover-data', 'children'),
            [Input('TSLA', 'hoverData')])(self.__create_callback__())
        # def callback_image(hoverData):
        #     print(hoverData)
        #     return json.dumps(hoverData, indent=2)
        # )

    def __init_interval_callback__(self):
        @self.app.callback(
            Output('interval-data', 'children'),
            [Input('interval-component', 'n_intervals')])
        def callback_interval(n_intervals):
            if n_intervals % 10 == 0:
                playsound('C:/Windows/media/alarm01.wav')
            return 'Interval-updates: {} at {}'.format(n_intervals, dt.datetime.now())

    @staticmethod
    def __create_callback__():
        def callback_hover_data(hoverData):
            return json.dumps(hoverData, indent=2)
        return callback_hover_data

    @staticmethod
    def __get_shape__(df: pd.DataFrame, shape_type: str):
        range_value = df['close'].mean() / 100
        shape_list = []
        row_start = None
        row_old = None
        if shape_type == 'line':
            for index, row in df.iterrows():
                if index % 10 == 0:
                    if row_start is None:
                        row_start = row
                    else:
                        shape_list.append(MyLineShape([row_start.date, row.date], [row_start.close, row.close]))
                        row_start = None
        elif shape_type == 'path':
            for index, row in df.iterrows():
                if index % 8 == 0:
                    if row_start is None:
                        row_start = row
                    else:
                        x = [row_start.date, row.date, row.date, row_start.date]
                        y = [row_start.high, row.high + range_value, row.low - range_value, row_start.high]
                        shape_list.append(MyPolygonShape(x, y))
                        row_start = None
        elif shape_type == 'circle':
            for index, row in df.iterrows():
                if index % 3 == 0:
                    if row_start is None:
                        row_start = row
                    else:
                        shape_list.append(MyCircleShape(row_old.date, row_old.high, range_value))
                        row_start = None
                row_old = row
        return shape_list

    @staticmethod
    def __get_candlesticks_trace__(df: pd.DataFrame, ticker: str):
        candlestick = {
            'x': df['date'],
            'open': df['open'],
            'high': df['high'],
            'low': df['low'],
            'close': df['close'],
            'type': 'candlestick',
            'name': ticker,
            'legendgroup': ticker,
            'hoverover': 'skip',
            'increasing': {'line': {'color': 'g'}},
            'decreasing': {'line': {'color': 'r'}}
        }
        return candlestick

    def __get_boolinger_band_trace__(self, df: pd.DataFrame, ticker: str):
        colorscale = cl.scales['9']['qual']['Paired']
        bb_bands = self.__get_bollinger_band_values__(df['close'])

        bollinger_traces = [{
            'x': df['date'],
            'y': y,
            'type': 'scatter', 'mode': 'lines',
            'line': {'width': 1, 'color': colorscale[(i * 2) % len(colorscale)]},
            'hoverinfo': 'none',
            'legendgroup': ticker + ' - Bollinger',
            'showlegend': True if i == 0 else False,
            'name': '{} - bollinger bands'.format(ticker)
        } for i, y in enumerate(bb_bands)]

        return bollinger_traces

    def __get_bollinger_band_values__(self, price: pd.DataFrame, window_size=10, num_of_std=5):
        rolling_mean = price.rolling(window=window_size).mean()
        rolling_std = price.rolling(window=window_size).std()
        upper_band = rolling_mean + (rolling_std * num_of_std)
        lower_band = rolling_mean - (rolling_std * num_of_std)
        return [rolling_mean, upper_band, lower_band]

    def __set_app_layout__(self):
        self.app.layout = html.Div([
            html.H1('Stock Ticker Dashboard'),
            dcc.Interval(
                id='interval-component',
                interval=6000,  # 6000 milliseconds = 6 seconds
                n_intervals=0
            ),
            html.Div(
                [
                    html.H3('Select stock symbols:', style={'paddingRight': '30px'}),
                    dcc.Dropdown(id='my_ticker_symbol', options=self.options, value=['TSLA'], multi=True)
                ],
                style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '30%'}
            ),
            html.Div(
                [
                    html.H3('Select start and end dates:'),
                    dcc.DatePickerRange(id='my_date_picker',
                        min_date_allowed=datetime(2015, 1, 1), max_date_allowed=datetime.today(),
                        start_date=datetime(2018, 1, 1), end_date=datetime.today())
                ],
                style={'display': 'inline-block'}
            ),
            html.Div(
                [
                    html.Button(id='submit-button', n_clicks=0, children='Submit',
                                style={'fontSize': 24, 'marginLeft': '30px'})
                ],
                style={'display': 'inline-block'}),
            html.Div(id='graphs'),
            html.Div(
                [
                    html.Pre(id='hover-data', style={'paddingTop': 35})
                ],
                style={'width': '30%', 'display':'inline-block', 'verticalAlign': 'top'}
            ),
            html.Div(
                [
                    html.Pre(id='interval-data', style={'paddingTop': 35})
                ],
                style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}
            )
        ])


my_dash = MyDash()
my_dash.get_stock_prices()
my_dash.run_on_server()