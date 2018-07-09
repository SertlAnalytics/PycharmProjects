"""
Description: This module contains the Fibonacci wave tree class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
import pandas as pd
from sertl_analytics.constants.pattern_constants import FD, CM
from fibonacci.fibonacci_wave_component import FibonacciRegressionComponent, FibonacciRetracementComponent
from fibonacci.fibonacci_wave import FibonacciWave, FibonacciAscendingWave, FibonacciDescendingWave
from pattern_wave_tick import WaveTick


class FibonacciWaveTree:
    def __init__(self, df_source: pd.DataFrame, min_max_tick_list: list, print_wave_details = False):
        self.df_source = df_source
        self.print_wave_details = print_wave_details
        self.min_max_tick_list = min_max_tick_list
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
                reg_comp = FibonacciRegressionComponent(self.df_source, tick_previous, tick_next, reg_comp_id_next)
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
                ret_comp = FibonacciRetracementComponent(self.df_source, tick_previous, tick_next, ret_comp_id_next)
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

    def __add_wave_after_check_to_list__(self, wave_list: list, wave: FibonacciWave):
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
                if self.print_wave_details:
                    wave.print('added...')
            else:
                wave_list[replacing_index] = wave
                if self.print_wave_details:
                    wave.print('replacing...')
