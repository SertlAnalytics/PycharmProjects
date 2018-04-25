# ColumbiaX: course-v1:ColumbiaX+CSMM.101x+1T2018 - Assigment week 9
# Week 9 Project: Constraint Satisfaction Problems - 2018-04-09
# Sudoku
# Copyright Josef Sertl (https://www.sertl-analytics.com)
# $ python3 problem2_3.py input2.csv output2.csv
# CAUTION: Please remove all plotting - will raise an error within the workbench on vocareum

import numpy as np
import pandas as pd
import sys


class SudokuHelper:
    ROWS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    COLUMNS = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    GRID_SET_OFFS = [0, 3, 6]
    n_rows = len(ROWS)
    n_columns = len(COLUMNS)

    def add_to_constraint_list(self, constraint_list: list, entry_list: list):
        len_entry_list = len(entry_list)
        for ind_1 in range(len_entry_list - 1):
            for ind_2 in range(ind_1 + 1, len_entry_list):
                new_entry_list = [[entry_list[ind_1], entry_list[ind_2], 'NOT_EQUAL'],
                              [entry_list[ind_2], entry_list[ind_1], 'NOT_EQUAL']]
                for entries in new_entry_list:
                    if not entries in constraint_list:
                        constraint_list.append(entries)

    def get_binary_constraint_list(self):
        constraint_list = []
        # add row constraints to the list
        for ind_r in range(self.n_rows):
            entry_list = []
            for ind_c in range(self.n_columns):
                entry_list.append(self.ROWS[ind_r] + self.COLUMNS[ind_c])
            self.add_to_constraint_list(constraint_list, entry_list)

        # add column constraints to the list
        for ind_c in range(self.n_columns):
            entry_list = []
            for ind_r in range(self.n_rows):
                entry_list.append(self.ROWS[ind_r] + self.COLUMNS[ind_c])
            self.add_to_constraint_list(constraint_list, entry_list)

        # add grid constraints to the list
        for off_set_r in self.GRID_SET_OFFS:
            for off_set_c in self.GRID_SET_OFFS:
                entry_list = []
                for ind_r in range(off_set_r, off_set_r + 3):
                    for ind_c in range(off_set_c, off_set_c + 3):
                        entry_list.append(self.ROWS[ind_r] + self.COLUMNS[ind_c])
                self.add_to_constraint_list(constraint_list, entry_list)
        return constraint_list


class Queue:  # First in - first out FIFO
    def __init__(self):
        self.items = []

    @property
    def is_empty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def is_element(self, item):
        return item in self.items

    def size(self):
        return len(self.items)


class SudokuConstraints:
    def __init__(self):
        self.df = self.get_data_frame()
        self.print_df_details()

    def print_df_details(self):
        print(self.df.info())
        print(self.df.head())

    @staticmethod
    def get_data_frame():
        df = pd.DataFrame(SudokuHelper().get_binary_constraint_list())
        df.columns = ['Node_1', 'Node_2', 'Constraint']
        return df

    def get_all_constraints_for_node(self, node: str):
        df = self.df[self.df.Node_1 == node]
        # print('constraints for node {}\n{}'.format(node, df))
        return df

    def get_all_constraints_for_nodes(self, node_1: str, node_2: str):
        df = self.df[np.logical_and(self.df.Node_1 == node_1, self.df.Node_2 == node_2)]
        # print('constraints for node {} and {}\n{}'.format(node_1, node_2, df))
        return df


class SudokuBoard:
    def __init__(self, input_str):
        self.str = input_str
        self.np_array = self.get_array_from_str()
        self.value_dic = {}
        self.domain_dic = {}
        self.init_value_dic()
        self.init_domain_dic()
        self.grids_dic = {}
        self.min_non_assigned_values_in_grid = 0  # will be updated in init_grids_dic
        self.grid_min_non_assigned_values_in_grid = ''
        self.init_variables_min_non_assigned_values_in_grid()
        self.init_grids_dic()
        # self.print_details()

    def init_variables_min_non_assigned_values_in_grid(self):
        self.min_non_assigned_values_in_grid = 10  # default
        for grid_key in self.grids_dic:
            new_number = self.grids_dic[grid_key].not_assigned
            if new_number < self.min_non_assigned_values_in_grid:
                self.min_non_assigned_values_in_grid = new_number
                self.grid_min_non_assigned_values_in_grid = grid_key

    def print_details(self):
        print(self.np_array)
        print(self.value_dic)
        print(self.domain_dic)
        self.print_number_unassigned()

    def init_value_dic(self):
        self.value_dic = {}
        for ind_r, row_name in enumerate(SudokuHelper.ROWS):
            for ind_c, column_name in enumerate(SudokuHelper.COLUMNS):
                self.value_dic[row_name + column_name] = self.np_array[ind_r, ind_c]

    def init_domain_dic(self):
        self.domain_dic = {}
        for ind_r, row_name in enumerate(SudokuHelper.ROWS):
            for ind_c, column_name in enumerate(SudokuHelper.COLUMNS):
                if self.np_array[ind_r, ind_c] == 0:
                    self.domain_dic[row_name + column_name] = [i for i in range(1, 10)]
                else:
                    self.domain_dic[row_name + column_name] = [self.np_array[ind_r, ind_c]]

    def print_number_unassigned(self):
        for grid_key in self.grids_dic:
            print('self.grids_dic[{}].not_assigned: {}'.format(grid_key, self.grids_dic[grid_key].not_assigned))

    def get_array_from_str(self):
        np_array = np.array(list(self.str), dtype=int)
        return np_array.reshape(9,9)

    def init_grids_dic(self):
        set_offs = [0, 3, 6]
        self.grids_dic = {}

        for r in range(self.np_array.shape[0]):
            self.grids_dic['R' + str(r+1)] = SudokuGrid(self.np_array[r, :])

        for c in range(self.np_array.shape[1]):
            self.grids_dic['C' + str(c + 1)] = SudokuGrid(self.np_array[:, c])

        for ind_x, x in enumerate(set_offs):
            for ind_y, y in enumerate(set_offs):
                sub_array = self.np_array[x:x+3, y:y+3]
                self.grids_dic['Q' + str(ind_x + 1) + str(ind_y + 1)] = SudokuGrid(sub_array)

    def clone(self):
        return SudokuBoard(*self.str)

    # def is_identical(self, board_compare):
    #     return self.arg_str == board_compare.arg_str


class SudokuGrid:
    def __init__(self, input_array: np.array):
        self.np_array = input_array.reshape(1, 9)

    @property
    def not_assigned(self):
        return self.np_array.size - np.count_nonzero(self.np_array)


class Solver:
    def __init__(self, input_str: str):
        self.str = input_str
        self.sudoku = SudokuBoard(self.str)
        self.value_dic = self.sudoku.value_dic
        self.domain_dic = self.sudoku.domain_dic
        self.constraints = SudokuConstraints()
        self.arc_queue = Queue()
        self.init_arc_queue()
        # print('len of arc_queue = {} - expected: 288 arcs'.format(self.arc_queue.size()))

    """
    function AC-3(csp)
    returns False if an inconsistence is found. True otherwise
    inputs: csp, a binary CSP with components (X, D, C)
    local variables: queue, a queue of arcs, initially all the arcs in csp

    while queue is not empty do
        (Xi, Xj) = REMOVE-FIRST(queue)
        if Revise(csp, Xi, Xj) then
            if size of Di = 0 then return False
            for each Xk in Xi NEIGHBORS - {Xj} do 
                add (Xk, Xi) to queue
    return true
    """
    def perform_ac3(self, write_results_to_new_array: bool = False):  # QUEUE: FIRST IN FIRST OUT (FIFO)
        while not self.arc_queue.is_empty:
            queue_entry = self.arc_queue.dequeue()
            if self.revise(queue_entry[0], queue_entry[1]):
                if len(self.domain_dic[queue_entry[0]]) == 0:
                    return False
                else:
                    self.add_neighbors_to_arc_queue(queue_entry[0], queue_entry[1], 2)
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
        for ind_r in range(SudokuHelper.n_rows):
            for ind_c in range(SudokuHelper.n_columns):
                self.add_neighbors_to_arc_queue(SudokuHelper.ROWS[ind_r] + SudokuHelper.COLUMNS[ind_c])

    def add_neighbors_to_arc_queue(self, node: str, node_to_skip: str = '', position: int = 1):
        neighbors = self.get_node_neighbors(node)
        for neighbor in neighbors:
            if neighbor != node_to_skip:
                if position == 1:
                    new_entry = [node, neighbor]
                else:
                    new_entry = [neighbor, node]
                if not self.arc_queue.is_element(new_entry):
                    self.arc_queue.enqueue(new_entry)

    def get_node_neighbors(self, node: str):
        neighbors = []
        fd_neighbors = self.constraints.get_all_constraints_for_node(node)
        for ind, row in fd_neighbors.iterrows():
            neighbor = row['Node_2']
            if not neighbor in neighbors:
                neighbors.append(neighbor)
        return neighbors

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
# AC3
# '000001000020000008691200000000000014102506003800020506005000000730000000006319405'
# '000260701680070090190004500820100040004602900050003028009300074040050036703018000'

# BTS
# 000000000302540000050301070000000004409006005023054790000000050700810000080060009

test = True
if test:
    test_str = '000001000020000008691200000000000014102506003800020506005000000730000000006319405'
elif len(sys.argv)> 1:  # started from command prompt
    test_str = sys.argv[1].upper()
else:
    test_str = '000260701680070090190004500820100040004602900050003028009300074040050036703018000'

solver = Solver(test_str)
# df = solver.constraints.get_all_constraints_for_node('H3')
# print(df)
print('Original:\n{}'.format(solver.sudoku.np_array))
solver.perform_ac3(True)
solver.write_not_assignable_domain_entries()


