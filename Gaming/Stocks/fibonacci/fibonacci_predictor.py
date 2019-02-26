"""
Description: This module is the central modul for optimizing prediction by taking the predictor with the
best precision for a certain label.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-08-22
"""

from sertl_analytics.constants.pattern_constants import PRED, STBL, FT, DC, MT, MDC, WPC
from sertl_analytics.models.learning_machine_factory import LearningMachineFactory
import numpy as np
import pandas as pd
from pattern_database.stock_database import StockDatabase
from pattern_database.stock_wave_entity import WaveEntityCollection
from pattern_database.stock_access_layer_prediction import AccessLayerPrediction
from pattern_database.stock_access_layer import AccessLayer4Wave
from fibonacci.fibonacci_wave import FibonacciWave
from pattern_database.stock_wave_entity import WaveEntity


class FibonacciPredictor:
    """
    This class predicts whether a finished Fibonacci Wave is really finished
    - and can be traded in recommendation tab
    """
    def __init__(self, db_stock: StockDatabase, compression_classes=4):
        print('Initializing FibonacciPredictor')
        self._db_stock = db_stock
        self._compression_classes = compression_classes
        self._labels = [DC.WAVE_END_FLAG, DC.WAVE_MAX_RETR_TS_PCT, DC.WAVE_MAX_RETR_PCT]
        self._access_layer_wave = AccessLayer4Wave(db_stock)
        self._access_layer_prediction = AccessLayerPrediction(db_stock)
        self._model_dict = LearningMachineFactory.get_classifier_learning_machine_dict(False)
        self._model_regression_dict = LearningMachineFactory.get_regression_learning_machine_dict()
        self._df_waves_for_prediction = self.__get_df_waves_for_prediction__()
        self._x_train = self.__get_x_train__()
        self._y_train_dict = self.__get_y_train_dict__()
        self._trained_model_dict = {}
        self.__fill_trained_model_dict__()
        self._best_trained_model_dict = {}
        self._best_trained_regression_model_dict = {}
        self.__fill_best_model_dict__()
        self.__fill_best_regression_model_dict__()

    @property
    def db_stock(self):
        return self._db_stock

    def add_predictions_to_wave(self, fib_wave: FibonacciWave, print_prediction=False):
        if not fib_wave.is_wave_ready_for_wave_table():
            return
        data_dict = fib_wave.data_dict_obj.get_data_dict_for_target_table()
        data_dict_series = pd.Series(data_dict)
        wave_entity = WaveEntity(data_dict_series)
        x_data = wave_entity.data_list_for_prediction_x_data
        prediction_dict = self.get_prediction_as_dict(x_data)
        fib_wave.update_prediction_data_by_dict(prediction_dict)
        if print_prediction:
            fib_wave.print_predictions()

    def get_prediction_as_dict(self, x_data: list):
        return {label: self.predict(label, x_data) for label in self._labels}

    def predict(self, label: str, x_data: list):
        x_data_array = self._access_layer_prediction.get_x_data_in_correct_format(x_data)
        best_model_for_label = self._best_trained_model_dict[label]
        prediction_classifier = best_model_for_label.predict(x_data_array)
        best_regression_model_for_label = self._best_trained_regression_model_dict[label]
        prediction_regression = best_regression_model_for_label.predict(x_data_array)
        return [prediction_classifier[0], round(prediction_regression[0], 2)]

    def __get_df_waves_for_prediction__(self, symbol=''):
        df_waves = self._access_layer_wave.get_base_wave_data_frame_for_prediction(symbol)
        wave_entity_collection = WaveEntityCollection(df_waves, symbol=symbol)
        df = wave_entity_collection.get_data_frame_for_prediction()
        return df[WPC.get_wave_prediction_columns()]

    def __get_prediction_for_model__(
            self, model_name, table: str, predictor: str, label: str, x_data: np.array):
        trained_model = self.__get_trained_model__(model_name, table, predictor, label)
        if trained_model is None:
            return None
        prediction = trained_model.predict(x_data)[0]
        return prediction

    def __fill_trained_model_dict__(self):
        for label in self._labels:
            self.train_models(label)

    def train_models(self, label_column: str):
        for model_name in [name for name in self._model_dict] + [name for name in self._model_regression_dict]:
            key = self.__get_key_for_trained_model__(model_name, label_column)
            if key not in self._trained_model_dict:
                x_train, y_train = self._x_train, self._y_train_dict[label_column]
                lm = LearningMachineFactory.get_lm_by_model_type(model_name)  # we need a new learning machine for each key
                lm.fit(x_train, y_train)
                self._trained_model_dict[key] = lm

    def __fill_best_model_dict__(self):
        best_model_accuracy_dict = {}
        for label in self._labels:
            best_model_accuracy_dict[label] = 0
            for model_name in self._model_dict:
                key = self.__get_key_for_trained_model__(model_name, label)
                trained_model = self._trained_model_dict[key]
                cross_val_score_array = trained_model.cross_val_score(self._x_train, self._y_train_dict[label], cv=3)
                cross_val_score_mean = np.mean(cross_val_score_array)
                if cross_val_score_mean > best_model_accuracy_dict[label]:
                    best_model_accuracy_dict[label] = cross_val_score_mean
                    self._best_trained_model_dict[label] = trained_model
                    break

    def __fill_best_regression_model_dict__(self):
        for label in self._labels:
            for model_name in self._model_regression_dict:
                key = self.__get_key_for_trained_model__(model_name, label)
                trained_model = self._trained_model_dict[key]
                self._best_trained_regression_model_dict[label] = trained_model
                break

    def perform_cross_validation(self, label_column: str):
        for model_name, model in self._trained_model_dict.items():
            cross_val_score_array = model.cross_val_score(self._x_train, self._y_train_dict[label_column], cv=3)
            print('{}: {}'.format(model_name, cross_val_score_array))

    def __get_x_train__(self):
        columns = self._df_waves_for_prediction.columns
        feature_columns = columns[:-3]
        return self._df_waves_for_prediction[feature_columns]

    def __get_y_train_dict__(self):
        return {label: self.__get_y_train_for_label__(label) for label in self._labels}

    def __get_y_train_for_label__(self, label: str):
        y_train = self._df_waves_for_prediction[label]
        return self.__get_compressed_y_train__(y_train)

    @staticmethod
    def __get_key_for_trained_model__(model_name: str, label: str):
        return '{}-{}'.format(model_name, label)

    def __get_compressed_y_train__(self, y_train):
        number_classes =  self._compression_classes
        diff_values = list(set(y_train))
        if len(diff_values) < number_classes:
            return y_train
        min_value = np.min(diff_values)
        max_value = np.max(diff_values)
        compressor = max(abs(min_value), abs(max_value))
        y_train_compressed = round(y_train / compressor * number_classes) / number_classes * compressor
        y_train_compressed = y_train_compressed.astype(np.int64)
        # print('\ny_train_orig: {}\ny_train_compressed: {}'.format(list(y_train)[:50], list(y_train_compressed)[:50]))
        return y_train_compressed

    def __get_trained_model__(
            self, model_name: str, table_name: str, predictor: str, label_column: str):
        key = self.__get_key_for_trained_model__(model_name, table_name, predictor, label_column)
        if key in self._trained_model_dict:
            return self._trained_model_dict[key]

    def train_models_for_breakout(self, x_train, y_train):
        self.retrain_trained_models(STBL.STOCKS, PRED.BREAKOUT_LEVEL, 'Breakout_level', x_train, y_train)

    def retrain_trained_models(
            self, table_name: str, predictor: str, label_column: str, x_train, y_train):
        y_train_set = set(y_train)
        for model_name, model in self._model_dict.items():
            key = self.__get_key_for_trained_model__(model_name, table_name, predictor, label_column)
            if len(y_train_set) == 1:
                if key in self._trained_model_dict:  # remove this from the dict since no training is possible
                    del self._trained_model_dict[key]
            else:
                if key not in self._trained_model_dict:  # we need a new learning machine for each key
                    self._trained_model_dict[key] = LearningMachineFactory.get_lm_by_model_type(model_name)
                self._trained_model_dict[key].fit(x_train, y_train)

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


