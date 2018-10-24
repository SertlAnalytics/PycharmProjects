"""
Description: This module contains wrapper classes for dash components.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dte
from datetime import datetime
from sertl_analytics.mydates import MyDate
import pandas as pd
from abc import ABCMeta, abstractmethod


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


class DropDownHandler:
    __metaclass__ = ABCMeta

    @classmethod
    def version(cls): return 1.0

    def __init__(self):
        self._drop_down_value_dict = self.__get_drop_down_value_dict__()

    def get_element_id(self, drop_down_type: str):
        return self.__get_element_id__(drop_down_type)

    def get_embracing_div_id(self, drop_down_type: str):
        return '{}_div'.format(self.__get_element_id__(drop_down_type))

    def get_drop_down_type_by_embracing_div_id(self, div_id: str):
        for drop_down_type in self._drop_down_value_dict:
            if self.get_embracing_div_id(drop_down_type) == div_id:
                return drop_down_type
        return ''

    def get_style_display(self, drop_down_type: str):
        return {
            'display': 'inline-block',
            'verticalAlign': 'top',
            'width': self.__get_width__(drop_down_type),
            'padding-bottom': 20,
            'padding-left': 10
        }

    def get_drop_down_parameters(self, drop_down_type: str, default_value=None):
        return {
            'div_text': self.__get_div_text__(drop_down_type),
            'element_id': self.__get_element_id__(drop_down_type),
            'options': self.__get_options__(drop_down_type),
            'default': self.__get_default_value__(drop_down_type, default_value),
            'width': self.__get_width__(drop_down_type),
            'for_multi': self.__get_for_multi__(drop_down_type)
        }

    @abstractmethod
    def __get_drop_down_value_dict__(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def __get_div_text__(self, drop_down_type: str):
        raise NotImplementedError

    @abstractmethod
    def __get_element_id__(self, drop_down_type: str):
        raise NotImplementedError

    def __get_options__(self, drop_down_type: str):
        li = self._drop_down_value_dict[drop_down_type]
        if li[0].__class__.__name__ == 'dict':  # already label - value entries
            return li
        return [{'label': value.replace('_', ' '), 'value': value} for value in li]

    @abstractmethod
    def __get_default_value__(self, drop_down_type: str, default_value=None) -> str:
        raise NotImplementedError

    @abstractmethod
    def __get_width__(self, drop_down_type: str):
        raise NotImplementedError

    @abstractmethod
    def __get_for_multi__(self, drop_down_type: str):
        raise NotImplementedError


class DccGraphApi:
    def __init__(self, graph_id: str, title: str):
        self.period = ''
        self.id = graph_id
        self.ticker_id = ''
        self.df = None
        self.pattern_trade = None
        self.figure_data = None
        self.figure_layout_auto_size = False
        self.figure_layout_height = 500
        self.figure_layout_width = 1200
        self.figure_layout_yaxis_title = title
        self.figure_layout_margin = {'b': 50, 'r': 50, 'l': 50, 't': 50}
        self.figure_layout_legend = {'x': +5}
        self.figure_layout_hovermode = 'closest'
        self.figure_layout_shapes = None
        self.figure_layout_annotations = None
        self.figure_layout_x_axis_dict = None
        self.figure_layout_y_axis_dict = None

    @property
    def values_total(self):
        figure_data_dict = self.figure_data[0]
        value_list = figure_data_dict['values']
        return sum(value_list)


class DccGraphSecondApi(DccGraphApi):
    def __init__(self, graph_id: str, title: str):
        DccGraphApi.__init__(self, graph_id, title)
        self.figure_layout_height = self.figure_layout_height # / 2
        self.figure_layout_width = self.figure_layout_width  # / 2


class MyHTMLTable:
    def __init__(self, rows: int, cols: int):
        self._rows = rows
        self._cols = cols
        self._row_range = range(1, self._rows + 1)
        self._col_range = range(1, self._cols + 1)
        self._list = [['' for col in self._col_range] for row in self._row_range]
        self._init_cells_()

    @property
    def padding_table(self):
        return 5

    @property
    def padding_cell(self):
        return 5

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
        return {'padding': self.padding_table, 'width': '100%'}


class MyHTML:
    @staticmethod
    def button():
        return html.Button

    @staticmethod
    def button_submit(element_id: str, children='Submit'):
        return html.Button(id=element_id, n_clicks=0, children=children, hidden='hidden',
                style={'fontSize': 24, 'margin-left': '30px'})

    @staticmethod
    def div_with_html_button_submit(element_id: str, children='Submit'):
        return html.Div(
            [MyHTML.button_submit(element_id, children)],
            style={'width': '10%', 'display': 'inline-block', 'vertical-align': 'bottom', 'padding-bottom': 20,
                   'padding-left': 10}
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
    def div_drop_down(children: str):
        style = {'font-weight': 'bold', 'display': 'inline-block', 'fontSize': 14,
                 'color': 'black', 'padding-bottom': 5}
        return html.Div(children=children, style=style)

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
    def div_with_dcc_drop_down(div_text: str, element_id: str, options: list, default='', width=20, for_multi=False):
        div_element_list = []
        if div_text != '':
            div_element_list.append(MyHTML.div_drop_down('{}:'.format(div_text)))
        div_element_list.append(MyDCC.drop_down(element_id, options, default, for_multi))
        style = {'display': 'inline-block', 'verticalAlign': 'top', 'width': width,
                 'padding-bottom': 10, 'padding-left': 10}
        return html.Div(div_element_list, style=style, id='{}_div'.format(element_id))


class MyDCC:
    @staticmethod
    def tabs(element_id: str, children: list):
        return dcc.Tabs(
            id=element_id,
            children=children,
            style={'fontFamily': 'system-ui', 'colors': {'primary': '#FF4136', 'secondary': 'red'}},
            content_style={
                'borderLeft': '1px solid #d6d6d6',
                'borderRight': '1px solid #d6d6d6',
                'borderBottom': '1px solid #d6d6d6',
                'padding': '10px'
            },
            parent_style={
                'maxWidth': '1250px',
                'margin': '0 auto'
            }
        )

    @staticmethod
    def tab(label: str, children: list):
        return dcc.Tab(
            label=label,
            children=children,
            style={'fontFamily': 'system-ui'}
        )

    @staticmethod
    def drop_down(element_id, options: list, default='', multi=False, clearable=False):
        # {'label': '{} {}'.format(symbol, name), 'value': symbol}
        default = options[0]['value'] if default == '' else default
        return dcc.Dropdown(id=element_id, options=options, value=default, multi=multi, clearable=clearable)

    @staticmethod
    def graph(graph_api: DccGraphApi):
        if graph_api.figure_layout_x_axis_dict:
            x_axis_dict = graph_api.figure_layout_x_axis_dict
        else:
            # x_axis_dict = {'title': 'ticker-x', 'type': 'date'}
            x_axis_dict = {}

        if graph_api.figure_layout_y_axis_dict:
            y_axis_dict = graph_api.figure_layout_y_axis_dict
        else:
            y_axis_dict = {'title': graph_api.figure_layout_yaxis_title}

        MyDCC.add_properties_to_x_y_axis_dict(x_axis_dict, y_axis_dict)
        # print('y_axis_dict={}'.format(y_axis_dict))

        return dcc.Graph(
            id=graph_api.id,
            figure={
                'data': graph_api.figure_data,
                'layout': {
                    'showlegend': True,
                    # 'spikedistance': 1,
                    'title': graph_api.figure_layout_yaxis_title,
                    'xaxis': x_axis_dict,
                    'autosize': graph_api.figure_layout_auto_size,
                    'yaxis': y_axis_dict,
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
    def add_properties_to_x_y_axis_dict(x_axis_dict: dict, y_axis_dict: dict):
        #  https://plot.ly/python/reference/#layout-xaxis-showspikes
        axis_dict_list = [x_axis_dict, y_axis_dict]
        for axis_dict in axis_dict_list:
            axis_dict['showspikes'] = True
            axis_dict['spikethickness'] = 1
            axis_dict['spikedash'] = 'dot'  # "solid", "dot", "dash", "longdash", "dashdot", or "longdashdot"
            axis_dict['spikemode'] = 'toaxis+across'  #  "toaxis", "across", "marker" joined with a "+"
            axis_dict['spikesnap'] = 'cursor'  # enumerated : "data" | "cursor"
            axis_dict['showline'] = True
            axis_dict['autorange'] = True
            axis_dict['showticklabels'] = True
            axis_dict['ticks'] = 'outside'
        y_axis_dict['automargin'] = True

    @staticmethod
    def interval(element_id: str, seconds=10):
        print('get_interval: id={}, seconds={}'.format(element_id, seconds))
        return dcc.Interval(id=element_id, interval=seconds * 1000, n_intervals=0)

    @staticmethod
    def data_table(element_id: str, rows: list, min_width=1200, min_height=1000):
        return dte.DataTable(
            id=element_id,
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            rows=rows,
            min_width=min_width,
            min_height=min_height
        )

    @staticmethod
    def get_rows_from_df_for_data_table(df: pd.DataFrame):
        df_dict = df.to_dict()
        rows = []
        columns = [column for column in df_dict]
        row_numbers = [number for number in df_dict[columns[0]]]
        for row_number in row_numbers:
            rows.append({column: df_dict[column][row_number] for column in columns})
        return rows

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