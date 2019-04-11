"""
Description: This class is responsible for the automated daily update of the stock database.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-12-10
"""

from sertl_analytics.constants.pattern_constants import BT, TSTR, FT, DC, PRD, TRT, EQUITY_TYPE, TRC
from sertl_analytics.constants.pattern_constants import INDICES, EDC, EST, FD
from sertl_analytics.constants.pattern_constants import TPMDC
from sertl_analytics.mydates import MyDate
from tutti import Tutti
from salesman_database.salesman_access_layer import AccessLayer4Offer
from salesman_scheduling.salesman_job_result import SalesmanDatabaseUpdateJobResult
from salesman_logging.salesman_log import SalesmanLog
from time import sleep
import numpy as np


class SalesmanDatabaseUpdater:
    def __init__(self, db_salesman):
        self.db_salesman = db_salesman

    def update_similar_offers(self):
        print('ToDo: update similar offers...')  # ToDo

    def update_equity_records(self) -> SalesmanDatabaseUpdateJobResult:
        result_obj = SalesmanDatabaseUpdateJobResult()
        access_layer = AccessLayer4Offer(self.db_salesman)
        dt_today = MyDate.get_date_from_datetime()
        # dt_today = MyDate.adjust_by_days(dt_today, 40)
        dt_valid_until = MyDate.adjust_by_days(dt_today, 30)
        dt_today_str = str(dt_today)
        dt_valid_until_str = str(dt_valid_until)
        return result_obj
