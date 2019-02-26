"""
Description: This module contains the data dictionaries for stock tables.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""
from sertl_analytics.pybase.data_dictionary import DataDictionary
from pattern_database.stock_tables import WaveTable, AssetTable
from sertl_analytics.constants.pattern_constants import DC, EQUITY_TYPE
from sertl_analytics.exchanges.exchange_cls import Balance


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
        self.add(DC.WAVE_END_FLAG, -1)
        self.add(DC.WAVE_MAX_RETR_PCT, 0)
        self.add(DC.WAVE_MAX_RETR_TS_PCT, 0)
        self.add(DC.FC_TS, 0)
        self.add(DC.FC_DT, '')
        self.add(DC.FC_C_WAVE_END_FLAG, -1)
        self.add(DC.FC_C_WAVE_MAX_RETR_PCT, 0)
        self.add(DC.FC_C_WAVE_MAX_RETR_TS_PCT, 0)
        self.add(DC.FC_R_WAVE_END_FLAG, -1)
        self.add(DC.FC_R_WAVE_MAX_RETR_PCT, 0)
        self.add(DC.FC_R_WAVE_MAX_RETR_TS_PCT, 0)


class AssetDataDictionary(DataDictionaryWithTable):
    @staticmethod
    def __get_target_table_columns__() -> list:
        return AssetTable().column_name_list

    def get_data_dict_for_target_table_for_balance(self, balance: Balance, validity_ts: int, validity_dt: str):
        self._data_dict = {}
        self.add(DC.VALIDITY_DT, validity_dt)
        self.add(DC.VALIDITY_TS, validity_ts)
        self.add(DC.LOCATION, 'Bitfinex')
        if balance.asset == 'USD':
            self.add(DC.EQUITY_TYPE, EQUITY_TYPE.CASH)
            self.add(DC.EQUITY_TYPE_ID, EQUITY_TYPE.get_id(EQUITY_TYPE.CASH))
        else:
            self.add(DC.EQUITY_TYPE, EQUITY_TYPE.CRYPTO)
            self.add(DC.EQUITY_TYPE_ID, EQUITY_TYPE.get_id(EQUITY_TYPE.CRYPTO))
        self.add(DC.EQUITY_ID, balance.asset)
        self.add(DC.EQUITY_NAME, balance.asset)
        self.add(DC.QUANTITY, balance.amount)
        self.add(DC.VALUE_PER_UNIT, 0)
        self.add(DC.VALUE_TOTAL, balance.current_value)
        self.add(DC.CURRENCY, 'USD')
        return self.get_data_dict_for_target_table()