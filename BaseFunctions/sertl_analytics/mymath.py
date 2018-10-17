"""
Description: This module contains the math classes for sertl-analytics
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-07-24
"""

import numpy as np
from scipy.stats import entropy
import pandas as pd


class ParentEntropy:
    def __init__(self, label: str, value, value_prob: float):
        self._label = label
        self._value = value
        self._v_p = value_prob
        self._not_v_p = 1 - self._v_p

    @property
    def label(self):
        return self._label

    @property
    def value(self):
        return self._value

    @property
    def entropy(self):
        if self._v_p == 0 or self._v_p == 1:
            return 0
        return round(-self._v_p * np.log2(self._v_p) - self._not_v_p * np.log2(self._not_v_p), 3)


class ChildEntropy:
    def __init__(self, label: str, label_value, feature_label_value_prob: float, feature: str, value, value_prob: float):
        self._label = label
        self._label_value = label_value
        self._feature = feature
        self._feature_value = value
        self._feature_value_prob = value_prob
        # this is the probability of the feature value over the whole distribution
        self._v_p = feature_label_value_prob  # the probability of the feature value for the parent value
        self._not_v_p = 1 - self._v_p

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
    def entropy(self):
        if self._v_p == 0 or self._v_p == 1:
            return 0
        return round(-self._v_p * np.log2(self._v_p) - self._not_v_p * np.log2(self._not_v_p), 3)

    @property
    def information_gain_contribution(self):
        return round(self._feature_value_prob * self.entropy, 3)


class EntropyHandler:
    def __init__(self, df: pd.DataFrame, labels: list, features: list):
        self._df = df
        self._elements_total = self._df.shape[0]
        self._labels = labels
        self._features = features
        self._parent_entropy_list = []
        self._child_entropy_list = []
        self.__fill_parent_entropy_list__()
        self.__fill_child_entropy_list__()

    def calculate_information_gain_for_label_and_feature(self, label: str, feature: str):
        child_correction_sum = 0
        for parent_entropy in [e for e in self._parent_entropy_list if e.label == label]: # label, value, entropy
            child_list = self.__get_child_entropy_list_for_feature_and_parent_entropy__(feature, parent_entropy)
            for child_entropy in child_list:
                child_correction_sum += child_entropy.information_gain_contribution
            child_correction_sum = round(child_correction_sum, 4)
        information_gain = round(parent_entropy.entropy - child_correction_sum, 4)
        percentage = '{:.1f}%'.format(information_gain/parent_entropy.entropy*100)
        return [parent_entropy.entropy, child_correction_sum, information_gain, percentage]

    def __get_child_entropy_list_for_feature_and_parent_entropy__(self, feature: str, p_e: ParentEntropy):
        return [e for e in self._child_entropy_list
                if e.label == p_e.label and e.label_value == p_e.value and e.feature == feature]

    def __fill_parent_entropy_list__(self):
        for label in self._labels:
            binary_value = self.__get_value_for_binary_label_column__(label)
            unique_values = [binary_value] if binary_value else df[label].unique()
            for label_value in unique_values:
                self.__fill_parent_entropy_list_for_label__(label, label_value)

    def __fill_parent_entropy_list_for_label__(self, label: str, label_value):
         elements_for_value = self._df[self._df[label] == label_value].shape[0]
         p_v = round(elements_for_value / self._elements_total, 3)
         self._parent_entropy_list.append(ParentEntropy(label, label_value, p_v))

    def __fill_child_entropy_list__(self):
        for parent_entropy in self._parent_entropy_list:
            for feature in self._features:
                feature_unique_values = self._df[feature].unique()
                for feature_value in feature_unique_values:
                    self.__fill_child_entropy_list_for_label_and_feature__(
                        parent_entropy.label, parent_entropy.value, feature, feature_value)

    def __fill_child_entropy_list_for_label_and_feature__(
            self, label: str, label_value, feature: str, feature_value):
        elements_feature_value_total = self._df[self._df[feature] == feature_value].shape[0]
        p_f_v = round(elements_feature_value_total / self._elements_total, 3)
        df_for_values = self._df[np.logical_and(self._df[feature] == feature_value, self._df[label] == label_value)]
        elements_feature_value_with_label_value = df_for_values.shape[0]
        p_v = round(elements_feature_value_with_label_value / elements_feature_value_total, 3)
        self._child_entropy_list.append(ChildEntropy(label, label_value, p_v, feature, feature_value, p_f_v))

    def __get_value_for_binary_label_column__(self, label_column: str):  # get the highest value for binary
        unique_values = sorted(self._df[label_column].unique())
        if len(unique_values) <= 2:
            return unique_values[-1]
        return None


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