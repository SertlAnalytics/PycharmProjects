"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, BT, TSTR, TTC, TP, INDICES
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList
from pattern_test.trade_test import TradeTest, TradeTestApi


api = TradeTestApi()
api.test_process = TP.BACK_TESTING
back_testing = TradeTest(api)

back_testing.sys_config.config.pattern_type_list = FT.get_long_trade_able_types()
# back_testing.sys_config.config.pattern_type_list = [FT.TRIANGLE_DOWN]
back_testing.sys_config.config.save_trade_data = True
back_testing.sys_config.config.simple_moving_average_number = 20
back_testing.sys_config.config.trading_last_price_mean_aggregation = 16

# ******** START setup **********
api.buy_trigger = BT.BREAKOUT
api.trade_strategy = TSTR.SMA

# ******** END setup **********

ticker_dic = IndicesComponentList.get_ticker_name_dic(INDICES.DOW_JONES)
# ticker_dic = IndicesComponentList.get_ticker_name_dic(INDICES.CRYPTO_CCY)
# ticker_dic = {'CVX': 'a'}
api.and_clause = "Date BETWEEN '2018-06-07' AND '2019-09-04'"

# 2018-02-09_00:00_2018-04-03
for symbol in ticker_dic:
    api.symbol = symbol
    back_testing.run_back_testing(api)





