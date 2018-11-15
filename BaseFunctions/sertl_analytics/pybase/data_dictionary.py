"""
Description: This module contains the data dictionary class. This serves as a column centric data container.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-15
"""

import numpy as np


class DataDictionary:
    def __init__(self):
        self._data_dict = {}
        self.__init_data_dict__()

    @property
    def data_dict(self) -> dict:
        return self._data_dict

    def add(self, key: str, value):
        value = self.__get_manipulated_value__(key, value)
        self._data_dict[key] = value

    def inherit_values(self, data_dict: dict):
        for key, values in data_dict.items():
            self.data_dict[key] = values

    def get(self, key: str, default_value=None):
        return self._data_dict.get(key, default_value)

    def __init_data_dict__(self):
        pass

    def __get_manipulated_value__(self, key: str, value):
        if type(value) in [np.float64, float]:
            if value == -0.0:
                value = 0.0
        return self.__get_rounded_value__(key, value)

    @staticmethod
    def __get_rounded_value__(key: str, value):
        return value