"""
Description: This module contains the plotter functions for assets statistics tabs.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import plotly.graph_objs as go
from sertl_analytics.constants.pattern_constants import DC, CHT, FT
from sertl_analytics.mydash.my_dash_components import MyDCC, DccGraphApi
from pattern_dash.my_dash_colors import DashColorHandler
from pattern_trade_handler import PatternTradeHandler
import pandas as pd
from pattern_dash.plotter_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter


class MyDashTabStatisticsPlotter4Assets(MyDashTabStatisticsPlotter):
    def __init__(self, df_base: pd.DataFrame, color_handler: DashColorHandler, trade_handler_online: PatternTradeHandler):
        MyDashTabStatisticsPlotter.__init__(self, df_base, color_handler)
        self._trade_handler_online = trade_handler_online
        # self.__print_df_base__()

    def __init_parameter__(self):
        self._chart_id = 'asset_statistics_graph'
        self._chart_name = 'Assets'
        self.chart_type = CHT.AREA_WINNER_LOSER
        self.category = DC.LOCATION
        self.x_variable = DC.LOCATION
        self.y_variable = DC.VALUE_TOTAL
        self.z_variable = DC.VALUE_TOTAL
        self.text_variable = DC.LOCATION
        self.pattern_type = FT.ALL

    def __print_df_base__(self):
        columns = [DC.VALIDITY_DT, DC.VALIDITY_TS, DC.EQUITY_NAME, DC.VALUE_TOTAL]
        df_reduced = self._df_base[columns]
        print('__print_df_base__: _df_wave\n{}'.format(df_reduced.head(100)))

    @staticmethod
    def __get_result_id_from_row__(row) -> int:
        return row[DC.VALUE_TOTAL]

    def __get_chart_type_pie__(self):
        graph_api = DccGraphApi(self._chart_id, self._chart_name)
        graph_api.figure_data = self.__get_pie_figure_data__('all')
        graph_api.figure_layout_height = 800
        graph_api.figure_layout_margin = {'b': 200, 'r': 50, 'l': 50, 't': 50}
        return [MyDCC.graph(graph_api)]

    def __get_line_figure_data__(self):
        df_base = self.__get_df_for_selection__()
        df = pd.DataFrame(df_base.groupby([self.x_variable, self.category])[DC.VALUE_TOTAL].sum())
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

    def __get_stack_group_figure_data__(self):
        df_base = self.__get_df_for_selection__()
        df = pd.DataFrame(df_base.groupby([self.x_variable, self.category])[DC.VALUE_TOTAL].sum())
        df.reset_index(inplace=True)
        color_dict = {cat: self._color_handler.get_color_for_category(cat) for cat in df[self.category].unique()}
        combined_list = list(df[self.category].unique())
        return [
            dict(
                x=df[df[self.category] == element][self.x_variable],
                y=df[df[self.category] == element][self.y_variable],
                text=['{}: {:0.2f}'.format(element, y) for y in df[df[self.category] == element][self.y_variable]],
                line={'color': color_dict[element], 'width': 2},
                fill='tonexty',
                opacity=0.7,
                name='{}'.format(element),
                stackgroup='one'
            ) for element in combined_list
        ]

    def __get_data_for_pie_figure__(self, scope: str):
        df = self.__get_df_for_selection__()
        ts_sorted_list = sorted(df[DC.VALIDITY_TS].unique())
        df = df[df[DC.VALIDITY_TS] == ts_sorted_list[-1]]
        sorted_category_list = sorted(df[self.category].unique())
        df = pd.DataFrame(df.groupby([self.category])[DC.VALUE_TOTAL].sum())
        y_values = [df.loc[cat][DC.VALUE_TOTAL] for cat in sorted_category_list]
        colors = [self._color_handler.get_color_for_category(cat) for cat in sorted_category_list]
        text = ['{}: {:0.2f}'.format(cat, y_values[index]) for index, cat in enumerate(sorted_category_list)]
        pull = [0 for cat in sorted_category_list]
        return sorted_category_list, y_values, colors, text, pull


