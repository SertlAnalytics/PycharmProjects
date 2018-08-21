"""
Description: This module starts the stock database processes (update data, ...)
CAUTION: This script is NOT saved on git hub.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod
from sertl_analytics.constants.pattern_constants import Indices
from pattern_database.stock_database import StockDatabase

stock_db = StockDatabase()
# _stock_db.update_stock_data_by_index(Indices.DOW_JONES, ApiPeriod.DAILY)
# _stock_db.update_stock_data_by_index(Indices.NASDAQ100, ApiPeriod.DAILY)
# _stock_db.update_stock_data_for_symbol('MMM')
stock_db.update_stock_data_by_index(Indices.DOW_JONES, ApiPeriod.DAILY)
stock_db.update_stock_data_for_symbol('FCEL')
stock_db.update_stock_data_for_symbol('TSLA')
