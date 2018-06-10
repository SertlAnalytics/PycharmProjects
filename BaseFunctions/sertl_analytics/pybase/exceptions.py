"""
Description: This module contains dedicated exceptions for the applications of SERTL Analytics.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-22
"""
import sys
import logging
import cProfile, pstats


class MyException(Exception):
    pass


class MyError:
    def __init__(self, module_name: str, unexpected_error: bool = True):
        self.type, self.value, self.traceback = sys.exc_info()
        self.module = module_name
        self.unexpected_error = unexpected_error
        self.print_details()

    def print_details(self):
        label = 'Unexpected error'  if self.unexpected_error else 'Error'
        print('{} in module {}: type = {}, value = {}, traceback = {}'.format(
            label, self.module, self.type, self.value, self.traceback))


class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger('MyLogger')
        self.retry_dic = {}
        self.error_list = []

    def catch_known_exception(self, module_name: str, message: str = ''):
        self.logger.exception('known exception')
        self.error_list.append(MyError(module_name, False))
        if message != '':
            print(message)

    def catch_exception(self, module_name: str, message: str = ''):
        self.logger.exception('unknown exception')
        self.error_list.append(MyError(module_name, True))
        if message != '':
            print(message)

    def add_to_retry_dic(self, key, entry):
        self.retry_dic[key] = entry


class MyProfiler:  # https://docs.python.org/3/library/profile.html
    def __init__(self):
        self.profile = cProfile.Profile()
        self.profile.enable()

    def disable(self, to_print: bool = True, print_stats_filter: str = 'pattern'):
        self.profile.disable()
        if to_print:
            self.print_stats(print_stats_filter)

    def print_stats(self, filter: str):
        ps = pstats.Stats(self.profile).sort_stats('cumulative')
        ps.print_stats(0.1, filter)
