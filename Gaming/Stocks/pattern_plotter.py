"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import CN, DIR
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Circle
from matplotlib.collections import PatchCollection
from sertl_analytics.pybase.loop_list import LoopList
from pattern_configuration import config, runtime
from pattern_data_container import pattern_data_handler as pdh
from pattern_wave_tick import WaveTick, WaveTickList
from pattern_detector import PatternDetector
from pattern import Pattern
from mpl_finance import candlestick_ohlc
from pattern_range import PatternRange
from fibonacci import FibonacciWaveTree


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
        self.df = pdh.pattern_data.df
        self.tick_list = pdh.pattern_data.tick_list
        self.symbol = runtime.actual_ticker
        self.pattern_plot_container_loop_list = PatternPlotContainerLoopList()
        self.ranges_polygon_dic_list = {}
        self.ranges_opposite_polygon_dic_list = {}
        self.__currently_visible_ranges_polygon_list = []
        self.axes_for_candlesticks = None

    def plot_data_frame(self):
        with_close_plot = False
        with_volume_plot = False

        if with_close_plot:
            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 10), sharex='all')
            self.__plot_close__(axes[0])
            self.__plot_volume__(axes[2])
            self.axes_for_candlesticks = axes[1]
        else:
            if with_volume_plot:
                fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 7), sharex='all')
                self.__plot_volume__(axes[1])
                self.axes_for_candlesticks = axes[0]
            else:
                fig, axes = plt.subplots(figsize=(15, 7))
                self.axes_for_candlesticks = axes

        self.__plot_candlesticks__()
        if config.plot_min_max:
            self.__plot_min_max__()
            self.__plot_ranges__()
        self.__plot_patterns__()
        self.__plot_fibonacci_relations__()

        plt.title('{}. {} ({}) for {}'.format(
            runtime.actual_number, runtime.actual_ticker,
            runtime.actual_ticker_name, self.__get_date_range_for_title__()))
        plt.tight_layout()
        # plt.xticks(rotation=45)
        fig.canvas.mpl_connect('button_press_event', self.__on_click__)
        fig.canvas.mpl_connect('motion_notify_event', self.__on_motion_notify__)
        self.axes_for_candlesticks.format_coord = self.__on_hover__
        plt.show()

    @staticmethod
    def motion(event):
        print('motion')

    @staticmethod
    def button_1(event):
        print('Single Click - Button-1')

    @staticmethod
    def double_1(event):
        print('Double Click - so let us stop')

    def __get_date_range_for_title__(self):
        tick_first = WaveTick(self.df.iloc[0])
        tick_last = WaveTick(self.df.iloc[-1])
        return 'Date between "{}" AND "{}"'.format(tick_first.date_str, tick_last.date_str)

    def __on_click__(self, event):
        self.pattern_plot_container_loop_list.show_only_selected_containers(event)

    def __hide_range_polygons__(self, event):
        if len(self.__currently_visible_ranges_polygon_list) == 0:
            return
        for polygon in self.__currently_visible_ranges_polygon_list:
            polygon.set_visible(False)
        event.canvas.draw()

    def __on_motion_notify__(self, event):
        draw_canvas = False
        self.__hide_range_polygons__(event)
        for patches in self.axes_for_candlesticks.patches:
            if patches.__class__.__name__ == 'Circle':
                cont, dic = patches.contains(event)
                if cont:
                    tick = pdh.pattern_data.get_tick_by_date_num(patches.center[0])
                    if self.__show_ranges_polygons__(tick):
                        draw_canvas = True
        if draw_canvas:
            event.canvas.draw()

    def __show_ranges_polygons__(self, tick: WaveTick) -> bool:
        if tick.f_var in self.ranges_polygon_dic_list:
            for polygon in self.ranges_polygon_dic_list[tick.f_var]:
                polygon.set_visible(True)
                self.__currently_visible_ranges_polygon_list.append(polygon)
            if tick.f_var in self.ranges_opposite_polygon_dic_list:
                for polygon in self.ranges_opposite_polygon_dic_list[tick.f_var]:
                    polygon.set_visible(True)
                    self.__currently_visible_ranges_polygon_list.append(polygon)
            return True
        return False

    @staticmethod
    def __on_hover__(x, y):
        tick = pdh.pattern_data.tick_by_date_num_ext_dic.get_value(int(x + 0.5))
        return '{} ({:3.0f} / {:6.0f}): [{:5.1f}; {:5.1f}]; vol={:8.0f}(t); y={:0.2f}'.format(
            tick.date_str, tick.position, tick.f_var, tick.low, tick.high, tick.volume / 1000, y)

    def __plot_close__(self, axis):
        axis.plot(self.df.loc[:, CN.DATEASNUM], self.df.loc[:, CN.CLOSE])
        axis.grid()
        axis.legend(loc='upper left')

    def __plot_candlesticks__(self):
        ohlc_list = [[t.date_num, t.open, t.high, t.low, t.close] for t in pdh.pattern_data.tick_list]
        candlestick_ohlc(self.axes_for_candlesticks, ohlc_list, width=0.4, colorup='g')
        self.axes_for_candlesticks.xaxis_date()
        self.axes_for_candlesticks.grid()
        # self.__add_fibonacci_waves__(axis)

    def __plot_patterns__(self):
        self.__fill_plot_container_list__()
        self.__add_pattern_shapes_to_plot__()

    def __plot_min_max__(self):
        wave_tick_list = WaveTickList(pdh.pattern_data.df_min_max)
        radius_out, radius_in = self.__get_circle_radius_for_plot_min_max__(wave_tick_list.mean)
        for ticks in wave_tick_list.tick_list:
            if ticks.is_min:
                self.axes_for_candlesticks.add_patch(Circle((ticks.f_var, ticks.low), radius_out, color='r'))
            else:
                self.axes_for_candlesticks.add_patch(Circle((ticks.f_var, ticks.high), radius_out, color='g'))
        for ticks in pdh.pattern_data.tick_list_min_without_hidden_ticks:
            self.axes_for_candlesticks.add_patch(Circle((ticks.f_var, ticks.low), radius_in, color='w'))
        for ticks in pdh.pattern_data.tick_list_max_without_hidden_ticks:
            self.axes_for_candlesticks.add_patch(Circle((ticks.f_var, ticks.high), radius_in, color='w'))

    def __plot_ranges__(self):
        pattern_range_list_max = self.detector.range_detector_max.get_pattern_range_list()
        pattern_range_list_min = self.detector.range_detector_min.get_pattern_range_list()
        for ranges in pattern_range_list_max + pattern_range_list_min:
            polygon = ranges.f_param_shape
            self.__add_to_ranges_polygon_dic__(polygon, True, ranges)
            opposite_polygon_list = ranges.get_f_param_list_shapes()
            for polygon_opposite in opposite_polygon_list:
                self.__add_to_ranges_polygon_dic__(polygon_opposite, False, ranges)

    def __add_to_ranges_polygon_dic__(self, polygon: Polygon, for_main: bool, range: PatternRange):
        polygon.set_visible(False)
        polygon.set_color('r' if for_main else 'k')
        polygon.set_linewidth(1)
        self.axes_for_candlesticks.add_patch(polygon)
        for ticks in range.tick_list:
            if for_main:
                if ticks.f_var not in self.ranges_polygon_dic_list:
                    self.ranges_polygon_dic_list[ticks.f_var] = [polygon]
                else:
                    self.ranges_polygon_dic_list[ticks.f_var].append(polygon)
            else:
                if ticks.f_var not in self.ranges_opposite_polygon_dic_list:
                    self.ranges_opposite_polygon_dic_list[ticks.f_var] = [polygon]
                else:
                    self.ranges_opposite_polygon_dic_list[ticks.f_var].append(polygon)

    def __plot_fibonacci_relations__(self):
        fib_wave_tree = FibonacciWaveTree()
        fib_wave_tree.parse_tree()
        for fib_waves in fib_wave_tree.fibonacci_wave_list:
            xy = fib_waves.get_xy_parameter()
            fib_polygon = Polygon(np.array(xy), closed=False, fill=False)
            fib_polygon.set_visible(True)
            fib_polygon.set_color('r')
            fib_polygon.set_linewidth(1)
            self.axes_for_candlesticks.add_patch(fib_polygon)

    def __get_xy_parameters_for_fibonacci__(self):
        xy = []
        direction = DIR.DOWN if self.tick_list[0].low > self.tick_list[1].low else DIR.UP
        self.__append_tick_for_fibonacci__(xy, self.tick_list[0], direction)
        for index in range(1, len(self.tick_list)):
            tick_last = self.tick_list[index - 1]
            tick_current = self.tick_list[index]
            if direction == DIR.UP:
                if tick_last.range > tick_current.range:
                    direction_new = DIR.DOWN
                else:
                    direction_new = DIR.UP
            else:
                if tick_last.range > tick_current.range:
                    direction_new = DIR.DOWN
                else:
                    direction_new = DIR.UP
            if direction_new != direction:
                direction = direction_new
                self.__append_tick_for_fibonacci__(xy, tick_last, direction)
            if direction != tick_current.direction:
                direction = tick_current.direction
                self.__append_tick_for_fibonacci__(xy, tick_current, direction)
        return xy

    @staticmethod
    def __append_tick_for_fibonacci__(xy: list, tick: WaveTick, direction: str):
        xy.append([tick.f_var, tick.high if direction == DIR.DOWN else tick.low])

    def __get_circle_radius_for_plot_min_max__(self, mean_of_data: float):
        radius_out = 0.5 * mean_of_data/300
        radius_in = 0.3 * mean_of_data/300
        return radius_out, radius_in

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

    def __add_pattern_shapes_to_plot__(self):
        for pattern_plot_container in self.pattern_plot_container_loop_list.value_list:
            pattern_plot_container.add_elements_as_patch_collection(self.axes_for_candlesticks)
            pattern_plot_container.add_annotation(self.axes_for_candlesticks)
