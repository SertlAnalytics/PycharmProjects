"""
Description: This module contains the class for the interface between pattern and dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import numpy as np
from pattern_dash.pattern_shapes import MyPolygonShape, MyPolygonLineShape, MyLineShape
from sertl_analytics.constants.pattern_constants import PRD
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.mydates import MyDate
from pattern import Pattern
from pattern_trade import PatternTrade
from pattern_part import PatternPart
from pattern_range import PatternRange
from pattern_wave_tick import WaveTickList
from pattern_detector import PatternDetector
from fibonacci.fibonacci_wave import FibonacciWave


class DashInterface:
    @staticmethod
    def get_x_y_separated_for_shape(xy):
        xy_array = np.array(xy)
        x = xy_array[:, 0]
        y = xy_array[:, 1]
        # print('get_x_y_separated_for_shape:')
        # print(x)
        return x, y

    @staticmethod
    def get_tick_distance_in_date_as_number(sys_config: SystemConfiguration):
        if sys_config.period == PRD.INTRADAY:
            return MyDate.get_date_as_number_difference_from_epoch_seconds(0, sys_config.period_aggregation * 60)
        return 1

    @staticmethod
    def get_tolerance_range_for_extended_dict(sys_config: SystemConfiguration):
        return DashInterface.get_tick_distance_in_date_as_number(sys_config)/2

    @staticmethod
    def get_ellipse_width_height_for_plot_min_max(sys_config: SystemConfiguration, wave_tick_list: WaveTickList):
        if sys_config.period == PRD.DAILY:
            width_value = 0.6
        else:
            width_value = 0.6 / (sys_config.period_aggregation * 60)
        height_value = wave_tick_list.value_range / 100
        return width_value, height_value

    @staticmethod
    def get_xy_from_timestamp_to_date_str(xy):
        if type(xy) == list:
            return [(str(MyDate.get_date_from_epoch_seconds(t_val[0])), t_val[1]) for t_val in xy]
        return str(MyDate.get_date_from_epoch_seconds(xy[0])), xy[1]

    @staticmethod
    def get_xy_from_timestamp_to_time_str(xy):
        if type(xy) == list:
            return [(str(MyDate.get_time_from_epoch_seconds(t_val[0])), t_val[1]) for t_val in xy]
        return str(MyDate.get_time_from_epoch_seconds(xy[0])), xy[1]

    @staticmethod
    def get_xy_from_timestamp_to_date_time_str(xy):
        if type(xy) == list:
            return [(str(MyDate.get_date_time_from_epoch_seconds(t_val[0])), t_val[1]) for t_val in xy]
        return str(MyDate.get_date_time_from_epoch_seconds(xy[0])), xy[1]

    @staticmethod
    def get_annotation_param(pattern: Pattern):
        annotation_param = pattern.get_annotation_parameter('blue')
        annotation_param.xy = DashInterface.get_xy_from_timestamp_to_date(annotation_param.xy)
        annotation_param.xy_text = DashInterface.get_xy_from_timestamp_to_date(annotation_param.xy_text)
        return annotation_param

    @staticmethod
    def get_pattern_part_entry_shape(pattern: Pattern, color: str):
        x, y = DashInterface.get_xy_separated_from_timestamp(pattern.sys_config, pattern.xy_pattern_range)
        print('get_pattern_part_main_shape: x= {}, y={}'.format(x, y))
        return MyPolygonShape(x, y, color)

    @staticmethod
    def get_pattern_part_trade_shape(pattern: Pattern, color: str):
        x, y = DashInterface.get_xy_separated_from_timestamp(pattern.sys_config, pattern.xy_trade)
        return MyPolygonShape(x, y, color)

    @staticmethod
    def get_pattern_trade_watching_shape(pattern_trade: PatternTrade, color: str):
        return DashInterface.__get_pattern_trade_shape__(pattern_trade, color, pattern_trade.xy_for_watching)

    @staticmethod
    def get_pattern_trade_buying_shape(pattern_trade: PatternTrade, color: str):
        return DashInterface.__get_pattern_trade_shape__(pattern_trade, color, pattern_trade.xy_for_buying)

    @staticmethod
    def get_pattern_trade_selling_shape(pattern_trade: PatternTrade, color: str):
        return DashInterface.__get_pattern_trade_shape__(pattern_trade, color, pattern_trade.xy_for_selling)

    @staticmethod
    def get_pattern_trade_after_selling_shape(pattern_trade: PatternTrade, color: str):
        return DashInterface.__get_pattern_trade_shape__(pattern_trade, color, pattern_trade.xy_after_selling)

    @staticmethod
    def __get_pattern_trade_shape__(pattern_trade: PatternTrade, color: str, xy):
        if xy is None:
            return None
        x, y = DashInterface.get_xy_separated_from_timestamp(pattern_trade.sys_config, xy)
        # print('C={}: __get_pattern_trade_shape__: x={}, y={}\nxy={}'.format(color, x, y, xy))
        return MyPolygonShape(x, y, color)

    @staticmethod
    def get_fibonacci_wave_shape(sys_config: SystemConfiguration, fib_wave: FibonacciWave, color: str):
        x, y = DashInterface.get_xy_separated_from_timestamp(sys_config, fib_wave.get_xy_parameter())
        return MyPolygonLineShape(x, y, color)

    @staticmethod
    def get_indicator_wave_shape_list(detector: PatternDetector, indicator: str, color):
        xy_upper, xy_lower = detector.pdh.get_bollinger_band_xy_upper_lower_boundaries()
        x_upper, y_upper = DashInterface.get_xy_separated_from_timestamp(detector.sys_config, xy_upper)
        x_lower, y_lower = DashInterface.get_xy_separated_from_timestamp(detector.sys_config, xy_lower)
        return [MyPolygonLineShape(x_upper, y_upper, color), MyPolygonLineShape(x_lower, y_lower, color)]

    @staticmethod
    def get_f_regression_shape(pattern_part: PatternPart, color: str):
        x, y = DashInterface.get_xy_separated_from_timestamp(pattern_part.sys_config, pattern_part.xy_regression)
        return MyLineShape(x, y, color)

    @staticmethod
    def get_xy_separated_from_timestamp(sys_config: SystemConfiguration, xy):
        if sys_config.period == PRD.INTRADAY:
            xy_new = DashInterface.get_xy_from_timestamp_to_date_time_str(xy)
        else:
            xy_new = DashInterface.get_xy_from_timestamp_to_date_str(xy)
        return DashInterface.get_x_y_separated_for_shape(xy_new)

    @staticmethod
    def get_pattern_center_shape(sys_config: SystemConfiguration, pattern: Pattern):
        if sys_config.period == PRD.DAILY:
            ellipse_breadth = 10
        else:
            ellipse_breadth = 2 / (sys_config.period_aggregation * 60)
        ellipse_height = pattern.part_entry.height / 6
        xy_center = DashInterface.get_xy_from_timestamp_to_date(pattern.xy_center)
        return Ellipse(np.array(xy_center), ellipse_breadth, ellipse_height)

    @staticmethod
    def get_f_upper_shape(pattern_part: PatternPart):
        return pattern_part.stock_df.get_f_upper_shape(pattern_part.function_cont)

    @staticmethod
    def get_f_lower_shape(pattern_part: PatternPart):
        return pattern_part.stock_df.get_f_lower_shape(pattern_part.function_cont)

    @staticmethod
    def get_range_f_param_shape(pattern_range: PatternRange):
        xy_f_param = DashInterface.get_xy_from_timestamp_to_date_str(pattern_range.xy_f_param)
        return MyPolygonShape(np.array(xy_f_param), True)

    @staticmethod
    def get_range_f_param_shape_list(pattern_range: PatternRange):
        return_list = []
        for xy_f_param in pattern_range.xy_f_param_list:
            xy_f_param = DashInterface.get_xy_from_timestamp_to_date(xy_f_param)
            return_list.append(MyPolygonShape(np.array(xy_f_param), True))
        return return_list