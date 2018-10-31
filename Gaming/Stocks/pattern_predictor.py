"""
Description: This module is the central modul for prediction pattern detection application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-08-22
"""

from sertl_analytics.constants.pattern_constants import FT
from sertl_analytics.models.nn_collector import NearestNeighborCollector
import numpy as np
import pandas as pd
from pattern_database.stock_database import StockDatabase, PatternTable, TradeTable
from pattern_database.stock_database import DatabaseDataFrame
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.model_selection import train_test_split
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pattern_configuration import PatternConfiguration
from pattern_database import stock_database
from sertl_analytics.mymath import EntropyHandler


class PatternPredictorApi:
    def __init__(self, config: PatternConfiguration, db_stock: StockDatabase,
                 pattern_table: PatternTable, trade_table: TradeTable):
        self.config = config
        self.db_stock = db_stock
        self.pattern_table = pattern_table
        self.trade_table = trade_table


class PatternFeaturesSelector:
    def __init__(self, _df_features_with_label: pd.DataFrame, label_columns: list, features_columns_orig: list):
        self._df_features_with_label = _df_features_with_label
        self._label_columns = label_columns
        self._features_columns_orig = features_columns_orig
        self._features_columns = self._features_columns_orig  # default
        self._label_feature_information_gain_dict = {}
        self._entropy_handler = EntropyHandler(
            self._df_features_with_label, self._label_columns, self._features_columns_orig)

    @property
    def features_columns(self) -> list:
        return self._features_columns

    def calculate_information_gain_for_feature_columns(self):
        if self._df_features_with_label.shape[0] == 0:
            return
        for label in self._label_columns:
            for feature in self._features_columns_orig:
                information_gain = self._entropy_handler.calculate_information_gain_for_label_and_feature(label, feature)
                print('label={}, feature={}: information_gain={}'.format(label, feature, information_gain))


class PatternPredictor:
    def __init__(self, db_stock: StockDatabase, pattern_type: str, skip_condition_list=None):
        # print('Loading Predictor: {}'.format(self.__class__.__name__))
        self._predictor = self.__class__.__name__
        self.db_stock = db_stock
        self.pattern_type = pattern_type
        self.skip_condition_list = skip_condition_list
        self.feature_table = self.__get_table_with_prediction_features__()
        self._features_columns_orig = self.__get_feature_columns_orig__()
        self.label_columns = self.__get_label_columns__()
        self._predictor_dict = self.__get_predictor_dict__()
        self._query_for_feature_and_label_data = self.__get_query_for_feature_and_label_data__()
        self._df_features_with_labels_and_id = self.__get_df_features_with_labels__()
        self._feature_columns = self.__get_feature_columns_by_information_gain__()
        self._neighbor_collector = None
        if self.is_ready_for_prediction:
            self._df_features = self._df_features_with_labels_and_id[self._feature_columns]
            self._df_labels = self._df_features_with_labels_and_id[self.label_columns]
            self._x_data = np.array(self._df_features)
            self.__train_models__(True)
        # self.__print_details__()
        # print('self.x_data.shape={}'.format(self._x_data.shape))

    def __print_details__(self):
        pos_where = self._query_for_feature_and_label_data.find('WHERE')
        where_clause = self._query_for_feature_and_label_data[pos_where:]
        elements = self._df_features_with_labels_and_id.shape[0]
        print('Loading Predictor {}: {} elements found for {}'.format(self._predictor, elements, where_clause))

    @property
    def feature_columns(self):
        return self._feature_columns

    @property
    def is_ready_for_prediction(self):
        return self._df_features_with_labels_and_id.shape[0] > 10

    def get_sorted_nearest_neighbor_entry_list_for_previous_prediction(self):
        return self._neighbor_collector.get_sorted_entry_list()

    def __get_feature_columns_by_information_gain__(self) -> list:
        if self._df_features_with_labels_and_id.shape[0] == 0 or True:
            return self._features_columns_orig
        entropy_handler = EntropyHandler(self._df_features_with_labels_and_id,
                                         self.label_columns, self._features_columns_orig)
        for label in self.label_columns:
            for feature in self._features_columns_orig:
                information_gain = entropy_handler.calculate_information_gain_for_label_and_feature(label, feature)
                if len(information_gain) > 1:
                    print('{}: label={}, feature={}: information_gain={}'.format(
                        self.__class__.__name__, label, feature, information_gain))
        return self._features_columns_orig

    def predict_for_label_columns(self, x_data: list):
        np_array = np.array(x_data)
        np_array = np_array.reshape(1, np_array.size)
        return_dict = {}
        collector_id = '{}_{}'.format(self.__class__.__name__, self.pattern_type)
        self._neighbor_collector = NearestNeighborCollector(self._df_features_with_labels_and_id, collector_id)
        for label in self.label_columns:
            if self.is_ready_for_prediction:
                prediction = self._predictor_dict[label].predict(np_array)[0]
                dist, ind = self._predictor_dict[label].kneighbors(np_array)
                self._neighbor_collector.add_dist_ind_array(ind, dist)
            else:
                prediction = 0
            if self.feature_table.is_label_column_for_regression(label):
                return_dict[label] = round(prediction, -1)
            else:
                return_dict[label] = int(prediction)
        return return_dict

    def __get_base_query_with_pattern_type_condition__(self, base_query: str):
        if self.pattern_type != '':
            if base_query.find('WHERE') >= 0:  # already where clause available
                return base_query + " AND Pattern_Type = '{}'".format(self.pattern_type)
            return base_query + " WHERE Pattern_Type = '{}'".format(self.pattern_type)
        return base_query

    def __get_base_query_with_skip_conditions__(self, base_query: str):
        if self.skip_condition_list:
            skip_condition_all = ' AND '.join(self.skip_condition_list)
            if base_query.find('WHERE') >= 0:  # already where clause available
                return base_query + ' AND NOT ({})'.format(skip_condition_all)
            return base_query + ' WHERE NOT ({})'.format(skip_condition_all)
        return base_query

    def __get_table_with_prediction_features__(self):
        pass

    def __get_feature_columns_orig__(self):
        return []

    def __get_label_columns__(self):
        return []

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
    def __get_table_with_prediction_features__(self) -> PatternTable:
        return PatternTable()

    def __get_feature_columns_orig__(self):
        return self.feature_table.feature_columns_touch_points

    def __get_label_columns__(self):
        return self.feature_table.label_columns_touch_points

    def __get_query_for_feature_and_label_data__(self):
        base_query = self.feature_table.query_for_feature_and_label_data_touch_points
        base_query = self.__get_base_query_with_pattern_type_condition__(base_query)
        return self.__get_base_query_with_skip_conditions__(base_query)


class PatternPredictorBeforeBreakout(PatternPredictor):
    def __get_table_with_prediction_features__(self) -> PatternTable:
        return PatternTable()

    def __get_feature_columns_orig__(self):
        return self.feature_table.features_columns_before_breakout

    def __get_label_columns__(self):
        return self.feature_table.label_columns_before_breakout

    def __get_query_for_feature_and_label_data__(self):
        base_query = self.feature_table.query_for_feature_and_label_data_before_breakout
        base_query = self.__get_base_query_with_pattern_type_condition__(base_query)
        return self.__get_base_query_with_skip_conditions__(base_query)


class PatternPredictorAfterBreakout(PatternPredictor):
    def __get_table_with_prediction_features__(self) -> PatternTable:
        return PatternTable()

    def __get_feature_columns_orig__(self):
        return self.feature_table.features_columns_after_breakout

    def __get_label_columns__(self):
        return self.feature_table.label_columns_after_breakout

    def __get_query_for_feature_and_label_data__(self):
        base_query = self.feature_table.query_for_feature_and_label_data_after_breakout
        base_query = self.__get_base_query_with_pattern_type_condition__(base_query)
        return self.__get_base_query_with_skip_conditions__(base_query)


class PatternPredictorForTrades(PatternPredictor):
    def __get_table_with_prediction_features__(self) -> TradeTable:
        return TradeTable()

    def __get_feature_columns_orig__(self):
        return self.feature_table.feature_columns_for_trades

    def __get_label_columns__(self):
        return self.feature_table.label_columns_for_trades

    def __get_query_for_feature_and_label_data__(self):
        base_query = self.feature_table.query_for_feature_and_label_data_for_trades
        base_query = self.__get_base_query_with_pattern_type_condition__(base_query)
        return self.__get_base_query_with_skip_conditions__(base_query)


class PatternMasterPredictor:
    def __init__(self, api: PatternPredictorApi):
        self.config = api.config
        self.db_stock = api.db_stock
        self.pattern_table = api.pattern_table
        self.trade_table = api.trade_table

        self.predictor_dict = {}
        # self.__init_predictor_dict__()  # currently we don't need this - we'll do that later per ticker id

    def get_feature_columns(self, pattern_type: str):
        predictor = self.predictor_dict[pattern_type]
        return predictor.feature_columns

    def predict_for_label_columns(self, pattern_type: str, x_data: list):
        predictor = self.predictor_dict[pattern_type]
        return predictor.predict_for_label_columns(x_data)

    def get_sorted_nearest_neighbor_entry_list(self, pattern_type: str):
        predictor = self.predictor_dict[pattern_type]
        return predictor.get_sorted_nearest_neighbor_entry_list_for_previous_prediction()

    def init_without_condition_list(self, ticker_id: str, and_clause: str):
        self.__init_predictor_dict__(self.__get_skip_condition_list__(ticker_id, and_clause))

    def __init_predictor_dict__(self, skip_condition_list=None):
        for pattern_type in FT.get_all():
            self.predictor_dict[pattern_type] = \
                self.__get_predictor_for_pattern_type__(pattern_type, skip_condition_list)

    def __get_skip_condition_list__(self, ticker_id: str, and_clause: str) -> list:
        pass

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        pass


class PatternMasterPredictorTouchPoints(PatternMasterPredictor):
    def __get_skip_condition_list__(self, ticker_id: str, and_clause: str) -> list:
        return ["Ticker_ID = '{}'".format(ticker_id), and_clause]

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        return PatternPredictorTouchPoints(self.db_stock, pattern_type, skip_condition_list)


class PatternMasterPredictorBeforeBreakout(PatternMasterPredictor):
    def __get_skip_condition_list__(self, ticker_id: str, and_clause: str) -> list:
        return ["Ticker_ID = '{}'".format(ticker_id), and_clause]

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        return PatternPredictorBeforeBreakout(self.db_stock, pattern_type, skip_condition_list)


class PatternMasterPredictorAfterBreakout(PatternMasterPredictor):
    def __get_skip_condition_list__(self, ticker_id: str, and_clause: str) -> list:
        return ["Ticker_ID = '{}'".format(ticker_id), and_clause]

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        return PatternPredictorAfterBreakout(self.db_stock, pattern_type, skip_condition_list)


class PatternMasterPredictorForTrades(PatternMasterPredictor):
    def __get_skip_condition_list__(self, ticker_id: str, and_clause: str) -> list:
        return ["Ticker_ID = '{}'".format(ticker_id), and_clause]

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        return PatternPredictorForTrades(self.db_stock, pattern_type, skip_condition_list)


class PatternMasterPredictorHandler:
    def __init__(self, api: PatternPredictorApi):
        self.master_predictor_touch_points = PatternMasterPredictorTouchPoints(api)
        self.master_predictor_before_breakout = PatternMasterPredictorBeforeBreakout(api)
        self.master_predictor_after_breakout = PatternMasterPredictorAfterBreakout(api)
        self.master_predictor_for_trades = PatternMasterPredictorForTrades(api)

    def init_predictors_without_condition_list(self, ticker_id: str, and_clause_pattern: str, and_clause_trades: str):
        self.master_predictor_touch_points.init_without_condition_list(ticker_id, and_clause_pattern)
        self.master_predictor_before_breakout.init_without_condition_list(ticker_id, and_clause_pattern)
        self.master_predictor_after_breakout.init_without_condition_list(ticker_id, and_clause_pattern)
        self.master_predictor_for_trades.init_without_condition_list(ticker_id, and_clause_trades)

