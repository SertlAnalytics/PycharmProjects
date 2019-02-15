"""
Description: This module contains the schedulers for pattern tasks.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-17
"""

import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pattern_scheduling.pattern_job import MyPatternJob
from sertl_analytics.mydates import MyDate
from pattern_logging.pattern_log import PatternLog


class MyPatternScheduler:
    def __init__(self, check_interval_min=30):
        self._check_date_str = ''
        self._check_interval_min = check_interval_min
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._job_list = []
        self._pattern_log = PatternLog('pattern_log_scheduler.csv')

    @property
    def process_name(self):
        return 'Scheduler'

    def add_job(self, scheduled_job: MyPatternJob):
        self._job_list.append(scheduled_job)

    def start_scheduler(self):  # Run the task scheduler in another thread
        self._executor.submit(self.__check_scheduled_jobs__)

    def __check_scheduled_jobs__(self):
        interval_seconds = self._check_interval_min * 60
        while True:
            self._pattern_log.log_message('__check_scheduled_jobs__', process='Scheduler', process_step='Start')
            # ToDo - get rid of this log when error for missing second day start is found
            print("{}: Checking for scheduled tasks...(next time in {} seconds)".format(
                self.process_name, interval_seconds))
            actual_date_str = MyDate.get_date_as_string_from_date_time()
            if actual_date_str != self._check_date_str:
                for task in self._job_list:
                    task.init_task()
                self._check_date_str = actual_date_str
            for task in self._job_list:
                if task.is_ready(self._check_interval_min):
                    task.start_task()
            time.sleep(interval_seconds)




