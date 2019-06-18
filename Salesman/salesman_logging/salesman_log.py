"""
Description: This module contains the central pattern log class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.myfilelog import FileLog
import os


class SalesmanLog(FileLog):
    def __get_file_path_for_messages__(self):
        return self.__get_file_path__('salesman_log.csv')

    def __get_file_path_for_errors__(self):
        return self.__get_file_path__('salesman_log_errors.csv')

    def __get_file_path_for_waiting_db_transactions__(self):
        return self.__get_file_path__('salesman_log_db_transactions.csv')

    def __get_file_path_for_scheduler__(self):
        return self.__get_file_path__('salesman_log_scheduler.csv')

    def __get_file_path_for_test__(self):
        return self.__get_file_path__('salesman_log_test.csv')

    def __get_file_path_for_trades__(self):
        return self.__get_file_path__('salesman_log_trades.csv')

    def __get_file_path__(self, file_name: str):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, file_name)

