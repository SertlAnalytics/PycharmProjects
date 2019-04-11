"""
Description: This module contains all the scheduled jobs and its handler
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-22
"""

from salesman_scheduling.salesman_job import MySalesmanJob
from sertl_analytics.constants.pattern_constants import PRD
from sertl_analytics.constants.salesman_constants import SMPR
from sertl_analytics.constants.my_constants import MYPR
from salesman_database.salesman_database_updater import SalesmanDatabaseUpdater


class MyDashSalesmanJob(MySalesmanJob):
    def __init__(self, weekdays: list, start_times: list, db_updater: SalesmanDatabaseUpdater):
        MySalesmanJob.__init__(self, period=PRD.DAILY, weekdays=weekdays, start_times=start_times)
        self._db_updater = db_updater


class MyDashUpdateSimilarOffersJob(MyDashSalesmanJob):
    def __perform_task__(self):
        self._db_updater.update_similar_offers()

    @property
    def process_name(self):
        return SMPR.UPDATE_OFFER_DAILY


class MyDashOptimizeLogFilesJob(MyDashSalesmanJob):
    def __perform_task__(self):
        self._file_log.process_optimize_log_files()

    @property
    def process_name(self):
        return MYPR.OPTIMIZE_LOG_FILES



