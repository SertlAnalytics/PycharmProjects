"""
Description: This module contains the Fibonacci classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import TT, DIR, FR
from pattern_wave_tick import WaveTick
from pattern_data_container import pattern_data_handler
import math


class FibonacciWaveComponent:
    def __init__(self, position_in_wave: int):
        self.position_in_wave = position_in_wave
        self._tick_list = []
        self.tick_first = None
        self.tick_last = None
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

    def get_tick_min(self):
        min_value = math.inf
        tick_return = None
        for tick in self._tick_list:
            if tick.low < min_value:
                min_value = tick.low
                tick_return = tick
        return tick_return

    def get_tick_max(self):
        max_value = -math.inf
        tick_return = None
        for tick in self._tick_list:
            if tick.high > max_value:
                max_value = tick.high
                tick_return = tick
        return tick_return

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
        return (self.tick_first.low == self.min and self.tick_last.high == self.max) or True

    def is_component_wave_consistent(self):
        return self.position_in_wave == 1 or self.regression_pct_against_last_regression >= FR.R_500

    def is_a_regression_to(self, wave_compare: FibonacciWaveComponent):
        return self.max > wave_compare.max

    def is_regression_fibonacci_compliant(self):
        return self.position_in_wave == 1 or FR.is_regression_pct_compliant(self.regression_pct_against_last_regression)

    def is_component_ready_for_another_tick(self):
        return self.is_component_internally_consistent()

    def get_details(self):
        return '{: <12}: {} - {}: Regression against reg: {} ({:4.1f}%) - against retracement: {}'.\
            format('Regression', self.tick_first.date, self.tick_last.date,
                   self.regression_value_against_last_regression,
                   self.regression_pct_against_last_regression * 100,
                   self.regression_value_against_last_retracement)

    def get_xy_parameter(self):
        if self.position_in_wave == 1:
            x = [self.tick_first.f_var, self.get_tick_max().f_var]
            y = [self.tick_first.low, self.get_tick_max().high]
        else:
            x = [self.get_tick_max().f_var]
            y = [self.get_tick_max().high]
        xy = list(zip(x, y))
        return xy


class FibonacciRetracementComponent(FibonacciWaveComponent):
    def __init__(self, position_in_wave: int):
        FibonacciWaveComponent.__init__(self, position_in_wave)
        self.retracement_value = 0
        self.retracement_pct = 0

    def is_component_internally_consistent(self):
        return self.tick_first.direction == DIR.DOWN or self.tick_first.tick_type == TT.DOJI or True

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
        x = [self.get_tick_min().f_var]
        y = [self.get_tick_min().low]
        xy = list(zip(x, y))
        return xy


class FibonacciWave:
    wave_id_list_regression = ['w_1', 'w_3', 'w_5']
    wave_id_list_retracement = ['w_2', 'w_4']
    wave_id_list = ['w_1', 'w_2', 'w_3', 'w_4', 'w_5']

    def __init__(self, tick_list, component_len_list: list):
        self.level_in_search_tree = 0
        self.wave_dic = {}
        self.tick_list = tick_list
        self.start = self.tick_list[0].position
        self.length = len(self.wave_id_list)
        self.component_len_list = component_len_list
        self.__arg_str = self.__get_arg_str__()
        self.__init_wave_dic__()
        self.__add_ticks_to_wave_components__()
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

    def get_wave_component_by_index(self, index: int):
        return self.wave_dic[self.wave_id_list[index]]

    def get_wave_component_by_number(self, number: int):
        return self.wave_dic[self.wave_id_list[number - 1]]

    def __get_arg_str__(self):
        return 'Start: {} - Length_list: {}'.format(self.start, self.component_len_list)

    def __init_wave_dic__(self):
        for wave_id in self.wave_id_list_regression:
            self.wave_dic[wave_id] = FibonacciRegressionComponent(int(wave_id[-1]))
        for wave_id in self.wave_id_list_retracement:
            self.wave_dic[wave_id] = FibonacciRetracementComponent(int(wave_id[-1]))

    def __add_ticks_to_wave_components__(self):
        position = - 1
        for index, len_value in enumerate(self.component_len_list):
            wave_id = self.wave_id_list[index]
            for k in range(0, len_value):
                position += 1
                self.wave_dic[wave_id].add_tick(self.tick_list[position])

    def is_wave_fibonacci_wave(self):
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
        for retracement_wave in self.retracement_wave_list:
            if not retracement_wave.is_retracement_fibonacci_compliant():
                return False

        # 5. check if the regressions are fibonacci regressions
        for regression_wave in self.regression_wave_list:
            if not regression_wave.is_regression_fibonacci_compliant():
                return False

        return True

    def __calculate_retracements__(self):
        pass

    def __calculate_regressions__(self):
       pass

    def __are_components_internally_consistent__(self):
        for wave_id in self.wave_id_list:
            if not self.wave_dic[wave_id].is_component_internally_consistent():
                return False
        return True

    def print(self):
        for wave_id in self.wave_id_list:
            print(self.wave_dic[wave_id].get_details())

    def get_xy_parameter(self):
        xy = []
        for index in range(0, 5):
            xy = xy + self.get_wave_component_by_index(index).get_xy_parameter()
        return xy


class FibonacciAscendingWave(FibonacciWave):
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

    def __calculate_retracements__(self):
        for k in range(0, 2):
            wave_regression = self.wave_dic[self.wave_id_list_regression[k]]
            wave_retracement = self.wave_dic[self.wave_id_list_retracement[k]]
            if wave_retracement.is_a_retracement_to(wave_regression):
                wave_retracement.retracement_value = round(wave_regression.max - wave_retracement.min, 2)
                wave_retracement.retracement_pct = round(wave_retracement.retracement_value/wave_regression.range, 3)


class FibonacciDescendingWave(FibonacciWave):
    def __calculate_regressions__(self):
        for k in range(0, 2):
            wave_regression_previous = self.wave_dic[self.wave_id_list_regression[k]]
            wave_retracement_previous = self.wave_dic[self.wave_id_list_retracement[k]]
            wave_regression_next = self.wave_dic[self.wave_id_list_regression[k + 1]]
            wave_regression_next.regression_value_against_last_regression = \
                round(wave_regression_previous.min - wave_regression_next.min, 2)
            wave_regression_next.regression_value_against_last_retracement = \
                round(wave_retracement_previous.min - wave_regression_next.min, 2)
            wave_regression_next.regression_pct_against_last_regression = \
                round(wave_regression_next.range / wave_regression_previous.range, 3)

    def __calculate_retracements__(self):
        for k in range(0, 2):
            wave_regression = self.wave_dic[self.wave_id_list_regression[k]]
            wave_retracement = self.wave_dic[self.wave_id_list_retracement[k]]
            if wave_retracement.is_a_retracement_to(wave_regression):
                wave_retracement.retracement_value = round(wave_retracement.max - wave_regression.min, 2)
                wave_retracement.retracement_pct = round(wave_retracement.retracement_value/wave_regression.range, 3)


class FibonacciWaveTree:
    def __init__(self, tick_list: list):
        self.tick_list = tick_list
        self.length = len(self.tick_list)

    def get_component_len_lists(self, for_ascending_wave: bool):
        ascending_tick_high_index_list = self.__get_min_or_max_tick_index_list__(for_ascending_wave)
        number_tick_high = len(ascending_tick_high_index_list)
        if number_tick_high < 3:
            return []
        len_list = []
        for i_01 in range(0, number_tick_high - 2):
            index_01 = ascending_tick_high_index_list[i_01]
            for i_02 in range(i_01 + 1, number_tick_high - 1):
                index_02 = ascending_tick_high_index_list[i_02]
                index_min_01 = self.__get_index_between_indices__(index_01, index_02, for_ascending_wave)
                index_min_02 = self.__get_index_between_indices__(index_02, ascending_tick_high_index_list[-1],
                                                                  for_ascending_wave)
                len_list.append([index_01+1, index_min_01 - index_01, index_02 - index_min_01,
                                 index_min_02 - index_02, ascending_tick_high_index_list[-1] - index_min_02])
        return len_list

    def __get_index_between_indices__(self, index_01: int, index_02: int, for_min_between_max: bool):
        compare_value = math.inf if for_min_between_max else -math.inf
        index_return = 0
        for tick_index in range(index_01 + 1, index_02):
            tick = self.tick_list[tick_index]
            if for_min_between_max and tick.low < compare_value:
                index_return = tick_index
                compare_value = tick.low
            elif not for_min_between_max and tick.high > compare_value:
                index_return = tick_index
                compare_value = tick.high
        return index_return

    def __get_min_or_max_tick_index_list__(self, for_ascending_wave: bool):
        tick_index_list = []
        comp_value = -math.inf if for_ascending_wave else math.inf
        for index in range(0, self.length-1):
            tick = self.tick_list[index]
            tick_next = self.tick_list[index+1]
            if for_ascending_wave:
                if tick_next.close < tick.close and index != 0:
                    if comp_value < tick.close:
                        comp_value = tick.close
                        tick_index_list.append(index)
                if index == self.length-2 and comp_value < tick_next.close:
                    tick_index_list.append(index+1)
            else:
                if tick_next.close > tick.close and index != 0:
                    if comp_value > tick.close:
                        comp_value = tick.close
                        tick_index_list.append(index)
                if index == self.length - 2 and comp_value > tick_next.close:
                    tick_index_list.append(index + 1)
        return tick_index_list


class FibonacciWaveController:
    def __init__(self):
        self.success_wave_list = []

    def process_tick_list(self):
        for for_ascending_wave in [False]:
            global_min_max_range_tick_lists = \
                pattern_data_handler.pattern_data.get_global_min_max_range_tick_lists(for_ascending_wave)
            for tick_list in global_min_max_range_tick_lists:
                tree = FibonacciWaveTree(tick_list)
                component_len_lists = tree.get_component_len_lists(for_ascending_wave)
                for component_len_list in component_len_lists:
                    if for_ascending_wave:
                        wave = FibonacciAscendingWave(tick_list, component_len_list)
                    else:
                        wave = FibonacciDescendingWave(tick_list, component_len_list)
                    if wave.is_wave_fibonacci_wave():
                        print('Fibonacci Wave for: {}'.format(component_len_list))
                        wave.print()
                        self.success_wave_list.append(wave)
