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


USERNAME_PASSWORD_PAIRS = [['JamesBond', '007'],['LouisArmstrong', 'satchmo']]


class MyDash:
    def __init__(self):
        self.app = Dash()
        self.auth = dash_auth.BasicAuth(self.app, USERNAME_PASSWORD_PAIRS)
        if __name__ != '__main__':
            self.server = self.app.server
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
        options = self.__get_option_entries__()
        self.__get_app_layout__(options)
        self.__update_data_by_callback__()

    def __update_data_by_callback__(self):
        @self.app.callback(
            # Output('my_graph', 'figure'),
            Output('graphs', 'children'),
            [Input('submit-button', 'n_clicks')],
            [State('my_ticker_symbol', 'value'),
             State('my_date_picker', 'start_date'),
             State('my_date_picker', 'end_date')])
        def update_graph(n_clicks, tickers, start_date, end_date):
            start = datetime.strptime(start_date[:10], '%Y-%m-%d')
            end = datetime.strptime(end_date[:10], '%Y-%m-%d')
            graphs = []
            for ticker in tickers:
                df = web.DataReader(ticker, 'iex', start, end).reset_index()

                print(df.head())
                print('n_clicks={}'.format(n_clicks))
                candlestick = self.__get_candlesticks_trace__(df, ticker)
                bollinger_traces = self.__get_boolinger_band_trace__(df, ticker)
                polygon_trace = self.__get_polygon_trace__(df, ticker)

                graphs.append(dcc.Graph(
                    id=ticker,
                    figure={
                        'data': [candlestick] + bollinger_traces,
                        'layout': {
                            'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
                            'legend': {'x': 0},
                            'shapes': [self.__get_shape__('line'), self.__get_shape__('path')],
                            'annotations': [{
                                'x': '2018-04-02', 'y': 200.05,
                                'showarrow': False, 'xanchor': 'left',
                                'text': 'Increase Period Begins'
                            }]
                        }
                    }))

            return graphs

    @staticmethod
    def __get_shape__(shape_type: str):
        if shape_type == 'line':
            return {'type': 'line', 'x0': '2018-01-02', 'x1': '2018-04-02', 'y0': 400, 'y1': 200,
                   'line': {'color': 'k', 'width': 10}}
        elif shape_type == 'path':
            x = ['2018-01-02', '2018-04-02', '2018-04-02', '2018-01-02']
            y = [350, 200, 150, 200]
            path = MyDash.__get_svg_path__(x, y)
            print('path={}'.format(path))
            return {'type': 'path', 'path': path, 'fillcolor': 'red', 'opacity': 0.5,
                    'line': {'color': 'red', 'width': 5}}

    @staticmethod
    def __get_svg_path__(date_str_list: list, value_list: list):
        length = len(date_str_list)
        epoch = dt.datetime.utcfromtimestamp(0)
        svg_path = ''
        for k in range(0, length):
            date_value = datetime.strptime(date_str_list[k], '%Y-%m-%d')
            delta = date_value - epoch
            number_value = delta.days + 736693
            if k == 0:
                svg_path = 'M {},{}'.format(date_str_list[k], value_list[k])
            elif k == length - 1:
                svg_path += ' Z'
            else:
                svg_path += ' L {},{}'.format(date_str_list[k], value_list[k])
        return svg_path

    @staticmethod
    def __get_polygon_trace__(df, ticker):
        date_list = ['2018-01-02', '2018-02-02', '2018-01-02', '2018-01-02']
        value_list = [400, 200, 100, 400]
        polygon = {
            'x': date_list,
            'y': value_list,
            'type': 'polygon',
            'name': ticker,
            'legendgroup': ticker
        }
        return [polygon]

    @staticmethod
    def __get_candlesticks_trace__(df, ticker):
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

    def __get_boolinger_band_trace__(self, df, ticker):
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

    def __get_app_layout__(self, options):
        self.app.layout = html.Div([
            html.H1('Stock Ticker Dashboard'),
            html.Div([
                html.H3('Select stock symbols:', style={'paddingRight': '30px'}),
                dcc.Dropdown(id='my_ticker_symbol', options=options, value=['TSLA'], multi=True)
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '30%'}),
            html.Div([
                html.H3('Select start and end dates:'),
                dcc.DatePickerRange(id='my_date_picker',
                    min_date_allowed=datetime(2015, 1, 1), max_date_allowed=datetime.today(),
                    start_date=datetime(2018, 1, 1), end_date=datetime.today()
                )
            ], style={'display': 'inline-block'}),
            html.Div([
                html.Button(id='submit-button', n_clicks=0, children='Submit',
                            style={'fontSize': 24, 'marginLeft': '30px'}),
                ], style={'display': 'inline-block'}),
            # dcc.Graph(id='my_graph', figure={'data': [{'x': [1, 1000], 'y': [3000, 1]}]})
            html.Div(id='graphs')
            # dcc.Graph(id='my_graph')
        ])


my_dash = MyDash()
my_dash.get_stock_prices()
my_dash.run_on_server()