"""
Description: This module contains wrapper classes for dash components.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime


class MyHTML:
    @staticmethod
    def Button():
        return html.Button

    @staticmethod
    def get_submit_button():
        return html.Button(id='submit-button', n_clicks=0, children='Submit',
                style={'fontSize': 24, 'marginLeft': '30px'})

    @staticmethod
    def Div():
        return html.Div

    @staticmethod
    def Iframe():
        return html.Iframe

    @staticmethod
    def H1():
        return html.H1

    @staticmethod
    def H2():
        return html.H2

    @staticmethod
    def H3():
        return html.H3

    @staticmethod
    def get_pre(element_id: str):
        return html.Pre(id=element_id, style={'paddingTop': 35})


class MyDCC:
    @staticmethod
    def get_drop_down(element_id, options: list, multi=False):
        # {'label': '{} {}'.format(symbol, name), 'value': symbol}
        return dcc.Dropdown(id=element_id, options=options, value=options[0]['value'], multi=multi)

    @staticmethod
    def get_graph(element_id, data: list, shapes: list, annotations: list):
        return dcc.Graph(
            id=element_id,
            figure={
                'data': data,
                'layout': {
                    'height': 500,
                    'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
                    'legend': {'x': 0},
                    'hovermode': 'closest',
                    'shapes': shapes,
                    'annotations': annotations
                }
            })

    @staticmethod
    def get_interval(element_id: str, seconds=10):
        return dcc.Interval(id=element_id, interval=seconds * 1000, n_intervals=0)

    @staticmethod
    def Markdown():
        return dcc.Markdown

    @staticmethod
    def RangeSlider():
        return dcc.RangeSlider

    @staticmethod
    def get_date_picker_range(element_id: str, start_date: datetime, end_date=datetime.today()):
        return dcc.DatePickerRange(id=element_id,
                                   min_date_allowed=datetime(2015, 1, 1), max_date_allowed=datetime.today(),
                                   start_date=start_date, end_date=end_date)

    @staticmethod
    def get_ratio_items(element_id, options: list, inline=True):
        # {'label': '{} {}'.format(symbol, name), 'value': symbol}
        if inline:
            return dcc.RadioItems(id=element_id, options=options, value=options[0]['value'],
                                  labelStyle={'display': 'inline-block'})
        else:
            return dcc.RadioItems(id=element_id, options=options, value=options[0]['value'])

    @staticmethod
    def get_radio_items_inline(element_id, options: list, inline=True):
        return html.Div(
            [MyDCC.get_ratio_items(element_id, options, inline)],
            style={'display': 'inline-block'})