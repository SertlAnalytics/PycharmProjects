"""
Description: This module is the main module for file imports.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""

import pandas as pd


class FileFetcher:
    def __init__(self, file_name: str, **args):
        self.file_name = file_name.lower()
        print(self.file_name)
        self.file_type = self.__get_file_type__()
        self.df = self.__read_file_into_data_frame__(**args)

    def __get_file_type__(self):
        return self.file_name[self.file_name.index('.')+1:]

    def __read_file_into_data_frame__(self, **args):
        """
        :param params: na_values='n/a' (np.nan NumPy not a Number), parse_dates=['col_1', 'col_2']
        :return:
        """
        if self.file_type == 'csv':  # args = na_values='n/a' (np.nan NumPy not a Number), parse_dates=['col_1', 'col_2']
            return pd.read_csv(self.file_name, args)
        elif self.file_type in ['xls', 'xlsx']:  # args = sheetname='Name' or index or sheetname=['sheet1', 'sheet2']
            return pd.read_excel(self.file_name, args)

    def info(self):
        self.df.info()

    def head(self, rows: int = 5):
        self.df.head(rows)




