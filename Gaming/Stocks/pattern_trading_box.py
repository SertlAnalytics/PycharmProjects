"""
Description: This module contains the Trading box classes. They represent the trading range.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-10
"""

from sertl_analytics.constants.pattern_constants import TSTR, DC, TBT
from sertl_analytics.mydates import MyDate


class TradingBox:
    def __init__(self, pattern_data_dict: dict, off_set_price: float, trade_strategy: str):
        self.box_type = ''
        self._data_dict = pattern_data_dict
        self._ticker_id = self._data_dict[DC.TICKER_ID]
        self._off_set_price = off_set_price
        self._trade_strategy = trade_strategy
        self._ticker_last_price_list = []
        self._height = 0
        self._time_stamp_end = self.__get_time_stamp_end__()
        self._date_time_end = MyDate.get_date_time_from_epoch_seconds(self._time_stamp_end)
        self._distance_bottom = 0
        self._distance_top = 0
        self._stop_loss_orig = 0
        self._stop_loss_current = 0
        self._sell_limit_orig = 0
        self._sell_limit_current = 0
        self._trailing_stop_distance = 0
        self._next_trailing_stop = 0
        self._init_parameters_()
        self.__calculate_stops_and_limits__()

    @property
    def max_ticker_last_price(self):
        return round(max(self._ticker_last_price_list), 2)

    @property
    def max_ticker_last_price_pct(self) -> int:
        return int((self.max_ticker_last_price - self._off_set_price)/self._distance_top * 100)

    @property
    def height(self):
        return self._height

    @property
    def time_stamp_end(self):
        return self._time_stamp_end

    @property
    def distance_top_bottom(self):
        return self._distance_bottom + self._distance_top

    @property
    def distance_stepping(self):
        return round(self._distance_bottom / 2, 2)

    @property
    def stop_loss(self):
        return self._stop_loss_current

    @property
    def limit(self):
        return self._sell_limit_current

    @property
    def distance_trailing_stop(self):
        return self._trailing_stop_distance

    @property
    def multiplier_positive(self):
        return round(max(100, self._data_dict[DC.FC_HALF_POSITIVE_PCT], self._data_dict[DC.FC_FULL_POSITIVE_PCT])/100, 2)

    @property
    def multiplier_negative(self):
        return round(max(100, self._data_dict[DC.FC_HALF_NEGATIVE_PCT], self._data_dict[DC.FC_FULL_NEGATIVE_PCT])/100, 2)

    def set_time_stamp_end(self):
        self._time_stamp_end = MyDate.get_epoch_seconds_from_datetime() - 60

    def print_box(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        details = '; '.join('{}: {}'.format(key, value) for key, value in self.__get_value_dict__().items())
        print('{}-box for {}: {}'.format(self.box_type, self._ticker_id, details))

    def __get_time_stamp_end__(self):
        ts_now = MyDate.get_epoch_seconds_from_datetime()
        return ts_now + (self._data_dict.get(DC.TS_PATTERN_TICK_LAST) - self._data_dict.get(DC.TS_PATTERN_TICK_FIRST))

    def __get_value_dict__(self) -> dict:
        return {'Orig_height': self._height,
                'dist_top': '{:.2f} ({:.2f})'.format(self._distance_top, self.multiplier_positive),
                'dist_bottom': '{:.2f} ({:.2f})'.format(self._distance_bottom, self.multiplier_negative),
                'limit': self.limit, 'stop loss': self.stop_loss,
                'dist_stepping': self.distance_stepping,
                'dist_trailing_stop': self.distance_trailing_stop
        }

    def adjust_to_next_ticker_last_price(self, ticker_last_price: float):
        self._ticker_last_price_list.append(ticker_last_price)
        self.__adjust_to_next_ticker_last_price__(ticker_last_price)

    def __adjust_to_next_ticker_last_price__(self, ticker_last_price: float):
        if self._trade_strategy == TSTR.LIMIT:
            pass
        elif self._trade_strategy == TSTR.TRAILING_STOP:
            if self._stop_loss_current < ticker_last_price - self._distance_bottom:
                self._stop_loss_current = ticker_last_price - self._distance_bottom
                self._sell_limit_current = self._stop_loss_current + self.distance_top_bottom
                self.__print_new_adjusted_values__()
        elif self._trade_strategy == TSTR.TRAILING_STEPPED_STOP:
            if self._stop_loss_current < ticker_last_price - self._distance_bottom - self.distance_stepping:
                self._stop_loss_current = ticker_last_price - self.distance_stepping
                self._sell_limit_current = self._stop_loss_current + self.distance_top_bottom
                self.__print_new_adjusted_values__()

    def __print_new_adjusted_values__(self):
        print('..adjusted: new stop_loss={}, new limit={} (top_bottom = {})'.format(
            self._stop_loss_current, self._sell_limit_current, self.distance_top_bottom))

    def _init_parameters_(self):
        pass

    def __calculate_stops_and_limits__(self):
        self._stop_loss_orig = self._off_set_price - self._distance_bottom
        self._stop_loss_current = self._stop_loss_orig
        self._sell_limit_orig = self._off_set_price + self._distance_top
        self._sell_limit_current = self._sell_limit_orig
        self._trailing_stop_distance = self._distance_bottom
        self._next_trailing_stop = self._off_set_price


class ExpectedWinTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = TBT.EXPECTED_WIN
        self._height = self._data_dict[DC.EXPECTED_WIN]
        self._distance_top = round(self._height * self.multiplier_positive, 2)
        self._distance_bottom = round(self._height * self.multiplier_negative, 2)


class ForecastHalfLengthTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = TBT.FORECAST_HALF_LENGTH
        self._height = self._data_dict[DC.PATTERN_HEIGHT]
        self._top_correction = 0.8
        self._bottom_correction = 1.0
        self._distance_top = round(self._height * self.multiplier_positive * self._top_correction, 2)
        self._distance_bottom = round(self._height * self.multiplier_positive, 2)


class ForecastFullLengthTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = TBT.FORECAST_FULL_LENGTH
        self._height = self._data_dict[DC.PATTERN_HEIGHT]
        self._distance_top = round(self._height * self.multiplier_positive, 2)
        self._distance_bottom = round(self._height * self.multiplier_positive, 2)


class TouchPointTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = TBT.TOUCH_POINT  # ToDo Touch_point
        self._height = self._data_dict[DC.PATTERN_HEIGHT]
        self._distance_top = round(self._height/2, 2)
        self._distance_bottom = round(self._height, 2)


class FibonacciTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = TBT.FIBONACCI  # ToDo Fibonacci
        self._height = self._data_dict[DC.PATTERN_HEIGHT]
        self._distance_top = round(self._height, 2)
        self._distance_bottom = round(self._height, 2)
