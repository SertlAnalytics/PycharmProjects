"""
Description: This module contains different excel helper classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-05
"""


import xlsxwriter
import xlrd
from sertl_analytics.mydates import MyDate


class MyExcel:
    def __init__(self, file_path: str, sheet_name='Data', with_header=True):
        self._file_path = file_path
        self._sheet_name = sheet_name
        self._with_header = with_header
        self._columns = []
        self._added_rows_per_iteration = 0
        self._number_of_iterations = 0
        self._row_number_actual = 1 if with_header else 0
        self._workbook = xlsxwriter.Workbook(self._file_path)
        self._workbook.add_worksheet(self._sheet_name)
        self._worksheet = self._workbook.get_worksheet_by_name(self._sheet_name)
        
    @property
    def columns(self) -> list:
        return self._columns

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def number_rows(self) -> int:
        return self._row_number_actual - (1 if self._with_header else 0)   # we have to regard the first row number = 0

    def write_header(self, columns: list):       
        self._columns = columns
        for col_number, col_header in enumerate(self._columns):
            self._worksheet.write(0, col_number, col_header)

    def start_iteration(self):
        self._number_of_iterations += 1
        self._added_rows_per_iteration = 0
        
    def write(self, row_number: int, col_number: int, value):
        self._worksheet.write(row_number, col_number, value)
        
    def add_row_by_value_dict(self, col_value_dict: dict):        
        for col_number, col in enumerate(self._columns):
            if col in col_value_dict:               
                self._worksheet.write(self._row_number_actual, col_number, col_value_dict[col])
        self._row_number_actual += 1
        self._added_rows_per_iteration += 1

    def write_next_row(self, row_values: list):
        for col_number, row_value in enumerate(row_values):
            self._worksheet.write(self._row_number_actual, col_number, col_header)
        self._row_number_actual += 1
        self._added_rows_per_iteration += 1
    
    def close(self):        
        self._workbook.close()

    def print_message_after_iteration(self, expected_rows_for_last_iteration: int):
        if expected_rows_for_last_iteration == self._added_rows_per_iteration:
            if self._number_of_iterations == 1:
                print('Success: {} rows written to {}'.format(self._added_rows_per_iteration, self._file_path))
            else:
                print('Success: {} rows written to {} (total written rows: {})'.format(
                    self._added_rows_per_iteration, self._file_path, self.number_rows))
        else:
            print('Error: only {} rows written to {}: expected: {}'.format(
                self._added_rows_per_iteration, self._file_path, expected_rows_for_last_iteration))


