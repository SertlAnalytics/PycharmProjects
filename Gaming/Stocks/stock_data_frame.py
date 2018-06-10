"""
Description: This module contains the StockDataFrame class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_wave_tick import WaveTick
from sertl_analytics.plotter.my_plot import MyPlotHelper
import pandas as pd
import numpy as np
from matplotlib.patches import Polygon
from sertl_analytics.constants.pattern_constants import FT, CN, FD
from pattern_function_container import PatternFunctionContainer


class StockDataFrame:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.tick_first = WaveTick(self.df.iloc[0])
        self.tick_last = WaveTick(self.df.iloc[-1])

    def get_f_upper_shape(self, function_cont: PatternFunctionContainer) -> Polygon:
        return self.__get_f_param_shape__(function_cont, True)

    def get_f_lower_shape(self, function_cont: PatternFunctionContainer) -> Polygon:
        return self.__get_f_param_shape__(function_cont, False)

    def __get_f_param_shape__(self, function_cont: PatternFunctionContainer, for_upper: bool) -> Polygon:
        if function_cont.tick_for_helper is None:
            tick_list = [self.tick_first, self.tick_last]
        else:
            tick_list = [self.tick_first, function_cont.tick_for_helper, self.tick_last]
        f = function_cont.get_upper_value if for_upper else function_cont.get_lower_value
        return MyPlotHelper.get_polygon_for_tick_list(tick_list, f, False)

    def get_f_regression(self, column: str = CN.CLOSE) -> np.poly1d:
        if self.df.shape[0] < 2:
            return np.poly1d([0, 0])
        np_array = np.polyfit(self.df[CN.DATEASNUM], self.df[column], 1)
        return np.poly1d([np_array[0], np_array[1]])

    def get_f_param_shape(self, f_param: np.poly1d) -> Polygon:
        tick_list = [self.tick_first, self.tick_last]
        return MyPlotHelper.get_polygon_for_tick_list(tick_list, f_param)

    def get_f_regression_shape(self, f_regression: np.poly1d = None) -> Polygon:
        if f_regression is None:
            f_regression = self.get_f_regression()
        tick_list = [self.tick_first, self.tick_last]
        return MyPlotHelper.get_polygon_for_tick_list(tick_list, f_regression)

    def get_xy_parameter(self, function_cont: PatternFunctionContainer):
        tick_first, tick_last, tick_helper = self.tick_first, self.tick_last, function_cont.tick_for_helper
        f_upper = function_cont.f_upper
        f_lower = function_cont.f_lower
        h_upper = function_cont.h_upper
        h_lower = function_cont.h_lower
        f_upper_extended = function_cont.get_upper_value
        f_lower_extended = function_cont.get_lower_value

        if function_cont.tick_for_helper is None:
            tick_list = [tick_first, tick_first, tick_last, tick_last]
            function_list = [f_upper, f_lower, f_lower, f_upper]
        else:
            tick_helper = function_cont.tick_for_helper
            if function_cont.pattern_type == FT.TKE_UP:
                tick_list = [tick_first, tick_last, tick_last, tick_helper, tick_first]
                function_list = [h_upper, h_upper, h_lower, h_lower, f_lower]
            elif function_cont.pattern_type == FT.TKE_DOWN:
                tick_list = [tick_first, tick_helper, tick_last, tick_last, tick_first]
                function_list = [f_upper, h_upper, h_upper, f_lower, f_lower]
            elif function_cont.f_var_cross_f_upper_f_lower > 0:
                tick_list = [tick_first, tick_helper, tick_last, tick_last, tick_first]
                if function_cont.pattern_direction == FD.ASC:
                    function_list = [f_upper_extended, f_upper_extended, f_upper_extended, f_lower, f_lower]
                else:
                    function_list = [f_lower_extended, f_lower_extended, f_lower_extended, f_upper, f_upper]
            else:
                tick_list = [tick_first, tick_helper, tick_last, tick_last, tick_first]
                if function_cont.pattern_direction == FD.ASC:
                    function_list = [f_upper_extended, f_upper_extended, f_upper_extended, f_lower, f_lower]
                else:
                    function_list = [f_lower_extended, f_lower_extended, f_lower_extended, f_upper, f_upper]

        return MyPlotHelper.get_xy_parameter_for_tick_function_list(tick_list, function_list)

    def get_xy_center(self, f_regression: np.poly1d = None):
        diff_f_var = self.tick_last.f_var - self.tick_first.f_var
        middle_f_var = self.tick_first.f_var + int(diff_f_var/2)
        tick = self.get_nearest_tick_to_f_var(middle_f_var)
        if f_regression is None:
            f_regression = self.get_f_regression()
        return tick.f_var, f_regression(tick.f_var)

    def get_nearest_tick_to_f_var(self, f_var: int):
        df = self.df.assign(Distance=(abs(self.df.DateAsNumber - f_var)))
        df = df[df["Distance"] == df["Distance"].min()]
        return WaveTick(df.iloc[0])

    def get_parallel_to_function_by_low(self, func: np.poly1d) -> np.poly1d:
        pos = self.df[CN.LOW].idxmin()
        tick = WaveTick(self.df.loc[pos])
        diff = func(tick.f_var) - tick.low
        return np.poly1d([func[1], func[0] - diff])

    def get_parallel_to_function_by_high(self, func: np.poly1d) -> np.poly1d:
        pos = self.df[CN.HIGH].idxmax()
        tick = WaveTick(self.df.loc[pos])
        diff = func(tick.f_var) - tick.high
        return np.poly1d([func[1], func[0] - diff])