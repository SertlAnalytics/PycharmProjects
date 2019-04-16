"""
Description: This module contains the plotter functions for trades statistics tabs.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import plotly.graph_objs as go
from pattern_logging.pattern_log import PatternLog
from sertl_analytics.constants.pattern_constants import DC, CHT, FT
import pandas as pd
from pattern_dash.plotter_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter


class MyDashTabStatisticsPlotter4Trades(MyDashTabStatisticsPlotter):
    def __init_parameter__(self):
        self._chart_id = 'trade_statistics_graph'
        self._chart_name = 'Trades'
        self.chart_type = CHT.MY_TRADES
        self.category = DC.PATTERN_TYPE
        self.x_variable = DC.PATTERN_RANGE_BEGIN_DT
        self.y_variable = DC.TRADE_RESULT_PCT
        self.z_variable = DC.EXPECTED_WIN
        self.text_variable = DC.TRADE_STRATEGY
        self.pattern_type = FT.ALL

    @staticmethod
    def __get_df_secondary__():
        return PatternLog().get_data_frame_for_trades()

    @staticmethod
    def __get_result_id_from_row__(row) -> int:
        return row[DC.TRADE_RESULT_ID]

    def __get_scatter_figure_data__(self):
        df = self.__get_df_for_selection__()
        color_dict = {cat: self._color_handler.get_color_for_category(cat) for cat in df[self.category].unique()}
        category_list = list(df[self.category].unique())
        regression_traces = self.__get_regression_traces_for_categories__(df, category_list, color_dict)
        scatter_traces = self.__get_scatter_traces_for_categories__(df, category_list, color_dict)
        return regression_traces + scatter_traces

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

    def __get_line_figure_data__(self):
        df_base = self.__get_df_for_selection__()
        df = pd.DataFrame(df_base.groupby([self.x_variable, self.category])[DC.TRADE_RESULT_PCT].sum())
        df.reset_index(inplace=True)
        color_dict = {cat: self._color_handler.get_color_for_category(cat) for cat in df[self.category].unique()}
        combined_list = list(df[self.category].unique())
        return [
            go.Scatter(
                x=df[df[self.category] == element][self.x_variable],
                y=df[df[self.category] == element][self.y_variable],
                text=['{}: {:0.2f}'.format(element, y) for y in df[df[self.category] == element][self.y_variable]],
                line={'color': color_dict[element], 'width': 2},
                opacity=0.7,
                name=element
            ) for element in combined_list
        ]


