"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.mydates import MyDate
from salesman_database.salesman_tables import CompanyTable, MetricTable, ProcessTable
from salesman_database.access_layer.access_layer_base import AccessLayer
import pandas as pd
from sertl_analytics.constants.pattern_constants import DC, PRDC, MDC


class AccessLayer4Company(AccessLayer):
    def __get_table__(self):
        return CompanyTable()

    def is_company_available(self, company_name: str) -> pd.DataFrame:
        df = self.select_data_by_data_dict({DC.NAME: company_name})
        return df.shape[0] > 0


class AccessLayer4Process(AccessLayer):
    def __get_table__(self):
        return ProcessTable()

    def is_process_available_for_today(self, process: str) -> pd.DataFrame:
        dt_today = MyDate.get_date_as_string_from_date_time()  # e.g. dt_today = '2018-12-22'
        df = self.select_data_by_data_dict({PRDC.PROCESS: process, PRDC.START_DT: dt_today})
        return df.shape[0] > 0


class AccessLayer4Metric(AccessLayer):
    def __get_table__(self):
        return MetricTable()

    def get_actual_metric_data_frame(self) -> pd.DataFrame:
        dt_today = MyDate.get_date_as_string_from_date_time()
        # dt_today = '2018-12-22'
        return self.select_data_by_data_dict({MDC.VALID_DT: dt_today})

