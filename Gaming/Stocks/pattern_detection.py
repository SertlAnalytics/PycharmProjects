"""
Description: This module detects pattern from any kind of input stream.
In the first version we concentrate our target on identifying stock pattern by given formation types.
In the second version we allow the system to find own patterns or change existing pattern constraints.
The main algorithm is CSP (constraint satisfaction problems) with binary constraints.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sertl_analytics.environment  # init some environment variables during load - for security reasons
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, ApiPeriod, ApiOutputsize
import stock_database
from mpl_finance import candlestick_ohlc
import matplotlib.dates as dt
from matplotlib.patches import Circle, Wedge, Polygon, Rectangle, Arrow, Ellipse
from matplotlib.collections import PatchCollection
from datetime import datetime, timedelta
from sertl_analytics.pybase.date_time import MyPyDate
from sertl_analytics.pybase.loop_list import LL, LoopList4Dictionaries, LoopList, ExtendedDictionary
import itertools
from pattern_constants import FT, Indices, FD, FCC, CN, SVC, CT, PSC
from pattern_configuration import PatternConfiguration, RuntimeConfiguration
from pattern_wave_tick import WaveTick
from pattern_function_container import PatternFunctionContainer
from pattern_range import PatternRange, PatternRangeDetectorMax, PatternRangeDetectorMin
from pattern_breakout import PatternBreakoutApi, PatternBreakout
from pattern_part import PatternPart
from pattern import Pattern, PatternHelper
from pattern_statistics import PatternStatistics, PatternDetectorStatisticsApi, DetectorStatistics

"""
Implementation steps:
1. Define a framework for CSPs: Unary, Binary, Global, Preferences
2. The solver should be domain independent (i.e. it doesn't matter to check stock markets or health data...)
3. Node consistency, Arc-consistency, Path consistency.
Recall:
a) A constraint satisfaction problem consists of three components:
a.1) A set of variables X = {X1, X2, ..., Xn}
a.2) A set of domains for each variable: D = {D1, D2, ..., Dn)
a.3) A set of constraints C that specifies allowable combinations of values
b) Solving the CSP: Finding the assignment(s) that satisfy all constraints.
c) Concepts: problem formulation, backtracking search, arc consistence, etc
d) We call a solution a consistent assignment
e) Factored representation: Each state has some attribute-value properties, e.g. GPS location (properties = features)
"""


class ExtendedDictionary4WaveTicks(ExtendedDictionary):
    def __init__(self, df: pd.DataFrame):
        ExtendedDictionary.__init__(self)
        self.df = df
        self.__process_df__()

    def __process_df__(self):
        for ind, rows in self.df.iterrows():
            tick = WaveTick(rows)
            self.append(tick.date_num, tick)


class DataFrameFactory:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df_length = self.df.shape[0]
        self.__add_columns__()

    def __add_columns__(self):
        pass


class DataFramePlotterFactory(DataFrameFactory):
    """
    This class has two purposes:
    1. Identify all extrema: global and local maxima and minima which is used as checkpoint for pattern detections.
    2. Identify ranges which can be used for a thorough inspection in the further process
    """
    def __init__(self, df: pd.DataFrame):
        DataFrameFactory.__init__(self, df)
        self.__length_for_global = int(self.df_length / 2)
        self.__length_for_local = 3

    def __add_columns__(self):
        self.df = self.df.assign(Date=self.df.index.map(MyPyDate.get_date_from_datetime))
        self.df = self.df.assign(DateAsNumber=self.df.index.map(dt.date2num))
        self.df[CN.DATEASNUM] = self.df[CN.DATEASNUM].apply(int)
        self.df = self.df.assign(Position=self.df.index.map(self.df.index.get_loc))
        self.df[CN.POSITION] = self.df[CN.POSITION].apply(int)


class DataFramePatternFactory(DataFrameFactory):
    """
    This class has two purposes:
    1. Identify all extrema: global and local maxima and minima which is used as checkpoint for pattern detections.
    2. Identify ranges which can be used for a thorough inspection in the further process
    """
    def __init__(self, df: pd.DataFrame):
        DataFrameFactory.__init__(self, df)
        self.__length_for_global = int(self.df_length / 2)
        self.__length_for_local = 3
        self.__init_columns_for_ticks_distance__()
        self.df_min_max = self.df[np.logical_or(self.df[CN.IS_MIN], self.df[CN.IS_MAX])]

    def __add_columns__(self):
        self.df = self.df.assign(MeanHL=round((self.df.High + self.df.Low) / 2, 2))
        self.df = self.df.assign(Date=self.df.index.map(MyPyDate.get_date_from_datetime))
        self.df = self.df.assign(DateAsNumber=self.df.index.map(dt.date2num))
        self.df[CN.DATEASNUM] = self.df[CN.DATEASNUM].apply(int)
        self.df = self.df.assign(Position=self.df.index.map(self.df.index.get_loc))
        self.df[CN.POSITION] = self.df[CN.POSITION].apply(int)
        self.df.reset_index(drop=True, inplace=True)  # get position index

    def __init_columns_for_ticks_distance__(self):
        self.__add_distance_columns__()
        self.__add_min_max_columns__()

    def __add_distance_columns__(self):
        for pos, high, before in itertools.product(range(0, self.df_length), (False, True), (False, True)):
            value = self.__get_distance__(pos, high, before)
            if high and before:
                self.df.loc[pos, CN.TICKS_BREAK_HIGH_BEFORE] = value
            elif high and not before:
                self.df.loc[pos, CN.TICKS_BREAK_HIGH_AFTER] = value
            elif not high and before:
                self.df.loc[pos, CN.TICKS_BREAK_LOW_BEFORE] = value
            elif not high and not before:
                self.df.loc[pos, CN.TICKS_BREAK_LOW_AFTER] = value

    def __add_min_max_columns__(self):
        self.df[CN.GLOBAL_MIN] = np.logical_and(self.df[CN.TICKS_BREAK_LOW_AFTER] > self.__length_for_global
                                                , self.df[CN.TICKS_BREAK_LOW_BEFORE] > self.__length_for_global)
        self.df[CN.GLOBAL_MAX] = np.logical_and(self.df[CN.TICKS_BREAK_HIGH_AFTER] > self.__length_for_global
                                                , self.df[CN.TICKS_BREAK_HIGH_BEFORE] > self.__length_for_global)
        self.df[CN.LOCAL_MIN] = np.logical_and(self.df[CN.TICKS_BREAK_LOW_AFTER] > self.__length_for_local
                                               , self.df[CN.TICKS_BREAK_LOW_BEFORE] > self.__length_for_local)
        self.df[CN.LOCAL_MAX] = np.logical_and(self.df[CN.TICKS_BREAK_HIGH_AFTER] > self.__length_for_local
                                               , self.df[CN.TICKS_BREAK_HIGH_BEFORE] > self.__length_for_local)
        self.df[CN.IS_MIN] = np.logical_or(self.df[CN.GLOBAL_MIN], self.df[CN.LOCAL_MIN])
        self.df[CN.IS_MAX] = np.logical_or(self.df[CN.GLOBAL_MAX], self.df[CN.LOCAL_MAX])

    def __get_distance__(self, row_pos: int, for_high: bool, for_before: bool) -> int:
        signature = -1 if for_before else 1
        pos_compare = row_pos + signature
        actual_value_pair = self.__get_value_pair_for_comparison__(self.df.iloc[row_pos], for_high)
        while 0 <= pos_compare < self.df_length:
            if self.__is_new_value_a_break__(actual_value_pair, pos_compare, for_high):
                break
            pos_compare += signature
        return self.df_length + 1 if (pos_compare < 0 or pos_compare >= self.df_length) else abs(row_pos - pos_compare)

    def __is_new_value_a_break__(self, actual_value_pair: list, pos_compare: int, for_high: bool) -> bool:
        """
        We need a separate script for handling when values are different to avoid min/max neighbors with the same value
        The idea behind this algorithm is that the extrema is mostly not the longest tick.
        """
        value_pair_compare = self.__get_value_pair_for_comparison__(self.df.iloc[pos_compare], for_high)
        if for_high:
            if value_pair_compare[0] > actual_value_pair[0]:
                return True
            if value_pair_compare[0] == actual_value_pair[0]:
                return value_pair_compare[1] > actual_value_pair[1]  # break if the compare has a greater low value
        else:
            if value_pair_compare[0] < actual_value_pair[0]:
                return True
            if value_pair_compare[0] == actual_value_pair[0]:
                return value_pair_compare[1] < actual_value_pair[1]  # break if the compare has a smaller high value
        return False

    def __get_value_pair_for_comparison__(self, row, for_high: bool) -> list:
        value_first = row[CN.HIGH] if for_high else row[CN.LOW]
        value_second = row[CN.LOW] if for_high else row[CN.HIGH]
        return [value_first, value_second]


class PatternDetector:
    def __init__(self, df: pd.DataFrame, df_min_max: pd.DataFrame, config: PatternConfiguration):
        self.config = config
        self.pattern_type_list = list(config.pattern_type_list)
        self.df = df
        self.df_length = self.df.shape[0]
        self.df_min_max = df_min_max
        self.df_min_max_length = self.df_min_max.shape[0]
        self.range_detector_max = PatternRangeDetectorMax
        self.range_detector_min = PatternRangeDetectorMin
        self.pattern_list = []

    @property
    def possible_pattern_ranges_available(self):
        return self.range_detector_max.are_pattern_ranges_available \
               or self.range_detector_min.are_pattern_ranges_available

    def parse_for_pattern(self):
        """
        We parse only over the actual known min-max-dataframe
        """
        self.__fill_possible_pattern_ranges__()
        possible_pattern_range_list = self.__get_combined_possible_pattern_ranges__()

        for pattern_type in self.pattern_type_list:
            self.config.runtime.actual_pattern_type = pattern_type
            for pattern_range in possible_pattern_range_list:
                # pattern_range.print_range_details()
                pattern = PatternHelper.get_pattern_for_pattern_type(pattern_type, self.df, self.df_min_max,
                                                                     pattern_range, self.config)
                if pattern.function_cont.is_valid():
                    self.__handle_single_pattern_when_parsing(pattern)

    def __handle_single_pattern_when_parsing(self, pattern: Pattern):
        can_be_added = self.__can_pattern_be_added_to_list_after_checking_next_ticks__(pattern)
        if pattern.breakout is None and not can_be_added:
            return
        self.config.runtime.actual_breakout = pattern.breakout
        pattern.add_part_main(PatternPart(pattern.function_cont, self.config))
        if pattern.is_formation_established():
            if pattern.breakout is not None:
                pattern.function_cont.breakout_direction = pattern.breakout.breakout_direction
                self.__add_part_trade__(pattern)
            self.pattern_list.append(pattern)

    def __add_part_trade__(self, pattern: Pattern):
        if not pattern.was_breakout_done():
            return None
        df = self.__get_trade_df__(pattern)
        f_upper_trade = pattern.function_cont.f_upper_trade
        f_lower_trade = pattern.function_cont.f_lower_trade
        function_cont = PatternFunctionContainer(pattern.pattern_type, df, f_lower_trade, f_upper_trade)
        part = PatternPart(function_cont, self.config)
        pattern.add_part_trade(part)

    def __get_trade_df__(self, pattern: Pattern):
        left_pos = pattern.function_cont.tick_for_helper.position
        right_pos = left_pos + pattern.pattern_range.get_maximal_trade_size_for_pattern_type(pattern.pattern_type)
        # right_pos += right_pos - left_pos  # double length
        return self.df.loc[left_pos:min(right_pos, self.df_length)]

    def __can_pattern_be_added_to_list_after_checking_next_ticks__(self, pattern: Pattern):
        tick_last = pattern.function_cont.tick_last
        pos_start = tick_last.position + 1
        number_of_positions = pattern.function_cont.number_of_positions
        counter = 0
        can_be_added = True
        for pos in range(pos_start, self.df_length):
            counter += 1
            next_tick = WaveTick(self.df.loc[pos])
            break_loop = self.__check_for_break__(pattern.function_cont, counter, number_of_positions, next_tick)
            if break_loop:
                can_be_added = False
                tick_last = next_tick
                break
            pattern.function_cont.adjust_functions_when_required(next_tick)
            if pattern.breakout is None:
                pattern.breakout = self.__get_confirmed_breakout__(pattern, tick_last, next_tick)
            tick_last = next_tick
        pattern.function_cont.add_tick_from_main_df_to_df(self.df, tick_last)
        return can_be_added

    @staticmethod
    def __check_for_break__(function_cont, counter: int, number_of_positions: int, tick: WaveTick) -> bool:
        if counter > number_of_positions:  # maximal number for the whole pattern after its building
            return True
        if not function_cont.is_regression_value_in_pattern_for_position(tick.position):
            return True
        if not function_cont.is_tick_inside_pattern_range(tick):
            return True
        return False

    def __get_confirmed_breakout__(self, pattern: Pattern, last_tick: WaveTick, next_tick: WaveTick):
        if pattern.function_cont.is_tick_breakout(next_tick):
            breakout = self.__get_pattern_breakout__(pattern, last_tick, next_tick)
            if breakout.is_breakout_a_signal():
                pattern.function_cont.set_tick_for_breakout(next_tick)
                return breakout
        return None

    def __get_pattern_breakout__(self, pattern: Pattern, tick_previous: WaveTick
                                 , tick_breakout: WaveTick) -> PatternBreakout:
        breakout_api = PatternBreakoutApi(pattern.function_cont, self.config)
        breakout_api.tick_previous = tick_previous
        breakout_api.tick_breakout = tick_breakout
        breakout_api.constraints = pattern.constraints
        return PatternBreakout(breakout_api)

    def __fill_possible_pattern_ranges__(self):
        self.range_detector_max = PatternRangeDetectorMax(self.df_min_max, self.config.range_detector_tolerance_pct)
        # self.range_detector_max.print_list_of_possible_pattern_ranges()
        self.range_detector_min = PatternRangeDetectorMin(self.df_min_max, self.config.range_detector_tolerance_pct)
        # TODO get rid of print statements

    def __get_combined_possible_pattern_ranges__(self) -> list:
        return self.range_detector_max.get_pattern_range_list()

    def print_statistics(self):
        api = self.get_statistics_api()
        print(
            'Investment change: {} -> {}, Diff: {}%'.format(api.investment_start, api.investment_working, api.diff_pct))
        print('counter_stop_loss = {}, counter_formation_OK = {}, counter_formation_NOK = {}, ticks = {}'.format(
            api.counter_stop_loss, api.counter_formation_OK, api.counter_formation_NOK, api.counter_actual_ticks
        ))

    def get_statistics_api(self):
        return PatternDetectorStatisticsApi(self.pattern_list, self.config.investment)


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
    def __init__(self, api_object, detector: PatternDetector):
        self.api_object = api_object  # StockDatabaseDataFrame or AlphavantageStockFetcher
        self.api_object_class = self.api_object.__class__.__name__
        self.detector = detector
        self.config = self.detector.config
        self.df = DataFramePlotterFactory(api_object.df).df
        self.df_data = api_object.df_data
        self.column_data = api_object.column_data
        self.df_volume = api_object.df_volume
        self.column_volume = api_object.column_volume
        self.symbol = api_object.symbol
        self.pattern_plot_container_loop_list = PatternPlotContainerLoopList()
        self.axes = None
        self.tick_by_date_num_ext_dic = ExtendedDictionary4WaveTicks(self.df)
        # TODO ext dic

    def plot_data_frame(self):
        with_close_plot = False
        with_volume_plot = False

        if with_close_plot:
            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 10), sharex='all')
            self.__plot_close__(axes[0])
            self.__plot_candlesticks__(axes[1])
            self.__plot_patterns__(axes[1])
            self.__plot_volume__(axes[2])
        else:
            if with_volume_plot:
                fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 7), sharex='all')
                self.__plot_candlesticks__(axes[0])
                self.__plot_patterns__(axes[0])
                self.__plot_volume__(axes[1])
            else:
                fig, axes = plt.subplots(figsize=(15, 7))
                self.axes = axes
                self.__plot_candlesticks__(axes)
                self.__plot_patterns__(axes)

        plt.title('{}. {} ({}) for {}'.format(self.config.runtime.actual_number, self.config.runtime.actual_ticker
                            , self.config.runtime.actual_ticker_name, self.__get_date_range_for_title__()))
        plt.tight_layout()
        plt.xticks(rotation=45)
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
        tick = self.tick_by_date_num_ext_dic.get_value(int(x + 0.5))
        return '{} ({:3.0f}): [{:5.1f}; {:5.1f}]; vol={:8.0f}(t); y={:0.2f}'.format(
            tick.date_str, tick.position, tick.low, tick.high, tick.volume/1000, y)

    def __plot_close__(self, axis):
        plot_01 = self.df_data[[self.column_data]].plot(ax=axis)
        plot_01.legend(loc='upper left')

    def __plot_candlesticks__(self, axis):
        ohlc_list = []
        for ind, rows in self.df.iterrows():
            append_me = int(dt.date2num(ind)), rows[CN.OPEN], rows[CN.HIGH], rows[CN.LOW], rows[CN.CLOSE]
            ohlc_list.append(append_me)
        chart = candlestick_ohlc(axis, ohlc_list, width=0.4, colorup='g')
        axis.xaxis_date()
        axis.grid()
        # self.__add_fibonacci_waves__(axis)

    def __plot_patterns__(self, axis):
        self.__fill_plot_container_list__()
        self.__add_pattern_shapes_to_plot__(axis)

    def __plot_volume__(self, axis):
        self.df_volume.plot(ax=axis, title=self.column_volume)

    def __fill_plot_container_list__(self):
        color_handler = FormationColorHandler()
        for pattern in self.detector.pattern_list:
            color_pattern, color_trade = color_handler.get_colors_for_formation(pattern)
            plot_container = PatternPlotContainer(pattern.get_shape_part_main(), color_pattern)
            if pattern.was_breakout_done() and pattern.is_part_trade_available():
                plot_container.add_trade_shape(pattern.get_shape_part_trade(), color_trade)
            plot_container.add_center_shape(pattern.get_center_shape())
            plot_container.annotation_param = pattern.get_annotation_parameter(True, 'blue')
            # plot_container.add_border_line_top_shape(pattern.part_main.get_f_upper_shape())
            # plot_container.add_border_line_bottom_shape(pattern.part_main.get_f_lower_shape())
            plot_container.add_regression_line_shape(pattern._part_main.get_f_regression_shape())
            self.pattern_plot_container_loop_list.append(plot_container)

    def __add_pattern_shapes_to_plot__(self, ax):
        for pattern_plot_container in self.pattern_plot_container_loop_list.value_list:
            pattern_plot_container.add_elements_as_patch_collection(ax)
            pattern_plot_container.add_annotation(ax)


class PatternController:
    def __init__(self, config: PatternConfiguration):
        self.config = config
        self.detector_statistics = DetectorStatistics()
        self.pattern_statistics = PatternStatistics()
        self.stock_db = None
        self.plotter_input_obj = None
        self.df_data = None
        self.__excel_file_with_test_data = ''
        self.df_test_data = None
        self.loop_list_ticker = None  # format of an entry (ticker, and_clause, number)
        self.__start_row = 0
        self.__end_row = 0

    def run_pattern_checker(self, excel_file_with_test_data: str = '', start_row: int = 1, end_row: int = 0):
        self.__init_db_and_test_data__(excel_file_with_test_data, start_row, end_row)
        self.__init_loop_list_for_ticker__()

        for value_dic in self.loop_list_ticker.value_list:
            ticker = value_dic[LL.TICKER]
            self.__add_runtime_parameter_to_config__(value_dic)
            print('\nProcessing {} ({})...\n'.format(ticker, self.config.runtime.actual_ticker_name))
            if config.get_data_from_db:
                and_clause = value_dic[LL.AND_CLAUSE]
                stock_db_df_obj = stock_database.StockDatabaseDataFrame(self.stock_db, ticker, and_clause)
                self.plotter_input_obj = stock_db_df_obj
                self.df_data = stock_db_df_obj.df_data
            else:
                fetcher = AlphavantageStockFetcher(ticker, self.config.api_period, self.config.api_output_size)
                self.plotter_input_obj = fetcher
                self.df_data = fetcher.df_data

            data_frame_factory = DataFramePatternFactory(self.df_data)
            detector = PatternDetector(data_frame_factory.df, data_frame_factory.df_min_max, self.config)
            detector.parse_for_pattern()
            self.__handle_statistics__(detector)

            if self.config.plot_data:
                if len(detector.pattern_list) == 0: # and not detector.possible_pattern_ranges_available:
                    print('...no formations found.')
                else:
                    plotter = PatternPlotter(self.plotter_input_obj, detector)
                    plotter.plot_data_frame()
                    # plotter.plot_data_frame_with_mpl3()

            if value_dic[LL.NUMBER] >= self.config.max_number_securities:
                break

        if config.show_final_statistics:
            self.__show_statistics__()

    def __add_runtime_parameter_to_config__(self, entry_dic: dict):
        self.config.runtime.actual_ticker = entry_dic[LL.TICKER]
        self.config.runtime.actual_and_clause = entry_dic[LL.AND_CLAUSE]
        self.config.runtime.actual_number = entry_dic[LL.NUMBER]
        self.config.runtime.actual_ticker_name = self.config.ticker_dic[self.config.runtime.actual_ticker]

    def __show_statistics__(self):
        self.config.print()
        if self.config.statistics_excel_file_name == '':
            self.pattern_statistics.print_overview()
            self.detector_statistics.print_overview()
        else:
            writer = pd.ExcelWriter(self.config.statistics_excel_file_name)
            self.pattern_statistics.write_to_excel(writer, 'Formations')
            self.detector_statistics.write_to_excel(writer, 'Overview')
            print('Statistics were written to file: {}'.format(self.config.statistics_excel_file_name))
            writer.save()

    def __init_db_and_test_data__(self, excel_file_with_test_data: str, start_row: int, end_row: int):
        if self.config.get_data_from_db:
            self.stock_db = stock_database.StockDatabase()
            if excel_file_with_test_data != '':
                self.__excel_file_with_test_data = excel_file_with_test_data
                self.df_test_data = pd.ExcelFile(self.__excel_file_with_test_data).parse(0)
                self.__start_row = start_row
                self.__end_row = self.df_test_data.shape[0] if end_row == 0 else end_row

    def __init_loop_list_for_ticker__(self):
        self.loop_list_ticker = LoopList4Dictionaries()
        if self.config.get_data_from_db and self.__excel_file_with_test_data != '':
            for ind, rows in self.df_test_data.iterrows():
                if self.loop_list_ticker.counter >= self.__start_row:
                    self.config.ticker_dic[rows[PSC.TICKER]] = rows[PSC.NAME]
                    start_date = MyPyDate.get_date_from_datetime(rows[PSC.BEGIN_PREVIOUS])
                    date_end = MyPyDate.get_date_from_datetime(rows[PSC.END] + timedelta(days=rows[PSC.T_FINAL] + 20))
                    and_clause = "Date BETWEEN '{}' AND '{}'".format(start_date, date_end)
                    self.loop_list_ticker.append({LL.TICKER: rows[PSC.TICKER], LL.AND_CLAUSE: and_clause})
                if self.loop_list_ticker.counter >= self.__end_row:
                    break
        else:
            for ticker in self.config.ticker_dic:
                self.loop_list_ticker.append({LL.TICKER: ticker, LL.AND_CLAUSE: self.config.and_clause})

    def __handle_statistics__(self, detector: PatternDetector):
        for pattern in detector.pattern_list:
            self.pattern_statistics.add_entry(pattern)

        if config.show_final_statistics:
            self.detector_statistics.add_entry(self.config, detector.get_statistics_api())
        else:
            detector.print_statistics()


config = PatternConfiguration()
config.get_data_from_db = False
config.api_period = ApiPeriod.DAILY
config.pattern_type_list = FT.get_all()
config.pattern_type_list = [FT.TRIANGLE_BOTTOM]
config.plot_data = True
config.statistics_excel_file_name = 'statistics_pattern_05-31.xlsx'
config.statistics_excel_file_name = ''
config.bound_upper_value = CN.CLOSE
config.bound_lower_value = CN.CLOSE
config.breakout_over_congestion_range = False
# config.show_final_statistics = True
config.max_number_securities = 1000
config.breakout_range_pct = 0.05  # default is 0.05
config.use_index(Indices.DOW_JONES)
# config.use_own_dic({'CAT': 'Caterpillar'})  # "INTC": "Intel",  "NKE": "Nike", "V": "Visa",  "GE": "GE", MRK (Merck)
# "FCEL": "FuelCell" "KO": "Coca Cola" # "BMWYY": "BMW" NKE	Nike, "CSCO": "Nike", "AXP": "American", "WMT": "Wall mart",
# config.and_clause = "Date BETWEEN '2017-10-25' AND '2018-04-18'"
config.and_clause = "Date BETWEEN '2018-01-22' AND '2019-02-18'"
# config.and_clause = ''
config.api_output_size = ApiOutputsize.COMPACT

pattern_controller = PatternController(config)
pattern_controller.run_pattern_checker('')

# Head Shoulder: GE Date BETWEEN '2016-01-25' AND '2019-10-30'
# Triangle: Processing KO (Coca Cola)...Date BETWEEN '2017-10-25' AND '2019-10-30'
"""
'CAT': 'Caterpillar'
"""

