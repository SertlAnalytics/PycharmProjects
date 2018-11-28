"""
Description: This module is the abstract base class for all exchanges, i.e they have to implement those functions.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-08-28
"""

from abc import ABCMeta, abstractmethod
from sertl_analytics.exchanges.exchange_cls import Order


class ExchangeInterface:
    __metaclass__ = ABCMeta

    @classmethod
    def version(cls): return 1.0

    @abstractmethod
    def delete_order(self, order_id: int, is_order_simulation: bool):
        raise NotImplementedError

    @abstractmethod
    def delete_all_orders(self):
        raise NotImplementedError

    @abstractmethod
    def create_order(self, order: Order, is_order_simulation: bool):
        raise NotImplementedError

    @abstractmethod
    def get_order(self, order_id: int):
        raise NotImplementedError

    @abstractmethod
    def update_order(self, order_id: int, price_new: float, is_order_simulation: bool):
        raise NotImplementedError

    @abstractmethod
    def get_active_orders(self):
        raise NotImplementedError

    @abstractmethod
    def get_active_positions(self):
        raise NotImplementedError

    @abstractmethod
    def get_past_trades(self, symbol: str, from_time_stamp: float):
        raise NotImplementedError

    @abstractmethod
    def get_balances(self):
        raise NotImplementedError

    @abstractmethod
    def get_history(self, since_ts: int, until_ts, limit: int):
        raise NotImplementedError

    @abstractmethod
    def get_symbols(self):
        raise NotImplementedError

    @abstractmethod
    def get_ticker(self, symbol: str):
        raise NotImplementedError

    @abstractmethod
    def get_candles(self, symbol: str, period: str, aggregation: int, section='hist',
                    limit=200, ms_start=0, ms_end=0, sort=1):
        raise NotImplementedError

    @abstractmethod
    def get_order_book(self, symbol: str):
        raise NotImplementedError

    @abstractmethod
    def print_active_orders(self):
        raise NotImplementedError

    @abstractmethod
    def print_active_balances(self, prefix=''):
        raise NotImplementedError

