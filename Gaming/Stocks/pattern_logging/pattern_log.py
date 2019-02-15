"""
Description: This module contains the central pattern log class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.mydates import MyDate
import os


class PatternLog:
    def __init__(self, file_name='pattern_log_test.csv'):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        self._log_file_path = os.path.join(package_dir, file_name)

    def log_message(self, log_message: str, process='', process_step='run'):
        for old, new in {',': ' ', '; ': ' ', '  ': ' '}.items():
            log_message = log_message.replace(old, new).strip()
        process = 'logging' if process == '' else process
        file1 = open(self._log_file_path, 'a')  # write append mode
        date_time = MyDate.get_date_time_as_string_from_date_time()
        date_time_parts = date_time.split(' ')
        line_list = [date_time_parts[0], date_time_parts[1], process, process_step, log_message]
        file1.write('{}\n'.format(','.join(line_list)))
        file1.close()
