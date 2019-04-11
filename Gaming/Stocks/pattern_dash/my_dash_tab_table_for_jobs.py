"""
Description: This module contains the dash table for representing the database tables
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-01
"""

from sertl_analytics.constants.pattern_constants import JDC
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

    def __fill_rows_for_selected_table__(self):
        self._rows = []
        for job in self._job_handler.job_list:
            db_row = JobRow(self._columns)
            job_data_dict = job.get_data_dict_for_job_table_rows(self._columns)
            for column in job_data_dict:
                db_row.add_value(column, job_data_dict[column])
            self._rows.append(db_row)



