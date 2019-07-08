"""
Description: This module contains the PatternDataHandler class - central data container for patterns
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import pandas as pd
from sertl_analytics.mymath import MyMath
from sertl_analytics.constants.pattern_constants import CN, DIR
from pattern_configuration import PatternConfiguration
from pattern_data_container import PatternData, PatternDataFibonacci
from pattern_data_matrix import PatternDataMatrix


class PatternDataHandler:
    def __init__(self, config: PatternConfiguration, df: pd.DataFrame):
        self.config = config
        self.pattern_data = PatternData(self.config, df)
        self.pattern_data_fibonacci = PatternDataFibonacci(self.config, df)
        self._pattern_data_matrix = PatternDataMatrix(self.pattern_data)
        self._tolerance_pct, self._tolerance_pct_equal, self._tolerance_pct_buying = self.get_tolerance_pct_values()

    @property
    def tolerance_pct(self) -> float:
        return self._tolerance_pct

    @property
    def tolerance_pct_equal(self) -> float:
        return self._tolerance_pct_equal

    @property
    def tolerance_pct_buying(self) -> float:
        return self._tolerance_pct_buying

    def get_x_y_off_set_for_shape_annotation(self, xy_center) -> list:
        return self._pattern_data_matrix.get_x_y_off_set_for_shape_annotation(xy_center)

    def get_bollinger_band_xy_upper_lower_boundaries(self):
        distance = self.config.bollinger_band_settings['distance']
        window_size = self.config.bollinger_band_settings['window_size']
        num_of_std = self.config.bollinger_band_settings['num_of_std']
        upper_band, lower_band = self.__get_bollinger_band_boundaries_series__(window_size, num_of_std)
        reduced_position_list = self.__get_reduced_position_list__(distance)
        df_time_stamp = self.pattern_data.df[CN.TIMESTAMP]
        time_stamp_reduced = [df_time_stamp[pos] for pos in reduced_position_list]
        upper_band_reduced = [upper_band[pos] for pos in reduced_position_list]
        lower_band_reduced = [lower_band[pos] for pos in reduced_position_list]
        x = time_stamp_reduced
        y_upper = upper_band_reduced
        y_lower = lower_band_reduced
        return list(zip(x, y_upper)), list(zip(x, y_lower))

    def get_bollinger_band_boundary_break_direction(self) -> str:
        window_size = self.config.bollinger_band_settings['window_size']
        num_of_std = self.config.bollinger_band_settings['num_of_std']
        last_elements = self.config.bollinger_band_settings['last_elements']
        upper_band, lower_band = self.__get_bollinger_band_boundaries_series__(window_size, num_of_std)
        high_series = self.pattern_data.df[CN.HIGH]
        low_series = self.pattern_data.df[CN.LOW]
        for k in range(-last_elements, 0):
            if low_series.values[k] < lower_band.values[k]:
                return DIR.DOWN
            elif high_series.values[k] > upper_band.values[k]:
                return DIR.UP
        return ''

    def get_tolerance_pct_values(self):
        mean_hl = MyMath.round_smart(self.pattern_data.df[CN.MEAN_HL].mean())
        std_dev_mean_hl = MyMath.round_smart(self.pattern_data.df[CN.MEAN_HL].std())
        base_tolerance_pct = MyMath.round_smart(std_dev_mean_hl / mean_hl)
        tolerance_pct = base_tolerance_pct / 5
        tolerance_pct_equal = tolerance_pct / 2
        tolerance_pct_buying = tolerance_pct / 2
        print('tolerance_pct={:.2f}%, tolerance_pct_equal={:.2f}%, tolerance_pct_buying={:.2f}%'.format(
            tolerance_pct*100, tolerance_pct_equal*100, tolerance_pct_buying*100
        ))
        return tolerance_pct, tolerance_pct_equal, tolerance_pct_buying

    def __get_reduced_position_list__(self, distance: int):
        pos_last_element = self.pattern_data.df_length - 1
        range_end = int((pos_last_element + distance - 1)/distance)
        position_list = [1 + i * distance for i in range(0, range_end)]  # we don't want the first position (=n/a)
        if pos_last_element not in position_list:
            position_list.append(pos_last_element)
        return position_list

    def __get_bollinger_band_boundaries_series__(self, window_size: int, num_of_std: int):
        df_base = self.pattern_data.df[CN.CLOSE]
        rolling_mean = df_base.rolling(window=window_size, min_periods=1).mean()
        rolling_std = df_base.rolling(window=window_size, min_periods=1).std()
        upper_band = rolling_mean + (rolling_std * num_of_std)
        lower_band = rolling_mean - (rolling_std * num_of_std)
        return upper_band, lower_band