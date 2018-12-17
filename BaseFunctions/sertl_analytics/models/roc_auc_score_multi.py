"""
Description: This module contains the ROC class to get the receiver operator characteristics for multi class classifiers.
Reason: roc_auc_score doesn't support multi-class "Error: multiclass format is not supported"
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-12-15
"""

from sklearn.metrics import roc_auc_score
import numpy as np
import statistics as stat


class MyMetrics:
    @staticmethod
    def get_roc_auc_score(y_train: np.array, y_train_predict: np.array, average=None):
        if len(y_train) < 3:
            return [roc_auc_score(y_train, y_train_predict, average=average)]
        scores = []
        std_dev = stat.stdev(y_train)
        for value in y_train:
            y_train_adjusted = np.array(y_train)
            y_train_predict_adjusted = np.array(y_train_predict)
            for index in range(0, len(y_train)):
                y_train_adjusted[index] = 1 if abs(y_train_adjusted[index] - value) <= std_dev else 0
                y_train_predict_adjusted[index] = 1 if abs(y_train_predict_adjusted[index] - value) < std_dev else 0
            if len(set(y_train_adjusted)) == 1:
                # Only one class present in y_true. ROC AUC score is not defined in that case.
                print('{}: y={}, y_predict={}'.format(std_dev, y_train, y_train_predict))
                scores.append(0.5)
            else:
                scores.append(roc_auc_score(y_train_adjusted, y_train_predict_adjusted, average=average))
        return np.array(scores)

