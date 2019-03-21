"""
Description: This module contains the plotter functions for statistics tabs.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import plotly.graph_objs as go
from sertl_analytics.constants.pattern_constants import DC, CHT, FT, PRED, MT, STBL, MTC, MDC, WAVEST, PRD, FD
from sertl_analytics.constants.pattern_constants import EQUITY_TYPE, INDICES
from sertl_analytics.mydates import MyDate
from pattern_dash.my_dash_components import MyDCC, DccGraphApi
from pattern_dash.my_dash_colors import DashColorHandler
from pattern_trade_handler import PatternTradeHandler
from pattern_database.stock_database import StockDatabase
from pattern_database.stock_tables import PatternTable, TradeTable
from pattern_predictor_optimizer import PatternPredictorOptimizer
from fibonacci.fibonacci_wave_data import FibonacciWaveDataHandler
import pandas as pd
import itertools
import numpy as np


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
        elif chart_type == CHT.ROC:
            return self.__get_chart_type_roc__()

    def __get_chart_type_area_winner_loser__(self):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'winner & loser'))
        graph_api.figure_data = self.__get_area_winner_loser_figure_data__()
        graph_api.figure_layout_x_axis_dict = None  # dict(type='date',)
        graph_api.figure_layout_y_axis_dict = None  # dict(type='linear', range=[1, 100], dtick=20, ticksuffix='%')
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
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'predictor'))
        graph_api.figure_data = self.__get_scatter_figure_data_for_predictor__()
        return [MyDCC.graph(graph_api)]

    def __get_chart_type_stack_group__(self):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self._chart_name, 'Assets'))
        graph_api.figure_data = self.__get_stack_group_figure_data__()
        # print(graph_api.figure_data)
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
        if self.pattern_type in [FT.ALL, '']:
            df = self._df_base
        else:
            df = self._df_base[self._df_base[DC.PATTERN_TYPE] == self.pattern_type]
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

    def __get_line_figure_data__(self):
        pass

    def __get_stack_group_figure_data__(self):
        pass

    def __get_confusion_matrix_figure_data__(self):
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
        if self.__can_axis_be_scaled_log_for_selected_variable__(self.x_variable):
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


class MyDashTabStatisticsPlotter4Models(MyDashTabStatisticsPlotter):
    def __init__(self, df_base: pd.DataFrame, color_handler: DashColorHandler,
                 db_stock: StockDatabase, predictor_optimizer: PatternPredictorOptimizer):
        self.db_stock = db_stock
        self.pattern_table = PatternTable()
        self.trade_table = TradeTable()
        self._predictor_optimizer = predictor_optimizer
        MyDashTabStatisticsPlotter.__init__(self, df_base, color_handler)
        self._df_base_cache_dict = {}
        # print('MyDashTabStatisticsPlotter4Models.__init__()')

    def __init_parameter__(self):
        self._chart_id = 'models_statistics_graph'
        self._chart_name = 'Models'
        self.chart_type = CHT.CONFUSION
        self.category = STBL.PATTERN
        self.predictor = PRED.TOUCH_POINT
        self.x_variable = DC.TOUCH_POINTS_TILL_BREAKOUT_TOP
        self.y_variable = [MTC.PRECISION]
        self.model_type = [MT.K_NEAREST_NEIGHBORS]
        self.text_variable = DC.TRADE_STRATEGY
        self.pattern_type = FT.ALL

    @staticmethod
    def __get_result_id_from_row__(row) -> int:
        return row[DC.TRADE_RESULT_ID]

    def __get_confusion_matrix_figure_data__(self):
        model_type_list = self.model_type
        combined_list = list(itertools.product(model_type_list, self.y_variable))
        x_dict, y_dict = self.__get_x_dict_and_y_dict__(model_type_list, self.y_variable)
        color_dict = {cat: self._color_handler.get_color_for_category(cat) for cat in model_type_list}
        return [
            go.Scatter(
                x=x_dict[model_type],
                y=y_dict['{}-{}'.format(model_type, metric)],
                text=['{}-{}: {:0.2f}'.format(model_type, metric, y_value)
                      for y_value in y_dict['{}-{}'.format(model_type, metric)]],
                line={'color': color_dict[model_type], 'width': 2},
                opacity=0.7,
                name='{}-{}'.format(model_type, metric)
            ) for model_type, metric in combined_list
        ]

    def __get_x_dict_and_y_dict__(self, model_type_list: list, metric_list: list):
        # both together since we need the same order....
        x_dict = {}
        y_dict = {}
        for model_type in model_type_list:
            df_metric = self._predictor_optimizer.get_metrics_for_model_and_label_as_data_frame(
                model_type, self.category, self.predictor, self.x_variable, self.pattern_type)
            x_dict[model_type] = list(df_metric[MDC.VALUE])
            for metric in metric_list:
                key = '{}-{}'.format(model_type, metric)
                if metric == MTC.PRECISION:
                    y_dict[key] = list(df_metric[MDC.PRECISION])
                elif metric == MTC.RECALL:
                    y_dict[key] = list(df_metric[MDC.RECALL])
                elif metric == MTC.F1_SCORE:
                    y_dict[key] = list(df_metric[MDC.F1_SCORE])
                elif metric == MTC.ROC_AUC:
                    y_dict[key] = list(df_metric[MDC.ROC_AUC])
        return x_dict, y_dict


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


class MyDashTabStatisticsPlotter4Waves(MyDashTabStatisticsPlotter):
    def __init__(self, wave_handler: FibonacciWaveDataHandler, color_handler: DashColorHandler, index=''):
        self._wave_handler = wave_handler
        self._index = index
        MyDashTabStatisticsPlotter.__init__(self, self._wave_handler.df_wave, color_handler)

    def __init_parameter__(self):
        self.__init_parameter_by_chart_type__(CHT.HEAT_MAP)
        self._chart_id = 'waves_heatmap'
        self._chart_name = 'Waves'
        self.chart_type = CHT.HEAT_MAP

    def __init_parameter_by_chart_type__(self, chart_type: str):
        self.chart_type = chart_type
        if self.chart_type == CHT.HEAT_MAP:
            self._chart_id = 'waves_heatmap'
            self._chart_name = 'Waves'
        elif self.chart_type == CHT.MOOD_CHART:
            self._chart_id = 'waves_mood_chart'
            self._chart_name = 'Mood Chart'

    def __print_df_base__(self):
        columns = [DC.EQUITY_TYPE, DC.PERIOD, DC.WAVE_TYPE, DC.WAVE_END_DT]
        df_reduced = self._df_base[columns]
        print('__print_df_base__: _df_wave\n{}'.format(df_reduced.head(100)))

    def __get_chart_type_heatmap__(self):
        graph_list = []
        if self._index in ['', INDICES.ALL]:
            index_list = [INDICES.CRYPTO_CCY, INDICES.DOW_JONES, INDICES.NASDAQ100]
        else:
            index_list = [self._index]
        for index in index_list:
            index_for_key = index.replace(' ', '_').lower()
            index_for_key = index_for_key if self._index == '' else '{}_{}'.format(index_for_key, 'single')
            chart_id = '{}_{}'.format(self._chart_id, index_for_key)
            # print('__get_chart_type_heatmap__: chart_id={}'.format(chart_id))
            chart_name = index
            graph_api = DccGraphApi(chart_id, chart_name)
            graph_api.figure_data = self.__get_heatmap_figure_data__(index)
            graph_api.figure_layout_height = 200
            graph_api.figure_layout_margin = {'b': 50, 'r': 50, 'l': 50, 't': 50}
            graph_list.append(MyDCC.graph(graph_api))
        return graph_list

    def __get_data_for_heatmap_figure__(self, index: str, for_mood_graph=False):
        x_data = self._wave_handler.tick_key_list_for_retrospection
        if self._wave_handler.period_for_retrospection == PRD.INTRADAY:
            x_data = [str(MyDate.get_date_time_from_epoch_seconds(key)) for key in x_data]
        y_data = WAVEST.get_waves_types_for_processing([self._wave_handler.period_for_retrospection])
        y_data = y_data[::-1]  # we want them in this order
        z_data = [self._wave_handler.get_waves_number_list_for_wave_type_and_index(wt, index) for wt in y_data]
        # print('__get_data_for_heatmap_figure__: {}: \n{}\n{}\n{}'.format(index, x_data, y_data, z_data))
        if for_mood_graph:
            return self.__get_heatmap_data_for_mood_graph__(x_data, y_data, z_data)
        return [x_data, y_data, z_data]

    @staticmethod
    def __get_heatmap_data_for_mood_graph__(x_data: list, y_data: list, z_data: list):
        """
        :param x_data=['2018-12-11', '2018-12-12', '2018-12-13', '2018-12-14',
        :param y_data=['intraday_descending', 'daily_descending', 'intraday_ascending', 'daily_ascending']
        :param z_data=[[2, 0, 1, 13, 4, 0, 0, 0, 0, 0, 1, 0, 0,...], [...], [...], [...]]
        :return:
        """
        z_data_dict = {wave_type: z_data[ind] for ind, wave_type in enumerate(y_data)}
        y_data_dict = {FD.ASC: list(np.add(z_data_dict[WAVEST.DAILY_ASC], z_data_dict[WAVEST.INTRADAY_ASC])),
                       FD.DESC: list(np.add(z_data_dict[WAVEST.DAILY_DESC], z_data_dict[WAVEST.INTRADAY_DESC])),
                       WAVEST.DAILY_ASC: z_data_dict[WAVEST.DAILY_ASC],
                       WAVEST.DAILY_DESC: z_data_dict[WAVEST.DAILY_DESC],
                       }
        return [x_data, y_data_dict]

    def __get_chart_type_mood__(self):
        graph_list = []
        if self._index in ['', INDICES.ALL]:
            index_list = [INDICES.CRYPTO_CCY, INDICES.DOW_JONES, INDICES.NASDAQ100]
        else:
            index_list = [self._index]
        for index in index_list:
            index_for_key = index.replace(' ', '_').lower()
            index_for_key = index_for_key if self._index == '' else '{}_{}'.format(index_for_key, 'single')
            chart_id = '{}_{}'.format(self._chart_id, index_for_key)
            # print('__get_chart_type_heatmap__: chart_id={}'.format(chart_id))
            chart_name = index
            graph_api = DccGraphApi(chart_id, chart_name)
            figure_data, max_value = self.__get_mood_chart_figure_data__(index)
            max_value = int(round(max_value + 5, -1))
            value_interval = max(10, int(round(max_value/3, -1)))
            tick_vals = list(range(-max_value, max_value, value_interval))
            tick_text = [abs(value) for value in tick_vals]
            graph_api.figure_data = figure_data
            graph_api.figure_layout_height = 300
            graph_api.figure_layout_margin = {'b': 50, 'r': 50, 'l': 50, 't': 50}
            graph_api.figure_layout_barmode = 'overlay'
            graph_api.figure_layout_bargap = 0.1
            graph_api.figure_layout_x_axis_dict = {}
            graph_api.figure_layout_y_axis_dict = {'range': 'Date',
                                                   'tickvals': tick_vals,
                                                   'ticktext': tick_text}
            graph_list.append(MyDCC.graph(graph_api))
        return graph_list
