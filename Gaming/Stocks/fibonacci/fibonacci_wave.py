"""
Description: This module contains the Fibonacci wave classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
from sertl_analytics.constants.pattern_constants import FD, FR, CM
from fibonacci.fibonacci_wave_component import FibonacciWaveComponent, FibonacciRegressionComponent, \
    FibonacciRetracementComponent
from fibonacci.fibonacci_wave_component import FibonacciAscendingRegressionComponent
from fibonacci.fibonacci_wave_component import FibonacciDescendingRegressionComponent
from fibonacci.fibonacci_wave_component import FibonacciAscendingRetracementComponent
from fibonacci.fibonacci_wave_component import FibonacciDescendingRetracementComponent
from fibonacci.fibonacci_helper import fibonacci_helper, FibonacciHelperApi
from pattern_wave_tick import WaveTick
import math
from copy import deepcopy


class FibonacciWave:
    comp_id_list_reg = ['w_1', 'w_3', 'w_5']
    comp_id_list_ret = ['w_2', 'w_4']
    comp_id_list = ['w_1', 'w_2', 'w_3', 'w_4', 'w_5']

    def __init__(self, tick_distance: float):
        self.tick_distance = tick_distance
        self.comp_dic = {}
        self.comp_forecast_parameter_list = []
        self.forecast_value_list = []

    @property
    def w_1(self):
        return self.get_component_by_number(1)

    @property
    def w_4(self):
        return self.get_component_by_number(4)

    @property
    def w_5(self):
        return self.get_component_by_number(5)

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
    def comp_position_list(self) -> list:
        return self.__get_values_for_components__('Position')

    @property
    def comp_date_list(self) -> list:
        return self.__get_values_for_components__('Date')

    @property
    def comp_reg_ret_percent_list(self) -> list:
        return [round(100 * value, 1) for value in self.comp_reg_ret_pct_list]

    @property
    def comp_reg_ret_pct_list(self) -> list:
        return self.__get_values_for_components__('reg_ret_pct')

    @property
    def comp_reg_ret_value_list(self) -> list:
        return self.__get_values_for_components__('reg_ret_value')

    @property
    def comp_duration_list(self) -> list:
        return self.__get_values_for_components__('Duration')

    @property
    def comp_position_key_4(self):
        return self.__get_comp_position_key__(4)

    @property
    def comp_position_key_5(self):
        return self.__get_comp_position_key__(5)

    def __get_comp_position_key__(self, elements: int):
        part_list = self.comp_position_list[:elements]
        return '-'.join(map(str, part_list))

    def __get_values_for_components__(self, value_type: str) -> list:
        return_list = []
        for comp_id in self.comp_id_list:
            if comp_id in self.comp_dic:
                comp = self.comp_dic[comp_id]
                if value_type == 'Position':
                    if comp.position_in_wave == 1:
                        return_list.append(comp.tick_start.position)
                    return_list.append(comp.tick_end.position)
                elif value_type == 'Date':
                    if comp.position_in_wave == 1:
                        return_list.append(comp.tick_start.date_str)
                    return_list.append(comp.tick_end.date_str)
                elif value_type == 'reg_ret_pct':
                    if comp_id in self.comp_id_list_ret:
                        return_list.append(comp.retracement_pct)
                    elif comp_id in self.comp_id_list_reg:
                        return_list.append(comp.regression_pct_against_last_regression)
                elif value_type == 'reg_ret_value':
                    return_list.append(abs(comp.get_end_to_end_range()))
                elif value_type == 'Duration':
                    return_list.append(comp.duration)
            else:
                if value_type == 'Date':
                    return_list.append('')
                else:
                    return_list.append(0)
        if value_type == 'reg_ret_pct':
            return [round(value, 3) for value in return_list]
        elif value_type == 'reg_ret_value':
            return [round(value, 2) for value in return_list]
        else:
            return return_list

    @property
    def position_start(self):
        return self.comp_position_list[0]

    @property
    def position_end(self):
        return self.comp_position_list[-1]

    def clone(self):
        return deepcopy(self)

    def get_component_by_number(self, number: int):
        return self.__get_wave_component_by_index__(number - 1)

    def __get_wave_component_by_index__(self, index: int):
        return self.comp_dic[self.comp_id_list[index]] if self.comp_id_list[index] in self.comp_dic else None

    def get_coverage_mode(self, wave_later) -> str:
        count_difference = 0
        difference_at_index = 0
        position_list_later = wave_later.comp_position_list
        for index, position in enumerate(self.comp_position_list):
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

    def add_retracement(self, ret_comp: FibonacciRetracementComponent):
        self.comp_dic[ret_comp.comp_id] = ret_comp
        if ret_comp.comp_id == 'w_4':
            if self.is_wave_fibonacci_wave(True):
                self.__fill_comp_forecast_parameter_list__()

    def __fill_comp_forecast_parameter_list__(self):
        comp_previous = self.comp_dic['w_4']
        api = FibonacciHelperApi(self.wave_type, comp_previous.tick_end)
        api.comp_reg_ret_pct_list = self.comp_reg_ret_pct_list
        api.comp_reg_ret_value_list = self.comp_reg_ret_value_list
        api.comp_duration_list = self.comp_duration_list

        forecast_parameter_list = fibonacci_helper.get_forecast_candidate_list(api)
        for entry in forecast_parameter_list:
            value = entry[1]
            if self.wave_type == FD.ASC and value > comp_previous.max * 0.98:
                self.comp_forecast_parameter_list.append(entry)
            elif self.wave_type == FD.DESC and value < comp_previous.min * 1.02:
                self.comp_forecast_parameter_list.append(entry)

    def is_wave_fibonacci_wave(self, for_forecast = False):
        # 1. check if the components are internally consistent
        internal_ok = self.__are_components_internally_consistent__()
        if not internal_ok:
            return False

        # 2. check if each retracement component is a retracement
        for ret_comp in self.ret_comp_list:
            if ret_comp.retracement_pct == 0:
                return False

        # 3. check if the retracements are fibonacci retracements
        if self.__get_number_of_fibonacci_compliant_retracements__(0.1) < 1:
                return False

        # 4. check if the regressions are fibonacci regressions - the FIRST regression is always compliant !!!
        if self.__get_number_of_fibonacci_compliant_regressions__(0.05 if for_forecast else 0.1) < 2:
                return False

        if not for_forecast:  # 5. verify that the middle regression is not the smallest one
            reg_range_list = [comp.range_max for comp in self.reg_comp_list]
            if np.argmin(reg_range_list) == 1:
                return False

        return True

    def __get_number_of_fibonacci_compliant_retracements__(self, tolerance_pct: float = 0.2) -> int:
        counter = 0
        for ret_comp in self.ret_comp_list:
            if ret_comp.is_retracement_fibonacci_compliant(tolerance_pct):
                counter += 1
        return counter

    def __get_number_of_fibonacci_compliant_regressions__(self, tolerance_pct: float = 0.2) -> int:
        counter = 0
        for reg_comp in self.reg_comp_list:
            if reg_comp.is_regression_fibonacci_compliant(tolerance_pct):
                counter += 1
        return counter

    def calculate_regression_values_for_component(self, component: FibonacciWaveComponent):
        self.__calculate_regression_values_for_component__(component)

    def calculate_retracement_values_for_component(self, component: FibonacciWaveComponent):
        self.__calculate_retracement_values_for_component__(component)

    def __calculate_retracement_values_for_component__(self, component: FibonacciWaveComponent):
        pass

    def __calculate_regression_values_for_component__(self, component: FibonacciWaveComponent):
        pass

    def __are_components_internally_consistent__(self):
        for wave in self.comp_dic.values():
            if not wave.is_component_internally_consistent():
                return False
        return True

    def print_detailed(self):
        for wave_id in self.comp_id_list:
            print(self.comp_dic[wave_id].get_details())

    def get_annotation_details(self):
        ret_reg_list = self.comp_reg_ret_pct_list
        return '{:<12}: {:=5.1f}% / {:=5.1f}%\n{:<12}: {:=5.1f}% / {:=5.1f}%\n{}: {}'.format(
            'Retracements', ret_reg_list[1], ret_reg_list[3],
            'Regressions', ret_reg_list[2], ret_reg_list[4],
            'Positions', self.comp_position_list)

    def print(self, suffix: str = ''):
        dates = self.comp_date_list
        positions = self.comp_position_list
        ret_reg_list = [round(value * 100, 1) for value in self.comp_reg_ret_pct_list]
        print('{}{}: {} - {} ({}): R_1={:=5.1f}%, P_1={:=5.1f}%, R_2={:=5.1f}%, P_2={:=5.1f}%'.format(
            '' if suffix == '' else suffix + ': ', self.wave_type, dates[0], dates[-1], positions,
            ret_reg_list[1], ret_reg_list[2], ret_reg_list[3], ret_reg_list[4]))

    def get_xy_parameter(self):
        if len(self.forecast_value_list) == 0:
            return self.__get_xy_parameter_for_wave__(5)
        else:
            return self.__get_xy_parameter_for_forecast_wave__()

    def __get_xy_parameter_for_wave__(self, components: int):
        xy = []
        for index in range(0, components):
            xy = xy + self.__get_wave_component_by_index__(index).get_xy_parameter()
        return xy

    def __get_xy_parameter_for_forecast_wave__(self):
        xy = self.__get_xy_parameter_for_wave__(4)
        forecast_values = np.array(sorted(self.forecast_value_list))
        value_list = [forecast_values.min(), forecast_values.mean(), forecast_values.max()]
        if self.wave_type == FD.DESC:
            value_list = sorted(value_list, reverse=True)
        for index, values in enumerate(value_list):
            xy = xy + [(self.comp_dic['w_5'].tick_start.f_var, values)]
            len_horizontal_line =  2 * self.tick_distance if index == 1 else 3 * self.tick_distance
            xy = xy + [(self.comp_dic['w_5'].tick_start.f_var + len_horizontal_line, values)]
            xy = xy + [(self.comp_dic['w_5'].tick_start.f_var, values)]
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

    def can_regression_component_be_added(self, reg_comp: FibonacciAscendingRegressionComponent) -> bool:
        return reg_comp.tick_start.position == reg_comp.idx_min and reg_comp.tick_end.position == reg_comp.idx_max

    def __is_tick_next_retracement__(self, tick: WaveTick, ret_comp_id_next: str) -> bool:
        ret_min_list = [comp.min for comp in self.ret_comp_list]
        max_ret_min_list = -math.inf if len(ret_min_list) == 0 else max(ret_min_list)
        return tick.low > self.min and tick.low > max_ret_min_list

    def can_retracement_component_be_added(self, ret_comp: FibonacciAscendingRetracementComponent) -> bool:
        return ret_comp.tick_end.position == ret_comp.idx_min and ret_comp.retracement_pct < FR.R_764 + 0.1

    def __calculate_regression_values_for_component__(self, reg_comp: FibonacciAscendingRegressionComponent):
        index_comp_id = self.comp_id_list_reg.index(reg_comp.comp_id)
        if index_comp_id > 0:
            reg_comp_prev = self.comp_dic[self.comp_id_list_reg[index_comp_id - 1]]
            ret_comp_prev = self.comp_dic[self.comp_id_list_ret[index_comp_id - 1]]
            reg_comp.regression_pct_against_last_regression = reg_comp.get_regression_pct(reg_comp_prev)
            reg_comp.regression_pct_against_last_retracement = reg_comp.get_regression_pct(ret_comp_prev)

    def __calculate_retracement_values_for_component__(self, ret_comp: FibonacciAscendingRetracementComponent):
        index_wave_id = self.comp_id_list_ret.index(ret_comp.comp_id)
        reg_comp = self.comp_dic[self.comp_id_list_reg[index_wave_id]]
        ret_comp.retracement_value = ret_comp.get_retracement_value(reg_comp)
        ret_comp.retracement_pct = ret_comp.get_retracement_pct(reg_comp)


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

    def can_regression_component_be_added(self, reg_comp: FibonacciDescendingRegressionComponent) -> bool:
        return reg_comp.tick_start.position == reg_comp.idx_max and reg_comp.tick_end.position == reg_comp.idx_min

    def __is_tick_next_retracement__(self, tick: WaveTick, ret_comp_id_next: str) -> bool:
        ret_max_list = [comp.max for comp in self.ret_comp_list]
        min_ret_mat_list = math.inf if len(ret_max_list) == 0 else min(ret_max_list)
        return tick.high < self.max and tick.high < min_ret_mat_list

    def can_retracement_component_be_added(self, ret_comp: FibonacciDescendingRetracementComponent) -> bool:
        return ret_comp.tick_end.position == ret_comp.idx_max and ret_comp.retracement_pct < FR.R_764 + 0.1

    def __calculate_regression_values_for_component__(self, reg_comp: FibonacciDescendingRegressionComponent):
        index_comp_id = self.comp_id_list_reg.index(reg_comp.comp_id)
        if index_comp_id > 0:
            reg_comp_prev = self.comp_dic[self.comp_id_list_reg[index_comp_id - 1]]
            ret_comp_prev = self.comp_dic[self.comp_id_list_ret[index_comp_id - 1]]
            reg_comp.regression_value_against_last_regression = round(reg_comp_prev.min - reg_comp.min, 2)
            reg_comp.regression_value_against_last_retracement = round(ret_comp_prev.min - reg_comp.min, 2)
            reg_comp.regression_pct_against_last_regression = round(reg_comp.get_end_to_end_range()
                                                    / reg_comp_prev.get_end_to_end_range(), 3)

    def __calculate_retracement_values_for_component__(self, ret_comp: FibonacciDescendingRetracementComponent):
        index_wave_id = self.comp_id_list_ret.index(ret_comp.comp_id)
        reg_comp = self.comp_dic[self.comp_id_list_reg[index_wave_id]]
        ret_comp.retracement_value = ret_comp.get_retracement_value(reg_comp)
        ret_comp.retracement_pct = ret_comp.get_retracement_pct(reg_comp)