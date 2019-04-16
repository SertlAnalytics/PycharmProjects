"""
Description: This module contains the job class for patterns
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-23
"""

from concurrent.futures import ThreadPoolExecutor
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import PRD, PRDC, JDC, PPR
from sertl_analytics.constants.my_constants import MYPR
from sertl_analytics.myfilelog import FileLog
from sertl_analytics.processes.my_job_result import JobResult
from sertl_analytics.processes.my_process import MyProcess
from sertl_analytics.processes.my_job_runtime import JobRuntime


class MyJob:
    def __init__(self, period: str, weekdays: list, start_times: list):
        self._file_log = self.__get_file_log__()
        self._access_layer_process = self.__get_access_layer_process__()  # this has to be set by derived class
        self._scheduled_period = PRD.DAILY if period == '' else period
        self._scheduled_start_time_list = ['01:00'] if start_times is None else start_times
        self._scheduled_start_time = self.__init_scheduled_start_time__()
        self._scheduled_weekdays = weekdays
        self._for_test = False
        self._executor = None
        self._is_running = False
        self._job_runtime = JobRuntime()
        self._last_run_start_date_time = None
        self._last_run_end_date_time = None
        self._last_run_runtime_seconds = 0
        self._last_run_processed_details = ''
        self._process = None
        self._is_active = True

    @property
    def job_name(self):
        return self.__class__.__name__

    @property
    def process_name(self):
        return PPR.RUN_UNDEFINED_PROCESS

    @property
    def process(self) -> MyProcess:
        return self._process

    @process.setter
    def process(self, process: MyProcess):
        self._process = process

    @property
    def start_time(self):
        return self._scheduled_start_time

    @property
    def last_run_runtime_seconds(self):
        if not(self._last_run_start_date_time is None or self._last_run_end_date_time is None):
            return MyDate.get_time_difference_in_seconds(self._last_run_end_date_time,
                                                         self._last_run_start_date_time)

    @property
    def is_running(self):
        return self._is_running

    @property
    def for_test(self) -> bool:
        return self._for_test

    @for_test.setter
    def for_test(self, value: bool):
        self._for_test = value

    @property
    def is_active(self):
        return self._is_active

    def is_ready(self, last_run_time_stamp: int):
        if self._is_running or not self._is_active:
            return False
        if MyDate.weekday() in self._scheduled_weekdays:
            now_time_stamp = MyDate.time_stamp_now()
            start_time_stamp = MyDate.get_epoch_seconds_for_current_day_time(self._scheduled_start_time)
            return last_run_time_stamp < start_time_stamp <= now_time_stamp
        return False

    def switch_job_state(self):
        self._is_active = not self._is_active

    def start_job(self): # Run the function in another thread
        self._process.__start_process__()
        self._is_running = True
        self._job_runtime.start()
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._executor.submit(self.__run_job__)

    def get_data_dict_for_job_table_rows(self, columns_for_job_table: list):
        return {column: self.__get_data_for_job_table_column__(column) for column in columns_for_job_table}

    def __get_file_log__(self):
        pass

    def __get_access_layer_process__(self):
        pass

    def __init_scheduled_start_time__(self):
        if len(self._scheduled_start_time_list) == 1:
            return self._scheduled_start_time_list[0]
        return MyDate.get_nearest_time_in_list(self._scheduled_start_time_list)

    def __get_data_for_job_table_column__(self, column: str):
        if column == JDC.NAME:
            return self.job_name
        elif column == JDC.PERIOD:
            return self._scheduled_period
        elif column == JDC.WEEKDAYS:
            return ','.join(MyDate.get_weekdays_for_list(self._scheduled_weekdays))
        elif column == JDC.START_TIMES:
            return ', '.join(self._scheduled_start_time_list)
        elif column == JDC.NEXT_START_TIME:
            return self._scheduled_start_time
        elif column == JDC.LAST_RUN:
            return '-' if self._last_run_start_date_time is None else \
                MyDate.get_time_str_from_datetime(self._last_run_start_date_time)
        elif column == JDC.LAST_RUN_TIME:
            if not self._is_active:
                return 'deactivated'
            return '- running -' if self._is_running else self.last_run_runtime_seconds
        elif column == JDC.PROCESSED:
            return '' if self._last_run_end_date_time is None else ','.join(self.process.get_record_numbers_as_string())

    def __run_job__(self):
        process_step = 'End'
        self.__init_run_parameters__()
        print("{}: Thread started at {}...(scheduled: {})".format(
            self.job_name, MyDate.time_now_str(), self._scheduled_start_time))
        if not self._for_test:
            self._file_log.log_message(self.job_name, process='Scheduler', process_step='Start')
        try:
            self.__perform_task__()
            self._last_run_end_date_time = MyDate.get_datetime_object()
        except:
            if self._for_test:
                print("{}: Error at {}".format(self.job_name, MyDate.time_now_str()))
            else:
                self._file_log.log_error()
                process_step = 'End with error'
        finally:
            if not self._for_test:
                self._file_log.log_message(self.job_name, process='Scheduler', process_step=process_step)
            self._is_running = False
            self._job_runtime.stop()
            self._executor.shutdown(wait=False)
            self._process.__end_process__()
            if not self._for_test:
                self.__write_statistics_to_database__()
            print("{}: Thread shutdown at {}".format(self.job_name, MyDate.time_now_str()))
            self.__schedule_next_time__()

    def __init_run_parameters__(self):
        self._last_run_start_date_time = MyDate.get_datetime_object()
        self._last_run_end_date_time = None
        self._last_run_runtime_seconds = 0
        self._last_run_processed_details = ''

    def __perform_task__(self):
        if self._process is not None:
            self._process.increment_processed_records()
        print('Do something - the first time...')

    def __handle_job_result__(self, job_result: JobResult):
        if job_result is None:
            return
        self._last_run_processed_details = job_result.job_details

    def __schedule_next_time__(self):
        if len(self._scheduled_start_time_list) == 1:  # no rescheduling necessary
            return
        self._scheduled_start_time = MyDate.get_nearest_time_in_list(self._scheduled_start_time_list)
        print('{}: Rescheduled for next run at {}'.format(self.job_name, self._scheduled_start_time))

    def __write_statistics_to_database__(self):
        input_dict = {PRDC.PROCESS: self.job_name,
                      PRDC.TRIGGER: 'scheduled',
                      PRDC.START_DT: self._job_runtime.start_date,
                      PRDC.START_TIME: self._job_runtime.start_time,
                      PRDC.END_DT: self._job_runtime.end_date,
                      PRDC.END_TIME: self._job_runtime.end_time,
                      PRDC.RUNTIME_SECONDS: self._job_runtime.runtime_seconds,
                      PRDC.COMMENT: 'scheduled at {}'.format(self._scheduled_start_time_list)
                      }
        self._access_layer_process.insert_data([input_dict])
