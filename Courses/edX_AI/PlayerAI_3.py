from random import randint
from BaseAI_3 import BaseAI
from Grid_3 import Grid
import time
import math
import sys

"""
returns a number that indicates the player’s action. In particular, 0 stands for "Up", 1 stands for "Down", 2 stands for "Left", and 3 stands for "Right". You need to create this file and make it as intelligent as possible. You may include other files in your submission, but they will have to be included through this file.
"""

class PlayerAI(BaseAI):

    def __init__(self):
        self.visited_grid_id_set = {''}  # set which contains the already explored nodes
        self.depth_level = 0  # will be set depending on the tree structure and the speed of the first branch
        self.number_grid_cells = 0
        self.number_grid_cells_zero = 0
        self.time_start = None
        self.run_time = None
        self.level_number_branches = {}
        self.return_move = -1  # will be overwritten by the latest best next move - to sort the children accordingly
        self.maximize_values = {}
        self.minimize_values = {}
        self.run_time_list = []

    def getMove(self, grid):
        self.time_start = time.clock()
        self.maximize_values = {}
        self.minimize_values = {}
        self.depth_level = 0  # init this variable for each run
        self.set_grid_cell_numbers(grid)
        grid.current_depth = 0
        self.return_move = self.get_decision_move(grid)
        self.run_time = time.clock() - self.time_start
        self.run_time_list.append(self.run_time)
        # print('getMove = {0} within {1:9.8f} seconds'.format(self.return_move, self.run_time), end='\n')
        return self.return_move
        moves = grid.getAvailableMoves()
        return moves[randint(0, len(moves) - 1)] if moves else None

    def add_grid_value_to_dictionary(self, grid: Grid, grid_value, min_max: str):
        grid_id = self.get_grid_id(grid)
        # print('add_grid_value_to_dictionary - {}: {} for {}'.format(min_max, grid_value, grid_id))
        if min_max == 'min' and not grid_id in self.minimize_values:
                self.minimize_values.update({grid_id: grid_value})
        elif min_max == 'max' and not grid_id in self.maximize_values:
                self.maximize_values.update({grid_id: grid_value})

    def is_grid_value_in_dictionary(self, grid: Grid, min_max: str):
        grid_id = self.get_grid_id(grid)
        if (min_max == 'min' and grid_id in self.minimize_values) or (min_max == 'max' and grid_id in self.maximize_values):
            return True
        else:
            return False

    def get_grid_value_from_dictionary(self, grid: Grid, min_max: str):
        grid_id = self.get_grid_id(grid)
        if min_max == 'min' and grid_id in self.minimize_values:
            return self.minimize_values.get(grid_id)
        elif min_max == 'max' and grid_id in self.maximize_values:
            return self.maximize_values.get(grid_id)

    def set_grid_cell_numbers(self, grid: Grid):
        self.number_grid_cells = grid.size**2
        self.number_grid_cells_zero = len(grid.getAvailableCells())
        if self.number_grid_cells_zero == 0:
            self.number_grid_cells_zero = 1  # to avoid problems
        self.level_number_branches.update({'0': 1})  # default value for 0 - which is only used for this calculation
        for k in range(1, 100):
            if k % 2 == 1:  # on that level the computer's values are added to each branch
                self.level_number_branches.update({str(k): self.level_number_branches.get(str(k-1)) * self.number_grid_cells_zero * 2})
            else: # on that level the movements are added to each branch
                self.level_number_branches.update({str(k): self.level_number_branches.get(str(k-1)) * 4})

    def set_depth_level(self, current_grid_level: int):
        time_spent = time.clock() - self.time_start
        if time_spent * self.level_number_branches.get(str(current_grid_level)) > 0.2:
            self.depth_level = current_grid_level  # we are using alpha-beta pruning (i.e. twice so fast)
            # print('Current depth_level = {}'.format(self.depth_level))

    def is_grid_already_visited(self, grid: Grid):
        grid_id = self.get_grid_id(grid)
        if grid_id in self.visited_grid_id_set:
            return True
        else:
            self.visited_grid_id_set.add(grid_id)
            return False

    @staticmethod
    def get_grid_id(grid: Grid) -> str:
        grid_id = ''
        for x in range(grid.size):
            for y in range(grid.size):
                grid_id += str(grid.map[x][y]) if x == 0 and y == 0 else '-' + str(grid.map[x][y])
        return grid_id

    def minimize(self, grid: Grid, a, b):  # returns TUPLE of (state, utility)
        if self.is_state_terminal(grid, 'min'): # or self.is_grid_already_visited(grid):
            return None, self.get_grid_value(grid)

        (min_child, min_utility) = (None, math.inf)

        children = self.get_children(grid, 'min')  # get children by filling the gaps
        for child in children:
            if self.is_grid_value_in_dictionary(child, 'min'):
                utility = self.get_grid_value_from_dictionary(child, 'min')
            else:
                (terminal_child, utility) = self.maximize(child, a, b)
                # self.add_grid_value_to_dictionary(child, utility, 'min')

            try:
                if utility < min_utility:
                    (min_child, min_utility) = (child, utility)
            except TypeError:
                print('error with grid {}: {}'.format(self.get_grid_id(child), sys.exc_info()[0]))
                raise

            if min_utility <= a:
                break

            if min_utility < b:
                b = min_utility

        return min_child, min_utility

    def maximize(self, grid: Grid, a, b):  # returns TUPLE of (state, utility)
        if self.is_state_terminal(grid, 'max'):  # or self.is_grid_already_visited(grid):
            return None, self.get_grid_value(grid)

        (max_child, max_utility) = (None, -math.inf)

        children = self.get_children(grid, 'max')  # get children by UDLR
        for child in children:
            if self.is_grid_value_in_dictionary(child, 'max'):
                utility = self.get_grid_value_from_dictionary(child, 'max')
            else:
                (terminal_child, utility) = self.minimize(child, a, b)
                # self.add_grid_value_to_dictionary(child, utility, 'max')

            try:
                if utility > max_utility:
                    (max_child, max_utility) = (child, utility)
            except TypeError:
                print('error with grid {}: {}'.format(self.get_grid_id(child), sys.exc_info()[0]))
                raise

            if max_utility >= b:
                break

            if max_utility > a:
                a = max_utility

        return max_child, max_utility

    def is_state_terminal(self, grid_to_check: Grid, min_max: str):
        if self.is_grid_depth_out_of_bound(grid_to_check.current_depth):
            return True

        if min_max == 'min':
            return len(grid_to_check.getAvailableCells()) == 0 # or grid.getMaxTile() > 100
        else:
            return not grid_to_check.canMove()  # or grid.getMaxTile() > 100

    def is_grid_depth_out_of_bound(self, grid_current_depth: int):
        if self.depth_level == 0:
            self.set_depth_level(grid_current_depth)
            return False
        else:
            return grid_current_depth >= self.depth_level

    def get_children(self, grid: Grid, min_or_max: str):
        grid_children = []

        if min_or_max == 'max':
            moves = grid.getAvailableMoves()
            for move in moves:
                child_grid = self.get_grid_for_move(grid, move)
                child_grid.current_depth = grid.current_depth + 1
                grid_children.append(child_grid)
        else:
            cells = grid.getAvailableCells()
            values = [2, 4]
            for cell in cells:
                for value in values:
                    grid_copy = grid.clone()
                    grid_copy.setCellValue(cell, value)
                    grid_copy.current_depth = grid.current_depth + 1
                    grid_children.append(grid_copy)
        return grid_children

    def get_decision_move(self, grid: Grid) -> Grid:
        # print('get_decision_move (input): {}'.format(grid.map))
        moves = grid.getAvailableMoves()
        max_value = -math.inf
        self.sort_moves_for_alpha_beta_pruning(moves)
        for move in moves:
            grid_after_move = self.get_grid_for_move(grid, move)
            grid_after_move.current_depth = grid.current_depth + 1
            a = -math.inf
            b = math.inf
            (child, utility) = self.minimize(grid_after_move, a, b)  # the first move was already done in this function
            # print('get_decision_move: {} with utility_value (min) = {} for move {}'.format(grid_after_move.map, utility, move))
            if utility > max_value:
                move_return = move
                max_value = utility
        return move_return

    def sort_moves_for_alpha_beta_pruning(self, moves):
        if self.return_move < 0 or moves[0] == self.return_move or not self.return_move in moves:
            return
        moves[moves.index(self.return_move)] = moves[0]
        moves[0] = self.return_move

    def get_grid_for_move(self, grid: Grid, move: int):
        clone = grid.clone()
        clone.move(move)
        return clone

    @staticmethod
    def get_grid_value(grid: Grid):
        number_cells = grid.size ** 2
        sum_tiles = 0
        neigbors_equal = 0
        for x in range(grid.size):
            for y in range(grid.size):
                sum_tiles += grid.map[x][y]
                if (x < grid.size -1) and grid.map[x][y] == grid.map[x+1][y]:
                    neigbors_equal += 1
                if (y < grid.size -1) and grid.map[x][y] == grid.map[x][y+1]:
                    neigbors_equal += 1

        average = sum_tiles/number_cells
        number_zero_cells = len(grid.getAvailableCells())

        return 2*number_zero_cells/number_cells + average/2048 + neigbors_equal/number_cells