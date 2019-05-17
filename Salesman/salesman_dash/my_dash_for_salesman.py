"""
Description: This module is the main module for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

from dash.dependencies import Input, Output, State
import json
from sertl_analytics.myconstants import MyAPPS
from sertl_analytics.my_http import MyHttpClient
from sertl_analytics.mydash.my_dash_base import MyDashBase
from sertl_analytics.mydates import MyDate
from sertl_analytics.mydash.my_dash_components import MyDCC, MyHTML
from salesman_dash.header_tables.my_dash_header_tables import MyHTMLHeaderTable
from salesman_dash.my_dash_tab_for_sales import MyDashTab4Sales
from salesman_dash.my_dash_tab_for_search import MyDashTab4Search
from salesman_dash.my_dash_tab_for_jobs import MyDashTab4Jobs
from salesman_system_configuration import SystemConfiguration
from salesman_tutti.tutti import Tutti
from datetime import datetime, timedelta


class MyDash4Salesman(MyDashBase):
    def __init__(self, sys_config: SystemConfiguration):
        MyDashBase.__init__(self, MyAPPS.SALESMAN_DASH())
        self.sys_config = sys_config
        self.tutti = Tutti(sys_config)
        self.tab_sales = MyDashTab4Sales(self.app, self.sys_config, self.tutti)
        self.tab_search = MyDashTab4Search(self.app, self.sys_config, self.tutti)
        # self.tab_log = MyDashTab4Log(self.app)
        self.tab_jobs = MyDashTab4Jobs(self.app, self.tutti)

    def get_salesman(self):
        self.__set_app_layout__()
        self.__init_interval_callback_for_user_name__()
        self.__init_interval_callback_for_time_div__()
        self.__init_interval_refresh_callback_for_http_connection_div__()
        self.__init_interval_callback_for_interval_refresh_details__()
        self.tab_sales.init_callbacks()
        self.tab_search.init_callbacks()
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

    def __init_interval_refresh_callback_for_http_connection_div__(self):
        @self.app.callback(
            Output('my_http_connection_div', 'children'),
            [Input('my_interval_timer', 'n_intervals')],
            [State('my_http_connection_div', 'children')]
        )
        def handle_interval_refresh_callback_for_http_connection_value(n_intervals, old_value: str):
            self.sys_config.is_http_connection_ok = MyHttpClient.do_we_have_internet_connection()
            return MyHttpClient.get_status_message(old_value)

        @self.app.callback(
            Output('my_http_connection_div', 'style'),
            [Input('my_http_connection_div', 'children')])
        def handle_interval_refresh_callback_for_http_connection_value(http_connection_info: str):
            if self.sys_config.is_http_connection_ok:
                return {'font-weight': 'normal', 'color': 'black', 'display': 'inline-block'}
            return {'font-weight': 'bold', 'color': 'red', 'display': 'inline-block'}

    def __init_interval_callback_for_interval_refresh_details__(self):
        @self.app.callback(
            Output('my_last_refresh_time_div', 'children'),
            [Input('my_interval_refresh', 'n_intervals')])
        def handle_interval_callback_for_last_refresh(n_intervals):
            self._time_stamp_last_refresh = MyDate.time_stamp_now()
            last_refresh_dt = MyDate.get_time_from_datetime(datetime.now())
            return '{} ({})'.format(last_refresh_dt, n_intervals)

        @self.app.callback(
            Output('my_next_refresh_time_div', 'children'),
            [Input('my_interval_refresh', 'n_intervals')],
            [State('my_interval_refresh', 'interval')])
        def handle_interval_callback_for_next_refresh(n_intervals, interval_ms):
            dt_next = datetime.now() + timedelta(milliseconds=interval_ms)
            self._time_stamp_next_refresh = int(dt_next.timestamp())
            return '{}'.format(MyDate.get_time_from_datetime(dt_next))

    def __set_app_layout__(self):
        # self.app.layout = self.__get_div_for_tab_pattern_detection__()
        self.app.layout = self.__get_div_for_app_layout__()

    def __get_div_for_app_layout__(self):
        children_list = [
            MyHTMLHeaderTable().get_table(),
            MyDCC.interval('my_interval_timer', 60),
            MyDCC.interval('my_interval_refresh', 600),
            self.__get_tabs_for_app__()
        ]
        return MyHTML.div('my_app', children_list)

    def __get_tabs_for_app__(self):
        tab_list = [
            MyDCC.tab('Search', [self.tab_search.get_div_for_tab()]),
            MyDCC.tab('Sales', [self.tab_sales.get_div_for_tab()]),
            # MyDCC.tab('Logs', [self.tab_log.get_div_for_tab()]),
            MyDCC.tab('Jobs', [self.tab_jobs.get_div_for_tab()]),
        ]
        return MyDCC.tabs('my_app_tabs', tab_list)
