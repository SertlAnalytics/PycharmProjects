"""
Description: This module is the abstract base class for all exchanges, i.e they have to implement those functions.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-08-28
"""

from abc import ABCMeta, abstractmethod
from sertl_analytics.exchanges.exchange_cls import Order
from sertl_analytics.test.my_test_abc import TestInterface
from sertl_analytics.constants.pattern_constants import PRD, CN
from sertl_analytics.mydates import MyDate


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


class MyExchangeTest(TestInterface):
    GET_TICKER = 'get_ticker'
    GET_CANDLES = 'get_candles'

    def __init__(self, print_all_test_cases_for_units=False):
        self._exchange = self.__get_exchange__()
        self._symbol = self.__get_symbol__()
        self._order_id = self.__get_order_id__()
        TestInterface.__init__(self, print_all_test_cases_for_units)

    @staticmethod
    def __get_exchange__():
        return ExchangeInterface()

    @staticmethod
    def __get_symbol__():
        return ''

    @staticmethod
    def __get_order_id__():
        return ''

    def test_delete_order(self, order_id: int, is_order_simulation: bool):
        self._exchange.delete_order(order_id, is_order_simulation)

    def test_delete_all_orders(self):
        self._exchange.delete_all_orders()

    def test_create_order(self, order: Order, is_order_simulation: bool):
        self._exchange.create_order(order, is_order_simulation)

    def test_get_order(self, order_id: int):
        self._exchange.get_order(order_id)

    def test_update_order(self, order_id: int, price_new: float, is_order_simulation: bool):
        self._exchange.update_order(order_id, price_new, is_order_simulation)

    def test_get_active_orders(self):
        self._exchange.get_active_orders()

    def test_get_active_positions(self):
        self._exchange.get_active_positions()

    def test_get_past_trades(self, symbol: str, from_time_stamp: float):
        self._exchange.get_past_trades(symbol, from_time_stamp)

    def test_get_balances(self):
        self._exchange.get_balances()

    def test_get_history(self, since_ts: int, until_ts, limit: int):
        self._exchange.get_history(since_ts, until_ts, limit)

    def test_get_symbols(self):
        self._exchange.get_symbols()

    def test_get_ticker(self):
        test_list = [[self._symbol, self._symbol]]
        test_case_dict = {}
        for test in test_list:
            test_data = test[0]
            key = '{}'.format(test_data)
            ticker = self._exchange.get_ticker(self._symbol)
            test_case_dict[key] = [ticker.ticker_id, test[1]]
        return self.__verify_test_cases__(self.GET_TICKER, test_case_dict)

    def test_get_candles(self):
        """
        get_candles(self, symbol: str, period: str, aggregation: int, section='hist',
                    limit=200, ms_start=0, ms_end=0, sort=1):
        """
        test_list = self.__get_test_list_for_get_candles__()
        test_case_dict = {}
        for test in test_list:
            symbol, period, aggregation, section, limit = test[0]
            key = '{}'.format(test[0])
            if section == '' and limit == 0:
                df = self._exchange.get_candles(symbol, period, aggregation)
            elif section != '' and limit == 0:
                df = self._exchange.get_candles(symbol, period, aggregation, section=section)
            elif section == '' and limit != 0:
                df = self._exchange.get_candles(symbol, period, aggregation, limit=limit)
            else:
                df = self._exchange.get_candles(symbol, period, aggregation, section=section, limit=limit)
            result_list = [self._symbol, df.shape[0]]
            test_case_dict[key] = [result_list, test[1]]
        return self.__verify_test_cases__(self.GET_CANDLES, test_case_dict)

    def __get_test_list_for_get_candles__(self):
        return [
            [[self._symbol, PRD.DAILY, 1, '', 0], [self._symbol, 120]],
            [[self._symbol, PRD.DAILY, 1, '', 150], [self._symbol, 150]],
            [[self._symbol, PRD.INTRADAY, 15, '', 0], [self._symbol, 120]],
            [[self._symbol, PRD.INTRADAY, 15, '', 100], [self._symbol, 100]],
            [[self._symbol, PRD.INTRADAY, 30, '', 0], [self._symbol, 120]],
            [[self._symbol, PRD.INTRADAY, 30, '', 100], [self._symbol, 100]],
        ]

    def test_get_order_book(self, symbol: str):
        self._exchange.get_order_book(symbol)

    def test_print_active_orders(self):
        self._exchange.print_active_orders()

    def test_print_active_balances(self, prefix=''):
        self._exchange.print_active_balances(prefix)

    def __get_class_name_tested__(self):
        return self._exchange.__class__.__name__

    def __run_test_for_unit__(self, unit: str) -> bool:
        if unit == self.GET_TICKER:
            return self.test_get_ticker()
        elif unit == self.GET_CANDLES:
            return self.test_get_candles()

    def __get_test_unit_list__(self):
        # return [self.GET_TIME_DIFFERNCE_IN_SECONDS]
        return [self.GET_TICKER,
                self.GET_CANDLES
                ]

