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
        self._time_stamp_last_refresh = MyDate.time_stamp_now()
        self._tab = self.__get_tab_name__()
        self._color_handler = self.__get_color_handler__()
        self._dd_handler = self.__get_drop_down_handler__()
        self._button_handler = self.__get_button_handler__()
        self.__init_dash_element_ids__()

    def init_callbacks(self):
        pass

    def get_div_for_tab(self):
        pass

    @staticmethod
    def __get_tab_name__():
        return ''

    @staticmethod
    def __get_drop_down_handler__():
        pass

    @staticmethod
    def __get_button_handler__():
        pass

    def __get_color_handler__(self):
        return DashColorHandler()

    def __init_dash_element_ids__(self):
        pass

