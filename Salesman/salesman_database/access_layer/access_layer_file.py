"""
Description: This module contains the access layer base class for Salesman
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import pandas as pd
from sertl_analytics.constants.salesman_constants import SLDC


class AccessLayerFile:
    def __init__(self, file_path: str, columns: list):
        self._file_path = file_path
        self._columns = columns
        self._df = self.__get_source_df__()

    @property
    def df(self):
        return self._df

    def get_row(self, row_number: int):
        return self._df.iloc[row_number]

    def get_my_sales_as_dd_options(self, with_refresh=False):
        if with_refresh:
            self._df = self.__get_source_df__()
        option_list = []
        for idx, row in self._df.iterrows():
            label = '{}-{}'.format(row[SLDC.SALE_ID], row[SLDC.TITLE])
            option_list.append({'label': label, 'value': idx})
        return option_list

    def __get_source_df__(self):
        df = pd.read_csv(self._file_path, delimiter='#', header=None)
        df.columns = SLDC.get_columns_for_virtual_sales_in_file()
        return df


class MySalesAccessLayerFile(AccessLayerFile):
    def __init__(self, file_path: str):
        self._file_path = file_path
        AccessLayerFile.__init__(self, file_path, SLDC.get_columns_for_virtual_sales_in_file())

