"""
Description: This module contains the paatern observation class which is used for reinforcement leaarning.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-17
"""

from sertl_analytics.constants.pattern_constants import POC, DC


class TradeObservation:
    """
     return [POC.LIMIT_PCT, POC.CURRENT_VALUE_PCT, POC.STOP_LOSS_PCT,
                POC.BEFORE_PATTERN_MAX_PCT, POC.BEFORE_PATTERN_MIN_PCT,
                POC.PATTERN_MAX_PCT, POC.PATTERN_MIN_PCT,
                POC.AFTER_BUY_MAX_PCT, POC.AFTER_BUY_MIN_PCT,
                DC.FC_HALF_POSITIVE_PCT, DC.FC_FULL_POSITIVE_PCT,
                DC.FC_HALF_NEGATIVE_PCT, DC.FC_HALF_NEGATIVE_PCT,
                DC.FC_TICKS_TO_POSITIVE_HALF, DC.FC_TICKS_TO_POSITIVE_FULL,
                DC.FC_TICKS_TO_NEGATIVE_HALF, DC.FC_TICKS_TO_NEGATIVE_FULL]
    """
    def __init__(self, data_dict: dict):
        self._data_dict = data_dict
        self._limit_pct_orig = self._data_dict[POC.LIMIT_PCT]
        self._stop_loss_pct_orig = self._data_dict[POC.STOP_LOSS_PCT]

    @property
    def forecast_limit(self):
        return self._limit_pct_orig * \
               max(50, self._data_dict[DC.FC_HALF_POSITIVE_PCT], self._data_dict[DC.FC_FULL_POSITIVE_PCT])/100

    @property
    def limit_pct_orig(self):
        return self._limit_pct_orig

    @property
    def limit_pct(self):
        return self._data_dict[POC.LIMIT_PCT]

    @limit_pct.setter
    def limit_pct(self, value_pct: float):
        self._data_dict[POC.LIMIT_PCT] = value_pct

    @property
    def current_value_high_pct(self):
        return self._data_dict[POC.CURRENT_VALUE_HIGH_PCT]

    @current_value_high_pct.setter
    def current_value_high_pct(self, value_pct: float):
        self._data_dict[POC.CURRENT_VALUE_HIGH_PCT] = value_pct
        self.__update_after_buy_max__()

    @property
    def current_value_low_pct(self):
        return self._data_dict[POC.CURRENT_VALUE_LOW_PCT]

    @current_value_low_pct.setter
    def current_value_low_pct(self, value_pct: float):
        self._data_dict[POC.CURRENT_VALUE_LOW_PCT] = value_pct
        self.__update_after_buy_min__()

    @property
    def current_value_open_pct(self):
        return self._data_dict[POC.CURRENT_VALUE_OPEN_PCT]

    @current_value_open_pct.setter
    def current_value_open_pct(self, value_pct: float):
        self._data_dict[POC.CURRENT_VALUE_OPEN_PCT] = value_pct

    @property
    def current_value_close_pct(self):
        return self._data_dict[POC.CURRENT_VALUE_CLOSE_PCT]

    @current_value_close_pct.setter
    def current_value_close_pct(self, value_pct: float):
        self._data_dict[POC.CURRENT_VALUE_CLOSE_PCT] = value_pct

    @property
    def stop_loss_pct(self):
        return self._data_dict[POC.STOP_LOSS_PCT]

    @stop_loss_pct.setter
    def stop_loss_pct(self, value_pct: float):
        self._data_dict[POC.STOP_LOSS_PCT] = value_pct

    def __update_after_buy_max__(self):
        extrema_new = self._data_dict[POC.CURRENT_VALUE_HIGH_PCT]
        if self._data_dict[POC.AFTER_BUY_MAX_PCT] < extrema_new:
            self._data_dict[POC.AFTER_BUY_MAX_PCT] = extrema_new

    def __update_after_buy_min__(self):
        extrema_new = self._data_dict[POC.CURRENT_VALUE_HIGH_PCT]
        if self._data_dict[POC.AFTER_BUY_MIN_PCT] > extrema_new:
            self._data_dict[POC.AFTER_BUY_MIN_PCT] = extrema_new
