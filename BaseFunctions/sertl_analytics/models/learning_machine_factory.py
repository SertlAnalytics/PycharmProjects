"""
Description: This module is the factory for the machine learning classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-12-21
"""

from sertl_analytics.constants.pattern_constants import MT
from sertl_analytics.models.learning_machine import LearningMachine
from sertl_analytics.models.learning_machine import LmKNeighborsClassifier, LmSVM
from sertl_analytics.models.learning_machine import LmDecisionTreeClassifier, LmLogisticRegression
from sertl_analytics.models.learning_machine import LmSequentialClassification, LmRandomForestClassifier


class LearningMachineFactory:
    @staticmethod
    def get_classifier_model_dict():
        model_type_list = MT.get_all_classifiers()
        return {model: LearningMachineFactory.get_model_by_model_type(model) for model in model_type_list}

    @staticmethod
    def get_nn_classifier_model_dict():
        model_type_list = [MT.NN]
        return {model: LearningMachineFactory.get_model_by_model_type(model) for model in model_type_list}

    @staticmethod
    def get_classifier_learning_machine_dict():
        model_type_list = MT.get_all_classifiers()
        return {model: LearningMachineFactory.get_lm_by_model_type(model) for model in model_type_list}

    @staticmethod
    def get_nn_classifier_learning_machine_dict():
        model_type_list = [MT.NN]
        return {model: LearningMachineFactory.get_lm_by_model_type(model) for model in model_type_list}

    @staticmethod
    def get_learning_machine_for_model_as_dict(model_type: str):
        return {model_type: LearningMachineFactory.get_lm_by_model_type(model_type)}

    @staticmethod
    def get_model_by_model_type(model_type: str):
        lm = LearningMachineFactory.get_lm_by_model_type(model_type)
        return lm.get_model()

    @staticmethod
    def get_lm_by_model_type(model_type: str) -> LearningMachine:
        if model_type == MT.K_NEAREST_NEIGHBORS:
            return LmKNeighborsClassifier()
        elif model_type == MT.LOGISTIC_REGRESSION:
            return LmLogisticRegression()
        elif model_type == MT.DECISION_TREE:
            return LmDecisionTreeClassifier()
        elif model_type == MT.RANDOM_FOREST:
            return LmRandomForestClassifier()
        elif model_type == MT.SVM:
            return LmSVM()
        elif model_type == MT.NN:
            return LmSequentialClassification()
        else:
            return LmKNeighborsClassifier()
