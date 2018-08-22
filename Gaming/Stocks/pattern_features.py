"""
Description: This module handles the pattern features for the pattern detection application.
a) Store to DB
b) Retrieve from DB
c) Calculate predictions
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from sertl_analytics.constants.pattern_constants import FT, Indices, CN, DC
from pattern_detector import PatternDetector
from pattern_wave_tick import WaveTick
from pattern import Pattern
from pattern_database.stock_database import StockDatabase


class PatternFeatureFactory:
    def __init__(self):
        self._feature_list = DC.get_all()
        self._db = StockDatabase()
        self._detector = None
        self._df = None
        self._df_length = 0
        self.sys_config = None

    def get_feature_dict_for_detector_pattern(self, pattern: Pattern):
        feature_dict = {}
        tick_first = pattern.part_main.tick_first
        tick_last = pattern.part_main.tick_last
        tick_breakout = pattern.part_main.breakout.tick_breakout
        pos_breakout = tick_breakout.position
        pattern_length = tick_breakout.position - tick_first.position
        if tick_first.position < pattern_length or self._df_length < tick_last.position + pattern_length:
            return None
        min_max_values_dict = self._get_min_max_value_dict_(tick_first, tick_breakout, pattern_length)
        slope_upper, slope_lower, slope_regression = pattern.part_main.get_slope_values()
        feature_dict[DC.TICKER_ID] = self._detector.sys_config.runtime.actual_ticker
        feature_dict[DC.TICKER_NAME] = self._detector.sys_config.runtime.actual_ticker_name
        feature_dict[DC.PATTERN_TYPE] = pattern.pattern_type
        feature_dict[DC.PATTERN_TYPE_ID] = FT.get_id(pattern.pattern_type)
        feature_dict[DC.TS_PATTERN_TICK_FIRST] = tick_first.time_stamp
        feature_dict[DC.TS_PATTERN_TICK_LAST] = tick_last.time_stamp
        feature_dict[DC.TS_BREAKOUT] = tick_breakout.time_stamp
        feature_dict[DC.TICKS_TILL_PATTERN_FORMED] = tick_last.position - tick_first.position
        feature_dict[DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT] = tick_breakout.position - tick_last.position
        feature_dict[DC.DT_BEGIN] = tick_first.date
        feature_dict[DC.TIME_BEGIN] = tick_first.date_str
        feature_dict[DC.DT_END] = tick_last.date
        feature_dict[DC.TIME_END] = tick_last.date_str
        feature_dict[DC.TOLERANCE_PCT] = pattern.tolerance_pct
        feature_dict[DC.BREAKOUT_RANGE_MIN_PCT] = self.sys_config.config.breakout_range_pct
        feature_dict[DC.BEGIN_LOW] = pattern.function_cont.f_lower(tick_first.f_var)
        feature_dict[DC.BEGIN_HIGH] = pattern.function_cont.f_upper(tick_first.f_var)
        feature_dict[DC.END_LOW] = pattern.function_cont.f_lower(tick_last.f_var)
        feature_dict[DC.END_HIGH] = pattern.function_cont.f_upper(tick_last.f_var)
        feature_dict[DC.SLOPE_UPPER] = slope_upper
        feature_dict[DC.SLOPE_LOWER] = slope_lower
        feature_dict[DC.SLOPE_REGRESSION] = slope_regression
        feature_dict[DC.SLOPE_BREAKOUT] = 0
        feature_dict[DC.TOUCH_POINTS_TILL_BREAKOUT_HIGH] = ''
        feature_dict[DC.TOUCH_POINTS_TILL_BREAKOUT_LOW] = ''
        feature_dict[DC.BREAKOUT_DIRECTION] = pattern.part_main.breakout.tick_breakout.sign
        feature_dict[DC.VOLUME_CHANGE_AT_BREAKOUT_PCT] = pattern.part_main.breakout.tick_breakout.volume_change_pct
        feature_dict[DC.SLOPE_VOLUME_REGRESSION] = 0
        feature_dict[DC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED] = 0
        feature_dict[DC.PREVIOUS_PERIOD_HALF_UPPER_PCT] = min_max_values_dict['max_previous_half'][0]
        feature_dict[DC.PREVIOUS_PERIOD_FULL_UPPER_PCT] = min_max_values_dict['max_previous_full'][0]
        feature_dict[DC.PREVIOUS_PERIOD_HALF_LOWER_PCT] = min_max_values_dict['min_previous_half'][0]
        feature_dict[DC.PREVIOUS_PERIOD_FULL_LOWER_PCT] = min_max_values_dict['min_previous_full'][0]
        feature_dict[DC.NEXT_PERIOD_HALF_POSITIVE_PCT] = min_max_values_dict['max_next_half'][0]
        feature_dict[DC.NEXT_PERIOD_FULL_POSITIVE_PCT] = min_max_values_dict['max_next_full'][0]
        feature_dict[DC.NEXT_PERIOD_HALF_NEGATIVE_PCT] = min_max_values_dict['min_next_half'][0]
        feature_dict[DC.NEXT_PERIOD_FULL_NEGATIVE_PCT] = min_max_values_dict['min_next_full'][0]
        feature_dict[DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF] = pos_breakout - min_max_values_dict['max_next_half'][1]
        feature_dict[DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF] = pos_breakout - min_max_values_dict['min_next_half'][1]
        feature_dict[DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL] = pos_breakout - min_max_values_dict['max_next_full'][1]
        feature_dict[DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL] = pos_breakout - min_max_values_dict['min_next_full'][1]
        feature_dict[DC.AVAILABLE_FIBONACCI_END] = pattern.available_fibonacci_end_type
        feature_dict[DC.EXPECTED_WIN] = pattern.trade_result.expected_win
        feature_dict[DC.FALSE_BREAKOUT] = 0
        feature_dict[DC.EXPECTED_WIN_REACHED] = 0
        return feature_dict

    def save_patterns_to_database(self, detector: PatternDetector):
        self._detector = detector
        self._df = self._detector.df
        self._df_length = self._detector.df_length
        self.sys_config = self._detector.sys_config
        for pattern in self._detector.pattern_list:
            feature_dict = self.get_feature_dict_for_detector_pattern(pattern)
            if feature_dict is not None:
                for key, value in feature_dict.items():
                    print('{}: {}'.format(key, value))

    def _get_min_max_value_dict_(self, tick_first: WaveTick, tick_last: WaveTick, pattern_length: int):
        pattern_length_half = int(pattern_length / 2)
        pos_first = tick_first.position
        pos_last = tick_last.position
        pos_previous_full = pos_first - pattern_length
        pos_previous_half = pos_first - pattern_length_half
        pos_next_full = pos_last + pattern_length
        pos_next_half = pos_last + pattern_length_half
        value_dict = {}
        value_dict['max_previous_half'] = self._get_df_max_values_(pos_previous_full, pos_first, tick_first.high)
        value_dict['max_previous_full'] = self._get_df_max_values_(pos_previous_full, pos_first, tick_first.high)
        value_dict['min_previous_half'] = self._get_df_max_values_(pos_previous_full, pos_first, tick_first.low)
        value_dict['min_previous_full'] = self._get_df_max_values_(pos_previous_full, pos_first, tick_first.low)

        value_dict['max_next_half'] = self._get_df_max_values_(pos_last, pos_next_half, tick_first.high)
        value_dict['max_next_full'] = self._get_df_max_values_(pos_last, pos_next_full, tick_first.high)
        value_dict['min_next_half'] = self._get_df_max_values_(pos_last, pos_next_half, tick_first.low)
        value_dict['min_next_full'] = self._get_df_max_values_(pos_last, pos_next_full, tick_first.low)
        return value_dict

    def _get_df_min_values_(self, pos_begin: int, pos_end: int, ref_value: float):
        df_part = self._df.iloc[pos_begin:pos_end + 1]
        min_value = df_part[CN.LOW].min()
        min_index = df_part[CN.LOW].idxmin()
        pct = round((min_value - ref_value) / ref_value, 2)
        return pct, min_index, min_value

    def _get_df_max_values_(self, pos_begin: int, pos_end: int, ref_value: float):
        df_part = self._df.iloc[pos_begin:pos_end + 1]
        max_value = df_part[CN.LOW].max()
        max_index = df_part[CN.LOW].idxmax()
        pct = round((max_value - ref_value)/ref_value, 2)
        return pct, max_index, max_value

    def read_features_from_database(self):
        pass
