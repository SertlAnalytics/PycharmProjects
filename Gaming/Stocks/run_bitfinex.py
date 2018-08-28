"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_bitfinex import MyBitfinexTradeClient

my_trade_client = MyBitfinexTradeClient()
# print(my_bitfinex.get_symbols())
print(my_trade_client.bitfinex.get_balances())
# print(my_bitfinex.get_active_orders())
# print(my_bitfinex.get_order(16021592271))
# print(my_bitfinex.get_past_trades('neousd', 10000))
# print(my_bitfinex.get_active_positions())
# print(my_bitfinex.get_ticker('eosusd'))
# my_bitfinex.sell_all('iot')
my_trade_client.bitfinex.buy_available('btcusd')
# print(my_bitfinex.get_summary())
# from pattern_bitfinex import MyBitfinexTradeClient
#
# my_trade_client = MyBitfinexTradeClient()
# print(my_trade_client.get_balances())
# # print(my_trade_client.place_order('30.0', '17.0', 'buy', 'exchange market', 'eosusd'))
# print(my_trade_client.get_active_orders())
# # print(my_trade_client.delete_order(16021592271))
# print(my_trade_client.get_active_orders())
# exchange limit
