"""
Description: This module contains the tab for Dash for pattern statistics.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

from dash.dependencies import Input, Output
from sertl_analytics.constants.pattern_constants import DC, CHT, PRED, FT
from pattern_database.stock_tables import PatternTable
from pattern_dash.my_dash_header_tables import MyHTMLTabPatternStatisticsHeaderTable
from pattern_dash.my_dash_tab_dd_for_statistics import DDT, PatternStatisticsDropDownHandler
from pattern_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter4Pattern
from pattern_dash.my_dash_tab_for_statistics_base import MyDashTab4StatisticsBase
import pandas as pd


class MyDashTab4PatternStatistics(MyDashTab4StatisticsBase):
    def __fill_tab__(self):
        self._tab = 'pattern'

    @property
    def column_result(self):
        return DC.EXPECTED_WIN_REACHED

    @staticmethod
    def __get_html_tab_header_table__():
        return MyHTMLTabPatternStatisticsHeaderTable().get_table()

    def __get_df_base__(self) -> pd.DataFrame:
        return self.sys_config.db_stock.get_pattern_records_as_dataframe()

    def __init_dd_handler__(self):
        self._dd_handler = PatternStatisticsDropDownHandler()

    def __init_plotter__(self):
        self._plotter = MyDashTabStatisticsPlotter4Pattern(self._df_base, self._color_handler)

    @staticmethod
    def __get_value_list_for_x_variable_options__(chart_type: str, predictor: str):
        if chart_type == CHT.PREDICTOR:
            if predictor == PRED.BEFORE_BREAKOUT:
                return PatternTable.get_feature_columns_before_breakout_for_statistics()
            elif predictor == PRED.AFTER_BREAKOUT:
                return PatternTable.get_feature_columns_after_breakout_for_statistics()
            else:
                return PatternTable.get_feature_columns_touch_points_for_statistics()
        return PatternTable.get_columns_for_statistics_x_variable()

    @staticmethod
    def __get_value_list_for_y_variable_options__(chart_type: str, predictor: str):
        if chart_type == CHT.PREDICTOR:
            if predictor == PRED.BEFORE_BREAKOUT:
                return PatternTable.get_label_columns_before_breakout_for_statistics()
            elif predictor == PRED.AFTER_BREAKOUT:
                return PatternTable.get_label_columns_after_breakout_for_statistics()
            else:
                return PatternTable.get_label_columns_touch_points_for_statistics()
        return PatternTable.get_columns_for_statistics_y_variable()

