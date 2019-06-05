"""
Description: This module contains different text helper classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-14
"""
import urllib.parse
from sertl_analytics.test.my_test_abc import TestInterface
import re


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
    def get_text_for_markdown(input_string: str) -> str:
        replace_dict = {'[': '\[', ']': '\]'}
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

    @staticmethod
    def replace_substring(string_orig: str, string_old: str, string_new: str) -> str:
        start_list = [match.start() for match in re.finditer(string_old, string_orig, flags=re.IGNORECASE)]
        if len(start_list) > 0:
            len_old_value = len(string_old)
            start_list.sort(reverse=True)
            for start_pos in start_list:
                string_orig = string_orig[:start_pos] + string_new + string_orig[start_pos + len_old_value:]
        return string_orig


class MyTextTest(MyText, TestInterface):
    REPLACE_SUBSTRING = 'replace_substring'

    def __init__(self, print_all_test_cases_for_units=False):
        TestInterface.__init__(self, print_all_test_cases_for_units)

    def test_replace_substring(self):
        """
         def divide(dividend: float, divisor: float, round_decimals = 2, return_value_on_error = 0):
        if divisor == 0:
            return return_value_on_error
        return round(dividend/divisor, round_decimals)
        :return:
        """
        test_case_dict = {
            'Several replacements': [
                self.replace_substring('Das ist ein Text mit GoreTex und goretex und Goretex', 'Goretex', 'Gore-Tex'),
                'Das ist ein Text mit Gore-Tex und Gore-Tex und Gore-Tex'
            ],
            'One replacements': [
                self.replace_substring('Das ist ein Text mit GoreTex', 'Goretex', 'Gore-Tex'),
                'Das ist ein Text mit Gore-Tex'
            ],
        }
        return self.__verify_test_cases__(self.REPLACE_SUBSTRING, test_case_dict)

    def __get_class_name_tested__(self):
        return MyText.__name__

    def __run_test_for_unit__(self, unit: str) -> bool:
        if unit == self.REPLACE_SUBSTRING:
            return self.test_replace_substring()

    def __get_test_unit_list__(self):
        return [self.REPLACE_SUBSTRING]
