"""
Description: This module contains  a test case for class variables compared with instance variables
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


class Exchange:
    buy_order_value_max = 100

    def __init__(self, max_value: float):
        self._max_value = max_value


class BitfinexExchange(Exchange):
    buy_order_value_max = 150

    def __init__(self, max_value: float):
        Exchange.__init__(self, max_value)
        self._max_value_2 = max_value * 2


exchange = Exchange(200)
bitfinex = BitfinexExchange(200)

print('After: init')
print('exchange.buy_order_value_max = {}'.format(exchange.buy_order_value_max))
print('bitfinex.buy_order_value_max = {}'.format(bitfinex.buy_order_value_max))


Exchange.buy_order_value_max = 200
print('\nAfter: Exchange.buy_order_value_max = 200')
print('exchange.buy_order_value_max = {}'.format(exchange.buy_order_value_max))
print('bitfinex.buy_order_value_max = {}'.format(bitfinex.buy_order_value_max))

BitfinexExchange.buy_order_value_max = 400
print('\nAfter: BitfinexExchange.buy_order_value_max = 400')
print('exchange.buy_order_value_max = {}'.format(exchange.buy_order_value_max))
print('bitfinex.buy_order_value_max = {}'.format(bitfinex.buy_order_value_max))

Exchange.buy_order_value_max = 600
print('\nAfter: Exchange.buy_order_value_max = 600')
print('exchange.buy_order_value_max = {}'.format(exchange.buy_order_value_max))
print('bitfinex.buy_order_value_max = {}'.format(bitfinex.buy_order_value_max))
