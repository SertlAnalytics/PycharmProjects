"""
Description: This module contains the pattern data factory for delivering data of a certain class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FD, DC, CN, EQUITY_TYPE, BT, ST, TR, TSTR, OT, PRD
from sertl_analytics.mydates import MyDate
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_wave_tick import WaveTick
from sertl_analytics.mymath import MyMath
from pattern_data_frame import PatternDataFrame
from sertl_analytics.exchanges.exchange_cls import Order, OrderStatus
from pattern_data_container import PatternDataHandler
import numpy as np


class PatternDataDictionary:
    def __init__(self, sys_config: SystemConfiguration, pdh: PatternDataHandler):
        self.sys_config = sys_config
        self.pdh = pdh
        self.df = self.pdh.pattern_data.df
        self.df_length = self.df.shape[0]
        self.df_min_max = self.pdh.pattern_data.df_min_max
        self._data_dict = {}
        self.__init_data_dict__()

    @property
    def data_dict(self) -> dict:
        return self._data_dict

    def add(self, key: str, value):
        value = self.__get_manipulated_value__(key, value)
        self._data_dict[key] = value

    def inherit_values(self, data_dict: dict):
        for key, values in data_dict.items():
            self.data_dict[key] = values

    @staticmethod
    def __get_manipulated_value__(key: str, value):
        if type(value) in [np.float64, float]:
            if value == -0.0:
                value = 0.0
        return PatternDataDictionary.__get_rounded_value__(key, value)

    @staticmethod
    def __get_rounded_value__(key, value):
        if key in [DC.SLOPE_VOLUME_REGRESSION_PCT, DC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED_PCT,
                   DC.VOLUME_CHANGE_AT_BREAKOUT_PCT,
                   DC.PREVIOUS_PERIOD_HALF_TOP_OUT_PCT, DC.PREVIOUS_PERIOD_FULL_TOP_OUT_PCT,
                   DC.PREVIOUS_PERIOD_HALF_BOTTOM_OUT_PCT, DC.PREVIOUS_PERIOD_FULL_BOTTOM_OUT_PCT]:
            return 1000 if value > 1000 else round(value, -1)
        elif key in [DC.SLOPE_UPPER_PCT, DC.SLOPE_LOWER_PCT, DC.SLOPE_REGRESSION_PCT, DC.SLOPE_BREAKOUT_PCT]:
            return 1000 if value > 1000 else round(value, 0)
        return value

    def get(self, key: str, default_value=None):
        return self._data_dict.get(key, None)

    def __init_data_dict__(self):
        self._data_dict[DC.EQUITY_TYPE] = self.sys_config.runtime.actual_ticker_equity_type
        self._data_dict[DC.EQUITY_TYPE_ID] = EQUITY_TYPE.get_id(self._data_dict[DC.EQUITY_TYPE])
        self._data_dict[DC.PERIOD] = self.sys_config.period
        self._data_dict[DC.PERIOD_ID] = PRD.get_id(self.sys_config.period)
        if self.sys_config.period == PRD.INTRADAY:
            self._data_dict[DC.PERIOD_AGGREGATION] = self.sys_config.period_aggregation
        else:
            self._data_dict[DC.PERIOD_AGGREGATION] = 1
        self._data_dict[DC.TICKER_ID] = self.sys_config.runtime.actual_ticker
        self._data_dict[DC.TICKER_NAME] = self.sys_config.runtime.actual_ticker_name

    def is_data_dict_ready_for_pattern_table(self):
        for col in self.sys_config.pattern_table.column_name_list:
            if col not in self._data_dict:
                return False
        return True

    def is_data_dict_ready_for_trade_table(self):
        for col in self.sys_config.trade_table.column_name_list:
            if col not in self._data_dict:
                return False
        return True

    def is_data_dict_ready_for_columns(self, columns: list):
        for col in columns:
            if col not in self._data_dict:
                return False
        return True

    def get_data_list_for_columns(self, columns: list):
        return [self._data_dict[col] for col in columns]

    def get_data_dict_for_features_table(self):
        return {col: self._data_dict[col] for col in self.sys_config.pattern_table.column_name_list}

    def get_data_dict_for_trade_table(self):
        return {col: self._data_dict[col] for col in self.sys_config.trade_table.column_name_list}

    def add_buy_order_status_data_to_pattern_data_dict(self, order_status: OrderStatus, trade_strategy: str):
        self._data_dict[DC.BUY_ORDER_ID] = order_status.order_id
        self._data_dict[DC.BUY_ORDER_TPYE] = order_status.type
        self._data_dict[DC.BUY_ORDER_TPYE_ID] = OT.get_id(order_status.type)
        self._data_dict[DC.BUY_DT] = MyDate.get_date_from_epoch_seconds(order_status.time_stamp)
        self._data_dict[DC.BUY_TIME] = str(MyDate.get_time_from_epoch_seconds(order_status.time_stamp))
        self._data_dict[DC.BUY_AMOUNT] = order_status.original_amount
        self._data_dict[DC.BUY_PRICE] = order_status.avg_execution_price
        self._data_dict[DC.BUY_TOTAL_COSTS] = order_status.value_total
        self._data_dict[DC.BUY_TRIGGER] = order_status.order_trigger
        self._data_dict[DC.BUY_TRIGGER_ID] = BT.get_id(order_status.order_trigger)
        self._data_dict[DC.BUY_COMMENT] = order_status.order_comment
        self._data_dict[DC.TRADE_STRATEGY] = trade_strategy
        self._data_dict[DC.TRADE_STRATEGY_ID] = TSTR.get_id(trade_strategy)

    def add_sell_order_status_data_to_pattern_data_dict(self, order_status: OrderStatus):
        self._data_dict[DC.SELL_ORDER_ID] = order_status.order_id
        self._data_dict[DC.SELL_ORDER_TPYE] = order_status.type
        self._data_dict[DC.SELL_ORDER_TPYE_ID] = OT.get_id(order_status.type)
        self._data_dict[DC.SELL_DT] = MyDate.get_date_from_epoch_seconds(order_status.time_stamp)
        self._data_dict[DC.SELL_TIME] = str(MyDate.get_time_from_epoch_seconds(order_status.time_stamp))
        self._data_dict[DC.SELL_AMOUNT] = order_status.original_amount
        self._data_dict[DC.SELL_PRICE] = order_status.avg_execution_price
        self._data_dict[DC.SELL_TOTAL_VALUE] = order_status.value_total
        self._data_dict[DC.SELL_TRIGGER] = order_status.order_trigger
        self._data_dict[DC.SELL_TRIGGER_ID] = ST.get_id(order_status.order_trigger)
        self._data_dict[DC.SELL_COMMENT] = order_status.order_comment
        win_min = round(self._data_dict[DC.BUY_PRICE] * 1.005, 2)  # at least 0.5%
        if self._data_dict[DC.SELL_PRICE] > win_min:
            self._data_dict[DC.TRADE_RESULT] = TR.WINNER
        elif self._data_dict[DC.SELL_PRICE] > self._data_dict[DC.BUY_PRICE]:
            self._data_dict[DC.TRADE_RESULT] = TR.NEUTRAL
        else:
            self._data_dict[DC.TRADE_RESULT] = TR.LOSER
        self._data_dict[DC.TRADE_RESULT_ID] = TR.get_id(self._data_dict[DC.TRADE_RESULT])

    def get_flag_for_false_breakout(self):
        is_positive_first = self._data_dict[DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF] < \
                            self._data_dict[DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF]
        is_positive_value_larger = self._data_dict[DC.NEXT_PERIOD_HALF_POSITIVE_PCT] > \
                                   self._data_dict[DC.NEXT_PERIOD_HALF_NEGATIVE_PCT]
        min_pct_reached = self._data_dict[DC.NEXT_PERIOD_FULL_POSITIVE_PCT] >= 20.0
        return 0 if (is_positive_first or is_positive_value_larger) and min_pct_reached else 1

    def get_slope_breakout(self, pos_breakout: int, df_col: str = CN.CLOSE):
        distance = 4
        return self.get_slope(pos_breakout - distance, pos_breakout - 1, df_col)  # slope BEFORE the breakout

    def get_slope(self, pos_start: int, pos_end: int, df_col: str = CN.CLOSE):
        df_part = self.df.iloc[pos_start:pos_end + 1]
        tick_first = WaveTick(df_part.iloc[0])
        tick_last = WaveTick(df_part.iloc[-1])
        stock_df = PatternDataFrame(df_part)
        func = stock_df.get_f_regression(df_col)
        return MyMath.get_change_in_percentage(func(tick_first.f_var), func(tick_last.f_var), 1)

    def get_min_max_value_dict(self, tick_first: WaveTick, tick_last: WaveTick, pattern_length: int):
        # the height at the start is the relative comparison value
        # c_range = round(self._data_dict[DC.PATTERN_BEGIN_HIGH] - self._data_dict[DC.PATTERN_BEGIN_LOW], 2)
        c_range = self._data_dict[DC.PATTERN_HEIGHT]  # new since 2018-08-29 - ToDo has to be clarified
        pattern_length_half = int(pattern_length / 2)
        pos_first = tick_first.position
        pos_last = tick_last.position
        pos_prev_full = max(0, pos_first - pattern_length)
        pos_prev_half = max(0, pos_first - pattern_length_half)
        pos_next_full = min(pos_last + pattern_length, self.df_length - 1)
        pos_next_half = min(pos_last + pattern_length_half, self.df_length - 1)
        value_dict = {}

        high = self._data_dict[DC.PATTERN_BEGIN_HIGH]
        low = self._data_dict[DC.PATTERN_BEGIN_LOW]
        value_dict['max_previous_half'] = self._get_df_max_values_(pos_prev_half, pos_first, high, c_range)
        value_dict['max_previous_full'] = self._get_df_max_values_(pos_prev_full, pos_first, high, c_range)
        value_dict['min_previous_half'] = self._get_df_min_values_(pos_prev_half, pos_first, low, c_range)
        value_dict['min_previous_full'] = self._get_df_min_values_(pos_prev_full, pos_first, low, c_range)

        high = self._data_dict[DC.PATTERN_END_HIGH]
        low = self._data_dict[DC.PATTERN_END_LOW]
        if self._data_dict[DC.BREAKOUT_DIRECTION] == FD.ASC:
            value_dict['positive_next_half'] = self._get_df_max_values_(pos_last, pos_next_half, high, c_range)
            value_dict['positive_next_full'] = self._get_df_max_values_(pos_last, pos_next_full, high, c_range)
            value_dict['negative_next_half'] = self._get_df_min_values_(pos_last, pos_next_half, high, c_range)
            value_dict['negative_next_full'] = self._get_df_min_values_(pos_last, pos_next_full, high, c_range)
        else:
            value_dict['positive_next_half'] = self._get_df_min_values_(pos_last, pos_next_half, low, c_range)
            value_dict['positive_next_full'] = self._get_df_min_values_(pos_last, pos_next_full, low, c_range)
            value_dict['negative_next_half'] = self._get_df_max_values_(pos_last, pos_next_half, low, c_range)
            value_dict['negative_next_full'] = self._get_df_max_values_(pos_last, pos_next_full, low, c_range)
        return value_dict

    def _get_df_min_values_(self, pos_begin: int, pos_end: int, ref_value: float, comp_range: float):
        df_part = self.df.iloc[pos_begin:pos_end + 1]
        min_value = df_part[CN.LOW].min()
        min_position = df_part[CN.LOW].idxmin()
        pct = 0 if min_value > ref_value else round((ref_value - min_value) / comp_range * 100, 2)
        return round(pct, -1), min_position, min_value

    def _get_df_max_values_(self, pos_begin: int, pos_end: int, ref_value: float, comp_range: float):
        df_part = self.df.iloc[pos_begin:pos_end + 1]
        max_value = df_part[CN.HIGH].max()
        max_position = df_part[CN.HIGH].idxmax()
        pct = 0 if max_value < ref_value else round((max_value - ref_value) / comp_range * 100, 2)
        return round(pct, -1), max_position, max_value
