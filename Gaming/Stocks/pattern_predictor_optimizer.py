"""
Description: This module is the central modul for optimizing prediction by taking the predictor with the
best precision for a certain label.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-08-22
"""

from sertl_analytics.constants.pattern_constants import PRED, STBL, FT, DC, MT, MDC
from sertl_analytics.models.learning_machine_factory import LearningMachineFactory
from sertl_analytics.mydates import MyDate
import numpy as np
from pattern_database.stock_database import StockDatabase
from pattern_database.stock_access_layer import AccessLayer4Metric
from pattern_database.stock_access_layer_prediction import AccessLayerPrediction
from sertl_analytics.models.performance_measure import ModelPerformance
import math


class PatternPredictorOptimizer:
    def __init__(self, db_stock: StockDatabase):
        self._db_stock = db_stock
        self._access_layer_metric = AccessLayer4Metric(self._db_stock)
        self._access_layer_prediction = AccessLayerPrediction(self._db_stock)
        self._model_dict = LearningMachineFactory.get_classifier_learning_machine_dict()
        self._df_metric = None
        self._df_metric_optimal = None
        self.__calculate_df_metrics__()
        self._trained_model_dict = {}
        self._is_test = False

    @property
    def db_stock(self):
        return self._db_stock

    def predict(self, table_name: str, predictor: str, label: str, pattern_type: str, x_data: list):
        self.__train_models__(table_name, predictor, label, pattern_type)
        x_data_array = self._access_layer_prediction.get_x_data_in_correct_format(x_data)
        return self.get_optimal_prediction(table_name, predictor, label, pattern_type, x_data_array)

    def calculate_class_metrics_for_predictor_and_label_for_today(self, pattern_list: list):
        table_list = [STBL.PATTERN, STBL.TRADE]
        predictor_dict_list = {STBL.PATTERN: PRED.get_for_pattern_all(), STBL.TRADE: PRED.get_for_trade_all()}
        for table in table_list:
            for predictor in predictor_dict_list[table]:
                label_list = self._access_layer_prediction.get_label_columns_for_predictor(table, predictor)
                for label in label_list:
                    for pattern_type in pattern_list:
                        self.__calculate_class_metrics_for_predictor_and_label__(table, predictor, label, pattern_type)

    def __calculate_df_metrics__(self):
        self._df_metric = self._access_layer_metric.get_actual_metric_data_frame()
        self._df_metric_optimal = None if self._df_metric.empty else self.__get_df_metric_optimal__()

    def __get_df_metric_optimal__(self):
        group_by_columns = [MDC.TABLE, MDC.PREDICTOR, MDC.LABEL, MDC.PATTERN_TYPE, MDC.VALUE]
        value_columns = [MDC.F1_SCORE, MDC.RECALL, MDC.PRECISION, MDC.ROC_AUC]
        df_group_max = self._df_metric.groupby(group_by_columns)[value_columns].max()
        df_group_max.reset_index(inplace=True)
        return df_group_max

    def get_optimal_prediction(self, table_name: str, predictor: str, label: str, pattern_type: str, x_data: np.array):
        # if label == DC.BREAKOUT_DIRECTION_ID:
        #     print('stop: {}'.format(label))
        prediction_precision_optimal = 0
        prediction_optimal = - math.inf
        for model_name in self._model_dict:
            prediction = self.__get_prediction_for_model__(
                model_name, table_name, predictor, label, pattern_type, x_data)
            if prediction is not None:
                prediction_precision = self.__get_precision_for_model_value__(
                    model_name, table_name, predictor, label, pattern_type, prediction)
                if prediction_precision > prediction_precision_optimal:
                    prediction_precision_optimal = prediction_precision
                    prediction_optimal = prediction
        return 0 if prediction_optimal == - math.inf else prediction_optimal

    def __get_prediction_for_model__(
            self, model_name, table: str, predictor: str, label: str, pattern_type: str, x_data: np.array):
        trained_model = self.__get_trained_model__(model_name, table, predictor, label, pattern_type)
        if trained_model is None:
            return None
        prediction = trained_model.predict(x_data)[0]
        return prediction

    @staticmethod
    def __get_key_for_trained_model__(model_name: str, table_name: str, predictor: str, label: str, pattern_type: str):
        return '{}-{}-{}-{}-{}'.format(model_name, table_name, predictor, label, pattern_type)

    def __calculate_class_metrics_for_predictor_and_label__(
            self, table_name: str, predictor: str, label: str, pattern_type: str):
        if not self.__is_class_metric_for_predictor_and_label_available__(table_name, predictor, label, pattern_type):
            self.__calculate_class_metrics__(table_name, predictor, label, pattern_type)

    def __get_precision_for_model_value__(
            self, model_name: str, table_name: str, predictor: str, label: str, pattern_type: str, value):
        self.__calculate_class_metrics_for_predictor_and_label__(table_name, predictor, label, pattern_type)
        df = self._df_metric[self._df_metric[MDC.PATTERN_TYPE] == pattern_type]
        row = df[np.logical_and(
            df[MDC.MODEL] == model_name, np.logical_and(
                df[MDC.TABLE] == table_name, np.logical_and(df[MDC.PREDICTOR] == predictor,
                                                       np.logical_and(df[MDC.LABEL] == label, df[MDC.VALUE] == value))))]
        if row.empty:
            return 0
        return row.iloc[0][MDC.PRECISION]

    def __is_class_metric_for_predictor_and_label_available__(
            self, table_name: str, predictor: str, label: str, pattern_type: str):
        if self._df_metric.shape[0] == 0 or self._is_test:
            return False
        df = self._df_metric[self._df_metric[MDC.PATTERN_TYPE] == pattern_type]
        df_filtered = df[np.logical_and(df[MDC.TABLE] == table_name,
                                        np.logical_and(df[MDC.PREDICTOR] == predictor, df[MDC.LABEL] == label))]
        return df_filtered.shape[0] > 0

    def get_metrics_for_model_and_label_as_data_frame(
            self, model_name: str, table_name: str, predictor: str, label: str, pattern_type: str):
        if model_name == MT.OPTIMIZER:  # we don't have a MDC.MODEL column
            df = self._df_metric_optimal[self._df_metric_optimal[MDC.PATTERN_TYPE] == pattern_type]
        else:
            self.__calculate_class_metrics_for_predictor_and_label__(table_name, predictor, label, pattern_type)
            df = self._df_metric
            df = df[np.logical_and(df[MDC.PATTERN_TYPE] == pattern_type, df[MDC.MODEL] == model_name)]
        df_filtered = df[np.logical_and(df[MDC.TABLE] == table_name,
                                        np.logical_and(df[MDC.PREDICTOR] == predictor, df[MDC.LABEL] == label))]
        df_filtered = df_filtered[[MDC.VALUE, MDC.PRECISION, MDC.RECALL, MDC.F1_SCORE, MDC.ROC_AUC]]
        return df_filtered.sort_values([MDC.VALUE])

    def get_sorted_value_list_for_predictor_label(
            self, model_name: str, table_name: str, predictor: str, label: str, pattern_type: str):
        self.__calculate_class_metrics_for_predictor_and_label__(table_name, predictor, label, pattern_type)
        df = self._df_metric[self._df_metric[MDC.PATTERN_TYPE] == pattern_type]
        df_filtered = df[np.logical_and(df[MDC.MODEL] == model_name,
                                        np.logical_and(df[MDC.TABLE] == table_name,
                                        np.logical_and(df[MDC.PREDICTOR] == predictor, df[MDC.LABEL] == label)))]
        return sorted(list(set(df_filtered[MDC.VALUE])))

    def test_model(self, model_name: str, table_name: str, predictor: str, label: str, pattern_type: str):
        self._model_dict = LearningMachineFactory.get_learning_machine_for_model_as_dict(model_name)
        self._is_test = True  # so don't save...
        self.__calculate_class_metrics_for_predictor_and_label__(table_name, predictor, label, pattern_type)
        df = self._df_metric[self._df_metric[MDC.PATTERN_TYPE] == pattern_type]
        df_filtered = df[np.logical_and(df[MDC.MODEL] == model_name,
                                        np.logical_and(df[MDC.TABLE] == table_name,
                                        np.logical_and(df[MDC.PREDICTOR] == predictor, df[MDC.LABEL] == label)))]
        return sorted(list(set(df_filtered[MDC.VALUE])))

    def __train_models__(self, table_name: str, predictor: str, label_column: str, pattern_type: str):
        for model_name in self._model_dict:
            key = self.__get_key_for_trained_model__(model_name, table_name, predictor, label_column, pattern_type)
            if key not in self._trained_model_dict:
                x_train, y_train = self._access_layer_prediction.get_x_data_y_train_data_for_predictor(
                    table_name, predictor, label_column, pattern_type)
                lm = LearningMachineFactory.get_lm_by_model_type(model_name)  # we need a new learning machine for each key
                lm.fit(x_train, y_train)
                self._trained_model_dict[key] = lm

    def __get_trained_model__(
            self, model_name: str, table_name: str, predictor: str, label_column: str, pattern_type: str):
        key = self.__get_key_for_trained_model__(model_name, table_name, predictor, label_column, pattern_type)
        if key in self._trained_model_dict:
            return self._trained_model_dict[key]

    def train_models_for_breakout(self, x_train, y_train):
        self.retrain_trained_models(STBL.STOCKS, PRED.BREAKOUT_LEVEL, 'Breakout_level', FT.ALL, x_train, y_train)

    def retrain_trained_models(
            self, table_name: str, predictor: str, label_column: str, pattern_type: str, x_train, y_train):
        y_train_set = set(y_train)
        for model_name, model in self._model_dict.items():
            key = self.__get_key_for_trained_model__(model_name, table_name, predictor, label_column, pattern_type)
            if len(y_train_set) == 1:
                if key in self._trained_model_dict:  # remove this from the dict since no training is possible
                    del self._trained_model_dict[key]
            else:
                if key not in self._trained_model_dict:  # we need a new learning machine for each key
                    self._trained_model_dict[key] = LearningMachineFactory.get_lm_by_model_type(model_name)
                self._trained_model_dict[key].fit(x_train, y_train)

    def __calculate_class_metrics__(self, table_name: str, predictor: str, label: str, pattern_type: str):
        x_train, y_train = self._access_layer_prediction.get_x_data_y_train_data_for_predictor(
            table_name, predictor, label, pattern_type)
        insert_dict_list = []
        valid_date = MyDate.get_date_as_string_from_date_time()
        for model_name, model in self._model_dict.items():
            self.__print_class_metrics_details__(model_name, table_name, predictor, label, pattern_type)
            model_performance = ModelPerformance(model, x_train, y_train, label)
            y_sorted_value_list = model_performance.y_sorted_value_list
            f1_score_dict = model_performance.f1_score_dict
            recall_dict = model_performance.recall_dict
            precision_dict = model_performance.precision_dict
            roc_auc_dict = model_performance.roc_auc_dict

            for y_value in y_sorted_value_list:
                insert_dict_list.append({
                    MDC.VALID_DT: valid_date,
                    MDC.MODEL: model_name,
                    MDC.TABLE: table_name,
                    MDC.PREDICTOR: predictor,
                    MDC.LABEL: label,
                    MDC.PATTERN_TYPE: pattern_type,
                    MDC.VALUE: y_value,
                    MDC.F1_SCORE: f1_score_dict[y_value] if y_value in f1_score_dict else 0,
                    MDC.PRECISION: precision_dict[y_value] if y_value in precision_dict else 0,
                    MDC.RECALL: recall_dict[y_value] if y_value in recall_dict else 0,
                    MDC.ROC_AUC: roc_auc_dict[y_value] if y_value in recall_dict else 0
                })
        if self._is_test:
            print(insert_dict_list)
        else:
            if len(insert_dict_list) > 0:
                self._access_layer_metric.insert_data(insert_dict_list)
                self.__calculate_df_metrics__()

    def __get_parameters_for_optimizer__(self, table_name, predictor, label, pattern_type):
        df = self._df_metric
        df_filtered = df[np.logical_and(df[MDC.PATTERN_TYPE] == pattern_type,
                                        np.logical_and(df[MDC.TABLE] == table_name,
                                                       np.logical_and(df[MDC.PREDICTOR] == predictor,
                                                                      df[MDC.LABEL] == label)))]

        y_sorted_value_list = sorted(list(set(df_filtered[MDC.VALUE])))
        df_group_f1_score_max = df_filtered.groupby([MDC.VALUE])[MDC.F1_SCORE].max()
        df_group_recall_max = df_filtered.groupby([MDC.VALUE])[MDC.RECALL].max()
        df_group_precision_max = df_filtered.groupby([MDC.VALUE])[MDC.PRECISION].max()
        df_group_roc_auc_max = df_filtered.groupby([MDC.VALUE])[MDC.ROC_AUC].max()

        f1_score_dict = {y_value: df_group_f1_score_max.loc[y_value] for y_value in y_sorted_value_list}
        recall_dict = {y_value: df_group_recall_max.loc[y_value] for y_value in y_sorted_value_list}
        precision_dict = {y_value: df_group_precision_max.loc[y_value] for y_value in y_sorted_value_list}
        roc_auc_dict = {y_value: df_group_roc_auc_max.loc[y_value] for y_value in y_sorted_value_list}

        return y_sorted_value_list, f1_score_dict, recall_dict, precision_dict, roc_auc_dict

    @staticmethod
    def __print_class_metrics_details__(model_name: str, table: str, predictor: str, label: str, pattern_type: str):
        key_model = '{}-{}-{}-{}-PT_{}'.format(model_name, table, predictor, label, pattern_type)
        print('calculate_class_metrics: {}'.format(key_model))


