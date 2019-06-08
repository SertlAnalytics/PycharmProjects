"""
Description: This module contains the plotter functions for trades statistics tabs.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-29
"""

import plotly.graph_objs as go
from entities.salesman_entity_handler import SalesmanEntityHandler
from sertl_analytics.constants.salesman_constants import SLDC
import pandas as pd
from salesman_dash.plotting.my_dash_plotter_for_salesman import MyDashTabPlotter
from sertl_analytics.mydash.my_dash_components import MyDCC, DccGraphApi
from sertl_analytics.my_numpy import MyNumpy
import numpy as np
from sklearn.linear_model import LinearRegression
from salesman_sale import SalesmanSale
from salesman_dash.my_dash_colors import DashColorHandler


class MyDashTabPlotter4Sales(MyDashTabPlotter):
    def __init__(self, df_base: pd.DataFrame, color_handler: DashColorHandler, entity_handler: SalesmanEntityHandler):
        self._entity_handler = entity_handler
        MyDashTabPlotter.__init__(self, df_base, color_handler)

    def __init_parameter__(self):
        self._chart_id = 'sales_statistics_graph'
        self._chart_name = 'Statistics'
        self.category = SLDC.PLOT_CATEGORY
        self.x_variable = SLDC.START_DATE
        self.y_variable = SLDC.PRICE_SINGLE
        self.text_variable = SLDC.TITLE
        self.category_list = []

    def get_chart_type_regression(self, master_sale: SalesmanSale):
        graph_api = DccGraphApi(self._chart_id, '{}'.format(master_sale.title), use_title_for_y_axis=False)
        graph_api.figure_data = self.__get_regression_figure_data__(master_sale)
        graph_api.figure_layout_x_axis_dict = self.__get_figure_layout_x_axis_dict__()
        # graph_api.figure_layout_y_axis_dict = self.__get_figure_layout_y_axis_dict__(graph_api)
        return [MyDCC.graph(graph_api)]

    def __get_regression_figure_data__(self, master_sale: SalesmanSale):
        x_orig = self._df_base[self.x_variable]
        y_data = self._df_base[self.y_variable]
        x_orig_predict = MyNumpy.get_date_values_as_number_for_date_time_array(list(x_orig))
        entity_name_list = []
        print('master_sale.entity_label_values_dict={}'.format(master_sale.entity_label_values_dict))
        for label, values in master_sale.entity_label_main_values_dict.items():
            entity_name_list = entity_name_list + values
        x_dict, y_dict = self.__get_x_dict_and_y_dict_for_regression__(entity_name_list, self.y_variable)
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

    def __get_x_dict_and_y_dict_for_regression__(self, entity_name_list: list, metric_list: list):
        x_dict = {}
        y_dict = {}
        print('entity_name_list={}'.format(entity_name_list))
        for entity_name in entity_name_list:
            df_cat = self._df_base[self._df_base[SLDC.ENTITY_LABELS_DICT].str.contains(entity_name)]
            if df_cat.shape[0] > 3:  # we need some for getting a correct regression
                x_dict[entity_name] = list(df_cat[SLDC.START_DATE])
                y_dict[entity_name] = list(df_cat[SLDC.PRICE_SINGLE])
        return x_dict, y_dict

    @staticmethod
    def __get_regression_trace_for_x_y_data__(
            x_orig: pd.Series, x_orig_predict: pd.Series, color: str, x_train: list, y_train: list, cat: str):
        lin_reg = LinearRegression()
        x_train_reshaped = MyNumpy.get_date_values_as_number_for_date_time_array(x_train)
        y_train_reshaped = np.array(y_train).reshape(-1, 1)
        lin_reg.fit(x_train_reshaped, y_train_reshaped)
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
