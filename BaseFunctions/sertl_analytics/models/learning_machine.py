"""
Description: This module is the main module for machine learning algorithms.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""

import numpy as np
from keras.layers import Dense
from keras.models import Sequential
from keras.utils import to_categorical
from sklearn import linear_model
from sklearn.metrics import confusion_matrix, classification_report


class Optimizer:
    ADAM = "adam"
    SGD = "Stochastic gradient descent"


class LossFunction:
    MSE = "mean_squared_error"
    CAT_CROSS = "categorical_crossentropy"


class ModelType:
    SEQUENTIAL_REGRESSION = "Model: Sequential, Type: Regression"
    SEQUENTIAL_CLASSIFICATION = "Model: Sequential, Type: Classification"
    LINEAR_REGRESSION = "Model: Linear, Type: Regression"
    LINEAR_CLASSIFICATION = "Model: Linear, Type: Classification"


class LearningMachine:
    def __init__(self, hidden_layers, optimizer: Optimizer = Optimizer.ADAM
                 , loss: LossFunction = LossFunction.MSE):
        self.hidden_layers = hidden_layers
        self.model = None
        self.model_type = None
        self.optimizer = optimizer
        self.loss = loss
        self.n_cols = 0
        self.np_predictors = None
        self.np_target = None
        self.np_prediction_data = None
        self.prediction = None
        self.prediction_pct = None  # percentage for classification
        self.accuracy = 0

    def get_regression_prediction(self, np_training_data: np.array, np_training_data_target: np.array, np_test_data: np.array):
        return self.__get_prediction__(np_training_data, np_training_data_target, np_test_data)

    def __get_prediction__(self, predictors: np.array, target: np.array, prediction_data: np.array):
        self.np_predictors = predictors
        self.__set_np_target__(target)
        self.np_prediction_data = prediction_data
        self.n_cols = self.np_predictors.shape[1]
        # self.print_details()
        self.model = self.get_model()
        self.__add_hidden_layers__()
        self.__add_output_layer__()
        self.__compile_model__()
        self.model.fit(self.np_predictors, self.np_target)
        # make prediction
        self.prediction = self.model.predict(self.np_prediction_data)
        self.__manipulate_model_prediction__()
        return self.prediction

    def get_model(self):
        pass

    def __manipulate_model_prediction__(self):
        pass

    def __set_np_target__(self, target: np.array):
        self.np_target = target

    def __add_output_layer__(self):
        pass

    def __compile_model__(self):
        pass

    def compare_prediction_with_results(self, test_set_target: np.array):
        np_comparison = np.zeros((self.prediction.shape[0], 3), dtype=np.float)
        hit_counter = 0
        for k in range(self.prediction.shape[0]):
            np_comparison[k, 0] = self.prediction[k]
            np_comparison[k, 1] = test_set_target[k]
            np_comparison[k, 2] = np_comparison[k, 0] - np_comparison[k, 1]
            if abs(np_comparison[k, 2]) < 0.5:
                hit_counter += 1
        # print(np.round(np_comparison, 2))
        self.accuracy = hit_counter/self.prediction.shape[0]
        self.__print_statistical_data__(test_set_target)

    def __print_statistical_data__(self, test_set_target: np.array):
        pass

    def print_details(self):
        print('optimizer={}, loss={}, np_predictors.shape={}, np_target.shape={}, np_pred_data.shape={}'.format(
            self.optimizer, self.loss, self.np_predictors.shape, self.np_target.shape, self.np_prediction_data.shape))

    def __add_hidden_layers__(self):
        pass


class LmLinearRegression(LearningMachine):
    def __init__(self):  # is needed since we don't need any other parameters
        pass

    def get_model(self):
        return linear_model.LinearRegression()


class LmLogisticRegression(LearningMachine):
    def __init__(self):  # is needed since we don't need any other parameters
        pass

    def get_model(self):
        return linear_model.LogisticRegression()

    def __print_statistical_data__(self, np_test_set_target : np.array):
        self.accuracy = self.model.score(self.np_prediction_data, np_test_set_target)
        print(confusion_matrix(np_test_set_target, self.prediction))
        print(classification_report(np_test_set_target, self.prediction))


class LmSequentialRegression(LearningMachine):
    def get_model(self):
        return Sequential()

    def __add_hidden_layers__(self):
        for hl_index, hidden_layers in enumerate(self.hidden_layers):
            if hl_index == 0:
                self.model.add(Dense(hidden_layers, activation='relu', input_shape=(self.n_cols,)))
            else:
                self.model.add(Dense(hidden_layers, activation='relu'))

    def __add_output_layer__(self):
        self.model.add(Dense(self.np_target.shape[1]))  # output layer

    def __compile_model__(self):
        self.model.compile(optimizer=self.optimizer, loss=self.loss)


class LmSequentialClassification(LearningMachine):
    def __init__(self, hidden_layers, optimizer: Optimizer = Optimizer.ADAM
                 , loss: LossFunction = LossFunction.CAT_CROSS):
        LearningMachine.__init__(self, hidden_layers, optimizer, loss)

    def get_model(self):
        return Sequential()

    def __manipulate_model_prediction__(self):
        self.prediction_pct = np.max(self.prediction, axis=1).round(2)
        self.prediction = np.argmax(self.prediction, axis=1)

    def __add_hidden_layers__(self):
        for hl_index, hidden_layers in enumerate(self.hidden_layers):
            if hl_index == 0:
                self.model.add(Dense(hidden_layers, activation='relu', input_shape=(self.n_cols,)))
            else:
                self.model.add(Dense(hidden_layers, activation='relu'))

    def __compile_model__(self):
        self.model.compile(optimizer=self.optimizer, loss=self.loss, metrics=['accuracy'])

    def __set_np_target__(self, target: np.array):
        self.np_target = to_categorical(target)

    def __add_output_layer__(self):
        self.model.add(Dense(self.np_target.shape[1], activation='softmax'))