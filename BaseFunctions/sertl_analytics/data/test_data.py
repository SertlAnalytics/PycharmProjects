"""
Description: This module is the main module for generating test data for simulations.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""

import numpy as np


class TestDataGenerator:
    @staticmethod
    def get_test_data_for_summation():
        list_1 = [
            [1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1], [0, 1, 0, 0, 1], [0, 0, 1, 0, 1], [0, 0, 0, 1, 1], [0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1], [0, 1, 1, 1, 1]
        ]
        training_set = np.array(list_1)
        training_set_labels = training_set.sum(axis=1).reshape(training_set.shape[0], 1)
        list_2 = [
            [1, 1, 0, 0, 0], [0, 1, 1, 0, 0], [0, 0, 1, 1, 0], [0, 0, 0, 1, 1], [0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1], [1, 1, 0, 0, 1], [0, 0, 1, 0, 1], [0, 0, 0, 1, 1], [1, 0, 0, 0, 1]
        ]
        test_set = np.array(list_2)
        test_set_labels = test_set.sum(axis=1).reshape(test_set.shape[0], 1)
        return training_set, training_set_labels, test_set, test_set_labels