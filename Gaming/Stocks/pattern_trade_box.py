"""
Description: This module contains the Trading box classes. They represent the exchange_config range.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-10
"""

from sertl_analytics.constants.pattern_constants import TSTR, DC, BTT, FT
from sertl_analytics.mymath import MyMath
from sertl_analytics.mydates import MyDate
from sertl_analytics.mymath import MyMath
from pattern_logging.pattern_log import PatternLog
import math
from scipy import stats
import statistics


class TradingBoxApi:
    def __init__(self):
        self.data_dict = None
        self.off_set_value = 0.0
        self.buy_price = 0.0
        self.trade_strategy = ''
        self.height = 0  # is used for touch point
        self.distance_bottom = 0  # is used for touch point
        self.last_price_mean_aggregation = 8  # will be overwritten by config or optimizer data
        self.small_profit_taking_active = False  # will be overwritten by config
        self.small_profit_taking_parameters = []  # will be overwritten by config


class TradingBox:
    def __init__(self, api: TradingBoxApi):
        self.box_type = ''
        self._api = api
        self._data_dict = api.data_dict
        self._pattern_type = self._data_dict[DC.PATTERN_TYPE]
        self._ticker_id = self._data_dict[DC.TICKER_ID]
        self._off_set_value = api.off_set_value  # basis for distance_top and _bottom
        self._buy_price = api.buy_price
        self._sma_value = 0  # simple moving average value for this strategy
        self._trade_strategy = api.trade_strategy
        self._ticker_last_price_list = [api.off_set_value, api.buy_price]  # off_set is used to guarantee: max >= offset
        self._ticker_last_price = api.buy_price
        self._height = self.round(api.height)
        self._time_stamp_end = self.__get_time_stamp_end__()
        self._date_time_end = MyDate.get_date_time_from_epoch_seconds(self._time_stamp_end)
        self._distance_bottom = api.distance_bottom
        self._distance_top = 0
        self._stop_loss_orig = 0
        self._stop_loss = 0
        self._sell_limit_orig = 0
        self._sell_limit = 0
        self._init_parameters_()
        self.__calculate_stops_and_limits__()
        self._price_was_close_to_stop = False
        self._small_profit_taking_active = api.small_profit_taking_active
        self._small_profit_taking_parameters = api.small_profit_taking_parameters
        self._was_adjusted_to_small_profit_taking = False

    @property
    def buy_price(self) -> float:
        return self._buy_price

    @property
    def last_price(self) -> float:
        return self._ticker_last_price

    @property
    def current_result_pct(self) -> float:
        return round((self.last_price - self._buy_price) / self._buy_price * 100, 2) # we want to have full % numbers

    @staticmethod
    def round(value: float):
        return MyMath.round_smart(value)

    @property
    def std(self):
        sorted_list = sorted(self._ticker_last_price_list)
        slope, intercept, r_value, p_value, std_err = stats.linregress(sorted_list, self._ticker_last_price_list)
        return std_err

    @property
    def off_set_value(self):
        return self.round(self._off_set_value)

    @property
    def max_ticker_last_price(self):
        return MyMath.round_smart(max(self._ticker_last_price_list))

    @property
    def max_ticker_last_price_pct(self) -> float:
        return round((self.max_ticker_last_price - self._off_set_value) / self._off_set_value * 100, 2)

    @property
    def height(self):
        return self._height

    @property
    def time_stamp_end(self):
        return self._time_stamp_end

    @property
    def distance_top_bottom(self):
        return self.round(self._distance_bottom + self._distance_top)

    @property
    def distance_stepping(self):
        return self.round(self._distance_bottom / 2)

    @property
    def stop_loss_orig(self):
        return self.round(self._stop_loss_orig)

    @property
    def stop_loss(self):
        return self.round(self._stop_loss)

    @property
    def limit_orig(self):
        return self.round(self._sell_limit_orig)

    @property
    def limit(self):
        return self.round(self._sell_limit)

    @property
    def limit_for_graph(self):
        if self._trade_strategy in [TSTR.LIMIT, TSTR.LIMIT_FIX]:
            return self.limit
        return self.round(self.max_ticker_last_price + 2 * self._distance_top)

    @property
    def distance_trailing_stop(self):
        return self.round(self._distance_bottom)

    @property
    def multiplier_positive(self):
        return round(max(100, self._data_dict[DC.FC_HALF_POSITIVE_PCT], self._data_dict[DC.FC_FULL_POSITIVE_PCT])/100, 2)

    @property
    def multiplier_negative(self):
        return round(max(100, self._data_dict[DC.FC_HALF_NEGATIVE_PCT], self._data_dict[DC.FC_FULL_NEGATIVE_PCT])/100, 2)

    def print_box(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        details = '; '.join('{}: {}'.format(key, value) for key, value in self.__get_value_dict__().items())
        print('{}-box for {}: {}'.format(self.box_type, self._ticker_id, details))

    def __get_time_stamp_end__(self):
        ts_now = MyDate.get_epoch_seconds_from_datetime()
        # return ts_now + (self._data_dict.get(DC.TS_PATTERN_TICK_LAST) - self._data_dict.get(DC.TS_PATTERN_TICK_FIRST))
        return ts_now + (self._data_dict.get(DC.BUY_TIME_STAMP) - self._data_dict.get(DC.TS_PATTERN_TICK_FIRST))

    def __get_value_dict__(self) -> dict:
        return {'Orig_height': self._height,
                'dist_top': '{} ({:.2f})'.format(self._distance_top, self.multiplier_positive),
                'dist_bottom': '{} ({:.2f})'.format(self._distance_bottom, self.multiplier_negative),
                '_limit': self.limit, 'stop loss': self.stop_loss,
                'dist_stepping': self.distance_stepping,
                'dist_trailing_stop': self.distance_trailing_stop
        }

    def adjust_to_next_ticker_last_price(self, ticker_last_price: float, sma_value=0, small_profit=False) -> bool:
        self._ticker_last_price = ticker_last_price
        if self._ticker_last_price <= self._ticker_last_price_list[-1]:  # no adjustments necessary
            return False
        self._ticker_last_price_list.append(ticker_last_price)
        self._sma_value = sma_value
        self._small_profit_taking_active = small_profit
        return self.__adjust_to_next_ticker_last_price__()

    def __adjust_to_next_ticker_last_price__(self) -> bool:
        stop_loss_changed = self.__adjust_stop_loss_to_next_ticker_last_price__(self._ticker_last_price)
        limit_changed = self.__adjust_limit_to_next_ticker_last_price__(self._ticker_last_price)
        return stop_loss_changed or limit_changed

    def __adjust_stop_loss_to_next_ticker_last_price__(self, ticker_last_price: float) -> bool:
        ticker_last_price_mean = self.__get_ticker_last_price_mean__(ticker_last_price)
        small_profit_adjusted = self.__adjust_stop_loss_to_small_profit_taking__(ticker_last_price)
        pattern_type_specific_adjusted = self.__adjust_stop_loss_to_pattern_type_specifics__(ticker_last_price)
        self.__adjust_distance_bottom_to_current_result__(ticker_last_price)
        if self._trade_strategy == TSTR.LIMIT:  # with trailing stop
            if self._stop_loss < ticker_last_price_mean - self._distance_bottom:
                self._stop_loss = ticker_last_price_mean - self._distance_bottom
                return True
        elif self._trade_strategy == TSTR.LIMIT_FIX:
            pass  # no change in stop loss
        elif self._trade_strategy == TSTR.TRAILING_STOP:  # ToDo trailing stop closer after some time...
            if self._stop_loss < ticker_last_price_mean - self._distance_bottom:
                self._stop_loss = ticker_last_price_mean - self._distance_bottom
                return True
        elif self._trade_strategy == TSTR.TRAILING_STEPPED_STOP:  # ToDo trailing stop closer after some time...
            if self._stop_loss < ticker_last_price_mean - self.distance_stepping:
                multiplier = int((ticker_last_price_mean - self._stop_loss) / self.distance_stepping) - 1
                self._stop_loss = self._stop_loss + multiplier * self.distance_stepping
                return True
        elif self._trade_strategy == TSTR.SMA:  # ToDo trailing stop closer after some time (above buy price !!!)
            if self._stop_loss < self._sma_value:
                self._stop_loss = self._sma_value
                return True
        return small_profit_adjusted or pattern_type_specific_adjusted

    def __adjust_stop_loss_to_small_profit_taking__(self, last_price: float) -> bool:
        # 1. param: this limit reached => stop loss at 2. param,
        if not self._small_profit_taking_active:
            return False

        if self._was_adjusted_to_small_profit_taking or len(self._small_profit_taking_parameters) != 2:
            return False

        if self.current_result_pct <= self._small_profit_taking_parameters[0]:
            return False

        stop_loss_pct = self._small_profit_taking_parameters[1]
        stop_loss_for_small_profit_parameters = self._buy_price * (1.0 + stop_loss_pct/100)
        if self._stop_loss >= stop_loss_for_small_profit_parameters:
            return False
        self.__log_stop_loss_adjustment__(
            'stop_loss_for_small_profit_parameters', 'small profit', stop_loss_for_small_profit_parameters)
        self._stop_loss = stop_loss_for_small_profit_parameters
        self._was_adjusted_to_small_profit_taking = True
        return True

    def __adjust_stop_loss_to_pattern_type_specifics__(self, last_price: float) -> bool:
        module = '__adjust_stop_loss_to_pattern_type_specifics__'
        if FT.is_pattern_type_any_triangle(self._pattern_type):
            # expected breakout = high of the triangle, but stop loss at apex
            apex_value = self._data_dict.get(DC.APEX_VALUE)
            pattern_begin_high = self._data_dict.get(DC.PATTERN_BEGIN_HIGH)
            max_apex_and_high = max(apex_value, pattern_begin_high)
            if last_price > max_apex_and_high * 1.01 > max_apex_and_high > self._stop_loss:  # we want to have a close stop_loss
                self.__log_stop_loss_adjustment__(module, self._pattern_type, max_apex_and_high)
                self._stop_loss = max_apex_and_high
                return True
        return False

    def __log_stop_loss_adjustment__(self, module_name: str, reason: str, new_stop_loss: float):
        message = '{}: Stop loss adjusted for {}: old stop={}, new stop={} (params: {})'.format(
                self._ticker_id, reason, self._stop_loss, new_stop_loss, self._small_profit_taking_parameters)
        print(message)
        PatternLog().log_message(message, module_name)

    def __get_ticker_last_price_mean__(self, ticker_last_price):
        if self._api.last_price_mean_aggregation == 1:
            return ticker_last_price
        if self.current_result_pct > 1:  # after 1% gain we want to follow the actual price - no means at all
            print('{}: ticker_last_price_mean = current_price = {} since current_result = {:.2f}% > 1%'.format(
                self._ticker_id, ticker_last_price, self.current_result_pct))
            return ticker_last_price
        mean_ticker = statistics.mean(self._ticker_last_price_list[-self._api.last_price_mean_aggregation:])
        print('{}: ticker_last_price_mean = {} - mean_aggregation = {}'.format(
            self._ticker_id, mean_ticker, self._api.last_price_mean_aggregation))
        return mean_ticker

    def __adjust_distance_bottom_to_current_result__(self, last_price: float):
        # the idea is to get closer to the curve when we are in a winning trade... but not closer than 1 %
        if self.current_result_pct > 2:
            adjusted_distance = self._distance_bottom / (self.current_result_pct - 1)
            if adjusted_distance/self._buy_price > 0.01:
                print('distance_bottom_adjusted: {:.2f} -> {:.2f}'.format(self._distance_bottom, adjusted_distance))
                self._distance_bottom = adjusted_distance
        elif self._price_was_close_to_stop:  # the first trace back occurred - we can be closer...
            adjusted_distance = last_price/100  # 1%
            if adjusted_distance < self._distance_bottom:
                print('distance_bottom_adjusted: {:.2f} -> {:.2f}'.format(self._distance_bottom, adjusted_distance))
                self._distance_bottom = adjusted_distance
        else:
            if abs(last_price - self._stop_loss)/last_price < 0.005:
                self._price_was_close_to_stop = True

    def __adjust_limit_to_next_ticker_last_price__(self, ticker_last_price: float) -> bool:
        if self._trade_strategy in [TSTR.LIMIT, TSTR.LIMIT_FIX]:  # _limit doesn't change
            return False
        else:
            # if self._sell_limit < ticker_last_price + self._distance_top:
            #     self._sell_limit = ticker_last_price + 2 * self._distance_top
            #     return True
            return False

    def _init_parameters_(self):
        pass

    def __calculate_stops_and_limits__(self):
        self._stop_loss_orig = self._off_set_value - self._distance_bottom
        self._stop_loss = self._stop_loss_orig
        if self._trade_strategy in [TSTR.LIMIT, TSTR.LIMIT_FIX]:
            self._sell_limit_orig = self._off_set_value + self._distance_top
        else:
            self._sell_limit_orig = math.inf
        self._sell_limit = self._sell_limit_orig
        self.__print_values__('Initialize stop and _limit')

    def __print_values__(self, prefix: str):
        print('...{} for {}-{}: limit={:.2f}, buy={:.2f}, offset={:.2f}, stop_loss={:.2f} '
              '(dist_top={:.2f}, dist_bottom={:.2f})'.format(
            prefix, self._ticker_id, self._trade_strategy, self._sell_limit, self._buy_price,
            self.off_set_value, self._stop_loss, self._distance_top, self._distance_bottom))


class ExpectedWinTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = BTT.EXPECTED_WIN
        self._height = self.round(self._data_dict[DC.EXPECTED_WIN])
        self._distance_top = self.round(self._height * self.multiplier_positive)
        # self._distance_bottom = self.round(self._height * self.multiplier_negative)


class BollingerBandTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = BTT.BOLLINGER_BAND
        self._height = self.round(self._data_dict[DC.EXPECTED_WIN])
        self._distance_top = self.round(self._height * self.multiplier_positive)
        # self._distance_bottom = self.round(self._height * self.multiplier_negative)


class TouchPointTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = BTT.TOUCH_POINT
        self._distance_top = self.round(self._height - self._distance_bottom)
        self._distance_bottom = self.round(self._distance_bottom)


