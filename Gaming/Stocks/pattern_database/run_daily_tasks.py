"""
Description: This module deletes duplicate entries within the trade and pattern table.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-05
"""
from sertl_analytics.constants.pattern_constants import PRD, INDICES
from pattern_database.stock_database import StockDatabase, PatternTable, TradeTable
from pattern_database.stock_database_updater import StockDatabaseUpdater
from datetime import date, datetime

stock_db = StockDatabase()
stock_db_updater = StockDatabaseUpdater()
pattern_table = PatternTable()
trade_table = TradeTable()

process_single_ticker_id = False

# stock_db_updater.update_trade_records(16, 16)

if process_single_ticker_id:
    stock_db_updater.update_wave_records_for_daily_period('AAPL', 400)
else:
    is_weekday = datetime.today().weekday() in [1, 2, 3, 4, 5]  # tuesday till saturday => update stock data as well

    stock_db.delete_duplicate_records(trade_table)
    stock_db.delete_duplicate_records(pattern_table)
    stock_db.update_crypto_currencies(PRD.DAILY)
    #
    if is_weekday:
        stock_db.update_stock_data_by_index(INDICES.DOW_JONES, PRD.DAILY)
        stock_db.update_stock_data_for_symbol('FCEL')
        stock_db.update_stock_data_for_symbol('TSLA')
        stock_db.update_stock_data_for_symbol('GE')
        #
        stock_db.update_stock_data_by_index(INDICES.NASDAQ100, PRD.DAILY)

    # print(stock_db.get_wave_counter_dict(400))

    stock_db_updater.update_wave_data_by_index_for_daily_period(INDICES.CRYPTO_CCY, 400)
    if is_weekday:
        stock_db_updater.update_wave_data_by_index_for_daily_period(INDICES.DOW_JONES, 400)
        stock_db_updater.update_wave_data_by_index_for_daily_period(INDICES.NASDAQ100, 400)

    stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.CRYPTO_CCY)
    if is_weekday:
        stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.DOW_JONES)
        stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.NASDAQ100)

    stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.CRYPTO_CCY)
    if is_weekday:
        stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.DOW_JONES)
        stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.NASDAQ100)

    if is_weekday:
        stock_db_updater.update_trade_records(16, 16)


