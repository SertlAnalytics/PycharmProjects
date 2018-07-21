"""
Description: This module contains different date time helper classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-21
"""
from datetime import datetime, timedelta
import matplotlib.dates as m_dates


class MyPyDate:
    @staticmethod
    def get_datetime_object(date_time):
        if date_time is None:
            return None
        if date_time.__class__.__name__ == 'datetime':  # no change
            return date_time
        if len(str(date_time)) == 10:
            return datetime.strptime(str(date_time), '%Y-%m-%d')
        else:
            return datetime.strptime(str(date_time), '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_epoch_seconds_from_datetime(date_time) -> int:
        if date_time is None:
            return 0
        date_time_object = MyPyDate.get_datetime_object(date_time)
        return datetime.timestamp(date_time_object)

    @staticmethod
    def get_epoch_number_from_datetime(date_time) -> float:
        if date_time is None:
            return 0
        date_time_object = MyPyDate.get_datetime_object(date_time)
        return m_dates.date2num(date_time_object)

    @staticmethod
    def get_datetime_from_epoch_number(epoch_number: float) -> datetime:
        return m_dates.num2date(epoch_number)

    @staticmethod
    def get_date_as_number_from_epoch_seconds(epoch_seconds: int) -> datetime:
        return m_dates.date2num(MyPyDate.get_date_time_from_epoch_seconds(epoch_seconds))

    @staticmethod
    def get_date_time_from_epoch_seconds(epoch_seconds: int) -> datetime:
       return datetime.fromtimestamp(epoch_seconds)

    @staticmethod
    def get_date_from_epoch_seconds(epoch_seconds: int) -> datetime:
        return datetime.fromtimestamp(epoch_seconds).date()

    @staticmethod
    def get_time_from_epoch_seconds(epoch_seconds: int) -> datetime:
        return datetime.fromtimestamp(epoch_seconds).time()

    @staticmethod
    def get_date_as_string_from_date_time(date_time) -> str:  # '2018-07-18'
        date_time_object = MyPyDate.get_datetime_object(date_time)
        return date_time_object.strftime('%Y-%m-%d')

    @staticmethod
    def get_date_from_datetime(date_time):
        if date_time is None:
            return None
        if date_time.__class__.__name__ == 'date':  # no change
            return date_time
        return datetime.strptime(str(date_time), '%Y-%m-%d %H:%M:%S').date()

    @staticmethod
    def get_time_from_datetime(date_time):
        if date_time is None:
            return None
        if date_time.__class__.__name__ == 'time':  # no change
            return date_time
        return datetime.strptime(str(date_time), '%Y-%m-%d %H:%M:%S').time()

    @staticmethod
    def get_number_for_date_time(date_time):
        time_difference = date_time - datetime(2010, 1, 1)
        difference_in_seconds = (time_difference.days * 86400) + time_difference.seconds
        return difference_in_seconds

    @staticmethod
    def get_date_from_number(num: int):
        return (datetime(1, 1, 1) + timedelta(days=num)).date()


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