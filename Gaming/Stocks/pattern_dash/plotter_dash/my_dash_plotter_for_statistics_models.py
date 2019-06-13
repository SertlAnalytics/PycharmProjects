"""
Description: This module contains the plotter functions for models statistics tabs.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import plotly.graph_objs as go

from sertl_analytics.constants.pattern_constants import DC, CHT, FT, PRED, MT, STBL, MTC, MDC
from sertl_analytics.my_numpy import MyNumpy
from pattern_dash.my_dash_colors import DashColorHandler
from pattern_database.stock_database import StockDatabase
from pattern_database.stock_tables import PatternTable, TradeTable
from pattern_predictor_optimizer import PatternPredictorOptimizer
import pandas as pd
import itertools
import numpy as np
from sklearn.linear_model import LinearRegression
from pattern_dash.plotter_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter


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
            self.__fill_y_dict_for_metrics__(df_metric, metric_list, model_type, y_dict)
        return x_dict, y_dict

    def __get_confusion_regression_figure_data__(self):
        x_orig = self._predictor_optimizer.get_x_orig_data_for_confusion_regression()
        x_orig_predict = MyNumpy.get_date_values_as_number_for_date_time_array(list(x_orig))
        # print('x_orig={}\nx_orig_predict={}'.format(x_orig, x_orig_predict, type(x_orig_predict)))
        model_type_list = self.model_type
        x_dict, y_dict = self.__get_x_dict_and_y_dict_for_regression__(model_type_list, self.y_variable)
        color_dict = {cat: self._color_handler.get_color_for_category(cat) for cat in model_type_list}
        trace_list = []
        trace_list_regression = []
        for model_type_value in x_dict:
            color = self._color_handler.get_color_for_category(model_type_value)
            x_data = x_dict[model_type_value]
            for metric in self.y_variable:
                y_key = '{}-{}'.format(model_type_value, metric)
                y_data = y_dict[y_key]
                trace_list.append(
                    self.__get_trace_for_confusion_regression__(color, metric, model_type_value, x_dict, y_dict)
                )
                trace_list_regression.append(
                    self.__get_regression_trace_for_x_y_data__(x_orig, x_orig_predict, color, x_data, y_data, y_key)
                )
        return trace_list_regression  # ToDo - check with other list trace_list_regression

    @staticmethod
    def __get_trace_for_confusion_regression__(color, metric, model_type_value, x_dict, y_dict):
        return go.Scatter(
            x=x_dict[model_type_value],
            y=y_dict['{}-{}'.format(model_type_value, metric)],
            text=['{}-{}: {:0.2f}'.format(model_type_value, metric, y_value)
                  for y_value in y_dict['{}-{}'.format(model_type_value, metric)]],
            line={'color': color, 'width': 2},
            opacity=0.7,
            name='{}-{}'.format(model_type_value, metric)
        )

    @staticmethod
    def __get_regression_trace_for_x_y_data__(
            x_orig: pd.Series, x_orig_predict, color: str, x_train: list, y_train: list, y_key: str):
        lin_reg = LinearRegression()
        x_train, y_train = MyDashTabStatisticsPlotter4Models.__get_x_y_train_only_with_y_values__(x_train, y_train)
        x_train_reshaped = MyNumpy.get_date_values_as_number_for_date_time_array(x_train)
        y_train_reshaped = np.array(y_train).reshape(-1, 1)
        # MyDashTabStatisticsPlotter4Models.__print_x_y_data_details__(
        #     y_key, x_orig, x_orig_predict, x_train_reshaped, y_train_reshaped, with_details=False)
        lin_reg.fit(x_train_reshaped, y_train_reshaped)
        y_predict = lin_reg.predict(x_orig_predict)
        y_predict_values = np.array([y_value[0] for y_value in y_predict])

        return go.Scatter(
            x=x_orig.values,
            y=y_predict_values,
            mode='lines',
            opacity=0.7,
            line=dict(color=color, width=3),
            name=y_key
        )

    @staticmethod
    def __print_x_y_data_details__(
            key: str, x_orig, x_orig_predict, x_train_reshaped, y_train_reshaped, with_details=False):
        print('{}: type(x_train_reshaped)={}, type(y_train_reshaped)={}, type(x_orig)={}, type(x_orig_predict)={}'.
            format(key, type(x_train_reshaped), type(y_train_reshaped), type(x_orig), type(x_orig_predict)))
        print('{}: shape(x_train_reshaped)={}, shape(y_train_reshaped)={}, shape(x_orig)={}, shape(x_orig_predict)={}'.
            format(key, x_train_reshaped.shape, y_train_reshaped.shape, x_orig.shape, x_orig_predict.shape))
        if with_details:
            print('{}: x_train_reshaped={}\ny_train_reshaped={}\nx_orig={}\nx_orig_predict={}'.format(
                key, x_train_reshaped, y_train_reshaped, x_orig, x_orig_predict))

    @staticmethod
    def __get_x_y_train_only_with_y_values__(x_train: list, y_train: list):
        x_train_new = []
        y_train_new = []
        for idx, x_value in enumerate(x_train):
            y_value = y_train[idx]
            if y_value > 0:
                x_train_new.append(x_value)
                y_train_new.append(y_value)
        return x_train_new, y_train_new

    def __get_x_dict_and_y_dict_for_regression__(self, model_type_list: list, metric_list: list):
        # both together since we need the same order....
        x_dict = {}
        y_dict = {}
        for model_type in model_type_list:
            df_metric = self._predictor_optimizer.get_metrics_for_model_and_label_as_data_frame_for_regression(
                model_type, self.predictor, self.x_variable, self.pattern_type)
            # print('__get_x_dict_and_y_dict_for_regression__: df.head={}'.format(df_metric.head()))
            distinct_values = df_metric[MDC.VALUE].unique()
            for value in distinct_values:
                df_metric_specific_value = df_metric[
                    np.logical_and(
                        df_metric[MDC.VALUE] == value,
                        df_metric[MDC.PRECISION] > 0  # sometimes we have 0 values... problem
                    )]
                if df_metric_specific_value.shape[0] > 20:  # we need some for getting a correct regression
                    model_type_value = '{}-{}'.format(model_type, value)
                    x_dict[model_type_value] = list(df_metric_specific_value[MDC.VALID_DT])
                    self.__fill_y_dict_for_metrics__(df_metric_specific_value, metric_list, model_type_value, y_dict)
        return x_dict, y_dict

    @staticmethod
    def __fill_y_dict_for_metrics__(df: pd.DataFrame, metric_list: list, model_type_value: str, y_dict: dict):
        for metric in metric_list:
            key = '{}-{}'.format(model_type_value, metric)
            if metric == MTC.PRECISION:
                y_dict[key] = list(df[MDC.PRECISION])
            elif metric == MTC.RECALL:
                y_dict[key] = list(df[MDC.RECALL])
            elif metric == MTC.F1_SCORE:
                y_dict[key] = list(df[MDC.F1_SCORE])
            elif metric == MTC.ROC_AUC:
                y_dict[key] = list(df[MDC.ROC_AUC])

