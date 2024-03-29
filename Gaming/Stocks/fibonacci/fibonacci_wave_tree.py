"""
Description: This module contains the Fibonacci wave tree class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
import pandas as pd
from sertl_analytics.constants.pattern_constants import FD, CN
from sertl_analytics.mydates import MyDate
from fibonacci.fibonacci_wave_component import FibonacciAscendingRegressionComponent, \
    FibonacciDescendingRegressionComponent, FibonacciAscendingRetracementComponent, \
    FibonacciDescendingRetracementComponent
from fibonacci.fibonacci_wave import FibonacciWave, FibonacciAscendingWave, FibonacciDescendingWave
from pattern_wave_tick import WaveTick
from copy import deepcopy


class FibonacciWaveForecastCollector:
    def __init__(self):
        self.__idx_list = []
        self.__forecast_value_list_dict = {}
        self.__max_position_5_dict = {}
        self.__max_position_5_wave_dict = {}

    def add_forecast_wave(self, wave: FibonacciWave):
        idx = str(wave.comp_position_list[0]) + '-' + str(wave.comp_position_list[4])
        value = wave.w_5.tick_end.high if wave.wave_type == FD.ASC else wave.w_5.tick_end.low
        if idx not in self.__idx_list:
            self.__idx_list.append(idx)
            self.__forecast_value_list_dict[idx] = [value]
            self.__max_position_5_dict[idx] = wave.comp_position_list[4]
            self.__max_position_5_wave_dict[idx] = wave
        else:
            if value not in self.__forecast_value_list_dict[idx]:
                self.__forecast_value_list_dict[idx].append(value)
            if wave.comp_position_list[4] > self.__max_position_5_dict[idx]:
                self.__max_position_5_dict[idx] = wave.comp_position_list[4]
                self.__max_position_5_wave_dict[idx] = wave
        self.__max_position_5_wave_dict[idx].forecast_value_list = self.__forecast_value_list_dict[idx]

    def get_forecast_wave_list(self) -> list:
        ts_now = MyDate.get_epoch_seconds_from_datetime()  # new on 10.01.2019 to avoid forecast in the past
        return [wave for wave in self.__max_position_5_wave_dict.values() if wave.w_5.tick_end.time_stamp > ts_now]


class FibonacciWaveTree:
    def __init__(self, df_source: pd.DataFrame, min_max_tick_list: list,
                 max_wave_component_length: int, tick_distance: float, parent_data: dict):
        self.df_source = df_source
        self._max_wave_component_length = max_wave_component_length
        self._parent_data_dict = parent_data
        self.tick_distance = tick_distance
        self.position_last = self.df_source.iloc[-1].Position
        self.min_max_tick_list = min_max_tick_list
        self.min_max_list_length = len(self.min_max_tick_list)
        self.min_tick_list = []
        self.max_tick_list = []
        self.min_possible_max_tick_dic = {}
        self.max_possible_min_tick_dic = {}
        self.__fill_lists_and_dictionaries_dics__()
        self.fibonacci_wave_list = []
        self.fibonacci_unfinished_wave_list = []
        self.fibonacci_wave_forecast_collector = FibonacciWaveForecastCollector()
        self.min_list_length = len(self.min_tick_list)
        self.max_list_length = len(self.max_tick_list)

    def parse_tree(self, parse_direction=FD.NONE):
        if parse_direction in [FD.NONE, FD.ASC]:
            self.__parse_for_ascending_waves__()
        if parse_direction in [FD.NONE, FD.DESC]:
            self.__parse_for_descending_waves__()

    def was_any_wave_finished_since_time_stamp(self, time_stamp: float):
        for wave in self.fibonacci_wave_list:
            tick_end = wave.w_5.tick_end
            if tick_end.is_asc_fibonacci_end or tick_end.is_desc_fibonacci_end:
                self.__print_time_stamps__(tick_end.time_stamp, time_stamp)
                if tick_end.time_stamp >= time_stamp:
                    return True
        return False

    def get_actual_forecast_wave_list(self):
        return_list = []
        for wave in self.fibonacci_wave_forecast_collector.get_forecast_wave_list():
            if wave.w_5.tick_end.position >= self.position_last - 10:
                return_list.append(wave)
        return return_list

    @staticmethod
    def __print_time_stamps__(tick_end_time_stamp: float, last_refresh_time_stamp: float):
        flag = tick_end_time_stamp >= last_refresh_time_stamp
        if not flag:
            return
        date_time_end = MyDate.get_date_time_from_epoch_seconds(tick_end_time_stamp)
        date_time_last_refresh = MyDate.get_date_time_from_epoch_seconds(last_refresh_time_stamp)
        print('was_any_wave_finished_since_time_stamp = {}: tick_end = {} / {} = last_refresh'.format(
            flag, date_time_end, date_time_last_refresh
        ))

    def __parse_for_descending_waves__(self):
        for tick_max in self.max_tick_list:
            if tick_max.is_global_max:
                wave = FibonacciDescendingWave(self.tick_distance)
                wave.inherit_data_dict_values(self._parent_data_dict)
                self.__add_next_reg_comp__(wave, wave.reg_comp_id_next, tick_max)

    def __parse_for_ascending_waves__(self):
        for tick_min in self.min_tick_list:
            if tick_min.is_global_min:
                wave = FibonacciAscendingWave(self.tick_distance)
                wave.inherit_data_dict_values(self._parent_data_dict)
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
            if tick_min.position - tick_max.position > self._max_wave_component_length:
                break
            if tick_min.is_local_min and tick_min.low <= min_array.mean():
                min_array = np.append(min_array, np.array([tick_min.low]))
                self.max_possible_min_tick_dic[tick_max.position].append(tick_min)

    def __fill_min_possible_max_tick_dic__(self, index: int, tick_min: WaveTick):
        self.min_possible_max_tick_dic[tick_min.position] = []
        max_array = np.array([tick_min.high])
        for index_max in range(index + 1, self.min_max_list_length):
            tick_max = self.min_max_tick_list[index_max]
            if tick_max.position - tick_min.position > self._max_wave_component_length:
                break
            if tick_max.is_local_max and tick_max.high >= max_array.mean():
                max_array = np.append(max_array, np.array([tick_max.high]))
                self.min_possible_max_tick_dic[tick_min.position].append(tick_max)

    def __add_next_reg_comp__(self, wave: FibonacciWave, reg_comp_id: str, tick_previous: WaveTick):
        possible_next_tick_list = self.__get_possible_next_tick_list__(tick_previous, wave, True)
        for tick_next in possible_next_tick_list:
            if wave.is_wave_ready_for_next_regression(tick_next, reg_comp_id):
                reg_comp = self.__get_regression_component__(wave, tick_previous, tick_next, reg_comp_id)
                wave.calculate_regression_values_for_component(reg_comp)
                if wave.can_regression_component_be_added(reg_comp):
                    wave.add_regression(reg_comp)
                    if wave.is_wave_complete():
                        self.__process_completed_wave__(wave)
                        self.__delete_component_from_dic__(wave, reg_comp_id)
                        self.__handle_forecasts__(wave)
                    else:
                        ret_comp_id_next = wave.ret_comp_id_next
                        if ret_comp_id_next != '':
                            self.__add_next_ret_comp__(wave, ret_comp_id_next, tick_next)
                        self.__delete_component_from_dic__(wave, reg_comp_id)

    def __get_regression_component__(self, wave: FibonacciWave, tick_start: WaveTick, tick_end: WaveTick, comp_id: str):
        if wave.wave_type == FD.ASC:
            return FibonacciAscendingRegressionComponent(self.df_source, tick_start, tick_end, comp_id)
        else:
            return FibonacciDescendingRegressionComponent(self.df_source, tick_start, tick_end, comp_id)

    def __add_next_ret_comp__(self, wave: FibonacciWave, ret_comp_id: str, tick_previous: WaveTick):
        possible_next_tick_list = self.__get_possible_next_tick_list__(tick_previous, wave, False)
        for tick_next in possible_next_tick_list:
            if wave.is_wave_ready_for_next_retracement(tick_next, ret_comp_id):
                ret_comp = self.__get_retracement_component__(wave, tick_previous, tick_next, ret_comp_id)
                wave.calculate_retracement_values_for_component(ret_comp)
                if wave.can_retracement_component_be_added(ret_comp):
                    wave.add_retracement(ret_comp)
                    if wave.is_wave_unfinished(self.position_last):
                        self.fibonacci_unfinished_wave_list.append(wave.clone())
                        print('Forecast w_5-{} (position_last={}: {} -> {}'.format(
                            wave.wave_type, self.position_last, wave.comp_position_list,
                            wave.comp_forecast_parameter_list))
                        # Forecast w_5 (position_last=299: [[1.781, 3595.51, 337], [2.219, 3634.49, 348]]
                    ret_comp_id_next = wave.reg_comp_id_next
                    if ret_comp_id_next != '':
                        self.__add_next_reg_comp__(wave, ret_comp_id_next, tick_next)
                    self.__delete_component_from_dic__(wave, ret_comp_id)

    def __get_retracement_component__(self, wave: FibonacciWave, tick_start: WaveTick, tick_end: WaveTick, comp_id: str):
        if wave.wave_type == FD.ASC:
            return FibonacciAscendingRetracementComponent(self.df_source, tick_start, tick_end, comp_id)
        else:
            return FibonacciDescendingRetracementComponent(self.df_source, tick_start, tick_end, comp_id)

    def __delete_component_from_dic__(self, wave: FibonacciWave, comp_id: str):
        if comp_id == 'w_4':
            self.__handle_forecasts__(wave)
        del wave.comp_dic[comp_id]

    def __handle_forecasts__(self, wave: FibonacciWave):
        if len(wave.comp_forecast_parameter_list) > 0:
            for parameter in wave.comp_forecast_parameter_list:  # [0.382, 207.46, 110] = fib, value, after_ticks
                value = parameter[1]
                position = self.position_last if parameter[2] > self.position_last else parameter[2]
                tick_forecast = self.__get_wave_tick_for_forecast__(wave, value, position)
                reg_comp = self.__get_regression_component__(wave, wave.w_4.tick_end, tick_forecast, 'w_5')
                wave.calculate_regression_values_for_component(reg_comp)
                if wave.can_regression_component_be_added(reg_comp):
                    wave.add_regression(reg_comp)
                    self.__process_forecast_wave__(wave)
                    del wave.comp_dic['w_5']  # we need this component for the next forecast wave
            wave.comp_forecast_parameter_list = []  # we are through...

    def __get_wave_tick_for_forecast__(self, wave: FibonacciWave, value: float, position: int):
        df = self.df_source[self.df_source[CN.POSITION] == position]
        row = deepcopy(df.iloc[0])
        row.High, row.Low, row.Open, row.Close = value, value, value, value
        tick = WaveTick(row)
        return tick

    def __get_possible_next_tick_list__(self, tick_previous, wave, for_regression: bool):
        base_possible_next_tick_list = self.__get_base_possible_next_tick_list__(tick_previous, wave, for_regression)
        return_list = []
        for tick in base_possible_next_tick_list:
            if wave.wave_type == FD.DESC:
                if for_regression:
                    if tick.low < wave.min:
                        return_list.append(tick)
                else:
                    if wave.min < tick.high < wave.max:
                        return_list.append(tick)
            else:
                if for_regression:
                    if tick.high > wave.max:
                        return_list.append(tick)
                else:
                    if wave.min < tick.low < wave.max:
                        return_list.append(tick)
        return return_list

    def __get_base_possible_next_tick_list__(self, tick_previous, wave, for_regression: bool):
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
            self.__add_wave_after_check_to_list__(self.fibonacci_wave_list, wave_clone)

    def __process_forecast_wave__(self, wave: FibonacciWave):
        if wave.is_wave_fibonacci_wave(True):
            self.fibonacci_wave_forecast_collector.add_forecast_wave(wave.clone())

    def __add_wave_after_check_to_list__(self, wave_list: list, wave: FibonacciWave):
        is_covered_by_list = False
        replacing_index = -1
        # for index, wave_in_list in enumerate(wave_list):
        #     coverage_mode = wave_in_list.get_coverage_mode(wave)
        #     if coverage_mode == CM.COVERING:
        #         is_covered_by_list = True
        #         break
        #     elif coverage_mode == CM.COVERED_BY:
        #         replacing_index = index
        #         break

        if not is_covered_by_list:
            self.__mark_last_tick_as_fibonacci_end__(wave)
            if replacing_index == -1:
                wave_list.append(wave)
            else:
                wave_list[replacing_index] = wave

    @staticmethod
    def __mark_last_tick_as_fibonacci_end__(wave: FibonacciWave):
        if wave.wave_type == FD.ASC:
            wave.w_5.tick_end.is_asc_fibonacci_end = True
        else:
            wave.w_5.tick_end.is_desc_fibonacci_end = True
