"""
Description: This module deletes duplicate entries within the trade and pattern table.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-05
"""
from sertl_analytics.constants.pattern_constants import PRD, INDICES, FT
from pattern_database.stock_database import StockDatabase, PatternTable, TradeTable, WaveTable
from pattern_database.stock_database_updater import StockDatabaseUpdater
from pattern_predictor_optimizer import PatternPredictorOptimizer
from sertl_analytics.exchanges.bitfinex import BitfinexConfiguration
from pattern_system_configuration import SystemConfiguration
from datetime import date, datetime
from sertl_analytics.mydates import MyDate

sys_config = SystemConfiguration()
stock_db = sys_config.db_stock
exchange_config = BitfinexConfiguration()
predictor_optimizer = PatternPredictorOptimizer(stock_db)
stock_db_updater = StockDatabaseUpdater(sys_config)

stock_db.update_stock_data_by_index(INDICES.INDICES, PRD.DAILY)

if True:
    # stock_db_updater.fill_asset_gaps(1545498000, 1546297200, 21600)
    # stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.CRYPTO_CCY)
    # stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.DOW_JONES)
    # stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.NASDAQ100)
    # stock_db_updater.complete_wave_records(symbol='', ts_start=0, ts_end=0)
    # stock_db_updater.update_trade_policy_metric_for_today(
    #     [FT.TRIANGLE, FT.TRIANGLE_DOWN, FT.CHANNEL, FT.FIBONACCI_DESC])
    pass
    # stock_db.update_crypto_currencies(PRD.DAILY, symbol_list=exchange_config.ticker_id_list)
    # stock_db_updater.add_wave_prediction_data_to_wave_records(symbol='')
    # stock_db_updater.update_trade_records(4, 16)
    # stock_db_updater.update_trade_policy_metric_for_today(
    #     [FT.TRIANGLE, FT.TRIANGLE_DOWN, FT.CHANNEL, FT.FIBONACCI_DESC])
    # stock_db_updater.update_trade_policy_metric_for_today([FT.TRIANGLE, FT.TRIANGLE_DOWN, FT.CHANNEL, FT.FIBONACCI_DESC])
    # stock_db_updater.update_equity_records()
    # stock_db.update_crypto_currencies(PRD.DAILY, symbol_list=exchange_config.ticker_id_list)
    # stock_db_updater.update_wave_records_for_daily_period('AAPL', 400)
else:
    if MyDate.is_sunday():
        stock_db_updater.update_trade_policy_metric_for_today(
            [FT.TRIANGLE, FT.TRIANGLE_DOWN, FT.CHANNEL, FT.FIBONACCI_DESC])
    pattern_type_list = [FT.ALL] + sys_config.trade_strategy_optimizer.optimal_pattern_type_list_for_long_trading
    predictor_optimizer.calculate_class_metrics_for_predictor_and_label_for_today(pattern_type_list)

    stock_db.delete_duplicate_records(stock_db.trade_table)
    stock_db.delete_duplicate_records(stock_db.pattern_table)
    stock_db.delete_duplicate_records(stock_db.wave_table)

    stock_db.update_crypto_currencies(PRD.DAILY, symbol_list=exchange_config.ticker_id_list)

    if MyDate.is_tuesday_till_saturday():
        stock_db.update_stock_data_by_index(INDICES.INDICES, PRD.DAILY)
        stock_db.update_stock_data_by_index(INDICES.DOW_JONES, PRD.DAILY)
        stock_db.update_stock_data_for_symbol('FCEL')
        stock_db.update_stock_data_for_symbol('TSLA')
        stock_db.update_stock_data_for_symbol('GE')
        stock_db.update_stock_data_by_index(INDICES.NASDAQ100, PRD.DAILY)
    else:
        stock_db_updater.update_equity_records()

    # print(stock_db.get_wave_counter_dict(PRD.DAILY, 400))

    stock_db_updater.update_wave_data_by_index_for_daily_period(INDICES.CRYPTO_CCY, 400)
    if MyDate.is_tuesday_till_saturday():
        stock_db_updater.update_wave_data_by_index_for_daily_period(INDICES.INDICES, 400)
        stock_db_updater.update_wave_data_by_index_for_daily_period(INDICES.DOW_JONES, 400)
        stock_db_updater.update_wave_data_by_index_for_daily_period(INDICES.NASDAQ100, 400)

    stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.CRYPTO_CCY)
    if MyDate.is_tuesday_till_saturday():
        stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.INDICES)
        stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.DOW_JONES)
        stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.NASDAQ100)

    stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.CRYPTO_CCY)
    if MyDate.is_tuesday_till_saturday():
        stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.INDICES)
        stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.DOW_JONES)
        stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.NASDAQ100)

    stock_db_updater.update_trade_policy_metric_for_today(
        [FT.TRIANGLE, FT.TRIANGLE_DOWN, FT.CHANNEL, FT.FIBONACCI_DESC])

    # if is_weekday:
    #     stock_db_updater.update_trade_records(4, 16)


