"""
Description: This module contains the outlier calculator for Salesman
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
import statistics
from sertl_analytics.mymath import MyMath


class Outlier:
    def __init__(self, values: list, threshold_pct: int):
        self._values = values
        self._mean_values = 0
        self._min_values = 0
        self._max_values = 0
        self._threshold_pct = threshold_pct
        self._bottom_threshold = 0
        self._top_threshold = 0
        self._bottom_threshold_iqr = 0
        self._top_threshold_iqr = 0
        self._values_without_outliers = []
        self._values_without_iqr_outliers = []
        self._mean_values_without_outliers = 0
        self._mean_values_without_iqr_outliers = 0
        self.__calculate_variables__()

    @property
    def min_values(self) -> float:
        return self._min_values

    @property
    def bottom_threshold(self) -> float:
        return self._bottom_threshold

    @property
    def bottom_threshold_iqr(self) -> float:
        return self._bottom_threshold_iqr

    @property
    def mean_values(self) -> float:
        return self._mean_values

    @property
    def top_threshold(self) -> float:
        return self._top_threshold

    @property
    def top_threshold_iqr(self) -> float:
        return self._top_threshold_iqr

    @property
    def max_values(self) -> float:
        return self._max_values

    @property
    def mean_values_without_iqr_outliers(self) -> float:
        return self._mean_values_without_iqr_outliers

    @property
    def mean_values_without_outliers(self) -> float:
        return self._mean_values_without_outliers

    def is_value_outlier(self, value: float):
        # print('is_value_outlier: value={} <-> [{}, {}]'.format(value, self._bottom_threshold, self._top_threshold))
        return value < self._bottom_threshold or value > self._top_threshold

    def is_value_iqr_outlier(self, value: float):
        return value < self._bottom_threshold_iqr or value > self._top_threshold_iqr

    def get_markdown_text(self) -> str:
        iqr = '- **IQR:** [{:.2f}, {:.2f}]'.format(
            self.bottom_threshold_iqr, self.top_threshold_iqr)
        return '**[min, bottom, mean, top, max]:** [{:.2f}, {:.2f}, **{:.2f}**, {:.2f}, {:.2f}] {}'.format(
            self.min_values, self.bottom_threshold, self.mean_values, self.top_threshold, self.max_values, iqr)

    def print_outlier_details(self):
        print('Outlier: min={}, bottom={}, mean={}, top={}, max={}, mean_without_outliers={}'.format(
            self.min_values, self.bottom_threshold, self.mean_values, self.top_threshold, self.max_values,
            self.mean_values_without_outliers))

    def print_iqr_outlier_details(self):
        print('Outlier: min={}, bottom={}, mean={}, top={}, max={}, mean_without_outliers={}'.format(
            self.min_values, self._bottom_threshold_iqr, self.mean_values, self._top_threshold_iqr, self.max_values,
            self.mean_values_without_iqr_outliers))

    def __calculate_variables__(self, by_iqr=False):
        self._min_values = MyMath.round_smart(min(self._values))
        self._max_values = MyMath.round_smart(max(self._values))
        self._mean_values = MyMath.round_smart(statistics.mean(self._values))
        self.__calculate_thresholds__()
        for value in self._values:
            if not self.is_value_outlier(value):
                self._values_without_outliers.append(value)
            if not self.is_value_iqr_outlier(value):
                self._values_without_iqr_outliers.append(value)

        if len(self._values_without_outliers) == 0:
            self._mean_values_without_outliers = 0
        else:
            self._mean_values_without_outliers = \
                MyMath.round_smart(statistics.mean(self._values_without_outliers))

        if len(self._values_without_iqr_outliers) == 0:
            self._mean_values_without_iqr_outliers = 0
        else:
            self._mean_values_without_iqr_outliers = \
                MyMath.round_smart(statistics.mean(self._values_without_iqr_outliers))

    def __calculate_thresholds__(self):
        q75, q25 = np.percentile(self._values, [75, 25])
        iqr = q75 - q25
        self._bottom_threshold_iqr = MyMath.round_smart(q25 - 1.5 * iqr)
        self._top_threshold_iqr = MyMath.round_smart(q75 + 1.5 * iqr)
        if len(self._values) <= 4:
            self._bottom_threshold = self._bottom_threshold_iqr
            self._top_threshold = self._top_threshold_iqr
        else:
            self._bottom_threshold = MyMath.round_smart(np.percentile(self._values, self._threshold_pct))
            self._top_threshold = MyMath.round_smart(np.percentile(self._values, 100 - self._threshold_pct))

