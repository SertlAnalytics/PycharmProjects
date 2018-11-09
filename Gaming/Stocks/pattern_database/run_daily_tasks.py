"""
Description: This module deletes duplicate entries within the trade and pattern table.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-05
"""
from sertl_analytics.constants.pattern_constants import PRD, Indices
from pattern_database.stock_database import StockDatabase, PatternTable, TradeTable

stock_db = StockDatabase()
pattern_table = PatternTable()
trade_table = TradeTable()

# stock_db.delete_duplicate_records(trade_table)
# stock_db.delete_duplicate_records(pattern_table)
# stock_db.update_crypto_currencies(PRD.DAILY)
#
# stock_db.update_stock_data_by_index(Indices.DOW_JONES, PRD.DAILY)
# stock_db.update_stock_data_for_symbol('FCEL')
# stock_db.update_stock_data_for_symbol('TSLA')
# stock_db.update_stock_data_for_symbol('GE')

stock_db.update_stock_data_by_index(Indices.NASDAQ100, PRD.DAILY)