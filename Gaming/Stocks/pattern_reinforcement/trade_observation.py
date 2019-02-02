"""
Description: This module contains the paatern observation class which is used for reinforcement leaarning.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-17
"""

from sertl_analytics.constants.pattern_constants import POC, DC
from pattern_wave_tick import WaveTick
import numpy as np


class TradeObservation:
    """
     return [POC.CURRENT_TICK_PCT, POC.LIMIT_PCT, POC.CURRENT_VALUE_PCT, POC.STOP_LOSS_PCT,
                POC.BEFORE_PATTERN_MAX_PCT, POC.BEFORE_PATTERN_MIN_PCT,
                POC.PATTERN_MAX_PCT, POC.PATTERN_MIN_PCT,
                POC.AFTER_BUY_MAX_PCT, POC.AFTER_BUY_MIN_PCT,
                DC.FC_HALF_POSITIVE_PCT, DC.FC_FULL_POSITIVE_PCT,
                DC.FC_HALF_NEGATIVE_PCT, DC.FC_FULL_NEGATIVE_PCT,
                POC.FC_TICKS_TO_POSITIVE_HALF_PCT, POC.FC_TICKS_TO_POSITIVE_FULL_PCT,
                POC.FC_TICKS_TO_NEGATIVE_HALF_PCT, POC.FC_TICKS_TO_NEGATIVE_FULL_PCT]
    """
    def __init__(self, data_dict: dict, wave_tick: WaveTick):
        self._data_dict = data_dict
        self._columns = [col for col in self._data_dict]
        self._wave_tick = wave_tick
        self._limit_pct_orig = self._data_dict[POC.LIMIT_PCT]
        self._stop_loss_pct_orig = self._data_dict[POC.STOP_LOSS_PCT]
        self._scaled_value_array = None

    def scale_value_array(self, scaler):
        self._scaled_value_array = scaler.transform(self.value_array)

    @property
    def scaled_value_array(self):
        return self._scaled_value_array

    @property
    def wave_tick(self):
        return self._wave_tick

    @wave_tick.setter
    def wave_tick(self, value):
        self._wave_tick = value

    @property
    def size(self):
        return len(self._data_dict)

    @property
    def columns(self):
        return self._columns

    @property
    def value_array(self):
        np_array = np.array([self._data_dict[col] for col in self._columns])
        return np_array.reshape(1, np_array.shape[0])

    @property
    def after_buy_max_pct(self) -> float:
        return self._data_dict[POC.AFTER_BUY_MAX_PCT]

    @property
    def forecast_limit(self):
        return self._limit_pct_orig * \
               max(50, self._data_dict[DC.FC_HALF_POSITIVE_PCT], self._data_dict[DC.FC_FULL_POSITIVE_PCT])/100

    @property
    def forecast_ticks_to_positive_max_pct(self) -> int:
        return max(self._data_dict[POC.FC_TICKS_TO_POSITIVE_HALF_PCT], self._data_dict[POC.FC_TICKS_TO_POSITIVE_FULL_PCT])

    @property
    def limit_pct_orig(self):
        return self._limit_pct_orig

    @property
    def current_tick_pct(self):
        return self._data_dict[POC.CURRENT_TICK_PCT]

    @current_tick_pct.setter
    def current_tick_pct(self, value_pct: float):
        self._data_dict[POC.CURRENT_TICK_PCT] = value_pct

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
    def current_volume_buy_pct(self):
        return self._data_dict[POC.CURRENT_VOLUME_BUY_PCT]

    @current_volume_buy_pct.setter
    def current_volume_buy_pct(self, value_pct: float):
        self._data_dict[POC.CURRENT_VOLUME_BUY_PCT] = value_pct

    @property
    def current_volume_last_pct(self):
        return self._data_dict[POC.CURRENT_VOLUME_LAST_PCT]

    @current_volume_last_pct.setter
    def current_volume_last_pct(self, value_pct: float):
        self._data_dict[POC.CURRENT_VOLUME_LAST_PCT] = value_pct

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
