"""
Description: This module contains the job class for patterns
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-23
"""

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pattern_database.stock_access_layer import AccessLayer4Process
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import PRD, PRDC
from pattern_logging.pattern_log import PatternLog


class JobRuntime:
    def __init__(self):
        self._start_date_time = ''
        self._start_ts = 0
        self._end_date_time = ''
        self._end_ts = 0

    @property
    def runtime_seconds(self) -> int:
        return self._end_ts - self._start_ts

    @property
    def runtime_minutes(self):
        return round((self._end_ts - self._start_ts)/60, 2)

    @property
    def start_date(self):
        return self._start_date_time.split(' ')[0]

    @property
    def start_time(self):
        return self._start_date_time.split(' ')[1]

    @property
    def end_date(self):
        return self._end_date_time.split(' ')[0]

    @property
    def end_time(self):
        return self._end_date_time.split(' ')[1]

    def start(self):
        self._start_date_time = MyDate.get_date_time_as_string_from_date_time()
        self._start_ts = MyDate.get_epoch_seconds_from_datetime()

    def stop(self):
        self._end_date_time = MyDate.get_date_time_as_string_from_date_time()
        self._end_ts = MyDate.get_epoch_seconds_from_datetime()


class MyPatternJob:
    def __init__(self, period=PRD.DAILY, weekdays=list([0, 1, 2, 3, 4, 5, 6]), start_time='01:00'):
        self._scheduled_period = period
        self._scheduled_start_time = start_time
        self._scheduled_weekdays = weekdays
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._is_running = False
        self._access_layer_process = AccessLayer4Process()
        self._job_runtime = JobRuntime()
        self._pattern_log = PatternLog('../pattern_logging/pattern_log.csv')

    @property
    def job_name(self):
        return self.__class__.__name__

    @property
    def is_running(self):
        return self._is_running

    @property
    def done(self):
        return self._access_layer_process.is_process_available_for_today(self.job_name)

    def is_ready(self, check_interval_min: int):
        if self.done or self.is_running:
            return False
        if MyDate.weekday() in self._scheduled_weekdays:
            diff_to_now_minutes = MyDate.get_time_difference_to_now_in_minutes(self._scheduled_start_time)
            return 0 <= diff_to_now_minutes <= check_interval_min
        return False

    def start_task(self): # Run the function in another thread
        self._is_running = True
        self._job_runtime.start()
        self._executor.submit(self.__run_task__)

    def init_task(self):
        self._is_running = False

    def __run_task__(self):
        print("{}: Thread started at {}...(scheduled: {})".format(
            self.job_name, MyDate.time_now_str(), self._scheduled_start_time))
        self._pattern_log.log_message(self.job_name, process='Scheduler', process_step='Start')
        self.__perform_task__()
        self._pattern_log.log_message(self.job_name, process='Scheduler', process_step='End')
        self._is_running = False
        self._done = True
        self._job_runtime.stop()
        self._executor.shutdown(wait=False)
        self.__write_statistics_to_database__()
        print("{}: Thread shutdown at {}".format(self.job_name, MyDate.time_now_str()))

    def __perform_task__(self):
        print('Do something - the first time...')

    def __write_statistics_to_database__(self):
        input_dict = {PRDC.PROCESS: self.job_name,
                      PRDC.TRIGGER: 'scheduled',
                      PRDC.START_DT: self._job_runtime.start_date,
                      PRDC.START_TIME: self._job_runtime.start_time,
                      PRDC.END_DT: self._job_runtime.end_date,
                      PRDC.END_TIME: self._job_runtime.end_time,
                      PRDC.RUNTIME_SECONDS: self._job_runtime.runtime_seconds,
                      PRDC.COMMENT: 'scheduled at {}'.format(self._scheduled_start_time)
                      }
        self._access_layer_process.insert_data([input_dict])


class MySecondJob(MyPatternJob):
    def __perform_task__(self):
        print('Do something - the second time...')