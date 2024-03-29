"""
Description: This module contains different loop lists.
They enable to loop with a counter without declaring a counter variable.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-21
"""

import collections


class LL:
    AND_CLAUSE = 'and_clause'
    TICKER = 'Ticker'
    NUMBER = 'Number'


class LoopList:
    def __init__(self):
        self.counter = 0
        self.value_list = []

    def append(self, value):
        self.counter += 1
        self.value_list.append(value)


class LoopList4Dictionaries(LoopList):
    index_list = []

    def append(self, value_dic: dict):
        self.counter += 1
        value_dic[LL.NUMBER] = self.counter  # add of number to dictionary
        self.index_list.append(self.counter)
        self.value_list.append(value_dic)


class ExtendedDictionary:
    def __init__(self):
        self.counter = 0
        self.min_index = None
        self.max_index = None
        self.index = []
        self.dic = {}

    @staticmethod
    def get_key_for_value(my_dict: dict, value):
        my_dict_keys = list(my_dict.keys())
        index = list(my_dict.values()).index(value)
        return my_dict_keys[index]

    def append(self, key, value):
        self.counter += 1
        self.index.append(key)
        self.dic[key] = value
        if self.min_index is None:
            self.min_index = key
            self.max_index = key
        else:
            if key < self.min_index:
                self.min_index = key
            if key > self.max_index:
                self.max_index = key

    def get_value_by_dict_key(self, key, key_tolerance: float = 0.0):
        if key in self.dic:
            return self.dic[key]

        if key_tolerance > 0:
            for x in self.dic:
                if abs(x - key) < key_tolerance:
                    return self.dic[x]

        return None
