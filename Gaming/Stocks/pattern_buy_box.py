"""
Description: This module contains the Trading box classes. They represent the exchange_config range.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-10
"""

from sertl_analytics.constants.pattern_constants import TSTR, DC, BBT, SVC, FD, TSP
from sertl_analytics.mymath import MyMath
from pattern_wave_tick import WaveTick
from scipy import stats
from sertl_analytics.plotter.my_plot import MyPlotHelper


class BoxBuyApi:
    def __init__(self):
        self.tolerance_pct = 0
        self.tolerance_pct_buying = 0
        self.data_dict = None
        self.pattern_series_hit_details = []
        self.wave_tick_latest = None
        self.f_upper = None
        self.f_lower = None


class BoxBuy:
    def __init__(self, api: BoxBuyApi):
        self.box_type = ''
        self._api = api
        self._tolerance_pct = api.tolerance_pct
        self._tolerance_pct_buying = api.tolerance_pct_buying
        self._data_dict = api.data_dict
        self._pattern_type = self._data_dict[DC.PATTERN_TYPE]
        self._pattern_id = self._data_dict[DC.ID]
        self._ticker_id = self._data_dict[DC.TICKER_ID]
        self._range_end_value_category = api.pattern_series_hit_details[-1][0]
        self._forecast_breakout_direction = self.__get_forecast_breakout_direction__()
        self._forecast_is_false_breakout = True if self._data_dict[DC.FC_FALSE_BREAKOUT_ID] == 1 else False
        self._forecast_touch_points_top = self._data_dict[DC.FC_TOUCH_POINTS_TILL_BREAKOUT_TOP]
        self._forecast_touch_points_bottom = self._data_dict[DC.FC_TOUCH_POINTS_TILL_BREAKOUT_BOTTOM]
        self._forecast_ticks_breakout = self._data_dict[DC.FC_TICKS_TILL_BREAKOUT]
        self._wave_tick_latest = api.wave_tick_latest
        self._wave_tick_timestamp_list = [self._wave_tick_latest.time_stamp]
        self._wave_tick_list = [self._wave_tick_latest]
        self._wave_tick_upper_breakout = None
        self._wave_tick_lower_breakout = None
        self._f_upper = api.f_upper
        self._f_lower = api.f_lower
        self._buy_limit_upper = self.__get_f_upper_value_for_wave_tick__(self._wave_tick_latest)  # default
        self._buy_limit_lower = self.__get_f_lower_value_for_wave_tick__(self._wave_tick_latest)  # default
        self.__adjust_buy_limit_upper_by_wave_tick__(self._wave_tick_latest)
        self.__adjust_buy_limit_lower_by_wave_tick__(self._wave_tick_latest)
        self.__set_buy_limits_to_wave_tick__(self._wave_tick_latest)
        self._ticker_last_price_list = []
        self._ticker_last_price = 0
        self._init_parameters_()

    @property
    def buy_limit_upper(self) -> float:
        return self._buy_limit_upper

    @property
    def buy_limit_lower(self) -> float:
        return self._buy_limit_lower

    @property
    def forecast_breakout_direction(self) -> str:
        return self._forecast_breakout_direction

    @property
    def breakout_direction(self) -> str:
        if self._wave_tick_upper_breakout is not None:
            if self._wave_tick_lower_breakout is not None:  # we have breakouts in one tick in both directions
                if abs(self._wave_tick_lower_breakout.low - self._wave_tick_lower_breakout.wrong_breakout_value) <\
                        abs(self._wave_tick_lower_breakout.high - self._wave_tick_lower_breakout.breakout_value):
                    return FD.ASC
                return FD.DESC
            else:
                return FD.ASC
        elif self._wave_tick_lower_breakout is not None:
            return FD.DESC
        return self._forecast_breakout_direction

    def __get_forecast_breakout_direction__(self):
        fc_breakout_direction = self._data_dict[DC.FC_BREAKOUT_DIRECTION]
        # fc_positive_pct_list = [self._data_dict[DC.FC_HALF_POSITIVE_PCT], self._data_dict[DC.FC_FULL_POSITIVE_PCT]]
        # fc_negative_pct_list = [self._data_dict[DC.FC_HALF_NEGATIVE_PCT], self._data_dict[DC.FC_FULL_NEGATIVE_PCT]]
        # if min(fc_negative_pct_list) > max(fc_positive_pct_list):
        #     print('{}: positive_pct={}, negative_pct={}'.format(self._pattern_id, fc_positive_pct_list,
        #                                                         fc_negative_pct_list))
        #     return FD.DESC if fc_breakout_direction == FD.ASC else FD.ASC
        return fc_breakout_direction

    @property
    def latest_wave_tick(self) -> WaveTick:
        return self._wave_tick_latest

    @staticmethod
    def round(value: float):
        return MyMath.round_smart(value)

    @property
    def std(self):
        sorted_list = sorted(self._ticker_last_price_list)
        slope, intercept, r_value, p_value, std_err = stats.linregress(sorted_list, self._ticker_last_price_list)
        return std_err

    @property
    def xy(self):
        xy = MyPlotHelper.get_xy_parameter_for_replay_list(self._wave_tick_list, TSP.BUYING)
        print('buy_box.xy={}'.format(xy))
        return xy

    def _init_parameters_(self):
        pass

    def is_last_price_breakout(self, price: float) -> bool:
        return self.__is_last_price_upper_breakout__(price) or self.__is_last_price_lower_breakout__(price)

    def is_wave_tick_breakout(self, wave_tick: WaveTick) -> bool:
        high, low = wave_tick.body_high, wave_tick.body_low
        is_upper_breakout = self.__is_last_price_upper_breakout__(high)
        is_lower_breakout = self.__is_last_price_lower_breakout__(low)
        self._wave_tick_upper_breakout = wave_tick if is_upper_breakout else None
        self._wave_tick_lower_breakout = wave_tick if is_lower_breakout else None
        return is_upper_breakout or is_lower_breakout

    def __is_last_price_upper_breakout__(self, price: float) -> bool:
        is_buy_limit_upper_broken = price > self._buy_limit_upper and self.__is_forecast_ticks_for_breakout_fulfilled__()
        return self.__was_pattern_broken_upwards__() or is_buy_limit_upper_broken

    def __is_last_price_lower_breakout__(self, price: float) -> bool:
        is_buy_limit_lower_broken = price < self._buy_limit_lower and self.__is_forecast_ticks_for_breakout_fulfilled__()
        return self.__was_pattern_broken_downwards__() or is_buy_limit_lower_broken

    def __is_forecast_ticks_for_breakout_fulfilled__(self) -> bool:
        upper_categories = [SVC.U_in, SVC.U_on, SVC.H_U_in, SVC.H_U_on]
        lower_categories = [SVC.L_in, SVC.L_on, SVC.H_L_in, SVC.H_L_on]
        if self._forecast_breakout_direction == FD.ASC and self._range_end_value_category in lower_categories:
            return True
        elif self._forecast_breakout_direction == FD.DESC and self._range_end_value_category in upper_categories:
            return True
        return len(self._wave_tick_list) * 2 >= self._forecast_ticks_breakout

    def print_box(self, prefix=''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        details = '; '.join('{}: {}'.format(key, value) for key, value in self.__get_value_dict__().items())
        print('{}-box for {}: {}'.format(self.box_type, self._ticker_id, details))

    def __was_pattern_broken_upwards__(self) -> bool:
        return self._wave_tick_latest.high >= self.__get_f_upper_value_for_wave_tick__(self._wave_tick_latest)

    def __was_pattern_broken_downwards__(self) -> bool:
        return self._wave_tick_latest.low <= self.__get_f_lower_value_for_wave_tick__(self._wave_tick_latest)

    def __get_f_upper_value_for_wave_tick__(self, wave_tick: WaveTick):
        return MyMath.round_smart(self._f_upper(wave_tick.time_stamp))  # * (1 + self._tolerance_pct_buying))

    def __get_f_lower_value_for_wave_tick__(self, wave_tick: WaveTick):
        return MyMath.round_smart(self._f_lower(wave_tick.time_stamp))  # * (1 - self._tolerance_pct_buying))

    def __adjust_buy_limit_upper_by_wave_tick__(self, wave_tick: WaveTick):
        if self._forecast_breakout_direction == FD.ASC:
            self.__adjust_buy_limit_upper_for_wave_tick_and_breakout_asc__(wave_tick)
        else:
            self.__adjust_buy_limit_upper_for_wave_tick_and_breakout_desc__(wave_tick)

    def __adjust_buy_limit_upper_for_wave_tick_and_breakout_asc__(self, wave_tick: WaveTick):
        if len(self._wave_tick_list) >= self._forecast_ticks_breakout * 2 and False:  # we want to enforce buying...
            tick_upper_boundary = min([tick.body_low for tick in self._wave_tick_list])
        else:
            tick_upper_boundary = wave_tick.high_buy_box * (1 + self._tolerance_pct_buying)
        self._buy_limit_upper = min(self._buy_limit_upper, tick_upper_boundary)

    def __adjust_buy_limit_upper_for_wave_tick_and_breakout_desc__(self, wave_tick: WaveTick):
        self._buy_limit_upper = self.__get_f_upper_value_for_wave_tick__(wave_tick)

    def __adjust_buy_limit_lower_by_wave_tick__(self, wave_tick: WaveTick):
        if self._forecast_breakout_direction == FD.ASC:
            self.__adjust_buy_limit_lower_for_wave_tick_and_breakout_asc__(wave_tick)
        else:
            self.__adjust_buy_limit_lower_for_wave_tick_and_breakout_desc__(wave_tick)

    def __adjust_buy_limit_lower_for_wave_tick_and_breakout_asc__(self, wave_tick: WaveTick):
        self._buy_limit_lower = self.__get_f_lower_value_for_wave_tick__(wave_tick)

    def __adjust_buy_limit_lower_for_wave_tick_and_breakout_desc__(self, wave_tick: WaveTick):
        if len(self._wave_tick_list) >= self._forecast_ticks_breakout * 2 and False:  # we want to enforce buying...
            tick_lower_boundary = max([tick.body_high for tick in self._wave_tick_list])
        else:
            tick_lower_boundary = wave_tick.low_buy_box * (1 - self._tolerance_pct_buying)
        self._buy_limit_lower = max(self._buy_limit_lower, tick_lower_boundary)

    def __get_value_dict__(self) -> dict:
        return {'Offset': self._wave_tick_latest.high,
                'Forecast ticks till breakout': self._forecast_ticks_breakout,
                'Ticks till breakout': len(self._wave_tick_list)
        }

    def adjust_to_next_tick(self, wave_tick: WaveTick) -> bool:
        if wave_tick.time_stamp in self._wave_tick_timestamp_list:
            return False
        self._wave_tick_latest = wave_tick
        self._wave_tick_timestamp_list.append(wave_tick.time_stamp)
        self._wave_tick_list.append(wave_tick)
        self.__adjust_buy_limit_upper_by_wave_tick__(wave_tick)
        self.__adjust_buy_limit_lower_by_wave_tick__(wave_tick)
        self.__set_buy_limits_to_wave_tick__(wave_tick)

    def __set_buy_limits_to_wave_tick__(self, wave_tick: WaveTick):
        wave_tick.breakout_value = self._buy_limit_upper
        wave_tick.wrong_breakout_value = self._buy_limit_lower


class BreakoutBoxBuy(BoxBuy):
    def _init_parameters_(self):
        self.box_type = BBT.BREAKOUT


class BollingerBandBoxBuy(BoxBuy):
    def _init_parameters_(self):
        self.box_type = BBT.BOLLINGER_BAND


class TouchPointBoxBuy(BoxBuy):
    def _init_parameters_(self):
        self.box_type = BBT.TOUCH_POINT

