"""
Description: This module detects pattern from any kind of input stream.
In the first version we concentrate our target on identifying stock pattern by given formation types.
In the second version we allow the system to find own patterns or change existing pattern constraints.
The main algorithm is CSP (constraint satisfaction problems) with binary constraints.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sertl_analytics.environment  # init some environment variables during load - for security reasons
import seaborn as sns
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, ApiPeriod, ApiOutputsize
import stock_database
from stock_database import StockSymbols
from mpl_finance import candlestick_ohlc
import matplotlib.dates as dt
from matplotlib.patches import Circle, Wedge, Polygon, Rectangle, Arrow
from matplotlib.collections import PatchCollection
from datetime import datetime, timedelta
import ftplib
import tempfile
from sertl_analytics.datafetcher.database_fetcher import BaseDatabase, DatabaseDataFrame
import stock_database as sdb
from sertl_analytics.searches.smart_searches import Queue, Stack
from sertl_analytics.functions import math_functions
import math

"""
Implementation steps:
1. Define a framework for CSPs: Unary, Binary, Global, Preferences
2. The solver should be domain independent (i.e. it doesn't matter to check stock markets or health data...)
3. Node consistency, Arc-consistency, Path consistency.
Recall:
a) A constraint satisfaction problem consists of three components:
a.1) A set of variables X = {X1, X2, ..., Xn}
a.2) A set of domains for each variable: D = {D1, D2, ..., Dn)
a.3) A set of constraints C that specifies allowable combinations of values
b) Solving the CSP: Finding the assignment(s) that satisfy all constraints.
c) Concepts: problem formulation, backtracking search, arc consistence, etc
d) We call a solution a consistent assignment
e) Factored representation: Each state has some attribute-value properties, e.g. GPS location (properties = features)
"""


class CN:  # Column Names
    OPEN = 'Open'
    HIGH = 'High'
    LOW = 'Low'
    CLOSE = 'Close'
    MEAN_HL = 'MeanHL'
    VOL = 'Volume'
    DATE = 'Date'
    DATEASNUM = 'DateAsNumber'
    POSITION = 'Position'
    TICKS_BREAK_HIGH_BEFORE = 'BREAK_HIGH_BEFORE'
    TICKS_BREAK_HIGH_AFTER = 'BREAK_HIGH_AFTER'
    TICKS_BREAK_LOW_BEFORE = 'BREAK_LOW_BEFORE'
    TICKS_BREAK_LOW_AFTER = 'BREAK_LOW_AFTER'
    GLOBAL_MIN = 'G_MIN'
    GLOBAL_MAX = 'G_MAX'
    LOCAL_MIN = 'L_MIN'
    LOCAL_MAX = 'L_MAX'
    F_UPPER = 'F_UPPER'
    F_LOWER = 'F_LOWER'
    DOMAIN_VALUE = 'Domain_Value'
    VALUE_CATEGORY = 'Value_Category'


class ValueCategories:
    pass


class SVC(ValueCategories):  # Stock value categories:
    U_out = 'Upper_out'
    U_in = 'Upper_in'
    U_on = 'Upper_on'
    M_in = 'Middle_in'
    L_in = 'Low_in'
    L_on = 'Low_on'
    L_out = 'Low_out'


class CT:  # Constraint types
    ALL_IN = 'All_In'
    COUNT = 'Count'
    SERIES = 'Series'

class CountConstraint:
    def __init__(self, value_category: ValueCategories, comparison: str, value: float):
        self.value_category = value_category
        self.comparison = comparison
        self.comparison_value = value

    def is_value_satisfying_constraint(self, value: float):
        if self.comparison == '=':
            return self.comparison_value == value
        if self.comparison == '<=':
            return self.comparison_value <= value
        if self.comparison == '<':
            return self.comparison_value < value
        if self.comparison == '>=':
            return self.comparison_value >= value
        if self.comparison == '>':
            return self.comparison_value > value


class Constraints:
    def __init__(self):
        self.global_all_in = []
        self.global_count = []
        self.global_series = []
        self.__fill_global_constraints__()

    def get_unary_constraints(self, df: pd.DataFrame):
        pass

    def get_binary_constraints(self, df: pd.DataFrame):
        pass

    def __fill_global_constraints__(self):
        pass

class ChannelConstraints(Constraints):
    def __fill_global_constraints__(self):
        """
        1. All values have to be in a range (channel)
        2. There must be at least 3 variables with domain value = SPD.U_in (incl the ticks for the f_upper)
        3. There must be at least 3 variables with domain value = SPD.L_in (incl the ticks for the f_lower)
        """
        self.global_all_in = [SVC.L_in, SVC.M_in, SVC.U_in]
        self.global_count = ['AND', CountConstraint(SVC.U_in, '>=', 3), CountConstraint(SVC.L_in, '>=', 3)]
        self.global_series = ['OR', [SVC.L_in, SVC.U_in, SVC.L_in, SVC.U_in, SVC.L_in],
                          [SVC.U_in, SVC.L_in, SVC.U_in, SVC.L_in, SVC.L_in]]


class ValueCategorizer:
    def __init__(self, df: pd.DataFrame, accuracy_pct: float, f_upper, f_lower = None):
        self.df = df
        self.__accuracy_ptc = accuracy_pct
        self.__accuracy_ptc_equal = 0.001
        self.__f_upper = f_upper
        self.__f_lower = f_lower
        self.df[CN.F_UPPER] = self.df[CN.POSITION].apply(self.__f_upper)
        self.df[CN.F_LOWER] = self.df[CN.POSITION].apply(self.__f_lower)
        self.__add_value_category_to_df__()
        self.__available_value_category_list = list(self.df[CN.VALUE_CATEGORY].unique())

    def are_value_categories_available(self, category_list: list) -> bool:
        intersection = list(set(category_list) & set(self.__available_value_category_list))
        return len(intersection) != 0

    def get_number_of_rows_with_value_categories(self, category_list: list) -> bool:
        counter = 0
        for categories in category_list:
            df_cat = self.df[self.df[CN.VALUE_CATEGORY] == categories]
            counter += df_cat.shape[0]
        return counter

    def __add_value_category_to_df__(self):
        for ind, row in self.df.iterrows():
            row[CN.VALUE_CATEGORY] = self.__get_value_category_for_df_row__(row)

    def __get_value_category_for_df_row__(self, row) -> list:
        pass

    def __is_row_value_in_f_upper_range__(self, row):
        return abs(row[CN.CLOSE] - row[CN.F_UPPER])/np.mean([row[CN.CLOSE], row[CN.F_UPPER]]) <= self.__accuracy_ptc

    def __is_row_value_in_f_lower_range__(self, row):
        return abs(row[CN.CLOSE] - row[CN.F_LOWER]) / np.mean([row[CN.CLOSE], row[CN.F_LOWER]]) <= self.__accuracy_ptc

    def __is_row_value_between_f_lower_f_upper__(self, row):
        return row[CN.F_LOWER] < row[CN.CLOSE] < row[CN.F_UPPER]

    def __is_row_value_equal_f_upper__(self, row):
        return abs(row[CN.HIGH] - row[CN.F_UPPER]) / np.mean([row[CN.HIGH], row[CN.F_UPPER]]) <= self.__accuracy_ptc_equal

    def __is_row_value_larger_f_upper__(self, row):
        return row[CN.CLOSE] > row[CN.F_UPPER]

    def __is_row_value_smaller_f_upper__(self, row):
        return row[CN.CLOSE] < row[CN.F_UPPER]

    def __is_row_value_equal_f_lower__(self, row):
        return abs(row[CN.LOW] - row[CN.F_LOWER]) / np.mean([row[CN.LOW], row[CN.F_LOWER]]) <= self.__accuracy_ptc_equal

    def __is_row_value_larger_f_lower__(self, row):
        return row[CN.CLOSE] > row[CN.F_LOWER]

    def __is_row_value_smaller_f_lower__(self, row):
        return row[CN.CLOSE] < row[CN.F_LOWER]


class ChannelValueCategorizer(ValueCategorizer):
    def __get_value_category_for_df_row__(self, row):  # the series is important
        if self.__is_row_value_equal_f_upper__(row):
            return SVC.U_on
        elif self.__is_row_value_in_f_upper_range__(row):
            return SVC.U_in
        elif self.__is_row_value_larger_f_upper__(row):
            return SVC.U_out
        elif self.__is_row_value_equal_f_lower__(row):
            return SVC.L_on
        elif self.__is_row_value_in_f_lower_range__(row):
            return SVC.L_in
        elif self.__is_row_value_between_f_lower_f_upper__(row):
            return SVC.M_in
        elif self.__is_row_value_smaller_f_lower__(row):
            return SVC.L_out


class SeriesConstraintSolver:
    def __init__(self, conjunction: str, constraint_list: list, df: pd.DataFrame):
        self.conjunction = conjunction
        self.constraint_list = constraint_list
        self.df = self.channel.df
        self.df_length = self.df.shape[0]

        self.assignment = []
        self.arc_queue = Queue()
        self.init_arc_queue()

    def perform_ac3(self, write_results_to_new_array: bool = False):  # QUEUE: FIRST IN FIRST OUT (FIFO)
        while not self.arc_queue.is_empty:
            queue_entry = self.arc_queue.dequeue()
            if self.revise(queue_entry):
                if len(self.domain_dic[queue_entry[0]]) == 0:
                    return False
                else:
                    self.add_neighbors_to_arc_queue(queue_entry)
        if write_results_to_new_array:
            self.write_results_to_new_array()
        return True

    def write_not_assignable_domain_entries(self):
        print('Not assignable entries:\n')
        for key in self.domain_dic:
            if len(self.domain_dic[key]) > 1:
                print('{}: {}'.format(key, self.domain_dic[key]))

    def write_results_to_new_array(self):
        np_result = np.array(self.sudoku.np_array)
        for key in self.domain_dic:
            if len(self.domain_dic[key]) == 1:
                value = self.domain_dic[key][0]
                ind_r = SudokuHelper.ROWS.index(key[0])
                ind_c = SudokuHelper.COLUMNS.index(key[1])
                np_result[ind_r, ind_c] = value
        print('Result:\n{}'.format(np_result))

    def init_arc_queue(self):
        self.arc_queue.enqueue(self.channel.df[0])

    def add_neighbors_to_arc_queue(self, row):
        if row[CN.POSITION] + 1 < self.df_length:
            self.arc_queue.enqueue(self.channel.df[row[CN.POSITION] + 1])

    def revise(self, node_i: str, node_j: str):
        revised = False
        domain_i = self.sudoku.domain_dic[node_i]
        domain_j = self.sudoku.domain_dic[node_j]
        df_ij = self.constraints.get_all_constraints_for_nodes(node_i, node_j)
        for ind, rows in df_ij.iterrows():
            if rows['Constraint'] == 'NOT_EQUAL':
                for x in domain_i:
                    constraint_satisfied = False
                    for y in domain_j:
                        if x != y:
                            constraint_satisfied = True
                            break
                    if not constraint_satisfied:
                        domain_i.remove(x)
                        revised = True
        return revised


class PatternCheck:
    def __init__(self, df: pd.DataFrame, accuracy_pct: float):
        self.df = df
        self.accuracy_pct = accuracy_pct
        self.df_length = self.df.shape[0]
        self.pattern_dic = {'Channel': 6, 'TKE': 5}
        self.constraints = None

    def parse_for_pattern(self):
        for pattern_key in self.pattern_dic:
            if pattern_key == 'Channel':
                self.constraints = ChannelConstraints()
                for i in range(0, self.df_length - self.pattern_dic[pattern_key]):
                    for k in range(i + self.pattern_dic[pattern_key], self.df_length):
                        is_check_ok = self.check_tick_range(self.df.iloc[i:k])

    def check_tick_range(self, df_check: pd.DataFrame):
        left_tick = df_check.iloc[0]
        left_pos = left_tick[CN.POSITION]
        right_tick = df_check.iloc[-1]
        right_pos = right_tick[CN.POSITION]
        f_upper = math_functions.get_function_parameters(left_pos, left_tick[CN.HIGH], right_pos, right_tick[CN.HIGH])
        f_lower = math_functions.get_function_parameters(left_pos, left_tick[CN.LOW], right_pos, right_tick[CN.LOW])
        value_categorizer = ChannelValueCategorizer(self.df, self.accuracy_pct, f_upper, f_lower)
        if self.__is_global_constraint_all_in_satisfied__(df_check, value_categorizer):
            if self.__is_global_constraint_count_satisfied__(value_categorizer):
                if self._is_global_constraint_series_satisfied__(df_check, value_categorizer):
                    return True
        return False

    def __is_global_constraint_all_in_satisfied__(self, df_check: pd.DataFrame, value_categorizer):
        if len(self.constraints.global_all_in) == 0:
            return True
        number_correct = value_categorizer.get_number_of_rows_with_value_categories(self.constraints.global_all_in)
        return number_correct == df_check.shape[0]

    def __is_global_constraint_count_satisfied__(self, value_categorizer):
        if len(self.constraints.global_count) == 0:
            return True
        conjunction = self.constraints.global_count[0]
        for k in range(1, len(self.constraints.global_count)):
            count_constraint = self.constraints.global_count[k]
            number = value_categorizer.get_number_of_rows_with_value_categories(count_constraint.value_category)
            bool_value = count_constraint.is_value_satisfying_constraint(number)
            if bool_value and conjunction == 'OR':
                return True
            elif not bool_value and conjunction == 'AND':
                return False
        return False

    def __is_global_constraint_series_satisfied__(self, df_check: pd.DataFrame, value_categorizer):
        if len(self.constraints.global_series) == 0:
            return True
        conjunction = self.constraints.global_series[0]
        for k in range(1, len(self.constraints.global_series)):
            series = self.constraints.global_count[k]

            number = value_categorizer.get_number_of_rows_with_value_categories(count_constraint.value_category)
            bool_value = count_constraint.is_value_satisfying_constraint(number)
            if bool_value and conjunction == 'OR':
                return True
            elif not bool_value and conjunction == 'AND':
                return False
        return False