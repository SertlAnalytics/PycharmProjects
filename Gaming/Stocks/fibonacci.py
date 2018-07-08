"""
Description: This module contains the Fibonacci classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
from sertl_analytics.constants.pattern_constants import CN, FD, FR, fibonacci_helper, CM
from pattern_wave_tick import WaveTick
from pattern_data_container import pattern_data_handler as pdh
import math
from copy import deepcopy
from pattern_configuration import config


class FibonacciWaveComponent:
    def __init__(self, tick_start: WaveTick, tick_end: WaveTick, comp_id: str):
        self.comp_id = comp_id
        self.position_in_wave = int(self.comp_id[-1])
        self.tick_start = tick_start
        self.tick_end = tick_end
        self.df = self.__get_df_for_range__()
        self._tick_list = []
        self.__fill_tick_list__()
        self.max = round(self.df[CN.HIGH].max(), 2)
        self.min = round(self.df[CN.LOW].min(), 2)

    @property
    def position_start(self):
        return self.tick_start.position

    @property
    def position_end(self):
        return self.tick_end.position

    def __get_df_for_range__(self):
        df = pdh.pattern_data.df
        return df[np.logical_and(df[CN.POSITION] >= self.tick_start.position, df[CN.POSITION] <= self.tick_end.position)]

    def __fill_tick_list__(self):
        for index, row in self.df.iterrows():
            self._tick_list.append(WaveTick(row))

    @property
    def range_max(self):
        return round(self.max - self.min, 2)

    def get_end_to_end_range(self, direction: str) -> float:
        pass

    def is_component_consistent(self):
        return self.is_component_internally_consistent() and self.is_component_wave_consistent()

    def is_component_internally_consistent(self):
        pass

    def is_component_wave_consistent(self):
        pass

    def get_details(self):
        pass

    def get_xy_parameter(self, is_for_ascending_wave: bool):
        pass


class FibonacciRegressionComponent(FibonacciWaveComponent):
    def __init__(self, tick_start: WaveTick, tick_end: WaveTick, comp_id: str):
        FibonacciWaveComponent.__init__(self, tick_start, tick_end, comp_id)
        self.regression_pct_against_last_regression = 0
        self.regression_pct_against_last_retracement = 0

    def get_end_to_end_range(self, direction: str) -> float:
        if direction == FD.ASC:
            return round(self.tick_end.high - self.tick_start.low, 2)
        else:
            return round(self.tick_start.high - self.tick_end.low, 2)

    def get_regression_pct(self, comp: FibonacciWaveComponent, wave_type: str):
        range_comp = comp.get_end_to_end_range(wave_type)
        range_ret_comp = self.get_end_to_end_range(wave_type)
        return round(range_ret_comp / range_comp, 3)

    def is_component_internally_consistent(self):
        return True

    def is_component_wave_consistent(self):
        return self.position_in_wave == 1 or self.regression_pct_against_last_regression >= FR.R_236

    def is_a_regression_to(self, wave_compare: FibonacciWaveComponent):
        return self.max > wave_compare.max

    def is_regression_fibonacci_compliant(self):
        return self.position_in_wave == 1 or \
               fibonacci_helper.is_value_a_fibonacci_relation(
                   self.regression_pct_against_last_regression, config.fibonacci_tolerance_pct)

    def get_details(self):
        return '{: <12}: {} - {}: Regression against reg: {:4.1f}% - against retracement: {:4.1f}%'.\
            format('Regression', self.tick_start.date, self.tick_end.date,
                   self.regression_pct_against_last_regression * 100,
                   self.regression_pct_against_last_retracement)

    def get_xy_parameter(self, is_for_ascending_wave: bool):
        if self.position_in_wave == 1:
            x = [self.tick_start.f_var, self.tick_end.f_var]
            y = [self.tick_start.low, self.tick_end.high] if is_for_ascending_wave \
                else [self.tick_start.high, self.tick_end.low]
        else:
            x = [self.tick_end.f_var]
            y = [self.tick_end.high] if is_for_ascending_wave else [self.tick_end.low]
        xy = list(zip(x, y))
        return xy


class FibonacciRetracementComponent(FibonacciWaveComponent):
    def __init__(self, tick_start: WaveTick, tick_end: WaveTick, comp_id: str):
        FibonacciWaveComponent.__init__(self, tick_start, tick_end, comp_id)
        self.retracement_value = 0
        self.retracement_pct = 0

    def get_end_to_end_range(self, wave_type: str) -> float:
        if wave_type == FD.ASC:
            return round(self.tick_start.high - self.tick_end.low, 2)
        else:
            return round(self.tick_end.high - self.tick_start.low, 2)

    def get_retracement_value(self, reg_comp: FibonacciRegressionComponent, wave_type: str):
        if wave_type == FD.ASC:
            return round(reg_comp.tick_end.high - self.tick_end.low, 2)
        else:
            return round(reg_comp.tick_end.low - self.tick_end.high, 2)

    def get_retracement_pct(self, reg_comp: FibonacciRegressionComponent, wave_type: str):
        range_reg_comp = reg_comp.get_end_to_end_range(wave_type)
        range_ret_comp = self.get_end_to_end_range(wave_type)
        return round(range_ret_comp/range_reg_comp, 3)

    def is_component_internally_consistent(self):
        return True

    def is_component_wave_consistent(self):
        return 0 < self.retracement_pct < 1

    def is_retracement_fibonacci_compliant(self):
        return fibonacci_helper.is_value_a_fibonacci_relation(self.retracement_pct, config.fibonacci_tolerance_pct)

    def get_details(self):
        return '{: <12}: {} - {}: Retracement: {} ({:4.1f}%)'.format(
            'Retracement', self.tick_start.date, self.tick_end.date, self.retracement_value, self.retracement_pct * 100)

    def get_xy_parameter(self, is_for_ascending_wave: bool):
        x = [self.tick_end.f_var]
        y = [self.tick_end.low] if is_for_ascending_wave else [self.tick_end.high]
        xy = list(zip(x, y))
        return xy


class FibonacciWave:
    comp_id_list_reg = ['w_1', 'w_3', 'w_5']
    comp_id_list_ret = ['w_2', 'w_4']
    comp_id_list = ['w_1', 'w_2', 'w_3', 'w_4', 'w_5']

    def __init__(self):
        self.comp_dic = {}

    @property
    def wave_type(self):
        return FD.NONE

    @property
    def max(self):
        return max([comp.max for comp in self.comp_dic.values()]) if len(self.comp_dic) > 0 else -math.inf

    @property
    def min(self):
        return min([comp.min for comp in self.comp_dic.values()]) if len(self.comp_dic) > 0 else math.inf

    @property
    def reg_comp_id_next(self):
        for comp_id in self.comp_id_list_reg:
            if comp_id not in self.comp_dic:
                return comp_id
        return ''

    @property
    def ret_comp_id_next(self):
        for comp_id in self.comp_id_list_ret:
            if comp_id not in self.comp_dic:
                return comp_id
        return ''

    @property
    def position_list(self) -> list:
        return_list = []
        for comp_id in self.comp_id_list:
            if comp_id in self.comp_dic:
                comp = self.comp_dic[comp_id]
                return_list.append(comp.tick_start.position)
                if comp.position_in_wave == 5:
                    return_list.append(comp.tick_end.position)
            else:
                return_list.append(0)
        return return_list

    @property
    def date_list(self) -> list:
        return_list = []
        for comp_id in self.comp_id_list:
            if comp_id in self.comp_dic:
                comp = self.comp_dic[comp_id]
                if comp.position_in_wave == 1:
                    return_list.append(comp.tick_start.date_str)
                return_list.append(comp.tick_end.date_str)
            else:
                return_list.append('')
        return return_list

    @property
    def reg_ret_list(self) -> list:
        return_list = []
        for comp_id in self.comp_id_list:
            if comp_id in self.comp_dic:
                comp = self.comp_dic[comp_id]
                if comp_id in self.comp_id_list_ret:
                    return_list.append(comp.retracement_pct)
                elif comp_id in self.comp_id_list_reg:
                    return_list.append(comp.regression_pct_against_last_regression)
            else:
                return_list.append(0)
        return [round(100 * value, 1) for value in return_list]

    @property
    def value_list(self) -> list:
        return []

    @property
    def position_start(self):
        return self.position_list[0]

    @property
    def position_end(self):
        return self.position_list[-1]

    def clone(self):
        return deepcopy(self)

    def get_coverage_mode(self, wave_later) -> str:
        count_difference = 0
        difference_at_index = 0
        position_list_later = wave_later.position_list
        for index, position in enumerate(self.position_list):
            difference = position_list_later[index] - position
            if difference != 0:
                difference_at_index = difference
                count_difference += 1
                if count_difference > 1:
                    return ''
        if difference_at_index > 6:
            return CM.COVERED_BY # take the current wave since there is long component development
        else:
            return CM.COVERING

    def is_wave_complete(self):
        return len(self.comp_dic) == len(self.comp_id_list)

    def is_wave_ready_for_next_retracement(self, tick_next: WaveTick, ret_comp_id_next: str):
        is_next_tick_retracement = self.__is_tick_next_retracement__(tick_next, ret_comp_id_next)
        are_all_previous_components_available = self.__are_all_components_filled_before_wave_id__(ret_comp_id_next)
        return is_next_tick_retracement and are_all_previous_components_available

    def can_retracement_component_be_added(self, ret_comp: FibonacciRetracementComponent) -> bool:
        pass

    def is_wave_ready_for_next_regression(self, tick_next: WaveTick, reg_comp_id_next: str):
        is_next_tick_regression = self.__is_tick_next_regression__(tick_next, reg_comp_id_next)
        are_all_previous_components_available = self.__are_all_components_filled_before_wave_id__(reg_comp_id_next)
        return is_next_tick_regression and are_all_previous_components_available

    def can_regression_component_be_added(self, reg_comp: FibonacciRegressionComponent) -> bool:
        pass

    def __are_all_components_filled_before_wave_id__(self, wave_id_next: str):
        for comp_id in self.comp_id_list:
            if comp_id == wave_id_next:
                return True
            if comp_id not in self.comp_dic:
                return False

    def __is_tick_next_regression__(self, tick: WaveTick, reg_comp_id_next: str) -> bool:
        pass

    def __is_tick_next_retracement__(self, tick: WaveTick, ret_comp_id_next: str) -> bool:
        pass

    def add_regression(self, reg_comp: FibonacciRegressionComponent):
        self.comp_dic[reg_comp.comp_id] = reg_comp
        self.__calculate_regression_values_for_component__(reg_comp)

    def add_retracement(self, ret_comp: FibonacciRetracementComponent):
        self.comp_dic[ret_comp.comp_id] = ret_comp
        self.__calculate_retracement_values_for_component__(ret_comp)

    @property
    def arg_str(self):
        return self.__get_arg_str__()

    @property
    def reg_comp_list(self):
        comp_list = []
        for comp_id in self.comp_id_list_reg:
            if comp_id in self.comp_dic:
                comp_list.append(self.comp_dic[comp_id])
        return comp_list

    @property
    def ret_comp_list(self):
        comp_list = []
        for comp_id in self.comp_id_list_ret:
            if comp_id in self.comp_dic:
                comp_list.append(self.comp_dic[comp_id])
        return comp_list

    def get_wave_component_by_index(self, index: int):
        return self.comp_dic[self.comp_id_list[index]]

    def get_component_by_number(self, number: int):
        return self.comp_dic[self.comp_id_list[number - 1]]

    def __get_arg_str__(self):
        return 'Start_End: {} - {}'.format(self.position_start, self.position_end)

    def is_wave_fibonacci_wave(self):
        # 1. check if the components are internally consistent
        internal_ok = self.__are_components_internally_consistent__()
        if not internal_ok:
            return False

        # 2. check if each retracement component is a retracement
        for ret_comp in self.ret_comp_list:
            if ret_comp.retracement_pct == 0:
                return False

        # 3. check if the retracements are fibonacci retracements
        # for ret_comp in self.ret_comp_list:
        #     if not ret_comp.is_retracement_fibonacci_compliant():
        #         return False

        # 4. check if the regressions are fibonacci regressions
        # for reg_comp in self.reg_comp_list:
        #     if not reg_comp.is_regression_fibonacci_compliant():
        #         return False

        # 5. verify that the middle regression is not the smallest one
        reg_range_list = [comp.range_max for comp in self.reg_comp_list]
        if np.argmin(reg_range_list) == 1:
            return False

        return True

    def calculate_regression_values_for_component(self, component: FibonacciWaveComponent):
        self.__calculate_regression_values_for_component__(component)

    def calculate_retracement_values_for_component(self, component: FibonacciWaveComponent):
        self.__calculate_retracement_values_for_component__(component)

    def __calculate_retracement_values_for_component__(self, component: FibonacciWaveComponent):
        pass

    def __calculate_regression_values_for_component__(self, component: FibonacciWaveComponent):
        pass

    def __are_components_internally_consistent__(self):
        for wave_id in self.comp_id_list:
            if not self.comp_dic[wave_id].is_component_internally_consistent():
                return False
        return True

    def print_detailed(self):
        for wave_id in self.comp_id_list:
            print(self.comp_dic[wave_id].get_details())

    def get_annotation_details(self):
        ret_reg_list = self.reg_ret_list
        return '{:<12}: {:=5.1f}% / {:=5.1f}%\n{:<12}: {:=5.1f}% / {:=5.1f}%\n{}: {}'.format(
            'Retracements', ret_reg_list[1], ret_reg_list[3],
            'Regressions', ret_reg_list[2], ret_reg_list[4],
            'Positions', self.position_list)

    def print(self, suffix: str = ''):
        dates = self.date_list
        positions = self.position_list
        ret_reg_list = self.reg_ret_list
        print('{}{}: {} - {} ({}): R_1={:=5.1f}%, P_1={:=5.1f}%, R_2={:=5.1f}%, P_2={:=5.1f}%'.format(
            '' if suffix == '' else suffix + ': ', self.wave_type, dates[0], dates[1], positions,
            ret_reg_list[1], ret_reg_list[2], ret_reg_list[3], ret_reg_list[4]))

    def get_xy_parameter(self):
        xy = []
        is_for_ascending_wave = self.wave_type == FD.ASC
        for index in range(0, 5):
            xy = xy + self.get_wave_component_by_index(index).get_xy_parameter(is_for_ascending_wave)
        return xy


class FibonacciAscendingWave(FibonacciWave):
    @property
    def wave_type(self):
        return FD.ASC

    @property
    def value_list(self) -> list:
        return_list = []
        for comp_id in self.comp_id_list:
            if comp_id in self.comp_dic:
                comp = self.comp_dic[comp_id]
                if comp_id in self.comp_id_list_ret:
                    return_list.append(comp.tick_end.low)
                elif comp_id in self.comp_id_list_reg:
                    if comp.position_in_wave == 1:
                        return_list.append(comp.tick_start.low)
                    return_list.append(comp.tick_end.high)
            else:
                return_list.append(0)
        return return_list

    def __is_tick_next_regression__(self, tick: WaveTick, reg_comp_id_next: str) -> bool:
        return tick.high > self.max and (reg_comp_id_next != 'w_5' or tick.is_global_max)

    def can_regression_component_be_added(self, reg_comp: FibonacciRegressionComponent) -> bool:
        return reg_comp.tick_start.low <= reg_comp.min and reg_comp.tick_end.high >= reg_comp.max

    def __is_tick_next_retracement__(self, tick: WaveTick, ret_comp_id_next: str) -> bool:
        ret_min_list = [comp.min for comp in self.ret_comp_list]
        max_ret_min_list = -math.inf if len(ret_min_list) == 0 else max(ret_min_list)
        return tick.low > self.min and tick.low > max_ret_min_list

    def can_retracement_component_be_added(self, ret_comp: FibonacciRetracementComponent) -> bool:
        return ret_comp.tick_start.high >= ret_comp.max and ret_comp.tick_end.low <= ret_comp.min \
               and ret_comp.retracement_pct < FR.R_764

    def __calculate_regression_values_for_component__(self, reg_comp: FibonacciRegressionComponent):
        index_comp_id = self.comp_id_list_reg.index(reg_comp.comp_id)
        if index_comp_id > 0:
            reg_comp_prev = self.comp_dic[self.comp_id_list_reg[index_comp_id - 1]]
            ret_comp_prev = self.comp_dic[self.comp_id_list_ret[index_comp_id - 1]]
            reg_comp.regression_pct_against_last_regression = reg_comp.get_regression_pct(reg_comp_prev, self.wave_type)
            reg_comp.regression_pct_against_last_retracement = reg_comp.get_regression_pct(ret_comp_prev, self.wave_type)

    def __calculate_retracement_values_for_component__(self, ret_comp: FibonacciRetracementComponent):
        index_wave_id = self.comp_id_list_ret.index(ret_comp.comp_id)
        reg_comp = self.comp_dic[self.comp_id_list_reg[index_wave_id]]
        ret_comp.retracement_value = ret_comp.get_retracement_value(reg_comp, self.wave_type)
        ret_comp.retracement_pct = ret_comp.get_retracement_pct(reg_comp, self.wave_type)


class FibonacciDescendingWave(FibonacciWave):
    @property
    def wave_type(self):
        return FD.DESC

    @property
    def value_list(self) -> list:
        return_list = []
        for comp_id in self.comp_id_list:
            if comp_id in self.comp_dic:
                comp = self.comp_dic[comp_id]
                if comp_id in self.comp_id_list_ret:
                    return_list.append(comp.tick_end.high)
                elif comp_id in self.comp_id_list_reg:
                    if comp.position_in_wave == 1:
                        return_list.append(comp.tick_start.high)
                    return_list.append(comp.tick_end.low)
            else:
                return_list.append(0)
        return return_list

    def __is_tick_next_regression__(self, tick: WaveTick, reg_comp_id_next: str) -> bool:
        return tick.low < self.min and (reg_comp_id_next != 'w_5' or tick.is_global_min)

    def can_regression_component_be_added(self, reg_comp: FibonacciRegressionComponent) -> bool:
        return reg_comp.tick_start.high >= reg_comp.max and reg_comp.tick_end.low <= reg_comp.min

    def __is_tick_next_retracement__(self, tick: WaveTick, ret_comp_id_next: str) -> bool:
        ret_max_list = [comp.max for comp in self.ret_comp_list]
        min_ret_mat_list = math.inf if len(ret_max_list) == 0 else min(ret_max_list)
        return tick.high < self.max and tick.high < min_ret_mat_list

    def can_retracement_component_be_added(self, ret_comp: FibonacciRetracementComponent) -> bool:
        return ret_comp.tick_start.low <= ret_comp.min and ret_comp.retracement_pct < FR.R_764
        # and ret_comp.tick_end.high >= ret_comp.max

    def __calculate_regression_values_for_component__(self, reg_comp: FibonacciRegressionComponent):
        index_comp_id = self.comp_id_list_reg.index(reg_comp.comp_id)
        if index_comp_id > 0:
            reg_comp_prev = self.comp_dic[self.comp_id_list_reg[index_comp_id - 1]]
            ret_comp_prev = self.comp_dic[self.comp_id_list_ret[index_comp_id - 1]]
            reg_comp.regression_value_against_last_regression = round(reg_comp_prev.min - reg_comp.min, 2)
            reg_comp.regression_value_against_last_retracement = round(ret_comp_prev.min - reg_comp.min, 2)
            reg_comp.regression_pct_against_last_regression = round(reg_comp.get_end_to_end_range(self.wave_type)
                                                    / reg_comp_prev.get_end_to_end_range(self.wave_type), 3)

    def __calculate_retracement_values_for_component__(self, ret_comp: FibonacciRetracementComponent):
        index_wave_id = self.comp_id_list_ret.index(ret_comp.comp_id)
        reg_comp = self.comp_dic[self.comp_id_list_reg[index_wave_id]]
        ret_comp.retracement_value = ret_comp.get_retracement_value(reg_comp, self.wave_type)
        ret_comp.retracement_pct = ret_comp.get_retracement_pct(reg_comp, self.wave_type)


class FibonacciWaveTree:
    def __init__(self):
        self.min_max_tick_list = pdh.pattern_data.wave_tick_list_min_max.tick_list
        self.min_max_list_length = len(self.min_max_tick_list)
        self.min_tick_list = []
        self.max_tick_list = []
        self.min_possible_max_tick_dic = {}
        self.max_possible_min_tick_dic = {}
        self.__fill_lists_and_dictionaries_dics__()
        self.fibonacci_ascending_wave_list = []
        self.fibonacci_descending_wave_list = []
        self.min_list_length = len(self.min_tick_list)
        self.max_list_length = len(self.max_tick_list)

    def parse_tree(self):
        self.__parse_for_ascending_waves__()
        self.__parse_for_descending_waves__()

    def __parse_for_descending_waves__(self):
        for tick_max in self.max_tick_list:
            if tick_max.is_global_max:
                wave = FibonacciDescendingWave()
                self.__add_next_reg_comp__(wave, wave.reg_comp_id_next, tick_max)

    def __parse_for_ascending_waves__(self):
        for tick_min in self.min_tick_list:
            if tick_min.is_global_min:
                wave = FibonacciAscendingWave()
                self.__add_next_reg_comp__(wave, wave.reg_comp_id_next, tick_min)

    def __fill_lists_and_dictionaries_dics__(self):
        """
        Fills two dictionaries which contain only the possible min/max ticks for the next fibonacci component
        """
        for index, tick in enumerate(self.min_max_tick_list):
            if tick.is_local_max:
                self.max_tick_list.append(tick)
                self.__fill_max_possible_min_tick_dic__(index, tick)
            if tick.is_local_min:
                self.min_tick_list.append(tick)
                self.__fill_min_possible_max_tick_dic__(index, tick)

    def __fill_max_possible_min_tick_dic__(self, index: int, tick_max: WaveTick):
        self.max_possible_min_tick_dic[tick_max.position] = []
        min_array = np.array([tick_max.low])
        for index_min in range(index + 1, self.min_max_list_length):
            tick_min = self.min_max_tick_list[index_min]
            if tick_min.is_local_min and tick_min.low <= min_array.mean():
                min_array = np.append(min_array, np.array([tick_min.low]))
                self.max_possible_min_tick_dic[tick_max.position].append(tick_min)

    def __fill_min_possible_max_tick_dic__(self, index: int, tick_min: WaveTick):
        self.min_possible_max_tick_dic[tick_min.position] = []
        max_array = np.array([tick_min.high])
        for index_max in range(index + 1, self.min_max_list_length):
            tick_max = self.min_max_tick_list[index_max]
            if tick_max.is_local_max and tick_max.high >= max_array.mean():
                max_array = np.append(max_array, np.array([tick_max.high]))
                self.min_possible_max_tick_dic[tick_min.position].append(tick_max)

    def __add_next_reg_comp__(self, wave: FibonacciWave, reg_comp_id_next: str, tick_previous: WaveTick):
        possible_next_tick_list = self.__get_possible_next_tick_dic__(tick_previous, wave, True)
        for tick_next in possible_next_tick_list:
            if wave.is_wave_ready_for_next_regression(tick_next, reg_comp_id_next):
                reg_comp = FibonacciRegressionComponent(tick_previous, tick_next, reg_comp_id_next)
                wave.calculate_regression_values_for_component(reg_comp)
                if wave.can_regression_component_be_added(reg_comp):
                    wave.add_regression(reg_comp)
                    if wave.is_wave_complete():
                        self.__process_completed_wave__(wave)
                    else:
                        if wave.ret_comp_id_next != '':
                            self.__add_next_ret_comp__(wave, wave.ret_comp_id_next, tick_next)
                    del wave.comp_dic[reg_comp_id_next]

    def __add_next_ret_comp__(self, wave: FibonacciWave, ret_comp_id_next: str, tick_previous: WaveTick):
        possible_next_tick_list = self.__get_possible_next_tick_dic__(tick_previous, wave, False)
        for tick_next in possible_next_tick_list:
            if wave.is_wave_ready_for_next_retracement(tick_next, ret_comp_id_next):
                ret_comp = FibonacciRetracementComponent(tick_previous, tick_next, ret_comp_id_next)
                wave.calculate_retracement_values_for_component(ret_comp)
                if wave.can_retracement_component_be_added(ret_comp):
                    wave.add_retracement(ret_comp)
                    if wave.reg_comp_id_next != '':
                        self.__add_next_reg_comp__(wave, wave.reg_comp_id_next, tick_next)
                    del wave.comp_dic[ret_comp_id_next]

    def __get_possible_next_tick_dic__(self, tick_previous, wave, for_regression: bool):
        if wave.wave_type == FD.DESC:
            if for_regression:
                return self.max_possible_min_tick_dic[tick_previous.position]
            else:
                return self.min_possible_max_tick_dic[tick_previous.position]
        else:
            if for_regression:
                return self.min_possible_max_tick_dic[tick_previous.position]
            else:
                return self.max_possible_min_tick_dic[tick_previous.position]

    def __process_completed_wave__(self, wave: FibonacciWave):
        if wave.is_wave_fibonacci_wave():
            wave_clone = wave.clone()
            if wave.wave_type == FD.DESC:
                self.__add_wave_after_check_to_list__(self.fibonacci_descending_wave_list, wave_clone)
            else:
                self.__add_wave_after_check_to_list__(self.fibonacci_ascending_wave_list, wave_clone)

    @staticmethod
    def __add_wave_after_check_to_list__(wave_list: list, wave: FibonacciWave):
        is_covered_by_list = False
        replacing_index = -1
        for index, wave_in_list in enumerate(wave_list):
            coverage_mode = wave_in_list.get_coverage_mode(wave)
            if coverage_mode == CM.COVERING:
                is_covered_by_list = True
                break
            elif coverage_mode == CM.COVERED_BY:
                replacing_index = index
                break

        if not is_covered_by_list:
            if replacing_index == -1:
                wave_list.append(wave)
                if config.fibonacci_detail_print:
                    wave.print('added...')
            else:
                wave_list[replacing_index] = wave
                if config.fibonacci_detail_print:
                    wave.print('replacing...')

