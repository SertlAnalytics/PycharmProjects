"""
Description: This module contains different date time helper classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-21
"""
from sertl_analytics.constants.pattern_constants import DTRG, PRD
from datetime import datetime, timedelta, date
from time import mktime
import matplotlib.dates as m_dates
from sertl_analytics.test.my_test_abc import TestInterface
import math


class MyDate:
    @staticmethod
    def weekday():  # Monday = 0, ..., Sunday = 6
        return datetime.today().weekday()

    @staticmethod
    def time_stamp_now() -> int:
        return int(datetime.now().timestamp())

    @staticmethod
    def get_seconds_for_period_aggregation(period: str, aggregation=1):
        if period == PRD.DAILY:
            return MyDate.get_seconds_for_period(days=1)
        elif period == PRD.INTRADAY:
            return MyDate.get_seconds_for_period(min=aggregation)
        elif period == PRD.WEEKLY:
            return MyDate.get_seconds_for_period(days=7)
        return 0

    @staticmethod
    def get_seconds_for_period(days=0.0, hours=0.0, min=0.0) -> int:
        second_days = 60 * 60 * 24
        second_hours = 60 * 60
        second_min = 60
        return int(days * second_days + hours * second_hours + min * second_min)

    @staticmethod
    def get_offset_timestamp(days=0.0, hours=0.0, minutes=0.0):
        if days == 0:
            return MyDate.time_stamp_now() + MyDate.get_seconds_for_period(days, hours, minutes)
        return MyDate.get_epoch_seconds_for_date() + MyDate.get_seconds_for_period(days, hours, minutes)

    @staticmethod
    def get_offset_timestamp_for_period_aggregation(number: int, period: str, aggregation: int):
        if period == PRD.DAILY:
            return MyDate.get_offset_timestamp(days=-number)
        else:
            return MyDate.get_offset_timestamp(minutes=-number * aggregation)

    @staticmethod
    def time_now_str() -> str:
        dt_now = datetime.now()
        return '{}'.format(MyDate.get_time_from_datetime(dt_now))

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
    def get_time_difference_to_now_in_minutes(time_01: str) -> int:
        time_01 = time_01 if len(time_01) == 8 else '{}:00'.format(time_01)
        return int(MyDate.get_time_difference_in_seconds(time_01)/60)

    @staticmethod
    def get_time_difference_in_seconds(time_01, time_02=None) -> int:
        if type(time_01) is datetime:
            epoch_seconds_01 = MyDate.get_epoch_seconds_from_datetime(time_01)
        else:
            epoch_seconds_01 = MyDate.get_epoch_seconds_for_current_day_time(time_01)

        if time_02 is None:
            epoch_seconds_02 = MyDate.get_epoch_seconds_from_datetime()
        else:
            if type(time_02) is datetime:
                epoch_seconds_02 = MyDate.get_epoch_seconds_from_datetime(time_02)
            else:
                epoch_seconds_02 = MyDate.get_epoch_seconds_for_current_day_time(time_02)
        return epoch_seconds_01 - epoch_seconds_02

    @staticmethod
    def get_epoch_seconds_for_current_day_time(time: str) -> int:
        time = time if len(time) == 8 else '{}:00'.format(time)
        dt_str = MyDate.get_date_as_string_from_date_time()
        return MyDate.get_epoch_seconds_from_datetime('{} {}'.format(dt_str, time))

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
    def get_date_time_from_epoch_seconds_as_string(epoch_seconds: int) -> str:
        date_str = str(MyDate.get_date_from_epoch_seconds(epoch_seconds))
        time_str = str(MyDate.get_time_from_epoch_seconds(epoch_seconds))
        return '{} {}'.format(date_str, time_str[:8])

    @staticmethod
    def get_date_time_t_from_epoch_seconds(epoch_seconds: float) -> str:
        dt = datetime.fromtimestamp(epoch_seconds)
        return str(dt.date()) + 'T' + str(dt.time())[:8]

    @staticmethod
    def get_date_as_number_difference_from_epoch_seconds(epoch_seconds_1: int, epoch_seconds_2: int) -> float:
        off_set = 1000000  # must be at least this number
        date_as_number_1 = MyDate.get_date_as_number_from_epoch_seconds(off_set + epoch_seconds_1)
        date_as_number_2 = MyDate.get_date_as_number_from_epoch_seconds(off_set + epoch_seconds_2)
        return abs(date_as_number_1 - date_as_number_2)

    @staticmethod
    def get_date_from_epoch_seconds(epoch_seconds: int) -> date:
        return datetime.fromtimestamp(epoch_seconds).date()

    @staticmethod
    def get_time_stamp_rounded_to_previous_hour(epoch_seconds: int):
        seconds_per_hour = MyDate.get_seconds_for_period(hours=1)
        remaining_seconds = epoch_seconds % seconds_per_hour
        return epoch_seconds - remaining_seconds

    @staticmethod
    def get_time_from_epoch_seconds(epoch_seconds: int):
        return datetime.fromtimestamp(epoch_seconds).time()

    @staticmethod
    def get_date_as_string_from_date_time(date_time=None) -> str:  # '2018-07-18'
        date_time_object = MyDate.get_datetime_object(date_time)
        return date_time_object.strftime('%Y-%m-%d')

    @staticmethod
    def get_date_time_as_string_from_date_time(date_time=None, dt_format='%Y-%m-%d %H:%M:%S') -> str:  # '2018-07-18 hh:mm:ss'
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
    def get_time_str_from_datetime(date_time=None):
        time_str = str(MyDate.get_time_from_datetime(date_time))
        return time_str[:8]

    @staticmethod
    def get_time_from_datetime(date_time=None):
        if date_time is None:
            date_time = datetime.now()
        if date_time.__class__.__name__ == 'time':  # no change
            return date_time
        return datetime.strptime(str(date_time)[:19], '%Y-%m-%d %H:%M:%S').time()

    @staticmethod
    def get_date_str_from_datetime(date_time=None):
        if date_time is None:
            date_time = datetime.now()
        return str(MyDate.get_date_from_datetime(date_time))

    @staticmethod
    def get_number_for_date_time(date_time) -> int:
        if type(date_time) is str:
            date_time = MyDate.get_datetime_object(date_time)
        time_difference = date_time - datetime(2010, 1, 1)
        difference_in_seconds = (time_difference.days * 86400) + time_difference.seconds
        return difference_in_seconds

    @staticmethod
    def get_date_from_number(num: int):
        return (datetime(1, 1, 1) + timedelta(days=num)).date()

    @staticmethod
    def get_offset_date_for_date_range(date_range: str):
        if date_range == DTRG.TODAY:
            return MyDate.adjust_by_days(None, -1)
        if date_range == DTRG.CURRENT_WEEK:
            return MyDate.adjust_by_days(None, -7)
        if date_range == DTRG.CURRENT_MONTH:
            return MyDate.adjust_by_days(None, -31)

    @staticmethod
    def get_offset_time_stamp_for_date_range(date_range: str):
        time_stamp_now = MyDate.time_stamp_now()
        time_stamp_day = MyDate.get_seconds_for_period(days=1)
        if date_range == DTRG.TODAY:
            return time_stamp_now - time_stamp_day
        if date_range == DTRG.CURRENT_WEEK:
            return time_stamp_now - 7 * time_stamp_day
        if date_range == DTRG.CURRENT_MONTH:
            return time_stamp_now - 31 * time_stamp_day
        return 0

    @staticmethod
    def adjust_by_days(date_time, days: int):
        if date_time is None:
            date_time = MyDate.get_date_from_datetime()
        if type(date_time) is str:
            date_time = MyDate.get_date_from_datetime(date_time)
        if type(date_time) is date:
            return (date_time + timedelta(days=days))
        return (date_time + timedelta(days=days)).date()

    @staticmethod
    def adjust_by_seconds(date_time, seconds: int):
        if type(date_time) is str:
            date_time = MyDate.get_date_from_datetime(date_time)
        if type(date_time) is date:
            return (date_time + timedelta(seconds=seconds))
        return (date_time + timedelta(seconds=seconds))

    @staticmethod
    def is_tuesday_till_saturday(date_obj=None):
        date_obj = datetime.today() if date_obj is None else MyDate.get_datetime_object(date_obj)
        return date_obj.weekday() in [1, 2, 3, 4, 5]

    @staticmethod
    def is_monday_till_friday(date_obj=None):
        date_obj = datetime.today() if date_obj is None else MyDate.get_datetime_object(date_obj)
        return date_obj.weekday() in [0, 1, 2, 3, 4]

    @staticmethod
    def is_sunday(date_obj=None):
        date_obj = datetime.today() if date_obj is None else MyDate.get_datetime_object(date_obj)
        return date_obj.weekday() == 6

    @staticmethod
    def is_monday(date_obj=None):
        date_obj = datetime.today() if date_obj is None else MyDate.get_datetime_object(date_obj)
        return date_obj.weekday() == 0

    @staticmethod
    def get_time_stamp_list_for_time_stamp(time_stamp: int, numbers: int, period: str, aggregation=1):
        period_seconds_part = int(MyDate.get_seconds_for_period_aggregation(period, aggregation)/numbers)
        if period == PRD.DAILY:
            return [(time_stamp + k * period_seconds_part) for k in range(0, numbers)]
        else:
            return [(time_stamp - k * period_seconds_part) for k in range(0, numbers)]

    @staticmethod
    def get_weekdays_for_list(weekday_list: list):
        return [MyDate.get_weekday_for_number(number) for number in weekday_list]

    @staticmethod
    def get_weekday_for_number(weekday_number: int):
        weekday_dict = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        return weekday_dict.get(weekday_number, 'Sun')

    @staticmethod
    def get_nearest_time_in_list(time_list: list, forward=True):
        time_now_str = str(MyDate.get_time_from_datetime())
        diff_list = [0, math.inf]
        diff_start_time_list = ['', '']
        # 1. check: Is there any time this day after now?
        for start_time in time_list:
            seconds_start_time_to_now = MyDate.get_time_difference_in_seconds(start_time, time_now_str)
            if 0 < seconds_start_time_to_now <= diff_list[1]:
                # here want the smallest positive number
                diff_list[1] = seconds_start_time_to_now
                diff_start_time_list[1] = start_time[:5]
            elif seconds_start_time_to_now <= diff_list[0]:  # here we want to have the smallest negative number
                diff_list[0] = seconds_start_time_to_now
                diff_start_time_list[0] = start_time[:5]
        return diff_start_time_list[0] if diff_start_time_list[1] == '' else diff_start_time_list[1]


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


class MyDateTest(MyDate, TestInterface):
    GET_TIME_STAMP_ROUNDED_TO_PREVIOUS_HOUR = 'get_time_stamp_rounded_to_previous_hour'
    GET_OFFSET_TIMESTAMP_FOR_PERIOD_AGGREGATION = 'get_offset_timestamp_for_period_aggregation'
    GET_NEAREST_TIME_IN_LIST = 'get_nearest_time_in_list'
    GET_TIME_DIFFERNCE_IN_SECONDS = 'get_time_difference_in_seconds'

    def __init__(self, print_all_test_cases_for_units=False):
        TestInterface.__init__(self, print_all_test_cases_for_units)

    def test_get_time_difference_in_seconds(self):
        time_now_str = str(MyDate.get_time_from_datetime())

        test_list = [[['01:00', '01:10'], -600],
                     [['01:00', '00:55'], 300],
                     [[datetime.now(), datetime.now() + timedelta(seconds=10)], -10],
                     [['01:00', None], MyDate.get_epoch_seconds_for_current_day_time('01:00') - MyDate.time_stamp_now()],
                     [[datetime.now() + timedelta(seconds=10), None], 10],
                     ]
        test_case_dict = {}
        for test in test_list:
            test_data = test[0]
            key = '{}'.format(test_data)
            test_case_dict[key] = [self.get_time_difference_in_seconds(test_data[0], test_data[1]), test[1]]
        return self.__verify_test_cases__(self.GET_NEAREST_TIME_IN_LIST, test_case_dict)

    def test_get_nearest_time_in_list(self):
        time_now_str = str(MyDate.get_time_from_datetime())
        test_list = [[['01:00', '05:00', '12:00', '18:00', '22:00'], '18:00'],
                     [['01:00', '05:00'], '01:00'],
                     [['03:00', '01:00', '05:00'], '01:00'],
                      [['18:00', '22:00'], '18:00'],
                    ]

        test_case_dict = {}
        for test in test_list:
            key = '{}'.format(test[0])
            test_case_dict[key] = [self.get_nearest_time_in_list(test[0]), test[1]]
        return self.__verify_test_cases__(self.GET_NEAREST_TIME_IN_LIST, test_case_dict)

    def test_get_time_stamp_rounded_to_previous_hour(self):
        test_list = [[1552423400, 1552420800],
                     [1552424400, 1552424400],
                     [1552435400, 1552435200],
                     [1552446400, 1552446000]
                    ]

        test_case_dict = {}
        for test in test_list:
            key = '{}: {} expected {}'.format(
                test[0], MyDate.get_date_time_from_epoch_seconds_as_string(test[0]),
                MyDate.get_date_time_from_epoch_seconds_as_string(test[1]))
            test_case_dict[key] = [self.get_time_stamp_rounded_to_previous_hour(test[0]), test[1]]
        return self.__verify_test_cases__(self.GET_TIME_STAMP_ROUNDED_TO_PREVIOUS_HOUR, test_case_dict)

    def test_get_offset_timestamp_for_period_aggregation(self):
        """
        def get_offset_timestamp_for_period_aggregation(number: int, period: str, aggregation: int):
        if period == PRD.DAILY:
            return MyDate.get_offset_timestamp(days=-number)
        else:
            return MyDate.get_offset_timestamp(min=-number * aggregation)
        """
        base_day = MyDate.get_epoch_seconds_for_date()
        seconds_for_day = MyDate.get_seconds_for_period(days=1)
        time_stamp_now = MyDate.time_stamp_now()
        test_list = [[[1, PRD.DAILY, 1], base_day - seconds_for_day],
                     [[-1, PRD.DAILY, 1], base_day + seconds_for_day],
                     [[1, PRD.INTRADAY, 15], time_stamp_now - 15 * 60],
                     [[-1, PRD.INTRADAY, 30], time_stamp_now + 30 * 60],
                     ]

        test_case_dict = {}
        for entry in test_list:
            test = entry[0]
            expected = entry[1]
            key = '{}'.format(test)
            offset_time_stamp = self.get_offset_timestamp_for_period_aggregation(test[0], test[1], test[2])
            offset_date_time = MyDate.get_date_time_from_epoch_seconds_as_string(offset_time_stamp)
            expected_offset_date_time = MyDate.get_date_time_from_epoch_seconds_as_string(expected)
            test_case_dict[key] = [offset_time_stamp, expected]
        return self.__verify_test_cases__(self.GET_OFFSET_TIMESTAMP_FOR_PERIOD_AGGREGATION, test_case_dict)

    def __get_class_name_tested__(self):
        return MyDate.__name__

    def __run_test_for_unit__(self, unit: str) -> bool:
        if unit == self.GET_TIME_STAMP_ROUNDED_TO_PREVIOUS_HOUR:
            return self.test_get_time_stamp_rounded_to_previous_hour()
        elif unit == self.GET_OFFSET_TIMESTAMP_FOR_PERIOD_AGGREGATION:
            return self.test_get_offset_timestamp_for_period_aggregation()
        elif unit == self.GET_NEAREST_TIME_IN_LIST:
            return self.test_get_nearest_time_in_list()
        elif unit == self.GET_TIME_DIFFERNCE_IN_SECONDS:
            return self.test_get_time_difference_in_seconds()

    def __get_test_unit_list__(self):
        # return [self.GET_TIME_DIFFERNCE_IN_SECONDS]
        return [self.GET_TIME_STAMP_ROUNDED_TO_PREVIOUS_HOUR,
                self.GET_OFFSET_TIMESTAMP_FOR_PERIOD_AGGREGATION,
                self.GET_NEAREST_TIME_IN_LIST,
                self.GET_TIME_DIFFERNCE_IN_SECONDS]