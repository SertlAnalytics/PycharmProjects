"""
Description: This module is the base class for our dash - deferred classes required.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import colorlover as cl
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas_datareader.data as web  # requires v0.6.0 or later
from datetime import datetime
import pandas as pd
import datetime as dt
import json
from pattern_dash.pattern_shapes import MyPolygonShape, MyCircleShape, MyLineShape
from sertl_analytics.myconstants import MyAPPS
from pattern_dash.my_dash_base_tab_for_pattern import MyDashBase
from pattern_sound.pattern_sound_machine import PatternSoundMachine

"""
Description: This module is the main module for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""




class MyDash4Nasdaq(MyDashBase):
    def __init__(self):
        MyDashBase.__init__(self, MyAPPS.PATTERN_DETECTOR_DASH)
        self.options = self.__get_option_entries__()
        self.sound_machine = PatternSoundMachine()

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
                shape_list = self.__get_shape__(df, 'line') + self.__get_shape__(df, 'path') + self.__get_shape__(df,
                                                                                                                  'circle')
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
                self.sound_machine.play_alarm_new_pattern()
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
                style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}
            ),
            html.Div(
                [
                    html.Pre(id='interval-data', style={'paddingTop': 35})
                ],
                style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}
            )
        ])


if __name__ == '__main__':
    my_dash = MyDash4Nasdaq()
    my_dash.get_stock_prices()
    my_dash.run_on_server()