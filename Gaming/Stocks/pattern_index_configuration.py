"""
Description: This module contains the index configuration for pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-20
"""

from sertl_analytics.constants.pattern_constants import INDICES, EQUITY_TYPE
from pattern_database.stock_database import StockDatabase
from pattern_database.stock_access_layer import AccessLayer4Equity
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentFetcher


class IndexConfiguration:
    def __init__(self, db_stock: StockDatabase, indices: list):
        self.db_stock = db_stock
        self._equity_access_layer = AccessLayer4Equity(self.db_stock)
        self._index_list = []
        self._index_ticker_dict = {}
        self._ticker_equity_type_dict = {}
        self.__init_by_indices__(indices)

    def get_ticker_dict_for_index(self, index: str, ticker_id_list=None):
        if index not in self._index_list:
            self.__init_variables_for_index__(index)
        if ticker_id_list is None:
            return self._index_ticker_dict[index]
        return self.__get_ticker_dict_for_index_and_ticker_id_list__(index, ticker_id_list)

    def __get_ticker_dict_for_index_and_ticker_id_list__(self, index: str, ticker_id_list: list):
        dict_all = self._index_ticker_dict[index]
        return {ticker_id: dict_all[ticker_id] for ticker_id in ticker_id_list if ticker_id in dict_all}

    def __init_variables_for_index__(self, index):
        index_dict = self._equity_access_layer.get_index_dict(index)
        if len(index_dict) == 0:
            index_dict = IndicesComponentFetcher.get_ticker_name_dic(index)
        self._index_list.append(index)
        self._index_ticker_dict[index] = index_dict
        self.__add_index_dict_to_symbol_equity_type_dict__(index)

    def get_equity_type_for_symbol(self, symbol: str) -> str:
        if symbol in self._ticker_equity_type_dict:
            return self._ticker_equity_type_dict[symbol]
        return EQUITY_TYPE.SHARE

    def get_index_for_symbol(self, symbol: str) -> str:
        for index in self._index_ticker_dict:
            index_dict = self._index_ticker_dict[index]
            if symbol in index_dict:
                return index
        return INDICES.NONE

    def is_symbol_crypto(self, symbol: str) -> bool:
        if symbol in self._ticker_equity_type_dict:
            return self._ticker_equity_type_dict[symbol] == EQUITY_TYPE.CRYPTO
        return '{}USD'.format(symbol) in self._ticker_equity_type_dict or symbol[-3:] == 'USD'

    def get_indices_as_options(self):
        return [{'label': index, 'value': index} for index in self._index_list]

    def get_values_for_index_list_as_options(self, index_list: list):
        option_list = []
        for index in index_list:
            for key, values in self._index_ticker_dict[index].items():
                option_list.append({'label': values, 'value': key})
        return option_list

    def __init_by_indices__(self, indices: list):
        for index in indices:
            index_dict = self.get_ticker_dict_for_index(index)

    def __add_index_dict_to_symbol_equity_type_dict__(self, index):
        for symbol, name in self._index_ticker_dict[index].items():
            if index == INDICES.CRYPTO_CCY:
                self._ticker_equity_type_dict[symbol] = EQUITY_TYPE.CRYPTO
            else:
                self._ticker_equity_type_dict[symbol] = EQUITY_TYPE.SHARE


