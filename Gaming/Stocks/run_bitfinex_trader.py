"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_bitfinex import MyBitfinexTradeClient
from sertl_analytics.exchanges.bitfinex import BitfinexConfiguration, TP
from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod, ApiOutputsize
from sertl_analytics.myprofiler import MyProfiler
from sertl_analytics.constants.pattern_constants import FT, Indices, CN, BT, ST, TBT, TSTR
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_detection_controller import PatternDetectionController
from pattern_bitfinex import BitfinexConfiguration
from pattern_trade_handler import PatternTradeHandler
import time

exchange_config = BitfinexConfiguration()
exchange_config.buy_order_value_max = 100
exchange_config.is_simulation = True

sys_config = SystemConfiguration()

intraday = False
if intraday:
    sys_config.config.get_data_from_db = False
    sys_config.config.api_period = ApiPeriod.INTRADAY
    sys_config.config.api_period_aggregation = 5
else:
    sys_config.config.get_data_from_db = True
    sys_config.config.api_period = ApiPeriod.DAILY
    sys_config.config.api_period_aggregation = 1
sys_config.config.pattern_type_list = FT.get_all()
sys_config.config.pattern_type_list = [FT.TRIANGLE_DOWN]
sys_config.config.plot_data = True
sys_config.prediction_mode_active = True
sys_config.config.save_pattern_features = True
# sys_config.config.use_index(Indices.DOW_JONES)
sys_config.config.use_index(Indices.CRYPTO_CCY)
# sys_config.config.use_own_dic({'XOM': 'b', 'GS': 'b'}) # BCH_USD, BTC_USD, ETH_USD, LTC_USD, NEO_USD, EOS_USD, IOTA_USD
sys_config.config.use_own_dic({'ETH_USD': 'a'})
sys_config.config.and_clause = "Date BETWEEN '2018-03-01' AND '2018-07-05'"

trade_handler = PatternTradeHandler(sys_config, exchange_config)
pattern_controller = PatternDetectionController(sys_config)
detector = pattern_controller.get_detector_for_dash(sys_config, 'ETH_USD', sys_config.config.and_clause)
pattern_list = detector.get_pattern_list_for_buy_trigger(BT.BREAKOUT)
trade_handler.add_pattern_list_for_trade(pattern_list, BT.BREAKOUT, TBT.EXPECTED_WIN, TSTR.LIMIT)
time.sleep(10)
trade_handler.check_actual_trades(500)
# time.sleep(10)
# trade_handler.check_actual_trades(200)  # sell stop loss expected
# trade_handler.check_actual_trades(1000)  # sell limit expected


