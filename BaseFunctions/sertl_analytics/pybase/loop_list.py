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
    NUMBER = 'Number'
    TICKER = 'Ticker'


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

    def append(self, key, value):
        self.counter += 1
        self.index.append(key)
        self.dic[key] = value
        if self.min_index == None:
            self.min_index = key
            self.max_index = key
        else:
            if key < self.min_index:
                self.min_index = key
            if key > self.max_index:
                self.max_index = key

    def get_value(self, key, key_tolerance: float):
        if key in self.dic:
            return self.dic[key]

        for x in self.dic:
            if abs(x - key) < key_tolerance:
                return self.dic[x]
