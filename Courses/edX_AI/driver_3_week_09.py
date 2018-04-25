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
        # self.print_df_details()

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


class DomainController:
    def __init__(self, dic: dict, constraints: SudokuConstraints):
        self.constraints = constraints
        self.dic = {}
        self.init_dic(dic)

    def init_dic(self, dic: dict):
        for key in dic:
            self.dic[key] = list(dic[key])

    def is_assignment_complete(self):
        for variable in self.dic:
            if len(self.dic[variable]) > 1:
                return False
        return self.are_domains_consistent()  # this check has to be done after the first check

    def are_domains_consistent(self):
        for variable in self.dic:
            if len(self.dic[variable]) == 1:
                if not self.is_single_value_consistent(variable, self.dic[variable][0]):
                    return False
            else:
                multi_values_consistent = False
                for value in self.dic[variable]:
                    if self.is_single_value_consistent(variable, value):
                        multi_values_consistent = True
                        break
                if not multi_values_consistent:
                    return False
        return True

    def get_total_length(self):
        length = 0
        counter = 0
        for key in self.dic:
            counter = counter + 1
            length = length + len(self.dic[key])
        return length

    def remove_values_from_neighors(self):
        for variable in self.dic:
            if len(self.dic[variable]) == 1:
                self.remove_value_from_neighbors(variable)

    def remove_value_from_neighbors(self, variable: str):
        if len(self.dic[variable]) == 1:  # remove this value from the related variables
            value = self.dic[variable][0]
            df_neighbors = self.constraints.get_all_constraints_for_node(variable)
            for ind, rows in df_neighbors.iterrows():
                if rows['Constraint'] == 'NOT_EQUAL':
                    variable_node_2 = rows['Node_2']
                    domain_node_2 = self.dic[variable_node_2]
                    if value in domain_node_2 and len(self.dic[variable_node_2]) > 1:
                        domain_node_2.remove(value)
                        if len(domain_node_2) == 1:
                            self.remove_value_from_neighbors(variable_node_2)

    def get_unassigned_mrv_variable(self):
        for i in range(2, 10):
            for variable in self.dic:
                if len(self.dic[variable]) == i:
                    return variable

    def is_single_value_consistent(self, variable: str, value: int):
        df_neighbors = self.constraints.get_all_constraints_for_node(variable)
        for ind, rows in df_neighbors.iterrows():
            if rows['Constraint'] == 'NOT_EQUAL':
                domain_node_2 = self.dic[rows['Node_2']]
                if len(domain_node_2) == 1 and value == domain_node_2[0]:
                    return False
        return True


class SudokuBoard:
    def __init__(self, input_str):
        self.str = input_str
        self.np_array = self.get_array_from_str()
        self.sorted_variable_list = []
        self.init_sorted_variable_list()
        self.value_dic = {}
        self.domain_dic = {}
        self.init_value_dic()
        self.init_domain_dic()
        self.grids_dic = {}
        self.min_non_assigned_values_in_grid = 0  # will be updated in init_grids_dic
        self.grid_min_non_assigned_values_in_grid = ''
        self.init_variables_min_non_assigned_values_in_grid()
        self.init_grids_dic()
        # print(self.np_array)

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

    def init_sorted_variable_list(self):
        self.sorted_variable_list = []
        for ind_r, row_name in enumerate(SudokuHelper.ROWS):
            for ind_c, column_name in enumerate(SudokuHelper.COLUMNS):
                self.sorted_variable_list.append(row_name + column_name)

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
        return np_array.reshape(9, 9)

    def init_grids_dic(self):
        set_offs = [0, 3, 6]
        self.grids_dic = {}

        for r in range(self.np_array.shape[0]):
            self.grids_dic['R' + str(r + 1)] = SudokuGrid(self.np_array[r, :])

        for c in range(self.np_array.shape[1]):
            self.grids_dic['C' + str(c + 1)] = SudokuGrid(self.np_array[:, c])

        for ind_x, x in enumerate(set_offs):
            for ind_y, y in enumerate(set_offs):
                sub_array = self.np_array[x:x + 3, y:y + 3]
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
        self.sorted_variable_list = self.sudoku.sorted_variable_list
        self.value_dic = self.sudoku.value_dic
        self.domain_dic = self.sudoku.domain_dic
        self.constraints = SudokuConstraints()
        self.arc_queue = Queue()
        self.init_arc_queue()
        # print('len of arc_queue = {} - expected: 288 arcs'.format(self.arc_queue.size()))

    def get_sudoku_solution(self, write_results_to_new_array: bool):
        self.perform_ac3(write_results_to_new_array)
        domain_controller = DomainController(self.domain_dic, self.constraints)
        resolved_by_ac3 = domain_controller.is_assignment_complete()
        # resolved_by_ac3 = False
        if not resolved_by_ac3:
            resolved_by_bts = self.perform_bts(self.domain_dic, write_results_to_new_array)
        if not (resolved_by_ac3 or resolved_by_bts):
            return self.str + ' NOT RESOLVED BY AC3 AND BTS'
        assignment = self.get_assignment()
        if resolved_by_ac3:
            return assignment + ' AC3'
        else:
            return assignment + ' BTS'

    def write_solution_to_output_file(self, output_file: str):
        with open(output_file, 'w') as file_obj:
            file_obj.write(self.get_sudoku_solution(False))

    def get_assignment(self):
        assignment = ''
        for sorted_variable in self.sorted_variable_list:
            assignment = assignment + str(self.domain_dic[sorted_variable][0])
        return assignment

    """
    function Backtracking Algorithm (BTS)

    function BACKTRACKING_SEARCH(csp) returns a solution, or failure
        return BACKTRACK({}, csp)

    function BACKTRACK(assigment, csp): returns a solution, or failure
        if assignment is complete then return assignment
        var = SELECT_UNASSIGNED_VARIABLES(csp)
        for each value in ORDER_DOMAIN_VALUES(var, assignment, csp)
            if value is consistent with assignment then
                add {var = value} to assignment  & forward checking to reduce variables domains
                result = BACKTRACK(assignment, csp)
                if result != failure then return result
                remove {var = value} from assignment
        return failure
    """

    def perform_bts(self, domain_dic: dict,
                    write_results_to_new_array: bool = False):  # QUEUE: FIRST IN FIRST OUT (FIFO)
        domain_controller = DomainController(domain_dic, self.constraints)
        # domain_controller.remove_values_from_neighors()
        if domain_controller.is_assignment_complete():
            for variables in domain_controller.dic:
                self.domain_dic[variables] = domain_controller.dic[variables]
            if write_results_to_new_array:
                self.write_results_to_new_array()
            return True

        unassigned_mrv_variable = domain_controller.get_unassigned_mrv_variable()
        for value in domain_controller.dic[unassigned_mrv_variable]:
            if domain_controller.is_single_value_consistent(unassigned_mrv_variable, value):
                domain_controller_old = DomainController(domain_controller.dic, self.constraints)
                domain_controller.dic[unassigned_mrv_variable] = [value]
                domain_controller.remove_value_from_neighbors(unassigned_mrv_variable)
                if domain_controller.are_domains_consistent():
                    # self.print_current_state(unassigned_mrv_variable, value, domain_controller_old, domain_controller)
                    next_call_result = self.perform_bts(domain_controller.dic, write_results_to_new_array)
                    if next_call_result:
                        return True
                domain_controller = DomainController(domain_controller_old.dic, self.constraints)
        return False

    def print_current_state(self, variable: str, value: int, domain_controller_old: DomainController,
                            domain_controller: DomainController):
        print('Variable = {}, Domain = {}, Value = {}, len.Controller = {}, '
              'Domain_after_change = {}, len.Controller_after_change = {}'.format(
            variable, domain_controller_old.dic[variable], value, domain_controller_old.get_total_length(),
            domain_controller.dic[variable], domain_controller.get_total_length()))

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
# 059030100000000800000800032020000000900000580360007004090780005000050010002003700


test = False

if test:
    solver = Solver('000001000020000008691200000000000014102506003800020506005000000730000000006319405')
    print(solver.get_sudoku_solution(False))
elif len(sys.argv) > 1:  # started from command prompt
    input_str = sys.argv[1].upper()
    solver = Solver(input_str)
    solver.write_solution_to_output_file('output.txt')
else:
    df = pd.read_csv('sudoku_start.txt', header=None)
    df.columns = ['C1']
    for ind, rows in df.iterrows():
        solver = Solver(rows['C1'])
        # print('{} INPUT for line {}:'.format(solver.str, ind))
        print(solver.get_sudoku_solution(False))
        if ind > 20:
            break








