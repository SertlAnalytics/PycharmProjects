"""
Description: This module contains the math classes for sertl-analytics
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-07-24
"""

import numpy as np
from scipy.stats import entropy
import pandas as pd


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
    def get_change_in_percentage(value_from: float, value_to: float, decimal_round=1) -> float:
        value_change = value_to - value_from
        value_mean = (value_from + value_to)/2
        return round(value_change/value_mean * 100, decimal_round)

    @staticmethod
    def get_change_in_pct(value_from: float, value_to: float, decimal_round=3) -> float:
        value_change = value_to - value_from
        value_mean = (value_from + value_to) / 2
        return round(value_change / value_mean, decimal_round)


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