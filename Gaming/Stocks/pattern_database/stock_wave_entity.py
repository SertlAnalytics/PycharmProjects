"""
Description: This module contains the entities from the stock tables
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-17
"""

import pandas as pd
from sertl_analytics.constants.pattern_constants import DC, WPC, FD
from sertl_analytics.mymath import MyMath
from sertl_analytics.mydates import MyDate
from pattern_database.stock_access_layer import AccessLayer4Stock
from pattern_database.stock_database import StockDatabase
from pattern_wave_tick import WaveTick
from pattern_database.stock_access_entity import AccessEntity, EntityCollection
import math
import numpy as np


class WaveEntity(AccessEntity):
    def __init__(self, data_series):
        AccessEntity.__init__(self, data_series)
        self._wave_value_range = \
            abs(self._entity_data_dict[DC.W1_BEGIN_VALUE] - self._entity_data_dict[DC.WAVE_END_VALUE])
        self._wave_ts_range = self._entity_data_dict[DC.WAVE_END_TS] - self._entity_data_dict[DC.W1_BEGIN_TS]
        self._w1_ts_range = self._entity_data_dict[DC.W2_BEGIN_TS] - self._entity_data_dict[DC.W1_BEGIN_TS]
        self._w2_ts_range = self._entity_data_dict[DC.W3_BEGIN_TS] - self._entity_data_dict[DC.W2_BEGIN_TS]
        self._w3_ts_range = self._entity_data_dict[DC.W4_BEGIN_TS] - self._entity_data_dict[DC.W3_BEGIN_TS]
        self._w4_ts_range = self._entity_data_dict[DC.W5_BEGIN_TS] - self._entity_data_dict[DC.W4_BEGIN_TS]
        self._w5_ts_range = self._entity_data_dict[DC.WAVE_END_TS] - self._entity_data_dict[DC.W5_BEGIN_TS]
        self._w1_range = self._entity_data_dict[DC.W1_RANGE]
        self._w2_range = self._entity_data_dict[DC.W2_RANGE]
        self._w3_range = self._entity_data_dict[DC.W3_RANGE]
        self._w4_range = self._entity_data_dict[DC.W4_RANGE]
        self._w5_range = self._entity_data_dict[DC.W5_RANGE]
        self.__add_wave_prediction_specific_columns_to_data_dict__()

    @property
    def row_id(self):
        return self._entity_data_dict[DC.ROWID]

    @property
    def entity_key(self):
        return '{}_{}_{}_{}_{}_{}_{}'.format(self._entity_data_dict[DC.TICKER_ID],
                                             self._entity_data_dict[DC.W1_BEGIN_DT],
                                             self._entity_data_dict[DC.W2_BEGIN_DT],
                                             self._entity_data_dict[DC.W3_BEGIN_DT],
                                             self._entity_data_dict[DC.W4_BEGIN_DT],
                                             self._entity_data_dict[DC.W5_BEGIN_DT],
                                             self._entity_data_dict[DC.WAVE_END_DT])

    @property
    def data_dict_for_prediction(self) -> dict:
        return {column: self._entity_data_dict[column] for column in WPC.get_wave_prediction_columns()}

    @property
    def data_list_for_prediction(self) -> list:
        return [self._entity_data_dict[column] for column in WPC.get_wave_prediction_columns()]

    @property
    def data_list_for_prediction_x_data(self) -> list:
        return self.data_list_for_prediction[:-3]

    @property
    def wave_end_reached(self):
        return self._entity_data_dict[DC.WAVE_END_FLAG]

    @property
    def symbol(self):
        return self._entity_data_dict[DC.TICKER_ID]

    @property
    def wave_type(self):
        return self._entity_data_dict[DC.WAVE_TYPE]

    @property
    def wave_value_range(self):
        return self._wave_value_range

    @property
    def wave_ts_range(self):
        return self._wave_ts_range

    @property
    def wave_end_value(self):
        return self._entity_data_dict[DC.WAVE_END_VALUE]

    def get_ts_start_end_for_check_period(self):
        ts_wave_end = self._entity_data_dict[DC.WAVE_END_TS]
        return ts_wave_end, ts_wave_end + int(self._wave_ts_range/2)  # we check only the half Fibonacci wave

    @staticmethod
    def __get_pct__(nominator: float, denominator: float):
        return round(nominator/denominator * 100, 2)

    def __add_wave_prediction_specific_columns_to_data_dict__(self):
        self._entity_data_dict[WPC.W1_VALUE_RANGE_PCT] = self.__get_pct__(self._w1_range, self._wave_value_range)
        self._entity_data_dict[WPC.W2_VALUE_RANGE_PCT] = self.__get_pct__(self._w2_range, self._wave_value_range)
        self._entity_data_dict[WPC.W3_VALUE_RANGE_PCT] = self.__get_pct__(self._w3_range, self._wave_value_range)
        self._entity_data_dict[WPC.W4_VALUE_RANGE_PCT] = self.__get_pct__(self._w4_range, self._wave_value_range)
        self._entity_data_dict[WPC.W5_VALUE_RANGE_PCT] = self.__get_pct__(self._w5_range, self._wave_value_range)

        self._entity_data_dict[WPC.W1_TS_RANGE_PCT] = self.__get_pct__(self._w1_ts_range, self._wave_ts_range)
        self._entity_data_dict[WPC.W2_TS_RANGE_PCT] = self.__get_pct__(self._w2_ts_range, self._wave_ts_range)
        self._entity_data_dict[WPC.W3_TS_RANGE_PCT] = self.__get_pct__(self._w3_ts_range, self._wave_ts_range)
        self._entity_data_dict[WPC.W4_TS_RANGE_PCT] = self.__get_pct__(self._w4_ts_range, self._wave_ts_range)
        self._entity_data_dict[WPC.W5_TS_RANGE_PCT] = self.__get_pct__(self._w5_ts_range, self._wave_ts_range)


class WaveEntityCollection(EntityCollection):
    def __init__(self, df: pd.DataFrame, symbol=''):
        EntityCollection.__init__(self, df, [DC.TICKER_ID, DC.W1_BEGIN_TS])
        self._symbol = symbol

    def __get_entity_for_row__(self, row) -> AccessEntity:
        return WaveEntity(row)

    def get_data_frame_for_prediction(self) -> pd.DataFrame:
        dict_for_data_frame = {}
        wave_entity = self.get_first_element()
        while wave_entity is not None:
            for column, value in wave_entity.data_dict_for_prediction.items():
                if column in dict_for_data_frame:
                    dict_for_data_frame[column].append(value)
                else:
                    dict_for_data_frame[column] = [value]
            wave_entity = self.get_next_element()
        return pd.DataFrame.from_dict(dict_for_data_frame)

