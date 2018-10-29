"""
Description: This module is the trigger for single trade tests.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-14
"""

from sertl_analytics.constants.pattern_constants import FT, BT, TSTR, TTC, TP
from pattern_test.trade_test_cases import TradeTestCaseFactory
from pattern_test.trade_test import TradeTest, TradeTestApi

api = TradeTestApi()
api.test_process = TP.TEST_SINGLE
api.volume_increase = 10
bitfinex_test = TradeTest(api)

# ******** START setup **********
triangle = True
if triangle:
    api.pattern_type = FT.TRIANGLE_DOWN
    api.buy_trigger = BT.BREAKOUT
    api.trade_strategy = TSTR.TRAILING_STEPPED_STOP
    api.test_process = TTC.BUY_SELL_STOP_LOSS
else:
    api.pattern_type = FT.FIBONACCI_DESC
    api.buy_trigger = BT.TOUCH_POINT
    api.trade_strategy = TSTR.TRAILING_STOP
    api.test_process = TTC.BUY_ADJUST_STOP_LOSS
# ******** END setup **********

test_case = TradeTestCaseFactory.get_test_case(api)
bitfinex_test.run_test_case(test_case)




