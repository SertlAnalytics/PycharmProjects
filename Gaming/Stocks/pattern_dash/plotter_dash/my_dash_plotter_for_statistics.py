"""
Description: This module contains the plotter functions for statistics tabs.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import plotly.graph_objs as go
from sertl_analytics.constants.pattern_constants import DC, CHT, FT, WAVEST, FD
from sertl_analytics.my_numpy import MyNumpy
from pattern_database.stock_database import StockDatabase
from sertl_analytics.mydash.my_dash_components import MyDCC, DccGraphApi
from pattern_dash.my_dash_colors import DashColorHandler
from pattern_logging.pattern_log import PatternLog
import pandas as pd
import itertools
import numpy as np
from sklearn.linear_model import LinearRegression


class MyDashTabStatisticsPlotter:
    def __init__(self, df_base: pd.DataFrame, color_handler: DashColorHandler):
        self._df_base = df_base
        self._color_handler = color_handler
        self._chart_id = ''
        self._chart_name = ''
        self.chart_type = ''
        self.category = ''
        self.predictor = ''
        self.x_variable = ''
        self.y_variable = ''
        self.z_variable = ''
        self.text_variable = ''
        self.model_type = ''
        self.pattern_type = ''
        self.__init_parameter__()

    def __init_parameter__(self):
        pass

    def __init_parameter_by_chart_type__(self, chart_type):
        pass

    @staticmethod
    def __get_df_secondary__():
        # ToDo - this should only be available at the deferred class...
        return StockDatabase().get_trade_records_for_statistics_as_dataframe()
        # return PatternLog().get_data_frame_for_trades()

    def __print_df_base__(self):
        columns = self._df_base.columns[:2]
        df_reduced = self._df_base[columns]
        print('__print_df_base__: _df_wave\n{}'.format(df_reduced.head(100)))

    def get_chart_list(self):
        return self.get_chart_list_by_chart_type(self.chart_type)

    def get_chart_list_by_chart_type(self, chart_type: str):
        self.__init_parameter_by_chart_type__(chart_type)
        if chart_type == CHT.SCATTER:
            return self.__get_chart_type_scatter__()
        elif chart_type == CHT.MY_TRADES:
            return self.__get_chart_type_my_trades__()
        elif chart_type == CHT.LINE:
            return self.__get_chart_type_line__()
        elif chart_type == CHT.STACK_GROUP:
            return self.__get_chart_type_stack_group__()
        elif chart_type == CHT.PREDICTOR:
            return self.__get_chart_type_predictor__()
        elif chart_type == CHT.HEAT_MAP:
            return self.__get_chart_type_heatmap__()
        elif chart_type == CHT.MOOD_CHART:
            return self.__get_chart_type_mood__()
        elif chart_type == CHT.PIE:
            return self.__get_chart_type_pie__()
        elif chart_type == CHT.AREA_WINNER_LOSER:
            return self.__get_chart_type_area_winner_loser__()
        elif chart_type == CHT.CONFUSION:
            return self.__get_chart_type_confusion_matrix__()
        elif chart_type == CHT.CONFUSION_REGRESSION:
            return self.__get_chart_type_confusion_regression__()
        elif chart_type == CHT.ROC:
            return self.__get_chart_type_roc__()

    def __get_chart_type_area_winner_loser__(self):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'winner & loser'))
        graph_api.figure_data = self.__get_area_winner_loser_figure_data__()
        graph_api.figure_layout_x_axis_dict = None  # dict(type='date',)
        graph_api.figure_layout_y_axis_dict = None  # dict(type='linear', range=[1, 100], dtick=20, ticksuffix='%')
        # graph_api.figure_layout_y_axis_dict = {'type': 'log', 'autorange': True}
        return [MyDCC.graph(graph_api)]

    def __get_chart_type_heatmap__(self):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'Heatmap'))
        graph_api.figure_data = self.__get_heatmap_figure_data__('Test')
        graph_api.figure_layout_x_axis_dict = None  # dict(type='date',)
        graph_api.figure_layout_y_axis_dict = None  # dict(type='linear', range=[1, 100], dtick=20, ticksuffix='%')
        return [MyDCC.graph(graph_api)]

    def __get_chart_type_mood__(self):
        pass

    def __get_chart_type_pie__(self):
        graph_api_all = DccGraphApi(self._chart_id + '_all', self._chart_name + ' (all)')
        graph_api_all.figure_data = self.__get_pie_figure_data__('all')
        graph_api_winner = DccGraphApi(self._chart_id + '_winner', self._chart_name + ' (winner)')
        graph_api_winner.figure_data = self.__get_pie_figure_data__('winner')
        graph_api_loser = DccGraphApi(self._chart_id + '_loser', self._chart_name + ' (loser)')
        graph_api_loser.figure_data = self.__get_pie_figure_data__('loser')
        w_h, l_h = self.__get_winner_loser_heights__(graph_api_winner.values_total, graph_api_loser.values_total)
        graph_api_all.figure_layout_height = 800
        graph_api_winner.figure_layout_height = 800
        graph_api_loser.figure_layout_height = 800
        graph_api_loser.figure_layout_height *= w_h
        graph_api_loser.figure_layout_height *= l_h
        graph_api_all.figure_layout_margin = {'b': 200, 'r': 50, 'l': 50, 't': 50}
        graph_api_winner.figure_layout_margin = {'b': 200, 'r': 50, 'l': 50, 't': 50}
        graph_api_loser.figure_layout_margin = {'b': 200, 'r': 50, 'l': 50, 't': 50}
        return [MyDCC.graph(graph_api_all), MyDCC.graph(graph_api_winner), MyDCC.graph(graph_api_loser)]

    def __get_chart_type_predictor__(self):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'master_predictor'))
        graph_api.figure_data = self.__get_scatter_figure_data_for_predictor__()
        return [MyDCC.graph(graph_api)]

    def __get_chart_type_stack_group__(self):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'Assets'))
        graph_api.figure_data = self.__get_stack_group_figure_data__()
        # print(graph_api.figure_data)
        graph_api.figure_layout_x_axis_dict = self.__get_figure_layout_x_axis_dict__()
        graph_api.figure_layout_y_axis_dict = self.__get_figure_layout_y_axis_dict__(graph_api)
        return [MyDCC.graph(graph_api)]

    def __get_chart_type_my_trades__(self):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'MyTrades'))
        graph_api.figure_data = self.__get_scatter_figure_data__()
        graph_api.figure_layout_x_axis_dict = self.__get_figure_layout_x_axis_dict__()
        graph_api.figure_layout_y_axis_dict = self.__get_figure_layout_y_axis_dict__(graph_api)
        return [MyDCC.graph(graph_api)]

    def __get_chart_type_line__(self):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'Assets'))
        graph_api.figure_data = self.__get_line_figure_data__()
        graph_api.figure_layout_x_axis_dict = self.__get_figure_layout_x_axis_dict__()
        graph_api.figure_layout_y_axis_dict = self.__get_figure_layout_y_axis_dict__(graph_api)
        return [MyDCC.graph(graph_api)]

    def __get_chart_type_confusion_matrix__(self):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self.predictor, self.x_variable))
        graph_api.figure_data = self.__get_confusion_matrix_figure_data__()
        graph_api.figure_layout_x_axis_dict = self.__get_figure_layout_x_axis_dict__()
        # graph_api.figure_layout_y_axis_dict = self.__get_figure_layout_y_axis_dict__(graph_api)
        return [MyDCC.graph(graph_api)]

    def __get_chart_type_confusion_regression__(self):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self.predictor, self.x_variable))
        graph_api.figure_data = self.__get_confusion_regression_figure_data__()
        graph_api.figure_layout_x_axis_dict = self.__get_figure_layout_x_axis_dict__()
        # graph_api.figure_layout_y_axis_dict = self.__get_figure_layout_y_axis_dict__(graph_api)
        return [MyDCC.graph(graph_api)]

    def __get_chart_type_roc__(self):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'Models'))
        graph_api.figure_data = self.__get_roc_figure_data__()
        graph_api.figure_layout_x_axis_dict = self.__get_figure_layout_x_axis_dict__()
        graph_api.figure_layout_y_axis_dict = self.__get_figure_layout_y_axis_dict__(graph_api)
        return [MyDCC.graph(graph_api)]

    def __get_chart_type_scatter__(self):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'winner & loser'))
        graph_api.figure_data = self.__get_scatter_figure_data__()
        graph_api.figure_layout_x_axis_dict = self.__get_figure_layout_x_axis_dict__()
        graph_api.figure_layout_y_axis_dict = self.__get_figure_layout_y_axis_dict__(graph_api)
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
        if self.chart_type == CHT.MY_TRADES or self.category == "Trade":  # ToDo: get rid of this string - use constant
            df_base = self.__get_df_secondary__()
        else:
            df_base = self._df_base
        if self.pattern_type in [FT.ALL, '']:
            df = df_base
        else:
            df = df_base[df_base[DC.PATTERN_TYPE] == self.pattern_type]
        return df

    def __get_scatter_figure_data__(self):
        df = self.__get_df_for_selection__()
        color_dict = {cat: self._color_handler.get_color_for_category(cat) for cat in df[self.category].unique()}
        if DC.TRADE_RESULT_ID in df.columns:
            combined_list = list(itertools.product(df[self.category].unique(), df[DC.TRADE_RESULT_ID].unique()))
            col = DC.TRADE_RESULT_ID
        else:
            combined_list = list(itertools.product(df[self.category].unique(), df[DC.EXPECTED_WIN_REACHED].unique()))
            col = DC.EXPECTED_WIN_REACHED
        return [
            go.Scatter(
                x=df[np.logical_and(df[self.category] == element[0], df[col] == element[1])][self.x_variable],
                y=df[np.logical_and(df[self.category] == element[0], df[col] == element[1])][self.y_variable],
                text=df[np.logical_and(df[self.category] == element[0], df[col] == element[1])][self.text_variable],
                mode='markers',
                opacity=0.7,
                marker={'symbol': 'diamond' if int(element[1]) == 1 else 'circle',
                        'size': 15,
                        'color': color_dict[element[0]],
                        'line': {'width': 0.5, 'color': 'white' if int(element[1]) == 1 else 'red'}},
                name=element[0]
            ) for element in combined_list
        ]

    def __get_regression_traces_for_categories__(self, df: pd.DataFrame, category_list: list, color_dict: dict):
        trace_list = []
        x_orig = df[self.x_variable]
        x_orig_predict = MyNumpy.get_date_values_as_number_for_date_time_array(list(x_orig))
        if len(category_list) > 1:  # we add a regression line for ALL
            trace_list.append(self.__get_regression_trace_for_data_frame__(df, x_orig, x_orig_predict, 'ALL', 'red'))
        for cat in category_list:
            df_cat = df[df[self.category] == cat]
            if df_cat.shape[0] > 0:
                trace = self.__get_regression_trace_for_data_frame__(df_cat, x_orig, x_orig_predict, cat, color_dict[cat])
                trace_list.append(trace)
        return trace_list

    def __get_regression_trace_for_data_frame__(
            self, df: pd.DataFrame, x_orig: pd.Series, x_orig_predict, cat: str, color: str):
        lin_reg = LinearRegression()
        x_train = df[self.x_variable]
        x_train_reshaped = MyNumpy.get_date_values_as_number_for_date_time_array(list(x_train))
        y_train = df[self.y_variable]
        y_train_reshaped = y_train.values.reshape(-1, 1)
        lin_reg.fit(x_train_reshaped, y_train_reshaped)
        # print('cat: {}, coeff: {}'.format(cat, lin_reg.coef_))
        y_predict = lin_reg.predict(x_orig_predict)
        y_predict_values = np.array([y_value[0] for y_value in y_predict])

        return go.Scatter(
            x=x_orig.values,
            y=y_predict_values,
            mode='lines',
            opacity=0.7,
            line=dict(color=color, width=3),
            name=cat
        )

    def __get_line_figure_data__(self):
        pass

    def __get_stack_group_figure_data__(self):
        pass

    def __get_confusion_matrix_figure_data__(self):
        pass

    def __get_confusion_regression_figure_data__(self):
        pass

    def __get_roc_figure_data__(self):
        return ''

    def __get_scatter_figure_data_for_predictor__(self):
        self.category = DC.PATTERN_TYPE
        return self.__get_scatter_figure_data__()

    def __get_pie_figure_data__(self, scope: str):
        labels, values, colors, text, pull = self.__get_data_for_pie_figure__(scope)
        return [
            go.Pie(labels=labels,
                   values=values,
                   text=text,
                   marker=dict(colors=colors),
                   pull=pull
                   )]

    def __get_heatmap_figure_data__(self, index: str):
        [x_data, y_data, z_data] = self.__get_data_for_heatmap_figure__(index)
        return [
            go.Heatmap(
                x=x_data,
                y=y_data,
                z=z_data,
                colorscale=self._color_handler.get_color_scale_for_heatmap()
                )]

    def __get_mood_chart_figure_data__(self, index: str):
        [x_data, y_data] = self.__get_data_for_heatmap_figure__(index, for_mood_graph=True)  # we use the same data
        # print('x_data={}, \ny_data={}'.format(x_data, y_data))
        all_ascending = np.array(y_data[FD.ASC])
        all_descending = -1 * np.array(y_data[FD.DESC])
        daily_ascending = np.array(y_data[WAVEST.DAILY_ASC])
        daily_descending = -1 * np.array(y_data[WAVEST.DAILY_DESC])
        max_value = max(max(y_data[FD.ASC]), max(y_data[FD.DESC]))
        opacity = 0.4
        # print('x_data={}, \ny_data={}'.format(x_data, y_data))
        return [
            go.Bar(x=x_data,
                   y=all_ascending,
                   orientation='v',
                   name='All ascending',
                   # hoverinfo='x',
                   marker=dict(color='green'),
                   opacity=opacity,
                   ),
            go.Bar(x=x_data,
                   y=all_descending,
                   orientation='v',
                   name='All descending',
                   text=-1 * all_descending.astype('int'),
                   # hoverinfo='text',
                   marker=dict(color='red'),
                   opacity=opacity,
                   ),
            go.Bar(x=x_data,
                   y=daily_ascending,
                   orientation='v',
                   name='daily ascending',
                   # text='{}: {}'.format('daily ascending', daily_ascending.astype('int')),
                   # text=daily_ascending.astype('int'),
                   # hoverinfo='x',
                   showlegend=True,
                   marker=dict(color='green')
                   ),
            go.Bar(x=x_data,
                   y=daily_descending,
                   orientation='v',
                   name='daily descending',
                   text=-1 * daily_descending.astype('int'),
                   # hoverinfo='text',
                   showlegend=True,
                   marker=dict(color='red')
                   )
        ], max_value

    def __get_data_for_heatmap_figure__(self, scope: str, for_mood_graph=False):
        x_data = []
        y_data = []
        z_data = []
        return [x_data, y_data, z_data]

    def __get_data_for_pie_figure__(self, scope: str):
        pull_distance = 0.1
        df = self.__get_df_for_selection__()
        sorted_categories_orig = sorted(df[self.category].unique())
        sorted_category_list_winner = ['{}_{}'.format(cat, 'winner') for cat in sorted_categories_orig]
        sorted_category_list_loser = ['{}_{}'.format(cat, 'loser') for cat in sorted_categories_orig]
        if scope == 'winner':
            sorted_category_list = sorted_category_list_winner
        elif scope == 'loser':
            sorted_category_list = sorted_category_list_loser
        else:
            sorted_category_list = sorted_category_list_winner + sorted_category_list_loser
        y_value_dict = {cat: 0 for cat in sorted_category_list}
        for index, row in df.iterrows():
            cat = row[self.category]
            result_id = self.__get_result_id_from_row__(row)
            cat_result = '{}_{}'.format(cat, 'winner' if result_id == 1 else 'loser')
            if cat_result in y_value_dict:
                y_value_dict[cat_result] += 1
        y_values = [y_value_dict[cat_result] for cat_result in sorted_category_list]
        colors = [self._color_handler.get_color_for_category(cat) for cat in sorted_category_list]
        text = [cat for cat in sorted_category_list]
        pull = []
        for cat in sorted_category_list:
            pull.append(pull_distance if cat.find('_winner') > 0 and scope == 'all' else 0)
        # print('colors={}, pull={}'.format(colors, pull))
        return sorted_category_list, y_values, colors, text, pull

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

    def __get_figure_layout_y_axis_dict__(self, graph_api: DccGraphApi):
        if self.__can_axis_be_scaled_log_for_selected_variable__(self.y_variable):
            return {'title': graph_api.figure_layout_yaxis_title, 'type': 'log', 'autorange': True}

    def __get_figure_layout_x_axis_dict__(self):
        if self.__can_axis_be_scaled_log_for_selected_variable__(self.x_variable) and False:
            return {'type': 'log', 'autorange': True}

    def __can_axis_be_scaled_log_for_selected_variable__(self, variable_for_axis: str) -> bool:
        if variable_for_axis in ['', DC.VALUE_TOTAL, DC.TOUCH_POINTS_TILL_BREAKOUT_TOP,
                                 DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM]:
            return False
        df = self.__get_df_for_selection__()
        min_value = df[variable_for_axis].min()
        if type(min_value) is not str:  # to avoid problems with dates, etc.
            unique_value_list = df[variable_for_axis].unique()
            return min_value >= 0 and len(unique_value_list) > 2
        return False

    @staticmethod
    def __get_area_figure_data_test__():
        x = ['Winter', 'Spring', 'Summer', 'Fall']
        trace0 = dict(
            x=x,
            y=['40', '20', '30', '40'],
            mode='lines',
            line=dict(width=0.5, color='rgb(184, 247, 212)'),
            stackgroup='one',
            # groupnorm='percent'
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

