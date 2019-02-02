"""
Description: This module contains the class to fetch file names and delivers as Excel sheet.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-30
"""

import os
import xlwt


class FileNameFetcher:
    def __init__(self, path: str, file_name: str, tab_name: str, file_extension=''):
        self._path = path.lower()
        self._excel_file_name = file_name
        self._excel_tab_name = tab_name
        self._process_directory__()

    def _process_directory__(self):
        file_list = self.__get_file_name_list__()
        self.__write_to_excel__(file_list)

    def __get_file_name_list__(self) -> list:
        return [file for file in os.listdir(self._path)]

    def __write_to_excel__(self, input_list: list):
        book = xlwt.Workbook(encoding="utf-8")
        sheet1 = book.add_sheet(self._excel_tab_name)

        for index, entry in enumerate(input_list):
            sheet1.write(index, 0, entry)

        book.save(self._excel_file_name)

        print('Done - {} entries written to {}'.format(len(input_list), self._excel_file_name))


file_name_fetcher = FileNameFetcher('D:/Backup/svg/', 'File_Names.xls', 'Files')







