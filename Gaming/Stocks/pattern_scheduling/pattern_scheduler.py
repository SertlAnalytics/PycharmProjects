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
    def __init__(self, process: str, for_test=False):
        self._process = process
        self._last_run_time_stamp = None
        self._last_run_date_time = ''
        self._for_test = for_test
        self._job_list = []

    @property
    def job_list(self):
        return self._job_list

    @property
    def last_run_date_time(self):
        return self._last_run_date_time

    def add_job(self, scheduled_job: MyPatternJob):
        print('add_job: {} - start_time={}'.format(scheduled_job.job_name, scheduled_job.start_time))
        scheduled_job.for_test = self._for_test
        self._job_list.append(scheduled_job)

    def check_tasks(self):
        date_time_str = MyDate.get_date_time_as_string_from_date_time()
        if not self._for_test:
            PatternLog.log_scheduler_process('__check_scheduled_jobs__', process='Scheduler', process_step='Start')
        print("{}: Checking for scheduled tasks at {}".format(self._process, date_time_str))
        if self._last_run_time_stamp is not None:
            for job in self._job_list:
                if job.is_ready(self._last_run_time_stamp):
                    print('...{}: Starting job: {}'.format(self._process, job.job_name))
                    job.start_job()
        self._last_run_time_stamp = MyDate.time_stamp_now()
        self._last_run_date_time = MyDate.get_date_time_from_epoch_seconds_as_string(self._last_run_time_stamp)

    def start_job_manually(self, job_to_start: str):
        for job in self._job_list:
            if job.job_name == job_to_start:
                if not job.is_running:
                    print('...{}: Starting job: {}'.format('Manually', job.job_name))
                    job.start_job()
                    return





