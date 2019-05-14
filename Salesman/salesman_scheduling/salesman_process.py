"""
Description: This module contains the PatternProcess and PatternProcessManager classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-22
"""

from sertl_analytics.constants.salesman_constants import SMPR, SMTBL
from sertl_analytics.constants.my_constants import MYPR
from sertl_analytics.processes.my_process import MyProcess
from salesman_logging.salesman_log import SalesmanLog

"""
    UPDATE_SIMILAR_SALES_DAILY = 'Update_Sale_Daily'
    UPDATE_COMPANY_DAILY = 'Update_Company_Daily'
"""


class SalesmanProcess(MyProcess):
    def __get_file_log__(self):
        return SalesmanLog()


class SalesmanSalesProcess(SalesmanProcess):
    @staticmethod
    def __get_child_process_names__():
        return [SMPR.UPDATE_SALES_DATA_IN_STATISTICS_TAB]


class ProcessCheckSalesState(SalesmanSalesProcess):
    @property
    def process_name(self):
        return SMPR.CHECK_SALES_STATE

    @staticmethod
    def __get_table_names__():
        return [SMTBL.SALE]


class ProcessUpdateSaleDaily(SalesmanSalesProcess):
    @property
    def process_name(self):
        return SMPR.UPDATE_SIMILAR_SALES_DAILY

    @staticmethod
    def __get_table_names__():
        return [SMTBL.SALE]


class ProcessCheckSimilarSalesInDatabase(SalesmanSalesProcess):
    @property
    def process_name(self):
        return SMPR.CHECK_SIMILAR_SALES_IN_DATABASE

    @staticmethod
    def __get_table_names__():
        return [SMTBL.SALE]


class ProcessUpdateSalesDataInStatisticsTab(SalesmanProcess):
    @property
    def process_name(self):
        return SMPR.UPDATE_SALES_DATA_IN_STATISTICS_TAB


class ProcessUpdateCompanyDaily(SalesmanProcess):
    @property
    def process_name(self):
        return SMPR.UPDATE_COMPANY_DAILY

    @staticmethod
    def __get_table_names__():
        return [SMTBL.COMPANY]


class ProcessOptimizeLogFiles(SalesmanProcess):
    @property
    def process_name(self):
        return MYPR.OPTIMIZE_LOG_FILES

    def __get_table_record_numbers__(self):  # here we have to count the lines within the concerned log files
        return self._file_log.count_rows_for_process_optimize_log_files()

