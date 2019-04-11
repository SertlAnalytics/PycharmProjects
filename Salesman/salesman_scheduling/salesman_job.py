"""
Description: This module contains the job class for patterns
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-23
"""


from salesman_database.salesman_access_layer import AccessLayer4Process
from salesman_logging.salesman_log import SalesmanLog
from sertl_analytics.processes.my_job import MyJob


class MySalesmanJob(MyJob):
    def __get_file_log__(self):
        return SalesmanLog()

    def __get_access_layer_process__(self):
        return AccessLayer4Process()



