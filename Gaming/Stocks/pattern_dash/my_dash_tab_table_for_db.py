"""
Description: This module contains the dash table for representing the database tables
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-01
"""

from sertl_analytics.constants.pattern_constants import DC, LOGDC, PRDC, DTRG, TPMDC, EDC, MDC, STBL
import pandas as pd


class DBRow:
    sort_column = DC.ID  # default - will be overwritten during processing

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


class DBTable:
    def __init__(self, df: pd.DataFrame, table: str, date_range: str, column_sort: str):
        self._df = df
        self._table_name = table
        self._date_range = date_range
        self._columns = self._df.columns
        self._sort_column = column_sort
        self._rows = []
        self.__fill_rows_for_selected_table__()

    @property
    def columns(self):
        return self._columns

    @property
    def height_for_display(self):
        height = max(100, 50 + len(self._rows) * 40)
        if height > 400:
            return 400
        return max(100, height)

    def get_rows_for_selected_items(self):
        if len(self._rows) == 0:
            return [DBRow(self._columns).get_row_as_dict()]
        DBRow.sort_column = self._sort_column
        sort_reverse = True
        sorted_list = sorted(self._rows, reverse=sort_reverse)
        return [row.get_row_as_dict() for row in sorted_list]

    @staticmethod
    def get_table_style_cell_conditional() -> list:
        return [{'if': {'column_id': c}, 'textAlign': 'left'} for c in ['Process', 'Comment']]

    def __fill_rows_for_selected_table__(self):
        self._rows = []
        if self._table_name != '':
            for index, row in self._df.iterrows():
                db_row = DBRow(self._columns)
                for column in self._columns:
                    db_row.add_value(column, row[column])
                self._rows.append(db_row)



