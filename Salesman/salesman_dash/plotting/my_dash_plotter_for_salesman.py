"""
Description: This module contains the plotter functions for statistics tabs.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-29
"""

import plotly.graph_objs as go
from sertl_analytics.constants.salesman_constants import SLDC
from sertl_analytics.my_numpy import MyNumpy
from sertl_analytics.mydash.my_dash_components import MyDCC, DccGraphApi
from salesman_dash.my_dash_colors import DashColorHandler
import pandas as pd
import itertools
import numpy as np
from sklearn.linear_model import LinearRegression


class MyDashTabPlotter:
    def __init__(self, df_base: pd.DataFrame, color_handler: DashColorHandler):
        self._df_base = df_base
        self._color_handler = color_handler
        self._chart_id = ''
        self._chart_name = ''
        self.category = ''
        self.x_variable = ''
        self.y_variable = ''
        self.text_variable = ''
        self.__init_parameter__()

    def __init_parameter__(self):
        pass

    def __print_df_base__(self):
        columns = self._df_base.columns[:2]
        df_reduced = self._df_base[columns]
        print('__print_df_base__: _df_wave\n{}'.format(df_reduced.head(100)))

    def get_chart_type_scatter(self, title: str):
        graph_api = DccGraphApi(self._chart_id, '{}: {}'.format(self._chart_name, title), use_title_for_y_axis=False)
        graph_api.figure_data = self.__get_scatter_figure_data__()
        graph_api.figure_layout_x_axis_dict = self.__get_figure_layout_x_axis_dict__()
        graph_api.figure_layout_y_axis_dict = self.__get_figure_layout_y_axis_dict__(graph_api)
        return [MyDCC.graph(graph_api)]

    def __get_df_for_selection__(self):
        return self._df_base

    def __get_scatter_figure_data__(self):
        pass

    def __get_figure_layout_y_axis_dict__(self, graph_api: DccGraphApi):
        if self.__can_axis_be_scaled_log_for_selected_variable__(self.y_variable):
            if graph_api.use_title_for_y_axis:
                return {'title': graph_api.title, 'type': 'file_log', 'autorange': True}
            else:
                return {'type': 'file_log', 'autorange': True}

    def __get_figure_layout_x_axis_dict__(self):
        if self.__can_axis_be_scaled_log_for_selected_variable__(self.x_variable):
            return {'type': 'file_log', 'autorange': True}

    def __can_axis_be_scaled_log_for_selected_variable__(self, variable_for_axis: str) -> bool:
        if variable_for_axis in ['']:
            return False
        df = self.__get_df_for_selection__()
        min_value = df[variable_for_axis].min()
        if type(min_value) is not str:  # to avoid problems with dates, etc.
            unique_value_list = df[variable_for_axis].unique()
            return min_value >= 0 and len(unique_value_list) > 2
        return False

    @staticmethod
    def _get_area_figure_layout_x_axis__():
        return dict(
            title='test',
            type='date',
            autotick=True,
            ticks='outside',
            tick0=0,
            dtick=0.25,
            ticklen=8,
            tickwidth=4,
            tickcolor='#000'
        )

