"""
Description: This module contains the schedulers for pattern tasks.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-17
"""

from sertl_analytics.processes.my_job import MyJob
from sertl_analytics.mydates import MyDate
from pattern_logging.pattern_log import PatternLog
from pattern_process_manager import PatternProcessManager


class MyPatternScheduler:
    def __init__(self, process: str, process_manager: PatternProcessManager, for_test=False):
        self._process = process
        self._process_manager = process_manager
        self._last_run_time_stamp = None
        self._last_run_date_time = ''
        self._for_test = for_test
        self._job_dict = {}

    @property
    def job_list(self):
        return [job for job in self._job_dict.values()]

    @property
    def last_run_date_time(self):
        return self._last_run_date_time

    def add_job(self, scheduled_job: MyJob):
        print('add_job: {} - start_time={}'.format(scheduled_job.job_name, scheduled_job.start_time))
        scheduled_job.process = self._process_manager.get_process_by_name(scheduled_job.process_name)
        scheduled_job.for_test = self._for_test
        self._job_dict[scheduled_job.job_name] = scheduled_job

    def get_job(self, job_name: str) -> MyJob:
        return self._job_dict.get(job_name, None)

    def check_tasks(self):
        date_time_str = MyDate.get_date_time_as_string_from_date_time()
        if not self._for_test:
            PatternLog().log_scheduler_process('__check_scheduled_jobs__', process='Scheduler', process_step='Start')
        print("{}: Checking for scheduled tasks at {}".format(self._process, date_time_str))
        if self._last_run_time_stamp is not None:
            for job in self._job_dict.values():
                if job.is_ready(self._last_run_time_stamp):
                    print('...{}: Starting job: {}'.format(self._process, job.job_name))
                    job.start_job()
        self._last_run_time_stamp = MyDate.time_stamp_now()
        self._last_run_date_time = MyDate.get_date_time_from_epoch_seconds_as_string(self._last_run_time_stamp)

    def switch_job_state(self, job_name: str):
        job = self.get_job(job_name)
        if job is not None:
            if not job.is_running:
                print('...{}: Switch job state to : {}'.format(job.job_name, 'inactive' if job.is_active else 'active'))
                job.switch_job_state()

    def start_job_manually(self, job_name: str):
        job = self.get_job(job_name)
        if job is not None:
            if not job.is_running:
                print('...{}: Starting job manually'.format(job.job_name))
                job.start_job()







