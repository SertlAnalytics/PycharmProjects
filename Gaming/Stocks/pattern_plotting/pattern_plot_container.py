"""
Description: This module contains the pattern plot container classes - handles the plots patches
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from matplotlib.patches import Polygon
from sertl_analytics.pybase.loop_list import LoopList


class PatternPlotContainer:
    border_line_top_color = 'green'
    border_line_bottom_color = 'red'
    regression_line_color = 'blue'
    center_color = 'blue'
    """
    Contains all plotting objects for one pattern
    """
    def __init__(self, polygon: Polygon, pattern_color: str):
        self.index_list = []
        self.shape_dic = {}
        self.patches_dic = {}
        self.color_dic = {}
        self.index_list.append('pattern')
        self.shape_dic['pattern'] = polygon
        self.color_dic['pattern'] = pattern_color
        self.annotation_param = None
        self.annotation = None

    def add_buy_shape(self, buy_shape, buy_color: str):
        self.index_list.append('buy')
        self.shape_dic['buy'] = buy_shape
        self.color_dic['buy'] = buy_color

    def add_trade_shape(self, trade_shape, trade_color: str):
        self.index_list.append('trade')
        self.shape_dic['trade'] = trade_shape
        self.color_dic['trade'] = trade_color

    def add_retracement_shape(self, retracement_shape, retracement_color: str):
        self.index_list.append('retracement')
        self.shape_dic['retracement'] = retracement_shape
        self.color_dic['retracement'] = retracement_color

    def add_border_line_top_shape(self, line_shape):
        self.index_list.append('top')
        self.shape_dic['top'] = line_shape
        self.color_dic['top'] = self.border_line_top_color

    def add_border_line_bottom_shape(self, line_shape):
        self.index_list.append('bottom')
        self.shape_dic['bottom'] = line_shape
        self.color_dic['bottom'] = self.border_line_top_color

    def add_regression_line_shape(self, line_shape):
        self.index_list.append('regression')
        self.shape_dic['regression'] = line_shape
        self.color_dic['regression'] = self.regression_line_color

    def add_center_shape(self, center_shape):
        self.index_list.append('center')
        self.shape_dic['center'] = center_shape
        self.color_dic['center'] = self.center_color

    def hide(self):
        self.__set_visible__(False, True)

    def show(self, with_annotation: bool):
        self.__set_visible__(True, with_annotation)

    def show_annotations(self):
        self.annotation.set_visible(True)

    def hide_annotations(self):
        self.annotation.set_visible(False)

    def __set_visible__(self, visible: bool, with_annotation: bool):
        self.annotation.set_visible(visible and with_annotation)
        for key in self.patches_dic:
            if key == 'center' and visible and with_annotation:
                self.patches_dic[key].set_visible(False)
            else:
                self.patches_dic[key].set_visible(visible)

    def add_annotation(self, axes):
        self.annotation = self.annotation_param.get_annotation(axes)

    def add_elements_as_patches(self, axes):
        for key in self.index_list:
            patch = self.shape_dic[key]
            self.patches_dic[key] = patch
            patch.set_alpha(0.2)
            if key in ['top', 'bottom']:
                patch.set_color('None')
                patch.set_edgecolor(self.color_dic[key])
            elif key in ['buy']:
                # patch.set_color(self.color_dic[key])
                patch.set_alpha(0.2)
            else:
                patch.set_color(self.color_dic[key])
            axes.add_patch(patch)


class PatternPlotContainerLoopList(LoopList):
    def show_only_selected_containers(self, event):
        show_list = []
        self.__add_first_first_selected_center_pattern_to_show_list__(event, show_list)
        if len(show_list) == 0:
            self.__add_selected_pattern_to_show_list__(event, show_list)
        if len(show_list) == 0:
            for pattern_plot_container in self.value_list:
                pattern_plot_container.show(False)
        else:
            for pattern_plot_container in self.value_list:
                pattern_plot_container.hide()
            for pattern_plot_container in show_list:
                pattern_plot_container.show(True)
        event.canvas.draw()

    def __add_selected_pattern_to_show_list__(self, event, show_list: list):
        for pattern_plot_container in self.value_list:
            for patch in pattern_plot_container.patches_dic.values():
                cont, dic = patch.contains(event)
                if cont:
                    show_list.append(pattern_plot_container)

    def __add_first_first_selected_center_pattern_to_show_list__(self, event, show_list: list):
        for pattern_plot_container in self.value_list:
            patch = pattern_plot_container.patches_dic['center']
            cont, dic = patch.contains(event)
            if cont:
                show_list.append(pattern_plot_container)
                break