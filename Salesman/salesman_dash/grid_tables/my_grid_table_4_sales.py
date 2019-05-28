"""
Description: This module contains the dash grid table for the tab sales
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-16
"""

from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_dash.grid_tables.my_grid_table_4_sales_base import MySaleBaseTable, GridTableSelectionApi, SaleRow
from salesman_system_configuration import SystemConfiguration
from salesman_result_data_handler import SalesmanResultDataHandler
from salesman_sale import SalesmanSale
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
        return self.sys_config.access_layer_file.df


class MySaleTable4SimilarSales(MySaleBaseTable):
    def __init__(self, sys_config: SystemConfiguration):
        MySaleBaseTable.__init__(self, sys_config)
        self._result_data_handler = SalesmanResultDataHandler(sys_config, self._source_df)

    @property
    def plot_categories(self):
        return self._result_data_handler.plot_categories

    @property
    def df_for_plot(self) -> pd.DataFrame:
        return self._result_data_handler.df_for_plot

    @property
    def sale_master(self) -> SalesmanSale:
        return self._result_data_handler.sale_master

    @property
    def result_data_handler(self) -> SalesmanResultDataHandler:
        return self._result_data_handler

    def __fill_rows_for_selection__(self, api: GridTableSelectionApi, with_master_id: bool):
        print('__fill_rows_for_selection__:')
        api.print_api_details()
        self._selected_row_index = -1  # no entry selected
        if len(api.entity_values) == 0:
            self._result_data_handler.init_by_sale_master(api.master_sale)
        self._result_data_handler.adjust_result_to_selected_entities(api.entity_values)
        if self._result_data_handler.df_for_grid is None:
            self._rows = []
        else:
            self._rows = [SaleRow(row, self.columns) for idx, row in self._result_data_handler.df_for_grid.iterrows()]

    @staticmethod
    def __get_source__():
        return SLSRC.DB

    def __get_source_df__(self):
        return self._access_layer.get_similar_sales_as_data_frame()

    @staticmethod
    def __get_columns__():
        return SLDC.get_columns_for_similar_sales_tab_table()

