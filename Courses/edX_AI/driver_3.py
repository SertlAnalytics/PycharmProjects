# ColumbiaX: CSMM.101x - Assigment week 2
# Search algorithms - 2018-02-01
# Copyright Josef Sertl

import math
import time
import os
import sys
import psutil
import random
import ast
from typing import Union


class SwitchDirection:  # Series UDLR
    UP = 'Up'
    DOWN = 'Down'    
    LEFT = 'Left'
    RIGHT = 'Right'
    NONE = 'None'   


class SwitchDirectionList:
    LIST = [SwitchDirection.UP, SwitchDirection.DOWN, SwitchDirection.LEFT, SwitchDirection.RIGHT]


class Stack:  # Last in - first out LIFO

    def __init__(self):
        self.items = []

    @property
    def is_empty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def pop_pos(self, pos: int):
        return self.items.pop(pos)

    def peek(self):
        return self.items[len(self.items)-1]

    def size(self):
        return len(self.items)


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


class Board:
    def __init__(self, *inputargs):
        self.items = list(inputargs)
        self.dim = int(math.sqrt(len(self.items)))
        self.level_in_search_tree = 0
        self.cost_function_costs = 0  # default - will be overwritten when a heuristic function is used
        self.parent_board = None
        self.direction_from_parent = SwitchDirection.NONE
        self.__arg_str = ''  # contains the arg parameters as delimited string (del = "-") to speed up some lists/sets
        self.set_arg_str()

    @property
    def arg_str(self):
        return self.__arg_str

    def set_arg_str(self):
        for p in self.items:
            if self.items.index(p) == 0:
                self.__arg_str = str(p)
            else:
                self.__arg_str += '-' + str(p)

    @property
    def index_zero(self):
        return self.items.index(0)

    def switch_zero(self, index_zero_new: int):
        index_zero_new_value = self.items[index_zero_new]
        self.items[self.index_zero] = index_zero_new_value
        self.items[index_zero_new] = 0
        self.set_arg_str()

    def get_matrix(self):
        matrix = []
        row = []
        for i in range(0, len(self.items)):
            row.append(self.items[i])
            if (i + 1) % self.dim == 0:
                matrix.append(row)
                row = []
        return matrix

    def print_matrix(self, header):
        matrix = self.get_matrix()
        if header is not None:
            print(header)
        for row in matrix:
            print(row)

    def clone(self):
        return Board(*self.items)

    def is_identical(self, board_compare):
        return self.arg_str == board_compare.arg_str


class BoardTree:

    def __init__(self, initial_board: Board, goal_board: Board):
        self.board_helper = BoardHelper(len(initial_board.items))
        self.initial_board = initial_board
        self.goal_board = goal_board
        self.explored_arg_set = {''} # set which contains the already explored nodes
        self.frontier_arg_set = {''} # set which contains the nodes currently in the frontier
        self.frontier = None  # will contain either a Queue or a Stack
        self.success_board = None
        self.success_path = []
        self.nodes_expanded = 0
        self.max_search_depth = 0
        self.time_lastCheck = time.time()

    def is_board_explored(self, board: Board):
        return board.arg_str in self.explored_arg_set

    def is_board_in_frontier(self, board: Board):
        return board.arg_str in self.frontier_arg_set

    def add_to_explored(self, board: Board):
        if not self.is_board_explored(board):
            self.explored_arg_set.add(board.arg_str)

    def add_to_frontier(self, board: Board):
        if not self.is_board_in_frontier(board):
            self.frontier_arg_set.add(board.arg_str)
            if isinstance(self.frontier, Queue):
                self.frontier.enqueue(board)
            else:  # Stack
                self.frontier.push(board)

    def get_next_board_from_frontier(self, *argv) -> Board:
        if isinstance(self.frontier, Queue):
            board = self.frontier.dequeue()
        else:  # Stack
            if argv[0] is None:
                board = self.frontier.pop()
            else:
                board = self.frontier.pop_pos(argv[0])
        self.add_to_explored(board)
        self.frontier_arg_set.remove(board.arg_str)
        return board

    def get_child_board_list(self, frontier_board: Board, udlr_reversed: bool):
        child_board_list = self.board_helper.get_child_boards(frontier_board, udlr_reversed)
        self.nodes_expanded += 1
        self.check_progress(self.frontier)
        if self.max_search_depth < frontier_board.level_in_search_tree:
            self.max_search_depth = frontier_board.level_in_search_tree + 1
        return child_board_list

    def check_progress(self, frontier):
        # return
        if self.nodes_expanded % 10000 == 0:
            print('self.nodes_expanded: {0} - second spent {1:3.2f} - len(frontier): {2} '
                  ' -  len(done_args_strs) = {3} - len(frontier_args) = {4}'.
                  format(self.nodes_expanded,
                         time.time() - self.time_lastCheck,
                         frontier.size(),
                         len(self.explored_arg_set),
                         len(self.frontier_arg_set)))
            self.time_lastCheck = time.time()

    def handle_success(self, frontier_board: Board):
        print('BOARD is identical to GOAL')
        self.success_board = frontier_board
        self.success_path = self.get_success_path()

    def perform_bfs(self, input_board: Board):  # QUEUE: FIRST IN FIRST OUT (FIFO)
        self.frontier = Queue()
        self.add_to_frontier(input_board)

        while not self.frontier.is_empty:
            frontier_board = self.get_next_board_from_frontier(None)

            if frontier_board.is_identical(self.goal_board):
                self.handle_success(frontier_board)
                return

            child_board_list = self.get_child_board_list(frontier_board, False)
                            
            for child_board in child_board_list:
                if not self.is_board_explored(child_board) and not self.is_board_in_frontier(child_board):
                    self.add_to_frontier(child_board)

    def perform_dfs(self, input_board: Board):  # STACK: LAST IN FIRST OUT (LIFO)
        self.frontier = Stack()
        self.add_to_frontier(input_board)

        while not self.frontier.is_empty:
            frontier_board = self.get_next_board_from_frontier(None)

            if frontier_board.is_identical(self.goal_board):
                self.handle_success(frontier_board)
                return

            child_board_list = self.get_child_board_list(frontier_board, True)

            for child_board in child_board_list:
                if not self.is_board_explored(child_board) and not self.is_board_in_frontier(child_board):
                    self.add_to_frontier(child_board)

    def perform_ast(self, input_board: Board):
        self.frontier = Stack()
        self.add_to_frontier(input_board)

        while not self.frontier.is_empty:
            frontier_board = self.get_next_board_from_frontier(self.get_frontier_index_with_minimal_cost(self.frontier))
            self.board_helper.calculate_cost_function_for_board(frontier_board)

            if frontier_board.is_identical(self.goal_board):
                self.handle_success(frontier_board)
                return

            child_board_list = self.get_child_board_list(frontier_board, False)
                            
            for child_board in child_board_list:
                if not self.is_board_explored(child_board) and not self.is_board_in_frontier(child_board):
                    self.add_to_frontier(child_board)
                    self.board_helper.calculate_cost_function_for_board(child_board)
                elif self.is_board_in_frontier(child_board):
                    self.board_helper.calculate_cost_function_for_board(child_board)
                    self.correct_cost_function_in_frontier_board(child_board)

    def correct_cost_function_in_frontier_board(self, board: Board):
        frontier_board = self.get_board_from_frontier_by_arg(board.arg_str)
        if frontier_board is None:
            return
        if frontier_board.cost_function_costs > board.cost_function_costs:
            frontier_board.cost_function_costs = board.cost_function_costs

    def get_board_from_frontier_by_arg(self, arg_str: str) -> Board:
        for boards in self.frontier.items:
            if boards.arg_str == arg_str:
                return boards

    def get_minimal_cost_for_boards_in_frontier(self) -> int:
        min_cost = -1
        for frontier_board in self.frontier.items:
            if frontier_board.cost_function_costs < min_cost or min_cost < 0:
                min_cost = frontier_board.cost_function_costs
        return min_cost

    def get_frontier_index_with_minimal_cost(self, frontier):  # regarding the UDLR order...
        min_cost = self.get_minimal_cost_for_boards_in_frontier()
        frontier_board_with_minimal_cost_list = []

        for frontier_board in frontier.items:
            if frontier_board.cost_function_costs == min_cost:
                frontier_board_with_minimal_cost_list.append(frontier_board)

        if len(frontier_board_with_minimal_cost_list) == 1:
            return frontier.items.index(frontier_board_with_minimal_cost_list[0])
        else:
            for directions in SwitchDirectionList.LIST:
                for frontier_boards in frontier_board_with_minimal_cost_list:
                    if frontier_boards.direction_from_parent == directions:  # get first direction accorind to UDLR
                        return frontier.items.index(frontier_boards)

    def print_success_path(self):
        for boards in self.success_path:
            boards.print_matrix('Success path - created by switch: ' + boards.direction_from_parent)
            
    def get_path_to_goal(self):
        path_to_goal = []        
        for boards in self.success_path:
            if boards.direction_from_parent != SwitchDirection.NONE:
                path_to_goal.append(boards.direction_from_parent)
        return path_to_goal
            
    def get_success_path(self):
        success_path_inverted = [self.success_board]
        parent_board = self.success_board.parent_board
        while parent_board is not None:
            success_path_inverted.append(parent_board)
            parent_board = parent_board.parent_board
        return success_path_inverted[::-1]  # reverse()


class BoardHelper:

    def __init__(self, size_board: int):
        self.size_board = size_board
        self.dim = int(math.sqrt(self.size_board))
        self.number_mapping = []
        for k in range(1, self.dim + 1):
            for m in range(1, self.dim + 1):
                self.number_mapping.append([k, m])
        self.udlr_list = self.__get_udlr_list()  # contains the possible udlr directions for a position
        # contains the lists for each direction for the mapping
        self.index_zero_new_after_switch = self.__get_position_zero_after_switch()

    def get_child_boards(self, board: Board, reverse_udlr: bool):
        index_zero = board.index_zero
        child_board_list = []
        if reverse_udlr:
            direction_list = self.get_reversed_udlr_list(index_zero)
        else:
            direction_list = self.get_udlr_list(index_zero)

        for directions in direction_list:
            index_zero_new = self.get_position_zero_after_switch(index_zero, directions)
            child_board = self.get_child_board(board, index_zero_new)
            if child_board is not None:
                child_board.direction_from_parent = directions
                child_board_list.append(child_board)
        return child_board_list

    @staticmethod
    def get_child_board(parent_board: Board, index_zero_new: int):
        child_board = parent_board.clone()
        child_board.parent_board = parent_board
        child_board.level_in_search_tree = parent_board.level_in_search_tree + 1
        child_board.switch_zero(index_zero_new)
        return child_board

    def calculate_cost_function_for_board(self, input_board: Board):
        g_current_costs = input_board.level_in_search_tree
        h_heuristic_costs = self.get_heuristic_cost_for_board(input_board)
        input_board.cost_function_costs = g_current_costs + h_heuristic_costs

    def get_heuristic_cost_for_board(self, input_board):
        return self.get_number_misplaced_tiles(input_board) + self.get_manhattan_distance(input_board)

    @staticmethod
    def get_number_misplaced_tiles(input_board):
        counter = 0
        for k in range(0, len(input_board.items)):
            if input_board.items[k] != k and k > 0:  # 0 is not regarded as wrong
                counter += 1
        return counter
    
    def get_manhattan_distance(self, input_board: Board):
        diff = 0
        for k in range(0, len(input_board.items)):
            value = input_board.items[k]
            if value > 0:  # 0 is not regarded as wrong
                position_k = self.get_manhattan_value(k)
                position_value = self.get_manhattan_value(value)
                diff += abs(position_k[0] - position_value[0]) + abs(position_k[1] - position_value[1])           
        return diff
    
    def get_manhattan_value(self, number):        
        return self.number_mapping[number]

    def get_udlr_list(self, zero_index: int):
        return self.udlr_list[zero_index]

    def is_switch_zero_possible(self, zero_index: int, next_direction: SwitchDirection):
        udlr_list_for_zero_index = self.udlr_list[zero_index]
        return next_direction in udlr_list_for_zero_index

    def __get_udlr_list(self):
        udlr_list_local = []
        for k in range(0, self.size_board):
            udlr = []
            mapping = self.number_mapping[k]
            if mapping[0] > 1:
                udlr.append(SwitchDirection.UP)
            if mapping[0] < self.dim:
                udlr.append(SwitchDirection.DOWN)
            if mapping[1] > 1:
                udlr.append(SwitchDirection.LEFT)
            if mapping[1] < self.dim:
                udlr.append(SwitchDirection.RIGHT)
            udlr_list_local.append(udlr)
        return udlr_list_local
            
    def get_reversed_udlr_list(self, zero_index: int):
        udlr = self.udlr_list[zero_index]
        return udlr[::-1] 
    
    def get_position_zero_after_switch(self, position_zero, switch_direction):
        return self.index_zero_new_after_switch[SwitchDirectionList.LIST.index(switch_direction)][position_zero]

    def __get_position_zero_after_switch(self):
        result_list = []
        for directions in SwitchDirectionList.LIST:
            direction_mapping = []
            for k in range(0, self.size_board):
                udlr_list = self.udlr_list[k]
                mapping = self.number_mapping[k].copy()  # flat copy
                if directions in udlr_list:
                    if directions == SwitchDirection.UP:
                        mapping[0] = mapping[0] - 1
                    elif directions == SwitchDirection.DOWN:
                        mapping[0] = mapping[0] + 1
                    elif directions == SwitchDirection.LEFT:
                        mapping[1] = mapping[1] - 1
                    elif directions == SwitchDirection.RIGHT:
                        mapping[1] = mapping[1] + 1
                    direction_mapping.append(self.number_mapping.index(mapping))
                else:
                    direction_mapping.append(self.number_mapping.index(mapping))
            result_list.append(direction_mapping)
            print(directions + ':' + str(direction_mapping))
        return result_list


class TestBoard:

    def __init__(self, depth_level: int):
        self.depth_level = depth_level
        self.board = Board(0, 1, 2, 3, 4, 5, 6, 7, 8)
        self.board_helper = BoardHelper(len(self.board.items))
        self.movements = []
        self.last_possible_random_direction = None  # used to avoid a forth and backward situation
        self.generate_test_board()
        
    def get_test_board_parameters(self):
        return self.board.items
        
    def generate_test_board(self):
        for k in range(0, self.depth_level):
            next_direction = self.get_next_possible_random_direction()
            self.movements.append(next_direction)
            self.board.switch_zero(self.board_helper.get_position_zero_after_switch(self.board.index_zero, next_direction))

    def is_new_direction(self, direction: SwitchDirection):
        if self.last_possible_random_direction == SwitchDirection.DOWN and direction == SwitchDirection.UP:
            return False
        if self.last_possible_random_direction == SwitchDirection.UP and direction == SwitchDirection.DOWN:
            return False
        if self.last_possible_random_direction == SwitchDirection.RIGHT and direction == SwitchDirection.LEFT:
            return False
        if self.last_possible_random_direction == SwitchDirection.LEFT and direction == SwitchDirection.RIGHT:
            return False
        return True

    def get_next_possible_random_direction(self) -> SwitchDirection:
        next_switch_possible = False
        next_possible_random_direction = 0
        while not next_switch_possible:
            direction_number = random.randint(1, 4) - 1
            next_possible_random_direction = SwitchDirectionList.LIST[direction_number]
            next_switch_possible = self.is_new_direction(next_possible_random_direction) \
                                   and self.board_helper.is_switch_zero_possible(self.board.index_zero, next_possible_random_direction)
        self.last_possible_random_direction = next_possible_random_direction
        return next_possible_random_direction


class Solver:

    def __init__(self, tree_type, *args):
        self.tree_type = tree_type  # BFS, DFS, AST
        self.board_start = Board(*args)
        self.board_goal = Board(0, 1, 2, 3, 4, 5, 6, 7, 8)
        self.board_tree = BoardTree(self.board_start, self.board_goal)
        self.running_start = time.time()
        self.running_end = None

    def run_algorithm(self):
        if self.tree_type == 'BFS':
            self.board_tree.perform_bfs(self.board_start)
        elif self.tree_type == 'DFS':
            self.board_tree.perform_dfs(self.board_start)
        else:
            self.board_tree.perform_ast(self.board_start)
        self.running_end = time.time()

    def print_success_path(self):
        self.board_tree.print_success_path()
        
    def print_results(self):
        self.board_start.print_matrix('BoardTree.board_start')
        for entries in self.get_results():
            print(entries)
            
    def write_results(self):        
        with open('output.txt', 'w') as file_obj:
            for entries in self.get_results():
                file_obj.write(entries + '\n')
        print('Results written to {}'.format(file_obj.name))
     
    def get_results(self):
        value_list = ['path_to_goal: {}'.format(str(self.board_tree.get_path_to_goal())),
                      'cost_of_path: {}'.format(len(self.board_tree.success_path) - 1),
                      'notes_expanded: {}'.format(self.board_tree.nodes_expanded),
                      'search_depth: {}'.format(len(self.board_tree.success_path) - 1),
                      'max_search_depth: {}'.format(self.board_tree.max_search_depth),
                      'running_time: {0:9.8f}'.format(self.running_end - self.running_start),
                      'max_ram_usage: {0:9.8f}'.format(self.get_max_ram_usage / (10 ** 6 * 8))]
        return value_list
        
    @property
    def get_max_ram_usage(self):
        process = psutil.Process(os.getpid())
        return process.memory_info()[0] / (1024 * 1000)  # float(2 ** 20)


# args = (1, 2, 5, 3, 4, 0, 6, 7, 8)
# board_helper = BoardHelper(len(args))
# print(len(sys.argv))
# print(sys.executable)

test = False
if test:
   test_board = TestBoard(7)
   print(tuple(test_board.get_test_board_parameters()))
   print(test_board.movements)
   args = tuple(test_board.get_test_board_parameters())
   type = 'AST'
elif len(sys.argv)> 1:  # started from command prompt
   type = sys.argv[1].upper()
   args = ast.literal_eval(sys.argv[2]) # ast.literal_eval splits the string into a tuple
else:
   type = 'BFS'
   args = (3, 1, 2, 0, 4, 5, 6, 7, 8) # BFS - 3 levels UDLR path_to_goal: ['Up']
   args = (6, 1, 8, 4, 0, 2, 7, 3, 5)  # 1,2,5,3,4,0,6,7,8
   args = (1, 2, 5, 3, 4, 0, 6, 7, 8) # BFS - 3 levels UDLR path_to_goal: ['Up', 'Left', 'Left']
#   args = (1, 0, 2, 3, 4, 5, 6, 7, 8)
   args = (8,6,4,2,1,3,5,7,0)
   type = 'DFS'


solver = Solver(type, *args)
solver.run_algorithm()
solver.print_results()
# solver.print_success_path()
solver.write_results()

# args = (3,1,2,6,4,5,0,7,8) # DFS - 3 levels UDLR
# args = (1,4,2,3,7,5,6,0,8) # DFS - 3 levels UDLR
# args = (1,2,0,3,4,5,6,7,8)
# args = (1,2,5,3,4,0,6,7,8) #example 1
#
# args_goal = (0,1,2,3,4,5,6,7,8)
# board_start = Board(*args)
# board_goal = Board(*args_goal)

