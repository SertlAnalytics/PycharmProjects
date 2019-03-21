"""
Description: This module contains the run commands for the current module test.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-13
"""

from test.test_factory import TestFactory

test_factory = TestFactory(True)
# test_factory.run_test_for_my_math()
# test_factory.run_test_for_stock_database()
# test_factory.run_test_for_my_dates()
# test_factory.run_test_for_bitfinex()
test_factory.run_test_for_ibkr()


