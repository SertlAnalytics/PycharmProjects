"""
Description: This module contains wrapper classes for dash components.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime
from sertl_analytics.mydates import MyDate


COLORS = [
    {
        'background': '#fef0d9',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#fdcc8a',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#fc8d59',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#d7301f',
        'text': 'rgb(30, 30, 30)'
    },
]


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


class MyHTMLTable:
    def __init__(self, rows: int, cols: int):
        self._rows = rows
        self._cols = cols
        self._row_range = range(1, self._rows + 1)
        self._col_range = range(1, self._cols + 1)
        self._list = [['' for col in self._col_range] for row in self._row_range]
        self._init_cells_()

    def set_value(self, row: int, col: int, value):
        self._list[row-1][col-1] = value

    def get_value(self, row: int, col: int):
        return self._list[row-1][col-1]

    def get_table(self):
        rows = []
        for row_number in self._row_range:
            row = []
            for col_number in self._col_range:
                value = self.get_value(row_number, col_number)
                cell_style = self._get_cell_style_(row_number, col_number)
                row.append(html.Td(value, style=cell_style))
            rows.append(html.Tr(row))
        return html.Table(rows, style=self._get_table_style_())

    def _init_cells_(self):
        pass

    def _get_cell_style_(self, row: int, col: int):
        pass

    def _get_table_style_(self):
        pass


class MyHTMLHeaderTable(MyHTMLTable):
    def __init__(self):
        MyHTMLTable.__init__(self, 2, 3)

    def _init_cells_(self):
        user_label_div = MyHTML.div('my_user_label_div', 'Username:', True)
        user_div = MyHTML.div('my_user_name_div', 'Josef Sertl', False)
        time_str = MyDate.get_time_from_datetime(datetime.now())
        login_label_div = MyHTML.div('my_login_label_div', 'Last login:', True, True)
        login_time_div = MyHTML.div('my_login_div', '{}'.format(time_str), False)
        last_refresh_label_div = MyHTML.div('my_last_refresh_label_div', 'Last refresh:', True)
        last_refresh_time_div = MyHTML.div('my_last_refresh_time_div', time_str)
        next_refresh_label_div = MyHTML.div('my_next_refresh_label_div', 'Next refresh:', True)
        next_refresh_time_div = MyHTML.div('my_next_refresh_time_div', time_str)
        ticker_label_div = MyHTML.div('my_ticker_label_div', 'Ticker:', True)
        ticker_div = MyHTML.div('my_ticker_div', '', False)
        time_label_div = MyHTML.div('my_time_label_div', 'Time:', True)
        time_div = MyHTML.div('my_time_div', '', False)

        my_user_div = MyHTML.div_embedded([user_label_div, MyHTML.span(' '), user_div])
        my_login_div = MyHTML.div_embedded([login_label_div, MyHTML.span(' '), login_time_div])

        last_refresh_div = MyHTML.div_embedded([last_refresh_label_div, MyHTML.span(' '), last_refresh_time_div])
        next_refresh_div = MyHTML.div_embedded([next_refresh_label_div, MyHTML.span(' '), next_refresh_time_div])

        self.set_value(1, 1, MyHTML.div_embedded([my_user_div, my_login_div]))
        self.set_value(1, 2, 'Pattern Detection Dashboard')
        self.set_value(1, 3, MyHTML.div_embedded([last_refresh_div, next_refresh_div]))
        self.set_value(2, 1, MyHTML.div_embedded([ticker_label_div, MyHTML.span(' '), ticker_div]))
        self.set_value(2, 2, MyDCC.markdown('my_ticket_markdown'))
        self.set_value(2, 3, MyHTML.div_embedded([time_label_div, MyHTML.span(' '), time_div]))

    def _get_cell_style_(self, row: int, col: int):
        padding = 5
        if row == 1:
            width = ['20%', '60%', '20%'][col-1]
            bg_color = COLORS[0]['background']
            color = COLORS[0]['text']
            text_align = ['left', 'center', 'left'][col-1]
            v_align = ['top', 'top', 'top'][col - 1]
            font_weight = ['normal', 'bold', 'normal'][col - 1]
            font_size = [16, 32, 16][col - 1]

            return {'width': width, 'background-color': bg_color, 'color': color, 'text-align': text_align,
                    'vertical-align': v_align, 'font-weight': font_weight, 'padding': padding, 'font-size': font_size}
        else:
            bg_color = COLORS[2]['background']
            color = COLORS[2]['text']
            text_align = ['left', 'center', 'left'][col - 1]
            v_align = ['top', 'top', 'top'][col - 1]
            return {'background-color': bg_color, 'color': color, 'text-align': text_align,
                    'vertical-align': v_align, 'padding': padding}

    def _get_table_style_(self):
        return {'padding': 5, 'width': '100%'}


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
    def div_embedded(embedded_element_list: list):
        return html.Div(embedded_element_list)

    @staticmethod
    def div(element_id: str, children='', bold=False, inline=True):
        style = {'font-weight': 'bold' if bold else 'normal'}
        if inline:
            style['display'] = 'inline-block'
        return html.Div(id=element_id, children=children, style=style)

    @staticmethod
    def h1(element_text: str, style_input=None):
        style = {'opacity': 1, 'color': 'black', 'fontSize': 12} if style_input is None else style_input
        return html.H1(element_text, style=style)

    @staticmethod
    def h2(element_text: str, color='black', font_size=12, opacity='1'):
        style = {'opacity': opacity, 'color': color, 'fontSize': font_size}
        return html.H2(element_text, style=style)

    @staticmethod
    def h3(element_text: str, color='black', font_size=24, opacity='1'):
        style = {'opacity': opacity, 'color': color, 'fontSize': font_size}
        return html.H3(element_text, style=style)

    @staticmethod
    def p(element_text: str):
        return html.P(element_text)

    @staticmethod
    def pre(element_id: str, children=''):
        return html.Pre(id=element_id, children=children, style={'padding-top': 20})

    @staticmethod
    def span(children=''):
        return html.Span(children=children)

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
            div_element_list.append(html.H3('{}:'.format(div_text), style={'padding-right': '10'}))
        div_element_list.append(MyDCC.drop_down(element_id, options, for_multi))
        style = {'display': 'inline-block', 'verticalAlign': 'top', 'width': width,
                 'padding-bottom': 20, 'padding-left': 10}
        return html.Div(div_element_list, style=style)


class MyDCC:
    @staticmethod
    def tabs(element_id: str, children: list):
        return dcc.Tabs(id=element_id, children=children)

    @staticmethod
    def tab(label: str, children: list):
        return dcc.Tab(label=label, children=children)

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
    def markdown(element_id: str, children=''):
        return dcc.Markdown(id=element_id, children=children)

    @staticmethod
    def RangeSlider():
        return dcc.RangeSlider

    @staticmethod
    def get_date_picker_range(element_id: str, start_date: datetime, end_date=datetime.today()):
        return dcc.DatePickerRange(id=element_id,
                                   min_date_allowed=datetime(2015, 1, 1), max_date_allowed=datetime.today(),
                                   start_date=start_date, end_date=end_date)

    @staticmethod
    def get_radio_items(element_id, options: list, inline=True):
        # {'label': '{} {}'.format(symbol, name), 'value': symbol}
        if inline:
            return dcc.RadioItems(id=element_id, options=options, value=options[0]['value'],
                                  labelStyle={'display': 'inline-block'})
        else:
            return dcc.RadioItems(id=element_id, options=options, value=options[0]['value'])

    @staticmethod
    def get_radio_items_inline(element_id, options: list, inline=True):
        return html.Div(
            [MyDCC.get_radio_items(element_id, options, inline)],
            style={'display': 'inline-block'})