"""
Description: This module contains different string classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-21
"""
from datetime import datetime, timedelta


class MyString:
    @staticmethod
    def surround(text: str, surrounding='****'):
        return '\n{}{}{}'.format(surrounding, text, surrounding)
