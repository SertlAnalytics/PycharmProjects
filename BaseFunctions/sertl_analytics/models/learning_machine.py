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
from sklearn.model_selection import cross_val_predict, cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler


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


class LearningMachine:
    def __init__(self, hidden_layers=None, optimizer=Optimizer.ADAM, loss=LossFunction.MSE):
        self.scaler = None
        self.hidden_layers = hidden_layers
        self.model = None
        self.model_type = None
        self.optimizer = optimizer
        self.loss = loss
        self.np_predictors = None
        self.np_target = None
        self.np_prediction_data = None
        self.prediction = None
        self.prediction_pct = None  # percentage for classification
        self.accuracy = 0

    @property
    def x_col(self):
        return self.np_predictors.shape[1]

    @property
    def y_col(self):
        return self.np_target.shape[1]

    def fit(self, x_train: np.array, y_train: np.array):
        if self.model is None:
            self.model = self.get_model()
        x_train_scaled = self.__get_newly_scaled_data__(x_train)
        self.model.fit(x_train_scaled, y_train)

    def __get_newly_scaled_data__(self, x_train):
        self.scaler = StandardScaler().fit(x_train)
        x_train_scaled = self.scaler.transform(x_train)
        return x_train_scaled

    def predict(self, prediction_data: np.array):
        prediction_data_scaled = self.scaler.transform(prediction_data)
        return self.model.predict(prediction_data_scaled)

    def get_regression_prediction(self, np_training_data: np.array, np_training_data_target: np.array, np_test_data: np.array):
        return self.__get_prediction__(np_training_data, np_training_data_target, np_test_data)

    def __get_prediction__(self, predictors: np.array, target: np.array, prediction_data: np.array):
        self.np_predictors = self.__get_newly_scaled_data__(predictors)
        self.__set_np_target__(target)
        self.np_prediction_data = self.scaler.transform(prediction_data)
        self.model = self.get_model()
        self.fit(self.np_predictors, self.np_target)
        # make prediction
        self.prediction = self.predict(self.np_prediction_data)
        self.__manipulate_model_prediction__()
        return self.prediction

    def cross_val_predict(self, predictors: np.array, target: np.array, cv: int):
        if self.model is None:
            self.model = self.get_model()
        return cross_val_predict(self.model, predictors, target, cv=cv)

    def cross_val_score(self, predictors: np.array, target: np.array, cv: int, scoring='accuracy'):
        if self.model is None:
            self.model = self.get_model()
        return cross_val_score(self.model, predictors, target, cv=cv, scoring=scoring)

    def get_model(self):
        pass

    def __manipulate_model_prediction__(self):
        pass

    def __set_np_target__(self, target: np.array):
        self.np_target = target

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


class LmSequential(LearningMachine):
    def fit(self, x_train: np.array, y_train: np.array):
        self.np_predictors = x_train
        self.__set_np_target__(y_train)
        if self.model is None:
            self.model = self.get_model()
        self.model.fit(self.np_predictors, self.np_target, epochs=150, batch_size=10, verbose=0)

    def get_model(self):
        model = Sequential()
        self.__add_hidden_layers__(model)
        self.__add_output_layer__(model)
        self.__compile_model__(model)
        return model

    def __add_hidden_layers__(self, model: Sequential):
        pass

    def __add_output_layer__(self, model: Sequential):
        pass

    def __compile_model__(self, model: Sequential):
        model.compile(optimizer=self.optimizer, loss=self.loss)

    def cross_val_predict(self, predictors: np.array, target: np.array, cv: int):
        # ToDo - we need the prediction data not the accuracy - this is done below...
        kfold = StratifiedKFold(n_splits=cv, shuffle=True, random_state=7)
        cv_scores = []
        for train, test in kfold.split(predictors, target):
            self.model = None
            self.fit(predictors[train], target[train])
            # evaluate the model
            scores = self.model.evaluate(self.np_predictors, self.np_target, verbose=0)
            print("%s: %.2f%%" % (self.model.metrics_names[1], scores[1] * 100))
            cv_scores.append(scores[1] * 100)
        return cv_scores

    def cross_val_score(self, predictors: np.array, target: np.array, cv: int, scoring='accuracy'):
        # ToDo: https://machinelearningmastery.com/regression-tutorial-keras-deep-learning-library-python/
        kfold = StratifiedKFold(n_splits=cv, shuffle=True, random_state=7)
        cv_scores = []
        for train, test in kfold.split(predictors, target):
            self.model = None
            self.fit(predictors[train], target[train])
            # evaluate the model
            scores = self.model.evaluate(predictors[test], target[test], verbose=0)
            print("%s: %.2f%%" % (self.model.metrics_names[1], scores[1] * 100))
            cv_scores.append(scores[1] * 100)
        return cv_scores


class LmSequentialRegression(LmSequential):
    def __add_hidden_layers__(self, model: Sequential):
        for hl_index, hidden_layers in enumerate(self.hidden_layers):
            if hl_index == 0:
                model.add(Dense(hidden_layers, activation='relu', input_shape=(self.x_col,)))
            else:
                model.add(Dense(hidden_layers, activation='relu'))

    def __add_output_layer__(self, model: Sequential):
        model.add(Dense(self.y_col))  # output layer


class LmSequentialClassification(LmSequential):
    def __init__(self, hidden_layers=None, optimizer=Optimizer.ADAM, loss=LossFunction.CAT_CROSS):
        if hidden_layers is None:
            hidden_layers = [10, 100, 10]
        LearningMachine.__init__(self, hidden_layers, optimizer, loss)

    def __manipulate_model_prediction__(self):
        self.prediction_pct = np.max(self.prediction, axis=1).round(2)
        self.prediction = np.argmax(self.prediction, axis=1)

    def __add_hidden_layers__(self, model: Sequential):
        for hl_index, hidden_layers in enumerate(self.hidden_layers):
            if hl_index == 0:
                model.add(Dense(hidden_layers, activation='relu', input_shape=(self.x_col,)))
            else:
                model.add(Dense(hidden_layers, activation='relu'))

    def __compile_model__(self, model: Sequential):
        model.compile(optimizer=self.optimizer, loss=self.loss, metrics=['accuracy'])

    def __set_np_target__(self, target: np.array):
        self.np_target = to_categorical(target)

    def __add_output_layer__(self, model: Sequential):
        model.add(Dense(self.y_col, activation='softmax'))