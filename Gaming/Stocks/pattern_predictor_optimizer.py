"""
Description: This module is the central modul for prediction pattern detection application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-08-22
"""

from sertl_analytics.constants.pattern_constants import PRED, STBL, MP, FT, DC, MT
from sertl_analytics.models.learning_machine import LearningMachineFactory
import numpy as np
import pandas as pd
from pattern_database.stock_database import StockDatabase, PatternTable, TradeTable
from pattern_database.stock_database import DatabaseDataFrame
from pattern_configuration import PatternConfiguration
from sertl_analytics.models.performance_measure import ModelPerformance
import math


class PatternPredictorOptimizer:
    def __init__(self, db_stock: StockDatabase):
        self._db_stock = db_stock
        self._pattern_table = PatternTable()
        self._trade_table = TradeTable()
        self._model_dict = LearningMachineFactory.get_classifier_model_dict()
        self._df_features_and_labels_dict = {}
        self._features_column_dict = {}
        self._class_key_list = []
        self._class_dict = {MP.MODEL_NAME: [], MP.TABLE: [], MP.PREDICTOR: [], MP.LABEL: [], MP.PATTERN_TYPE: [],
                            MP.VALUE: [], MP.PRECISION: [], MP.RECALL: [], MP.F1_SCORE: [], MP.ROC_AUC: []}
        self._df_metric = None
        self._trained_model_dict = {}

    def predict(self, table_name: str, predictor: str, label: str, pattern_type: str, x_data: list):
        x_data_array = self.__get_x_data_in_correct_format__(x_data)
        return self.__get_optimal_prediction__(table_name, predictor, label, pattern_type, x_data_array)

    def __get_optimal_prediction__(
            self, table_name: str, predictor: str, label: str, pattern_type: str, x_data: np.array):
        prediction_precision_optimal = 0
        prediction_optimal = - math.inf
        for model_name in self._model_dict:
            prediction = self.__get_prediction_for_model__(model_name, table_name, predictor, label, x_data)
            prediction_precision = self.__get_precision_for_model_value__(
                model_name, table_name, predictor, label, pattern_type, prediction)
            if prediction_precision > prediction_precision_optimal:
                prediction_precision_optimal = prediction_precision
                prediction_optimal = prediction
        return prediction_optimal

    def __get_prediction_for_model__(self, model_name, table: str, predictor: str, label: str, x_data: np.array):
        trained_model = self.__get_trained_model__(model_name, table, predictor, label)
        prediction = trained_model.predict(x_data)[0]
        return prediction

    @staticmethod
    def __get_x_data_in_correct_format__(x_data) -> np.array:
        np_array = np.array(x_data)
        np_array = np_array.reshape(1, np_array.size)
        return np_array

    @staticmethod
    def __get_key_for_df__(table_name: str, predictor: str):
        return '{}-{}'.format(table_name, predictor)

    @staticmethod
    def __get_key_for_class_key_list__(table_name: str, predictor: str, label: str, pattern_type: str):
        return '{}-{}-{}-{}'.format(table_name, predictor, label, pattern_type)

    @staticmethod
    def __get_key_for_trained_model__(model_name: str, table_name: str, predictor: str, label: str):
        return '{}-{}-{}-{}'.format(model_name, table_name, predictor, label)

    def __calculate_class_metrics_for_predictor_and_label__(
            self, table_name: str, predictor: str, label: str, pattern_type: str):
        key = self.__get_key_for_class_key_list__(table_name, predictor, label, pattern_type)
        if key not in self._class_key_list:
            self.__calculate_class_metrics__(table_name, predictor, label, pattern_type)
            self._class_key_list.append(key)

    def __get_precision_for_model_value__(
            self, model_name: str, table_name: str, predictor: str, label: str, pattern_type: str, value):
        self.__calculate_class_metrics_for_predictor_and_label__(table_name, predictor, label, pattern_type)
        df = self._df_metric[self._df_metric[MP.PATTERN_TYPE] == pattern_type]
        row = df[np.logical_and(
            df[MP.MODEL_NAME] == model_name, np.logical_and(
                df[MP.TABLE] == table_name, np.logical_and(df[MP.PREDICTOR] == predictor,
                                                       np.logical_and(df[MP.LABEL] == label, df[MP.VALUE] == value))))]
        return row.iloc[0][MP.PRECISION]

    def get_metrics_for_model_and_label_as_data_frame(
            self, model_name: str, table_name: str, predictor: str, label: str, pattern_type: str):
        self.__calculate_class_metrics_for_predictor_and_label__(table_name, predictor, label, pattern_type)
        df = self._df_metric[self._df_metric[MP.PATTERN_TYPE] == pattern_type]
        df_filtered = df[np.logical_and(df[MP.MODEL_NAME] == model_name,
                                        np.logical_and(df[MP.TABLE] == table_name,
                                                       np.logical_and(df[MP.PREDICTOR] == predictor,
                                                                      df[MP.LABEL] == label)))]
        df_filtered = df_filtered[[MP.VALUE, MP.PRECISION, MP.RECALL, MP.F1_SCORE, MP.ROC_AUC]]
        return df_filtered.sort_values([MP.VALUE])

    def get_sorted_value_list_for_predictor_label(
            self, model_name: str, table_name: str, predictor: str, label: str, pattern_type: str):
        self.__calculate_class_metrics_for_predictor_and_label__(table_name, predictor, label, pattern_type)
        df = self._df_metric[self._df_metric[MP.PATTERN_TYPE] == pattern_type]
        df_filtered = df[np.logical_and(df[MP.MODEL_NAME] == model_name,
                                        np.logical_and(df[MP.TABLE] == table_name,
                                        np.logical_and(df[MP.PREDICTOR] == predictor, df[MP.LABEL] == label)))]
        return sorted(list(set(df_filtered[MP.VALUE])))

    def __get_df_features_and_labels_for_predictor__(self, table_name: str, predictor: str):
        key = self.__get_key_for_df__(table_name, predictor)
        if key not in self._df_features_and_labels_dict:
            self._df_features_and_labels_dict[key] = \
                self.__get_data_frame_for_features_and_labels__(table_name, predictor)
        return self._df_features_and_labels_dict[key]

    def __get_features_columns_for_predictor__(self, table_name: str, predictor: str):
        key = self.__get_key_for_df__(table_name, predictor)
        if key not in self._features_column_dict:
            self._features_column_dict[key] = self.__get_feature_columns__(table_name, predictor)
        return self._features_column_dict[key]

    def __get_trained_model__(self, model_name: str, table_name: str, predictor: str, label_column: str):
        key = self.__get_key_for_trained_model__(model_name, table_name, predictor, label_column)
        if key not in self._trained_model_dict:
            df = self.__get_df_features_and_labels_for_predictor__(table_name, predictor)
            feature_columns = self.__get_features_columns_for_predictor__(table_name, predictor)
            x_train = df[feature_columns]
            y_train = df[label_column]
            model = LearningMachineFactory.get_model_by_model_type(model_name)  # we need a new model for each key
            model.fit(x_train, y_train)
            self._trained_model_dict[key] = model
        return self._trained_model_dict[key]

    def __calculate_class_metrics__(self, table_name: str, predictor: str, label: str, pattern_type: str):
        df = self.__get_df_features_and_labels_for_predictor__(table_name, predictor)
        if pattern_type != FT.ALL:
            df = df[df[DC.PATTERN_TYPE] == pattern_type]
        feature_columns = self.__get_features_columns_for_predictor__(table_name, predictor)
        x_train = df[feature_columns]
        y_train = df[label]
        for model_name, model in self._model_dict.items():
            self.__print_class_metrics_details__(model_name, table_name, predictor, label, pattern_type)
            if model_name == MT.OPTIMIZER:
                y_sorted_value_list, f1_score_dict, recall_dict, precision_dict, roc_auc_dict = \
                    self.__get_parameters_for_optimizer__(table_name, predictor, label, pattern_type)
            else:
                model_performance = ModelPerformance(model, x_train, y_train, label)
                y_sorted_value_list = model_performance.y_sorted_value_list
                f1_score_dict = model_performance.f1_score_dict
                recall_dict = model_performance.recall_dict
                precision_dict = model_performance.precision_dict
                roc_auc_dict = model_performance.roc_auc_dict
            for y_value in y_sorted_value_list:
                self._class_dict[MP.MODEL_NAME].append(model_name)
                self._class_dict[MP.TABLE].append(table_name)
                self._class_dict[MP.PREDICTOR].append(predictor)
                self._class_dict[MP.LABEL].append(label)
                self._class_dict[MP.PATTERN_TYPE].append(pattern_type)
                self._class_dict[MP.VALUE].append(y_value)
                self._class_dict[MP.F1_SCORE].append(f1_score_dict[y_value] if y_value in f1_score_dict else 0)
                self._class_dict[MP.PRECISION].append(precision_dict[y_value] if y_value in precision_dict else 0)
                self._class_dict[MP.RECALL].append(recall_dict[y_value] if y_value in recall_dict else 0)
                self._class_dict[MP.ROC_AUC].append(roc_auc_dict[y_value] if y_value in recall_dict else 0)
        self._df_metric = self.__get_data_frame_from_metric_dict__()

    def __get_data_frame_from_metric_dict__(self):
        df = pd.DataFrame.from_dict(self._class_dict)
        return df[[key for key in self._class_dict]]

    def __get_parameters_for_optimizer__(self, table_name, predictor, label, pattern_type):
        df = self.__get_data_frame_from_metric_dict__()
        df_filtered = df[np.logical_and(df[MP.PATTERN_TYPE] == pattern_type,
                                        np.logical_and(df[MP.TABLE] == table_name,
                                                       np.logical_and(df[MP.PREDICTOR] == predictor,
                                                                      df[MP.LABEL] == label)))]

        y_sorted_value_list = sorted(list(set(df_filtered[MP.VALUE])))
        df_group_f1_score_max = df_filtered.groupby([MP.VALUE])[MP.F1_SCORE].max()
        df_group_recall_max = df_filtered.groupby([MP.VALUE])[MP.RECALL].max()
        df_group_precision_max = df_filtered.groupby([MP.VALUE])[MP.PRECISION].max()
        df_group_roc_auc_max = df_filtered.groupby([MP.VALUE])[MP.ROC_AUC].max()

        f1_score_dict = {y_value: df_group_f1_score_max.loc[y_value] for y_value in y_sorted_value_list}
        recall_dict = {y_value: df_group_recall_max.loc[y_value] for y_value in y_sorted_value_list}
        precision_dict = {y_value: df_group_precision_max.loc[y_value] for y_value in y_sorted_value_list}
        roc_auc_dict = {y_value: df_group_roc_auc_max.loc[y_value] for y_value in y_sorted_value_list}

        return y_sorted_value_list, f1_score_dict, recall_dict, precision_dict, roc_auc_dict


    @staticmethod
    def __print_class_metrics_details__(model_name: str, table: str, predictor: str, label: str, pattern_type: str):
        key_model = '{}-{}-{}-{}-PT_{}'.format(model_name, table, predictor, label, pattern_type)
        print('calculate_class_metrics: {}'.format(key_model))

    def __get_data_frame_for_features_and_labels__(self, table_name: str, predictor: str) -> pd.DataFrame:
        if table_name == STBL.PATTERN:
            if predictor == PRED.TOUCH_POINT:
                query = self._pattern_table.query_for_feature_and_label_data_touch_points
            elif predictor == PRED.BEFORE_BREAKOUT:
                query = self._pattern_table.query_for_feature_and_label_data_before_breakout
            else:
                query = self._pattern_table.query_for_feature_and_label_data_after_breakout
        else:
            query = self._trade_table.query_for_feature_and_label_data_for_trades
        return DatabaseDataFrame(self._db_stock, query).df

    def __get_feature_columns__(self, table_name: str, predictor: str):
        if table_name == STBL.PATTERN:
            if predictor == PRED.TOUCH_POINT:
                return self._pattern_table.feature_columns_touch_points
            elif predictor == PRED.BEFORE_BREAKOUT:
                return self._pattern_table.features_columns_before_breakout
            else:
                return self._pattern_table.features_columns_after_breakout
        else:
            return self._trade_table.feature_columns_for_trades

    def __get_label_columns__(self, table_name: str, predictor: str):
        if table_name == STBL.PATTERN:
            if predictor == PRED.TOUCH_POINT:
                return self._pattern_table.get_label_columns_touch_points_for_statistics()
            elif predictor == PRED.BEFORE_BREAKOUT:
                return self._pattern_table.get_label_columns_before_breakout_for_statistics()
            elif predictor == PRED.AFTER_BREAKOUT:
                return self._pattern_table.get_label_columns_after_breakout_for_statistics()
        else:
            return self._trade_table.get_label_columns_for_trades_statistics()
