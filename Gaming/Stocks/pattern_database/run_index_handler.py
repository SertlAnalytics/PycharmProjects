"""
Description: This module starts the stock database processes (create tables, update data, ...)
CAUTION: This script is NOT saved on git hub.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from pattern_database.stock_database import StockDatabase
from pattern_database.stock_index_handler import IndexHandler
from sertl_analytics.constants.pattern_constants import INDICES

stock_db = StockDatabase()
index_handler = IndexHandler(index=INDICES.Q_FSE, db_stock=stock_db)

