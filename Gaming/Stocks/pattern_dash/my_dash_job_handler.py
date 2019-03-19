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
    def __init__(self, weekdays: list, start_times: list, stock_db_updater: StockDatabaseUpdater):
        MyPatternJob.__init__(self, period=PRD.DAILY, weekdays=weekdays, start_times=start_times)
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
            db_stock.update_stock_data_by_index(INDICES.FOREX, PRD.DAILY)
            db_stock.update_stock_data_by_index(INDICES.DOW_JONES, PRD.DAILY)
            db_stock.update_stock_data_for_symbol('FCEL')
            db_stock.update_stock_data_for_symbol('TSLA')
            db_stock.update_stock_data_for_symbol('GE')
            db_stock.update_stock_data_by_index(INDICES.NASDAQ100, PRD.DAILY)


class MyEquityUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        result_obj = self._stock_db_updater.update_equity_records()


class MyDailyWaveUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        index_list = [INDICES.CRYPTO_CCY, INDICES.FOREX, INDICES.DOW_JONES, INDICES.NASDAQ100]
        for index in index_list:
            if index == INDICES.CRYPTO_CCY or MyDate.is_tuesday_till_saturday():
                self._stock_db_updater.update_wave_data_by_index_for_daily_period(index, 400)
        self._stock_db_updater.add_wave_end_data_to_wave_records(symbol='', ts_start=0, ts_end=0, scheduled_job=True)


class MyIntradayWaveUpdateJob(MyDashPatternJob):
    @property
    def index_list(self):
        return [INDICES.CRYPTO_CCY, INDICES.FOREX, INDICES.DOW_JONES, INDICES.NASDAQ100]

    def __perform_task__(self):
        for index in self.index_list:
            self._stock_db_updater.update_wave_data_by_index_for_intraday(index)
        self._stock_db_updater.add_wave_end_data_to_wave_records(symbol='', ts_start=0, ts_end=0, scheduled_job=True)


class MyIntradayWaveUpdateJobForCrypto(MyIntradayWaveUpdateJob):
    @property
    def index_list(self):
        return [INDICES.CRYPTO_CCY]


class MyIntradayWaveUpdateJobForShares(MyIntradayWaveUpdateJob):
    @property
    def index_list(self):
        return [INDICES.DOW_JONES, INDICES.NASDAQ100]


class MyIntradayWaveUpdateJobForCurrencies(MyIntradayWaveUpdateJob):
    @property
    def index_list(self):
        return [INDICES.FOREX]


class MyPatternUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        self._stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.CRYPTO_CCY)
        if MyDate.is_tuesday_till_saturday():
            self._stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.FOREX)
            self._stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.INDICES)
            self._stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.DOW_JONES)
            self._stock_db_updater.update_pattern_data_by_index_for_daily_period(INDICES.NASDAQ100)


class MyTradeRecordsUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        self._stock_db_updater.update_trade_records(4, 16)


class MyDashJobHandler:
    def __init__(self, for_test=False):
        self._weekdays_all = [0, 1, 2, 3, 4, 5, 6]
        self._weekdays_week = [0, 1, 2, 3, 4]  # Monday till Friday
        self._scheduler = MyPatternScheduler('DashStockDatabaseUpdater')
        self._stock_db_updater = StockDatabaseUpdater()
        if for_test:
            self.__add_jobs_for_testing__()
        else:
            self.__add_jobs__()

    def check_scheduler_tasks(self):
        self._scheduler.check_tasks()

    def start_job_manually(self, job_to_start: str):
        self._scheduler.start_job_manually(job_to_start)

    @property
    def last_run_date_time(self):
        return self._scheduler.last_run_date_time

    @property
    def job_list(self):
        return self._scheduler.job_list

    def __add_jobs__(self):
        self._scheduler.add_job(MyDashDeleteDuplicatesJob(
            weekdays=self._weekdays_all, start_times=['01:00'], stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyDashStockDataUpdateJob(
            weekdays=self._weekdays_all, start_times=['01:30'], stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyEquityUpdateJob(
            weekdays=self._weekdays_all, start_times=['03:00'], stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyPatternUpdateJob(
            weekdays=self._weekdays_all, start_times=['03:15'], stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyDailyWaveUpdateJob(
            weekdays=self._weekdays_all, start_times=['04:00'], stock_db_updater=self._stock_db_updater))
        self.__add_jobs_for_intraday_wave_update__()
        self._scheduler.add_job(MyDashTradePolicyUpdateJob(
            weekdays=self._weekdays_all, start_times=['05:00'], stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyDashPredictorOptimizerJob(
            weekdays=self._weekdays_all, start_times=['05:30'], stock_db_updater=self._stock_db_updater))
        # self._scheduler.add_job(MyTradeRecordsUpdateJob(
        # weekdays=self._weekdays, start_times=['05:30'], stock_db_updater=self._stock_db_updater))

    def __add_jobs_for_intraday_wave_update__(self):
        start_times_crypto = ['04:30', '10:00', '16:00', '22:00']
        start_times_shares = ['18:00', '20:00', '23:00']
        start_times_currencies = ['06:00', '18:30']
        self._scheduler.add_job(MyIntradayWaveUpdateJobForCrypto(
            weekdays=self._weekdays_all, start_times=start_times_crypto, stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyIntradayWaveUpdateJobForShares(
            weekdays=self._weekdays_week, start_times=start_times_shares, stock_db_updater=self._stock_db_updater))
        self._scheduler.add_job(MyIntradayWaveUpdateJobForCurrencies(
            weekdays=self._weekdays_week, start_times=start_times_currencies, stock_db_updater=self._stock_db_updater))

    def __add_jobs_for_testing__(self):
        start_time = self.__get_start_time_for_testing__()
        self._scheduler.add_job(MyDashPredictorOptimizerJob(
            weekdays=self._weekdays_all, start_times=[start_time], stock_db_updater=self._stock_db_updater))

    @staticmethod
    def __get_start_time_for_testing__():
        dt_now = MyDate.get_datetime_object()
        dt_now = MyDate.adjust_by_seconds(dt_now, 10)
        return str(dt_now.time())[:8]
