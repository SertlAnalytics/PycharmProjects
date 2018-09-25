"""
Description: This module is the central modul for prediction pattern detection application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-08-22
"""

from sertl_analytics.constants.pattern_constants import DC
import pandas as pd
import numpy as np
from pattern_database.stock_tables import MyTable, PredictionFeatureTable
from pattern_database.stock_database import StockDatabase, FeaturesTable, TradeTable
from pattern_database.stock_database import DatabaseDataFrame
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from scipy.optimize import basinhopping
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from random import randrange
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class PatternPredictor:
    def __init__(self, db_stock: StockDatabase, skip_condition_list=None):
        # print('Loading Predictor: {}'.format(self.__class__.__name__))
        self.skip_condition_list = skip_condition_list
        self.feature_table = self.__get_table_with_prediction_features__()
        self.db_stock = db_stock
        self.feature_columns = self.__get_feature_columns__()
        self.label_columns = self.__get_label_columns__()
        self._query_for_feature_and_label_data = self.__get_query_for_feature_and_label_data__()
        self._predictor_dict = self.__get_predictor_dict__()
        self._df_features_with_labels = self.__get_df_features_with_labels__()
        if self.is_ready_for_prediction:
            self._df_features = self._df_features_with_labels[self.feature_columns]
            self._df_labels = self._df_features_with_labels[self.label_columns]
            self._x_data = np.array(self._df_features)
            self.__train_models__(True)
        # print('self.x_data.shape={}'.format(self._x_data.shape))

    @property
    def is_ready_for_prediction(self):
        return self._df_features_with_labels.shape[0] > 10

    def predict_for_label_columns(self, x_input: np.array):
        return_dict = {}
        for label in self.label_columns:
            if self.is_ready_for_prediction:
                prediction = self._predictor_dict[label].predict(x_input)[0]
            else:
                prediction = 0
            if self.feature_table.is_label_column_for_regression(label):
                return_dict[label] = round(prediction, -1)
            else:
                return_dict[label] = int(prediction)
        return return_dict

    def __get_base_query_with_skip_conditions__(self, base_query: str):
        if self.skip_condition_list:
            skip_condition_all = ' AND '.join(self.skip_condition_list)
            if base_query.find('WHERE') >= 0:  # already where clause available
                return base_query + ' AND NOT ({})'.format(skip_condition_all)
            return base_query + ' WHERE NOT ({})'.format(skip_condition_all)
        return base_query

    def __get_table_with_prediction_features__(self):
        pass

    def __get_feature_columns__(self):
        pass

    def __get_label_columns__(self):
        pass

    def __get_query_for_feature_and_label_data__(self):
        pass

    def __get_y_train_for_label_column__(self, label_column: str) -> np.array:
        return np.array(self._df_labels[label_column])

    def __get_df_features_with_labels__(self):
        return DatabaseDataFrame(self.db_stock, self._query_for_feature_and_label_data).df

    def __get_predictor_dict__(self) -> dict:
        return {label: self.__get_predictor_for_label_column__(label) for label in self.label_columns}

    def __get_predictor_for_label_column__(self, label_column: str):
        if self.feature_table.is_label_column_for_regression(label_column):
            return KNeighborsRegressor(n_neighbors=7, weights='distance')
            # return RandomForestRegressor(n_estimators=3, random_state=42)
        else:
            return KNeighborsClassifier(n_neighbors=7, weights='distance')
            # return RandomForestClassifier(n_estimators=3, random_state=42)

    @staticmethod
    def __get_predict_probability__(predictor, x_data):
        predict_probability = predictor.predict_proba(x_data).round(2)
        return predict_probability

    def __train_models__(self, perform_test=False):
        for label_columns in self.label_columns:
            self.__train_model__(label_columns, perform_test)

    def __train_model__(self, label_column: str, perform_test):
        # print('\nTrain model for label "{}"'.format(label_column))
        x_train = self._x_data
        y_train = self.__get_y_train_for_label_column__(label_column)
        predictor = self._predictor_dict[label_column]
        if perform_test:
            self.__perform_test_on_training_data__(x_train, y_train, predictor, label_column)
        else:
            predictor.fit(x_train, y_train)
            self.__print_report__(x_train, y_train, predictor, label_column)

    def __perform_test_on_training_data__(self, x_input, y_input, predictor, label_column: str):
        X_train, X_test, y_train, y_test = train_test_split(x_input, y_input, test_size=0.3)
        predictor.fit(X_train, y_train)
        self.__print_report__(X_test, y_test, predictor, label_column)

    def __print_report__(self, x_input, y_input, predictor, label_column: str):
        rfc_pred = predictor.predict(x_input)
        if self.feature_table.is_label_column_for_regression(label_column):
            self.__print_prediction_details__(y_input, rfc_pred, True)
        else:
            self.__print_prediction_details__(y_input, rfc_pred, False)
            # print(confusion_matrix(y_input, rfc_pred))
            # print('\n')
            # print(classification_report(y_input, rfc_pred))

    @staticmethod
    def __print_prediction_details__(y_input, v_predict, for_regression: bool):
        return
        for k in range(0, len(y_input)):
            if for_regression:
                print('{:6.2f} / {:6.2f}: diff = {:6.2f}'.format(y_input[k], v_predict[k], y_input[k]-v_predict[k]))
            else:
                print('{:2d} / {:2d}: diff = {:2d}'.format(y_input[k], v_predict[k], y_input[k] - v_predict[k]))

    def __plot_train_data__(self, number_matches: int):
        classes = ['No winner', 'Team 1', 'Team 2', 'Test match']
        c_light = ['#FFAAAA', '#AAFFAA', '#AAAAFF', 'k']
        matches = []
        for i in range(0, len(c_light)):
            matches.append(mpatches.Rectangle((0, 0), 1, 1, fc=c_light[i]))
        cmap_light = ListedColormap(c_light[:3])
        cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF'])
        self.__train_models__(4)
        x_train = self.get_x_train(4)  # normal ranking
        x_test = self.get_x_test(number_matches, 4)
        x_min, x_max = x_train[:, 0].min() - 1, x_train[:, 0].max() + 1
        y_min, y_max = x_train[:, 1].min() - 1, x_train[:, 1].max() + 1
        h = round((max(x_max, y_max) - min (x_min, y_min))/100,2) # step size in the mesh
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                             np.arange(y_min, y_max, h))
        x = np.c_[xx.ravel(), yy.ravel()]

        clf_list = [self.forest_clf, self.log_reg, self.knn_clf]
        title_list = ['Random_Forest', 'Logistic_Regression', 'K-Nearest Neighbors: {}'.format(7)]

        f, axes = plt.subplots(len(clf_list), 1, sharex='col', figsize=(7, 10))
        plt.tight_layout()

        for index, clfs in enumerate(clf_list):
            ax = axes[index]
            Z = clfs.predict(np.c_[xx.ravel(), yy.ravel()])
            Z = Z.reshape(xx.shape)
            ax.pcolormesh(xx, yy, Z, cmap=cmap_light)
            ax.scatter(x_train[:, 0], x_train[:, 1], c=self.y_train, cmap=cmap_bold, label='Test')
            ax.scatter(x_test[:, 0], x_test[:, 1], c=c_light[-1])
            for i in range(0, x_test.shape[0]):
                match = self.match_test_list[i]
                ax.annotate(match.annotation, (x_test[i, 0], x_test[i, 1]))
            ax.legend(matches, classes, loc='upper right')
            ax.set_title(title_list[index])
        plt.show()


class PatternPredictorTouchPoints(PatternPredictor):
    def __get_table_with_prediction_features__(self) -> FeaturesTable:
        return FeaturesTable()

    def __get_feature_columns__(self):
        return self.feature_table.feature_columns_touch_points

    def __get_label_columns__(self):
        return self.feature_table.label_columns_touch_points

    def __get_query_for_feature_and_label_data__(self):
        base_query = self.feature_table.query_for_feature_and_label_data_touch_points
        return self.__get_base_query_with_skip_conditions__(base_query)


class PatternPredictorBeforeBreakout(PatternPredictor):
    def __get_table_with_prediction_features__(self) -> FeaturesTable:
        return FeaturesTable()

    def __get_feature_columns__(self):
        return self.feature_table.features_columns_before_breakout

    def __get_label_columns__(self):
        return self.feature_table.label_columns_before_breakout

    def __get_query_for_feature_and_label_data__(self):
        base_query = self.feature_table.query_for_feature_and_label_data_before_breakout
        return self.__get_base_query_with_skip_conditions__(base_query)


class PatternPredictorAfterBreakout(PatternPredictor):
    def __get_table_with_prediction_features__(self) -> FeaturesTable:
        return FeaturesTable()

    def __get_feature_columns__(self):
        return self.feature_table.features_columns_after_breakout

    def __get_label_columns__(self):
        return self.feature_table.label_columns_after_breakout

    def __get_query_for_feature_and_label_data__(self):
        base_query = self.feature_table.query_for_feature_and_label_data_after_breakout
        return self.__get_base_query_with_skip_conditions__(base_query)


class PatternPredictorForTrades(PatternPredictor):
    def __get_table_with_prediction_features__(self) -> TradeTable:
        return TradeTable()

    def __get_feature_columns__(self):
        return self.feature_table.feature_columns_for_trades

    def __get_label_columns__(self):
        return self.feature_table.label_columns_for_trades

    def __get_query_for_feature_and_label_data__(self):
        base_query = self.feature_table.query_for_feature_and_label_data_for_trades
        return self.__get_base_query_with_skip_conditions__(base_query)


