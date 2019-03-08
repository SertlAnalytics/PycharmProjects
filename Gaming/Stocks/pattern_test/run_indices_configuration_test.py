"""
Description: This module contains tests for both classes IndexConfiguration and IndicesComponentFetcher
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-15
"""

from sertl_analytics.constants.pattern_constants import INDICES, EQUITY_TYPE
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentFetcher
from pattern_index_configuration import IndexConfiguration
from pattern_database.stock_database import StockDatabase


# indices_component_list = IndicesComponentFetcher.get_ticker_name_dic(INDICES.CRYPTO_CCY)
# print(indices_component_list.items())

index_configuration = IndexConfiguration(StockDatabase(), INDICES.get_index_list_for_index_configuration())
symbol = 'MMM'
index = index_configuration.get_index_for_symbol(symbol)
print('Index for symbol {}={}'.format(symbol, index))