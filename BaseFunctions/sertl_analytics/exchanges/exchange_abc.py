"""
Description: This module is the abstract base class for all exchanges, i.e they have to implement those functions.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-08-28
"""

from abc import ABCMeta, abstractmethod
from sertl_analytics.exchanges.exchange_cls import Order


class ExInterface:
    __metaclass__ = ABCMeta

    @classmethod
    def version(cls): return 1.0

    @abstractmethod
    def delete_order(self, order_id: int):
        raise NotImplementedError

    @abstractmethod
    def delete_all_orders(self):
        raise NotImplementedError

    @abstractmethod
    def create_order(self, order: Order):
        raise NotImplementedError

    @abstractmethod
    def get_order(self, order_id: int):
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
    def get_order_book(self, symbol: str):
        raise NotImplementedError