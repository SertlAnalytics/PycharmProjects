"""
Description: This module contains all the scheduled jobs and its handler
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-22
"""

from salesman_dash.my_dash_jobs import MyDashUpdateSimilarOffersJob, MyDashOptimizeLogFilesJob
from salesman_scheduling.salesman_process_manager import SalesmanProcessManager
from salesman_scheduling.salesman_scheduler import MySalesmanScheduler
from sertl_analytics.constants.pattern_constants import PRD, INDICES, FT, PPR, STBL
from salesman_database.salesman_db import SalesmanDatabase
from salesman_database.salesman_database_updater import SalesmanDatabaseUpdater
from sertl_analytics.mydates import MyDate


class MyDashJobHandler:
    def __init__(self, process_manager: SalesmanProcessManager, for_test=False):
        self._process_manager = process_manager
        self._weekdays_all = [0, 1, 2, 3, 4, 5, 6]
        self._weekdays_week = [0, 1, 2, 3, 4]  # Monday till Friday
        self._weekdays_tu_sa = [1, 2, 3, 4, 5]  # Tuesday till Saturday
        self._scheduler = MySalesmanScheduler('DashSalesDatabaseUpdater', self._process_manager)
        self._db_updater = SalesmanDatabaseUpdater(SalesmanDatabase())
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
        self._scheduler.add_job(
            MyDashUpdateSimilarOffersJob(
                weekdays=self._weekdays_all, start_times=['01:00'], db_updater=self._db_updater))
        self._scheduler.add_job(
            MyDashOptimizeLogFilesJob(weekdays=[6], start_times=['23:00'], db_updater=self._db_updater))

    def __add_jobs_for_intraday_wave_update__(self):
        start_times_crypto = ['04:30', '10:00', '16:00', '22:00']
        start_times_shares = ['18:00', '20:00', '23:00']
        start_times_currencies = ['06:00', '18:30']

    def __add_jobs_for_testing__(self):
        start_time = self.__get_start_time_for_testing__()
        self._scheduler.add_job(
            MyDashOptimizeLogFilesJob(weekdays=[6], start_times=[start_time], db_updater=self._db_updater))

    @staticmethod
    def __get_start_time_for_testing__():
        dt_now = MyDate.get_datetime_object()
        dt_now = MyDate.adjust_by_seconds(dt_now, 10)
        return str(dt_now.time())[:8]
