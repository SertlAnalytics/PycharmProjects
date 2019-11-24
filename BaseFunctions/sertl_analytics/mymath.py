"""
Description: This module contains the math classes for sertl-analytics
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-07-24
"""

import numpy as np
from scipy.stats import entropy
import pandas as pd
import math
from sertl_analytics.test.my_test_abc import TestInterface


class MyEntropy:
    def __init__(self, value_prob: float):
        self._v_p = value_prob
        self._not_v_p = 1 - self._v_p
        self._entropy = self.__get_entropy__()

    @property
    def entropy(self):
        return self._entropy

    def __get_entropy__(self):
        if self._v_p == 0 or self._v_p == 1:
            return 0
        return round(-self._v_p * np.log2(self._v_p) - self._not_v_p * np.log2(self._not_v_p), 3)


class ParentEntropy:
    def __init__(self, df: pd.DataFrame, label: str, label_value):
        self._df = df
        self._label = label
        self._label_value = label_value
        self._elements_total = self._df.shape[0]
        self._elements_for_label_value = self._df[self._df[label] == label_value].shape[0]
        self._probability_for_label_value = round(self._elements_for_label_value / self._elements_total, 3)
        self._entropy_obj = MyEntropy(self._probability_for_label_value)
        self._child_entropy_list = []

    def add_children_entropies_for_feature(self, feature: str):
        pass

    @property
    def entropy(self):
        return self._entropy_obj.entropy

    @property
    def label(self):
        return self._label

    @property
    def label_value(self):
        return self._label_value

    @property
    def elements_for_label_value(self):
        return self._elements_for_label_value

    @property
    def probability(self):
        return self._probability_for_label_value


class ChildEntropy:
    def __init__(self, parent: ParentEntropy, df: pd.DataFrame, feature: str, feature_value):
        self._parent = parent
        self._df = df
        self._feature = feature
        self._feature_value = feature_value
        self._elements_total = self._df.shape[0]
        self._label = self._parent.label
        self._label_value = self._parent.label_value
        self._elements_with_label_value = self._parent.elements_for_label_value
        self._elements_with_feature_value_total = self._df[self._df[feature] == feature_value].shape[0]
        self._probability_for_feature_value = round(self._elements_with_feature_value_total / self._elements_total, 3)
        self._elements_with_feature_label_values = self.__get_elements_with_feature_label_values__()
        self._probability_for_feature_value_resp_label_value = \
            round(self._elements_with_feature_label_values / self._elements_with_feature_value_total, 3)
        self._entropy_obj = MyEntropy(self._probability_for_feature_value_resp_label_value)

    def __get_elements_with_feature_label_values__(self):
        df_feature_label_values = self.__get_df_with_feature_and_label_values__()
        return df_feature_label_values.shape[0]

    def __get_df_with_feature_and_label_values__(self):
        return self._df[
            np.logical_and(self._df[self._feature] == self._feature_value, self._df[self._label] == self._label_value)]

    @property
    def entropy(self):
        return self._entropy_obj.entropy

    @property
    def label(self):
        return self._label

    @property
    def label_value(self):
        return self._label_value

    @property
    def feature(self):
        return self._feature

    @property
    def feature_value(self):
        return self._feature_value

    @property
    def information_gain_contribution(self):
        return self._probability_for_feature_value * self._entropy_obj.entropy


class EntropyHandler:
    def __init__(self, df: pd.DataFrame, labels: list, features: list):
        self._df = df
        self._elements_total = self._df.shape[0]
        self._labels = labels
        self._features = features
        self._unique_label_value_dict = {}
        self._unique_feature_value_dict = {}
        self.__fill_unique_label_value_dict__()
        self.__fill_unique_feature_value_dict__()
        self._parent_entropy_list = []
        self._child_entropy_list = []
        self.__fill_parent_entropy_list__()
        self.__fill_child_entropy_list__()

    def calculate_information_gain_for_label_and_feature(self, label: str, feature: str):
        if self.__is_calculation_information_gain_too_complex__(label, feature):
            label_v = len(self._unique_label_value_dict[label])
            feature_v = len(self._unique_feature_value_dict[feature])
            return ['label_values={}, feature_values={} ({})'.format(label_v, feature_v, label_v * feature_v)]
        parent_value_entropy_dict = {}
        parent_value_probability_dict = {}
        parent_value_child_correction_dict = {}
        parent_entropy_list_for_label = [p_e for p_e in self._parent_entropy_list if p_e.label == label]
        for parent_entropy in parent_entropy_list_for_label:
            label_value = parent_entropy.label_value
            parent_value_entropy_dict[label_value] = parent_entropy.entropy
            parent_value_probability_dict[label_value] = parent_entropy.probability
            parent_value_child_correction_dict[label_value] = 0
            child_list = self.__get_child_entropy_list_for_feature_and_parent_entropy__(feature, parent_entropy)
            for child_entropy in child_list:
                parent_value_child_correction_dict[label_value] += child_entropy.information_gain_contribution
        parent_entropy_weighted = 0
        child_correction_weighted = 0
        for label_value in parent_value_probability_dict:
            probability = parent_value_probability_dict[label_value]
            entropy = parent_value_entropy_dict[label_value]
            child_correction = parent_value_child_correction_dict[label_value]
            parent_entropy_weighted += probability * entropy
            child_correction_weighted += probability * child_correction
        parent_entropy_weighted = round(parent_entropy_weighted, 4)
        information_gain = round(parent_entropy_weighted - child_correction_weighted, 4)
        child_correction_weighted = round(child_correction_weighted, 4)
        if parent_entropy_weighted == 0:
            percentage = '{:.1f}%'.format(100)
        else:
            percentage = '{:.1f}%'.format(information_gain/parent_entropy_weighted*100)
        return [parent_entropy_weighted, child_correction_weighted, information_gain, percentage]

    def __is_calculation_information_gain_too_complex__(self, label, feature) -> bool:
        return len(self._unique_label_value_dict[label]) * len(self._unique_feature_value_dict[feature]) > 100

    def __get_child_entropy_list_for_feature_and_parent_entropy__(self, feature: str, p_e: ParentEntropy):
        return [e for e in self._child_entropy_list
                if e.label == p_e.label and e.label_value == p_e.label_value and e.feature == feature]

    def __fill_unique_label_value_dict__(self):
        for label in self._labels:
            self._unique_label_value_dict[label] = self._df[label].unique()

    def __fill_unique_feature_value_dict__(self):
        for feature in self._features:
            self._unique_feature_value_dict[feature] = self._df[feature].unique()

    def __fill_parent_entropy_list__(self):
        for label in self._labels:
            for label_value in self._unique_label_value_dict[label]:
                self.__fill_parent_entropy_list_for_label__(label, label_value)

    def __fill_parent_entropy_list_for_label__(self, label: str, label_value):
         parent_entropy_obj = ParentEntropy(self._df, label, label_value)
         self._parent_entropy_list.append(parent_entropy_obj)

    def __fill_child_entropy_list__(self):
        for parent_entropy in self._parent_entropy_list:
            for feature in self._features:
                if not self.__is_calculation_information_gain_too_complex__(parent_entropy.label, feature):
                    for feature_value in self._unique_feature_value_dict[feature]:
                        child_entropy_obj = ChildEntropy(parent_entropy, self._df, feature, feature_value)
                        self._child_entropy_list.append(child_entropy_obj)


class MyMath:
    @staticmethod
    def divide(dividend: float, divisor: float, round_decimals = 2, return_value_on_error = 0):
        if divisor == 0:
            return return_value_on_error
        return round(dividend/divisor, round_decimals)

    @staticmethod
    def get_change_in_percentage(value_from: float, value_to: float, offset_value=0, decimal_round=1) -> float:
        value_change = value_to - value_from
        if offset_value == 0:
            offset_value = value_from
        if offset_value == 0:
            return 0
        return round(value_change/offset_value * 100, decimal_round)

    @staticmethod
    def get_change_in_pct(value_from: float, value_to: float, offset_value=0, decimal_round=3) -> float:
        value_change = value_to - value_from
        if offset_value == 0:
            offset_value = value_from
        if offset_value == 0:
            return 0
        return round(value_change / offset_value, decimal_round)

    @staticmethod
    def get_value_from_percentage_on_base_value(value_pct: float, value_base: float, decimal_round=2) -> float:
        return round(value_base + (value_base * value_pct/100), decimal_round)  # 10% = 10 percentage

    @staticmethod
    def get_value_from_pct_on_base_value(value_pct: float, value_base: float, decimal_round=2) -> float:
        return round(value_base + (value_base * value_pct), decimal_round)  # 10% = 0.10 pct

    @staticmethod
    def get_standard_deviation_for_regression(x, y, rounding=2):
        np_array = np.polyfit(x, y, 1)
        intercept, slope = np_array[1], np_array[0]
        y_reg = np.array([intercept + x_value * slope for x_value in x])
        y_changed_by_reg = y - y_reg
        std_y_changed_by_reg = y_changed_by_reg.std()
        return round(std_y_changed_by_reg, rounding)

    @staticmethod
    def round_smart_series(value_series: pd.Series) -> pd.Series:
        for (key, value) in value_series.iteritems():
            value_series[key] = MyMath.round_smart(value)
        return value_series

    @staticmethod
    def round_smart(value: float) -> float:
        if value == math.inf or value == -math.inf:
            return value
        if value == 0:
            return 0
        try:
            decimals = int(math.ceil(math.log10(abs(value))))
        except:
            print('Error')
        if decimals > 3:
            rounded_value = round(value)
            # to avoid problems with an additional .0 in print statements...
            return int(rounded_value) if rounded_value == int(rounded_value) else rounded_value
        elif decimals > 0:
            return round(value, 5 - decimals)
        return round(value, min(5, -decimals + 5))  # not more than 5 decimals after comma

    @staticmethod
    def get_float_for_string(value_str: str, delimiter='.'):
        if type(value_str) is not str:
            return value_str
        value_str = value_str.replace("'", "")  # remove thousand separators
        value_str = value_str.replace("´", "")  # remove thousand separators
        value_str = value_str.replace("-", "")  # remove -- signs
        value_str = value_str.replace(" ", "")  # remove spaces
        if value_str.lower() in ['', 'gratis', 'umsonst']:
            return 0
        if value_str[-1] == delimiter:
            value_str = value_str[:-1]
        if value_str.isnumeric():
            return int(value_str)
        if value_str.find(delimiter) < 0:
            print('Wrong price {}'.format(value_str))
            return 0
        price_components = value_str.split(delimiter)
        integer_part = price_components[0] if price_components[0].isnumeric() else 0
        fractional_part = price_components[1] if price_components[1].isnumeric() else 0
        return float('{}.{}'.format(integer_part, fractional_part))

    @staticmethod
    def is_number(value):
        try:
            float(value)  # for int, long and float
        except ValueError:
            return False
        return True


class MyMathTest(MyMath, TestInterface):
    DIVIDE = 'divide'
    ROUND_SMART = 'round_smart'

    def __init__(self, print_all_test_cases_for_units=False):
        TestInterface.__init__(self, print_all_test_cases_for_units)

    def test_divide(self):
        """
         def divide(dividend: float, divisor: float, round_decimals = 2, return_value_on_error = 0):
        if divisor == 0:
            return return_value_on_error
        return round(dividend/divisor, round_decimals)
        :return:
        """
        test_case_dict = {
            'divisor=0, return_value_on_error=default(0)': [self.divide(7, 0), 0],
            'divisor=0, return_value_on_error=2)': [self.divide(7, 0, return_value_on_error=2), 2],
            'round=default(2)': [self.divide(2, 3), 0.67],
            'round=3': [self.divide(2, 3, 3), 0.667],
            'round=4': [self.divide(2, 3, 4), 0.6667],
             }
        return self.__verify_test_cases__(self.DIVIDE, test_case_dict)

    def test_round_smart(self, print_all=False):
        """
        if value == 0:
            return 0
        decimals = int(math.ceil(math.log10(abs(value))))
        if decimals > 3:
            return round(value)
        elif decimals > 0:
            return round(value, 5 - decimals)
        return round(value, min(5, -decimals + 3))  # not more then 5 decimals after comma
        :return:
        """
        test_case_dict = {
            'value=0': [self.round_smart(0), 0],
            'decimals before comma > 3': [self.round_smart(9234.66666), 9235],
            'decimals before comma > 3 (2)': [self.round_smart(1234.66666), 1235],
            'decimals before comma = 3': [self.round_smart(999.66666), 999.67],
            'decimals before comma = 3 (2)': [self.round_smart(234.66666), 234.67],
            'decimals before comma = 2': [self.round_smart(34.66666), 34.667],
            'decimals before comma = 1': [self.round_smart(4.66666), 4.6667],
            'number < 1 and zeros after comma=0 (like 0.55555555)': [self.round_smart(0.55555555), 0.556],
            'number < 1 and zeros after comma=1 (like 0.05555555)': [self.round_smart(0.05555555), 0.0556],
            'number < 1 and zeros after comma=2 (like 0.00555555)': [self.round_smart(0.00555555), 0.00556],
            'number < 1 and zeros after comma=3 (like 0.00055555)': [self.round_smart(0.00055555), 0.00056],
            'number < 1 and zeros after comma=4 (like 0.00005555)': [self.round_smart(0.00005555), 0.00006],
            'number < 1 and zeros after comma=5 (like 0.00000555)': [self.round_smart(0.00000555), 0.00001],
            'number < 1 and zeros after comma=6 (like 0.00000055)': [self.round_smart(0.00000055), 0],
        }
        return self.__verify_test_cases__(self.ROUND_SMART, test_case_dict)

    def __get_class_name_tested__(self):
        return MyMath.__name__

    def __run_test_for_unit__(self, unit: str) -> bool:
        if unit == self.DIVIDE:
            return self.test_divide()
        elif unit == self.ROUND_SMART:
            return self.test_round_smart()

    def __get_test_unit_list__(self):
        return [self.DIVIDE, self.ROUND_SMART]


class MyPoly1d:
    @staticmethod
    def get_slope_in_decimal_percentage(func: np.poly1d, set_off: int, length: int) -> float:
        """
        Gets the changes of the values for the input function WITHIN the range
        """
        mean_value = np.mean([func(set_off), func(set_off + length)])
        return_value = round((func(set_off + length) - func(set_off))/mean_value, 3)
        return return_value

    @staticmethod
    def get_poly1d(ind_left, value_left, ind_right, value_right) -> np.poly1d:
        """
        Gets the function parameter for the linear function which connects both points on the x-y-diagram
        """
        x = np.array([ind_left, ind_right])
        y = np.array([value_left, value_right])
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        # p[0] = round(p[0], 3)
        # p[1] = round(p[1], 2)
        return p

    @staticmethod
    def get_parallel_through_point(func: np.poly1d, x: float, y: float):
        diff = func(x) - y
        return np.poly1d([func[1], func[0] - diff])


class ToleranceCalculator:
    @staticmethod
    def are_values_in_tolerance_range(val_1: float, val_2: float, tolerance_pct: float):
        test = abs((val_1 - val_2)/np.mean([val_1, val_2]))
        return True if 0 == val_1 == val_2 else abs((val_1 - val_2)/np.mean([val_1, val_2])) < tolerance_pct

    @staticmethod
    def are_values_in_function_tolerance_range(x: list, y: list, f, tolerance_pct: float):
        for k in range(len(x)):
            y_k = y[k]
            f_k = f(x[k])
            if not ToleranceCalculator.are_values_in_tolerance_range(y_k, f_k, tolerance_pct):
                return False
        return True