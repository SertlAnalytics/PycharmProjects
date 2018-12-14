"""
Description: This module contains the index configuration for pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-20
"""

from sertl_analytics.constants.pattern_constants import INDICES, EQUITY_TYPE
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList


class IndexConfiguration:
    def __init__(self, index_list: list):
        self.index_list = index_list
        self.index_dict = {index: IndicesComponentList.get_ticker_name_dic(index) for index in self.index_list}
        self._symbol_equity_type_dict = self.__get_symbol_equity_type_dict__()

    def get_equity_type_for_symbol(self, symbol: str) -> str:
        if symbol in self._symbol_equity_type_dict:
            return self._symbol_equity_type_dict[symbol]
        return EQUITY_TYPE.SHARE

    def is_symbol_crypto(self, symbol: str) -> bool:
        if symbol in self._symbol_equity_type_dict:
            return self._symbol_equity_type_dict[symbol] == EQUITY_TYPE.CRYPTO
        return '{}USD'.format(symbol) in self._symbol_equity_type_dict or symbol[-3:] == 'USD'

    def get_indices_as_options(self):
        return [{'label': index, 'value': index} for index in self.index_list]

    def get_values_for_index_list_as_options(self, index_list: list):
        option_list = []
        for index in index_list:
            for key, values in self.index_dict[index].items():
                option_list.append({'label': values, 'value': key})
        return option_list

    def __get_symbol_equity_type_dict__(self) -> dict:
        return_dict = {}
        for index in self.index_list:
            for symbol in self.index_dict[index]:
                return_dict[symbol] = EQUITY_TYPE.CRYPTO if index == INDICES.CRYPTO_CCY else EQUITY_TYPE.SHARE
        return return_dict


