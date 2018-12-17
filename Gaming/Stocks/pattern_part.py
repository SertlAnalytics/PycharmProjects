"""
Description: This module contains the PatternPart classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import CN, FT, PRD
from sertl_analytics.mydates import MyDate
from sertl_analytics.mymath import MyMath
from pattern_function_container import PatternFunctionContainer
from pattern_wave_tick import WaveTick
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_data_frame import PatternDataFrame
import numpy as np


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
        self.pdh = sys_config.pdh
        self.function_cont = function_cont
        self.df = self.pdh.pattern_data.df.iloc[function_cont.position_first:function_cont.position_last + 1]
        self.tick_list = []
        self.pattern_type = self.sys_config.runtime_config.actual_pattern_type
        self.breakout = self.sys_config.runtime_config.actual_breakout
        self.pattern_range = self.sys_config.runtime_config.actual_pattern_range
        self.tick_first = None
        self.tick_last = None
        self.tick_high = None
        self.tick_low = None
        self.height = 0
        self.height_at_first_position = 0
        self.height_at_last_position = 0
        self.bound_upper = 0
        self.bound_lower = 0
        self.distance_min = 0
        self.distance_max = 0
        self.__xy = None
        self.__xy_pattern_range = None
        self.__xy_regression = None
        self.__xy_center = ()
        if self.df.shape[0] > 0:
            self.stock_df = PatternDataFrame(self.df)
            self.__calculate_values__()
            self.__set_xy_parameter__()
            self.__set_xy_pattern_range_parameter__()
            self.__set_xy_center__()
            self.__set_xy_regression__()

    def get_annotation_parameter(self, prediction_text_list: list, color: str = 'blue') -> AnnotationParameter:
        annotation_param = AnnotationParameter()
        offset = self.pdh.get_x_y_off_set_for_shape_annotation(self.__xy_center)
        annotation_param.text = self.__get_text_for_annotation__(prediction_text_list)
        annotation_param.xy = self.__xy_center
        annotation_param.xy_text = (self.__xy_center[0] + offset[0], self.__xy_center[1] + offset[1])
        annotation_param.visible = False
        annotation_param.arrow_props = {'color': color, 'width': 0.2, 'headwidth': 4}
        return annotation_param

    @property
    def length(self) -> int:
        return self.tick_last.position - self.tick_first.position

    @property
    def distance_for_trading_box(self) -> float:
        if self.height_at_last_position == 0:
            return self.std_regression
        return self.std_regression / (self.height_at_first_position/self.height_at_last_position)

    def __calculate_values__(self):
        self.tick_list = [self.pdh.pattern_data.tick_list[k] for k in range(self.function_cont.position_first,
                                                                            self.function_cont.position_last + 1)]
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
        self.height_at_last_position = f_upper_last - f_lower_last
        self.bound_upper = f_upper_last
        self.bound_lower = f_lower_last
        if self.pattern_type in [FT.TKE_BOTTOM, FT.TKE_TOP, FT.FIBONACCI_ASC, FT.FIBONACCI_DESC]:
            self.height = self.bound_upper - self.bound_lower
        else:
            self.distance_min = min(abs(f_upper_first - f_lower_first), abs(f_upper_last - f_lower_last))
            self.distance_max = max(abs(f_upper_first - f_lower_first), abs(f_upper_last - f_lower_last))
            self.height = (self.distance_min + self.distance_max) / 2

    def __set_xy_parameter__(self):
        self.__xy = self.stock_df.get_xy_parameter(self.function_cont)

    def __set_xy_pattern_range_parameter__(self):
        self.__xy_pattern_range = self.stock_df.get_xy_parameter(self.function_cont, self.pattern_range.tick_last)

    def __set_xy_regression__(self):
        self.__xy_regression = self.stock_df.get_xy_regression(self.function_cont)

    def __set_xy_center__(self):
        self.__xy_center = self.stock_df.get_xy_center(self.function_cont.f_regression)

    @property
    def xy(self):
        return self.__xy

    @property
    def xy_pattern_range(self):
        return self.__xy_pattern_range

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
    def diff_max_min_till_breakout(self) -> float:
        position_last = self.breakout.tick_breakout.position if self.breakout else self.tick_last.position
        df_part = self.df.loc[self.tick_first.position:position_last]
        return df_part[CN.HIGH].max() - df_part[CN.LOW].min()

    @property
    def max(self):
        return self.df[CN.HIGH].max()

    @property
    def min(self):
        return self.df[CN.LOW].min()

    @property
    def std(self):  # we need the standard deviation from the mean_HL for Low and High
        return ((self.df[CN.HIGH]-self.mean).std() + (self.df[CN.LOW]-self.mean).std())/2

    @property
    def std_regression(self):  # we need the standard deviation from the regression line
        x = np.array(list(range(1, self.df.shape[0] + 1)))
        y = (self.df[CN.HIGH] + self.df[CN.LOW])/2
        return MyMath.get_standard_deviation_for_regression(x, y)

    def get_slope_values(self):
        f_upper_slope = self.function_cont.f_upper_percentage
        f_lower_slope = self.function_cont.f_lower_percentage
        f_regression_slope = self.function_cont.f_regression_percentage
        # print('u={}, l={}, reg={}'.format(f_upper_slope, f_lower_slope, f_regression_slope))
        return f_upper_slope, f_lower_slope, f_regression_slope

    def __get_text_for_annotation__(self, prediction_text_list: list):
        annotations_as_dict = self.get_annotation_text_as_dict(prediction_text_list)
        annotation_text_list = ['{}: {}'.format(key, values) for key, values in annotations_as_dict.items()]
        return '\n'.join(annotation_text_list)

    def get_annotation_text_as_dict(self, prediction_text_list: list) -> dict:
        std_dev = round(self.df[CN.CLOSE].std(), 2)
        f_upper_percent, f_lower_percent, f_reg_percent = self.get_slope_values()
        if self.sys_config.period == PRD.INTRADAY:
            date_str_first = self.tick_first.time_str_for_f_var
            date_str_last = self.tick_last.time_str_for_f_var
        else:
            date_str_first = self.tick_first.date_str_for_f_var
            date_str_last = self.tick_last.date_str_for_f_var

        pattern = '{}: {} - {} ({})'.format(self.pattern_type, date_str_first, date_str_last, len(self.tick_list))

        if self.pattern_type in [FT.TKE_TOP, FT.HEAD_SHOULDER]:
            gradients = 'L={:.1f}%, Reg={:.1f}%'.format(f_lower_percent, f_reg_percent)
            height = '{:.2f}, Std_dev={:.2f}, Std_regression={:.2f}'.format(self.height, std_dev, self.std_regression)
        elif self.pattern_type in [FT.TKE_BOTTOM, FT.HEAD_SHOULDER_BOTTOM]:
            gradients = 'U={:.1f}%, Reg={:.1f}%'.format(f_upper_percent, f_reg_percent)
            height = '{:.2f}, Std_dev={:.2f}, Std_regression={:.2f}'.format(self.height, std_dev, self.std_regression)
        else:
            gradients = 'U={:.1f}%, L={:.1f}%, Reg={:.1f}%'.format(f_upper_percent, f_lower_percent, f_reg_percent)
            height = '{:.2f}, Max={:.2f}, Min={:.2f}, Std_dev={:.2f}, Std_regression={:.2f}'.format(
                self.height, self.distance_max, self.distance_min, std_dev, self.std_regression)

        return_dict = {'Pattern': pattern, 'Gradients': gradients, 'Height': height}
        if self.breakout is None:
            return_dict['Breakout'] = 'not yet'
        else:
            return_dict['Breakout'] = '{}'.format(self.breakout.get_details_for_annotations())
        self.__add_expected_trading_end_to_dict__(return_dict)
        return_dict['Range position'] = '{}'.format(self.pattern_range.position_list)
        return_dict['Prediction before breakout'] = prediction_text_list[0]
        if self.breakout:
            return_dict['Prediction after breakout'] = prediction_text_list[1]
        return return_dict

    def __add_expected_trading_end_to_dict__(self, return_dict: dict):
        if self.function_cont.f_var_cross_f_upper_f_lower > 0:
            date_forecast = MyDate.get_date_time_from_epoch_seconds(self.function_cont.f_var_cross_f_upper_f_lower)
            if self.sys_config.period == PRD.INTRADAY:
                return_dict['Expected exchange_config end'] = str(date_forecast.time())[:5]
            else:
                return_dict['Expected exchange_config end'] = str(date_forecast.date())

    def __get_slopes_by_f_param__(self) -> str:
        multiplier = 1000000
        f_upper_slope = round(self.function_cont.f_upper[1] * multiplier, 1)
        f_lower_slope = round(self.function_cont.f_lower[1] * multiplier, 1)
        f_reg_slope = round(self.function_cont.f_regression[1] * multiplier, 1)
        if self.pattern_type in [FT.TKE_TOP, FT.HEAD_SHOULDER]:
            return 'f_param: L={}%, Reg={}%'.format(f_lower_slope, f_reg_slope)
        elif self.pattern_type in [FT.TKE_BOTTOM, FT.HEAD_SHOULDER_BOTTOM]:
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


class PatternEntryPart(PatternPart):
    def __init__(self, sys_config: SystemConfiguration, function_cont: PatternFunctionContainer):
        PatternPart.__init__(self, sys_config, function_cont)


class PatternWatchPart(PatternPart):
    def __init__(self, sys_config: SystemConfiguration, function_cont: PatternFunctionContainer):
        PatternPart.__init__(self, sys_config, function_cont)


class PatternTradePart(PatternPart):
    def __init__(self, sys_config: SystemConfiguration, function_cont: PatternFunctionContainer):
        PatternPart.__init__(self, sys_config, function_cont)

