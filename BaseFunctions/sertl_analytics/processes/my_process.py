"""
Description: This module contains the PatternProcess and PatternProcessManager classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-22
"""

from sertl_analytics.constants.my_constants import MYPR
from sertl_analytics.mydates import MyDate
from sertl_analytics.datafetcher.database_fetcher import BaseDatabase


class MyProcess:
    def __init__(self, db: BaseDatabase):
        self._file_log = self.__get_file_log__()
        self._db_stock = db
        self._start_dt = None
        self._end_dt = None
        self._processed_records = 0
        self._deleted_records = 0
        self._updated_records = 0
        self._inserted_records = 0
        self._child_process_names = self.__get_child_process_names__()
        self._child_processes = []
        self._triggered_by_process_names = []
        self._process_result = None
        self._table_record_number_before_start = 0
        self._table_record_number_after_end = 0
        self._table_names = self.__get_table_names__()

    @property
    def process_name(self):
        return MYPR.RUN_UNDEFINED_PROCESS

    @property
    def process_result(self):
        return self._process_result

    @process_result.setter
    def process_result(self, value):
        self._process_result = value

    def was_triggered_by_another_process(self):
        return len(self._triggered_by_process_names) > 0

    def set_child_processes(self, process_dict: dict):
        self._child_processes = [process_dict.get(process_name) for process_name in self._child_process_names]

    def add_to_triggered_by_process_names(self, process_name: str):
        if process_name not in self._triggered_by_process_names:
            self._triggered_by_process_names.append(process_name)

    def process_decorator(self, func):
        # if a function use this decorator there must be a parameter in the signature called "process"
        def function_wrapper(*args, **kwargs):
            self.__start_process__()
            self.process_result = func(*args, **kwargs, process=self)
            self.__end_process__()
            return self.process_result
        return function_wrapper

    def __get_file_log__(self):
        pass

    def __start_process__(self):
        print('Start process: {}'.format(self.process_name))
        self._start_dt = MyDate.get_datetime_object()
        self._end_dt = None
        self._processed_records = 0
        self._updated_records = 0
        self._deleted_records = 0
        self._inserted_records = 0
        self._table_record_number_before_start = self.__get_table_record_numbers__()

    def __end_process__(self):
        print('End process: {}'.format(self.process_name))
        self._end_dt = MyDate.get_datetime_object()
        self._table_record_number_after_end = self.__get_table_record_numbers__()
        self.__calculate_insert_delete_numbers__()
        self._triggered_by_process_names = []  # done for this dependencies
        self.__trigger_child_processes__()
        self._file_log.log_message(self.get_statistics(), 'End Process', self.process_name)  # ToDo - get rid of this file_log...

    def __get_table_record_numbers__(self):
        counter = 0
        for table_name in self._table_names:
            counter += self._db_stock.get_number_of_records_for_table(table_name)
        return counter

    def __calculate_insert_delete_numbers__(self):
        change_since_start = self._table_record_number_after_end - self._table_record_number_before_start
        if change_since_start > 0:
            self.increment_inserted_records(change_since_start)
        else:
            self.increment_deleted_records(abs(change_since_start))

    def __trigger_child_processes__(self):
        for child_process in self._child_processes:
            print('__trigger_child_processes__: child_process={}, triggered_by_name={}'.format(
                child_process.process_name, self.process_name
            ))
            child_process.add_to_triggered_by_process_names(self.process_name)

    def increment_processed_records(self, increment=1):
        self._processed_records += increment

    def increment_deleted_records(self, increment=1):
        self._deleted_records += increment

    def increment_updated_records(self, increment=1):
        self._updated_records += increment

    def increment_inserted_records(self, increment=1):
        self._inserted_records += increment

    def get_record_numbers(self) -> list:
        return [self._processed_records, self._inserted_records, self._updated_records, self._deleted_records]

    def get_record_numbers_as_string(self) -> list:
        return [str(number) for number in self.get_record_numbers()]

    def get_statistics(self):
        record_numbers = self.get_record_numbers()
        if max(record_numbers) == 0:
            return ''
        prefix_list = ['processed', 'inserted', 'updated', 'deleted']
        prefix_value_list = ['{}: {}'.format(prefix_list[idx], n) for idx, n in enumerate(record_numbers) if n > 0]
        return ', '.join(prefix_value_list)

    @staticmethod
    def __get_child_process_names__():
        return []

    @staticmethod
    def __get_table_names__():
        return []


class ProcessRunUndefinedProcess(MyProcess):
    @property
    def process_name(self):
        return MYPR.RUN_UNDEFINED_PROCESS

