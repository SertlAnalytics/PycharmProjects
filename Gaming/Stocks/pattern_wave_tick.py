"""
Description: This module contains the wave tick class - central for stoock data management
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import pandas as pd
import numpy as np
from sertl_analytics.constants.pattern_constants import CN, TT, DIR, PRD, WAVEST
from matplotlib.patches import Arrow, FancyArrow, Polygon
from sertl_analytics.mymath import MyMath, MyPoly1d
from sertl_analytics.pybase.loop_list import ExtendedDictionary
from sertl_analytics.mydates import MyDate
from datetime import datetime
import math


class WaveTick:
    def __init__(self, tick):
        self.tick = tick
        self.is_asc_fibonacci_end = False
        self.is_desc_fibonacci_end = False
        self.watch_breakout_value = 0  # used for watching periods - currently used for touch_point
        self.watch_wrong_breakout_value = 0  # used for watching periods - currently used for touch_point
        self.breakout_value = 0
        self.wrong_breakout_value = 0
        self.limit_value = 0
        self.stop_loss_value = 0
        self._position = int(self.tick[CN.POSITION]) if CN.POSITION in tick else 0
        self._wave_type_number_dict = {}

    @property
    def date(self):
        return self.tick[CN.DATE] if CN.DATE in self.tick else MyDate.get_date_from_epoch_seconds(
            self.tick[CN.TIMESTAMP])

    @property
    def time(self):
        return self.tick[CN.TIME] if CN.TIME in self.tick else MyDate.get_time_from_epoch_seconds(
            self.tick[CN.TIMESTAMP])

    @property
    def time_str(self):
        return self.tick[CN.TIME].strftime("%H:%M")

    @property
    def date_time(self):
        return self.tick[CN.DATETIME]

    @property
    def time_stamp(self) -> int:
        return int(self.tick[CN.TIMESTAMP])

    @property
    def f_var(self):
        return int(self.tick[CN.TIMESTAMP])
        # return self.tick[CN.DATEASNUM]

    @property
    def direction(self):
        return DIR.UP if self.open < self.close else DIR.DOWN

    @property
    def date_num(self):
        return self.tick[CN.DATEASNUM]

    @property
    def date_str(self):
        return self.tick[CN.DATE].strftime("%Y-%m-%d")

    @property
    def date_time_str(self):
        return '{} {}'.format(self.date, self.time)

    @property
    def position(self) -> int:
        return self._position

    @position.setter
    def position(self, value: int):
        self._position = value

    @property
    def is_max(self):
        return self.tick[CN.IS_MAX]

    @property
    def is_min(self):
        return self.tick[CN.IS_MIN]

    @property
    def is_local_max(self):
        return self.tick[CN.LOCAL_MAX]

    @property
    def is_local_min(self):
        return self.tick[CN.LOCAL_MIN]

    @property
    def is_global_max(self):
        return self.tick[CN.GLOBAL_MAX]

    @property
    def is_global_min(self):
        return self.tick[CN.GLOBAL_MIN]

    @property
    def open(self):
        return MyMath.round_smart(self.tick[CN.OPEN])

    @property
    def high(self):
        return MyMath.round_smart(self.tick[CN.HIGH])

    @property
    def low(self):
        return MyMath.round_smart(self.tick[CN.LOW])

    @property
    def close(self):
        return MyMath.round_smart(self.tick[CN.CLOSE])

    @property
    def mean(self):
        return MyMath.round_smart((self.high + self.low)/2)

    @property
    def volume(self):
        return MyMath.round_smart(self.tick[CN.VOL])

    @property
    def tick_type(self):
        if (self.high - self.low) == 0:
            return TT.NONE
        if abs((self.open - self.close) / (self.high - self.low)) < 0.2:
            return TT.DOJI
        return TT.NONE

    @property
    def date_str_for_f_var(self):
        return str(MyDate.get_date_from_epoch_seconds(self.f_var))
        # return str(MyPyDate.get_datetime_from_epoch_number(self.f_var).date())

    @property
    def time_str_for_f_var(self):
        return str(MyDate.get_time_from_epoch_seconds(self.f_var))[:5]
        # return str(MyPyDate.get_datetime_from_epoch_number(self.f_var).time())[:5]

    def add_to_wave_type_number_dict(self, wave_type: str, number: int):
        self._wave_type_number_dict[wave_type] = number

    def get_wave_number_for_wave_type(self, wave_type: str):
        if wave_type in self._wave_type_number_dict:
            return self._wave_type_number_dict[wave_type]
        return 0

    def get_forecast_volume(self, seconds_for_period: int):
        actual_time_stamp = int(datetime.now().timestamp())
        if actual_time_stamp >= self.time_stamp + seconds_for_period:
            return self.volume
        else:
            return round(self.volume * seconds_for_period/(actual_time_stamp - self.time_stamp), 2)

    def print(self):
        print('Pos: {}, Date: {}, Time: {}, High: {}, Low: {}, Close: {}, Volume: {}, Timestamp={}'.format(
            self.position, self.date, self.time, self.high, self.low, self.close, self.volume, self.time_stamp))

    def get_date_or_time_for_f_var(self, for_time: False):
        if for_time:
            return MyDate.get_datetime_from_epoch_number(self.f_var).time()
        else:
            return MyDate.get_datetime_from_epoch_number(self.f_var).date()

    def get_linear_f_params_for_high(self, tick):
        return MyPoly1d.get_poly1d(self.f_var, self.high, tick.f_var, tick.high)

    def get_linear_f_params_for_low(self, tick):
        return MyPoly1d.get_poly1d(self.f_var, self.low, tick.f_var, tick.low)

    def is_sustainable(self):
        if self.high - self.low == 0:
            return False
        return abs((self.open - self.close) / (self.high - self.low)) > 0.6

    def is_volume_rising(self, volume_compare, min_percentage: int):
        return MyMath.divide(self.volume, volume_compare) > (100 + min_percentage) / 100

    def has_gap_to(self, tick_comp):
        return self.low > tick_comp.high or self.high < tick_comp.low


class TickerWaveTickConverter:
    def __init__(self, period: str, aggregation: int, pos_last: int, time_stamp_last: int):
        self._period = period
        self._aggregation = aggregation
        self._aggregation_time_stamp_range = MyDate.get_seconds_for_period_aggregation(self._period, self._aggregation)
        self._current_position = pos_last
        self._current_time_stamp = time_stamp_last
        self._current_open = 0
        self._current_close = 0
        self._current_low = math.inf
        self._current_high = -math.inf
        self._current_volume = 0
        self._begin_time_stamp = 0
        self._current_wave_tick = None

    @property
    def current_wave_tick(self) -> WaveTick:
        return self._current_wave_tick

    def reset_variables(self):
        self._begin_time_stamp = 0
        self._current_open = 0
        self._current_close = 0
        self._current_low = math.inf
        self._current_high = -math.inf

    def can_next_ticker_be_added_to_current_wave_tick(self, ticker_time_stamp: int):
        if not self._current_wave_tick:  # to regard the first ticker
            return False
        return ticker_time_stamp - self._begin_time_stamp < self._aggregation_time_stamp_range

    def add_value_with_timestamp(self, value: float, time_stamp: int, volume=0):
        self._current_volume = volume
        if self._begin_time_stamp == 0:
            self._begin_time_stamp = time_stamp
            self._current_position += 1
            self.__set_current_time_stamp_for_new_tick__(time_stamp)

        if self._current_open == 0:
            self._current_open = value
        if self._current_high < value:
            self._current_high = value
        if self._current_low > value:
            self._current_low = value
        self._current_close = value
        if self._begin_time_stamp == 0:
            self._begin_time_stamp = time_stamp

        self._current_wave_tick = self.__get_current_tick_values_as_wave_tick__()

    def __set_current_time_stamp_for_new_tick__(self, time_stamp: int):
        while self._current_time_stamp < time_stamp:
            if self._period == PRD.DAILY:  # the values are from the current day
                if self._current_time_stamp + self._aggregation_time_stamp_range > time_stamp:
                    break
            self._current_time_stamp += self._aggregation_time_stamp_range

    def __get_current_tick_values_as_wave_tick__(self):
        value_list = [self._current_open, self._current_close, self._current_low, self._current_high,
                      self._current_volume, self._current_time_stamp, self._current_position]
        row = pd.Series(value_list, index=[CN.OPEN, CN.CLOSE, CN.LOW, CN.HIGH, CN.VOL, CN.TIMESTAMP, CN.POSITION])
        return WaveTick(row)


class WaveTickList:
    def __init__(self, df_or_list):  # input = pd.DataFrame or tick_list[]
        self.df = None
        self.tick_list = []
        self._wave_type_number_min_dict = {}
        self._wave_type_number_max_dict = {}
        if df_or_list.__class__.__name__ == 'DataFrame':
            self.__init_by_df__(df_or_list)
        else:
            self.__init_by_tick_list__(df_or_list)
        self.elements = len(self.tick_list)
        self.tick_distance_in_seconds = self.__get_tick_distance_in_seconds__()

    def __get_tick_distance_in_seconds__(self):
        if len(self.tick_list) < 2:
            return 0
        else:
            return abs(self.tick_list[0].time_stamp - self.tick_list[1].time_stamp)

    @property
    def length(self):
        return self.tick_list[-1].f_var - self.tick_list[0].f_var

    @property
    def mean(self):
        return MyMath.round_smart(np.mean([tick.mean for tick in self.tick_list])[0])

    @property
    def max(self):
        return MyMath.round_smart(np.max([tick.high for tick in self.tick_list]))

    @property
    def min(self):
        return MyMath.round_smart(np.min([tick.low for tick in self.tick_list]))

    @property
    def value_range(self):
        return MyMath.round_smart(self.max - self.min)

    @property
    def first_wave_tick(self):
        return self.tick_list[0]

    @property
    def last_wave_tick(self):
        return self.tick_list[-1]

    def fill_wave_type_number_dicts(self):
        for wave_type in WAVEST.get_waves_types_for_processing([]):
            wave_type_number_list = []
            for tick in self.tick_list:
                wave_type_number_list.append(tick.get_wave_number_for_wave_type(wave_type))
            self._wave_type_number_min_dict[wave_type] = np.min(wave_type_number_list)
            self._wave_type_number_max_dict[wave_type] = np.max(wave_type_number_list)

    def get_arrow_size_parameter_for_wave_peaks(self, wave_type: str, number_waves: int):
        height_value = self.value_range / 10
        head_length = height_value / 4
        head_width = 4000 / self.elements
        min_number, max_number = self._wave_type_number_min_dict[wave_type], self._wave_type_number_max_dict[wave_type]
        if max_number == min_number:
            factor = 1
        else:
            factor = 0.3 + 0.7 * (number_waves - min_number)/(max_number - min_number)
        return height_value * factor, head_length * factor, head_width * factor

    def get_circle_shape_parameters_for_wave_peak(self, tick: WaveTick, wave_type: str):
        number_waves = tick.get_wave_number_for_wave_type(wave_type)
        height, head_length, head_width = self.get_arrow_size_parameter_for_wave_peaks(wave_type, number_waves)
        x = tick.date_str
        y = tick.high if wave_type in [WAVEST.DAILY_ASC, WAVEST.INTRADAY_ASC] else tick.low
        r = height
        return x, y, r

    def get_xy_parameters_for_wave_peak(self, tick: WaveTick, wave_type: str, period: str, aggregation: int):
        number_waves = tick.get_wave_number_for_wave_type(wave_type)
        height, head_length, head_width = self.get_arrow_size_parameter_for_wave_peaks(wave_type, number_waves)
        ts_period = MyDate.get_seconds_for_period(days=1) if period == PRD.DAILY else \
            MyDate.get_seconds_for_period(min=aggregation)
        x = [tick.f_var - ts_period, tick.f_var, tick.f_var + ts_period]
        if wave_type in [WAVEST.DAILY_ASC, WAVEST.INTRADAY_ASC]:
            y = [tick.high + height, tick.high, tick.high + height]
        else:
            y = [tick.low - height, tick.low, tick.low - height]
        x.append(x[0])  # close the triangle
        y.append(y[0])  # close the triangle
        return list(zip(x, y))

    def get_fancy_arrow_for_wave_peak(self, tick: WaveTick, wave_type: str):
        number_waves = tick.get_wave_number_for_wave_type(wave_type)
        height, head_length, head_width = self.get_arrow_size_parameter_for_wave_peaks(wave_type, number_waves)
        x = MyDate.get_date_as_number_from_epoch_seconds(tick.f_var)
        kwargs = self.__get_kw_args_for_arrows__(wave_type)
        if wave_type == WAVEST.DAILY_ASC:
            return FancyArrow(x=x, y=tick.high + height + head_length, dx=0, dy=-height, width=1,
                              head_width=head_width, head_length=head_length, **kwargs)
        elif wave_type == WAVEST.DAILY_DESC:
            return FancyArrow(x=x, y=tick.low - height - head_length, dx=0, dy=height, width=1,
                              head_width=head_width, head_length=head_length, **kwargs)

    def get_arrow_for_wave_peak(self, tick: WaveTick, wave_type: str):
        number_waves = tick.get_wave_number_for_wave_type(wave_type)
        height, head_length, head_width = self.get_arrow_size_parameter_for_wave_peaks(wave_type, number_waves)
        x = MyDate.get_date_as_number_from_epoch_seconds(tick.f_var)
        kwargs = self.__get_kw_args_for_arrows__(wave_type)
        if wave_type == WAVEST.DAILY_ASC:
            return Arrow(x=x, y=tick.high + height, dx=0, dy=-height, width=1, **kwargs)
        elif wave_type == WAVEST.DAILY_DESC:
            return Arrow(x=x, y=tick.low - height, dx=0, dy=height, width=1, **kwargs)

    @staticmethod
    def __get_kw_args_for_arrows__(wave_type: str):
        return {'color': 'magenta'} if wave_type == WAVEST.DAILY_ASC else {'color': 'cyan'}

    def get_tick_list_as_data_frame_for_replay(self):
        tick_table = []
        for tick in self.tick_list:
            date = MyDate.get_date_from_epoch_seconds(tick.time_stamp)
            time = MyDate.get_time_from_epoch_seconds(tick.time_stamp)
            date_time = str(MyDate.get_date_time_from_epoch_seconds(tick.time_stamp))
            row = [tick.position, tick.open, tick.high, tick.low, tick.close, tick.volume,
                   date, time, date_time, tick.time_stamp]
            tick_table.append(row)
        v_array = np.array(tick_table).reshape([len(self.tick_list), 10])
        return pd.DataFrame(v_array, columns=[CN.POSITION, CN.OPEN, CN.HIGH, CN.LOW, CN.CLOSE, CN.VOL,
                                              CN.DATE, CN.TIME, CN.DATETIME, CN.TIMESTAMP])

    def add_wave_tick(self, tick: WaveTick):
        self.tick_list.append(tick)

    def replace_last_wave_tick(self, wave_tick: WaveTick):
        self.tick_list[-1] = wave_tick

    def get_simple_moving_average(self, elements: int=0, ts_breakout=0, default_value=0):
        """
        The simple moving average is calculated in this way:
        a) For all ticks before the breakout we take the lower bound value = default_value
        b) For all others we take the low
        """
        base_list = self.tick_list if elements == 0 else self.tick_list[-elements:]
        base_list_reversed = base_list[::-1]
        value_list = []
        for tick in base_list_reversed:
            if tick.time_stamp < ts_breakout:
                value_list.append(default_value)
            else:
                value_list.append(tick.open)
        return MyMath.round_smart(np.average(value_list))

    def get_markdown_text_for_second_last_wave_tick(self, period=PRD.INTRADAY):
        prev_tick = self.tick_list[-2]
        prefix = prev_tick.time if period == PRD.INTRADAY else prev_tick.date
        return '**{}:** open={}, close={}, volume={}'.format(
            prefix, prev_tick.open, prev_tick.close, prev_tick.volume)

    def get_markdown_text_for_last_wave_tick(self, volume_mean=0, period=PRD.INTRADAY):
        prev_tick = self.tick_list[-2]
        actual_tick = self.tick_list[-1]
        prefix = actual_tick.time if period == PRD.INTRADAY else actual_tick.date
        forecast_volume = MyMath.round_smart(actual_tick.get_forecast_volume(self.tick_distance_in_seconds))
        volume_change_against_last = MyMath.round_smart(forecast_volume / prev_tick.volume * 100 - 100)
        if volume_mean == 0:
            forecast_values = '{} ({:+.0f} %)'.format(forecast_volume, volume_change_against_last)
        else:
            volume_change_against_mean = MyMath.round_smart(forecast_volume / volume_mean * 100 - 100)
            forecast_values = '{} ({:+.0f} % / {:+.0f} %)'.format(
                forecast_volume, volume_change_against_mean, volume_change_against_last)
        return '**{}:** open={}, close={}, volume={}, volume forecast={}'. \
            format(prefix, actual_tick.open, actual_tick.close, actual_tick.volume, forecast_values)

    def get_list_without_hidden_ticks(self, for_high: bool, tolerance_pct: float):
        """
        removes all ticks which ara hidden by their neighbors.
        """
        remove_index_list = []
        for n in range(1, self.elements - 2):
            if self.__is_tick_hidden_by_neighbors__(for_high, n, tolerance_pct):
                remove_index_list.append(n)
        for index in reversed(remove_index_list):
            del self.tick_list[index]
        return self.tick_list

    def __is_tick_hidden_by_neighbors__(self, for_high: bool, n: int, tolerance_pct: float):
        tick_left, tick, tick_right = self.tick_list[n - 1], self.tick_list[n], self.tick_list[n + 1]
        if for_high:
            f_param_left = tick_left.get_linear_f_params_for_high(tick)
            f_param_right = tick.get_linear_f_params_for_high(tick_right)
            for m in range(n - 1):
                if self.tick_list[m].high > f_param_left(self.tick_list[m].f_var):
                    return False
            for m in range(n + 1, self.elements - 1):
                if self.tick_list[m].high > f_param_right(self.tick_list[m].f_var):
                    return False
        else:
            f_param_left = tick_left.get_linear_f_params_for_low(tick)
            f_param_right = tick.get_linear_f_params_for_low(tick_right)
            for m in range(n - 1):
                if self.tick_list[m].low < f_param_left(self.tick_list[m].f_var):
                    return False
            for m in range(n + 1, self.elements - 1):
                if self.tick_list[m].low < f_param_right(self.tick_list[m].f_var):
                    return False
        return True

    def get_boundary_f_param_list(self, f_param: np.poly1d, for_high: bool):
        """
        gets all function parameters (np.poly1d) which are boundaries for the ticks.
        """
        f_param_list = []
        tick_list_without_valleys = self.__get_tick_list_without_valleys__(self.tick_list, for_high)
        for n in range(len(tick_list_without_valleys) - 1):
            tick_left = tick_list_without_valleys[n]
            tick_right = tick_list_without_valleys[n + 1]
            if for_high:
                f_param_boundary = tick_left.get_linear_f_params_for_high(tick_right)
            else:
                f_param_boundary = tick_left.get_linear_f_params_for_low(tick_right)
            if self.__is_f_param_boundary_compliant__(f_param, f_param_boundary):
                f_param_list.append(f_param_boundary)
        return f_param_list

    def __init_by_df__(self, df: pd.DataFrame):
        self.df = df
        self.tick_list = [WaveTick(row) for ind, row in self.df.iterrows()]

    def __init_by_tick_list__(self, tick_list: list):
        self.tick_list = list(tick_list)

    def __is_f_param_boundary_compliant__(self, f_param: np.poly1d, f_param_boundary: np.poly1d) -> bool:
        offset = self.tick_list[0].f_var
        slope_dec_main = MyPoly1d.get_slope_in_decimal_percentage(f_param, offset, self.length)
        slope_dec_bound = MyPoly1d.get_slope_in_decimal_percentage(f_param_boundary, offset, self.length)
        if f_param(offset) > f_param_boundary(offset):
            slope_main_bound = MyMath.round_smart(slope_dec_main - slope_dec_bound)
        else:
            slope_main_bound = MyMath.round_smart(slope_dec_bound - slope_dec_main)
        return slope_main_bound < 0.04  # we don't accept wide opening patterns

    def __get_tick_list_without_valleys__(self, tick_list, for_high: bool):
        """
        get the tick list without any valley (i.e. the middle of three ticks is not smaller than the others for high)
        recursive call !!!
        """
        len_tick_list = len(tick_list)
        if len_tick_list <= 2:
            return tick_list
        remove_index_list = []
        for n in range(len_tick_list - 2):
            tick_left, tick_middle, tick_right = tick_list[n], tick_list[n + 1], tick_list[n + 2]
            if for_high:
                f_param = tick_left.get_linear_f_params_for_high(tick_right)
                if tick_middle.high < f_param(tick_middle.f_var):
                    remove_index_list.append(n + 1)
            else:
                f_param = tick_left.get_linear_f_params_for_low(tick_right)
                if tick_middle.low > f_param(tick_middle.f_var):
                    remove_index_list.append(n + 1)
        if len(remove_index_list) == 0:
            return tick_list
        for index in reversed(remove_index_list):
            del tick_list[index]
        return self.__get_tick_list_without_valleys__(tick_list, for_high)  # recursive call !!!


class ExtendedDictionary4WaveTicks(ExtendedDictionary):
    def __init__(self, df: pd.DataFrame, column: str = CN.DATEASNUM):
        ExtendedDictionary.__init__(self)
        self.df = df
        self.__process_df__(column)

    def __process_df__(self, column: str):
        for ind, rows in self.df.iterrows():
            tick = WaveTick(rows)
            self.append(rows[column], tick)