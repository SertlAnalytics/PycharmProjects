"""
Description: This module contains the Fibonacci wave classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
from sertl_analytics.constants.pattern_constants import FD, FR, CM, FWST, DC
from sertl_analytics.mymath import MyPoly1d
from sertl_analytics.mydates import MyDate
from fibonacci.fibonacci_wave_component import FibonacciWaveComponent, FibonacciRegressionComponent, \
    FibonacciRetracementComponent
from fibonacci.fibonacci_wave_component import FibonacciAscendingRegressionComponent
from fibonacci.fibonacci_wave_component import FibonacciDescendingRegressionComponent
from fibonacci.fibonacci_wave_component import FibonacciAscendingRetracementComponent
from fibonacci.fibonacci_wave_component import FibonacciDescendingRetracementComponent
from fibonacci.fibonacci_helper import fibonacci_helper, FibonacciHelperApi
from pattern_database.stock_tables_data_dictionary import WaveDataDictionary
from pattern_wave_tick import WaveTick
import math
from copy import deepcopy


class FibonacciWave:
    # class properties
    comp_id_list_reg = ['w_1', 'w_3', 'w_5']
    comp_id_list_ret = ['w_2', 'w_4']
    comp_id_list = ['w_1', 'w_2', 'w_3', 'w_4', 'w_5']

    def __init__(self, tick_distance: float):
        self.data_dict_obj = WaveDataDictionary()
        self.tick_distance = tick_distance
        self.comp_dic = {}
        self.comp_forecast_parameter_list = []
        self.forecast_value_list = []

    @property
    def wave_type(self):
        return FD.NONE

    @property
    def position_start(self):
        return self.comp_position_list[0]

    @property
    def position_end(self):
        return self.comp_position_list[-1]

    @property
    def f_upper(self) -> np.poly1d:
        if self.wave_type == FD.ASC:
            tick_01, tick_02 = self.w_1.tick_end, self.w_5.tick_end
            f_upper_temp = MyPoly1d.get_poly1d(tick_01.f_var, tick_01.high, tick_02.f_var, tick_02.high)
            if f_upper_temp(self.w_1.tick_start.f_var) < self.w_1.tick_start.high:
                tick_01 = self.w_1.tick_start
        else:
            if self.wave_structure in [FWST.S_M_L, FWST.L_M_S]:
                tick_01, tick_02 = self.w_4.tick_end, self.w_5.tick_end
            else:
                tick_01, tick_02 = self.w_3.tick_start, self.w_5.tick_start
        return MyPoly1d.get_poly1d(tick_01.f_var, tick_01.high, tick_02.f_var, tick_02.high)

    @property
    def f_lower(self) -> np.poly1d:
        if self.wave_type == FD.ASC:
            if self.wave_structure in [FWST.S_M_L, FWST.L_M_S]:
                tick_01, tick_02 = self.w_4.tick_end, self.w_5.tick_end
            else:
                tick_01, tick_02 = self.w_3.tick_start, self.w_5.tick_start
        else:
            tick_01, tick_02 = self.w_3.tick_end, self.w_5.tick_end
            f_lower_temp = MyPoly1d.get_poly1d(tick_01.f_var, tick_01.low, tick_02.f_var, tick_02.low)
            if f_lower_temp(self.w_1.tick_start.f_var) > self.w_1.tick_start.low:
                tick_01 = self.w_1.tick_start
        return MyPoly1d.get_poly1d(tick_01.f_var, tick_01.low, tick_02.f_var, tick_02.low)

    def is_wave_ready_for_wave_table(self) -> bool:
        return self.data_dict_obj.is_data_dict_ready_for_target_table()

    def inherit_data_dict_values(self, data_dict: dict):
        self.data_dict_obj.inherit_values(data_dict)

    def is_closing_triangle_criteria_fulfilled(self):
        return self.wave_structure == FWST.S_M_L or self.f_upper[1] < self.f_lower[1]

    def is_neckline_criteria_fulfilled(self) -> bool:
        return self.__is_neckline_without_intersection__()

    def __is_neckline_without_intersection__(self) -> bool:
        return True

    def is_wave_indicator_for_dash(self, period_aggregation: int) -> bool:
        ts_last_tick = self.w_5.tick_end.time_stamp
        ts_now = MyDate.get_epoch_seconds_from_datetime()
        number_ticks = int(30/period_aggregation)  # we want to be reminded for 1/2 hour
        # number_ticks = 100
        return ts_now - ts_last_tick < period_aggregation * 60 * number_ticks

    @property
    def w_1(self) -> FibonacciWaveComponent:
        return self.get_component_by_number(1)

    @property
    def w_2(self) -> FibonacciWaveComponent:
        return self.get_component_by_number(2)

    @property
    def w_3(self) -> FibonacciWaveComponent:
        return self.get_component_by_number(3)

    @property
    def w_4(self) -> FibonacciWaveComponent:
        return self.get_component_by_number(4)

    @property
    def w_5(self) -> FibonacciWaveComponent:
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
    def wave_structure(self):
        if not self.is_wave_complete():
            return FWST.NONE
        if self.w_1.range_max > self.w_3.range_max > self.w_5.range_max:
            return FWST.L_M_S
        elif self.w_3.range_max > self.w_1.range_max + self.w_5.range_max \
                and 0.8 < self.w_1.range_max/self.w_5.range_max < 1.2:
            return FWST.S_L_S
        elif self.w_1.range_max < self.w_3.range_max < self.w_5.range_max:
            return FWST.S_M_L
        return FWST.NONE

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

    def get_minimal_retracement_range_after_finishing(self) -> float:
        wave_structure = self.wave_structure
        if self.wave_type == FD.ASC:
            if wave_structure == FWST.L_M_S:  # retracement at least to large wave
                return self.w_5.max - self.w_1.max
            elif wave_structure == FWST.S_M_L:  # retracement at least to medium wave
                return self.w_5.max - self.w_3.max
            elif wave_structure == FWST.S_L_S:  # retracement at least to middle of large wave
                return self.w_3.max - (self.w_3.max + self.w_3.min)/2
        else:
            if wave_structure == FWST.L_M_S:  # retracement at least to large wave
                return self.w_1.min - self.w_5.min
            elif wave_structure == FWST.S_M_L:  # retracement at least to medium wave
                return self.w_3.min - self.w_5.min
            elif wave_structure == FWST.S_L_S:  # retracement at least to middle of large wave
                return (self.w_3.max + self.w_3.min)/2 - self.w_3.min

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
        self.__add_component_data_to_data_dict__(reg_comp)

    def add_retracement(self, ret_comp: FibonacciRetracementComponent):
        self.comp_dic[ret_comp.comp_id] = ret_comp
        self.__add_component_data_to_data_dict__(ret_comp)
        if ret_comp.comp_id == 'w_4':
            if self.is_wave_fibonacci_wave(True):
                self.__fill_comp_forecast_parameter_list__()

    def __add_component_data_to_data_dict__(self, component: FibonacciWaveComponent):
        if component.comp_id == 'w_1':
            self.data_dict_obj.add(DC.W1_BEGIN_TS, component.tick_start.time_stamp)
            self.data_dict_obj.add(DC.W1_BEGIN_DT, component.tick_start.date_time_str)
            self.data_dict_obj.add(DC.W1_RANGE, component.range_max)
        elif component.comp_id == 'w_2':
            self.data_dict_obj.add(DC.W2_BEGIN_TS, component.tick_start.time_stamp)
            self.data_dict_obj.add(DC.W2_BEGIN_DT, component.tick_start.date_time_str)
            self.data_dict_obj.add(DC.W2_RANGE, component.range_max)
        elif component.comp_id == 'w_3':
            self.data_dict_obj.add(DC.W3_BEGIN_TS, component.tick_start.time_stamp)
            self.data_dict_obj.add(DC.W3_BEGIN_DT, component.tick_start.date_time_str)
            self.data_dict_obj.add(DC.W3_RANGE, component.range_max)
        elif component.comp_id == 'w_4':
            self.data_dict_obj.add(DC.W4_BEGIN_TS, component.tick_start.time_stamp)
            self.data_dict_obj.add(DC.W4_BEGIN_DT, component.tick_start.date_time_str)
            self.data_dict_obj.add(DC.W4_RANGE, component.range_max)
        elif component.comp_id == 'w_5':
            self.data_dict_obj.add(DC.W5_BEGIN_TS, component.tick_start.time_stamp)
            self.data_dict_obj.add(DC.W5_BEGIN_DT, component.tick_start.date_time_str)
            self.data_dict_obj.add(DC.W5_RANGE, component.range_max)
            # add wave specific data
            self.data_dict_obj.add(DC.WAVE_END_TS, component.tick_end.time_stamp)
            self.data_dict_obj.add(DC.WAVE_END_DT, component.tick_end.date_time_str)
            self.data_dict_obj.add(DC.WAVE_TYPE, self.wave_type)
            self.data_dict_obj.add(DC.WAVE_TYPE_ID, FD.get_id(self.wave_type))
            self.data_dict_obj.add(DC.WAVE_STRUCTURE, self.wave_structure)
            self.data_dict_obj.add(DC.WAVE_STRUCTURE_ID, FWST.get_id(self.wave_structure))


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

        # 5. verify that the middle regression is not the smallest one
        if not for_forecast:
            reg_range_list = [comp.range_max for comp in self.reg_comp_list]
            if np.argmin(reg_range_list) == 1:
                return False

        # 6. Only certain relations for the 3 regressions are allowed...
        if self.wave_structure == FWST.NONE:
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

    def get_details_as_dash_indicator(self):
        return '{} - last tick at {}'.format(self.wave_type, self.w_5.tick_end.time)

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

    def __is_neckline_without_intersection__(self) -> bool:
        return self.f_lower(self.w_5.tick_end.f_var) < self.w_5.tick_end.high

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

    def __is_neckline_without_intersection__(self) -> bool:
        return self.f_upper(self.w_5.tick_end.f_var) > self.w_5.tick_end.low

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