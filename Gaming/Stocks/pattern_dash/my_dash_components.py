"""
Description: This module contains wrapper classes for dash components.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime


class DccGraphApi:
    def __init__(self, graph_id: str, title: str):
        self.id = graph_id
        self.figure_data = None
        self.figure_layout_height = 500
        self.figure_layout_width = 1200
        self.figure_layout_yaxis_title = title
        self.figure_layout_margin = {'b': 0, 'r': 10, 'l': 60, 't': 0}
        self.figure_layout_legend = {'x': 0}
        self.figure_layout_hovermode = 'closest'
        self.figure_layout_shapes = None
        self.figure_layout_annotations = None


class DccGraphSecondApi(DccGraphApi):
    def __init__(self, graph_id: str, title: str):
        DccGraphApi.__init__(self, graph_id, title)
        self.figure_layout_height = self.figure_layout_height / 2
        self.figure_layout_width = self.figure_layout_width  # / 2


class MyHTML:
    @staticmethod
    def Button():
        return html.Button

    @staticmethod
    def button_submit(element_id: str, children='Submit'):
        return html.Button(id=element_id, n_clicks=0, children=children, hidden='hidden',
                style={'fontSize': 24, 'margin-left': '30px'})

    @staticmethod
    def div_with_html_button_submit(element_id: str, children='Submit'):
        return html.Div(
            [MyHTML.button_submit(element_id, children)],
            style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'bottom'
                , 'padding-bottom': 20, 'padding-left': 10}
        )

    @staticmethod
    def div(element_id: str, embedded_element_list: list = None):
        if embedded_element_list is None:
            return html.Div(id=element_id)
        else:
            return html.Div(embedded_element_list)

    @staticmethod
    def h1(element_text: str, color='black', font_size=12, opacity='1'):
        style = {'opacity': opacity, 'color': color, 'fontSize': font_size}
        return html.H1(element_text, style=style)

    @staticmethod
    def h2(element_text: str, color='black', font_size=12, opacity='1'):
        style = {'opacity': opacity, 'color': color, 'fontSize': font_size}
        return html.H2(element_text, style=style)

    @staticmethod
    def h3(element_text: str, color='black', font_size=12, opacity='1'):
        style = {'opacity': opacity, 'color': color, 'fontSize': font_size}
        return html.H3(element_text, style=style)

    @staticmethod
    def pre(element_id: str):
        return html.Pre(id=element_id, style={'padding-top': 20})

    @staticmethod
    def div_with_html_pre(element_id: str):
        return html.Div(
            [MyHTML.pre(element_id)],
            style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top', 'padding-bottom': 20}
        )

    @staticmethod
    def get_div_with_actual_date_time(element_id: str, color='black', font_size=12, opacity='1'):
        return html.Div([MyHTML.h1(datetime.now().strftime('%Y-%m-%d')),
                         MyHTML.h1(datetime.now().strftime('%H:%M:%S'))])

    @staticmethod
    def div_with_dcc_drop_down(div_text: str, element_id: str, options: list, width=20, for_multi=False):
        div_element_list = []
        if div_text != '':
            div_element_list.append(html.H3('{}:'.format(div_text), style={'padding-right': '30px'}))
        div_element_list.append(MyDCC.drop_down(element_id, options, for_multi))
        style = {'display': 'inline-block', 'verticalAlign': 'top', 'width': width,
                 'padding-bottom': 20, 'padding-left': 10}
        return html.Div(div_element_list, style=style)


class MyDCC:
    @staticmethod
    def drop_down(element_id, options: list, multi=False):
        # {'label': '{} {}'.format(symbol, name), 'value': symbol}
        return dcc.Dropdown(id=element_id, options=options, value=options[0]['value'], multi=multi)

    @staticmethod
    def graph(graph_api: DccGraphApi):
        return dcc.Graph(
            id=graph_api.id,
            figure={
                'data': graph_api.figure_data,
                'layout': {
                    # 'xaxis': {'title': 'ticker-x', 'type': 'date'},
                    'yaxis': {'title': graph_api.figure_layout_yaxis_title},
                    'height': graph_api.figure_layout_height,
                    'width': graph_api.figure_layout_width,
                    'margin': graph_api.figure_layout_margin,
                    'legend': graph_api.figure_layout_legend,
                    'hovermode': graph_api.figure_layout_hovermode,
                    'shapes': graph_api.figure_layout_shapes,
                    'annotations': graph_api.figure_layout_annotations
                }
            })

    @staticmethod
    def interval(element_id: str, seconds=10):
        print('get_interval: id={}, seconds={}'.format(element_id, seconds))
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