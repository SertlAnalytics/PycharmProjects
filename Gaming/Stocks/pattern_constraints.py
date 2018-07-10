"""
Description: This module contains the constraint classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
import pandas as pd
from sertl_analytics.constants.pattern_constants import CT, SVC
from pattern_value_categorizer import ValueCategorizer


class CountConstraint:
    def __init__(self, value_category: str, comparison: str, value: float):
        self.value_category = value_category
        self.comparison = comparison
        self.comparison_value = value

    def is_value_satisfying_constraint(self, value: float):
        if self.comparison == '=':
            return value == self.comparison_value
        if self.comparison == '<=':
            return value <= self.comparison_value
        if self.comparison == '<':
            return value < self.comparison_value
        if self.comparison == '>=':
            return value >=  self.comparison_value
        if self.comparison == '>':
            return value > self.comparison_value


class Constraints:
    def __init__(self):
        self.tolerance_pct = self.__get_tolerance_pct__()
        self.global_all_in = []
        self.global_count = []
        self.global_series = []
        self.f_upper_pct_bounds = [-0.02, 0.02]
        self.f_lower_pct_bounds = [-0.02, 0.02]
        self.f_upper_lower_relation_bounds = [-5, 5]  # the relationship bounds for the linear functions increase
        self.f_regression_pct_bounds = [-0.02, 0.02]  # this constraint checks the "direction" of the data
        # [0.8, 1.2] Channel,
        self.__fill_global_constraints__()
        self.__set_bounds_for_pattern_type__()
        self.__check_dic = {}

    def are_f_lower_f_upper_pct_compliant(self, f_lower_pct: float, f_upper_pct: float):
        if self.__is_f_lower_pct_compliant__(f_lower_pct):
            if self.__is_f_upper_pct_compliant__(f_upper_pct):
                return self.__is_relation_f_upper_f_lower_compliant__(f_upper_pct, f_lower_pct)
        return False

    def is_f_regression_pct_compliant(self, f_regression_pct: float):
        if len(self.f_regression_pct_bounds) == 0:  # no bounds defined
            return True
        return self.f_regression_pct_bounds[0] <= f_regression_pct <= self.f_regression_pct_bounds[1]

    def __is_f_lower_pct_compliant__(self, f_lower_pct: float):
        if len(self.f_lower_pct_bounds) == 0:  # no lower bounds defined
            return True
        return self.f_lower_pct_bounds[0] <= f_lower_pct <= self.f_lower_pct_bounds[1]

    def __is_f_upper_pct_compliant__(self, f_upper_pct: float):
        if len(self.f_upper_pct_bounds) == 0:  # no upper bounds defined
            return True
        return self.f_upper_pct_bounds[0] <= f_upper_pct <= self.f_upper_pct_bounds[1]

    def __is_relation_f_upper_f_lower_compliant__(self, f_upper_pct: float, f_lower_pct: float):
        if len(self.f_upper_lower_relation_bounds) == 0:  # no relation defined for both slopes
            return True
        if f_lower_pct == 0:
            return True
        u_l_relation = round((f_upper_pct / f_lower_pct), 2)
        return self.f_upper_lower_relation_bounds[0] <= u_l_relation <= self.f_upper_lower_relation_bounds[1]

    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_pct_bounds = [-100.0, 100]
        self.f_lower_pct_bounds = self.f_upper_pct_bounds
        self.f_upper_lower_relation_bounds = [-100, 100]

    def get_unary_constraints(self, df: pd.DataFrame):
        pass

    def get_binary_constraints(self, df: pd.DataFrame):
        pass

    def __fill_global_constraints__(self):
        pass

    @property
    def f_upper_pct_bounds_complementary(self):
        return [-1 * x for x in reversed(self.f_upper_pct_bounds)]

    @property
    def f_lower_pct_bounds_complementary(self):
        return [-1 * x for x in reversed(self.f_lower_pct_bounds)]

    @property
    def f_upper_lower_relation_bounds_complementary(self):
        if len(self.f_upper_lower_relation_bounds) == 0:
            return []
        return [round(1/x, 3) for x in reversed(self.f_upper_lower_relation_bounds)]

    def __set_bounds_by_complementary_constraints__(self, comp_constraints):
        self.f_upper_pct_bounds = comp_constraints.f_lower_pct_bounds_complementary
        self.f_lower_pct_bounds = comp_constraints.f_upper_pct_bounds_complementary
        self.f_upper_lower_relation_bounds = comp_constraints.f_upper_lower_relation_bounds_complementary

    def are_global_constraints_satisfied(self, value_categorizer: ValueCategorizer):
        self.__check_dic[CT.ALL_IN] = self.__is_global_constraint_all_in_satisfied__(value_categorizer)
        self.__check_dic[CT.COUNT] = self.__is_global_constraint_count_satisfied__(value_categorizer)
        self.__check_dic[CT.SERIES] = self.__is_global_constraint_series_satisfied__(value_categorizer)
        return False if False in [self.__check_dic[key] for key in self.__check_dic] else True

    def __is_global_constraint_all_in_satisfied__(self, value_categorizer: ValueCategorizer):
        if len(self.global_all_in) == 0:
            return True
        return value_categorizer.are_all_values_in_value_category_list(self.global_all_in)

    def __is_global_constraint_count_satisfied__(self, value_categorizer: ValueCategorizer):
        if len(self.global_count) == 0:
            return True
        conjunction = self.global_count[0]
        for k in range(1, len(self.global_count)):
            count_constraint = self.global_count[k]
            number = value_categorizer.get_number_of_rows_with_value_category(count_constraint.value_category)
            bool_value = count_constraint.is_value_satisfying_constraint(number)
            if bool_value and conjunction == 'OR':
                return True
            elif not bool_value and conjunction == 'AND':
                return False
        return False if conjunction == 'OR' else True

    def __is_global_constraint_series_satisfied__(self, value_categorizer: ValueCategorizer):
        if len(self.global_series) == 0:
            return True
        conjunction = self.global_series[0]
        for k in range(1, len(self.global_series)):
            series = self.global_series[k]
            check_ok = self.__is_series_constraint_check_done__(series, 0, value_categorizer)
            if check_ok and conjunction == 'OR':
                return True
            elif not check_ok and conjunction == 'AND':
                return False
        return False if conjunction == 'OR' else True

    def __is_series_constraint_check_done__(self, series: list, index: int, value_categorizer: ValueCategorizer):
        if len(series) == 0:
            return True
        if index == len(value_categorizer.index_list):
            return False
        if series[0] in value_categorizer.value_category_dic[value_categorizer.index_list[index]]:
            series = series[1:]
        return self.__is_series_constraint_check_done__(series, index + 1, value_categorizer)


class TKEDownConstraints(Constraints):
    def __fill_global_constraints__(self):
        """
        1. All values have to be in a range (channel)
        2. There must be at least 3 variables with domain value = SPD.U_in (incl the ticks for the f_upper)
        3. There must be at least 3 variables with domain value = SPD.L_in (incl the ticks for the f_lower)
        """
        self.global_all_in = [SVC.U_on, SVC.U_in, SVC.M_in, SVC.L_in, SVC.L_on]  # , SVC.H_M_in
        self.global_count = ['OR', CountConstraint(SVC.U_in, '>=', 3)]
        self.global_series = ['OR',
                              [SVC.U_on, SVC.U_in, SVC.U_on],
                              [SVC.U_on, SVC.U_on, SVC.U_on]]

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_pct_bounds = [-0.02, -0.50]
        self.f_lower_pct_bounds = []  # not required
        self.f_upper_lower_relation_bounds = []
        self.f_regression_pct_bounds = self.f_upper_pct_bounds


class TKEUpConstraints(Constraints):
    def __fill_global_constraints__(self):
        """
        1. All values have to be in a range (channel)
        2. There must be at least 3 variables with domain value = SPD.U_in (incl the ticks for the f_upper)
        3. There must be at least 3 variables with domain value = SPD.L_in (incl the ticks for the f_lower)
        """
        self.global_all_in = [SVC.L_on, SVC.L_in, SVC.M_in, SVC.U_in, SVC.U_on, SVC.H_M_in]
        self.global_count = ['OR', CountConstraint(SVC.L_in, '>=', 3)]
        self.global_series = ['OR',
                              [SVC.L_on, SVC.L_in, SVC.L_on],
                              [SVC.L_on, SVC.L_on, SVC.L_on]]

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_pct_bounds = []  # not required
        self.f_lower_pct_bounds = [0.02, 0.50]
        self.f_upper_lower_relation_bounds = []
        self.f_regression_pct_bounds = self.f_lower_pct_bounds


class ChannelConstraints(Constraints):
    def __fill_global_constraints__(self):
        """
        1. All values have to be in a range (channel)
        2. There must be at least 3 variables with domain value = SPD.U_in (incl the ticks for the f_upper)
        3. There must be at least 3 variables with domain value = SPD.L_in (incl the ticks for the f_lower)
        """
        self.global_all_in = [SVC.L_on, SVC.L_in, SVC.M_in, SVC.U_in, SVC.U_on]
        self.global_count = ['OR',
                             CountConstraint(SVC.U_in, '>=', 3),
                             CountConstraint(SVC.L_in, '>=', 3)]
        self.global_series = ['OR',
                              [SVC.L_in, SVC.U_in, SVC.L_in, SVC.U_in, SVC.L_in],
                              [SVC.U_in, SVC.L_in, SVC.U_in, SVC.L_in, SVC.U_in],
                              [SVC.U_in, SVC.L_in, SVC.L_in, SVC.U_in, SVC.U_in],
                              [SVC.L_in, SVC.U_in, SVC.U_in, SVC.L_in, SVC.L_in]]

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_pct_bounds = [-0.02, 0.02]
        self.f_lower_pct_bounds = self.f_upper_pct_bounds
        self.f_upper_lower_relation_bounds = [-2, 2]
        self.f_regression_pct_bounds = [-0.10, 0.10]


class ChannelUpConstraints(ChannelConstraints):
    def __set_bounds_for_pattern_type__(self):
        self.f_upper_pct_bounds = [0.02, 0.50]
        self.f_lower_pct_bounds = self.f_upper_pct_bounds
        self.f_upper_lower_relation_bounds = [0.8, 1.2]
        self.f_regression_pct_bounds = [0.00, 0.50]


class ChannelDownConstraints(ChannelConstraints):
    def __set_bounds_for_pattern_type__(self):
        self.__set_bounds_by_complementary_constraints__(ChannelUpConstraints())
        self.f_regression_pct_bounds = [-0.50, 0.00]


class HeadShoulderConstraints(Constraints):
    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def __fill_global_constraints__(self):
        """
        1. All values have to be in a range (channel)
        2. There must be at least 3 variables with domain value = SPD.U_in (incl the ticks for the f_upper)
        3. There must be at least 3 variables with domain value = SPD.L_in (incl the ticks for the f_lower)
        """
        self.global_all_in = [SVC.L_on, SVC.L_in, SVC.M_in, SVC.U_in, SVC.U_on]
        self.global_count = ['AND',
                             CountConstraint(SVC.L_in, '>=', 4),
                             CountConstraint(SVC.U_in, '>=', 1)]
        self.global_series = ['OR',
                              [SVC.L_on, SVC.M_in, SVC.L_on, SVC.U_on, SVC.L_on, SVC.M_in, SVC.L_on],
                              [SVC.L_on, SVC.M_in, SVC.L_in, SVC.U_on, SVC.M_in, SVC.M_in, SVC.L_on]]

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_pct_bounds = [-0.03, 0.03]
        self.f_lower_pct_bounds = self.f_upper_pct_bounds
        self.f_upper_lower_relation_bounds = [0.8, 1.1]
        self.f_regression_pct_bounds = [-0.05, 0.05]


class InverseHeadShoulderConstraints(HeadShoulderConstraints):
    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def __fill_global_constraints__(self):
        """
        1. All values have to be in a range (channel)
        2. There must be at least 3 variables with domain value = SPD.U_in (incl the ticks for the f_upper)
        3. There must be at least 3 variables with domain value = SPD.L_in (incl the ticks for the f_lower)
        """
        self.global_all_in = [SVC.L_on, SVC.L_in, SVC.M_in, SVC.U_in, SVC.U_on]
        self.global_count = ['AND',
                             CountConstraint(SVC.U_in, '>=', 4),
                             CountConstraint(SVC.L_in, '>=', 1)]
        self.global_series = ['OR',
                              [SVC.U_on, SVC.M_in, SVC.U_on, SVC.L_on, SVC.U_on, SVC.M_in, SVC.U_on],
                              [SVC.U_on, SVC.M_in, SVC.U_in, SVC.L_on, SVC.M_in, SVC.M_in, SVC.U_on]]

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_pct_bounds = [-0.03, 0.03]
        self.f_lower_pct_bounds = self.f_upper_pct_bounds
        self.f_upper_lower_relation_bounds = [0.8, 1.1]
        self.f_regression_pct_bounds = [-0.05, 0.05]


class TriangleConstraints(Constraints):
    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def __fill_global_constraints__(self):
        """
        1. All values have to be in a range (channel)
        2. There must be at least 3 variables with domain value = SPD.U_in (incl the ticks for the f_upper)
        3. There must be at least 3 variables with domain value = SPD.L_in (incl the ticks for the f_lower)
        """
        self.global_all_in = [SVC.L_on, SVC.L_in, SVC.M_in, SVC.U_in, SVC.U_on]
        self.global_count = ['OR',
                             CountConstraint(SVC.U_in, '>=', 3),
                             CountConstraint(SVC.L_in, '>=', 3)]
        self.global_series = ['OR',
                              [SVC.L_in, SVC.U_in, SVC.L_in, SVC.U_in, SVC.L_in],
                              [SVC.U_in, SVC.L_in, SVC.U_in, SVC.L_in, SVC.U_in],
                              [SVC.L_in, SVC.L_in, SVC.U_in, SVC.U_in, SVC.L_in],
                              [SVC.U_in, SVC.U_in, SVC.L_in, SVC.L_in, SVC.U_in]]

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_pct_bounds = [-1.5, -0.01]
        self.f_lower_pct_bounds = [0.01, 1.5]
        self.f_upper_lower_relation_bounds = [-10, -0.2]
        self.f_regression_pct_bounds = [-0.5, 0.5]


class TriangleTopConstraints(TriangleConstraints):
    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_pct_bounds = [-0.01, 0.01]
        self.f_lower_pct_bounds = [0.02, 1.0]
        self.f_upper_lower_relation_bounds = []
        self.f_regression_pct_bounds = []


class TriangleBottomConstraints(TriangleConstraints):
    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def __set_bounds_for_pattern_type__(self):
        self.__set_bounds_by_complementary_constraints__(TriangleTopConstraints())
        self.f_regression_pct_bounds = []


class TriangleUpConstraints(TriangleConstraints):
    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_pct_bounds = [0.02, 5.00]
        self.f_lower_pct_bounds = self.f_upper_pct_bounds
        self.f_upper_lower_relation_bounds = [0.02, 0.65]
        self.f_regression_pct_bounds = self.f_upper_pct_bounds


class TriangleDownConstraints(TriangleConstraints):
    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def __set_bounds_for_pattern_type__(self):
        self.__set_bounds_by_complementary_constraints__(TriangleUpConstraints())
        self.f_regression_pct_bounds = self.f_upper_pct_bounds