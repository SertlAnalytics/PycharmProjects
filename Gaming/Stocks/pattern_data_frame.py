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
from pattern_data_container import pattern_data_handler as pdh


class PatternDataFrame:
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
        tick_list, function_list = function_cont.get_tick_function_list_for_xy_parameter(self.tick_first, self.tick_last)
        return MyPlotHelper.get_xy_parameter_for_tick_function_list(tick_list, function_list)

    def get_xy_center(self, f_regression: np.poly1d = None):
        diff_f_var = self.tick_last.f_var - self.tick_first.f_var
        middle_f_var = self.tick_first.f_var + diff_f_var/2
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