"""
Description: This module contains the dash tab for database tables
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-06
"""

from dash.dependencies import Input, Output, State
from sertl_analytics.mydates import MyDate
from pattern_dash.my_dash_base_tab_for_pattern import MyPatternDashBaseTab
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.mydash.my_dash_components import MyDCC, MyHTML
from pattern_dash.my_dash_tab_dd_for_jobs import JOBDD, JobsTabDropDownHandler
from pattern_detection_controller import PatternDetectionController
from pattern_database.stock_access_layer import AccessLayer4Process, AccessLayer4Wave, AccessLayer4Pattern
from dash import Dash
from sertl_analytics.constants.pattern_constants import LOGT, LOGDC, DC, PRDC, STBL, DTRG, JDC
from pattern_news_handler import NewsHandler
from pattern_dash.my_dash_tab_table_for_jobs import JobTable
from pattern_dash.my_dash_job_handler import MyDashJobHandler


class MyDashTab4Jobs(MyPatternDashBaseTab):
    _data_table_name = 'my_jobs_table'
    _data_table_div = '{}_div'.format(_data_table_name)

    def __init__(self, app: Dash, sys_config: SystemConfiguration):
        MyPatternDashBaseTab.__init__(self, app, sys_config)
        self._job_handler = MyDashJobHandler(sys_config.process_manager)
        self.__init_dash_element_ids__()
        self.sys_config = sys_config
        self._db = self.sys_config.db_stock
        self._pattern_controller = PatternDetectionController(self.sys_config)
        self._dd_handler = JobsTabDropDownHandler()
        self._access_layer_process = AccessLayer4Process(self.sys_config.db_stock)
        self._n_clicks_refresh = 0
        self._selected_table_name = STBL.PROCESS
        self._selected_limit = 10
        self._selected_date_range = DTRG.TODAY
        self._grid_table = None

    def __init_dash_element_ids__(self):
        self._my_jobs_last_check_label_div = 'my_jobs_last_check_label_div'
        self._my_jobs_last_check_value_div = 'my_jobs_last_check_value_div'
        self._my_jobs_start_job_button = 'my_jobs_start_job_button'
        self._my_jobs_entry_markdown = 'my_jobs_entry_markdown'

    @staticmethod
    def __get_news_handler__():
        return NewsHandler('  \n', '')

    def get_div_for_tab(self):
        children_list = [
            self.__get_embedded_div_for_last_run_and_start_job_button__(),
            MyHTML.div(self._data_table_div, self.__get_table_for_jobs__(), False),
            MyDCC.markdown(self._my_jobs_entry_markdown)
        ]
        return MyHTML.div('my_jobs_div', children_list)

    def __get_embedded_div_for_last_run_and_start_job_button__(self):
        label_div = MyHTML.div(self._my_jobs_last_check_label_div, 'Last check:', True)
        value_div = MyHTML.div(self._my_jobs_last_check_value_div, '', False)
        button_only = MyHTML.button_submit(self._my_jobs_start_job_button, 'Start selected job')
        return MyHTML.div_embedded([label_div, MyHTML.span(' '), value_div, MyHTML.span(' '), button_only], inline=True)

    def init_callbacks(self):
        self.__init_callback_for_last_check_value_div__()
        self.__init_callback_for_button_visibility__()
        self.__init_callback_for_jobs_table__()
        self.__init_callback_for_jobs_markdown__()

    def __init_callback_for_last_check_value_div__(self):
        @self.app.callback(
            Output(self._my_jobs_last_check_value_div, 'children'),
            [Input('my_interval_refresh', 'n_intervals')])
        def handle_callback_for_last_check_value_div(n_intervals: int):
            self._job_handler.check_scheduler_tasks()
            return self._job_handler.last_run_date_time

    def __init_callback_for_jobs_table__(self):
        @self.app.callback(
            Output(self._data_table_div, 'children'),
            [Input(self._my_jobs_last_check_value_div, 'children'),
             Input(self._my_jobs_start_job_button, 'n_clicks')],
            [State(self._data_table_name, 'rows'),
             State(self._data_table_name, 'selected_row_indices')])
        def handle_callback_for_jobs_table(last_check_value: str, n_clicks_refresh: int,
                                           rows: list, selected_row_indices: list):
            if self._n_clicks_refresh != n_clicks_refresh and len(selected_row_indices) > 0:
                selected_job_row = rows[selected_row_indices[0]]
                job_name = selected_job_row[JDC.NAME]
                self._job_handler.start_job_manually(job_name)
                print('Start job manually: {}'.format(job_name))
            return self.__get_table_for_jobs__()

    def __init_callback_for_jobs_markdown__(self):
        @self.app.callback(
            Output(self._my_jobs_entry_markdown, 'children'),
            [Input(self._data_table_name, 'rows'),
             Input(self._data_table_name, 'selected_row_indices')])
        def handle_callback_for_jobs_markdown(rows: list, selected_row_indices: list):
            if len(selected_row_indices) == 0 or len(rows) == len(selected_row_indices) != 1:
                return ''
            selected_row = rows[selected_row_indices[0]]
            column_value_list = ['_**{}**_: {}'.format(col, selected_row[col]) for col in self._grid_table.columns]
            return '  \n'.join(column_value_list)

    def __init_callback_for_button_visibility__(self):
        @self.app.callback(
            Output(self._my_jobs_start_job_button, 'hidden'),
            [Input(self._data_table_name, 'selected_row_indices')])
        def handle_callback_for_button_visibility(selected_row_indices: list):
            return '' if len(selected_row_indices) == 1 else 'hidden'

    def __get_table_for_jobs__(self):
        self._grid_table = JobTable(self._job_handler)
        rows = self._grid_table.get_rows_for_selected_items()
        min_height = self._grid_table.effective_height_for_display
        return MyDCC.data_table(self._data_table_name, rows, [], min_height=min_height)

