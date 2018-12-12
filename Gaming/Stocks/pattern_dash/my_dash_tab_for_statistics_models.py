"""
Description: This module contains the tab for Dash for trade statistics.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-26
"""

from dash.dependencies import Input, Output, State
from sertl_analytics.constants.pattern_constants import DC, TRC, EQUITY_TYPE, PRED, STBL
from sertl_analytics.mydates import MyDate
from pattern_system_configuration import SystemConfiguration
from dash import Dash
from pattern_dash.my_dash_colors import DashColorHandler
from pattern_database.stock_tables import TradeTable, PatternTable
from pattern_dash.my_dash_header_tables import MyHTMLTabModelsStatisticsHeaderTable
from pattern_dash.my_dash_tab_dd_for_statistics import ModelsStatisticsDropDownHandler
from pattern_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter4Models
from pattern_dash.my_dash_tab_for_statistics_base import MyDashTab4StatisticsBase, DDT
from pattern_dash.my_dash_components import MyHTML
from pattern_database.stock_database import StockDatabase
import pandas as pd


class MyDashTab4ModelStatistics(MyDashTab4StatisticsBase):
    def __init__(self, app: Dash, sys_config: SystemConfiguration, color_handler: DashColorHandler):
        MyDashTab4StatisticsBase.__init__(self, app, sys_config, color_handler)

    def __fill_tab__(self):
        self._tab = 'models'

    @property
    def column_result(self):
        return DC.VALUE_TOTAL

    def init_callbacks(self):
        # self.__init_callback_for_numbers__()
        # self.__init_callback_for_pattern_type_label__()
        # self.__init_callback_for_pattern_type_numbers__()
        # self.__init_callbacks_for_drop_down_visibility__()
        self.__init_callbacks_for_chart__()
        self.__init_callback_for_predictor_options__()
        # self.__init_callback_for_markdown__()
        self.__init_callback_for_x_variable_options__()
        # self.__init_callback_for_y_variable_options__()
        pass

    def get_div_for_tab(self):
        children_list = [
            self.__get_html_tab_header_table__(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.CHART_TYPE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.CATEGORY)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.PREDICTOR)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.X_VARIABLE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.Y_VARIABLE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.CHART_TEXT_VARIABLE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.MODEL_TYPE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.PATTERN_TYPE)),
            MyHTML.div(self._my_statistics_chart_div, self.__get_charts_from_plotter__(), False),
        ]
        # print('self._my_statistics_chart_div={}'.format(self._my_statistics_chart_div))
        return MyHTML.div(self._my_statistics, children_list)

    def __init_callback_for_numbers__(self):
        @self.app.callback(
            Output('my_models_crypto_client_div', 'children'),
            [Input('my_interval_refresh', 'n_intervals')])
        def handle_callback_for_crypto_client_assets(n_intervals: int):
            amount, change_abs, change_pct = 0, 0, 0
            return '{:.0f} ({:+.0f}/{:+.2f}%)'.format(amount, change_abs, change_pct)

        @self.app.callback(
            Output('my_models_stock_client_div', 'children'),
            [Input('my_interval_refresh', 'n_intervals')])
        def handle_callback_for_stock_client_assets(n_intervals: int):
            amount, change_abs, change_pct = 0, 0, 0
            return '{:.0f} ({:+.0f}/{:+.2f}%)'.format(amount, change_abs, change_pct)

    def __init_callback_for_predictor_options__(self):
        @self.app.callback(
            Output(self._my_statistics_predictor_selection, 'options'),
            [Input(self._my_statistics_category_selection, 'value')]
        )
        def handle_callback_for_predictor_options(category: str):
            value_list = self.__get_value_list_for_predictor_options__(category)
            return [{'label': value.replace('_', ' '), 'value': value} for value in value_list]

        @self.app.callback(
            Output(self._my_statistics_predictor_selection, 'value'),
            [Input(self._my_statistics_predictor_selection, 'options')],
            [State(self._my_statistics_category_selection, 'value')]
        )
        def handle_callback_for_predictor_value(prediction_options, category: str):
            return self.__get_value_list_for_predictor_options__(category)[0]

    def __init_callback_for_x_variable_options__(self):
        @self.app.callback(
            Output(self._my_statistics_x_variable_selection, 'options'),
            [Input(self._my_statistics_predictor_selection, 'value')],
            [State(self._my_statistics_category_selection, 'value')]
        )
        def handle_callback_for_x_variable_options(predictor: str, category: str):
            value_list = self.__get_value_list_for_x_variable_options__(category, predictor)
            return [{'label': value.replace('_', ' '), 'value': value} for value in value_list]

        @self.app.callback(
            Output(self._my_statistics_x_variable_selection, 'value'),
            [Input(self._my_statistics_x_variable_selection, 'options')],
            [State(self._my_statistics_category_selection, 'value'),
             State(self._my_statistics_predictor_selection, 'value')]
        )
        def handle_callback_for_x_variable_value(x_varible_options, category: str, predictor: str):
            value_list = self.__get_value_list_for_x_variable_options__(category, predictor)
            return value_list[0]

    def __init_callbacks_for_chart__(self):
        @self.app.callback(
            Output(self._my_statistics_chart_div, 'children'),
            [Input(self._my_statistics_chart_type_selection, 'value'),
             Input(self._my_statistics_x_variable_selection, 'value'),
             Input(self._my_statistics_y_variable_selection, 'value'),
             Input(self._my_statistics_model_type_selection, 'value'),
             Input(self._my_statistics_text_variable_selection, 'value'),
             Input(self._my_statistics_pattern_type_selection, 'value'),
             Input('my_interval_refresh', 'n_intervals')],
            [State(self._my_statistics_category_selection, 'value'),
             State(self._my_statistics_predictor_selection, 'value')])
        def handle_callbacks_for_models_chart(ct: str, x: str, y: object,
                                              model_type: object, text_variable: str, pattern_type: str,
                                              n_intervals: int, category: str, pred: str):
            self._category_selected = category
            self.__fill_df_base__()
            self.__init_plotter__()
            self._plotter.chart_type = ct
            self._plotter.category = category
            self._plotter.predictor = pred
            self._plotter.x_variable = x
            self._plotter.y_variable = [y] if type(y) is str else y
            self._plotter.model_type = [model_type] if type(model_type) is str else model_type
            self._plotter.text_variable = text_variable
            self._plotter.pattern_type = pattern_type
            return self.__get_charts_from_plotter__()

    def __get_df_base__(self) -> pd.DataFrame:
        return self.sys_config.db_stock.get_pattern_records_as_dataframe()  # this will be overwritten within plotter...

    @staticmethod
    def __get_html_tab_header_table__():
        return MyHTMLTabModelsStatisticsHeaderTable().get_table()

    def __init_dd_handler__(self):
        self._dd_handler = ModelsStatisticsDropDownHandler()

    def __init_plotter__(self):
        self._plotter = MyDashTabStatisticsPlotter4Models(self._df_base, self._color_handler, self.sys_config.db_stock)

    @staticmethod
    def __get_value_list_for_x_variable_options__(category: str, predictor: str):
        if category == STBL.PATTERN:
            if predictor == PRED.TOUCH_POINT:
                return PatternTable.get_label_columns_touch_points_for_statistics()
            elif predictor == PRED.BEFORE_BREAKOUT:
                return PatternTable.get_label_columns_before_breakout_for_statistics()
            elif predictor == PRED.AFTER_BREAKOUT:
                return PatternTable.get_label_columns_after_breakout_for_statistics()
        else:
            return TradeTable.get_label_columns_for_trades_statistics()

    @staticmethod
    def __get_value_list_for_predictor_options__(category: str):
        return PRED.get_for_pattern_all() if category == STBL.PATTERN else PRED.get_for_trade_all()
