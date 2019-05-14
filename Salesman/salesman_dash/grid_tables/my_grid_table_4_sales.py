"""
Description: This module contains the dash grid table for the tab sales
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-16
"""

from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_dash.grid_tables.my_grid_table_4_sales_base import MySaleBaseTable
import pandas as pd
from salesman_database.access_layer.access_layer_file import MySalesAccessLayerFile


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
        return self.sys_config.access_layer_file.df


class MySaleTable4SimilarSales(MySaleBaseTable):
    @staticmethod
    def __get_source__():
        return SLSRC.DB

    def __get_source_df__(self):
        return self._access_layer.get_similar_sales_as_data_frame()

    @staticmethod
    def __get_columns__():
        return SLDC.get_columns_for_similar_sales_tab_table()

