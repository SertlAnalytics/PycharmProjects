"""
Description: This module contains the pattern data factory for delivering data of a certain class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.salesman_constants import SLDC
from sertl_analytics.mymath import MyMath
from sertl_analytics.pybase.data_dictionary import DataDictionary
from salesman_system_configuration import SystemConfiguration


class SalesmanDataDictionary(DataDictionary):
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        DataDictionary.__init__(self)

    @staticmethod
    def __get_rounded_value__(key, value):
        if key in [SLDC.PRICE, SLDC.PRICE_SINGLE, SLDC.PRICE_ORIGINAL]:
            return MyMath.round_smart(value)
        return value

    def is_data_dict_ready_for_sale_table(self):
        for col in self.sys_config.sale_table.column_name_list:
            if col not in self._data_dict:
                print('col not in data_dict: {}'.format(col))
                return False
        return True

    def get_data_list_for_columns(self, columns: list):
        return [self._data_dict[col] for col in columns]

    def get_data_dict_for_columns(self, columns: list):
        return {col: self._data_dict[col] for col in columns}

    def get_data_dict_for_sale_table(self):
        return {col: self._data_dict[col] for col in self.sys_config.sale_table.column_name_list}

