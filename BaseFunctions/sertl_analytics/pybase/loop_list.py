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
    counter = 0
    value_list = []

    def append(self, value):
        self.counter += 1
        self.value_list.append(value)


class DictionaryLoopList(LoopList):
    index_list = []

    def append(self, value_dic: dict):
        self.counter += 1
        value_dic[LL.NUMBER] = self.counter  # add of number to dictionary
        self.index_list.append(self.counter)
        self.value_list.append(value_dic)