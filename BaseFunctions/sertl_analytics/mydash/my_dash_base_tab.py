"""
Description: This module is the base class for a tab for Dash
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

from dash import Dash
from sertl_analytics.mydates import MyDate
from sertl_analytics.mydash.my_dash_color_handler import DashColorHandler


class MyDashBaseTab:
    def __init__(self, app: Dash):
        self.app = app
        self._color_handler = self.__get_color_handler__()
        self._time_stamp_last_refresh = MyDate.time_stamp_now()
        self._dd_handler = None
        self._button_handler = None

    def init_callbacks(self):
        pass

    def get_div_for_tab(self):
        pass

    def __get_color_handler__(self):
        return DashColorHandler()

