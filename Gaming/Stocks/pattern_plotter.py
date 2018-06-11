"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import CN
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from matplotlib.collections import PatchCollection
from sertl_analytics.pybase.loop_list import LoopList
from pattern_configuration import config, runtime
from pattern_data_container import pattern_data_handler
from pattern_wave_tick import WaveTick, WaveTickList
from pattern_detector import PatternDetector
from pattern import Pattern
from mpl_finance import candlestick_ohlc


class FormationColorHandler:
    def get_colors_for_formation(self, formation: Pattern):
        return self.__get_formation_color__(formation), self.__get_trade_color__(formation)

    @staticmethod
    def __get_formation_color__(formation: Pattern):
        if formation.was_breakout_done():
            return 'green'
        else:
            return 'yellow'

    @staticmethod
    def __get_trade_color__(formation: Pattern):
        if formation.was_breakout_done():
            if formation.trade_result.actual_win > 0:
                return 'lime'
            else:
                return 'orangered'
        else:
            return 'white'


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
        self.pc_dic = {}
        self.color_dic = {}
        self.index_list.append('pattern')
        self.shape_dic['pattern'] = polygon
        self.color_dic['pattern'] = pattern_color
        self.annotation_param = None
        self.annotation = None

    def add_trade_shape(self, trade_shape, trade_color: str):
        self.index_list.append('trade')
        self.shape_dic['trade'] = trade_shape
        self.color_dic['trade'] = trade_color

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
        for key in self.pc_dic:
            if key == 'center' and visible and with_annotation:
                self.pc_dic[key].set_visible(False)
            else:
                self.pc_dic[key].set_visible(visible)

    def add_annotation(self, axes):
        self.annotation = self.annotation_param.get_annotation(axes)

    def add_elements_as_patch_collection(self, axes):
        for keys in self.index_list:
            self.pc_dic[keys] = PatchCollection([self.shape_dic[keys]], alpha=0.4)
            if keys in ['top', 'bottom']:
                self.pc_dic[keys].set_color('None')
                self.pc_dic[keys].set_edgecolor(self.color_dic[keys])
            else:
                self.pc_dic[keys].set_color(self.color_dic[keys])

            axes.add_collection(self.pc_dic[keys])


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
            for collections_keys in pattern_plot_container.pc_dic:
                collection = pattern_plot_container.pc_dic[collections_keys]
                cont, dic = collection.contains(event)
                if cont:
                    show_list.append(pattern_plot_container)

    def __add_first_first_selected_center_pattern_to_show_list__(self, event, show_list: list):
        for pattern_plot_container in self.value_list:
            collection = pattern_plot_container.pc_dic['center']
            cont, dic = collection.contains(event)
            if cont:
                show_list.append(pattern_plot_container)
                break


class PatternPlotter:
    def __init__(self, detector: PatternDetector):
        self.detector = detector
        self.df = pattern_data_handler.pattern_data.df
        self.symbol = runtime.actual_ticker
        self.pattern_plot_container_loop_list = PatternPlotContainerLoopList()
        self.axes = None

    def plot_data_frame(self):
        with_close_plot = False
        with_volume_plot = False

        if with_close_plot:
            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 10), sharex='all')
            self.__plot_close__(axes[0])
            self.__plot_candlesticks__(axes[1])
            self.__plot_patterns__(axes[1])
            self.__plot_volume__(axes[2])
            self.axes = axes[1]
        else:
            if with_volume_plot:
                fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 7), sharex='all')
                self.__plot_candlesticks__(axes[0])
                self.__plot_patterns__(axes[0])
                self.__plot_volume__(axes[1])
                self.axes = axes[0]
            else:
                fig, axes = plt.subplots(figsize=(15, 7))
                self.axes = axes
                self.__plot_candlesticks__(axes)
                self.__plot_min_max__(axes)
                self.__plot_patterns__(axes)

        plt.title('{}. {} ({}) for {}'.format(
            runtime.actual_number, runtime.actual_ticker,
            runtime.actual_ticker_name, self.__get_date_range_for_title__()))
        plt.tight_layout()
        # plt.xticks(rotation=45)
        fig.canvas.mpl_connect('button_press_event', self.__on_click__)
        self.axes.format_coord = self.__on_hover__
        plt.show()

    def __get_date_range_for_title__(self):
        tick_first = WaveTick(self.df.iloc[0])
        tick_last = WaveTick(self.df.iloc[-1])
        return 'Date between "{}" AND "{}"'.format(tick_first.date_str, tick_last.date_str)

    def __on_click__(self, event):
        self.pattern_plot_container_loop_list.show_only_selected_containers(event)

    def __on_hover__(self, x, y):
        tick = pattern_data_handler.pattern_data.tick_by_date_num_ext_dic.get_value(int(x + 0.5))
        return '{} ({:3.0f}): [{:5.1f}; {:5.1f}]; vol={:8.0f}(t); y={:0.2f}'.format(
            tick.date_str, tick.position, tick.low, tick.high, tick.volume/1000, y)

    def __plot_close__(self, axis):
        axis.plot(self.df.loc[:, CN.DATEASNUM], self.df.loc[:, CN.CLOSE])
        axis.grid()
        axis.legend(loc='upper left')

    def __plot_candlesticks__(self, axis):
        ohlc_list = [[t.date_num, t.open, t.high, t.low, t.close] for t in pattern_data_handler.pattern_data.tick_list]
        candlestick_ohlc(axis, ohlc_list, width=0.4, colorup='g')
        axis.xaxis_date()
        axis.grid()
        # self.__add_fibonacci_waves__(axis)

    def __plot_patterns__(self, axis):
        self.__fill_plot_container_list__()
        self.__add_pattern_shapes_to_plot__(axis)

    def __plot_min_max__(self, axis):
        if not config.plot_min_max:
            return
        wave_tick_list = WaveTickList(pattern_data_handler.pattern_data.df_min_max)
        for ticks in wave_tick_list.tick_list:
            if ticks.is_min:
                axis.add_patch(Circle((ticks.f_var, ticks.low), 0.5, color='r'))
            else:
                axis.add_patch(Circle((ticks.f_var, ticks.high), 0.5, color='g'))
        for ticks in pattern_data_handler.pattern_data.tick_list_min_without_hidden_ticks:
            axis.add_patch(Circle((ticks.f_var, ticks.low), 0.3, color='w'))
        for ticks in pattern_data_handler.pattern_data.tick_list_max_without_hidden_ticks:
            axis.add_patch(Circle((ticks.f_var, ticks.high), 0.3, color='w'))

    def __plot_volume__(self, axis):
        axis.plot(self.df.loc[:, CN.DATEASNUM], self.df.loc[:, CN.VOL])
        axis.grid()
        axis.legend(loc='upper left')

    def __fill_plot_container_list__(self):
        color_handler = FormationColorHandler()
        for pattern in self.detector.pattern_list:
            color_pattern, color_trade = color_handler.get_colors_for_formation(pattern)
            plot_container = PatternPlotContainer(pattern.get_shape_part_main(), color_pattern)
            if pattern.was_breakout_done() and pattern.is_part_trade_available():
                plot_container.add_trade_shape(pattern.get_shape_part_trade(), color_trade)
            plot_container.add_center_shape(pattern.get_center_shape())
            plot_container.annotation_param = pattern.get_annotation_parameter('blue')
            # plot_container.add_border_line_top_shape(pattern.part_main.get_f_upper_shape())
            # plot_container.add_border_line_bottom_shape(pattern.part_main.get_f_lower_shape())
            plot_container.add_regression_line_shape(pattern.part_main.get_f_regression_shape())
            self.pattern_plot_container_loop_list.append(plot_container)

    def __add_pattern_shapes_to_plot__(self, ax):
        for pattern_plot_container in self.pattern_plot_container_loop_list.value_list:
            pattern_plot_container.add_elements_as_patch_collection(ax)
            pattern_plot_container.add_annotation(ax)
