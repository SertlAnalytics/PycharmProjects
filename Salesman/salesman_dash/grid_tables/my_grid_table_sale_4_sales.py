"""
Description: This module contains the dash grid table for sales (my sales)
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-16
"""

from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_dash.grid_tables.my_grid_table_base_4_sales import MySaleBaseTable


class MySaleTable(MySaleBaseTable):
    def __get_sale_df_dict__(self):
        return {
            SLSRC.DB: self._access_layer.get_my_sales_as_data_frame(),
            SLSRC.FILE: self.__get_offer_elements_from_file__()
        }

    def __get_sale_rows_dict__(self):
        return {key: [self.__get_offer_row_for_source__(key, row) for ind, row in self._sale_df_dict[key].iterrows()]
                for key in self._sale_df_dict}

    @staticmethod
    def __get_sale_columns_dict__():
        return {
            SLSRC.DB: SLDC.get_columns_for_sales_tab_table(),
            SLSRC.FILE: SLDC.get_columns_for_virtual_sales_in_file(),
        }

    def __fill_rows_for_selected_source__(self, master_id: str):
        self._rows_selected_source = self._sale_rows_dict[self._selected_source]

