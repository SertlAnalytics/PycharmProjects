"""
Description: This module contains the central pattern log class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import LOGT
import os
import sys
import traceback


class FileLogLine:
    def __init__(self, line: str):
        self._line = line
        self._values = self._line.split(',')

    @property
    def is_valid(self) -> bool:
        return len(self._values) == 5

    @property
    def date(self):
        return self._values[0]

    @property
    def date_time(self):
        return '{} {}'.format(self._values[0], self._values[1])

    @property
    def time(self):
        return self._values[1]

    @property
    def process(self):
        return self._values[2]

    @property
    def step(self):
        return self._values[3]

    @property
    def comment(self):
        return self._values[4]


class FileLog:
    log_activated = True

    def log_error(self, runtime_info=''):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        message = lines[-2]
        process = lines[-1]
        process = process.replace('\n', ' ').strip()
        runtime_info = runtime_info.replace(',', '#')  # runtime info can contain comma. Which is not allowed...
        self.__log_message__(self.__get_file_path_for_errors__(), message, process, runtime_info)

    def count_rows_for_process_optimize_log_files(self):
        log_types_for_processing = self.__get_log_types_for_process_optimize_log_files__()
        num_lines = 0
        for log_type in log_types_for_processing:
            file_path = self.get_file_path_for_log_type(log_type)
            num_lines += self.__get_line_number_for_file__(file_path)
        return num_lines

    def __get_line_number_for_file__(self, file_path):
        num_lines = 0
        with open(file_path) as file:
            num_lines += sum(1 for line in file)
        return num_lines

    def process_optimize_log_files(self):
        log_types_for_processing = self.__get_log_types_for_process_optimize_log_files__()
        date_compare = MyDate.get_date_str_from_datetime(MyDate.adjust_by_days(None, -7))
        for log_type in log_types_for_processing:
            file_path = self.get_file_path_for_log_type(log_type)
            line_to_keep_list = []
            with open(file_path, 'r') as file:
                for line in file.readlines():
                    log_line = FileLogLine(line)
                    if log_line.is_valid:
                        if log_line.date >= date_compare:
                            line_to_keep_list.append(line)
                    else:
                        print('{}: Line not valid in log file: {}'.format(file_path, line))
            self.__replace_file_when_changed__(file_path, line_to_keep_list)

    def __replace_file_when_changed__(self, file_path, line_to_keep_list):
        line_number = self.__get_line_number_for_file__(file_path)
        if line_number > len(line_to_keep_list):
            print('Update file: {}, old: {}, new={} lines'.format(file_path, line_number, len(line_to_keep_list)))
            with open(file_path, 'w') as file:
                for line_to_keep in line_to_keep_list:
                    file.write(line_to_keep)

    def log_message(self, log_message: str, process='', process_step='run'):
        self.__log_message__(self.__get_file_path_for_messages__(), log_message, process, process_step)

    def log_trade(self, log_message: str, process='', process_step='run'):
        self.__log_message__(self.__get_file_path_for_trades__(), log_message, process, process_step)

    def log_scheduler_process(self, log_message: str, process='', process_step='run'):
        self.__log_message__(self.__get_file_path_for_scheduler__(), log_message, process, process_step)

    def log_test_message(self, log_message: str, process='', process_step='run'):
        self.__log_message__(self.__get_file_path_for_test__(), log_message, process, process_step)

    def __get_log_types_for_process_optimize_log_files__(self):
        return [LOGT.ERRORS, LOGT.SCHEDULER, LOGT.MESSAGE_LOG]

    def __log_message__(self, file_path, log_message: str, process='', process_step='run'):
        if not self.log_activated:
            print('File_log is deactivated')
            return
        for old, new in {',': ' ', '; ': ' ', '  ': ' ', '\n': ' ', '"': ''}.items():
            log_message = log_message.replace(old, new).strip()
        log_message = log_message.strip()
        process = 'logging' if process == '' else process
        date_time = MyDate.get_date_time_as_string_from_date_time()
        date_time_parts = date_time.split(' ')
        line_list = [date_time_parts[0], date_time_parts[1], process, process_step, log_message]
        with open(file_path, 'a') as file:  # write append mode
            file.write('{}\n'.format(','.join(line_list)))

    def __get_file_path_for_messages__(self):
        return self.__get_file_path__('log_messages.csv')

    def __get_file_path_for_errors__(self):
        return self.__get_file_path__('log_errors.csv')

    def __get_file_path_for_scheduler__(self):
        return self.__get_file_path__('log_scheduler.csv')

    def __get_file_path_for_test__(self):
        return self.__get_file_path__('log_test.csv')

    def __get_file_path_for_trades__(self):
        return self.__get_file_path__('log_trades.csv')

    def __get_file_path__(self, file_name: str):
        pass

    def get_file_path_for_log_type(self, log_type: str):
        if log_type == LOGT.ERRORS:
            return self.__get_file_path_for_errors__()
        elif log_type == LOGT.PROCESSES:
            return ''
        elif log_type == LOGT.SCHEDULER:
            return self.__get_file_path_for_scheduler__()
        elif log_type == LOGT.MESSAGE_LOG:
            return self.__get_file_path_for_messages__()
        elif log_type == LOGT.WAVES:
            return ''
        elif log_type == LOGT.TRADES:
            return self.__get_file_path_for_trades__()
        return ''
