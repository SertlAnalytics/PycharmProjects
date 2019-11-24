"""
Description: This module contains different text helper classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-14
"""
import urllib.parse
from sertl_analytics.test.my_test_abc import TestInterface
from sertl_analytics.mymath import MyMath
import re
import datetime


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
    def trim(input_string: str):
        output_string = input_string.strip()
        while '  ' in output_string:
            output_string = output_string.replace('  ', ' ')
        return output_string

    @staticmethod
    def split_at_first(input_string: str, delimiter: str) -> list:
        position = input_string.find(delimiter)
        if position <= 0:
            return [MyText.trim(input_string), '']
        else:
            return [MyText.trim(input_string[:position]), MyText.trim(input_string[position+1:])]

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

    @staticmethod
    def get_dict_from_text(text: str) -> dict:
        # {'Validity_Datetime': '2019-06-15 12:00:00'# 'Validity_Timestamp': 1560592800# 'Location': 'Bitfinex'# 'Equity_Type': 'Crypto_Currencies'# 'Equity_Type_ID': 20# 'Equity_ID': 'XRP'# 'Equity_Name': 'XRP'# 'Quantity': 9980.0# 'Value_Unit': 0# 'Value_Total': 4031.92# 'Currency': 'USD'}
        # {'Equity_Type': 'Crypto_Currencies'# 'Equity_Type_ID': 20# 'Period': 'INTRADAY'# 'Period_ID': 0# 'Aggregation': 15# 'Ticker_ID': 'BABUSD'# 'Ticker_Name': 'BABUSD'# 'Wave_Type': 'ascending'# 'Wave_Type_ID': 1# 'Wave_Structure': 'Short_long_short'# 'Wave_Structure_ID': 2# 'W1_Begin_Timestamp': 1560531600# 'W1_Begin_Datetime': '2019-06-14 19:00:00'# 'W1_Begin_Value': 400.3# 'W2_Begin_Timestamp': 1560536100# 'W2_Begin_Datetime': '2019-06-14 20:15:00'# 'W2_Begin_Value': 406.4# 'W3_Begin_Timestamp': 1560540600# 'W3_Begin_Datetime': '2019-06-14 21:30:00'# 'W3_Begin_Value': 403.0# 'W4_Begin_Timestamp': 1560555900# 'W4_Begin_Datetime': '2019-06-15 01:45:00'# 'W4_Begin_Value': 422.0# 'W5_Begin_Timestamp': 1560557700# 'W5_Begin_Datetime': '2019-06-15 02:15:00'# 'W5_Begin_Value': 417.4# 'Wave_End_Timestamp': 1560564900# 'Wave_End_Datetime': '2019-06-15 04:15:00'# 'Wave_End_Value': 424.0# 'W1_Range': 6.1# 'W2_Range': 3.4# 'W3_Range': 19.0# 'W4_Range': 4.6# 'W5_Range': 6.6# 'Parent_Wave_OID': 0# 'Wave_in_parent': ''# 'Wave_End_Flag': -1# 'Wave_Max_Retr_PCT': 0# 'Wave_Max_Retr_Timestamp_PCT': 0# 'FC_Timestamp': 0# 'FC_Datetime': ''# 'FC_C_Wave_End_Flag': -1# 'FC_C_Wave_Max_Retr_PCT': 0# 'FC_C_Wave_Max_Retr_Timestamp_PCT': 0# 'FC_R_Wave_End_Flag': -1# 'FC_R_Wave_Max_Retr_PCT': 0# 'FC_R_Wave_Max_Retr_Timestamp_PCT': 0}
        dict_pairs = {'"': '"', "'": "'", '{': '}', '[': ']', '(': ')'}
        cut_positions = []
        pair_start = ''
        pair_start_counter = 0
        for i in range(0, len(text)):
            i_char = text[i]
            if i_char == '{' and len(cut_positions) == 0:
                cut_positions.append(i)
            else:
                if len(cut_positions) > 0:
                    if i_char in dict_pairs and pair_start == '':
                            pair_start = i_char
                            pair_start_counter = 1
                    elif pair_start != '' and dict_pairs[pair_start] == i_char:
                        pair_start = ''
                        pair_start_counter = 0
                    elif i_char == ',' and pair_start_counter == 0:
                        cut_positions.append(i)
                    elif i_char == '}' and pair_start_counter == 0:
                        cut_positions.append(i)
        return_dict = {}
        for idx in range(0, len(cut_positions) - 1):
            cut_start = cut_positions[idx]
            cut_end = cut_positions[idx + 1]
            entry = text[cut_start + 1:cut_end]
            key_value_parts = entry.split(': ')
            key = key_value_parts[0].strip()
            key = MyText.get_string_without_hyphen(key)
            value = key_value_parts[1].strip()
            value = MyText.get_string_without_hyphen(value)
            return_dict[key] = value
        return return_dict

    @staticmethod
    def is_number(value):
        try:
            float(value)  # for int, long and float
        except ValueError:
            return False
        return True

    @staticmethod
    def is_date_time_date(value: str):
        return value.find('datetime.date') >= 0

    @staticmethod
    def get_date_time_date(value: str):
        parameter_string = value[value.find('(')+1:value.find(')')]
        parameters = parameter_string.split(',')
        year, month, day = int(parameters[0]), int(parameters[1]), int(parameters[2])
        return datetime.date(year=year, month=month, day=day)

    @staticmethod
    def is_date_time_time(value: str):
        return value.find('datetime.time') >= 0

    @staticmethod
    def get_date_time_time(value: str):
        parameter_string = value[value.find('(') + 1:value.find(')')]
        parameters = parameter_string.split(',')
        hour, minute = int(parameters[0]), int(parameters[1])
        return datetime.time(hour=hour, minute=minute)

    @staticmethod
    def get_string_without_hyphen(text: str):
        text = text.replace("'", "")
        return text.replace('"', '')

    @staticmethod
    def get_list_from_text(text: str) -> list:
        # [entry1, entry2, ...] where entryNN could be text, dict, list, ....
        dict_pairs = {'"': '"', "'": "'", '{': '}', '[': ']'}
        cut_positions = []
        pair_start = ''
        pair_start_counter = 0
        for i in range(0, len(text)):
            i_char = text[i]
            if i_char == '[' and len(cut_positions) == 0:
                cut_positions.append(i)
            else:
                if len(cut_positions) > 0:
                    if i_char in dict_pairs:
                        if pair_start == '':
                            pair_start = i_char
                            pair_start_counter = 1
                        elif pair_start == i_char:
                            pair_start_counter += 1
                    elif pair_start != '' and dict_pairs[pair_start] == i_char:
                        pair_start_counter -= 1
                    elif i_char == ',' and pair_start_counter == 0:
                        cut_positions.append(i)
                    elif i_char == ']' and pair_start_counter == 0:
                        cut_positions.append(i)
        return_list = []
        for idx in range(0, len(cut_positions) - 1):
            cut_start = cut_positions[idx]
            cut_end = cut_positions[idx + 1]
            entry = text[cut_start + 1:cut_end]
            return_list.append(entry.strip())
        return return_list


class MyTextTest(MyText, TestInterface):
    REPLACE_SUBSTRING = 'replace_substring'
    GET_LIST_FROM_TEXT = 'get_list_from_text'
    GET_DICT_FROM_TEXT = 'get_dict_from_text'

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

    def test_get_list_from_text(self):
        test_case_dict = {
            'Flat list': [self.get_list_from_text('[entry1, entry2, ...]'), ['entry1', 'entry2', '...']],
            'Interleaved list': [
                self.get_list_from_text('[{entry1, {entry2}, ...}, {entry1, entry2, ...}]'),
                ['{entry1, {entry2}, ...}', '{entry1, entry2, ...}']]
        }
        return self.__verify_test_cases__(self.GET_LIST_FROM_TEXT, test_case_dict)

    def test_get_dict_from_text(self):
        test_case_dict = {
            'Simple dict': [
                self.get_dict_from_text(
                    "{'Validity_Datetime': '2019-06-15 12:00:00', 'Validity_Timestamp': 1560592800, "
                    "'Location': 'Bitfinex', 'Equity_Type': 'Crypto_Currencies', 'Equity_Type_ID': 20, "
                    "'Equity_ID': 'XRP', 'Equity_Name': 'XRP', 'Quantity': 9980.0, 'Value_Unit': 0, "
                    "'Value_Total': 4031.92, 'Currency': 'USD'}"),
                {'Validity_Datetime': '2019-06-15 12:00:00', 'Validity_Timestamp': '1560592800', 'Location': 'Bitfinex',
                 'Equity_Type': 'Crypto_Currencies', 'Equity_Type_ID': '20', 'Equity_ID': 'XRP', 'Equity_Name': 'XRP',
                 'Quantity': '9980.0', 'Value_Unit': '0', 'Value_Total': '4031.92', 'Currency': 'USD'}
            ],
            'Complex dict': [
                self.get_dict_from_text(
                    "{'Period': 'INTRADAY', 'Aggregation': 15, 'Symbol': 'XRPUSD', 'Timestamp': 1560784500, "
                    "'Date': datetime.date(2019, 6, 17), 'Time': datetime.time(17, 15), 'Open': 0.433, "
                    "'High': 0.434, 'Low': 0.432, 'Close': 0.434, 'Volume': 169404.0, 'BigMove': False, 'Direction': 0}"),
                {'Period': 'INTRADAY', 'Aggregation': '15', 'Symbol': 'XRPUSD', 'Timestamp': '1560784500',
                 'Date': 'datetime.date(2019, 6, 17)', 'Time': 'datetime.time(17, 15)', 'Open': '0.433', 'High': '0.434',
                 'Low': '0.432', 'Close': '0.434', 'Volume': '169404.0', 'BigMove': 'False', 'Direction': '0'}
            ]
        }
        return self.__verify_test_cases__(self.GET_LIST_FROM_TEXT, test_case_dict)

    def __get_class_name_tested__(self):
        return MyText.__name__

    def __run_test_for_unit__(self, unit: str) -> bool:
        if unit == self.REPLACE_SUBSTRING:
            return self.test_replace_substring()
        elif unit == self.GET_LIST_FROM_TEXT:
            return self.test_get_list_from_text()
        elif unit == self.GET_DICT_FROM_TEXT:
            return self.test_get_dict_from_text()

    def __get_test_unit_list__(self):
        return [self.REPLACE_SUBSTRING, self.GET_LIST_FROM_TEXT, self.GET_DICT_FROM_TEXT]
