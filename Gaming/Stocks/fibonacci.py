"""
Description: This module contains the Fibonacci classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_function_container import PatternFunctionContainer
from pattern_configuration import config
from sertl_analytics.constants.pattern_constants import FD, TT, DIR, FR, CN
from pattern_wave_tick import WaveTick
import pandas as pd
import time
import math
from sertl_analytics.searches.smart_searches import Stack, Queue


class FibonacciWaveComponent:
    def __init__(self, position_in_wave: int):
        self.position_in_wave = position_in_wave
        self._tick_list = []
        self.tick_previous = None
        self.tick_first = None
        self.tick_last = None
        self.tick_next = None
        self.max = -math.inf
        self.min = math.inf

    def add_tick(self, tick: WaveTick):
        self._tick_list.append(tick)
        if self.tick_first is None:
            self.tick_first = tick
        self.tick_last = tick
        if tick.high > self.max:
            self.max = tick.high
        if tick.low < self.min:
            self.min = tick.low

    @property
    def range(self):
        return round(self.max - self.min, 2)

    def is_component_consistent(self):
        return self.is_component_internally_consistent() and self.is_component_wave_consistent()

    def is_component_internally_consistent(self):
        pass

    def is_component_wave_consistent(self):
        pass

    def is_component_ready_for_another_tick(self):
        pass

    def get_details(self):
        pass

    def get_xy_parameter(self):
        pass


class FibonacciRegressionComponent(FibonacciWaveComponent):
    def __init__(self, position_in_wave: int):
        FibonacciWaveComponent.__init__(self, position_in_wave)
        self.regression_value_against_last_regression = 0
        self.regression_value_against_last_retracement = 0
        self.regression_pct_against_last_regression = 0

    def is_component_internally_consistent(self):
        return self.tick_first.low == self.min and self.tick_last.high == self.max

    def is_component_wave_consistent(self):
        return self.position_in_wave == 0 or self.regression_pct_against_last_regression >= FR.R_500

    def is_a_regression_to(self, wave_compare: FibonacciWaveComponent):
        return self.max > wave_compare.max

    def is_component_ready_for_another_tick(self):
        return self.is_component_internally_consistent()

    def get_details(self):
        return '{: <12}: {} - {}: Regression against reg: {} ({:4.1f}%) - against retracement: {}'.\
            format('Regression', self.tick_first.date, self.tick_last.date,
                   self.regression_value_against_last_regression,
                   self.regression_pct_against_last_regression * 100,
                   self.regression_value_against_last_retracement)

    def get_xy_parameter(self):
        x = [self.tick_first.f_var, self.tick_last.f_var]
        y = [self.tick_first.high, self.tick_last.low]
        xy = list(zip(x, y))
        return xy


class FibonacciRetracementComponent(FibonacciWaveComponent):
    def __init__(self, position_in_wave: int):
        FibonacciWaveComponent.__init__(self, position_in_wave)
        self.retracement_value = 0
        self.retracement_pct = 0

    def is_component_internally_consistent(self):
        return self.tick_first.direction == DIR.DOWN or self.tick_first.tick_type == TT.DOJI \
               or self.tick_first.high < self.tick_previous.high

    def is_component_wave_consistent(self):
        return 0 < self.retracement_pct < 1

    def is_a_retracement_to(self, wave_regression: FibonacciRegressionComponent):
        return wave_regression.min < self.min < wave_regression.max

    def is_retracement_fibonacci_compliant(self):
        return FR.is_retracement_value_compliant(self.retracement_pct)

    def is_component_ready_for_another_tick(self):
        return self.retracement_pct < 1

    def get_details(self):
        return '{: <12}: {} - {}: Retracement: {} ({:4.1f}%)'.format('Retracement', self.tick_first.date,
                                                                self.tick_last.date,
                                                                self.retracement_value,
                                                                self.retracement_pct * 100)

    def get_xy_parameter(self):
        x = [self.tick_first.f_var, self.tick_last.f_var]
        y = [self.tick_first.high, self.tick_last.low]
        xy = list(zip(x, y))
        return xy


class FibonacciWave:
    wave_id_list_regression = ['w_1', 'w_3', 'w_5']
    wave_id_list_retracement = ['w_2', 'w_4']
    wave_id_list = ['w_1', 'w_2', 'w_3', 'w_4', 'w_5']

    def __init__(self, tick_list, start: int, component_len_list: list):
        self.level_in_search_tree = 0
        self.wave_dic = {}
        self.tick_list = tick_list
        self.start = start
        self.component_len_list = component_len_list
        self.__arg_str = self.__get_arg_str__()
        self.__init_wave_dic__()
        self.__add_ticks_to_wave_components__()
        self.__add_previous_next_ticks_to_components__()
        self.__calculate_regressions__()
        self.__calculate_retracements__()

    @property
    def arg_str(self):
        return self.__arg_str

    @property
    def regression_wave_list(self):
        return [self.wave_dic[wave_id] for wave_id in self.wave_id_list_regression]

    @property
    def retracement_wave_list(self):
        return [self.wave_dic[wave_id] for wave_id in self.wave_id_list_retracement]

    def get_incremented_component_len_list(self, increment_index: int):
        return [len_value + 1 if index == increment_index else len_value
                for index, len_value in enumerate(self.component_len_list)]

    def get_wave_component_by_index(self, index: int):
        return self.wave_dic[self.wave_id_list[index]]

    def get_wave_component_by_number(self, number: int):
        return self.wave_dic[self.wave_id_list[number - 1]]

    def __get_arg_str__(self):
        return 'Start: {} - Len_list: {}'.format(self.start, self.component_len_list)

    def __init_wave_dic__(self):
        for wave_id in self.wave_id_list_regression:
            self.wave_dic[wave_id] = FibonacciRegressionComponent(int(wave_id[-1]))
        for wave_id in self.wave_id_list_retracement:
            self.wave_dic[wave_id] = FibonacciRetracementComponent(int(wave_id[-1]))

    def __add_ticks_to_wave_components__(self):
        position = self.start - 1
        for index, len_value in enumerate(self.component_len_list):
            wave_id = self.wave_id_list[index]
            for k in range(0, len_value):
                position += 1
                self.wave_dic[wave_id].add_tick(self.tick_list[position])

    def __add_previous_next_ticks_to_components__(self):
        for index in range(0, len(self.wave_id_list) - 1):
            wave_previous = self.get_wave_component_by_index(index)
            wave_next = self.get_wave_component_by_index(index + 1)
            wave_previous.tick_next = wave_next.tick_first
            wave_next.tick_previous = wave_previous.tick_last

    def is_wave_fibonacci_wave(self):
        print('Check fibonacci wave: {}'.format(self.__arg_str))
        # 1. check if the components are internally consistent
        internal_ok = self.__are_components_internally_consistent__()
        if not internal_ok:
            return False

        # 2. check if each retracement component is a retracement
        for retracement_wave in self.retracement_wave_list:
            if retracement_wave.retracement_pct == 0:
                return False

        # 3. check if each progression is a progression compared to the last progression and the latest retracement
        for k in range(0, 2):
            wave_regression_previous = self.wave_dic[self.wave_id_list_regression[k]]
            wave_retracement_previous = self.wave_dic[self.wave_id_list_retracement[k]]
            wave_regression_next = self.wave_dic[self.wave_id_list_regression[k+1]]
            if not wave_regression_next.is_a_regression_to(wave_regression_previous):
                return False
            if not wave_regression_next.is_a_regression_to(wave_retracement_previous):
                return False

        # 4. check if the retracements are fibonacci retracements
        # for retracement_wave in self.retracement_wave_list:
        #     if not retracement_wave.is_retracement_fibonacci_compliant():
        #         return False

        return True

    def __calculate_retracements__(self):
        for k in range(0, 2):
            wave_regression = self.wave_dic[self.wave_id_list_regression[k]]
            wave_retracement = self.wave_dic[self.wave_id_list_retracement[k]]
            if wave_retracement.is_a_retracement_to(wave_regression):
                wave_retracement.retracement_value = round(wave_regression.max - wave_retracement.min, 2)
                wave_retracement.retracement_pct = round(wave_retracement.retracement_value/wave_regression.range, 3)

    def __calculate_regressions__(self):
        for k in range(0, 2):
            wave_regression_previous = self.wave_dic[self.wave_id_list_regression[k]]
            wave_retracement_previous = self.wave_dic[self.wave_id_list_retracement[k]]
            wave_regression_next = self.wave_dic[self.wave_id_list_regression[k + 1]]
            wave_regression_next.regression_value_against_last_regression = \
                round(wave_regression_next.max - wave_regression_previous.max, 2)
            wave_regression_next.regression_value_against_last_retracement = \
                round(wave_regression_next.max - wave_retracement_previous.max, 2)
            wave_regression_next.regression_pct_against_last_regression = \
                round(wave_regression_next.range / wave_regression_previous.range, 3)

    def __are_components_internally_consistent__(self):
        for wave_id in self.wave_id_list_regression:
            if not self.wave_dic[wave_id].is_component_internally_consistent():
                return False
        return True

    def print(self):
        for wave_id in self.wave_id_list:
            print(self.wave_dic[wave_id].get_details())

    def get_xy_parameter(self):
        xy = []
        for wave_id in self.wave_id_list:
            xy = xy + self.wave_dic[wave_id].get_xy_parameter()
        return xy


class FibonacciWaveTree:
    def __init__(self, tick_list: list):
        self.tick_list = tick_list
        self.explored_arg_set = {''}  # set which contains the already explored nodes
        self.frontier_arg_set = {''}  # set which contains the nodes currently in the frontier
        self.frontier = None  # will contain either a Queue or a Stack
        self.success_wave_list = []
        self.success_path = []
        self.nodes_expanded = 0
        self.max_search_depth = 1
        self.time_lastCheck = time.time()

    def is_wave_explored(self, wave: FibonacciWave):
        return wave.arg_str in self.explored_arg_set

    def is_board_in_frontier(self, wave: FibonacciWave):
        return wave.arg_str in self.frontier_arg_set

    def add_to_explored(self, wave: FibonacciWave):
        if not self.is_wave_explored(wave):
            self.explored_arg_set.add(wave.arg_str)

    def add_to_frontier(self, wave: FibonacciWave):
        if not self.is_board_in_frontier(wave):
            self.frontier_arg_set.add(wave.arg_str)
            if isinstance(self.frontier, Queue):
                self.frontier.enqueue(wave)
            else:  # Stack
                self.frontier.push(wave)

    def get_next_wave_from_frontier(self, *argv) -> FibonacciWave:
        if isinstance(self.frontier, Queue):
            wave = self.frontier.dequeue()
        else:  # Stack
            if argv[0] is None:
                wave = self.frontier.pop()
            else:
                wave = self.frontier.pop_pos(argv[0])
        self.add_to_explored(wave)
        self.frontier_arg_set.remove(wave.arg_str)
        return wave

    def get_child_wave_list(self, frontier_wave: FibonacciWave):
        child_board_list = self.__get_child_waves__(frontier_wave)
        self.nodes_expanded += 1
        self.check_progress(self.frontier)
        if self.max_search_depth < frontier_wave.level_in_search_tree:
            self.max_search_depth = frontier_wave.level_in_search_tree + 1
        return child_board_list

    def __get_child_waves__(self, parent_wave: FibonacciWave):
        if not self.has_wave_any_children(parent_wave):
            return []
        child_list = []
        for comp_ind in range(0, len(parent_wave.component_len_list)):
            wave_component = parent_wave.get_wave_component_by_index(comp_ind)
            if wave_component.is_component_ready_for_another_tick():
                component_len_list = parent_wave.get_incremented_component_len_list(comp_ind)
                if parent_wave.start + sum(component_len_list) < len(parent_wave.tick_list):
                    wave = FibonacciWave(self.tick_list, parent_wave.start, component_len_list)
                    wave_component_new = wave.get_wave_component_by_index(comp_ind)
                    if wave_component_new.is_component_consistent():
                        child_list.append(wave)
        child_list = reversed(child_list)
        return child_list

    def has_wave_any_children(self, wave: FibonacciWave):
        wave_component_0 = wave.get_wave_component_by_index(0)
        wave_component_1 = wave.get_wave_component_by_index(1)
        if wave_component_0.is_component_ready_for_another_tick():
            component_len_list = wave.get_incremented_component_len_list(0)
            if wave.start + sum(component_len_list) < len(wave.tick_list):
                wave = FibonacciWave(self.tick_list, wave.start, component_len_list)
                wave_component_0_new = wave.get_wave_component_by_index(0)
                if wave_component_0_new.is_component_consistent():
                    return True
        return wave_component_1.is_component_consistent()

    def perform_dfs(self, input_wave: FibonacciWave):  # STACK: LAST IN FIRST OUT (LIFO)
        self.frontier = Stack()
        self.add_to_frontier(input_wave)

        while not self.frontier.is_empty:
            frontier_wave = self.get_next_wave_from_frontier(None)

            if frontier_wave.is_wave_fibonacci_wave():
                self.handle_success(frontier_wave)
                return

            child_board_list = self.get_child_wave_list(frontier_wave)

            for child_board in child_board_list:
                if not self.is_wave_explored(child_board) and not self.is_board_in_frontier(child_board):
                    self.add_to_frontier(child_board)

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

    def handle_success(self, wave: FibonacciWave):
        print('Wave {}: - data: {}'.format(wave.arg_str, wave.get_xy_parameter()))
        wave.print()
        self.success_wave_list.append(wave)


class FibonacciWaveController:
    def __init__(self, tick_list: list):
        self.tick_list = tick_list
        self.tree = FibonacciWaveTree(tick_list)
        print('len(tick_list)={}'.format(len(self.tick_list)))

    def process_tick_list(self):
        for index in range(0, len(self.tick_list)-5):
        # for index in range(0, 2):
            wave = FibonacciWave(self.tick_list, index, [1, 1, 1, 1, 1])
            self.tree.perform_dfs(wave)