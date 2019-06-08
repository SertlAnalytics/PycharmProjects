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
from pattern_dash.my_dash_tab_dd_for_db import DBDD, DBTabDropDownHandler
from pattern_detection_controller import PatternDetectionController
from pattern_database.stock_access_layer import AccessLayer4Process, AccessLayer4Wave, AccessLayer4Pattern
from dash import Dash
from sertl_analytics.constants.pattern_constants import LOGT, LOGDC, DC, PRDC, STBL, DTRG
from pattern_news_handler import NewsHandler
from pattern_dash.my_dash_tab_table_for_db import DBTable


class MyDashTab4DB(MyPatternDashBaseTab):
    _data_table_name = 'my_db_table'
    _data_table_div = '{}_div'.format(_data_table_name)

    def __init__(self, app: Dash, sys_config: SystemConfiguration):
        MyPatternDashBaseTab.__init__(self, app, sys_config)
        self.sys_config = sys_config
        self._db = self.sys_config.db_stock
        self._pattern_controller = PatternDetectionController(self.sys_config)
        self._dd_handler = DBTabDropDownHandler()
        self._access_layer_process = AccessLayer4Process(self.sys_config.db_stock)
        self._access_layer_wave = AccessLayer4Wave(self.sys_config.db_stock)
        self._access_layer_pattern = AccessLayer4Pattern(self.sys_config.db_stock)
        self._selected_table_name = STBL.PROCESS
        self._selected_limit = 10
        self._selected_date_range = DTRG.TODAY
        self._where_clause_entered = ''
        self._db_table = self._db.get_table_by_name(self._selected_table_name)
        self._df_for_grid_table = None
        self._db_grid_table = None

    def __init_dash_element_ids__(self):
        self._my_db_table_selection = 'my_db_table_selection'
        self._my_db_limit_selection = 'my_db_limit_selection'
        self._my_db_date_range_selection = 'my_db_date_range_selection'
        self._my_db_where_clause_input = 'my_db_where_clause_input'
        self._my_db_query = 'my_db_query'
        self._my_db_entry_markdown = 'my_db_entry_markdown'

    @staticmethod
    def __get_news_handler__():
        return NewsHandler('  \n', '')

    def get_div_for_tab(self):
        children_list = [
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(
                DBDD.TABLE, default_value=self._selected_table_name)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DBDD.LIMIT)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DBDD.DATE_RANGE)),
            MyHTML.span('', margin_left=10),
            MyHTML.div_with_input(element_id=self._my_db_where_clause_input,
                                  placeholder='Please enter where clause...', size=500, height=27),
            MyHTML.div(element_id=self._my_db_query),
            MyHTML.div_with_table(self._data_table_div, self.__get_table_for_db__()),
            MyDCC.markdown(self._my_db_entry_markdown)
        ]
        return MyHTML.div('my_db_div', children_list)

    def init_callbacks(self):
        self.__init_callback_for_db_query__()
        self.__init_callback_for_db_table__()
        self.__init_callback_for_db_markdown__()

    def __init_callback_for_db_table__(self):
        @self.app.callback(
            Output(self._data_table_div, 'children'),
            [Input(self._my_db_query, 'children')])
        def handle_callback_for_db_table(query: str):
            return self.__get_table_for_db__()

    def __init_callback_for_db_query__(self):
        @self.app.callback(
            Output(self._my_db_query, 'children'),
            [Input(self._my_db_table_selection, 'value'),
             Input(self._my_db_limit_selection, 'value'),
             Input(self._my_db_date_range_selection, 'value'),
             Input(self._my_db_where_clause_input, 'n_blur')],
            [State(self._my_db_where_clause_input, 'value')])
        def handle_callback_for_db_table(table: str, limit: int, date_range: str, n_blur: int, where_clause: str):
            if self._selected_table_name != table:
                self._selected_table_name = table
                self._db_table = self._db.get_table_by_name(self._selected_table_name)
            self._selected_limit = limit
            self._selected_date_range = date_range
            self._where_clause_entered = where_clause
            return self.__get_query_for_table__()

    def __init_callback_for_db_markdown__(self):
        @self.app.callback(
            Output(self._my_db_entry_markdown, 'children'),
            [Input(self._data_table_name, 'rows'),
             Input(self._data_table_name, 'selected_row_indices')],
            [State(self._my_db_table_selection, 'value')])
        def handle_callback_for_db_markdown(rows: list, selected_row_indices: list, table: str):
            if len(selected_row_indices) == 0 or len(rows) == len(selected_row_indices) != 1:
                return ''
            selected_row = rows[selected_row_indices[0]]
            column_value_list = ['_**{}**_: {}'.format(col, selected_row[col]) for col in self._db_grid_table.columns]
            return '  \n'.join(column_value_list)

    def __get_table_for_db__(self):
        if self._df_for_grid_table is None:
            return ''
        column_sort = self._db_table.column_sort
        self._db_grid_table = DBTable(
            self._df_for_grid_table, self._selected_table_name, self._selected_date_range, column_sort)
        rows = self._db_grid_table.get_rows_for_selected_items()
        return MyDCC.data_table(
            self._data_table_name, rows,
            columns=self._db_grid_table.columns,
            style_cell_conditional=self._db_grid_table.get_table_style_cell_conditional(),
        )

    def __get_query_for_table__(self):
        where_clause = self.__get_where_clause__()
        if where_clause != '':
            where_clause = " WHERE {}".format(where_clause)
        limit_clause = '' if self._selected_limit == 0 else ' LIMIT {}'.format(self._selected_limit)
        query = "SELECT * from {}{}{}".format(self._selected_table_name, where_clause, limit_clause)
        try:
            self._df_for_grid_table = self._db.select_data_by_query(query)
            return '{}: Found {} records'.format(query, self._df_for_grid_table.shape[0])
        except:
            self._df_for_grid_table = None
            return 'Problem with query: {}'.format(query)

    def __get_where_clause__(self):
        where_clause_from_selected_date_range = self.__get_where_clause_from_selected_date_range__()
        if self._where_clause_entered == '':
            return where_clause_from_selected_date_range
        else:
            if where_clause_from_selected_date_range == '':
                return self._where_clause_entered
            return '{} AND {}'.format(self._where_clause_entered, where_clause_from_selected_date_range)

    def __get_where_clause_from_selected_date_range__(self):
        if self._selected_date_range == '':
            return ''
        column_date = self._db_table.column_date
        column_time_stamp = self._db_table.column_time_stamp
        if column_date != '':
            date_obj = MyDate.get_offset_date_for_date_range(self._selected_date_range)
            if date_obj is not None:
                return "{} >= '{}'".format(column_date, str(date_obj))
        elif column_time_stamp != '':
            offset_time_stamp = MyDate.get_offset_time_stamp_for_date_range(self._selected_date_range)
            if offset_time_stamp > 0:
                return "{} >= {}".format(column_time_stamp, str(offset_time_stamp))
        return ''

