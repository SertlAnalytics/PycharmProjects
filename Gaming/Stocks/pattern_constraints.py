"""
Description: This module contains the constraint classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
import pandas as pd
from sertl_analytics.constants.pattern_constants import CT, SVC, FT
from sertl_analytics.mymath import MyMath
from pattern_value_categorizer import ValueCategorizer


class ConstraintHelper:
    @staticmethod
    def get_constraints_details_as_dict():
        return_dict = {}
        constraints_dic = ConstraintHelper.get_constraints_as_dict()
        for key, constraints in constraints_dic.items():
            return_dict[key] = constraints.get_value_dict()
        return return_dict

    @staticmethod
    def get_constraints_as_dict():
        return_dict = {}
        for pattern_type in FT.get_all():
            return_dict[pattern_type] = ConstraintHelper.get_constraint_by_pattern_type(pattern_type)
        return return_dict

    @staticmethod
    def get_constraint_by_pattern_type(pattern_type: str):
        if pattern_type == FT.TRIANGLE:
            return TriangleConstraints()
        elif pattern_type == FT.TRIANGLE_TOP:
            return TriangleTopConstraints()
        elif pattern_type == FT.TRIANGLE_BOTTOM:
            return TriangleBottomConstraints()
        elif pattern_type == FT.TRIANGLE_UP:
            return TriangleUpConstraints()
        elif pattern_type == FT.TRIANGLE_DOWN:
            return TriangleDownConstraints()
        elif pattern_type == FT.CHANNEL:
            return ChannelConstraints()
        elif pattern_type == FT.CHANNEL_UP:
            return ChannelUpConstraints()
        elif pattern_type == FT.CHANNEL_DOWN:
            return ChannelDownConstraints()
        elif pattern_type == FT.TKE_UP:
            return TKEUpConstraints()
        elif pattern_type == FT.TKE_DOWN:
            return TKEDownConstraints()
        elif pattern_type == FT.HEAD_SHOULDER:
            return HeadShoulderConstraints()
        elif pattern_type == FT.HEAD_SHOULDER_INVERSE:
            return InverseHeadShoulderConstraints()
        return None


class CountConstraint:
    def __init__(self, value_category: str, comparison: str, value: float):
        self.value_category = value_category
        self.comparison = comparison
        self.comparison_value = value

    def get_count_constraints_details(self):
        return '{} {} {}'.format(self.value_category, self.comparison, self.comparison_value)

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
        self.f_upper_percentage_bounds = [-2.0, 2.0]
        self.f_lower_percentage_bounds = [-2.0, 2.0]
        self.height_end_start_relation_bounds = [0.1, 1.5]  # the relationship bounds for end and start heights
        self.f_regression_percentage_bounds = [-5.0, 5.0]  # this constraint checks the "direction" of the data
        self.breakout_required_after_ticks = self.__get_breakout_required_after_ticks__()
        self._fill_global_constraints__()
        self._set_bounds_for_pattern_type_()
        self._check_dic = {}

    def get_value_dict(self):
        return dict(tolerance_pct = self.tolerance_pct,
                    global_all_in = self.global_all_in,
                    global_count = self.__get_global_count_details__(),
                    global_series = self.global_series,
                    f_upper_percentage_bounds = self.f_upper_percentage_bounds,
                    f_lower_percentage_bounds = self.f_lower_percentage_bounds,
                    height_end_start_relation_bounds = self.height_end_start_relation_bounds,
                    f_regression_percentage_bounds = self.f_regression_percentage_bounds,
                    breakout_required_after_ticks = self.breakout_required_after_ticks)

    def __get_global_count_details__(self):
        return [value if index == 0 else value.get_count_constraints_details()
                for index, value in enumerate(self.global_count)]

    def are_f_lower_f_upper_percentage_compliant(self, f_lower_percentage: float, f_upper_percentage: float):
        if self.__is_f_lower_percentage_compliant__(f_lower_percentage):
            return self.__is_f_upper_percentage_compliant__(f_upper_percentage)
        return False

    def is_f_regression_percentage_compliant(self, f_reg_percentage: float):
        if len(self.f_regression_percentage_bounds) == 0:  # no bounds defined
            return True
        return self.f_regression_percentage_bounds[0] <= f_reg_percentage <= self.f_regression_percentage_bounds[1]

    @staticmethod
    def __get_breakout_required_after_ticks__():
        return 0

    def __is_f_lower_percentage_compliant__(self, f_lower_percentage: float):
        if len(self.f_lower_percentage_bounds) == 0:  # no lower bounds defined
            return True
        return self.f_lower_percentage_bounds[0] <= f_lower_percentage <= self.f_lower_percentage_bounds[1]

    def __is_f_upper_percentage_compliant__(self, f_upper_pct: float):
        if len(self.f_upper_percentage_bounds) == 0:  # no upper bounds defined
            return True
        return self.f_upper_percentage_bounds[0] <= f_upper_pct <= self.f_upper_percentage_bounds[1]

    def is_relation_height_end_start_compliant(self, height_end: float, height_start: float):
        if len(self.height_end_start_relation_bounds) == 0:  # no relation defined
            return True
        if height_start == 0:
            return False
        end_start_relation = MyMath.divide(height_end, height_start)
        return self.height_end_start_relation_bounds[0] <= end_start_relation <= self.height_end_start_relation_bounds[1]

    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def _set_bounds_for_pattern_type_(self):
        self.f_upper_percentage_bounds = [-100.0, 100]
        self.f_lower_percentage_bounds = self.f_upper_percentage_bounds
        self.height_end_start_relation_bounds = [0.1, 1.2]

    def get_unary_constraints(self, df: pd.DataFrame):
        pass

    def get_binary_constraints(self, df: pd.DataFrame):
        pass

    def _fill_global_constraints__(self):
        pass

    @property
    def f_upper_percentage_bounds_complementary(self):
        return [-1 * x for x in reversed(self.f_upper_percentage_bounds)]

    @property
    def f_lower_percentage_bounds_complementary(self):
        return [-1 * x for x in reversed(self.f_lower_percentage_bounds)]

    @property
    def height_end_start_relation_bounds_complementary(self):
        return self.height_end_start_relation_bounds

    def __set_bounds_by_complementary_constraints__(self, comp_constraints):
        self.f_upper_percentage_bounds = comp_constraints.f_lower_percentage_bounds_complementary
        self.f_lower_percentage_bounds = comp_constraints.f_upper_percentage_bounds_complementary
        self.height_end_start_relation_bounds = comp_constraints.height_end_start_relation_bounds_complementary

    def are_global_constraints_satisfied(self, value_categorizer: ValueCategorizer):
        self._check_dic[CT.ALL_IN] = self.__is_global_constraint_all_in_satisfied__(value_categorizer)
        self._check_dic[CT.COUNT] = self.__is_global_constraint_count_satisfied__(value_categorizer)
        self._check_dic[CT.SERIES] = self.__is_global_constraint_series_satisfied__(value_categorizer)
        return False if False in [self._check_dic[key] for key in self._check_dic] else True

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
    def _fill_global_constraints__(self):
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

    def _set_bounds_for_pattern_type_(self):
        self.f_upper_percentage_bounds = [-50.0, -2.0]
        self.f_lower_percentage_bounds = []  # not required
        self.height_end_start_relation_bounds = [0.1, 0.5]
        self.f_regression_percentage_bounds = self.f_upper_percentage_bounds


class TKEUpConstraints(Constraints):
    def _fill_global_constraints__(self):
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

    def _set_bounds_for_pattern_type_(self):
        self.f_upper_percentage_bounds = []  # not required
        self.f_lower_percentage_bounds = [2.0, 50.0]
        self.height_end_start_relation_bounds = [0.1, 0.5]
        self.f_regression_percentage_bounds = self.f_lower_percentage_bounds


class ChannelConstraints(Constraints):
    def _fill_global_constraints__(self):
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

    def _set_bounds_for_pattern_type_(self):
        self.f_upper_percentage_bounds = [-2.0, 2.0]
        self.f_lower_percentage_bounds = self.f_upper_percentage_bounds
        self.height_end_start_relation_bounds = [0.9, 1.1]
        self.f_regression_percentage_bounds = [-5.0, 5.0]


class ChannelUpConstraints(ChannelConstraints):
    def _set_bounds_for_pattern_type_(self):
        self.f_upper_percentage_bounds = [2.0, 50.0]
        self.f_lower_percentage_bounds = self.f_upper_percentage_bounds
        self.height_end_start_relation_bounds = [0.9, 1.1]
        self.f_regression_percentage_bounds = [0.00, 50.0]


class ChannelDownConstraints(ChannelConstraints):
    def _set_bounds_for_pattern_type_(self):
        self.__set_bounds_by_complementary_constraints__(ChannelUpConstraints())
        self.height_end_start_relation_bounds = [0.9, 1.1]
        self.f_regression_percentage_bounds = [-50.0, 0.00]


class HeadShoulderConstraints(Constraints):
    @staticmethod
    def __get_breakout_required_after_ticks__():
        return 5

    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def _fill_global_constraints__(self):
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

    def _set_bounds_for_pattern_type_(self):
        self.f_upper_percentage_bounds = [-2.0, 2.0]
        self.f_lower_percentage_bounds = self.f_upper_percentage_bounds
        self.height_end_start_relation_bounds = []
        self.f_regression_percentage_bounds = [-5.0, 5.0]


class InverseHeadShoulderConstraints(HeadShoulderConstraints):
    @staticmethod
    def __get_breakout_required_after_ticks__():
        return 5

    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def _fill_global_constraints__(self):
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

    def _set_bounds_for_pattern_type_(self):
        self.f_upper_percentage_bounds = [-2.0, 2.0]
        self.f_lower_percentage_bounds = self.f_upper_percentage_bounds
        self.height_end_start_relation_bounds = []
        self.f_regression_percentage_bounds = [-5.0, 5.0]


class TriangleConstraints(Constraints):
    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def _fill_global_constraints__(self):
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

    def _set_bounds_for_pattern_type_(self):
        self.f_upper_percentage_bounds = [-50.0, -1.0]
        self.f_lower_percentage_bounds = [2.0, 50.0]
        self.height_end_start_relation_bounds = [0.1, 0.5]
        self.f_regression_percentage_bounds = [-20.0, 20.0]


class TriangleTopConstraints(TriangleConstraints):
    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def _set_bounds_for_pattern_type_(self):
        self.f_upper_percentage_bounds = [-1.0, 1.0]
        self.f_lower_percentage_bounds = [2.0, 50.0]
        self.f_regression_percentage_bounds = []


class TriangleBottomConstraints(TriangleConstraints):
    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def _set_bounds_for_pattern_type_(self):
        self.__set_bounds_by_complementary_constraints__(TriangleTopConstraints())
        self.f_regression_percentage_bounds = []
        self.height_end_start_relation_bounds = [0.1, 0.5]


class TriangleUpConstraints(TriangleConstraints):
    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def _set_bounds_for_pattern_type_(self):
        self.f_upper_percentage_bounds = [2.0, 50.00]
        self.f_lower_percentage_bounds = self.f_upper_percentage_bounds
        self.f_regression_percentage_bounds = self.f_upper_percentage_bounds
        self.height_end_start_relation_bounds = [0.1, 0.5]


class TriangleDownConstraints(TriangleConstraints):
    @staticmethod
    def __get_tolerance_pct__():
        return 0.02

    def _set_bounds_for_pattern_type_(self):
        self.__set_bounds_by_complementary_constraints__(TriangleUpConstraints())
        self.f_regression_percentage_bounds = self.f_upper_percentage_bounds
        self.height_end_start_relation_bounds = [0.1, 0.5]
