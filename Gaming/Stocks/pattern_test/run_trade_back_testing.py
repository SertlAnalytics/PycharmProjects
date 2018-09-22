"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, BT, TSTR, TTC, TP, Indices
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList
from pattern_test.trade_test import TradeTest, TradeTestApi


back_testing = TradeTest(TP.BACK_TESTING)
api = TradeTestApi()

back_testing.sys_config.config.pattern_type_list = [FT.TRIANGLE_DOWN]
back_testing.sys_config.config.save_trade_data = True

# ******** START setup **********
api.buy_trigger = BT.TOUCH_POINT
api.trade_strategy = TSTR.TRAILING_STOP
api.process = TTC.BACK_TESTING

# ******** END setup **********

ticker_dic = IndicesComponentList.get_ticker_name_dic(Indices.DOW_JONES)
# ticker_dic = IndicesComponentList.get_ticker_name_dic(Indices.CRYPTO_CCY)
ticker_dic = {'DIS': 'a'}
api.and_clause = "Date BETWEEN '2018-01-09' AND '2018-06-03'"

# 2018-02-09_00:00_2018-04-03
for symbol in ticker_dic:
    api.symbol = symbol
    back_testing.run_back_testing(api)





