"""
Description: This module contains the plotter functions for pattern statistics tabs.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""


from sertl_analytics.constants.pattern_constants import DC, CHT, FT, PRED
from pattern_dash.plotter_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter


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

