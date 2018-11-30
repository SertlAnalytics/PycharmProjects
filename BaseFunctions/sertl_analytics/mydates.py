"""
Description: This module contains different date time helper classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-21
"""
from datetime import datetime, timedelta, date
from time import mktime
import matplotlib.dates as m_dates


class MyDate:
    @staticmethod
    def time_stamp_now() -> int:
        return int(datetime.now().timestamp())

    @staticmethod
    def date_time_now_str() -> str:
        dt_now = datetime.now()
        return '{} {}'.format(MyDate.get_date_from_datetime(dt_now), MyDate.get_time_from_datetime(dt_now))

    @staticmethod
    def get_datetime_object(date_time=None):
        if date_time is None:
            return datetime.now()
        if date_time.__class__.__name__ == 'datetime':  # no change
            return date_time
        if len(str(date_time)) == 10:
            return datetime.strptime(str(date_time), '%Y-%m-%d')
        else:
            return datetime.strptime(str(date_time), '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_epoch_seconds_from_datetime(date_time=None) -> int:
        if date_time is None:
            return int(datetime.timestamp(datetime.now()))
        date_time_object = MyDate.get_datetime_object(date_time)
        return int(datetime.timestamp(date_time_object))

    @staticmethod
    def get_epoch_seconds_for_date(date_time=None) -> int:
        if date_time is None:
            return int(mktime(datetime.today().date().timetuple()))
        date_time_object = MyDate.get_datetime_object(date_time)
        return int(mktime(date_time_object.date().timetuple()))

    @staticmethod
    def get_epoch_seconds_for_current_day_as_list(interval=4) -> list:
        ts_base = MyDate.get_epoch_seconds_for_date()
        increment = 60 * 60 * int(24/interval)
        return [ts_base + k * increment for k in range(0, interval)]

    @staticmethod
    def get_epoch_number_from_datetime(date_time) -> float:
        if date_time is None:
            return 0
        date_time_object = MyDate.get_datetime_object(date_time)
        return m_dates.date2num(date_time_object)

    @staticmethod
    def get_datetime_from_epoch_number(epoch_number: float) -> datetime:
        return m_dates.num2date(epoch_number)

    @staticmethod
    def get_date_as_number_from_epoch_seconds(epoch_seconds: int) -> float:
        return m_dates.date2num(MyDate.get_date_time_from_epoch_seconds(epoch_seconds))

    @staticmethod
    def get_date_time_from_epoch_seconds(epoch_seconds: float) -> datetime:
       return datetime.fromtimestamp(epoch_seconds)

    @staticmethod
    def get_date_time_from_epoch_seconds_as_string(epoch_seconds: float) -> str:
        return '{} {}'.format(MyDate.get_date_from_epoch_seconds(epoch_seconds),
                              MyDate.get_time_from_epoch_seconds(epoch_seconds))

    @staticmethod
    def get_date_time_t_from_epoch_seconds(epoch_seconds: float) -> datetime:
        dt = datetime.fromtimestamp(epoch_seconds)
        return str(dt.date()) + 'T' + str(dt.time())[:8]

    @staticmethod
    def get_date_as_number_difference_from_epoch_seconds(epoch_seconds_1: int, epoch_seconds_2: int) -> float:
        off_set = 1000000  # must be at least this number
        date_as_number_1 = MyDate.get_date_as_number_from_epoch_seconds(off_set + epoch_seconds_1)
        date_as_number_2 = MyDate.get_date_as_number_from_epoch_seconds(off_set + epoch_seconds_2)
        return abs(date_as_number_1 - date_as_number_2)

    @staticmethod
    def get_date_from_epoch_seconds(epoch_seconds: int) -> datetime:
        return datetime.fromtimestamp(epoch_seconds).date()

    @staticmethod
    def get_time_from_epoch_seconds(epoch_seconds: int) -> datetime:
        return datetime.fromtimestamp(epoch_seconds).time()

    @staticmethod
    def get_date_as_string_from_date_time(date_time) -> str:  # '2018-07-18'
        date_time_object = MyDate.get_datetime_object(date_time)
        return date_time_object.strftime('%Y-%m-%d')

    @staticmethod
    def get_date_time_as_string_from_date_time(date_time, dt_format='%Y-%m-%d %H:%M:%S') -> str:  # '2018-07-18 hh:mm:ss'
        date_time_object = MyDate.get_datetime_object(date_time)
        return date_time_object.strftime(dt_format)

    @staticmethod
    def get_date_from_datetime(date_time=None):
        if date_time is None:
            return datetime.now().date()
        if date_time.__class__.__name__ == 'date':  # no change
            return date_time
        if len(str(date_time)) == 10:
            return datetime.strptime(str(date_time), '%Y-%m-%d').date()
        else:
            return datetime.strptime(str(date_time)[:19], '%Y-%m-%d %H:%M:%S').date()

    @staticmethod
    def get_time_from_datetime(date_time):
        if date_time is None:
            return None
        if date_time.__class__.__name__ == 'time':  # no change
            return date_time
        return datetime.strptime(str(date_time)[:19], '%Y-%m-%d %H:%M:%S').time()

    @staticmethod
    def get_number_for_date_time(date_time):
        time_difference = date_time - datetime(2010, 1, 1)
        difference_in_seconds = (time_difference.days * 86400) + time_difference.seconds
        return difference_in_seconds

    @staticmethod
    def get_date_from_number(num: int):
        return (datetime(1, 1, 1) + timedelta(days=num)).date()

    @staticmethod
    def adjust_by_days(date_time, days: int):
        if type(date_time) is str:
            date_time = MyDate.get_date_from_datetime(date_time)
        if type(date_time) is date:
            return (date_time + timedelta(days=days))
        return (date_time + timedelta(days=days)).date()


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