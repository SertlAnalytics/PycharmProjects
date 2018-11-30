"""
Description: This module is the main module for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""


import sertl_analytics.environment  # init some environment variables during load - for security reasons
from dash import Dash
import matplotlib
import matplotlib.pyplot as plt
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.figure_factory as ff
import dash_core_components as dcc
import dash_html_components as html
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

    def read_csv(self):
        self.df = pd.read_csv('salaries.csv')
        print(self.df.head())
        self.df.plot()
        # self._df.boxplot()
        # Dash.config
        plt.show()

    def app_with_http_basic_autentication(self):
        self.app.layout = html.Div([
            dcc.RangeSlider(
                id='range-slider',
                min=-5,
                max=6,
                marks={i: str(i) for i in range(-5, 7)},
                value=[-3, 4]
            ),
            html.H1(id='product')  # this is the output
        ], style={'width': '50%'})

        @self.app.callback(
            Output('product', 'children'),
            [Input('range-slider', 'value')])
        def update_value(value_list):
            return value_list[0] * value_list[1]

    def live_update_by_interval_web_data(self):
        self.app.layout = html.Div([
            html.Div([
                html.Iframe(src='https://www.sertl-analytics.com', height=500, width=1200)
            ]),

            html.Div([
                html.Pre(
                    id='counter_text',
                    children='Active flights worldwide:'
                ),
                dcc.Graph(id='live-update-graph', style={'width': 1200}),
                dcc.Interval(
                    id='interval-component',
                    interval=6000,  # 6000 milliseconds = 6 seconds
                    n_intervals=0
                )])
        ])
        counter_list = []

        @self.app.callback(Output('counter_text', 'children'),
                      [Input('interval-component', 'n_intervals')])
        def update_layout(n):
            url = "https://data-live.flightradar24.com/zones/fcgi/feed.js?faa=1\
                   &mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&stats=1"
            # A fake header is necessary to access the site:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = res.json()
            counter = 0
            for element in data["stats"]["total"]:
                counter += data["stats"]["total"][element]
            counter_list.append(counter)
            return 'Active flights worldwide: {}'.format(counter)

        @self.app.callback(Output('live-update-graph', 'figure'),
                      [Input('interval-component', 'n_intervals')])
        def update_graph(n):
            fig = go.Figure(
                data=[go.Scatter(
                    x=list(range(len(counter_list))),
                    y=counter_list,
                    mode='lines+markers'
                )])
            return fig

    def live_update_by_interval(self):
        self.app.layout = html.Div([
            html.H1(id='live-update-text'),
            dcc.Interval(
                id='interval-component',
                interval=2000,  # 2000 milliseconds = 2 seconds
                n_intervals=0
            )
        ])

        @self.app.callback(Output('live-update-text', 'children'),
                      [Input('interval-component', 'n_intervals')])
        def update_layout(n):
            return 'Crash free for {} refreshes'.format(n)

    def get_stock_prices(self):
        #######
        # First Milestone Project: Develop a Stock Ticker
        # dashboard that either allows the user to enter
        # a ticker _symbol into an input box, or to select
        # item(s) from a dropdown list, and uses pandas_datareader
        # to look up and display stock data on a graph.
        ######

        # EXPAND STOCK SYMBOL INPUT TO PERMIT MULTIPLE STOCK SELECTION
        nsdq = pd.read_csv('data/NASDAQcompanylist.csv')
        nsdq.set_index('Symbol', inplace=True)
        options = []
        for tic in nsdq.index:
            options.append({'label': '{} {}'.format(tic, nsdq.loc[tic]['Name']), 'value': tic})

            self.app.layout = html.Div([
            html.H1('Stock Ticker Dashboard'),
            html.Div([
                html.H3('Select stock symbols:', style={'paddingRight': '30px'}),
                dcc.Dropdown(
                    id='my_ticker_symbol',
                    options=options,
                    value=['TSLA'],
                    multi=True
                )
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '30%'}),
            html.Div([
                html.H3('Select start and end dates:'),
                dcc.DatePickerRange(
                    id='my_date_picker',
                    min_date_allowed=datetime(2015, 1, 1),
                    max_date_allowed=datetime.today(),
                    start_date=datetime(2018, 1, 1),
                    end_date=datetime.today()
                )
            ], style={'display': 'inline-block'}),
            html.Div([
                html.Button(
                    id='submit-button',
                    n_clicks=0,
                    children='Submit',
                    style={'fontSize': 24, 'marginLeft': '30px'}
                ),
            ], style={'display': 'inline-block'}),
            dcc.Graph(
                id='my_graph',
                figure={
                    'data': [
                        {'x': [1, 2], 'y': [3, 1]}
                    ]
                }
            )
        ])

        @self.app.callback(
            Output('my_graph', 'figure'),
            [Input('submit-button', 'n_clicks')],
            [State('my_ticker_symbol', 'value'),
             State('my_date_picker', 'start_date'),
             State('my_date_picker', 'end_date')])
        def update_graph(n_clicks, stock_ticker, start_date, end_date):
            start = datetime.strptime(start_date[:10], '%Y-%m-%d')
            end = datetime.strptime(end_date[:10], '%Y-%m-%d')
            traces = []
            for tic in stock_ticker:
                df = web.DataReader(tic, 'iex', start, end)
                traces.append({'x': df.index, 'y': df.close, 'name': tic})
            fig = {
                'data': traces,
                'layout': {'title': ', '.join(stock_ticker) + ' Closing Prices'}
            }
            return fig

    def update_graph_on_interaction(self):
        df = pd.read_csv('data/mpg.csv')

        # Add a random "jitter" to model_year to spread out the plot
        df['year'] = df['model_year'] + random.randint(-4, 5, len(df)) * 0.10

        self.app.layout = html.Div([
            html.Div([  # this Div contains our scatter plot
                dcc.Graph(
                    id='mpg_scatter',
                    figure={
                        'data': [go.Scatter(
                            x=df['year'] + 1900,  # our "jittered" data
                            y=df['mpg'],
                            text=df['name'],
                            hoverinfo='text',
                            mode='markers'
                        )],
                        'layout': go.Layout(
                            title='mpg.csv dataset',
                            xaxis={'title': 'model year'},
                            yaxis={'title': 'miles per gallon'},
                            hovermode='closest'
                        )
                    }
                )], style={'width': '50%', 'display': 'inline-block'}),
            html.Div([  # this Div contains our output graph and vehicle stats
                dcc.Graph(
                    id='mpg_line',
                    figure={
                        'data': [go.Scatter(
                            x=[0, 1],
                            y=[0, 1],
                            mode='lines'
                        )],
                        'layout': go.Layout(
                            title='acceleration',
                            margin={'l': 0}
                        )
                    }
                ),
                dcc.Markdown(
                    id='mpg_stats'
                )
            ], style={'width': '20%', 'height': '50%', 'display': 'inline-block'})
        ])

        @self.app.callback(
            Output('mpg_line', 'figure'),
            [Input('mpg_scatter', 'hoverData')])
        def callback_graph(hoverData):
            v_index = hoverData['points'][0]['pointIndex']
            fig = {
                'data': [go.Scatter(
                    x=[0, 1],
                    y=[0, 60 / df.iloc[v_index]['acceleration']],
                    mode='lines',
                    line={'width': 2 * df.iloc[v_index]['cylinders']}
                )],
                'layout': go.Layout(
                    title=df.iloc[v_index]['name'],
                    xaxis={'visible': False},
                    yaxis={'visible': False, 'range': [0, 60 / df['acceleration'].min()]},
                    margin={'l': 0},
                    height=300
                )
            }
            return fig

        @self.app.callback(
            Output('mpg_stats', 'children'),
            [Input('mpg_scatter', 'hoverData')])
        def callback_stats(hoverData):
            v_index = hoverData['points'][0]['pointIndex']
            stats = """
                {} cylinders
                {}cc displacement
                0 to 60mph in {} seconds
                """.format(df.iloc[v_index]['cylinders'],
                           df.iloc[v_index]['displacement'],
                           df.iloc[v_index]['acceleration'])
            return stats

    def handle_select_with_density(self):
        # create x and y arrays
        np.random.seed(10)  # for reproducible results
        x1 = np.linspace(0.1, 5, 50)  # left half
        x2 = np.linspace(5.1, 10, 50)  # right half
        y = np.random.randint(0, 50, 50)  # 50 random points

        # create three "half DataFrames"
        df1 = pd.DataFrame({'x': x1, 'y': y})
        df2 = pd.DataFrame({'x': x1, 'y': y})
        df3 = pd.DataFrame({'x': x2, 'y': y})

        # combine them into one DataFrame (df1 and df2 points overlap!)
        df = pd.concat([df1, df2, df3])

        self.app.layout = html.Div([
            html.Div([
                dcc.Graph(
                    id='plot',
                    figure={
                        'data': [
                            go.Scatter(
                                x=df['x'],
                                y=df['y'],
                                mode='markers'
                            )
                        ],
                        'layout': go.Layout(
                            title='Random Scatterplot',
                            hovermode='closest'
                        )
                    }
                )], style={'width': '30%', 'display': 'inline-block'}),

            html.Div([
                html.H1(id='density', style={'paddingTop': 25})
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ])

        @self.app.callback(
            Output('density', 'children'),
            [Input('plot', 'selectedData')])
        def find_density(selectedData):
            pts = len(selectedData['points'])
            rng_or_lp = list(selectedData.keys())
            rng_or_lp.remove('points')
            max_x = max(selectedData[rng_or_lp[0]]['x'])
            min_x = min(selectedData[rng_or_lp[0]]['x'])
            max_y = max(selectedData[rng_or_lp[0]]['y'])
            min_y = min(selectedData[rng_or_lp[0]]['y'])
            area = (max_x - min_x) * (max_y - min_y)
            d = pts / area
            return 'Density = {:.2f}'.format(d)

    def handle_select_data_with_json(self):
        df = pd.read_csv('data/wheels.csv')

        self.app.layout = html.Div([
            html.Div([
                dcc.Graph(
                    id='wheels-plot',
                    figure={
                        'data': [
                            go.Scatter(
                                x=df['color'],
                                y=df['wheels'],
                                dy=1,
                                mode='markers',
                                marker={
                                    'size': 12,
                                    'color': 'rgb(51,204,153)',
                                    'line': {'width': 2}
                                }
                            )
                        ],
                        'layout': go.Layout(
                            title='Wheels & Colors Scatterplot',
                            xaxis={'title': 'Color'},
                            yaxis={'title': '# of Wheels', 'nticks': 3},
                            hovermode='closest'
                        )
                    }
                )], style={'width': '30%', 'float': 'left'}),

            html.Div([
                html.Pre(id='selection', style={'paddingTop': 35})
            ], style={'width': '30%', 'display':'inline-block', 'verticalAlign': 'top'})
        ])

        @self.app.callback(
            Output('selection', 'children'),
            [Input('wheels-plot', 'selectedData')])
        def callback_image(selectedData):
            return json.dumps(selectedData, indent=2)

    def handle_hover_over_with_img(self):
        df = pd.read_csv('data/wheels.csv')

        self.app.layout = html.Div([
            html.Div([
                dcc.Graph(
                    id='wheels-plot',
                    figure={
                        'data': [
                            go.Scatter(
                                x=df['color'],
                                y=df['wheels'],
                                dy=1,
                                mode='markers',
                                marker={
                                    'size': 12,
                                    'color': 'rgb(51,204,153)',
                                    'line': {'width': 2}
                                }
                            )
                        ],
                        'layout': go.Layout(
                            title='Wheels & Colors Scatterplot',
                            xaxis={'title': 'Color'},
                            yaxis={'title': '# of Wheels', 'nticks': 3},
                            hovermode='closest'
                        )
                    }
                )], style={'width': '30%', 'float': 'left'}),

            html.Div([
                html.Img(id='hover-image', src='children', height=300)
            ], style={'paddingTop': 35})
        ])

        @self.app.callback(
            Output('hover-image', 'src'),
            [Input('wheels-plot', 'hoverData')])
        def callback_image(hoverData):
            wheel = hoverData['points'][0]['y']
            color = hoverData['points'][0]['x']
            path = 'images/'
            return self.encode_image(path + df[(df['wheels'] == wheel) & \
                                          (df['color'] == color)]['image'].values[0])

    def handle_hover_over_with_json(self):
        df = pd.read_csv('data/wheels.csv')

        self.app.layout = html.Div([
            html.Div([
                dcc.Graph(
                    id='wheels-plot',
                    figure={
                        'data': [
                            go.Scatter(
                                x=df['color'],
                                y=df['wheels'],
                                dy=1,
                                mode='markers',
                                marker={
                                    'size': 12,
                                    'color': 'rgb(51,204,153)',
                                    'line': {'width': 2}
                                }
                            )
                        ],
                        'layout': go.Layout(
                            title='Wheels & Colors Scatterplot',
                            xaxis={'title': 'Color'},
                            yaxis={'title': '# of Wheels', 'nticks': 3},
                            hovermode='closest'
                        )
                    }
                )], style={'width': '30%', 'float': 'left'}),

            html.Div([
                html.Pre(id='hover-data', style={'paddingTop': 35})
            ], style={'width': '30%', 'display':'inline-block', 'verticalAlign': 'top'})
        ])

        @self.app.callback(
            Output('hover-data', 'children'),
            [Input('wheels-plot', 'hoverData')])
        def callback_image(hoverData):
            return json.dumps(hoverData, indent=2)

    def handle_callback_states(self):
        self.app.layout = html.Div([
            dcc.Input(
                id='number-in',
                value=1,
                style={'fontSize': 28}
            ),
            html.Button(
                id='submit-button',
                n_clicks=0,
                children='Submit',
                style={'fontSize': 28}
            ),
            html.H1(id='number-out')
        ])

        @self.app.callback(
            Output('number-out', 'children'),
            [Input('submit-button', 'n_clicks')],
            [State('number-in', 'value')])
        def output(n_clicks, number):
            return '{} displayed after {} clicks'.format(number, n_clicks)

    def handle_callbacks_exercise(self):
        # Create a Dash layout that contains input components
        # and at least one output. Assign IDs to each component:
        self.app.layout = html.Div([
            dcc.RangeSlider(  # this is the input
                id='range-slider',
                min=-5,
                max=6,
                marks={i: str(i) for i in range(-5, 7)},
                value=[-3, 4]
            ),
            html.H1(id='product')  # this is the output
        ], style={'width': '50%'})

        # Create a Dash callback:
        @self.app.callback(
            Output('product', 'children'),
            [Input('range-slider', 'value')])
        def update_value(value_list):
            return value_list[0] * value_list[1]

    @staticmethod
    def encode_image(image_file):
        encoded = base64.b64encode(open(image_file, 'rb').read())
        return 'data:image/png;base64,{}'.format(encoded.decode())

    def handle_callbacks_for_several_outputs_with_img(self):
        df = pd.read_csv('data/wheels.csv')

        self.app.layout = html.Div([
            dcc.RadioItems(
                id='wheels',
                options=[{'label': i, 'value': i} for i in df['wheels'].unique()],
                value=1
            ),
            html.Div(id='wheels-output'),

            html.Hr(),  # add a horizontal rule
            dcc.RadioItems(
                id='colors',
                options=[{'label': i, 'value': i} for i in df['color'].unique()],
                value='blue'
            ),
            html.Div(id='colors-output'),
            html.Img(id='display-image', src='children', height=300)
        ], style={'fontFamily': 'helvetica', 'fontSize': 18})

        @self.app.callback(
            Output('wheels-output', 'children'),
            [Input('wheels', 'value')])
        def callback_a(wheels_value):
            return 'You\'ve selected "{}"'.format(wheels_value)

        @self.app.callback(
            Output('colors-output', 'children'),
            [Input('colors', 'value')])
        def callback_b(colors_value):
            return 'You\'ve selected "{}"'.format(colors_value)

        @self.app.callback(
            Output('display-image', 'src'),
            [Input('wheels', 'value'),
             Input('colors', 'value')])
        def callback_image(wheel, color):
            path = 'images/'
            return self.encode_image(path + df[(df['wheels'] == wheel) & \
                                          (df['color'] == color)]['image'].values[0])

    def handle_callbacks_for_several_outputs(self):
        df = pd.read_csv('data/wheels.csv')

        self.app.layout = html.Div([
            dcc.RadioItems(
                id='wheels',
                options=[{'label': i, 'value': i} for i in df['wheels'].unique()],
                value=1
            ),
            html.Div(id='wheels-output'),

            html.Hr(),  # add a horizontal rule
            dcc.RadioItems(
                id='colors',
                options=[{'label': i, 'value': i} for i in df['color'].unique()],
                value='blue'
            ),
            html.Div(id='colors-output')
        ], style={'fontFamily': 'helvetica', 'fontSize': 18})

        @self.app.callback(
            Output('wheels-output', 'children'),
            [Input('wheels', 'value')])
        def callback_a(wheels_value):
            return 'You\'ve selected "{}"'.format(wheels_value)

        @self.app.callback(
            Output('colors-output', 'children'),
            [Input('colors', 'value')])
        def callback_b(colors_value):
            return 'You\'ve selected "{}"'.format(colors_value)

    def handle_callbacks_for_several_inputs_on_stock_market(self):
        df = pd.read_csv(
            'https://gist.githubusercontent.com/chriddyp/'
            'cb5392c35661370d95f300086accea51/raw/'
            '8e0768211f6b747c0db42a9ce9a0937dafcbd8b2/'
            'indicators.csv')

        available_indicators = df['Indicator Name'].unique()

        self.app.layout = html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='xaxis-column',
                        options=[{'label': i, 'value': i} for i in available_indicators],
                        value='Fertility rate, total (births per woman)'
                    ),
                    dcc.RadioItems(
                        id='xaxis-type',
                        options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                        value='Linear',
                        labelStyle={'display': 'inline-block'}
                    )
                ],
                    style={'width': '48%', 'display': 'inline-block'}),

                html.Div([
                    dcc.Dropdown(
                        id='yaxis-column',
                        options=[{'label': i, 'value': i} for i in available_indicators],
                        value='Life expectancy at birth, total (years)'
                    ),
                    dcc.RadioItems(
                        id='yaxis-type',
                        options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                        value='Linear',
                        labelStyle={'display': 'inline-block'}
                    )
                ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
            ]),

            dcc.Graph(id='indicator-graphic'),

            dcc.Slider(
                id='year--slider',
                min=df['Year'].min(),
                max=df['Year'].max(),
                value=df['Year'].max(),
                step=None,
                marks={str(year): str(year) for year in df['Year'].unique()}
            )
        ], style={'padding': 10})

        @self.app.callback(
            Output('indicator-graphic', 'figure'),
            [Input('xaxis-column', 'value'),
             Input('yaxis-column', 'value'),
             Input('xaxis-type', 'value'),
             Input('yaxis-type', 'value'),
             Input('year--slider', 'value')])
        def update_graph(xaxis_column_name, yaxis_column_name,
                         xaxis_type, yaxis_type,
                         year_value):
            dff = df[df['Year'] == year_value]
            return {
                'data': [go.Scatter(
                    x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
                    y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
                    text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                    mode='markers',
                    marker={
                        'size': 15,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}
                    }
                )],
                'layout': go.Layout(
                    xaxis={
                        'title': xaxis_column_name,
                        'type': 'linear' if xaxis_type == 'Linear' else 'log'
                    },
                    yaxis={
                        'title': yaxis_column_name,
                        'type': 'linear' if yaxis_type == 'Linear' else 'log'
                    },
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
                    hovermode='closest'
                )
            }

    def handle_callbacks_for_several_inputs(self):
        df = pd.read_csv('data/mpg.csv')

        features = df.columns

        self.app.layout = html.Div([

            html.Div([
                dcc.Dropdown(
                    id='xaxis',
                    options=[{'label': i.title(), 'value': i} for i in features],
                    value='displacement'
                )
            ],
                style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                dcc.Dropdown(
                    id='yaxis',
                    options=[{'label': i.title(), 'value': i} for i in features],
                    value='acceleration'
                )
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

            dcc.Graph(id='feature-graphic')
        ], style={'padding': 10})

        @self.app.callback(
            Output('feature-graphic', 'figure'),
            [Input('xaxis', 'value'),
             Input('yaxis', 'value')])
        def update_graph(xaxis_name, yaxis_name):
            return {
                'data': [go.Scatter(
                    x=df[xaxis_name],
                    y=df[yaxis_name],
                    text=df['name'],
                    mode='markers',
                    marker={
                        'size': 15,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}
                    }
                )],
                'layout': go.Layout(
                    xaxis={'title': xaxis_name.title()},
                    yaxis={'title': yaxis_name.title()},
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
                    hovermode='closest'
                )
            }

    def handle_callbacks_for_single_input_and_graph(self):
        # https://dash.plot.ly/dash-core-components/dropdown
        # We need to construct a dictionary of dropdown values for the years
        df = pd.read_csv('data/gapminderDataFiveYear.csv')

        year_options = []
        for year in df['year'].unique():
            year_options.append({'label': str(year), 'value': year})

        self.app.layout = html.Div([
            dcc.Graph(id='graph'),
            dcc.Dropdown(id='year-picker', options=year_options, value=df['year'].min())
        ])

        @self.app.callback(Output('graph', 'figure'),
                      [Input('year-picker', 'value')])
        def update_figure(selected_year):
            filtered_df = df[df['year'] == selected_year]
            traces = []
            for continent_name in filtered_df['continent'].unique():
                df_by_continent = filtered_df[filtered_df['continent'] == continent_name]
                traces.append(go.Scatter(
                    x=df_by_continent['gdpPercap'],
                    y=df_by_continent['lifeExp'],
                    text=df_by_continent['country'],
                    mode='markers',
                    opacity=0.7,
                    marker={'size': 15},
                    name=continent_name
                ))

            return {
                'data': traces,
                'layout': go.Layout(
                    xaxis={'type': 'log', 'title': 'GDP Per Capita'},
                    yaxis={'title': 'Life Expectancy'},
                    hovermode='closest'
                )
            }

    def embed_callbacks_input_div(self):
        self.app.layout = html.Div([
            dcc.Input(id='my-id', value='initial value', type='text'),
            html.Div(id='my-div', style={'border': '2px blue solid'}, children='Start')
        ])

        @self.app.callback(
            Output(component_id='my-div', component_property='children'),
            [Input(component_id='my-id', component_property='value')]
        )
        def update_output_div(input_value):
            return 'You\'ve entered "{}"'.format(input_value)

    def embed_markdowns(self):
        markdown_text = dedent('''
        ### Dash and Markdown
        Dash apps can be written in Markdown.
        Dash uses the [CommonMark](http://commonmark.org/) specification of Markdown.
        Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
        if this is your first introduction to Markdown!
        Markdown includes syntax for things like **bold text** and *italics*,
        [Link](http://commonmark.org/help), inline `code` snippets, lists,
        quotes, and more.
        ''')

        self.app.layout = html.Div([
            dcc.Markdown(children=markdown_text)
        ])

    def embed_core_components(self):
        #######
        # This provides examples of Dash Core Components.
        # Feel free to add things to it that you find useful.
        ######
        self.app.layout = html.Div([

            # DROPDOWN https://dash.plot.ly/dash-core-components/dropdown
            html.Label('Dropdown'),
            dcc.Dropdown(
                options=[
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': 'Montréal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'}
                ],
                value='MTL'
            ),

            html.Label('Multi-Select Dropdown'),
            dcc.Dropdown(
                options=[
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': u'Montréal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'}
                ],
                value=['MTL', 'SF'],
                multi=True
            ),

            # SLIDER https://dash.plot.ly/dash-core-components/slider
            html.Label('Slider'),
            html.P(
                dcc.Slider(
                    min=-5,
                    max=10,
                    step=0.5,
                    marks={i: i for i in range(-5, 11)},
                    value=-3
                )),

            # RADIO ITEMS https://dash.plot.ly/dash-core-components/radioitems
            html.Label('Radio Items'),
            dcc.RadioItems(
                options=[
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': 'Montréal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'}
                ],
                value='MTL'
            )
        ], style={'width': '50%'})

    def embed_html_components(self):
        #######
        # This provides examples of Dash HTML Components.
        # Feel free to add things to it that you find useful.
        ######
        self.app.layout = html.Div([
            'This is the outermost Div',
            html.Div(
                'This is an inner Div',
                style={'color': 'blue', 'border': '2px blue solid', 'borderRadius': 5,
                       'padding': 10, 'width': 220}
            ),
            html.Div(
                'This is another inner Div',
                style={'color': 'green', 'border': '2px green solid',
                       'margin': 10, 'width': 220}
            ),
        ],
            # this styles the outermost Div:
            style={'width': 500, 'height': 200, 'color': 'red', 'border': '2px red dotted'})

    def embed_plotly_scatter(self):
        # Creating DATA
        np.random.seed(42)
        random_x = np.random.randint(1, 101, 100)
        random_y = np.random.randint(1, 101, 100)

        self.app.layout = html.Div([dcc.Graph(id='scatterplot',
                                         figure={'data': [
                                             go.Scatter(
                                                 x=random_x,
                                                 y=random_y,
                                                 mode='markers',
                                                 marker={
                                                     'size': 12,
                                                     'color': 'rgb(51,204,153)',
                                                     '_symbol': 'pentagon',
                                                     'line': {'width': 2}
                                                 }
                                             )],
                                             'layout': go.Layout(title='My Scatterplot',
                                                                 xaxis={'title': 'Some X title'})}
                                         ),
                               dcc.Graph(id='scatterplot2',
                                         figure={'data': [
                                             go.Scatter(
                                                 x=random_x,
                                                 y=random_y,
                                                 mode='markers',
                                                 marker={
                                                     'size': 12,
                                                     'color': 'rgb(200,204,53)',
                                                     '_symbol': 'pentagon',
                                                     'line': {'width': 2}
                                                 }
                                             )],
                                             'layout': go.Layout(title='Second Plot',
                                                                 xaxis={'title': 'Some X title'})}
                                         )])

    def embed_graph(self):
        colors = {
            'background': '#111111',
            'text': '#7FDBFF'
        }

        self.app.layout = html.Div(children=[
            html.H1(
                children='Hello Dash',
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
            ),

            html.Div(
                children='Dash: A web application framework for Python.',
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
            ),

            dcc.Graph(
                id='example-graph',
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                        {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                    ],
                    'layout': {
                        'plot_bgcolor': colors['background'],
                        'paper_bgcolor': colors['background'],
                        'font': {
                            'color': colors['text']
                        },
                        'title': 'Dash Data Visualization'
                    }
                }
            )],
            style={'backgroundColor': colors['background']}
        )

my_dash = MyDash()
my_dash.handle_hover_over_with_json()
my_dash.run_on_server()