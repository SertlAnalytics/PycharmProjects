"""
Description: This module starts the stock database processes (create tables, update data, ...)
CAUTION: This script is NOT saved on git hub.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from pattern_database.stock_database import StockDatabase

stock_db = StockDatabase()
# stock_db.create_pattern_feature_table()
# stock_db.create_process_table()
# stock_db.create_wave_view()
symbol_list = ['MMM', 'NVDA', 'EURUSD', 'BTCUSD']
for symbol in symbol_list:
    print('Index for {}: {}'.format(symbol, stock_db.get_index_for_symbol(symbol)))
