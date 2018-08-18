"""
Description: This module contains the PatternPart classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import CN, FT
from sertl_analytics.mymath import MyMath
from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod
from sertl_analytics.mydates import MyDate
from pattern_function_container import PatternFunctionContainer
from pattern_wave_tick import WaveTick
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_data_frame import PatternDataFrame
import numpy as np
import math


class AnnotationParameter:
    def __init__(self):
        self.text = ''
        self.xy = ()
        self.xy_text = ()
        self.arrow_props = {}
        self.visible = False

    def get_annotation(self, axes):
        annotation = axes.annotate(self.text, xy=self.xy, xytext=self.xy_text, arrowprops=self.arrow_props)
        annotation.set_visible(self.visible)
        return annotation


class PatternPart:
    def __init__(self, sys_config: SystemConfiguration, function_cont: PatternFunctionContainer):
        self.sys_config = sys_config
        self.pdh = self.sys_config.pdh
        self.function_cont = function_cont
        self.df = self.pdh.pattern_data.df.iloc[function_cont.position_first:function_cont.position_last + 1]
        self.tick_distance = self.pdh.pattern_data.tick_f_var_distance
        self.tick_list = []
        self.pattern_type = self.sys_config.runtime.actual_pattern_type
        self.breakout = self.sys_config.runtime.actual_breakout
        self.pattern_range = self.sys_config.runtime.actual_pattern_range
        self.tick_first = None
        self.tick_last = None
        self.tick_high = None
        self.tick_low = None
        self.height = 0
        self.height_at_first_position = 0
        self.bound_upper = 0
        self.bound_lower = 0
        self.distance_min = 0
        self.distance_max = 0
        self.__xy = None
        self.__xy_regression = None
        self.__xy_center = ()
        if self.df.shape[0] > 0:
            self.stock_df = PatternDataFrame(self.df)
            self.__calculate_values__()
            self.__set_xy_parameter__()
            self.__set_xy_center__()
            self.__set_xy_regression__()

    def get_annotation_parameter(self, color: str = 'blue') -> AnnotationParameter:
        annotation_param = AnnotationParameter()
        offset_x = self.__get_annotation_offset_x__()
        offset_y = self.__get_annotation_offset_y__()
        offset = [offset_x, offset_y]
        annotation_param.text = self.__get_text_for_annotation__()
        annotation_param.xy = self.__xy_center
        annotation_param.xy_text = (self.__xy_center[0] + offset[0], self.__xy_center[1] + offset[1])
        annotation_param.visible = False
        annotation_param.arrow_props = {'color': color, 'width': 0.2, 'headwidth': 4}
        return annotation_param

    @property
    def length(self):
        return self.tick_last.position - self.tick_first.position

    def __get_annotation_offset_x__(self):
        width = 25 * self.tick_distance
        if self.__xy_center[0] - self.pdh.pattern_data.tick_first.f_var <= width:
            return -width
        else:
            return -2*width

    def __get_annotation_offset_y__(self):
        c_value = self.__xy_center[1]
        offset = min(self.tick_high.high - c_value, c_value - self.tick_low.low)
        if self.pdh.pattern_data.max_value - c_value > c_value - self.pdh.pattern_data.min_value:
            return offset
        return - offset

    def __calculate_values__(self):
        self.tick_list = [self.pdh.pattern_data.tick_list[k] for k in range(self.function_cont.position_first,
                                                                            self.function_cont.position_last)]
        self.tick_first = self.tick_list[0]
        self.tick_last = self.tick_list[-1]
        self.tick_high = WaveTick(self.df.loc[self.df[CN.HIGH].idxmax(axis=0)])
        self.tick_low = WaveTick(self.df.loc[self.df[CN.LOW].idxmin(axis=0)])
        tick_breakout = self.function_cont.tick_for_breakout
        f_upper_first = self.function_cont.get_upper_value(self.tick_first.f_var)
        f_lower_first = self.function_cont.get_lower_value(self.tick_first.f_var)
        self.height_at_first_position = f_upper_first - f_lower_first
        if tick_breakout is None:
            f_upper_last = self.function_cont.get_upper_value(self.tick_last.f_var)
            f_lower_last = self.function_cont.get_lower_value(self.tick_last.f_var)
        else:
            f_upper_last = self.function_cont.get_upper_value(tick_breakout.f_var)
            f_lower_last = self.function_cont.get_lower_value(tick_breakout.f_var)
        self.bound_upper = f_upper_last
        self.bound_lower = f_lower_last
        if self.pattern_type in [FT.TKE_DOWN, FT.TKE_UP]:
            self.height = round(self.bound_upper - self.bound_lower, 2)
        else:
            self.distance_min = round(min(abs(f_upper_first - f_lower_first), abs(f_upper_last - f_lower_last)), 2)
            self.distance_max = round(max(abs(f_upper_first - f_lower_first), abs(f_upper_last - f_lower_last)), 2)
            self.height = round((self.distance_min + self.distance_max) / 2, 2)

    def __set_xy_parameter__(self):
        self.__xy = self.stock_df.get_xy_parameter(self.function_cont)

    def __set_xy_regression__(self):
        self.__xy_regression = self.stock_df.get_xy_regression(self.function_cont)

    def __set_xy_center__(self):
        self.__xy_center = self.stock_df.get_xy_center(self.function_cont.f_regression)

    @property
    def xy(self):
        return self.__xy

    @property
    def xy_center(self):
        return self.__xy_center

    @property
    def xy_regression(self):
        return self.__xy_regression

    @property
    def movement(self):
        return abs(self.tick_high.high - self.tick_low.low)

    @property
    def date_first(self):
        return self.tick_first.date

    @property
    def date_first_str(self):
        return self.tick_first.date_str

    @property
    def date_last(self):
        return self.tick_last.date

    @property
    def date_last_str(self):
        return self.tick_last.date_str

    @property
    def ticks(self):
        return self.df.shape[0]

    @property
    def mean(self):
        return self.df[CN.MEAN_HL].mean()

    @property
    def max(self):
        return self.df[CN.HIGH].max()

    @property
    def min(self):
        return self.df[CN.LOW].min()

    @property
    def std(self):  # we need the standard deviation from the mean_HL for Low and High
        return ((self.df[CN.HIGH]-self.mean).std() + (self.df[CN.LOW]-self.mean).std())/2

    def get_slope_values(self):
        f_upper_slope = self.function_cont.f_upper_percentage
        f_lower_slope = self.function_cont.f_lower_percentage
        f_regression_slope = self.function_cont.f_regression_percentage
        # print('u={}, l={}, reg={}'.format(f_upper_slope, f_lower_slope, f_regression_slope))
        return f_upper_slope, f_lower_slope, f_regression_slope

    def __get_text_for_annotation__(self):
        std_dev = round(self.df[CN.CLOSE].std(), 2)
        f_upper_percent, f_lower_percent, f_reg_percent = self.get_slope_values()
        if self.sys_config.config.api_period == ApiPeriod.INTRADAY:
            date_str_first = self.tick_first.time_str_for_f_var
            date_str_last = self.tick_last.time_str_for_f_var
        else:
            date_str_first = self.tick_first.date_str_for_f_var
            date_str_last = self.tick_last.date_str_for_f_var

        type_date = 'Type={}: {} - {} ({})'.format(self.pattern_type, date_str_first, date_str_last, len(self.tick_list))

        if self.pattern_type in [FT.TKE_UP, FT.HEAD_SHOULDER]:
            slopes = 'Gradients: L={}%, Reg={}%'.format(f_lower_percent, f_reg_percent)
            slopes_2 = 'f_param: L={}%, Reg={}%'.format(self.function_cont.f_lower[1], f_reg_percent)
            height = 'Height={}, Std_dev={}'.format(self.height, std_dev)
        elif self.pattern_type in [FT.TKE_DOWN, FT.HEAD_SHOULDER_BOTTOM]:
            slopes = 'Gradients: U={}%, Reg={}%'.format(f_upper_percent, f_reg_percent)
            height = 'Height={}, Std_dev={}'.format(self.height, std_dev)
        else:
            slopes = 'Gradients: U={}%, L={}%, Reg={}%'.format(f_upper_percent, f_lower_percent, f_reg_percent)
            height = 'Height={}, Max={}, Min={}, Std_dev={}'.format(
                self.height, self.distance_max, self.distance_min, std_dev)

        # slopes_by_param = self.__get_slopes_by_f_param__()

        if self.breakout is None:
            breakout_str = 'Breakout: not yet'
        else:
            breakout_str = 'Breakout: {}'.format(self.breakout.get_details_for_annotations())

        if self.function_cont.f_var_cross_f_upper_f_lower > 0:
            date_forecast = MyDate.get_date_time_from_epoch_seconds(self.function_cont.f_var_cross_f_upper_f_lower)
            breakout_str += '\nExpected trading end: {}'.format(
                str(date_forecast.time())[:5] if self.sys_config.config.api_period == ApiPeriod.INTRADAY
                else date_forecast.date())

        breakout_str += '\nRange positions: {}'.format(self.pattern_range.position_list)

        return '{}\n{}\n{}\n{}'.format(type_date, slopes, height, breakout_str)

    def __get_slopes_by_f_param__(self) -> str:
        multiplier = 1000000
        f_upper_slope = round(self.function_cont.f_upper[1] * multiplier, 1)
        f_lower_slope = round(self.function_cont.f_lower[1] * multiplier, 1)
        f_reg_slope = round(self.function_cont.f_regression[1] * multiplier, 1)
        if self.pattern_type in [FT.TKE_UP, FT.HEAD_SHOULDER]:
            return 'f_param: L={}%, Reg={}%'.format(f_lower_slope, f_reg_slope)
        elif self.pattern_type in [FT.TKE_DOWN, FT.HEAD_SHOULDER_BOTTOM]:
            return 'f_param: U={}%, Reg={}%'.format(f_upper_slope, f_reg_slope)
        else:
            return 'f_param: U={}%, L={}%, Reg={}%'.format(f_upper_slope, f_lower_slope, f_reg_slope)

    def get_retracement_pct(self, comp_part):
        if self.tick_low.low > comp_part.tick_high.high:
            return 0
        intersection = abs(comp_part.tick_high.high - self.tick_low.low)
        return round(intersection/self.movement, 2)

    def are_values_below_linear_function(self, f_lin: np.poly1d, tolerance_pct: float = 0.01, column: CN = CN.HIGH):
        for ind, rows in self.df.iterrows():
            value_function = round(f_lin(rows[CN.TIMESTAMP]), 2)
            tolerance_range = value_function * tolerance_pct
            if value_function + tolerance_range < rows[column]:
                return False
        return True

    def is_high_close_to_linear_function(self, f_lin: np.poly1d, tolerance_pct: float = 0.01):
        value_function = round(f_lin(self.tick_high.high), 2)
        mean = (value_function + self.tick_high.high) / 2
        value = abs(self.tick_high.high - value_function) / mean
        return value < tolerance_pct

    def is_high_before_low(self):
        return self.tick_high.position < self.tick_low.position

    def print_data(self, part: str):
        print('\n{}: min={}, max={}, mean={}, std={} \n{}'.format(part, self.tick_low.low, self.tick_high.high,
                                                                  self.mean, self.std, self.df.head(self.ticks)))
