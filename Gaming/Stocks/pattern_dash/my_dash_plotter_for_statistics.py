"""
Description: This module contains the plotter functions for statistics tabs.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import plotly.graph_objs as go
from sertl_analytics.constants.pattern_constants import DC, CHT, FT, PRED
from pattern_dash.my_dash_components import MyDCC, DccGraphApi
from pattern_dash.my_dash_colors import DashColorHandler
import pandas as pd


class MyDashTabStatisticsPlotter:
    def __init__(self, df_base: pd.DataFrame, color_handler: DashColorHandler):
        self._df_base = df_base
        self._color_handler = color_handler
        self._chart_id = ''
        self._chart_name = ''
        self.chart_type = ''
        self.category = ''
        self.x_variable = ''
        self.y_variable = ''
        self.z_variable = ''
        self.text_variable = ''
        self.pattern_type = ''
        self.__init_parameter__()

    def __init_parameter__(self):
        pass

    def get_chart_list(self):
        if self.chart_type == CHT.SCATTER:
            graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'winner & loser'))
            graph_api.figure_data = self.__get_scatter_figure_data__()
            return [MyDCC.graph(graph_api)]
        elif self.chart_type == CHT.PREDICTOR:
            graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'predictor'))
            graph_api.figure_data = self.__get_scatter_figure_data_for_predictor__()
            return [MyDCC.graph(graph_api)]
        elif self.chart_type == CHT.PIE:
            graph_api = DccGraphApi(self._chart_id + '_winner', self._chart_name + ' (winner)')
            graph_api.figure_data = self.__get_pie_figure_data__(True)
            graph_api_loser = DccGraphApi(self._chart_id + '_loser', self._chart_name + ' (loser)')
            graph_api_loser.figure_data = self.__get_pie_figure_data__(False)
            w_h, l_h = self.__get_winner_loser_heights__(graph_api.values_total, graph_api_loser.values_total)
            graph_api_loser.figure_layout_height *= w_h
            graph_api_loser.figure_layout_height *= l_h
            graph_api.figure_layout_height = 800
            graph_api_loser.figure_layout_height = 800
            graph_api.figure_layout_margin = {'b': 300, 'r': 50, 'l': 50, 't': 50}
            graph_api_loser.figure_layout_margin = {'b': 300, 'r': 50, 'l': 50, 't': 50}
            return [MyDCC.graph(graph_api), MyDCC.graph(graph_api_loser)]
        elif self.chart_type == CHT.AREA_WINNER_LOSER:
            graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'winner & loser'))
            graph_api.figure_data = self.__get_area_winner_loser_figure_data__()
            graph_api.figure_layout_x_axis_dict = None  # dict(type='date',)
            graph_api.figure_layout_y_axis_dict = None  # dict(type='linear', range=[1, 100], dtick=20, ticksuffix='%')
            return [MyDCC.graph(graph_api)]

    @staticmethod
    def __get_winner_loser_heights__(total_winner: int, total_loser: int):
        if total_winner >= total_loser:
            if total_winner >= 4 * total_loser:
                return 1, 0.75
            elif total_winner >= 2 * total_loser:
                return 1, 0.9
            return 1, 0.97
        else:
            if total_loser >= 4 * total_winner:
                return 0.75, 1
            elif total_loser >= 2 * total_winner:
                return 0.9, 1
            return 0.97, 1

    def __get_df_for_selection__(self):
        if self.pattern_type in [FT.ALL, '']:
            df = self._df_base
        else:
            df = self._df_base[self._df_base[DC.PATTERN_TYPE] == self.pattern_type]
        return df

    def __get_scatter_figure_data__(self):
        df = self.__get_df_for_selection__()
        return [
            go.Scatter(
                x=df[df[self.category] == category][self.x_variable],
                y=df[df[self.category] == category][self.y_variable],
                text=df[df[self.category] == category][self.text_variable],
                mode='markers',
                opacity=0.7,
                marker={'size': 15, 'line': {'width': 0.5, 'color': 'white'}},
                name=category
            ) for category in df[self.category].unique()
        ]

    def __get_scatter_figure_data_for_predictor__(self):
        df = self.__get_df_for_selection__()
        return [
            go.Scatter(
                x=df[df[DC.PATTERN_TYPE] == pattern_type][self.x_variable],
                y=df[df[DC.PATTERN_TYPE] == pattern_type][self.y_variable],
                text=df[df[DC.PATTERN_TYPE] == pattern_type][self.text_variable],
                mode='markers',
                opacity=0.7,
                marker={'size': 15, 'line': {'width': 0.5, 'color': 'white'}},
                name=pattern_type
            ) for pattern_type in df[DC.PATTERN_TYPE].unique()
        ]

    def __get_pie_figure_data__(self, for_winner: bool):
        labels, values, colors, text = self.__get_data_for_pie_figure__(for_winner)
        return [
            go.Pie(labels=labels,
                   values=values,
                   text=text,
                   marker=dict(colors=colors)
                   )]

    def __get_data_for_pie_figure__(self, for_winner: bool):
        df = self.__get_df_for_selection__()
        sorted_categories_orig = sorted(df[self.category].unique())
        if for_winner:
            sorted_category_list = ['{}_{}'.format(cat, 'winner') for cat in sorted_categories_orig]
        else:
            sorted_category_list = ['{}_{}'.format(cat, 'loser') for cat in sorted_categories_orig]
        y_value_dict = {cat: 0 for cat in sorted_category_list}
        for index, row in df.iterrows():
            cat = row[self.category]
            result_id = self.__get_result_id_from_row__(row)
            cat_result = '{}_{}'.format(cat, 'winner' if result_id == 1 else 'loser')
            if cat_result in y_value_dict:
                y_value_dict[cat_result] += 1
        y_values = [y_value_dict[cat_result] for cat_result in sorted_category_list]
        colors = [self._color_handler.get_color_for_category(cat) for cat in sorted_category_list]
        text = [cat for cat in sorted_categories_orig]
        return sorted_category_list, y_values, colors, text

    def __get_area_winner_loser_figure_data__(self):
        x_values, y_value_dict = self.__get_data_for_area_winner_loser_figure__()
        # print(x_values)
        # print(y_value_dict)
        return [
            dict(
                x=x_values,
                y=values,
                text=category,
                mode='lines',
                fill='tonexty',
                opacity=0.7,
                line=dict(width=0.5, color=self._color_handler.get_color_for_category(category)),
                stackgroup='one',
                name=category
            ) for category, values in y_value_dict.items()
        ]

    def __get_data_for_area_winner_loser_figure__(self):
        df = self.__get_df_for_selection__()
        x_value_dict = {}
        sorted_x_values = sorted(df[self.x_variable].unique())
        sorted_categories_orig = sorted(df[self.category].unique())
        sorted_category_list = ['{}_{}'.format(cat, 'winner') for cat in sorted_categories_orig]
        for cat in sorted_categories_orig:
            sorted_category_list.append('{}_{}'.format(cat, 'loser'))
        for index, row in df.iterrows():
            cat = row[self.category]
            result_id = self.__get_result_id_from_row__(row)
            cat_result = '{}_{}'.format(cat, 'winner' if result_id == 1 else 'loser')
            x_value = row[self.x_variable]
            if x_value not in x_value_dict:
                x_value_dict[x_value] = []
            x_value_dict[x_value].append([cat_result, result_id])

        cat_count_dict = {cat: [] for cat in sorted_category_list}
        for x_value in sorted_x_values:
            for cat in sorted_category_list:
                if len(cat_count_dict[cat]) == 0:
                    old_value = 0
                else:
                    old_value = cat_count_dict[cat][-1]
                cat_count_dict[cat].append(old_value)
            if x_value in x_value_dict:
                for cat_results in x_value_dict[x_value]:
                    category = cat_results[0]
                    result_id = cat_results[1]
                    old_value = cat_count_dict[category][-1]
                    cat_count_dict[category][-1] = old_value + result_id
        # print(sorted_382144: {}'.format(cat, cat_count_dict[cat]))
        return sorted_x_values, cat_count_dict

    @staticmethod
    def __get_result_id_from_row__(row) -> int:
        pass

    @staticmethod
    def __get_area_figure_data_test__():
        x = ['Winter', 'Spring', 'Summer', 'Fall']
        trace0 = dict(
            x=x,
            y=['40', '20', '30', '40'],
            mode='lines',
            line=dict(width=0.5, color='rgb(184, 247, 212)'),
            stackgroup='one',
            groupnorm='percent'
        )
        trace1 = dict(
            x=x,
            y=['50', '70', '40', '60'],
            mode='lines',
            line=dict(width=0.5, color='rgb(111, 231, 219)'),
            stackgroup='one'
        )
        trace2 = dict(
            x=x,
            y=['70', '80', '60', '70'],
            mode='lines',
            line=dict(width=0.5, color='rgb(127, 166, 238)'),
            stackgroup='one'
        )
        trace3 = dict(
            x=x,
            y=['100', '100', '100', '100'],
            mode='lines',
            line=dict(width=0.5, color='rgb(131, 90, 241)'),
            stackgroup='one'
        )
        return [trace0, trace1, trace2, trace3]

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

    @staticmethod
    def __get_scatter_figure_data_old__(df: pd.DataFrame):
        return [
            go.Scatter(
                x=df[df['Pattern_Type'] == i]['Forecast_Full_Positive_PCT'],
                y=df[df['Pattern_Type'] == i]['Trade_Result_ID'],
                text=df[df['Pattern_Type'] == i]['Trade_Strategy'],
                mode='markers',
                opacity=0.7,
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name=i
            ) for i in df.Pattern_Type.unique()
        ]


class MyDashTabStatisticsPlotter4Trades(MyDashTabStatisticsPlotter):
    def __init_parameter__(self):
        self._chart_id = 'trade_statistics_graph'
        self._chart_name = 'Trades'
        self.chart_type = CHT.AREA_WINNER_LOSER
        self.category = DC.PATTERN_TYPE
        self.x_variable = DC.FC_FULL_POSITIVE_PCT
        self.y_variable = DC.TRADE_RESULT_ID
        self.z_variable = DC.EXPECTED_WIN
        self.text_variable = DC.TRADE_STRATEGY
        self.pattern_type = FT.ALL

    @staticmethod
    def __get_result_id_from_row__(row) -> int:
        return row[DC.TRADE_RESULT_ID]


class MyDashTabStatisticsPlotter4Pattern(MyDashTabStatisticsPlotter):
    def __init_parameter__(self):
        self._chart_id = 'pattern_statistics_graph'
        self._chart_name = 'Pattern'
        self.chart_type = CHT.SCATTER
        self.predictor = PRED.TOUCH_POINT
        self.category = DC.PATTERN_TYPE
        self.x_variable = DC.PREVIOUS_PERIOD_FULL_TOP_OUT_PCT
        self.y_variable = DC.EXPECTED_WIN_REACHED
        self.z_variable = DC.EXPECTED_WIN_REACHED
        self.text_variable = DC.EXPECTED_WIN_REACHED
        self.pattern_type = FT.ALL

    @staticmethod
    def __get_result_id_from_row__(row) -> int:
        return 1 if row[DC.EXPECTED_WIN_REACHED] == 1 else -1
