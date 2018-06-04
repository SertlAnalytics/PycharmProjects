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