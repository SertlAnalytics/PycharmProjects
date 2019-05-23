"""
Description: This module contains the dash grid table for sales (base classes)
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-16
"""

from sertl_analytics.constants.salesman_constants import SLDC, SLSRC, REGION
from salesman_tutti.tutti_constants import PRCAT
from salesman_system_configuration import SystemConfiguration


class SaleRow:
    sort_column = SLDC.SALE_ID

    def __init__(self, row, columns: list):
        self._row = row
        self._columns = columns
        self._value_dict = self.__get_value_dict_from_row__()

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
    def master_id(self):
        return self._value_dict.get(SLDC.MASTER_ID, '')

    @property
    def region(self):
        return self._value_dict.get(SLDC.REGION, '')

    @property
    def category(self):
        return self._value_dict[SLDC.PRODUCT_CATEGORY]

    @property
    def sub_category(self):
        return self._value_dict[SLDC.PRODUCT_SUB_CATEGORY]

    @property
    def title(self):
        return self._value_dict[SLDC.TITLE]

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



class GridTableSelectionApi:
    def __init__(self):
        self.source = ''
        self.region = ''
        self.category = ''
        self.sub_category = ''
        self.master_id = ''
        self.input = ''

    def print_api_details(self):
        print('Selection_api_details: Source={}, Region={}, Category={}, SubCategory={}'.format(
            self.source, self.region, self.category, self.sub_category))


class MySaleBaseTable:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self._selection_api = None
        self._db = self.sys_config.db
        self._access_layer = self.sys_config.access_layer_sale
        self._columns = self.__get_columns__()
        self._source = self.__get_source__()
        self._source_df = self.__get_source_df__()
        self._source_rows = self.__get_source_rows__()
        self._selected_row_index = -1
        self._selected_row = None
        self._rows = self._source_rows

    @staticmethod
    def __get_source__():
        return SLSRC.DB

    def __get_source_df__(self):
        return self._access_layer.get_my_sales_as_data_frame()

    def __get_source_rows__(self):
        return [self.__get_row_for_source_row__(row) for ind, row in self._source_df.iterrows()]

    @staticmethod
    def __get_columns__():
        return SLDC.get_columns_for_sales_tab_table()

    def __get_row_for_source_row__(self, row):
        return SaleRow(row, self._columns)

    @property
    def columns(self):
        return self._columns

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
    def source(self):
        return self._source

    @property
    def height_for_display(self):
        return 200

    def reset_selected_row(self):
        self._selected_row = None
        self._selected_row_index = -1

    def get_rows_for_selection(self, api: GridTableSelectionApi, with_master_id=False):
        self.__fill_rows_for_selection__(api, with_master_id)
        SaleRow.sort_column = SLDC.SALE_ID
        sort_reverse = False
        sorted_list = sorted(self._rows, reverse=sort_reverse)
        return [row.get_row_as_dict() for row in sorted_list]

    def init_selected_row(self, table_rows: list, selected_row_indices: list=None):
        if selected_row_indices is None or len(selected_row_indices) != 1:  # ToDo: deselect the former selection
            self._selected_row_index = -1
            self._selected_row = None
        else:
            self._selected_row_index = selected_row_indices[0]  # the latest selected is always on position 0
            self._selected_row = table_rows[self._selected_row_index]

    def __fill_rows_for_selection__(self, api: GridTableSelectionApi, with_master_id: bool):
        self._selected_row_index = -1  # no entry selected
        print('__fill_rows_for_selection__:')
        api.print_api_details()
        self._rows = self._source_rows
        if with_master_id:
            self._rows = [row for row in self._rows if row.master_id == api.master_id]
        if api.region not in ['', REGION.GANZE_SCHWEIZ]:
            self._rows = [row for row in self._rows if row.region == api.region]
        if api.category not in ['', PRCAT.ALL]:
            self._rows = [row for row in self._rows if row.category == api.category]
        if api.sub_category not in ['', PRCAT.ALL]:
            self._rows = [row for row in self._rows if row.sub_category == api.sub_category]
        if api.input != '':
            self._rows = [row for row in self._rows if row.title.lower().find(api.input.lower()) > -1]
        # if api.master_id not in ['', 'SEARCH']:
        #     self._rows = [row for row in self._rows if row.master_id == api.master_id]

