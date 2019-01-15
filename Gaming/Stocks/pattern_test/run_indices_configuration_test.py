"""
Description: This module contains tests for both classes IndexConfiguration and IndicesComponentList
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-15
"""

from sertl_analytics.constants.pattern_constants import INDICES, EQUITY_TYPE
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList


indices_component_list = IndicesComponentList.get_ticker_name_dic(INDICES.CRYPTO_CCY)
print(indices_component_list.items())