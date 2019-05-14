"""
Description: This class is responsible for the automated daily update of the stock database.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-12-10
"""

from sertl_analytics.mydates import MyDate
from salesman_database.access_layer.access_layer_sale import AccessLayer4Sale
from salesman_scheduling.salesman_job_result import SalesmanDatabaseUpdateJobResult
from salesman_system_configuration import SystemConfiguration
from salesman_tutti.tutti import Tutti


class SalesmanDatabaseUpdater:
    def __init__(self, db_salesman, tutti: Tutti):
        self.sys_config = tutti.sys_config
        self.db_salesman = db_salesman
        self.tutti = tutti

    def check_sales_states(self):
        self.sys_config.file_log.log_message('check_status_of_sales_in_database', 'SalesmanDatabaseUpdater')
        self.tutti.check_status_of_sales_in_database()

    def update_similar_sales(self):
        self.sys_config.file_log.log_message('check_own_in_database_against_similar_sales', 'SalesmanDatabaseUpdater')
        self.tutti.check_own_sales_in_database_against_similar_sales()

    def check_similar_sales_in_database(self):
        self.sys_config.file_log.log_message('check_similar_sales_in_database', 'SalesmanDatabaseUpdater')
        self.tutti.check_similar_sales_in_db_against_master_sale_in_db()

    def update_equity_records(self) -> SalesmanDatabaseUpdateJobResult:
        result_obj = SalesmanDatabaseUpdateJobResult()
        access_layer = AccessLayer4Sale(self.db_salesman)
        dt_today = MyDate.get_date_from_datetime()
        # dt_today = MyDate.adjust_by_days(dt_today, 40)
        dt_valid_until = MyDate.adjust_by_days(dt_today, 30)
        dt_today_str = str(dt_today)
        dt_valid_until_str = str(dt_valid_until)
        return result_obj
