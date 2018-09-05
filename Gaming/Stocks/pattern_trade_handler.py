"""
Description: This module contains the PatternTradeContainer class - central data container for stock data trading
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import pandas as pd
import numpy as np
import itertools
from sertl_analytics.constants.pattern_constants import CN, DIR, FT, TSTR, BT, ST, FD, DC
from sertl_analytics.mydates import MyDate
from pattern_wave_tick import WaveTick, ExtendedDictionary4WaveTicks, WaveTickList
from pattern_configuration import PatternConfiguration
from pattern_system_configuration import SystemConfiguration
from pattern import Pattern
from pattern_bitfinex import MyBitfinexTradeClient, BitfinexConfiguration
from sertl_analytics.exchanges.exchange_cls import Order, OrderStatus, Ticker
from pattern_database.stock_database import StockDatabase


class PTS:  # PatternTradeStatus
    NEW = 'new'
    EXECUTED = 'filled'
    FINISHED = 'finished'


class PatternTrade:
    def __init__(self, pattern: Pattern, buy_trigger: str, trade_strategy: str):
        self.buy_trigger = buy_trigger
        self.trade_strategy = trade_strategy
        self.pattern = pattern
        self.expected_win = self.pattern.data_dict_obj.get(DC.EXPECTED_WIN)
        self.expected_breakout_direction = self.pattern.expected_breakout_direction
        self.id = '{}-{}: {}'.format(buy_trigger, trade_strategy, pattern.id)
        self._order_status_buy = None
        self._order_status_sell = None
        self._status = PTS.NEW
        self._stop_loss_orig = 0
        self._stop_loss_current = 0
        self._sell_limit_orig = 0
        self._sell_limit_current = 0
        self._trailing_stop_distance = 0
        self._next_trailing_stop_limit = 0
        self._next_trailing_stop = 0
        self._next_limit = 0

    def order_status_buy(self):
        return self._order_status_buy

    def __set_order_status_buy__(self, order_status: OrderStatus, buy_comment, ticker: Ticker):
        order_status.order_trigger = self.buy_trigger
        order_status.order_comment = buy_comment
        self._order_status_buy = order_status
        self.pattern.data_dict_obj.add_buy_order_status_data_to_pattern_data_dict(order_status, self.trade_strategy)
        self.__set_properties_after_buy__(ticker)

    def __set_properties_after_buy__(self, ticker: Ticker):
        self._status = PTS.EXECUTED
        if self.trade_strategy == TSTR.EXPECTED_WIN:
            self._sell_limit_orig = ticker.last_price + self.expected_win
            self._sell_limit_current = self._sell_limit_orig
            self._stop_loss_orig = ticker.last_price - self.expected_win
            self._stop_loss_current = self._stop_loss_orig

    def order_status_sell(self):
        return self._order_status_buy

    def __set_order_status_sell__(self, order_status: OrderStatus, sell_trigger: str, sell_comment, ticker: Ticker):
        order_status.order_trigger = sell_trigger
        order_status.order_comment = sell_comment
        self._order_status_sell = order_status
        self.pattern.data_dict_obj.add_sell_order_status_data_to_pattern_data_dict(order_status)
        self.__set_properties_after_sell__()

    def __set_properties_after_sell__(self):
        self._status = PTS.FINISHED

    @property
    def stop_loss_current(self):
        return self._stop_loss_current

    @property
    def trailing_stop_distance(self):
        return self._trailing_stop_distance

    @property
    def ticker_id(self):
        return self.pattern.ticker_id

    @property
    def status(self):
        return self._status

    def is_ticker_breakout(self, ticker: Ticker, time_stamp: int):
        if self.expected_breakout_direction == FD.ASC:
            upper_value = self.pattern.function_cont.get_upper_value(time_stamp)
            return ticker.last_price >= upper_value
        # elif self.expected_breakout_direction == FD.DESC:
        #     lower_value = self.pattern.function_cont.get_lower_value(time_stamp)
        #     return ticker.last_price <= lower_value
        return False

    def is_ticker_wrong_breakout(self, ticker: Ticker, time_stamp: int):
        if self.expected_breakout_direction == FD.ASC:
            lower_value = self.pattern.function_cont.get_lower_value(time_stamp)
            return ticker.last_price <= lower_value
        elif self.expected_breakout_direction == FD.DESC:
            upper_value = self.pattern.function_cont.get_upper_value(time_stamp)
            return ticker.last_price >= upper_value
        return False


class PatternTradeHandler:
    def __init__(self, sys_config: SystemConfiguration, bitfinex_config: BitfinexConfiguration):
        self.sys_config = sys_config
        self.bitfinex_trade_client = MyBitfinexTradeClient(bitfinex_config)
        self.stock_db = self.sys_config.db_stock
        self.ticker_id_list = []
        self.ticker_dict = {}
        self.pattern_trade_dict = {}
        self.time_stamp_check = 0
        self.date_time_check = None

    def __del__(self):
        self.__create_trailing_stop_order_for_all_executed_trades__()

    def add_pattern_for_trade(self, pattern: Pattern, buy_trigger: str, trade_strategy: str):
        if pattern.expected_breakout_direction != FD.ASC:  # currently we only handle higher curses...
            return
        if pattern.ticker_id not in self.ticker_id_list:
            self.ticker_id_list.append(pattern.ticker_id)
        pattern_trade = PatternTrade(pattern, buy_trigger, trade_strategy)
        if pattern_trade.id not in self.pattern_trade_dict:
            self.pattern_trade_dict[pattern_trade.id] = pattern_trade

    def check_actual_trades(self):
        self.time_stamp_check = MyDate.get_epoch_seconds_from_datetime()
        self.date_time_check = MyDate.get_date_time_from_epoch_seconds(self.time_stamp_check)
        self.__remove_finished_pattern_trades__()
        self.__init_ticker_dict__()
        self.__handle_sell_triggers__()
        self.__handle_wrong_breakout__()
        self.__handle_buy_breakout__()
        self.__handle_buy_touches__()
        self.__handle_trailing_stops__()
        self.__update_ticker_lists__()  # some entries could be deleted

    def sell_on_fibonacci_cluster_top(self):
        self.bitfinex_trade_client.delete_all_orders()
        self.bitfinex_trade_client.sell_all_assets()
        self.__clear_internal_lists__()

    def __init_ticker_dict__(self):
        self.ticker_dict = {ticker_id: self.bitfinex_trade_client.get_ticker(ticker_id)
                            for ticker_id in self.ticker_id_list}

    def __clear_internal_lists__(self):
        self.ticker_id_list = []
        self.ticker_dict = []
        self.pattern_trade_dict = {}

    def __handle_sell_triggers__(self):
        pass

    def __handle_wrong_breakout__(self):
        for ticker_id, ticker in self.ticker_dict.items():
            for key, pattern_trade in self.pattern_trade_dict.items():
                if pattern_trade.status == PTS.NEW and pattern_trade.ticker_id == ticker_id:
                    if pattern_trade.is_ticker_wrong_breakout(ticker, self.time_stamp_check):
                        del self.pattern_trade_dict[key]

    def __remove_finished_pattern_trades__(self):
        for key, pattern_trade in self.pattern_trade_dict.items():
            if pattern_trade.status == PTS.FINISHED:
                del self.pattern_trade_dict[key]
        self.__update_ticker_lists__()

    def __handle_buy_breakout__(self):
        for ticker_id, ticker in self.ticker_dict.items():
            for trade in self.pattern_trade_dict.values():
                if trade.status == PTS.NEW and trade.ticker_id == ticker_id:
                    if trade.is_ticker_breakout(ticker, self.time_stamp_check):
                        trade.buy_comment = 'Breakout at {:.2f} on {}'.format(ticker.last_price, self.date_time_check)
                        trade.order_status_sell = self.bitfinex_trade_client.buy_available(ticker_id)

    def __handle_buy_touches__(self):
        pass

    def __handle_trailing_stops__(self):
        pass

    def __create_trailing_stop_order_for_all_executed_trades__(self):
        for trades in self.pattern_trade_dict.values():
            if trades.status == PTS.EXECUTED:
                ticker_id = trades.ticker_id
                amount = trades.order_status_buy.executed_amount
                distance = trades.trailing_stop_distance
                trades.order_status_sell = self.bitfinex_trade_client.create_sell_trailing_stop_order(
                    ticker_id, amount, distance)

    def __update_ticker_lists__(self):
        self.ticker_id_list = []
        self.ticker_dict = []
        for pattern_trades in self.pattern_trade_dict:
            if pattern_trades.ticker_id not in self.ticker_id_list:
                self.ticker_id_list.append(pattern_trades.ticker_id)



