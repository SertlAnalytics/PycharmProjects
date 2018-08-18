"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import CN, FD
from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod
from sertl_analytics.mydates import MyDate
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Ellipse
from pattern_colors import PatternColorHandler
from pattern_system_configuration import SystemConfiguration
from pattern_wave_tick import WaveTick, WaveTickList
from pattern_detector import PatternDetector
from pattern import Pattern
from pattern_part import PatternPart
from mpl_finance import candlestick_ohlc
from pattern_range import PatternRange
from fibonacci.fibonacci_wave import FibonacciWave
from pattern_plotting.patch_helper import PatchHelper
from pattern_plotting.fibonacci_patches import FibonacciWavePatch, FibonacciWavePatchContainer
from pattern_plotting.pattern_plot_container import PatternPlotContainer, PatternPlotContainerLoopList


class PatternPlotter:
    def __init__(self, sys_config: SystemConfiguration, detector: PatternDetector):
        self.sys_config = sys_config
        self.detector = detector
        self.df = self.sys_config.pdh.pattern_data.df
        self.tick_list = self.sys_config.pdh.pattern_data.tick_list
        self.symbol = self.sys_config.runtime.actual_ticker
        self.pattern_plot_container_loop_list = PatternPlotContainerLoopList()
        self.ranges_polygon_dic_list = {}
        self.ranges_opposite_polygon_dic_list = {}
        self.fibonacci_patch_container = None
        self.__fib_wave_select_tolerance_range = self.sys_config.pdh.pattern_data.height / 50
        self.__currently_visible_ranges_polygon_list = []
        self.axes_for_candlesticks = None

    def plot_data_frame(self):
        with_close_plot = self.sys_config.config.plot_close
        with_volume_plot = self.sys_config.config.plot_volume

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

        # self.axes_for_candlesticks.set_yscale('log')
        self.axes_for_candlesticks.set_ylim(self.__get_y_dlim_for_candlestick_plot__())
        self.__plot_candlesticks__()
        if self.sys_config.config.plot_min_max:
            self.__plot_min_max__()
            self.__plot_ranges__()
        self.__plot_patterns__()
        self.__plot_fibonacci_waves__()

        plt.title('{}. {} ({}) for {}'.format(
            self.sys_config.runtime.actual_number, self.sys_config.runtime.actual_ticker,
            self.sys_config.runtime.actual_ticker_name, self.__get_date_range_for_title__()))
        plt.tight_layout()
        # plt.xticks(rotation=45)
        fig.canvas.mpl_connect('button_press_event', self.__on_click__)
        fig.canvas.mpl_connect('motion_notify_event', self.__on_motion_notify__)
        self.axes_for_candlesticks.format_coord = self.__on_hover__
        plt.show()

    def __get_y_dlim_for_candlestick_plot__(self):
        range_pct = [0.99, 1.005] if self.sys_config.config.api_period == ApiPeriod.INTRADAY else [0.95, 1.02]
        return self.sys_config.pdh.pattern_data.min_value * range_pct[0], \
               self.sys_config.pdh.pattern_data.max_value * range_pct[1]

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
        tick_first = self.sys_config.pdh.pattern_data.tick_list[0]
        tick_last = self.sys_config.pdh.pattern_data.tick_list[-1]
        if self.sys_config.config.api_period == ApiPeriod.INTRADAY:
            return 'Date between "{} {}" AND "{} {}"'.format(tick_first.date_str, tick_first.time_str_for_f_var,
                                                             tick_last.date_str, tick_last.time_str_for_f_var)
        else:
            return 'Date between "{}" AND "{}"'.format(tick_first.date_str, tick_last.date_str)

    def __on_hover__(self, x, y):
        tolerance = PlotterInterface.get_tolerance_range_for_extended_dict(self.sys_config)
        tick = self.sys_config.pdh.pattern_data.tick_by_date_num_ext_dic.get_value_by_dict_key(x, tolerance)
        if tick is None:
            return ''
        else:
            if self.sys_config.config.api_period == ApiPeriod.INTRADAY:
                date_obj = MyDate.get_date_time_from_epoch_seconds(tick.f_var)
                date_time_str = '{} {}'.format(date_obj.date(), str(date_obj.time())[:5])
            else:
                date_time_str = tick.date
            return '{} ({:3.0f} / {:6.0f}): [{:5.1f}; {:5.1f}]; vol={:8.0f}(t); y={:0.2f}'.format(
                date_time_str, tick.position, tick.f_var, tick.low, tick.high, tick.volume / 1000, y)

    def __on_click__(self, event):
        self.pattern_plot_container_loop_list.show_only_selected_containers(event)

    def __on_motion_notify__(self, event):
        self.__reset_patch_lists__(event)
        self.__handle_visibility_for_range_polygons__(event)
        self.__handle_visibility_for_fibonacci_waves__(event)
        # self.__print_current_selected_patch__(event)

    def __print_current_selected_patch__(self, event):
        for patches in self.axes_for_candlesticks.patches:
            cont, dic = patches.contains(event)
            if cont:
                print(patches)

    def __reset_patch_lists__(self, event):
        self.__hide_range_polygons__(event)
        self.__reset_fibonacci_waves__(event)

    def __handle_visibility_for_fibonacci_waves__(self, event):
        draw_canvas = False
        tolerance_range = self.__fib_wave_select_tolerance_range
        x, y = event.xdata, event.ydata
        for patches in self.axes_for_candlesticks.patches:
            if patches.__class__.__name__ == 'Polygon':
                cont, dic = patches.contains(event)
                if cont:
                    polygon_id = PatchHelper.get_id_for_polygon(patches)
                    if self.fibonacci_patch_container.contains_patch_id(polygon_id):
                        if PatchHelper.is_xy_close_to_polygon(x, y, patches, tolerance_range):
                            fib_patch_from_container = self.fibonacci_patch_container.get_patch_by_id(polygon_id)
                            fib_patch_from_container.select_fib_wave()
                            draw_canvas = True
                            break
        if draw_canvas:
            event.canvas.draw()

    def __reset_fibonacci_waves__(self, event):
        if self.fibonacci_patch_container.reset_selected_patches():
            event.canvas.draw()

    def __handle_visibility_for_range_polygons__(self, event):
        draw_canvas = False
        for patches in self.axes_for_candlesticks.patches:
            if patches.__class__.__name__ == 'Ellipse':
                cont, dic = patches.contains(event)
                if cont:
                    tick = self.sys_config.pdh.pattern_data.get_tick_by_date_num(patches.center[0])
                    if self.__show_ranges_polygons__(tick):
                        draw_canvas = True
                    break
        if draw_canvas:
            event.canvas.draw()

    def __hide_range_polygons__(self, event):
        if len(self.__currently_visible_ranges_polygon_list) == 0:
            return
        for polygon in self.__currently_visible_ranges_polygon_list:
            polygon.set_visible(False)
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

    def __plot_close__(self, axis):
        axis.plot(self.df.loc[:, CN.TIMESTAMP], self.df.loc[:, CN.CLOSE])
        axis.grid()
        axis.legend(loc='upper left')

    def __plot_candlesticks__(self):
        if self.sys_config.config.api_period == ApiPeriod.INTRADAY:
            ohlc_list = [[t.date_num, t.open, t.high, t.low, t.close] for t in self.sys_config.pdh.pattern_data.tick_list]
            width = 0.4 * (ohlc_list[1][0] - ohlc_list[0][0])
            candlestick_ohlc(self.axes_for_candlesticks, ohlc_list, width=width, colorup='g')
            self.axes_for_candlesticks.xaxis_date()
        else:
            ohlc_list = [[t.date_num, t.open, t.high, t.low, t.close] for t in self.sys_config.pdh.pattern_data.tick_list]
            candlestick_ohlc(self.axes_for_candlesticks, ohlc_list, width=0.4, colorup='g')
            self.axes_for_candlesticks.xaxis_date()
        self.axes_for_candlesticks.grid()

    def __plot_patterns__(self):
        self.__fill_plot_container_list__()
        self.__add_pattern_shapes_to_plot__()

    def __plot_min_max__(self):
        wave_tick_list = WaveTickList(self.sys_config.pdh.pattern_data.df_min_max)
        width, height = PlotterInterface.get_ellipse_width_height_for_plot_min_max(self.sys_config, wave_tick_list)
        for ticks in wave_tick_list.tick_list:
            x = MyDate.get_date_as_number_from_epoch_seconds(ticks.f_var)
            if ticks.is_min:
                self.axes_for_candlesticks.add_patch(Ellipse((x, ticks.low), width, height, color='r'))
            else:
                self.axes_for_candlesticks.add_patch(Ellipse((x, ticks.high), width, height, color='g'))
        # fill some ellipses with color white
        width, height =  width/2, height/2
        for ticks in self.sys_config.pdh.pattern_data.tick_list_min_without_hidden_ticks:
            self.axes_for_candlesticks.add_patch(Ellipse((ticks.f_var, ticks.low), width, height, color='w'))
        for ticks in self.sys_config.pdh.pattern_data.tick_list_max_without_hidden_ticks:
            self.axes_for_candlesticks.add_patch(Ellipse((ticks.f_var, ticks.high), width, height, color='w'))

    def __plot_ranges__(self):
        pattern_range_list = self.detector.get_combined_possible_pattern_ranges()
        for ranges in pattern_range_list:
            polygon = PlotterInterface.get_range_f_param_shape(ranges)
            self.__add_to_ranges_polygon_dic__(polygon, True, ranges)
            # opposite_polygon_list = ranges.get_f_param_list_shapes()
            opposite_polygon_list = PlotterInterface.get_range_f_param_shape_list(ranges)
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

    def __plot_fibonacci_waves__(self):
        self.fibonacci_patch_container = FibonacciWavePatchContainer()
        for fib_waves in self.detector.fib_wave_tree.fibonacci_wave_list:
            if fib_waves.wave_type == FD.ASC:
                self.__plot_single_fibonacci_wave__(fib_waves, 'g')
            else:
                self.__plot_single_fibonacci_wave__(fib_waves, 'r')
        for fib_waves in  self.detector.fib_wave_tree.fibonacci_wave_forecast_collector.get_forecast_wave_list():
            if fib_waves.wave_type == FD.ASC:
                self.__plot_single_fibonacci_wave__(fib_waves, 'yellowgreen', 'Forecast')
            else:
                self.__plot_single_fibonacci_wave__(fib_waves, 'lightcoral', 'Forecast')

    def __plot_single_fibonacci_wave__(self, fib_wave: FibonacciWave, color: str, suffix: str = ''):
        if self.sys_config.config.fibonacci_detail_print:
            fib_wave.print(suffix)
        xy = fib_wave.get_xy_parameter()
        xy = PlotterInterface.get_xy_from_timestamp_to_date_number(xy)
        fib_polygon = Polygon(np.array(xy), closed=False, fill=False)
        fib_polygon.set_visible(True)
        fib_polygon.set_color(color)
        fib_polygon.set_linewidth(1)
        self.axes_for_candlesticks.add_patch(fib_polygon)
        fib_wave_patch = FibonacciWavePatch(fib_wave, fib_polygon)
        self.fibonacci_patch_container.add_patch(fib_wave_patch)
        fib_wave_patch.add_retracement_patch_list_to_axis(self.axes_for_candlesticks)

    def __plot_volume__(self, axis):
        axis.plot(self.df.loc[:, CN.DATEASNUM], self.df.loc[:, CN.VOL])
        axis.grid()
        axis.legend(loc='upper left')

    def __fill_plot_container_list__(self):
        color_handler = PatternColorHandler()
        for pattern in self.detector.pattern_list:
            if not self.sys_config.config.plot_only_pattern_with_fibonacci_waves or pattern.intersects_with_fibonacci_wave:
                color_pattern, color_trade = color_handler.get_colors_for_pattern(pattern)
                plot_container = PatternPlotContainer(PlotterInterface.get_pattern_shape_part_main(pattern), color_pattern)
                if pattern.was_breakout_done() and pattern.is_part_trade_available():
                    plot_container.add_trade_shape(PlotterInterface.get_pattern_shape_part_trade(pattern), color_trade)
                plot_container.add_center_shape(PlotterInterface.get_pattern_center_shape(pattern))
                plot_container.annotation_param = PlotterInterface.get_annotation_param(pattern)
                # plot_container.add_border_line_top_shape(pattern.part_main.get_f_upper_shape())
                # plot_container.add_border_line_bottom_shape(pattern.part_main.get_f_lower_shape())
                plot_container.add_regression_line_shape(PlotterInterface.get_f_regression_shape(pattern.part_main))
                self.pattern_plot_container_loop_list.append(plot_container)

    def __add_pattern_shapes_to_plot__(self):
        for pattern_plot_container in self.pattern_plot_container_loop_list.value_list:
            pattern_plot_container.add_elements_as_patches(self.axes_for_candlesticks)
            pattern_plot_container.add_annotation(self.axes_for_candlesticks)


class PlotterInterface:
    @staticmethod
    def get_tick_distance_in_date_as_number(sys_config: SystemConfiguration):
        if sys_config.config.api_period == ApiPeriod.INTRADAY:
            return MyDate.get_date_as_number_difference_from_epoch_seconds(0, sys_config.config.api_period_aggregation * 60)
        return 1

    @staticmethod
    def get_tolerance_range_for_extended_dict(sys_config: SystemConfiguration):
        return PlotterInterface.get_tick_distance_in_date_as_number(sys_config)/2

    @staticmethod
    def get_ellipse_width_height_for_plot_min_max(sys_config: SystemConfiguration, wave_tick_list: WaveTickList):
        if sys_config.config.api_period == ApiPeriod.DAILY:
            width_value = 0.6
        else:
            width_value = 0.6 / (sys_config.config.api_period_aggregation * 60)
        height_value = wave_tick_list.value_range / 100
        return width_value, height_value

    @staticmethod
    def get_xy_from_timestamp_to_date_number(xy):
        if type(xy) == list:
            return [(MyDate.get_date_as_number_from_epoch_seconds(t_val[0]), t_val[1]) for t_val in xy]
        return MyDate.get_date_as_number_from_epoch_seconds(xy[0]), xy[1]

    @staticmethod
    def get_annotation_param(pattern: Pattern):
        annotation_param = pattern.get_annotation_parameter('blue')
        annotation_param.xy = PlotterInterface.get_xy_from_timestamp_to_date_number(annotation_param.xy)
        annotation_param.xy_text = PlotterInterface.get_xy_from_timestamp_to_date_number(annotation_param.xy_text)
        return annotation_param

    @staticmethod
    def get_pattern_shape_part_main(pattern: Pattern):
        xy = PlotterInterface.get_xy_from_timestamp_to_date_number(pattern.xy)
        return Polygon(np.array(xy), True)

    @staticmethod
    def get_pattern_shape_part_trade(pattern: Pattern):
        xy_trade = PlotterInterface.get_xy_from_timestamp_to_date_number(pattern.xy_trade)
        return Polygon(np.array(xy_trade), True)

    @staticmethod
    def get_pattern_center_shape(pattern: Pattern):
        if pattern.sys_config.config.api_period == ApiPeriod.DAILY:
            ellipse_breadth = 10
        else:
            ellipse_breadth = 2 / (pattern.sys_config.config.api_period_aggregation * 60)
        ellipse_height = pattern.part_main.height / 6
        xy_center = PlotterInterface.get_xy_from_timestamp_to_date_number(pattern.xy_center)
        return Ellipse(np.array(xy_center), ellipse_breadth, ellipse_height)

    @staticmethod
    def get_f_regression_shape(pattern_part: PatternPart):
        xy_regression = PlotterInterface.get_xy_from_timestamp_to_date_number(pattern_part.xy_regression)
        return Polygon(np.array(xy_regression), False)

    @staticmethod
    def get_f_upper_shape(pattern_part: PatternPart):
        return pattern_part.stock_df.get_f_upper_shape(pattern_part.function_cont)

    @staticmethod
    def get_f_lower_shape(pattern_part: PatternPart):
        return pattern_part.stock_df.get_f_lower_shape(pattern_part.function_cont)

    @staticmethod
    def get_range_f_param_shape(pattern_range: PatternRange):
        xy_f_param = PlotterInterface.get_xy_from_timestamp_to_date_number(pattern_range.xy_f_param)
        return Polygon(np.array(xy_f_param), True)

    @staticmethod
    def get_range_f_param_shape_list(pattern_range: PatternRange):
        return_list = []
        for xy_f_param in pattern_range.xy_f_param_list:
            xy_f_param = PlotterInterface.get_xy_from_timestamp_to_date_number(xy_f_param)
            return_list.append(Polygon(np.array(xy_f_param), True))
        return return_list
