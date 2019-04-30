"""
Description: This module contains different text helper classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-14
"""
import urllib.parse


class MyText:
    @staticmethod
    def get_next_best_abbreviation(text: str, length: int, tolerance_pct=10, exact=False, suffix='...') -> str:
        max_length = length if exact else length + int((100 + tolerance_pct)/100)
        if len(text) <= max_length:
            return text
        for k in range(length, max_length + 1):
            if text[k] in [' ', ',', ';']:
                return '{}{}'.format(text[:k], suffix)
        return '{}{}'.format(text[:max_length+1], suffix)

    @staticmethod
    def get_url_encode_plus(input_string):
        return urllib.parse.quote_plus(input_string)
