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
from sklearn import tree
from sklearn.svm import SVC
from sklearn import neighbors
from sklearn import ensemble
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from sertl_analytics.constants.pattern_constants import MT


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
    TREE_CLASSIFICATION = "Model: DecisionTree, Type: Classification"


class LearningMachineFactory:
    @staticmethod
    def get_classifier_model_dict():
        model_type_list = MT.get_all_classifiers()
        return {model: LearningMachineFactory.get_model_by_model_type(model) for model in model_type_list}

    @staticmethod
    def get_model_by_model_type(model_type: str):
        if model_type == MT.K_NEAREST_NEIGHBORS:
            return LmKNeighborsClassifier().get_model()
        elif model_type == MT.LOGISTIC_REGRESSION:
            return LmLogisticRegression().get_model()
        elif model_type == MT.DECISION_TREE:
            return LmDecisionTreeClassifier().get_model()
        elif model_type == MT.RANDOM_FOREST:
            return LmRandomForestClassifier().get_model()
        elif model_type == MT.SVM:
            return LmSVM().get_model()
        elif model_type == MT.NN:
            return LmSequentialClassification().get_model()
        else:
            return LmKNeighborsClassifier().get_model()


class LearningMachine:
    def __init__(self, hidden_layers=None, optimizer=Optimizer.ADAM, loss=LossFunction.MSE):
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

    def predict_proba(self, prediction_data: np.array):
        if self.model is None:
            self.model = self.get_model()
        return self.model.predict_proba(prediction_data)

    def compare_prediction_with_results(self, test_set_target: np.array):
        self.accuracy = accuracy_score(self.prediction, test_set_target )
        self.__print_statistical_data__(test_set_target)

    def __print_statistical_data__(self, test_set_target: np.array):
        pass

    def print_details(self):
        print('optimizer={}, loss={}, np_predictors.shape={}, np_target.shape={}, np_pred_data.shape={}'.format(
            self.optimizer, self.loss, self.np_predictors.shape, self.np_target.shape, self.np_prediction_data.shape))

    def __add_hidden_layers__(self):
        pass


class LmKNeighborsClassifier(LearningMachine):
    def __init__(self, n_neighbors=7, weights='distance'):
        self._n_neighbors = 7
        self._weights = weights
        LearningMachine.__init__(self)

    def get_model(self):
        return neighbors.KNeighborsClassifier(n_neighbors=self._n_neighbors, weights=self._weights)


class LmSVM(LearningMachine):
    def __init__(self, gamma='auto'):
        self._gamma = gamma
        LearningMachine.__init__(self)

    def get_model(self):
        return SVC(gamma=self._gamma)


class LmDecisionTreeClassifier(LearningMachine):
    def __init__(self, random_state=0):
        self._random_state = random_state
        LearningMachine.__init__(self)

    def get_model(self):
        return tree.DecisionTreeClassifier(random_state=self._random_state)


class LmRandomForestClassifier(LearningMachine):
    def __init__(self, n_estimators=100, max_depth=2, random_state=0):
        self._n_estimators = n_estimators
        self._max_depth = max_depth
        self._random_state =random_state
        LearningMachine.__init__(self)

    def get_model(self):
        return ensemble.RandomForestClassifier(
            n_estimators=self._n_estimators, max_depth=self._max_depth, random_state=self._random_state)


class LmLinearRegression(LearningMachine):
    def get_model(self):
        return linear_model.LinearRegression()


class LmLogisticRegression(LearningMachine):
    def get_model(self):
        # Create the hyperparameter grid
        # c_space = np.logspace(-5, 8, 15)
        # param_grid = {'C': c_space, 'penalty': ['l1', 'l2']}
        # logreg_cv = GridSearchCV(linear_model.LogisticRegression(), param_grid, cv=5)
        # return logreg_cv
        # scaler = StandardScaler()
        # pipeline = make_pipeline(scaler, linear_model.LogisticRegression())
        return linear_model.LogisticRegression()

    def __print_statistical_data__(self, np_test_set_target : np.array):
        self.accuracy = self.model.score(self.np_prediction_data, np_test_set_target)
        print(confusion_matrix(np_test_set_target, self.prediction))
        print(classification_report(np_test_set_target, self.prediction))
        # print("Tuned Logistic Regression Parameter: {}".format(self.model.best_params_))
        # print("Tuned Logistic Regression Accuracy: {}".format(self.model.best_score_))


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
    def __init__(self, hidden_layers=None, optimizer=Optimizer.ADAM, loss=LossFunction.CAT_CROSS):
        if hidden_layers is None:
            hidden_layers = [1000, 1000, 1000, 1000]
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