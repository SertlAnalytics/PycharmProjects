"""
Description: This module contains the PatternPart classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import CN, FT
from sertl_analytics.pybase.date_time import MyPyDate
from pattern_function_container import PatternFunctionContainer
from pattern_data_container import pattern_data_handler as pdh
from pattern_wave_tick import WaveTick
from pattern_configuration import runtime, debugger
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
    def __init__(self, function_cont: PatternFunctionContainer):
        self.function_cont = function_cont
        self.df = pdh.pattern_data.df.iloc[function_cont.position_first:function_cont.position_last + 1]
        self.tick_list = []
        self.pattern_type = self.function_cont.pattern_type
        self.breakout = runtime.actual_breakout
        self.pattern_range = runtime.actual_pattern_range
        self.tick_first = None
        self.tick_last = None
        self.tick_high = None
        self.tick_low = None
        self.breadth = 0
        self.breadth_first = 0
        self.bound_upper = 0
        self.bound_lower = 0
        self.distance_min = 0
        self.distance_max = 0
        self.__xy = None
        self.__xy_center = ()
        if self.df.shape[0] > 0:
            self.stock_df = PatternDataFrame(self.df)
            self.__calculate_values__()
            self.__set_xy_parameter__()
            self.__set_xy_center__()

    def get_annotation_parameter(self, color: str = 'blue'):
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
        width = 25
        if self.__xy_center[0] - pdh.pattern_data.tick_first.f_var <= width:
            return -width
        else:
            return -2*width

    def __get_annotation_offset_y__(self):
        c_value = self.__xy_center[1]
        offset = min(self.tick_high.high - c_value, c_value - self.tick_low.low)
        if pdh.pattern_data.max_value - c_value > c_value - pdh.pattern_data.min_value:
            return offset
        return - offset

    def __calculate_values__(self):
        self.tick_list = [pdh.pattern_data.tick_list[k] for k in range(self.function_cont.position_first,
                                                                        self.function_cont.position_last)]
        self.tick_first = self.tick_list[0]
        self.tick_last = self.tick_list[-1]
        self.tick_high = WaveTick(self.df.loc[self.df[CN.HIGH].idxmax(axis=0)])
        self.tick_low = WaveTick(self.df.loc[self.df[CN.LOW].idxmin(axis=0)])
        tick_helper = self.function_cont.tick_for_helper
        f_upper_first = self.function_cont.get_upper_value(self.tick_first.f_var)
        f_lower_first = self.function_cont.get_lower_value(self.tick_first.f_var)
        self.breadth_first = f_upper_first - f_lower_first
        if tick_helper is None:
            f_upper_last = self.function_cont.get_upper_value(self.tick_last.f_var)
            f_lower_last = self.function_cont.get_lower_value(self.tick_last.f_var)
        else:
            f_upper_last = self.function_cont.get_upper_value(tick_helper.f_var)
            f_lower_last = self.function_cont.get_lower_value(tick_helper.f_var)
        self.bound_upper = f_upper_last
        self.bound_lower = f_lower_last
        if self.pattern_type in [FT.TKE_DOWN, FT.TKE_UP]:
            self.breadth = round(self.bound_upper - self.bound_lower, 2)
        else:
            self.distance_min = round(min(abs(f_upper_first - f_lower_first), abs(f_upper_last - f_lower_last)), 2)
            self.distance_max = round(max(abs(f_upper_first - f_lower_first), abs(f_upper_last - f_lower_last)), 2)
            self.breadth = round((self.distance_min + self.distance_max) / 2, 2)

    def __set_xy_parameter__(self):
        self.__xy = self.stock_df.get_xy_parameter(self.function_cont)

    def __set_xy_center__(self):
        self.__xy_center = self.stock_df.get_xy_center(self.function_cont.f_regression)

    def get_f_regression_shape(self):
        return self.stock_df.get_f_regression_shape(self.function_cont.f_regression)

    def get_f_upper_shape(self):
        return self.stock_df.get_f_upper_shape(self.function_cont)

    def get_f_lower_shape(self):
        return self.stock_df.get_f_lower_shape(self.function_cont)

    @property
    def xy(self):
        return self.__xy

    @property
    def xy_center(self):
        return self.__xy_center

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
        f_upper_slope = round(self.function_cont.f_upper[1], 4)
        f_lower_slope = round(self.function_cont.f_lower[1], 4)
        relation_u_l = math.inf if f_lower_slope == 0 else round(f_upper_slope / f_lower_slope, 4)
        return f_upper_slope, f_lower_slope, relation_u_l

    def get_f_regression(self) -> np.poly1d:
        return self.stock_df.get_f_regression()

    def __get_text_for_annotation__(self):
        f_regression = self.get_f_regression()
        std_dev = round(self.df[CN.CLOSE].std(), 2)
        f_upper_slope, f_lower_slope, relation_u_l = self.get_slope_values()
        f_upper_pct = round(self.function_cont.f_upper_pct * 100, 1)
        f_lower_pct = round(self.function_cont.f_lower_pct * 100, 1)
        f_reg_pct = round(self.function_cont.f_regression_pct * 100, 1)

        type_date = 'Type={}: {} - {} ({})'.format(self.pattern_type, self.tick_first.date_str,
                                                   self.tick_last.date_str, len(self.tick_list))

        if self.pattern_type == FT.TKE_UP:
            slopes = 'Gradients: L={}%, Reg={}%'.format(f_lower_pct, f_reg_pct)
            breadth = 'Breadth={}, Std_dev={}'.format(self.breadth, std_dev)
        elif self.pattern_type == FT.TKE_DOWN:
            slopes = 'Gradients: U={}%, Reg={}%'.format(f_upper_pct, f_reg_pct)
            breadth = 'Breadth={}, Std_dev={}'.format(self.breadth, std_dev)
        else:
            slopes = 'Gradients: U={}%, L={}%, U/L={}, Reg={}%'.format(
                f_upper_pct, f_lower_pct, relation_u_l, f_reg_pct)
            breadth = 'Breadth={}, Max={}, Min={}, Std_dev={}'.format(
                self.breadth, self.distance_max, self.distance_min, std_dev)

        if self.breakout is None:
            breakout_str = 'Breakout: not yet'
        else:
            breakout_str = 'Breakout: {}'.format(self.breakout.get_details_for_annotations())

        if self.function_cont.f_var_cross_f_upper_f_lower > 0:
            date = MyPyDate.get_date_from_number(self.function_cont.f_var_cross_f_upper_f_lower - 2)
            breakout_str += '\nExpected trading end: {}'.format(date)

        breakout_str += '\nRange positions: {}'.format(self.pattern_range.position_list)

        return '{}\n{}\n{}\n{}'.format(type_date, slopes, breadth, breakout_str)

    def get_retracement_pct(self, comp_part):
        if self.tick_low.low > comp_part.tick_high.high:
            return 0
        intersection = abs(comp_part.tick_high.high - self.tick_low.low)
        return round(intersection/self.movement, 2)

    def are_values_below_linear_function(self, f_lin: np.poly1d, tolerance_pct: float = 0.01, column: CN = CN.HIGH):
        for ind, rows in self.df.iterrows():
            value_function = round(f_lin(rows[CN.DATEASNUM]), 2)
            tolerance_range = value_function * tolerance_pct
            if value_function + tolerance_range < rows[column]:
                return False
        return True

    def is_high_close_to_linear_function(self, f_lin: np.poly1d, tolerance_pct: float = 0.01):
        value_function = round(f_lin(self.tick_high.high), 2)
        mean = (value_function + self.tick_high.high)/2
        value = abs(self.tick_high.high - value_function)/mean
        return value < tolerance_pct

    def is_high_before_low(self):
        return self.tick_high.position < self.tick_low.position

    def print_data(self, part: str):
        print('\n{}: min={}, max={}, mean={}, std={} \n{}'.format(part, self.tick_low.low, self.tick_high.high,
                                                                  self.mean, self.std, self.df.head(self.ticks)))
