"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_bitfinex import MyBitfinexTradeClient
from sertl_analytics.exchanges.bitfinex import BitfinexConfiguration, TP

exchange_config = BitfinexConfiguration()
exchange_config.buy_order_value_max = 100
exchange_config.is_simulation = True

my_trade_client = MyBitfinexTradeClient(exchange_config)
# my_trade_client.print_active_balances()
my_trade_client.buy_available(TP.EOS_USD)
# my_trade_client.sell_all(TP.EOS_USD)
# my_trade_client.sell_all_assets()
# my_trade_client.create_sell_stop_loss_order(TP.IOT_USD, 5000, 0.5)
# my_trade_client.create_buy_stop_order(TP.IOT_USD, 5000, 0.9)
# my_trade_client.create_buy_limit_order(TP.NEO_USD, 2, 15.0)
# order_status = my_trade_client.create_buy_limit_order()
# my_trade_client.print_order_status(16111930471)
# my_trade_client.delete_order(16113337659)
# my_trade_client.print_active_orders()
# my_trade_client.delete_all_orders()

