"""
Description: This module contains the class for the interface between pattern and dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import numpy as np
from sertl_analytics.constants.pattern_constants import PRD
from sertl_analytics.mydates import MyDate
from salesman_tutti.tutti import Tutti


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
    def get_tick_distance_in_date_as_number(period: str, period_aggregation: int):
        if period == PRD.INTRADAY:
            return MyDate.get_date_as_number_difference_from_epoch_seconds(0, period_aggregation * 60)
        return 1

    @staticmethod
    def get_tolerance_range_for_extended_dict(period: str, period_aggregation: int):
        return DashInterface.get_tick_distance_in_date_as_number(period, period_aggregation)/2

    @staticmethod
    def get_ellipse_width_height_for_plot_min_max(period: str, period_aggregation: int, value_range: float):
        if period == PRD.DAILY:
            width_value = 0.6
        else:
            width_value = 0.6 / (period_aggregation * 60)
        height_value = value_range / 100
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
    def get_annotation_param(tutti: Tutti):
        annotation_param = tutti.get_annotation_parameter('blue')
        annotation_param.xy = DashInterface.get_xy_from_timestamp_to_date(annotation_param.xy)
        annotation_param.xy_text = DashInterface.get_xy_from_timestamp_to_date(annotation_param.xy_text)
        return annotation_param


