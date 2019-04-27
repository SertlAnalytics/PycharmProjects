"""
Description: This module is the main module for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

from dash.dependencies import Input, Output
from datetime import datetime
import json
from sertl_analytics.myconstants import MyAPPS
from sertl_analytics.mydash.my_dash_base import MyDashBase
from sertl_analytics.mydates import MyDate
from sertl_analytics.mydash.my_dash_components import MyDCC, MyHTML
from salesman_dash.header_tables.my_dash_header_tables import MyHTMLHeaderTable
from salesman_dash.my_dash_tab_for_sales import MyDashTab4Sales
from salesman_dash.my_dash_tab_for_pricing import MyDashTab4Pricing
from salesman_dash.my_dash_tab_for_jobs import MyDashTab4Jobs
from salesman_system_configuration import SystemConfiguration
from tutti import Tutti


class MyDash4Salesman(MyDashBase):
    def __init__(self, sys_config: SystemConfiguration):
        MyDashBase.__init__(self, MyAPPS.SALESMAN_DASH())
        self.sys_config = sys_config
        self.tutti = Tutti(sys_config)
        self.tab_sales = MyDashTab4Sales(self.app, self.sys_config, self.tutti)
        self.tab_pricing = MyDashTab4Pricing(self.app, self.sys_config, self.tutti)
        # self.tab_log = MyDashTab4Log(self.app)
        self.tab_jobs = MyDashTab4Jobs(self.app)

    def get_salesman(self):
        self.__set_app_layout__()
        self.__init_interval_callback_for_user_name__()
        self.__init_interval_callback_for_time_div__()
        self.tab_sales.init_callbacks()
        self.tab_pricing.init_callbacks()
        self.tab_jobs.init_callbacks()

    def run_on_server(self):
        self.app.run_server(debug=False, port=8051)

    @staticmethod
    def __create_callback__():
        def callback_hover_data(hoverData):
            return json.dumps(hoverData, indent=2)
        return callback_hover_data

    def __init_interval_callback_for_user_name__(self):
        @self.app.callback(
            Output('my_user_name_div', 'children'),
            [Input('my_interval_refresh', 'n_intervals')])
        def handle_interval_callback_for_user_name(n_intervals):
            if self._user_name == '':
                self._user_name = self._get_user_name_()
            return self._user_name

    def __init_interval_callback_for_time_div__(self):
        @self.app.callback(
            Output('my_time_div', 'children'),
            [Input('my_interval_timer', 'n_intervals')])
        def handle_interval_callback_for_time_div(n_intervals):
            return '{}'.format(MyDate.get_time_from_datetime(datetime.now()))

    def __set_app_layout__(self):
        # self.app.layout = self.__get_div_for_tab_pattern_detection__()
        self.app.layout = self.__get_div_for_app_layout__()

    def __get_div_for_app_layout__(self):
        children_list = [
            MyHTMLHeaderTable().get_table(),
            MyDCC.interval('my_interval_timer', 15),
            MyDCC.interval('my_interval_refresh', 120),
            self.__get_tabs_for_app__()
        ]
        return MyHTML.div('my_app', children_list)

    def __get_tabs_for_app__(self):
        tab_list = [
            MyDCC.tab('Sales', [self.tab_sales.get_div_for_tab()]),
            MyDCC.tab('Pricing', [self.tab_pricing.get_div_for_tab()]),
            # MyDCC.tab('Logs', [self.tab_log.get_div_for_tab()]),
            MyDCC.tab('Jobs', [self.tab_jobs.get_div_for_tab()]),

        ]
        return MyDCC.tabs('my_app_tabs', tab_list)
