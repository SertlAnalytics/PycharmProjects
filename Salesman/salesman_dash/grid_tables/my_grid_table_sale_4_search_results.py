"""
Description: This module contains the dash grid table for sales (similar sales)
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-16
"""

from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_dash.grid_tables.my_grid_table_4_sales_base import MySaleBaseTable


class MySearchResultTable(MySaleBaseTable):
    @staticmethod
    def __get_default_source__():
        return [SLSRC.TUTTI_CH]

    def __get_sale_df_dict__(self):
        return {
            SLSRC.DB: self._access_layer.get_similar_sales_as_data_frame(),
        }

    def __get_sale_rows_dict__(self):
        return {key: [self.__get_offer_row_for_source__(key, row) for ind, row in self._sale_df_dict[key].iterrows()]
                for key in self._sale_df_dict}

    @staticmethod
    def __get_sale_columns_dict__():
        return {
            SLSRC.DB: SLDC.get_columns_for_sales_tab_table(),
        }

    def __fill_rows_for_selected_source__(self, master_id: str):
        print('MySearchResultTable.__fill_rows_for_selected_source__')
        self._rows_selected_source = self._sale_rows_dict[self._selected_source]
        if master_id not in ['', 'SEARCH']:
            self._rows_selected_source = [row for row in self._rows_selected_source if row.master_id == master_id]

