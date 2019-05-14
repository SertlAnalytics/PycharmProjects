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

    @staticmethod
    def get_option_label(input_string: str):
        replace_dict = {' ': '', ':': '_', '&': '_', '+': ''}
        return MyText.replace_by_dict(input_string, replace_dict)
    
    @staticmethod
    def get_with_replaced_umlaute(input_string: str) -> str:
        umlaute_dict = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'}
        return MyText.replace_by_dict(input_string, umlaute_dict)

    @staticmethod
    def are_values_identical(value_01: str, value_02: str) -> bool:
        replace_dict = {' ': '', '\n': ''}
        value_01_changed = str(value_01)
        value_02_changed = str(value_02)
        for old_value, new_value in replace_dict.items():
            value_01_changed = value_01_changed.replace(old_value, new_value)
            value_02_changed = value_02_changed.replace(old_value, new_value)
        return value_01_changed == value_02_changed

    @staticmethod
    def replace_by_dict(input_string, replacement_dict):
        for old_value, new_value in replacement_dict.items():
            if input_string.find(old_value) > -1:
                input_string = input_string.replace(old_value, new_value)
        return input_string
