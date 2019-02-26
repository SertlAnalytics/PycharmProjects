"""
Description: This module contains the central pattern log class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.mydates import MyDate
import os
import sys
import traceback


class PatternLog:
    @staticmethod
    def log_error():
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        message = lines[-2]
        process = lines[-1]
        process = process.replace('\n', ' ').strip()
        PatternLog.__log_message__(PatternLog.__get_file_path_for_errors__(), message, process, '')

    @staticmethod
    def log_message(log_message: str, process='', process_step='run'):
        PatternLog.__log_message__(PatternLog.__get_file_path_for_messages__(), log_message, process, process_step)

    @staticmethod
    def log_trade(log_message: str, process='', process_step='run'):
        PatternLog.__log_message__(PatternLog.__get_file_path_for_trades__(), log_message, process, process_step)

    @staticmethod
    def log_scheduler_process(log_message: str, process='', process_step='run'):
        PatternLog.__log_message__(PatternLog.__get_file_path_for_scheduler__(), log_message, process, process_step)

    @staticmethod
    def log_test_message(log_message: str, process='', process_step='run'):
        PatternLog.__log_message__(PatternLog.__get_file_path_for_test__(), log_message, process, process_step)

    @staticmethod
    def __log_message__(file_path, log_message: str, process='', process_step='run'):
        for old, new in {',': ' ', '; ': ' ', '  ': ' ', '\n': ' ', '"': ''}.items():
            log_message = log_message.replace(old, new).strip()
        log_message = log_message.strip()
        process = 'logging' if process == '' else process
        file1 = open(file_path, 'a')  # write append mode
        date_time = MyDate.get_date_time_as_string_from_date_time()
        date_time_parts = date_time.split(' ')
        line_list = [date_time_parts[0], date_time_parts[1], process, process_step, log_message]
        file1.write('{}\n'.format(','.join(line_list)))
        file1.close()

    @staticmethod
    def __get_file_path_for_messages__():
        return PatternLog.__get_file_path__('pattern_log.csv')

    @staticmethod
    def __get_file_path_for_errors__():
        return PatternLog.__get_file_path__('pattern_log_errors.csv')

    @staticmethod
    def __get_file_path_for_scheduler__():
        return PatternLog.__get_file_path__('pattern_log_scheduler.csv')

    @staticmethod
    def __get_file_path_for_test__():
        return PatternLog.__get_file_path__('pattern_log_test.csv')

    @staticmethod
    def __get_file_path_for_trades__():
        return PatternLog.__get_file_path__('pattern_log_trades.csv')

    @staticmethod
    def __get_file_path__(file_name: str):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, file_name)