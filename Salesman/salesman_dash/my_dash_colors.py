"""
Description: This module contains wrapper classes for dash components.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import numpy as np


COLORS = [
    {
        'background': '#fef0d9',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#fdcc8a',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#fc8d59',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#d7301f',
        'text': 'rgb(30, 30, 30)'
    },
]


class DashColorHandler:
    def __init__(self):
        np.random.seed(42)
        self._category_color_dict = {}

    def get_color_for_category(self, category: str):
        category_str = self.__get_unique_category__(category)
        if category_str not in self._category_color_dict:
            self._category_color_dict[category_str] = 'rgb({}, {}, {})'.format(np.random.randint(1, 255),
                                                                               np.random.randint(1, 255),
                                                                               np.random.randint(1, 255))
        return self._category_color_dict[category_str]

    @staticmethod
    def get_color_scale_for_heatmap():
        # colorscale='RdBu',
        return [[0, 'white'], [0.1, 'rgb(31,120,180)'], [0.45, 'rgb(178,223,138)'],
                [0.65, 'rgb(51,160,44)'], [0.85, 'rgb(251,154,153)'], [1, 'rgb(227,26,28)']]

    @staticmethod
    def __get_unique_category__(category_orig):
        category_str = category_orig if category_orig is str else str(category_orig)
        suffix_list = ['_winner', '_loser']
        for suffix in suffix_list:
            if category_str[-len(suffix):] == suffix:
                return category_str[:-len(suffix)]
        return category_str

