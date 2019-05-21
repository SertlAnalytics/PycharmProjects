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
from sertl_analytics.mydash.my_dash_components import MyDCC, DccGraphApi
from sertl_analytics.my_numpy import MyNumpy
import numpy as np
from sklearn.linear_model import LinearRegression
from salesman_sale import SalesmanSale


class MyDashTabPlotter4Sales(MyDashTabPlotter):
    def __init_parameter__(self):
        self._chart_id = 'sales_statistics_graph'
        self._chart_name = 'Statistics'
        self.category = SLDC.PRINT_CATEGORY
        self.x_variable = SLDC.START_DATE
        self.y_variable = SLDC.PRICE_SINGLE
        self.text_variable = SLDC.TITLE
        self.category_list = []

    def get_chart_type_regression(self, master_sale: SalesmanSale):
        graph_api = DccGraphApi(self._chart_id, '{} ({})'.format(self.category, self.x_variable))
        graph_api.figure_data = self.__get_regression_figure_data__(master_sale)
        graph_api.figure_layout_x_axis_dict = self.__get_figure_layout_x_axis_dict__()
        # graph_api.figure_layout_y_axis_dict = self.__get_figure_layout_y_axis_dict__(graph_api)
        return [MyDCC.graph(graph_api)]

    def __get_regression_figure_data__(self, master_sale: SalesmanSale):
        x_orig = self._df_base[self.x_variable]
        y_data = self._df_base[self.y_variable]
        x_orig_predict = MyNumpy.get_date_values_as_number_for_date_time_array(list(x_orig))
        category_list = list(set([entity_label for entity_label in master_sale.entity_label_dict.values()]))
        x_dict, y_dict = self.__get_x_dict_and_y_dict_for_regression__(category_list, self.y_variable)
        trace_list_regression = []
        color_all = self._color_handler.get_color_for_category('ALL')
        # trace_list_regression.append(self.__get_scatter_trace_for_x_y_data__(x_orig, color_all, y_data, 'My'))
        trace_list_regression.append(self.__get_scatter_trace_for_x_y_data__(x_orig, color_all, y_data, 'All'))
        for cat in x_dict:
            color = self._color_handler.get_color_for_category(cat)
            x_data = x_dict[cat]
            y_data = y_dict[cat]
            trace_list_regression.append(
                self.__get_regression_trace_for_x_y_data__(x_orig, x_orig_predict, color, x_data, y_data, cat))
        return trace_list_regression

    def __get_x_dict_and_y_dict_for_regression__(self, category_list: list, metric_list: list):
        # both together since we need the same order....
        x_dict = {}
        y_dict = {}
        for cat in category_list:
            # df_cat = self._df_base[np.logical_and(self._df_base[SLDC.PRICE_SINGLE] > 0,
            #                                       self._df_base[SLDC.PRICE_SINGLE] > 0)]
            df_cat = self._df_base[self._df_base[SLDC.ENTITY_LABELS_DICT].str.contains(cat)]
            if df_cat.shape[0] > 10:  # we need some for getting a correct regression
                x_dict[cat] = list(df_cat[SLDC.START_DATE])
                y_dict[cat] = list(df_cat[SLDC.PRICE_SINGLE])
        return x_dict, y_dict

    @staticmethod
    def __get_regression_trace_for_x_y_data__(
            x_orig: pd.Series, x_orig_predict, color: str, x_train: list, y_train: list, cat: str):
        lin_reg = LinearRegression()
        x_train_reshaped = MyNumpy.get_date_values_as_number_for_date_time_array(x_train)
        y_train_reshaped = np.array(y_train).reshape(-1, 1)
        lin_reg.fit(x_train_reshaped, y_train_reshaped)
        y_predict = lin_reg.predict(X=x_orig_predict)
        y_predict_values = np.array([y_value[0] for y_value in y_predict])

        return go.Scatter(
            x=x_orig.values,
            y=y_predict_values,
            mode='lines',
            opacity=0.7,
            line=dict(color=color, width=3),
            name=cat
        )

    def __get_scatter_trace_for_x_y_data__(self, x_orig: pd.Series, color: str, y_data: list, cat: str):
        return go.Scatter(
            x=x_orig.values,
            y=y_data,
            mode='markers',
            opacity=0.7,
            marker={'symbol': 'diamond',
                    'size': 10,
                    'color': color,
                    'line': {'width': 0.5, 'color': 'white'}},
            text=self._df_base[SLDC.TITLE],
            name=cat,
        )
