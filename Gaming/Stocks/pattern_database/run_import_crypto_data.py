"""
Description: This module starts the stock database processes (create tables, update data, ...)
CAUTION: This script is NOT saved on git hub.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, ApiPeriod, ApiOutputsize
from sertl_analytics.constants.pattern_constants import Indices
from pattern_database.stock_database import StockDatabase

stock_db = StockDatabase()
stock_db.update_crypto_currencies(ApiPeriod.DAILY)

