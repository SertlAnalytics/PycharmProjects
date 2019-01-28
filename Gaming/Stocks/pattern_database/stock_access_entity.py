"""
Description: This module contains the entities from the stock tables
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-17
"""

import pandas as pd
from sertl_analytics.constants.pattern_constants import DC, POC, CN
from sertl_analytics.mymath import MyMath
from sertl_analytics.mydates import MyDate
from pattern_database.stock_access_layer import AccessLayer4Stock
from pattern_database.stock_database import StockDatabase
from pattern_wave_tick import WaveTick
import math


class AccessEntity:
    def __init__(self, data_series):
        self._entity_data_dict = data_series.to_dict()
        self.__add_specific_columns__()

    @property
    def entity_key(self):
        return ''

    def __add_specific_columns__(self):
        pass


class TradeEntity(AccessEntity):
    def __init__(self, data_series):
        AccessEntity.__init__(self, data_series)
        self.wave_tick_list_before_pattern = None
        self.wave_tick_list_pattern = None
        self.wave_tick_list_after_breakout = None

    @property
    def max_ticks_after_breakout(self) -> int:
        return 0 if self.wave_tick_list_after_breakout is None else self.wave_tick_list_after_breakout.df.shape[0]

    @property
    def entity_key(self):
        return self._entity_data_dict[DC.ID]

    @property
    def pattern_id(self):
        return self._entity_data_dict[DC.PATTERN_ID]

    @property
    def symbol(self):
        return self._entity_data_dict[DC.TICKER_ID]

    @property
    def buy_price(self) -> float:
        return self._entity_data_dict[DC.BUY_PRICE]

    @property
    def buy_date(self) -> str:
        return self._entity_data_dict[DC.BUY_DT]

    @property
    def trade_result_pct(self) -> float:
        return self._entity_data_dict[DC.TRADE_RESULT_PCT]

    @property
    def ts_before_pattern(self) -> int:
        return self.ts_pattern_start - (self.ts_breakout - self.ts_pattern_start)

    @property
    def ts_pattern_start(self) -> int:
        return self._entity_data_dict[DC.TS_PATTERN_TICK_FIRST]

    @property
    def ts_pattern_end(self) -> int:
        return self._entity_data_dict[DC.TS_PATTERN_TICK_LAST]

    @property
    def ts_trade_max(self) -> int:
        return self.ts_breakout + int(1.5 * (self.ts_breakout - self.ts_pattern_start))

    @property
    def ts_breakout(self):
        breakout_date_str = self._entity_data_dict[DC.BUY_DT]
        breakout_time_str = self._entity_data_dict[DC.BUY_TIME]
        return MyDate.get_epoch_seconds_from_datetime('{} {}'.format(breakout_date_str, breakout_time_str))

    def __add_specific_columns__(self):
        self._entity_data_dict[DC.TS_BREAKOUT] = self.ts_breakout

    def get_wave_tick_for_step(self, step_number: int) -> WaveTick:
        return self.wave_tick_list_after_breakout.tick_list[step_number-1]

    def get_data_dict_for_agent_first_observation(self) -> dict:
        columns = POC.get_observation_space_columns()
        self.__add_observation_specific_columns_to_data_dict__()
        return {column: self._entity_data_dict[column] for column in columns}

    def __add_observation_specific_columns_to_data_dict__(self):
        self._entity_data_dict[POC.CURRENT_TICK_PCT] = 0
        self._entity_data_dict[POC.LIMIT_PCT] = self.__get_limit_pct__()
        self._entity_data_dict[POC.CURRENT_VALUE_HIGH_PCT] = 0
        self._entity_data_dict[POC.CURRENT_VALUE_LOW_PCT] = 0
        self._entity_data_dict[POC.CURRENT_VALUE_OPEN_PCT] = 0
        self._entity_data_dict[POC.CURRENT_VALUE_CLOSE_PCT] = 0
        self._entity_data_dict[POC.STOP_LOSS_PCT] = self.__get_stop_loss_pct__()
        self._entity_data_dict[POC.BEFORE_PATTERN_MAX_PCT] = MyMath.get_change_in_percentage(
            self.buy_price, self.wave_tick_list_before_pattern.df[CN.HIGH].max())
        self._entity_data_dict[POC.BEFORE_PATTERN_MIN_PCT] = MyMath.get_change_in_percentage(
            self.buy_price, self.wave_tick_list_before_pattern.df[CN.LOW].min())
        self._entity_data_dict[POC.PATTERN_MAX_PCT] = MyMath.get_change_in_percentage(
            self.buy_price, self.wave_tick_list_pattern.df[CN.HIGH].max())
        self._entity_data_dict[POC.PATTERN_MIN_PCT] = MyMath.get_change_in_percentage(
            self.buy_price, self.wave_tick_list_pattern.df[CN.LOW].min())
        self._entity_data_dict[POC.AFTER_BUY_MAX_PCT] = 0
        self._entity_data_dict[POC.AFTER_BUY_MIN_PCT] = 0

        self._entity_data_dict[POC.FC_TICKS_TO_POSITIVE_HALF_PCT] = self.__get_forecast_ticks_as_pct__(
            DC.FC_TICKS_TO_POSITIVE_HALF)
        self._entity_data_dict[POC.FC_TICKS_TO_POSITIVE_FULL_PCT] = self.__get_forecast_ticks_as_pct__(
            DC.FC_TICKS_TO_POSITIVE_FULL)
        self._entity_data_dict[POC.FC_TICKS_TO_NEGATIVE_HALF_PCT] = self.__get_forecast_ticks_as_pct__(
            DC.FC_TICKS_TO_NEGATIVE_HALF)
        self._entity_data_dict[POC.FC_TICKS_TO_NEGATIVE_FULL_PCT] = self.__get_forecast_ticks_as_pct__(
            DC.FC_TICKS_TO_NEGATIVE_FULL)

    def __get_forecast_ticks_as_pct__(self, data_column: str):
        return round(self._entity_data_dict[data_column]/self.max_ticks_after_breakout*100, 2)

    def __get_limit_pct__(self):
        limit_orig = self._entity_data_dict[DC.TRADE_BOX_LIMIT_ORIG]
        if limit_orig == math.inf:
            limit_orig = self._entity_data_dict[DC.TRADE_BOX_STOP_LOSS_ORIG] \
                         + self._entity_data_dict[DC.TRADE_BOX_HEIGHT]
        return MyMath.get_change_in_percentage(self.buy_price, limit_orig)

    def __get_stop_loss_pct__(self):
        # we don't use self._entity_data_dict[DC.TRADE_BOX_STOP_LOSS_ORIG] - too narrow !!!
        stop_loss = self.buy_price - self._entity_data_dict[DC.TRADE_BOX_HEIGHT]
        return MyMath.get_change_in_percentage(self.buy_price, stop_loss)


class EntityCollection:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._entity_dict = {}
        self._entity_key_list = []
        self._counter = 0
        self.__fill_entity_dict__()

    @property
    def elements(self):
        return len(self._entity_dict)

    def get_nth_element(self, number: int):
        self._counter = number
        if 1 <= number <= self.elements:
            return self._entity_dict[self._entity_key_list[number-1]]

    def get_first_element(self):
        return self.get_nth_element(1)

    def get_next_element(self):
        return self.get_nth_element(self._counter + 1)

    def get_previous_element(self):
        return self.get_nth_element(self._counter - 1)

    def get_last_element(self):
        return self.get_nth_element(self.elements)

    def __fill_entity_dict__(self):
        for index, row in self._df.iterrows():
            entity = self.__get_entity_for_row__(row)
            self._entity_key_list.append(entity.entity_key)
            self._entity_dict[entity.entity_key] = entity
        pass

    def __get_entity_for_row__(self, row):
        pass


class TradeEntityCollection(EntityCollection):
    def __init__(self, df: pd.DataFrame):
        EntityCollection.__init__(self, df)
        self._collection_trade_result_pct = self.__get_collection_trade_result_pct__()

    @property
    def collection_trade_result_pct(self):
        return self._collection_trade_result_pct

    def __get_collection_trade_result_pct__(self):
        return sum([entity.trade_result_pct for entity in self._entity_dict.values()])

    def __get_entity_for_row__(self, row) -> AccessEntity:
        return TradeEntity(row)

    def add_wave_tick_lists(self):
        access_layer_stock = AccessLayer4Stock(StockDatabase())
        trade_entity = self.get_first_element()
        while trade_entity is not None:
            symbol = trade_entity.symbol
            ts_list = [trade_entity.ts_before_pattern, trade_entity.ts_pattern_start,
                       trade_entity.ts_pattern_end, trade_entity.ts_trade_max]
            wave_tick_lists = access_layer_stock.get_wave_tick_lists_for_time_stamp_intervals(symbol, ts_list)
            trade_entity.wave_tick_list_before_pattern = wave_tick_lists[0]
            trade_entity.wave_tick_list_pattern = wave_tick_lists[1]
            trade_entity.wave_tick_list_after_breakout = wave_tick_lists[2]
            trade_entity = self.get_next_element()



