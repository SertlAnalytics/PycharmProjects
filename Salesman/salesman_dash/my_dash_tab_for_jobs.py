"""
Description: This module contains the dash tab for database tables
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-06
"""

from dash.dependencies import Input, Output, State
from sertl_analytics.mydash.my_dash_base_tab import MyDashBaseTab
from salesman_database.salesman_db import SalesmanDatabase
from sertl_analytics.mydash.my_dash_components import MyDCC, MyHTML
from salesman_dash.my_dash_tab_dd_for_jobs import JobsTabDropDownHandler
from salesman_database.access_layer.access_layer_others import AccessLayer4Process
from dash import Dash
from sertl_analytics.constants.pattern_constants import STBL, DTRG, JDC
from sertl_analytics.constants.my_constants import DSHVT
from salesman_dash.my_dash_tab_table_for_jobs import JobTable
from salesman_dash.my_dash_job_handler import MyDashJobHandler
from salesman_scheduling.salesman_process_manager import SalesmanProcessManager
from salesman_tutti.tutti import Tutti
import pandas as pd


class MyDashTab4Jobs(MyDashBaseTab):
    _data_table_name = 'my_jobs_table'
    _data_table_div = '{}_div'.format(_data_table_name)

    def __init__(self, app: Dash, tutti: Tutti):
        MyDashBaseTab.__init__(self, app)
        self._job_handler = MyDashJobHandler(SalesmanProcessManager(), tutti)
        self._tutti = tutti
        self.__init_dash_element_ids__()
        self._db = SalesmanDatabase()
        self._dd_handler = JobsTabDropDownHandler()
        self._access_layer_process = AccessLayer4Process(self._db)
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

    def get_div_for_tab(self):
        children_list = [
            self.__get_embedded_div_for_last_run_and_start_job_button__(),
            MyHTML.div_with_table(self._data_table_div, self.__get_table_for_jobs__()),
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
            Output(self._my_jobs_last_check_value_div, DSHVT.CHILDREN),
            [Input('my_interval_refresh', DSHVT.N_INTERVALS)])
        def handle_callback_for_last_check_value_div(n_intervals: int):
            self._job_handler.check_scheduler_tasks()
            return self._job_handler.last_run_date_time

    def __init_callback_for_jobs_table__(self):
        @self.app.callback(
            Output(self._data_table_div, DSHVT.CHILDREN),
            [Input(self._my_jobs_last_check_value_div, DSHVT.CHILDREN),
             Input(self._my_jobs_start_job_button, DSHVT.N_CLICKS)],
            [State(self._data_table_name, DSHVT.ROWS),
             State(self._data_table_name, DSHVT.SELECTED_ROW_INDICES)])
        def handle_callback_for_jobs_table(last_check_value: str, n_clicks_refresh: int,
                                           rows: list, selected_row_indices: list):
            if self._n_clicks_refresh != n_clicks_refresh\
                    and selected_row_indices is not None and len(selected_row_indices) > 0:
                selected_job_row = rows[selected_row_indices[0]]
                job_name = selected_job_row[JDC.NAME]
                self._job_handler.start_job_manually(job_name)
                print('Start job manually: {}'.format(job_name))
            return self.__get_table_for_jobs__()

    def __init_callback_for_jobs_markdown__(self):
        @self.app.callback(
            Output(self._my_jobs_entry_markdown, DSHVT.CHILDREN),
            [Input(self._data_table_name, DSHVT.ROWS),
             Input(self._data_table_name, DSHVT.SELECTED_ROW_INDICES)])
        def handle_callback_for_jobs_markdown(rows: list, selected_row_indices: list):
            if selected_row_indices is None or len(selected_row_indices) == 0:
                return ''
            selected_row = rows[selected_row_indices[0]]
            column_value_list = ['_**{}**_: {}'.format(col, selected_row[col]) for col in self._grid_table.columns]
            return '  \n'.join(column_value_list)

    def __init_callback_for_button_visibility__(self):
        @self.app.callback(
            Output(self._my_jobs_start_job_button, DSHVT.HIDDEN),
            [Input(self._data_table_name, DSHVT.SELECTED_ROW_INDICES)])
        def handle_callback_for_button_visibility(selected_row_indices: list):
            return 'hidden' if selected_row_indices is None or len(selected_row_indices) == 0 else ''

    def __get_table_for_jobs__(self):
        self._grid_table = JobTable(self._job_handler)
        rows = self._grid_table.get_rows_for_selected_items()
        min_height = self._grid_table.height_for_display
        # return 'len={}, type={}, \n{}'.format(len(rows), type(rows), rows)
        df = pd.DataFrame.from_dict(rows)
        df = df[self._grid_table.columns]
        return MyDCC.data_table(self._data_table_name, rows, columns=self._grid_table.columns, min_height=min_height)

