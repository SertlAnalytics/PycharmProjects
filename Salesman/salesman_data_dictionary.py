"""
Description: This module contains the pattern data factory for delivering data of a certain class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import DC
from sertl_analytics.pybase.data_dictionary import DataDictionary
from salesman_system_configuration import SystemConfiguration


class SalesmanDataDictionary(DataDictionary):
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        DataDictionary.__init__(self)

    @staticmethod
    def __get_rounded_value__(key, value):
        if key in [DC.SLOPE_VOLUME_REGRESSION_PCT, DC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED_PCT,
                   DC.VOLUME_CHANGE_AT_BREAKOUT_PCT,
                   DC.PREVIOUS_PERIOD_HALF_TOP_OUT_PCT, DC.PREVIOUS_PERIOD_FULL_TOP_OUT_PCT,
                   DC.PREVIOUS_PERIOD_HALF_BOTTOM_OUT_PCT, DC.PREVIOUS_PERIOD_FULL_BOTTOM_OUT_PCT]:
            return 1000 if value > 1000 else round(value, -1)
        elif key in [DC.SLOPE_UPPER_PCT, DC.SLOPE_LOWER_PCT, DC.SLOPE_REGRESSION_PCT, DC.SLOPE_BREAKOUT_PCT]:
            return 1000 if value > 1000 else round(value, 0)
        return value

    def is_data_dict_ready_for_sale_table(self):
        for col in self.sys_config.sale_table.column_name_list:
            if col not in self._data_dict:
                print('col not in data_dict: {}'.format(col))
                return False
        return True

    def is_data_dict_ready_for_company_table(self):
        trade_id = self._data_dict.get(DC.ID)
        for col in self.sys_config.company_table.column_name_list:
            if col not in self._data_dict:
                self.sys_config.file_log.log_message(
                    log_message='{}: Col {} not in _data_dict'.format(trade_id, col),
                    process='Save trade', process_step='is_data_dict_ready_for_trade_table')
                return False
        return True

    def is_data_dict_ready_for_columns(self, columns: list):
        for col in columns:
            if col not in self._data_dict:
                return False
        return True

    def get_data_list_for_columns(self, columns: list):
        return [self._data_dict[col] for col in columns]

    def get_data_dict_for_sale_table(self):
        return {col: self._data_dict[col] for col in self.sys_config.sale_table.column_name_list}

    def get_data_dict_for_company_table(self):
        return {col: self._data_dict[col] for col in self.sys_config.company_table.column_name_list}


