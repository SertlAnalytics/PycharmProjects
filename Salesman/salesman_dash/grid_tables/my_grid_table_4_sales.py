"""
Description: This module contains the dash grid table for the tab sales
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-16
"""

from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_dash.grid_tables.my_grid_table_4_sales_base import MySaleBaseTable
import pandas as pd


class MySaleTable4MySales(MySaleBaseTable):
    @staticmethod
    def __get_source__():
        return SLSRC.DB

    def __get_source_df__(self):
        return self._access_layer.get_my_sales_as_data_frame()


class MySaleTable4MyFile(MySaleBaseTable):
    @staticmethod
    def __get_source__():
        return SLSRC.FILE

    def __get_source_df__(self):
        file_path = self.sys_config.file_handler.get_file_path_for_file(self.sys_config.virtual_sales_file_name)
        df = pd.read_csv(file_path, delimiter='#', header=None)
        df.columns = SLDC.get_columns_for_virtual_sales_in_file()
        return df


class MySaleTable4SimilarSales(MySaleBaseTable):
    @staticmethod
    def __get_source__():
        return SLSRC.DB

    def __get_source_df__(self):
        return self._access_layer.get_similar_sales_as_data_frame()

    @staticmethod
    def __get_columns__():
        return SLDC.get_columns_for_similar_sales_tab_table()

