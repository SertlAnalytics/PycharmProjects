"""
Description: This module contains the plotter functions for trades statistics tabs.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-29
"""

import plotly.graph_objs as go
from salesman_logging.salesman_log import SalesmanLog
from sertl_analytics.constants.salesman_constants import SLDC
import pandas as pd
from salesman_dash.plotting.my_dash_plotter_for_salesman import MyDashTabPlotter


class MyDashTabPlotter4Search(MyDashTabPlotter):
    def __init_parameter__(self):
        self._chart_id = 'search_result_graph'
        self._chart_name = 'Results'
        self.category = SLDC.PLOT_CATEGORY
        self.x_variable = SLDC.PRICE_SINGLE
        self.y_variable = SLDC.PLOT_CATEGORY
        self.text_variable = SLDC.TITLE
        self.category_list = []

    def __get_scatter_figure_data__(self):
        df = self.__get_df_for_selection__()
        color_dict = {cat: self._color_handler.get_color_for_category(cat) for cat in df[self.category].unique()}
        self.category_list = list(df[self.category].unique())
        scatter_traces = self.__get_scatter_traces_for_categories__(df, self.category_list, color_dict)
        box_plot_traces = self.__get_box_plot_traces_for_categories__(df, self.category_list, color_dict)
        return scatter_traces + box_plot_traces

    def __get_scatter_traces_for_categories__(self, df: pd.DataFrame, category_list: list, color_dict: dict):
        return [
            go.Scatter(
                x=df[df[self.category] == category][self.x_variable],
                y=df[df[self.category] == category][self.y_variable],
                text=df[df[self.category] == category][self.text_variable],
                mode='markers',
                opacity=0.7,
                marker={'symbol': 'diamond',
                        'size': 15,
                        'color': color_dict[category],
                        'line': {'width': 0.5, 'color': 'white'}},
                name=category
            ) for category in category_list
        ]

    def __get_box_plot_traces_for_categories__(self, df: pd.DataFrame, category_list: list, color_dict: dict):
        trace_list = []
        for cat in category_list:
            df_cat = df[df[self.category] == cat]
            if df_cat.shape[0] > 0:
                color = color_dict[cat]
                x_cat = df_cat[self.x_variable]
                trace = go.Box(x=x_cat.values, opacity=0.7, line=dict(color=color, width=1), name=cat)
                trace_list.append(trace)
        return trace_list
