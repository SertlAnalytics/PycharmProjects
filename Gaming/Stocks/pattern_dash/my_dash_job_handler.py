"""
Description: This module contains all the scheduled jobs and its handler
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-22
"""

from pattern_scheduling.pattern_job import MyPatternJob
from pattern_scheduling.pattern_scheduler import MyPatternScheduler
from sertl_analytics.constants.pattern_constants import PRD, INDICES, FT
from pattern_database.stock_database import StockDatabase
from pattern_database.stock_database_updater import StockDatabaseUpdater
from pattern_predictor_optimizer import PatternPredictorOptimizer
from sertl_analytics.exchanges.bitfinex import BitfinexConfiguration
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.mydates import MyDate


class MyDashPatternJob(MyPatternJob):
    def __init__(self, start_time: str, stock_db_updater: StockDatabaseUpdater):
        MyPatternJob.__init__(self, period=PRD.DAILY, weekdays=list([0, 1, 2, 3, 4, 5, 6]), start_time=start_time)
        self._stock_db_updater = stock_db_updater


class MyDashTradePolicyUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        self._stock_db_updater.update_trade_policy_metric_for_today(
            [FT.TRIANGLE, FT.TRIANGLE_DOWN, FT.CHANNEL, FT.FIBONACCI_DESC])


class MyDashPredictorOptimizerJob(MyDashPatternJob):
    def __perform_task__(self):
        sys_config = SystemConfiguration()
        predictor_optimizer = PatternPredictorOptimizer(sys_config.db_stock)
        pattern_type_list = [FT.ALL] + sys_config.trade_strategy_optimizer.optimal_pattern_type_list_for_long_trading
        predictor_optimizer.calculate_class_metrics_for_predictor_and_label_for_today(pattern_type_list)


class MyDashDeleteDuplicatesJob(MyDashPatternJob):
    def __perform_task__(self):
        db_stock = StockDatabase()
        db_stock.delete_duplicate_records(db_stock.trade_table)
        db_stock.delete_duplicate_records(db_stock.pattern_table)
        db_stock.delete_duplicate_records(db_stock.wave_table)


class MyDashStockDataUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        db_stock = StockDatabase()
        exchange_config = BitfinexConfiguration()

        db_stock.update_crypto_currencies(PRD.DAILY, symbol_list=exchange_config.ticker_id_list)
        if MyDate.is_tuesday_till_saturday():
            db_stock.update_stock_data_by_index(INDICES.INDICES, PRD.DAILY)
            db_stock.update_stock_data_by_index(INDICES.DOW_JONES, PRD.DAILY)
            db_stock.update_stock_data_for_symbol('FCEL')
            db_stock.update_stock_data_for_symbol('TSLA')
            db_stock.update_stock_data_for_symbol('GE')
            db_stock.update_stock_data_by_index(INDICES.NASDAQ100, PRD.DAILY)


class MyEquityUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        self._stock_db_updater.update_equity_records()


class MyWaveUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        self._stock_db_updater.update_wave_data_by_index_for_daily_period(INDICES.CRYPTO_CCY, 400)
        if MyDate.is_tuesday_till_saturday():
            self._stock_db_updater.update_wave_data_by_index_for_daily_period(INDICES.INDICES, 400)
            self._stock_db_updater.update_wave_data_by_index_for_daily_period(INDICES.DOW_JONES, 400)
            self._stock_db_updater.update_wave_data_by_index_for_daily_period(INDICES.NASDAQ100, 400)

        self._stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.CRYPTO_CCY)
        if MyDate.is_tuesday_till_saturday():
            self._stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.INDICES)
            self._stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.DOW_JONES)
            self._stock_db_updater.update_wave_data_by_index_for_intraday(INDICES.NASDAQ100)

        self._stock_db_updater.add_wave_end_data_to_wave_records(symbol='', ts_start=0, ts_end=0, scheduled_job=True)


class MyPatternUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        self._stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.CRYPTO_CCY)
        if MyDate.is_tuesday_till_saturday():
            self._stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.INDICES)
            self._stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.DOW_JONES)
            self._stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.NASDAQ100)


class MyTradeRecordsUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        self._stock_db_updater.update_trade_records(4, 16)


class MyDashJobHandler:
    def __init__(self, check_interval_min=15, for_test=False):
        self._scheduler = MyPatternScheduler(check_interval_min)
        self._stock_db_updater = StockDatabaseUpdater()
        if for_test:
            self.__add_jobs_for_testing__()
        else:
            self.__add_jobs__()

    def start_scheduler(self):
        self._scheduler.start_scheduler()

    def __add_jobs__(self):
        self._scheduler.add_job(MyDashDeleteDuplicatesJob(start_time='01:00', stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyDashStockDataUpdateJob(start_time='01:30', stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyEquityUpdateJob(start_time='03:00', stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyPatternUpdateJob(start_time='03:15', stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyWaveUpdateJob(start_time='04:00', stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyDashTradePolicyUpdateJob(start_time='05:00', stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyDashPredictorOptimizerJob(
            start_time='05:30', stock_db_updater=self._stock_db_updater))
        # self._scheduler.add_job(MyTradeRecordsUpdateJob(start_time='05:30', stock_db_updater=self._stock_db_updater))

    def __add_jobs_for_testing__(self):
        start_time = self.__get_start_time_for_testing__()
        self._scheduler.add_job(MyDashPredictorOptimizerJob(
            start_time=start_time, stock_db_updater=self._stock_db_updater))

    @staticmethod
    def __get_start_time_for_testing__():
        dt_now = MyDate.get_datetime_object()
        dt_now = MyDate.adjust_by_seconds(dt_now, 10)
        return str(dt_now.time())[:8]
