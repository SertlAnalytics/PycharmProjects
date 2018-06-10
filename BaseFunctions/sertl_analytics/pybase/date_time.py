"""
Description: This module contains different date time helper classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-21
"""
from datetime import datetime, timedelta


class MyPyDate:
    @staticmethod
    def get_date_from_datetime(date_time):
        if date_time is None:
            return None
        if date_time.__class__.__name__ == 'date':  # no change
            return date_time
        return datetime.strptime(str(date_time), '%Y-%m-%d %H:%M:%S').date()

    @staticmethod
    def get_date_from_number(num: int):
        return datetime(1, 1, 1) + timedelta(days=num)


class MyClock:
    def __init__(self, process: str = ''):
        self.__process = process
        self.__start_date_time = datetime.now()
        self.__end_date_time = None
        self.__time_difference = None

    def start(self, process: str = ''):
        self.__process = process
        self.__start_date_time = datetime.now()

    def stop(self, do_print: bool = True):
        self.__end_date_time = datetime.now()
        self.__time_difference = self.__end_date_time - self.__start_date_time
        self.__time_difference_seconds = round(self.__time_difference.seconds
                                               + self.__time_difference.microseconds/10**6, 2)
        if do_print:
            self.print()

    def print(self):
        print('{}: {} - {}: Difference: {} sec.'.format(
            self.__process, self.__start_date_time.time(), self.__end_date_time.time(), self.__time_difference_seconds))