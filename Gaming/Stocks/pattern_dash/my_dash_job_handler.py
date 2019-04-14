"""
Description: This module contains the dash job handler
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-22
"""

from pattern_dash.my_dash_jobs import MyDashDeleteDuplicatesJob, MyDashStockDataUpdateJobForCrypto
from pattern_dash.my_dash_jobs import MyDashStockDataUpdateJobForCurrencies, MyDashStockDataUpdateJobForShares
from pattern_dash.my_dash_jobs import MyEquityUpdateJob, MyPatternUpdateJob, MyDashOptimizeLogFilesJob
from pattern_dash.my_dash_jobs import MyDailyWaveUpdateJob, MyDashTradePolicyUpdateJob
from pattern_dash.my_dash_jobs import MyDashPredictorOptimizerJob, MyIntradayWaveUpdateJobForShares
from pattern_dash.my_dash_jobs import MyIntradayWaveUpdateJobForCrypto, MyIntradayWaveUpdateJobForCurrencies
from pattern_process_manager import PatternProcessManager
from pattern_scheduling.pattern_scheduler import MyPatternScheduler
from pattern_database.stock_database_updater import StockDatabaseUpdater
from sertl_analytics.mydates import MyDate


class MyDashJobHandler:
    def __init__(self, process_manager: PatternProcessManager, for_test=False):
        self._process_manager = process_manager
        self._weekdays_all = [0, 1, 2, 3, 4, 5, 6]
        self._weekdays_week = [0, 1, 2, 3, 4]  # Monday till Friday
        self._weekdays_tu_sa = [1, 2, 3, 4, 5]  # Tuesday till Saturday
        self._scheduler = MyPatternScheduler('DashStockDatabaseUpdater', self._process_manager)
        self._db_updater = StockDatabaseUpdater()
        if for_test:
            self.__add_jobs_for_testing__()
        else:
            self.__add_jobs__()

    def check_scheduler_tasks(self):
        self._scheduler.check_tasks()

    def start_job_manually(self, job_to_start: str):
        self._scheduler.start_job_manually(job_to_start)

    def switch_job_state(self, job_name: str):
        self._scheduler.switch_job_state(job_name)

    @property
    def last_run_date_time(self):
        return self._scheduler.last_run_date_time

    @property
    def job_list(self):
        return self._scheduler.job_list

    def __add_jobs__(self):
        self._scheduler.add_job(MyDashDeleteDuplicatesJob(
            weekdays=self._weekdays_all, start_times=['00:30'], db_updater=self._db_updater))
        self._scheduler.add_job(MyDashStockDataUpdateJobForCrypto(
            weekdays=self._weekdays_all, start_times=['00:45'], db_updater=self._db_updater))
        self._scheduler.add_job(MyDashStockDataUpdateJobForCurrencies(
            weekdays=self._weekdays_tu_sa, start_times=['01:00'], db_updater=self._db_updater))
        self._scheduler.add_job(MyDashStockDataUpdateJobForShares(
            weekdays=self._weekdays_tu_sa, start_times=['01:15'], db_updater=self._db_updater))
        self._scheduler.add_job(MyEquityUpdateJob(
            weekdays=self._weekdays_all, start_times=['02:30'], db_updater=self._db_updater))
        self._scheduler.add_job(MyPatternUpdateJob(
            weekdays=self._weekdays_all, start_times=['03:00'], db_updater=self._db_updater))
        self._scheduler.add_job(MyDailyWaveUpdateJob(
            weekdays=self._weekdays_all, start_times=['04:00'], db_updater=self._db_updater))
        self.__add_jobs_for_intraday_wave_update__()
        self._scheduler.add_job(MyDashTradePolicyUpdateJob(
            weekdays=self._weekdays_all, start_times=['04:30'], db_updater=self._db_updater))
        self._scheduler.add_job(MyDashPredictorOptimizerJob(
            weekdays=self._weekdays_all, start_times=['05:30'], db_updater=self._db_updater))
        self._scheduler.add_job(
            MyDashOptimizeLogFilesJob(weekdays=[6], start_times=['23:00'], db_updater=self._db_updater))
        # self._scheduler.add_job(MyTradeRecordsUpdateJob(
        # weekdays=self._weekdays, start_times=['05:30'], stock_db_updater=self._db_updater))

    def __add_jobs_for_intraday_wave_update__(self):
        start_times_crypto = ['04:30', '10:00', '16:00', '22:00']
        start_times_shares = ['18:00', '20:00', '23:00']
        start_times_currencies = ['06:00', '18:30']
        self._scheduler.add_job(MyIntradayWaveUpdateJobForCrypto(
            weekdays=self._weekdays_all, start_times=start_times_crypto, db_updater=self._db_updater))
        self._scheduler.add_job(MyIntradayWaveUpdateJobForShares(
            weekdays=self._weekdays_week, start_times=start_times_shares, db_updater=self._db_updater))
        self._scheduler.add_job(MyIntradayWaveUpdateJobForCurrencies(
            weekdays=self._weekdays_week, start_times=start_times_currencies, db_updater=self._db_updater))

    def __add_jobs_for_testing__(self):
        start_time = self.__get_start_time_for_testing__()
        self._scheduler.add_job(MyDashPredictorOptimizerJob(
            weekdays=self._weekdays_all, start_times=[start_time], db_updater=self._db_updater))

    @staticmethod
    def __get_start_time_for_testing__():
        dt_now = MyDate.get_datetime_object()
        dt_now = MyDate.adjust_by_seconds(dt_now, 10)
        return str(dt_now.time())[:8]
