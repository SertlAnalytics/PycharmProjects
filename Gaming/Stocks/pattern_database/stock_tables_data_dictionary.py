"""
Description: This module contains the data dictionaries for stock tables.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""
from sertl_analytics.pybase.data_dictionary import DataDictionary
from pattern_database.stock_tables import WaveTable
from sertl_analytics.constants.pattern_constants import DC


class DataDictionaryWithTable(DataDictionary):
    def __init__(self):
        self._target_table_columns = self.__get_target_table_columns__()
        DataDictionary.__init__(self)

    def is_data_dict_ready_for_target_table(self):
        for col in self._target_table_columns:
            if col not in self._data_dict:
                return False
        return True

    def get_data_dict_for_target_table(self):
        return {col: self._data_dict[col] for col in self._target_table_columns}

    @staticmethod
    def __get_target_table_columns__() -> list:
        return []


class WaveDataDictionary(DataDictionaryWithTable):
    @staticmethod
    def __get_target_table_columns__() -> list:
        return WaveTable().column_name_list

    def __init_data_dict__(self):
        self.add(DC.PARENT_WAVE_OID, 0)
        self.add(DC.WAVE_IN_PARENT , '')