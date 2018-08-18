"""
Description: This module contains the PatternFunctionContainer class - central function calculations
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import CN, FD, FT
from sertl_analytics.mymath import MyMath, MyPoly1d
from pattern_wave_tick import WaveTick
import numpy as np
import pandas as pd
from sertl_analytics.myexceptions import MyException
from pattern_system_configuration import SystemConfiguration


class PatternFunctionContainer:
    def __init__(self, sys_config: SystemConfiguration, df: pd.DataFrame, f_lower: np.poly1d, f_upper: np.poly1d):
        self.sys_config = sys_config
        self.df = df
        self._tick_for_helper = None
        self._tick_for_breakout = None
        self._tick_first = WaveTick(self.df.iloc[0])
        self._tick_last = WaveTick(self.df.iloc[-1])
        self._f_lower = f_lower
        self._f_upper = f_upper
        self._h_lower = f_lower
        self._h_upper = f_upper
        self._f_breakout = None
        self._f_regression = self.__get_f_regression__()
        self._f_upper_percentage = 0
        self._f_lower_percentage = 0
        self._f_regression_percentage = 0
        self._f_var_cross_f_upper_f_lower = 0
        self._position_cross_f_upper_f_lower = 0
        self._breakout_direction = None
        if self.is_valid():
            self.__init_tick_for_helper__()
            self.__set_f_var_cross_f_upper_f_lower__()
            self.__init_percentage_values__()

    @property
    def number_of_positions(self):
        return self._tick_last.position - self._tick_first.position

    @property
    def position_first(self):
        return self._tick_first.position

    @property
    def position_last(self):
        return self._tick_last.position

    @property
    def tick_first(self):
        return self._tick_first

    @property
    def tick_last(self):
        return self._tick_last

    @property
    def height_start(self):
        return round(abs(self.get_upper_value(self._tick_first.f_var) - self.get_lower_value(self._tick_first.f_var)), 2)

    @property
    def height_end(self):
        return round(abs(self.get_upper_value(self._tick_last.f_var) - self.get_lower_value(self._tick_last.f_var)), 2)

    @property
    def f_var_cross_f_upper_f_lower(self):
        return self._f_var_cross_f_upper_f_lower

    @property
    def position_cross_f_upper_f_lower(self):
        return self._position_cross_f_upper_f_lower

    @property
    def f_lower(self):
        return self._f_lower

    @property
    def f_upper(self):
        return self._f_upper

    @property
    def h_lower(self):
        return self._h_lower

    @property
    def h_upper(self):
        return self._h_upper

    @property
    def f_regression(self):
        return self._f_regression

    @property
    def f_breakout(self):
        return self._f_breakout

    @property
    def f_upper_percentage(self):
        return self._f_upper_percentage

    @property
    def f_lower_percentage(self):
        return self._f_lower_percentage

    @property
    def f_regression_percentage(self):
        return self._f_regression_percentage

    def __init_percentage_values__(self):
        self._f_upper_percentage = self.__get_slope_in_decimal_percentage__(self._f_upper)
        self._f_lower_percentage = self.__get_slope_in_decimal_percentage__(self._f_lower)
        self._f_regression_percentage = self.__get_slope_in_decimal_percentage__(self._f_regression)

    def __get_slope_in_decimal_percentage__(self, func: np.poly1d):
        return MyMath.get_change_in_percentage(func(self._tick_first.f_var), func(self.tick_last.f_var), 1)

    def is_regression_value_in_pattern_for_f_var(self, f_var: int):
        return self._f_lower(f_var) <= self._f_regression(f_var) <= self._f_upper(f_var)

    def is_valid(self):
        return not(self._f_lower is None or self._f_upper is None)

    def is_tick_breakout_on_wrong_side(self, tick: WaveTick) -> bool:
        return False

    def is_tick_breakout(self, tick: WaveTick):
        upper_boundary_value = self.get_upper_value(tick.f_var)
        lower_boundary_value = self.get_lower_value(tick.f_var)
        return not (lower_boundary_value <= tick.close <= upper_boundary_value)

    def is_tick_inside_pattern_range(self, tick: WaveTick):
        """
        tick is in the pattern range <=> upper_value >= lower_value, i.e. before crossing point
        """
        return self.get_upper_value(tick.f_var) >= self.get_lower_value(tick.f_var)

    def add_tick_from_main_df_to_df(self, df_main: pd.DataFrame, tick: WaveTick):
        if tick is not None:
            self._tick_last = tick
            self.df = pd.concat([self.df, df_main.loc[tick.position:tick.position]])

    def __get_f_regression__(self) -> np.poly1d:
        np_array = np.polyfit(self.df[CN.TIMESTAMP], self.df[CN.CLOSE], 1)
        return np.poly1d([np_array[0], np_array[1]])

    def __set_f_var_cross_f_upper_f_lower__(self):
        if self._f_upper[1] < self._f_lower[1]:
            for n in range(self._tick_last.position, self._tick_last.position + 3 * self.number_of_positions):
                f_var = self._tick_last.f_var + (n - self._tick_last.position) * self.sys_config.pdh.pattern_data.tick_f_var_distance
                u = self._f_upper(f_var)
                l = self._f_lower(f_var)
                if self._f_upper(f_var) < self._f_lower(f_var):
                    self._f_var_cross_f_upper_f_lower = f_var - self.sys_config.pdh.pattern_data.tick_f_var_distance
                    self._position_cross_f_upper_f_lower = n - 1
                    break

    def __get_tick_for_helper__(self):
        return self._tick_for_helper

    def __set_tick_for_helper__(self, tick):
        self._tick_for_helper = tick
        self._h_upper = np.poly1d([0, self._f_upper(tick.f_var)])
        self._h_lower = np.poly1d([0, self._f_lower(tick.f_var)])

    tick_for_helper = property(__get_tick_for_helper__, __set_tick_for_helper__)

    def __get_tick_for_breakout__(self):
        return self._tick_for_breakout

    def __set_tick_for_breakout__(self, tick):
        self._tick_for_breakout = tick
        if tick.close > self.get_upper_value(tick.f_var):
            self._f_breakout = np.poly1d([0, self.get_upper_value(tick.f_var)])
        else:
            self._f_breakout = np.poly1d([0, self.get_lower_value(tick.f_var)])

    tick_for_breakout = property(__get_tick_for_breakout__, __set_tick_for_breakout__)

    def adjust_functions_when_required(self, tick: WaveTick):
        pass

    def get_upper_value(self, f_var: float):
        return round(self._f_upper(f_var), 2)

    def get_lower_value(self, f_var: float):
        return round(self._f_lower(f_var), 2)

    def get_tick_list_for_xy_regression_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        return [tick_first, tick_last]

    def get_tick_function_list_for_xy_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        tick_list = [tick_first, tick_first, tick_last, tick_last]
        function_list = [self.f_upper, self.f_lower, self.f_lower, self.f_upper]
        return tick_list, function_list

    def __init_tick_for_helper__(self):
        pass


class ChannelPatternFunctionContainer(PatternFunctionContainer):
    def get_tick_function_list_for_xy_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        tick_last_temp = tick_last if self.tick_for_breakout is None else self.tick_for_breakout
        tick_list = [tick_first, tick_first, tick_last_temp, tick_last_temp]
        function_list = [self.f_upper, self.f_lower, self.f_lower, self.f_upper]
        return tick_list, function_list

    def get_tick_list_for_xy_regression_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        tick_last_temp = tick_last if self.tick_for_breakout is None else self.tick_for_breakout
        return [tick_first, tick_last_temp]


class ChannelUpPatternFunctionContainer(ChannelPatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close < self.get_lower_value(tick.f_var)

    def is_tick_breakout_on_wrong_side(self, tick: WaveTick) -> bool:
        return tick.close > self.get_upper_value(tick.f_var)


class ChannelDownPatternFunctionContainer(ChannelPatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close > self.get_upper_value(tick.f_var)

    def is_tick_breakout_on_wrong_side(self, tick: WaveTick) -> bool:
        return tick.close < self.get_lower_value(tick.f_var)


class TKEUpPatternFunctionContainer(PatternFunctionContainer):
    def get_tick_function_list_for_xy_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        # print('TKEUp: self.f_var_cross_f_upper_f_lower = {}'.format(self.f_var_cross_f_upper_f_lower))
        tick_list = [tick_first, tick_last, tick_last, self.tick_for_helper, tick_first]
        function_list = [self.h_upper, self.h_upper, self.h_lower, self.h_lower, self.f_lower]
        return tick_list, function_list

    def get_tick_list_for_xy_regression_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        return [tick_first, self.tick_for_helper]

    def __init_tick_for_helper__(self):
        pos = self.df[CN.HIGH].idxmax(axis=0)
        tick = WaveTick(self.df.loc[pos])
        self.__set_tick_for_helper__(tick)

    def is_tick_breakout(self, tick: WaveTick):
        return tick.close < self.get_lower_value(tick.f_var)

    def is_tick_breakout_on_wrong_side(self, tick: WaveTick) -> bool:
        return tick.close > self.get_upper_value(tick.f_var)

    def get_lower_value(self, f_var: int):
        return round(min(self._f_lower(f_var), self._h_lower(f_var)), 2)

    def adjust_functions_when_required(self, tick: WaveTick):
        if tick.high > self._f_upper(tick.f_var):
            self._f_upper = np.poly1d([0, tick.high])
            self.__set_f_var_cross_f_upper_f_lower__()
        self.__adjust_tick_for_helper_when_required__(tick)

    def __adjust_tick_for_helper_when_required__(self, tick: WaveTick):
        if tick.high > self._tick_for_helper.high:
            self.__set_tick_for_helper__(tick)


class TKEDownPatternFunctionContainer(PatternFunctionContainer):
    def get_tick_function_list_for_xy_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        # print('TKEDown: self.f_var_cross_f_upper_f_lower = {}'.format(self.f_var_cross_f_upper_f_lower))
        tick_list = [tick_first, self.tick_for_helper, tick_last, tick_last, tick_first]
        function_list = [self.f_upper, self.h_upper, self.h_upper, self.f_lower, self.f_lower]
        return tick_list, function_list

    def get_tick_list_for_xy_regression_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        return [tick_first, self.tick_for_helper]

    def __init_tick_for_helper__(self):
        pos = self.df[CN.LOW].idxmin(axis=0)
        tick = WaveTick(self.df.loc[pos])
        self.__set_tick_for_helper__(tick)

    def is_tick_breakout(self, tick: WaveTick):
        return tick.close > self.get_upper_value(tick.f_var)

    def is_tick_breakout_on_wrong_side(self, tick: WaveTick) -> bool:
        return tick.close < self.get_lower_value(tick.f_var)

    def get_upper_value(self, f_var: int):
        return round(max(self._f_upper(f_var), self._h_upper(f_var)), 2)

    def adjust_functions_when_required(self, tick: WaveTick):
        if tick.low < self._f_lower(tick.f_var):
            self._f_lower = np.poly1d([0, tick.low])
            self.__set_f_var_cross_f_upper_f_lower__()
        self.__adjust_tick_for_helper_when_required__(tick)

    def __adjust_tick_for_helper_when_required__(self, tick: WaveTick):
        if tick.low < self._tick_for_helper.low:
            self.__set_tick_for_helper__(tick)


class TrianglePatternFunctionContainer(PatternFunctionContainer):
    def get_tick_function_list_for_xy_parameter(self, tick_first: WaveTick, tick_last: WaveTick):
        if self.f_var_cross_f_upper_f_lower > 0:
            if self.f_var_cross_f_upper_f_lower <= self.sys_config.pdh.pattern_data.tick_last.f_var:
                tick_last = self.sys_config.pdh.pattern_data.get_tick_by_pos(self.position_cross_f_upper_f_lower)
                tick_list = [tick_first, tick_last, tick_first]
                function_list = [self.f_upper, self.f_upper, self.f_lower]
            else:
                tick_last = self.sys_config.pdh.pattern_data.tick_last
                tick_list = [tick_first, tick_last, tick_last, tick_first]
                function_list = [self.f_upper, self.f_upper, self.f_lower, self.f_lower]
        else:
            tick_list = [tick_first, tick_first, tick_last, tick_last]
            function_list = [self.f_upper, self.f_lower, self.f_lower, self.f_upper]
        return tick_list, function_list


class TriangleUpPatternFunctionContainer(TrianglePatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close < self.get_lower_value(tick.f_var)

    def is_tick_breakout_on_wrong_side(self, tick: WaveTick) -> bool:
        return tick.close > self.get_upper_value(tick.f_var)


class TriangleDownPatternFunctionContainer(TrianglePatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close > self.get_upper_value(tick.f_var)

    def is_tick_breakout_on_wrong_side(self, tick: WaveTick) -> bool:
        return tick.close < self.get_lower_value(tick.f_var)


class TriangleTopPatternFunctionContainer(TrianglePatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close < self.get_lower_value(tick.f_var)

    def is_tick_breakout_on_wrong_side(self, tick: WaveTick) -> bool:
        return tick.close > self.get_upper_value(tick.f_var)


class TriangleBottomPatternFunctionContainer(TrianglePatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close > self.get_upper_value(tick.f_var)

    def is_tick_breakout_on_wrong_side(self, tick: WaveTick) -> bool:
        return tick.close < self.get_lower_value(tick.f_var)


class HeadShoulderPatternFunctionContainer(PatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close < self.get_lower_value(tick.f_var)

    def is_tick_breakout_on_wrong_side(self, tick: WaveTick) -> bool:
        return tick.close > self.get_upper_value(tick.f_var)

    def set_tick_for_helper(self, tick: WaveTick):  # parallel to neckline = f_lower through left shoulder
        self._tick_for_helper = tick
        self._h_upper = MyPoly1d.get_parallel_through_point(self._f_lower, tick.f_var, tick.high)
        self._h_lower = self._h_upper


class HeadShoulderBottomPatternFunctionContainer(PatternFunctionContainer):
    def is_tick_breakout(self, tick: WaveTick):
        return tick.close > self.get_upper_value(tick.f_var)

    def is_tick_breakout_on_wrong_side(self, tick: WaveTick) -> bool:
        return tick.close < self.get_lower_value(tick.f_var)

    def set_tick_for_helper(self, tick: WaveTick):  # parallel to neckline = f_upper through left shoulder
        self._tick_for_helper = tick
        self._h_upper = MyPoly1d.get_parallel_through_point(self._f_upper, tick.f_var, tick.low)
        self._h_lower = self._h_upper


class PatternFunctionContainerFactoryApi:
    def __init__(self, sys_config: SystemConfiguration, pattern_type: str):
        self.sys_config = sys_config
        self.pattern_type = pattern_type
        self.df_min_max = sys_config.pdh.pattern_data.df_min_max
        self.pattern_range = None
        self.constraints = None
        self.complementary_function = None
        self.function_container = None


class PatternFunctionContainerFactory:
    @staticmethod
    def get_function_container_by_api(api: PatternFunctionContainerFactoryApi):
        df_check = api.pattern_range.get_related_part_from_data_frame(api.df_min_max)
        if api.pattern_range.is_minimum_pattern_range:
            f_upper = api.complementary_function
            f_lower = api.pattern_range.f_param
        else:
            f_lower = api.complementary_function
            f_upper = api.pattern_range.f_param

        f_cont = PatternFunctionContainerFactory.get_function_container(api.sys_config, api.pattern_type, df_check, f_lower, f_upper)
        if api.pattern_type in [FT.HEAD_SHOULDER, FT.HEAD_SHOULDER_BOTTOM]:
            f_cont.set_tick_for_helper(api.pattern_range.hsf.tick_shoulder_left)
        return f_cont

    @staticmethod
    def get_function_container(sys_config: SystemConfiguration, pattern_type: str, df: pd.DataFrame, f_lower: np.poly1d, f_upper: np.poly1d):
        if pattern_type == FT.CHANNEL:
            return ChannelPatternFunctionContainer(sys_config, df, f_lower, f_upper)
        elif pattern_type == FT.CHANNEL_DOWN:
            return ChannelDownPatternFunctionContainer(sys_config, df, f_lower, f_upper)
        elif pattern_type == FT.CHANNEL_UP:
            return ChannelUpPatternFunctionContainer(sys_config, df, f_lower, f_upper)
        elif pattern_type == FT.HEAD_SHOULDER:
            return HeadShoulderPatternFunctionContainer(sys_config, df, f_lower, f_upper)
        elif pattern_type == FT.HEAD_SHOULDER_BOTTOM:
            return HeadShoulderBottomPatternFunctionContainer(sys_config, df, f_lower, f_upper)
        elif pattern_type == FT.TRIANGLE:
            return TrianglePatternFunctionContainer(sys_config, df, f_lower, f_upper)
        elif pattern_type == FT.TRIANGLE_TOP:
            return TriangleTopPatternFunctionContainer(sys_config, df, f_lower, f_upper)
        elif pattern_type == FT.TRIANGLE_BOTTOM:
            return TriangleBottomPatternFunctionContainer(sys_config, df, f_lower, f_upper)
        elif pattern_type == FT.TRIANGLE_UP:
            return TriangleUpPatternFunctionContainer(sys_config, df, f_lower, f_upper)
        elif pattern_type == FT.TRIANGLE_DOWN:
            return TriangleDownPatternFunctionContainer(sys_config, df, f_lower, f_upper)
        elif pattern_type == FT.TKE_DOWN:
            return TKEDownPatternFunctionContainer(sys_config, df, f_lower, f_upper)
        elif pattern_type == FT.TKE_UP:
            return TKEUpPatternFunctionContainer(sys_config, df, f_lower, f_upper)
        else:
            raise MyException('No pattern function container defined for pattern type "{}"'.format(pattern_type))

