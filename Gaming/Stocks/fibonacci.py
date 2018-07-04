"""
Description: This module contains the Fibonacci classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
from sertl_analytics.constants.pattern_constants import TT, DIR, FR, CN
from pattern_wave_tick import WaveTick
from pattern_data_container import pattern_data_handler as pdh
import math
from copy import deepcopy
from pattern_configuration import config


class FibonacciWaveComponent:
    def __init__(self, tick_start: WaveTick, tick_end: WaveTick, position_in_wave: int):
        self.position_in_wave = position_in_wave
        self.tick_start = tick_start
        self.tick_end = tick_end
        self.df = self.__get_df_for_range__()
        self._tick_list = []
        self.__fill_tick_list__()
        self.max = self.df[CN.HIGH].max()
        self.min = self.df[CN.LOW].min()

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

    def get_xy_parameter(self, is_for_ascending_wave: bool):
        pass


class FibonacciRegressionComponent(FibonacciWaveComponent):
    def __init__(self, tick_start: WaveTick, tick_end: WaveTick, position_in_wave: int):
        FibonacciWaveComponent.__init__(self, tick_start, tick_end, position_in_wave)
        self.regression_value_against_last_regression = 0
        self.regression_pct_against_last_regression = 0
        self.regression_pct_against_last_retracement = 0

    def is_component_internally_consistent(self):
        return True

    def is_component_wave_consistent(self):
        return self.position_in_wave == 1 or self.regression_pct_against_last_regression >= FR.R_500

    def is_a_regression_to(self, wave_compare: FibonacciWaveComponent):
        return self.max > wave_compare.max

    def is_regression_fibonacci_compliant(self):
        return self.position_in_wave == 1 or \
               FR.is_regression_pct_compliant(self.regression_pct_against_last_regression,
                                              config.fibonacci_tolerance_pct)

    def get_details(self):
        return '{: <12}: {} - {}: Regression against reg: {} ({:4.1f}%) - against retracement: {:4.1f}%'.\
            format('Regression', self.tick_start.date, self.tick_end.date,
                   self.regression_value_against_last_regression,
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
    def __init__(self, tick_start: WaveTick, tick_end: WaveTick, position_in_wave: int):
        FibonacciWaveComponent.__init__(self, tick_start, tick_end, position_in_wave)
        self.retracement_value = 0
        self.retracement_pct = 0

    def is_component_internally_consistent(self):
        return True

    def is_component_wave_consistent(self):
        return 0 < self.retracement_pct < 1

    def is_retracement_fibonacci_compliant(self):
        return FR.is_retracement_value_compliant(self.retracement_pct, config.fibonacci_tolerance_pct)

    def get_details(self):
        return '{: <12}: {} - {}: Retracement: {} ({:4.1f}%)'.format('Retracement', self.tick_start.date,
                                                                self.tick_end.date,
                                                                self.retracement_value,
                                                                self.retracement_pct * 100)

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
    def position_start(self):
        return self.get_component_by_number(1).position_start

    @property
    def position_end(self):
        return self.get_component_by_number(5).position_end

    def clone(self):
        return deepcopy(self)

    def is_wave_complete(self):
        return self.reg_comp_id_next == '' and self.ret_comp_id_next == ''

    def is_wave_ready_for_next_retracement(self, tick_next_local_min: WaveTick):
        wave_id = self.ret_comp_id_next
        return self.__is_tick_next_retracement__(tick_next_local_min) \
               and self.__are_all_components_filled_before_wave_id__(wave_id)

    def is_wave_ready_for_next_regression(self, tick_next_local_min: WaveTick):
        wave_id = self.reg_comp_id_next
        return self.__is_tick_next_regression__(tick_next_local_min) \
               and self.__are_all_components_filled_before_wave_id__(wave_id)

    def __are_all_components_filled_before_wave_id__(self, wave_id_next: str):
        for comp_id in self.comp_id_list:
            if comp_id == wave_id_next:
                return True
            if comp_id not in self.comp_dic:
                return False

    def __is_tick_next_regression__(self, tick: WaveTick) -> bool:
        pass

    def __is_tick_next_retracement__(self, tick: WaveTick) -> bool:
        pass

    def add_regression(self, tick_start: WaveTick, tick_end: WaveTick):
        comp_id = self.reg_comp_id_next
        self.comp_dic[comp_id] = FibonacciRegressionComponent(tick_start, tick_end, int(comp_id[-1]))
        self.__calculate_regression_values_for_component__(self.comp_dic[comp_id], comp_id)

    def add_retracement(self, tick_start: WaveTick, tick_end: WaveTick):
        comp_id = self.ret_comp_id_next
        self.comp_dic[comp_id] = FibonacciRetracementComponent(tick_start, tick_end, int(comp_id[-1]))
        self.__calculate_retracement_values_for_component__(self.comp_dic[comp_id], comp_id)

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
        for ret_comp in self.ret_comp_list:
            if not ret_comp.is_retracement_fibonacci_compliant():
                return False

        # 4. check if the regressions are fibonacci regressions
        for reg_comp in self.reg_comp_list:
            if not reg_comp.is_regression_fibonacci_compliant():
                return False

        return True

    def __calculate_retracement_values_for_component__(self, component: FibonacciWaveComponent, wave_id: str):
        pass

    def __calculate_regression_values_for_component__(self, component: FibonacciWaveComponent, wave_id: str):
       pass

    def __are_components_internally_consistent__(self):
        for wave_id in self.comp_id_list:
            if not self.comp_dic[wave_id].is_component_internally_consistent():
                return False
        return True

    def print(self):
        for wave_id in self.comp_id_list:
            print(self.comp_dic[wave_id].get_details())

    def get_xy_parameter(self):
        xy = []
        is_for_ascending_wave = self.__class__.__name__ == 'FibonacciAscendingWave'
        for index in range(0, 5):
            xy = xy + self.get_wave_component_by_index(index).get_xy_parameter(is_for_ascending_wave)
        return xy


class FibonacciAscendingWave(FibonacciWave):
    def __is_tick_next_regression__(self, tick: WaveTick) -> bool:
        return tick.high > self.max

    def __is_tick_next_retracement__(self, tick: WaveTick) -> bool:
        ret_min_list = [comp.min for comp in self.ret_comp_list]
        max_ret_min_list = -math.inf if len(ret_min_list) == 0 else max(ret_min_list)
        return tick.low > self.min and tick.low > max_ret_min_list

    def __calculate_regression_values_for_component__(self, reg_comp: FibonacciRegressionComponent, wave_id: str):
        index_wave_id = self.comp_id_list_reg.index(wave_id)
        if index_wave_id > 0:
            reg_comp_prev = self.comp_dic[self.comp_id_list_reg[index_wave_id - 1]]
            ret_comp_prev = self.comp_dic[self.comp_id_list_ret[index_wave_id - 1]]
            reg_comp.regression_value_against_last_regression = round(reg_comp.max - reg_comp_prev.max, 2)
            reg_comp.regression_pct_against_last_regression = round(reg_comp.range / reg_comp_prev.range, 3)
            reg_comp.regression_pct_against_last_retracement = round(reg_comp.range / ret_comp_prev.range, 3)

    def __calculate_retracement_values_for_component__(self, ret_comp: FibonacciRetracementComponent, wave_id: str):
        index_wave_id = self.comp_id_list_ret.index(wave_id)
        reg_comp = self.comp_dic[self.comp_id_list_reg[index_wave_id]]
        ret_comp.retracement_value = round(reg_comp.max - ret_comp.min, 2)
        ret_comp.retracement_pct = round(ret_comp.retracement_value / reg_comp.range, 3)


class FibonacciDescendingWave(FibonacciWave):
    def __is_tick_next_regression__(self, tick: WaveTick) -> bool:
        return tick.low < self.min

    def __is_tick_next_retracement__(self, tick: WaveTick) -> bool:
        ret_max_list = [comp.max for comp in self.ret_comp_list]
        min_ret_mat_list = math.inf if len(ret_max_list) == 0 else min(ret_max_list)
        return tick.high < self.max and tick.high < min_ret_mat_list

    def __calculate_regression_values_for_component__(self, reg_comp: FibonacciRegressionComponent, wave_id: str):
        index_wave_id = self.comp_id_list_reg.index(wave_id)
        if index_wave_id > 0:
            reg_comp_prev = self.comp_dic[self.comp_id_list_reg[index_wave_id - 1]]
            ret_comp_prev = self.comp_dic[self.comp_id_list_ret[index_wave_id - 1]]
            reg_comp.regression_value_against_last_regression = round(reg_comp_prev.min - reg_comp.min, 2)
            reg_comp.regression_value_against_last_retracement = round(ret_comp_prev.min - reg_comp.min, 2)
            reg_comp.regression_pct_against_last_regression = round(reg_comp.range / reg_comp_prev.range, 3)

    def __calculate_retracement_values_for_component__(self, ret_comp: FibonacciRetracementComponent, wave_id: str):
        index_wave_id = self.comp_id_list_ret.index(wave_id)
        reg_comp = self.comp_dic[self.comp_id_list_reg[index_wave_id]]
        ret_comp.retracement_value = round(ret_comp.max - reg_comp.min, 2)
        ret_comp.retracement_pct = round(ret_comp.retracement_value / reg_comp.range, 3)


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
            elif tick.is_local_min:
                self.min_tick_list.append(tick)
                self.__fill_min_possible_max_tick_dic__(index, tick)

    def __fill_max_possible_min_tick_dic__(self, index, tick):
        self.max_possible_min_tick_dic[tick.position] = []
        min_value = math.inf
        for index_min in range(index + 1, self.min_max_list_length):
            tick_min = self.min_max_tick_list[index_min]
            if tick_min.is_local_min and tick_min.low <= min_value:
                min_value = tick_min.low
                self.max_possible_min_tick_dic[tick.position].append(tick_min)

    def __fill_min_possible_max_tick_dic__(self, index, tick):
        self.min_possible_max_tick_dic[tick.position] = []
        max_value = -math.inf
        for index_max in range(index + 1, self.min_max_list_length):
            tick_max = self.min_max_tick_list[index_max]
            if tick_max.is_local_max and tick_max.high >= max_value:
                max_value = tick_max.high
                self.min_possible_max_tick_dic[tick.position].append(tick_max)

    def __add_next_reg_comp__(self, wave: FibonacciWave, comp_id: str, tick_previous: WaveTick):
        possible_next_tick_list = self.__get_possible_next_tick_dic__(tick_previous, wave, True)
        for tick_next in possible_next_tick_list:
            if wave.is_wave_ready_for_next_regression(tick_next):
                wave.add_regression(tick_previous, tick_next)
                if wave.is_wave_complete():
                    self.__process_completed_wave__(wave)
                else:
                    if wave.ret_comp_id_next != '':
                        self.__add_next_ret_comp__(wave, wave.ret_comp_id_next, tick_next)
                del wave.comp_dic[comp_id]

    def __add_next_ret_comp__(self, wave: FibonacciWave, comp_id: str, tick_previous: WaveTick):
        possible_next_tick_list = self.__get_possible_next_tick_dic__(tick_previous, wave, False)
        for tick_next in possible_next_tick_list:
            if wave.is_wave_ready_for_next_retracement(tick_next):
                wave.add_retracement(tick_previous, tick_next)
                if wave.reg_comp_id_next != '':
                    self.__add_next_reg_comp__(wave, wave.reg_comp_id_next, tick_next)
                del wave.comp_dic[comp_id]

    def __get_possible_next_tick_dic__(self, tick_previous, wave, for_regression: bool):
        try:
            if wave.__class__.__name__ == 'FibonacciDescendingWave':
                if for_regression:
                    return self.max_possible_min_tick_dic[tick_previous.position]
                else:
                    return self.min_possible_max_tick_dic[tick_previous.position]
            else:
                if for_regression:
                    return self.min_possible_max_tick_dic[tick_previous.position]
                else:
                    return self.max_possible_min_tick_dic[tick_previous.position]
        except:  # ToDo find error for 'DWDP': 'DuPont' - "Date BETWEEN '2017-09-01' AND '2019-01-01'"
            return []

    def __process_completed_wave__(self, wave):
        if wave.is_wave_fibonacci_wave():
            wave_clone = wave.clone()
            if wave.__class__.__name__ == 'FibonacciDescendingWave':
                self.fibonacci_descending_wave_list.append(wave_clone)
            else:
                self.fibonacci_ascending_wave_list.append(wave_clone)
            # wave.print()
