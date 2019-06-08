"""
Description: This module contains the dash table for representing the database tables
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-01
"""

from sertl_analytics.constants.pattern_constants import JDC
from sertl_analytics.mydates import MyDate
from pattern_dash.my_dash_job_handler import MyDashJobHandler


class JobRow:
    sort_column = JDC.NAME

    def __init__(self, columns: list):
        self._columns = columns
        self._value_dict = {col: '' for col in self._columns}

    @property
    def value_dict(self):
        return self._value_dict

    @property
    def columns(self):
        return self._columns

    def add_value(self, column: str, value):
        self._value_dict[column] = value

    def get_row_as_dict(self):
        return self._value_dict

    def __eq__(self, other):
        return self._value_dict[self.sort_column] == other.value_dict[self.sort_column]

    def __lt__(self, other):
        return self._value_dict[self.sort_column] < other.value_dict[self.sort_column]

    def __gt__(self, other):
        return self._value_dict[self.sort_column] < other.value_dict[self.sort_column]


class JobTable:
    def __init__(self, job_handler: MyDashJobHandler):
        self._job_handler = job_handler
        self._columns = JDC.get_columns_for_job_table()
        self._sort_column = JDC.NAME
        self._rows = []
        self.__fill_rows_for_selected_table__()

    @property
    def columns(self):
        return self._columns

    @property
    def height_for_display(self):
        height = max(100, self.effective_height_for_display)
        if height > 400:
            return 400
        return max(100, height)

    @property
    def effective_height_for_display(self):
        return 50 + len(self._rows) * 40

    def get_rows_for_selected_items(self):
        if len(self._rows) == 0:
            return [JobRow(self._columns).get_row_as_dict()]
        JobRow.sort_column = self._sort_column
        sort_reverse = False
        sorted_list = sorted(self._rows, reverse=sort_reverse)
        return [row.get_row_as_dict() for row in sorted_list]

    @staticmethod
    def get_table_style_cell_conditional() -> list:
        # ['Name', 'Start times', 'Next start', 'Last start', 'Runtime (sec.)', 'pro/ins/upd/del', 'Weekdays']
        return [{'if': {'column_id': c}, 'textAlign': 'left'} for c in ['Name', 'Weekdays']]

    def get_table_style_data_conditional(self, rows: list):
        # ['Name', 'Start times', 'Next start', 'Last start', 'Runtime (sec.)', 'pro/ins/upd/del', 'Weekdays']
        idx_running_list = [idx for idx, row in enumerate(rows) if row['Runtime (sec.)'] == '- running -']
        idx_nearest_next = self.__get_idx_for_nearest_next_run__(rows)
        style_list = []
        for idx in idx_running_list:
            style_list.append({'if': {'row_index': idx}, 'backgroundColor': 'orange', 'color': 'white'})
        style_list.append({'if': {'row_index': idx_nearest_next}, 'backgroundColor': 'yellow'})
        return style_list

    @staticmethod
    def __get_idx_for_nearest_next_run__(rows: list) -> int:
        time_now = MyDate.get_time_str_from_datetime()[:5]
        time_smallest = time_now
        time_nearest_next = '24:00'
        idx_smallest = -1
        idx_nearest_next = -1
        for idx, row in enumerate(rows):
            time_row = row['Next start']
            if time_row < time_smallest:
                time_smallest = time_row
                idx_smallest = idx
            if time_now <= time_row < time_nearest_next:
                time_nearest_next = time_row
                idx_nearest_next = idx
        return idx_nearest_next if idx_nearest_next != -1 else idx_smallest

    def __fill_rows_for_selected_table__(self):
        self._rows = []
        for job in self._job_handler.job_list:
            db_row = JobRow(self._columns)
            job_data_dict = job.get_data_dict_for_job_table_rows(self._columns)
            for column in job_data_dict:
                db_row.add_value(column, job_data_dict[column])
            self._rows.append(db_row)



