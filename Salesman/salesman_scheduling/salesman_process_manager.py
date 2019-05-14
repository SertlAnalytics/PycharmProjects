"""
Description: This module contains process manager class for salesman
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-22
"""

from sertl_analytics.constants.salesman_constants import SMPR
from sertl_analytics.processes.my_process import ProcessRunUndefinedProcess
from sertl_analytics.processes.my_process_manager import MyProcessManager
import salesman_scheduling.salesman_process as smpr
from sertl_analytics.constants.my_constants import MYPR
from salesman_database.salesman_db import SalesmanDatabase


class SalesmanProcessManager(MyProcessManager):
    def __get_db__(self):
        return SalesmanDatabase()

    def __get_process_dict__(self) -> dict:
        return {
            SMPR.CHECK_SALES_STATE: smpr.ProcessCheckSalesState(self._db),
            SMPR.UPDATE_SIMILAR_SALES_DAILY: smpr.ProcessUpdateSaleDaily(self._db),
            SMPR.CHECK_SIMILAR_SALES_IN_DATABASE: smpr.ProcessCheckSimilarSalesInDatabase(self._db),
            SMPR.UPDATE_SALES_DATA_IN_STATISTICS_TAB: smpr.ProcessUpdateSalesDataInStatisticsTab(self._db),
            SMPR.UPDATE_COMPANY_DAILY: smpr.ProcessUpdateCompanyDaily(self._db),
            MYPR.OPTIMIZE_LOG_FILES: smpr.ProcessOptimizeLogFiles(self._db),
            MYPR.RUN_UNDEFINED_PROCESS: ProcessRunUndefinedProcess(self._db)
        }
