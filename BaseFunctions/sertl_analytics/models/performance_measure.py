"""
Description: This module is the main module for machine learning algorithms.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score
from sklearn.metrics import roc_curve, roc_auc_score
from sertl_analytics.models.roc_auc_score_multi import MyMetrics
from sklearn.model_selection import train_test_split, cross_val_predict, cross_val_score, GridSearchCV
from keras.wrappers.scikit_learn import KerasClassifier
from collections import Counter
from sertl_analytics.constants.pattern_constants import MTC
from sertl_analytics.models.learning_machine import LearningMachine
import warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # get rid of ...Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2

class ModelPerformance:
    def __init__(self, lm: LearningMachine, x_train, y_train, label: str):
        warnings.filterwarnings("ignore")
        self._label = label
        self._cv = 3
        self._lm = lm
        self._x_train = np.array(x_train)
        self._y_train = np.array(y_train)
        self._y_train_value_count_dict = Counter(self._y_train)
        self.__remove_low_values__()
        # print('self._y_train_value_count_dict: {}'.format(self._y_train_value_count_dict))
        self._y_train_predict = np.array([])
        self._y_train_scores = np.array([])
        self.__calculate_y_train_predict__()
        self.__calculate_y_train_scores__()
        self._y_predict_value_list = sorted(list(set(self._y_train)))
        zero_list = [0 for k in range(0, len(self._y_predict_value_list))]
        y_train_scores_max = max(self._y_train_scores)
        if len(self._y_train_predict) == 0:
            self._precision = zero_list
            self._recall = zero_list
            self._f1_score = zero_list
            self._roc_auc = zero_list
            self._roc_fpr = None
            self._roc_tpr = None
            self._roc_threshold = None
        else:
            self._confusion_matrix = confusion_matrix(self._y_train, self._y_train_predict)
            # print('self._confusion_matrix={}'.format(self._confusion_matrix))
            self._y_predict_value_list = sorted(list(set(self._y_train_predict)))
            self._precision = precision_score(self._y_train, self._y_train_predict, average=None)
            self._recall = recall_score(self._y_train, self._y_train_predict, average=None)
            self._f1_score = f1_score(self._y_train, self._y_train_predict, average=None)
            # self._roc_auc = MyMetrics.get_roc_auc_score(self._y_train, self._y_train_scores, average=None)
            self._roc_auc = np.array([y_train_scores_max for k in range(0, len(self._f1_score))])
            self._roc_fpr = None
            self._roc_tpr = None
            self._roc_threshold = None
            # self.__calculate_roc_values__()

    @property
    def y_sorted_value_list(self):
        return self._y_predict_value_list

    @property
    def precision_dict(self):
        return {self._y_predict_value_list[k]: self.__round__(self._precision[k])
                for k in range(0, len(self._y_predict_value_list))}

    @property
    def recall_dict(self):
        return {self._y_predict_value_list[k]: self.__round__(self._recall[k])
                for k in range(0, len(self._y_predict_value_list))}

    @property
    def f1_score_dict(self):
        return {self._y_predict_value_list[k]: self.__round__(self._f1_score[k])
                for k in range(0, len(self._y_predict_value_list))}

    @property
    def roc_auc_dict(self):
        return {self._y_predict_value_list[k]: self.__round__(self._roc_auc[k])
                for k in range(0, len(self._y_predict_value_list))}

    def get_metric_list(self, metric: str) -> list:
        if metric == MTC.PRECISION:
            return [values for values in self.precision_dict.values()]
        elif metric == MTC.RECALL:
            return [values for values in self.recall_dict.values()]
        else:
            return [values for values in self.f1_score_dict.values()]


    def __round__(self, value: float):
        return round(value, 4)

    def __remove_low_values__(self):
        x_train = []
        y_train = []
        for index, y_value in enumerate(self._y_train):
            if self._y_train_value_count_dict[y_value] >= self._cv:
                x_train.append(self._x_train[index])
                y_train.append(self._y_train[index])
        self._x_train = np.array(x_train)
        self._y_train = np.array(y_train, np.int64)

    def __calculate_y_train_predict__(self):
        try:
            self._y_train_predict = self._lm.cross_val_predict(self._x_train, self._y_train, cv=self._cv)
        except ValueError as e:
            print(e)

    def __calculate_y_train_scores__(self):
        try:
            self._y_train_scores = self._lm.cross_val_score(
                self._x_train, self._y_train, cv=self._cv, scoring='accuracy')
            print('accuracy per cv: {}'.format(self._y_train_scores))
        except ValueError:
            self._y_train_scores = np.array([0 for k in range(0, self._cv)])
            print('Not enough data...')

    def __calculate_roc_values__(self):
        self._roc_fpr, self._roc_tpr, self._roc_threshold = roc_curve(y_train, y_train_predict)

