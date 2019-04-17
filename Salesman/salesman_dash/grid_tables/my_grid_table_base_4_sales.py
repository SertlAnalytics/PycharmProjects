"""
Description: This module contains the dash grid table for sales (base classes)
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-16
"""

from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_database.access_layer.access_layer_sale import AccessLayer4Sale
from salesman_system_configuration import SystemConfiguration
import pandas as pd


class SaleRow:
    sort_column = SLDC.SALE_ID

    def __init__(self, row):
        self._row = row
        self._columns = self.__get_columns__()
        self._value_dict = self.__get_value_dict_from_row__()

    @staticmethod
    def __get_columns__():
        return SLDC.get_columns_for_sales_tab_table()

    def __get_value_dict_from_row__(self) -> dict:
        return_dict = {}
        for col in self.columns:
            return_dict[col] = ''  # default
            if col in self._row:
                return_dict[col] = self._row[col]
        return return_dict

    @property
    def value_dict(self):
        return self._value_dict

    @property
    def columns(self):
        return self._columns

    @property
    def sale_id(self):
        return self._value_dict[SLDC.SALE_ID]

    @property
    def source(self):
        return self._value_dict[SLDC.SOURCE]

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


class SaleRowFromDB(SaleRow):
    @property
    def master_id(self):
        return self._value_dict[SLDC.MASTER_ID]

    @staticmethod
    def __get_columns__():
        return SLDC.get_columns_for_sales_tab_table()


class SaleRowFromFile(SaleRow):
    @staticmethod
    def __get_columns__():
        return SLDC.get_columns_for_virtual_sales_in_file()


class MySaleBaseTable:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self._db = self.sys_config.db
        self._access_layer = AccessLayer4Sale(self._db)
        self._selected_source = self.__get_default_source__()
        self._sale_df_dict = self.__get_sale_df_dict__()
        self._sale_rows_dict = self.__get_sale_rows_dict__()
        self._sale_columns_dict = self.__get_sale_columns_dict__()
        self._selected_row_index = -1
        self._selected_row = None
        self._rows_selected_source = []

    @staticmethod
    def __get_default_source__():
        return SLSRC.DB

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

    @staticmethod
    def __get_offer_row_for_source__(source: str, row):
        if source == SLSRC.FILE:
            return SaleRowFromFile(row)
        return SaleRowFromDB(row)

    @property
    def columns(self):
        return self._sale_columns_dict.get(self._selected_source, [])

    @property
    def selected_row_index(self):
        return self._selected_row_index

    @selected_row_index.setter
    def selected_row_index(self, idx: int):
        self._selected_row_index = idx

    @property
    def selected_row(self):
        return self._selected_row

    @selected_row.setter
    def selected_row(self, row):
        self._selected_row = row

    @property
    def selected_source(self):
        return self._selected_source

    @selected_source.setter
    def selected_source(self, value):
        self._selected_source = value

    @property
    def height_for_display(self):
        return 400

    def reset_selected_row(self):
        self._selected_row = None
        self._selected_row_index = -1

    def get_rows_for_selected_source(self, master_id=''):
        self.__update_rows_for_selected_source__(master_id)
        SaleRow.sort_column = SLDC.SALE_ID
        sort_reverse = False
        sorted_list = sorted(self._rows_selected_source, reverse=sort_reverse)
        return [row.get_row_as_dict() for row in sorted_list]

    def init_selected_row(self, table_rows: list, selected_row_indices: list=None):
        if selected_row_indices is None or len(selected_row_indices) != 1:  # ToDo: deselect the former selection
            self._selected_row_index = -1
            self._selected_row = None
        else:
            self._selected_row_index = selected_row_indices[0]  # the latest selected is always on position 0
            self._selected_row = table_rows[self._selected_row_index]

    def __get_offer_elements_from_file__(self) -> pd.DataFrame:
        file_path = self.sys_config.file_handler.get_file_path_for_file(self.sys_config.virtual_sales_file_name)
        df = pd.read_csv(file_path, delimiter='#', header=None)
        df.columns = SLDC.get_columns_for_virtual_sales_in_file()
        return df

    def __update_rows_for_selected_source__(self, master_id: str):
        self._selected_row_index = -1  # no entry selected
        print('master_id={}'.format(master_id))
        self.__fill_rows_for_selected_source__(master_id)

    def __fill_rows_for_selected_source__(self, master_id: str):
        pass


