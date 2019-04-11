"""
Description: This module contains the job class for patterns
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-23
"""

from sertl_analytics.processes.my_job import MyJob
from pattern_database.stock_access_layer import AccessLayer4Process
from pattern_logging.pattern_log import PatternLog


class MyPatternJob(MyJob):
    def __get_file_log__(self):
        return PatternLog()

    def __get_access_layer_process__(self):
        return AccessLayer4Process()


class MySecondJob(MyPatternJob):
    def __perform_task__(self):
        print('Do something - the second time...')