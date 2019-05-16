"""
Description: This module contains the main test factory for the base functions.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-13
"""

from mymath import MyMathTest
from mydates import MyDateTest
from my_text import MyTextTest
from sertl_analytics.exchanges.bitfinex_trade_client import MyBitfinexTest
from sertl_analytics.exchanges.interactive_broker_trade_client import MyIBKRTest
from pattern_database.stock_database import StockDatabaseTest


class TestFactory:
    def __init__(self, print_all_test_cases_for_units=False):
        self._print_all_test_cases_for_units = print_all_test_cases_for_units

    def run_test_for_my_math(self):
        test = MyMathTest(self._print_all_test_cases_for_units)
        test.run_test_for_all_units(test.class_name_tested)

    def run_test_for_stock_database(self):
        test = StockDatabaseTest(self._print_all_test_cases_for_units)
        test.run_test_for_all_units(test.class_name_tested)

    def run_test_for_my_dates(self):
        test = MyDateTest(self._print_all_test_cases_for_units)
        test.run_test_for_all_units(test.class_name_tested)

    def run_test_for_my_text(self):
        test = MyTextTest(self._print_all_test_cases_for_units)
        test.run_test_for_all_units(test.class_name_tested)

    def run_test_for_bitfinex(self):
        test = MyBitfinexTest(self._print_all_test_cases_for_units)
        test.run_test_for_all_units(test.class_name_tested)

    def run_test_for_ibkr(self):
        test = MyIBKRTest(self._print_all_test_cases_for_units)
        test.run_test_for_all_units(test.class_name_tested)