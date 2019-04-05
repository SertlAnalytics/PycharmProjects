"""
Description: This module contains tome tools used within Tutti Salesman
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.mymath import MyMath
from itertools import combinations
import numpy as np


class TuttiSearchGenerator:
    def __init__(self, search_labels: list):
        self._search_labels = search_labels
        self._idx_last = len(self._search_labels) - 1

    def get_start_label_lists(self):
        return [[label] for label in self._search_labels]

    def get_label_list_with_child_labels(self, parent_label_list: list):
        idx_last_parent = self._search_labels.index(parent_label_list[-1])
        if idx_last_parent == self._idx_last:
            return []
        return [parent_label_list.append(label) for idx, label in enumerate(self._search_labels) if idx > idx_last_parent]


search_generator = TuttiSearchGenerator(['Wanderschuhe', 'Lowa', 'Rufus', 'GTX', 'Goretex'])
start_label_lists = search_generator.get_start_label_lists()
for level in range(2, 4):
    for label_list in start_label_lists:
        label_lists_with_child_labels = search_generator.get_label_list_with_child_labels(label_list)
        # now search with that labels - if found => next level else break
        for label_list_with_child in label_lists_with_child_labels:
            found_records = True
            if found_records:
                pass
            else:
                label_lists_with_child_labels = search_generator.get_label_list_with_child_labels(label_list)



['Wanderschuhe', 'Lowa', 'Rufus', 'GTX', 'Goretex']