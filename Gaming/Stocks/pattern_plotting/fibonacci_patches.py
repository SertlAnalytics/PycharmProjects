"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
from matplotlib.patches import Polygon, Rectangle
from matplotlib.offsetbox import TextArea, AnnotationBbox
from fibonacci.fibonacci_wave import FibonacciWave
from fibonacci.fibonacci_helper import fibonacci_helper
from pattern_plotting.patch_helper import PatchHelper


class FibonacciWavePatch:
    color_01 = 'darkgrey'
    color_02 = 'whitesmoke'
    color_bg = 'lightyellow'
    color_list = [color_01, color_02, color_01, color_02, color_01]

    def __init__(self, fib_wave: FibonacciWave, polygon: Polygon):
        self.fib_wave = fib_wave
        self.polygon = polygon
        self.xy = self.polygon.get_xy().round(2)
        self.id = PatchHelper.get_id_for_polygon(self.polygon)
        self.selected = False
        self.__fib_retracement_rectangle_dic = {}
        self.__fib_retracement_rectangle_text_dic = {}
        self.__fib_retracement_spikes_text_dic = {}
        self.__fill_fibonacci_retracement_rectangle_dic__()

    def add_retracement_patch_list_to_axis(self, axis):
        for key, rectangle in self.__fib_retracement_rectangle_dic.items():
            axis.add_patch(rectangle)
            axis.add_artist(self.__fib_retracement_rectangle_text_dic[key])
            if key in self.__fib_retracement_spikes_text_dic:  # we don't have this for unfinished waves
                axis.add_artist(self.__fib_retracement_spikes_text_dic[key])

    def hide_retracement_patch_list(self):
        for key, rectangle in self.__fib_retracement_rectangle_dic.items():
            rectangle.set_visible(False)
            self.__fib_retracement_rectangle_text_dic[key].set_visible(False)
            if key in self.__fib_retracement_spikes_text_dic:  # we don't have this for unfinished waves
                self.__fib_retracement_spikes_text_dic[key].set_visible(False)

    def show_retracement_patch_list(self):
        for key, rectangle in self.__fib_retracement_rectangle_dic.items():
            rectangle.set_visible(True)
            self.__fib_retracement_rectangle_text_dic[key].set_visible(True)
            if key in self.__fib_retracement_spikes_text_dic:  # we don't have this for unfinished waves
                self.__fib_retracement_spikes_text_dic[key].set_visible(True)

    def select_fib_wave(self):
        self.polygon.set_linewidth(3)
        self.show_retracement_patch_list()
        self.selected = True

    def reset_selected_fib_wave(self):
        self.polygon.set_linewidth(1)
        self.hide_retracement_patch_list()
        self.selected = False

    def __fill_fibonacci_retracement_rectangle_dic__(self):
        index_left = self.xy[0, 0]
        index_right = self.xy[self.xy.shape[0]-1, 0]
        value_left = self.xy[0, 1]
        value_right = self.xy[self.xy.shape[0]-1, 1]
        value_range = value_right - value_left
        width = index_right - index_left

        for k in range(0, len(fibonacci_helper.retracement_array_for_plotting)-1):
            ret_01 = fibonacci_helper.retracement_array_for_plotting[k]
            ret_02 = fibonacci_helper.retracement_array_for_plotting[k+1]

            value_01 = round(value_left + ret_01 * value_range, 2)
            value_02 = round(value_left + ret_02 * value_range, 2)
            height = value_02 - value_01
            rectangle = Rectangle(np.array([index_left, value_01]), width=width, height=height)
            rectangle.set_linewidth(1)
            rectangle.set_linestyle('dashed')
            rectangle.set_color(self.color_list[k])
            rectangle.set_edgecolor('k')
            rectangle.set_alpha(0.1)
            rectangle.set_visible(False)
            self.__fib_retracement_rectangle_dic[ret_02] = rectangle
            self.__fill_retracement_text_annotations__(index_left, ret_02, value_02)
            self.__fill_retracement_spikes_text_annotations__(ret_02, k + 1)

    def __fill_retracement_text_annotations__(self, index: int, ret: float, value: float):
        text = '{:=1.3f} - {:.2f}'.format(ret, value)
        text_area = TextArea(text, minimumdescent=True, textprops=dict(size=7))
        annotation_box = AnnotationBbox(text_area, (index, value))
        annotation_box.set_visible(False)
        self.__fib_retracement_rectangle_text_dic[ret] = annotation_box

    def __fill_retracement_spikes_text_annotations__(self, ret: str, position_in_wave: int):
        if position_in_wave >= self.xy.shape[0]:  # we don't have this component for unfinished waves
            return
        index = self.xy[position_in_wave, 0]
        value = self.xy[position_in_wave, 1]
        position = self.fib_wave.comp_position_list[position_in_wave]
        is_position_retracement = position_in_wave % 2 == 0
        prefix = 'Retr.' if is_position_retracement else 'Reg.'
        value_adjusted = value + (value * 0.01 if is_position_retracement else value * -0.01)
        reg_ret_value = self.fib_wave.comp_reg_ret_percent_list[position_in_wave - 1]
        if position_in_wave == 1:
            reg_ret_value = round(self.xy[position_in_wave, 1] - self.xy[position_in_wave - 1, 1], 2)
            text = 'P_{}={:.2f}\n{}: {:.2f}'.format(position, value, prefix, reg_ret_value)
        else:
            text = 'P_{}={:.2f}\n{}: {:=3.1f}%'.format(position, value, prefix, reg_ret_value)
        text_props = dict(color='crimson', backgroundcolor=self.color_bg, size=7)
        text_area = TextArea(text, minimumdescent=True, textprops=text_props)
        annotation_box = AnnotationBbox(text_area, (index, value_adjusted))
        annotation_box.set_visible(False)
        self.__fib_retracement_spikes_text_dic[ret] = annotation_box


class FibonacciWavePatchContainer:
    def __init__(self):
        self.fibonacci_wave_patch_dic = {}

    def contains_patch_id(self, patch_id: str):
        return patch_id in self.fibonacci_wave_patch_dic

    def add_patch(self, fib_patch: FibonacciWavePatch):
        self.fibonacci_wave_patch_dic[fib_patch.id] = fib_patch

    def get_patch_by_id(self, patch_id: str):
        if patch_id in self.fibonacci_wave_patch_dic:
            return self.fibonacci_wave_patch_dic[patch_id]
        return None

    def reset_selected_patches(self) -> bool:
        reset_flag = False
        for fib_patch in self.fibonacci_wave_patch_dic.values():
            if fib_patch.selected:
                fib_patch.reset_selected_fib_wave()
                reset_flag = True
        return reset_flag