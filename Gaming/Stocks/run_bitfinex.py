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
from sertl_analytics.constants.pattern_constants import FT, Indices, CN
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_detection_controller import PatternDetectionController

exchange_config = BitfinexConfiguration()
exchange_config.buy_order_value_max = 100
exchange_config.is_simulation = True

my_trade_client = MyBitfinexTradeClient(exchange_config)
ticker = my_trade_client.get_ticker(TP.EOS_USD)
# my_trade_client.print_active_balances()
# my_trade_client.buy_available(TP.EOS_USD)
# my_trade_client.sell_all(TP.EOS_USD)
# my_trade_client.sell_all_assets()
# my_trade_client.create_sell_stop_loss_order(TP.EOS_USD, 50, 5.5)
# my_trade_client.create_buy_stop_order(TP.IOT_USD, 5000, 0.9)
# my_trade_client.create_buy_limit_order(TP.NEO_USD, 2, 15.0)
# my_trade_client.print_order_status(16111930471)
# my_trade_client.delete_order(16146685034)
my_trade_client.print_active_orders()
# my_trade_client.update_order(16146685034, 5.6)
# my_trade_client.delete_all_orders()


my_profiler = MyProfiler()
sys_config = SystemConfiguration()

debugger.pattern_range_position_list = [98, 112]

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
# sys_config.config.pattern_type_list = [FT.TKE_BOTTOM, FT.TKE_TOP, FT.HEAD_SHOULDER_BOTTOM, FT.HEAD_SHOULDER]
sys_config.config.plot_data = True
sys_config.prediction_mode_active = True
sys_config.config.save_pattern_data = True
sys_config.config.plot_only_pattern_with_fibonacci_waves = False
sys_config.config.plot_min_max = True
sys_config.config.plot_volume = False
sys_config.config.length_for_local_min_max = 2
sys_config.config.length_for_local_min_max_fibonacci = 1
sys_config.config.statistics_excel_file_name = 'pattern_statistics/statistics_pattern_08-20.xlsx'
sys_config.config.statistics_excel_file_name = ''
sys_config.config.statistics_constraints_excel_file_name = ''
sys_config.config.bound_upper_value = CN.CLOSE
sys_config.config.bound_lower_value = CN.CLOSE
sys_config.config.breakout_over_congestion_range = False
sys_config.config.show_final_statistics = True
sys_config.config.max_number_securities = 1000
sys_config.config.breakout_range_pct = 0.05  # default is 0.05
sys_config.config.fibonacci_tolerance_pct = 0.1  # default is 0.20
sys_config.config.fibonacci_detail_print = True
# sys_config.config.use_index(Indices.DOW_JONES)
sys_config.config.use_index(Indices.CRYPTO_CCY)
# sys_config.config.use_own_dic({'XOM': 'b', 'GS': 'b'}) # BCH_USD, BTC_USD, ETH_USD, LTC_USD, NEO_USD, EOS_USD, IOTA_USD
sys_config.config.use_own_dic({'ETH_USD': 'a'})
# sys_config.config.use_own_dic({'TSLA': 'T', 'DWDP': 'DuPont', 'MMM': 'M', 'CAT': 'c', 'FCEL': 'c', 'GS': 'Goldman', 'NKE': 'Nike'})
# sys_config.config.use_own_dic({'NEO_USD': 'American', "INTC": "Intel", "NKE": "Nike", "V": "Visa", "GE": "GE", 'MRK':'Merck',
#                     "KO": "Coca Cola", "BMWYY": "BMW", 'NKE':'Nike', "CSCO": "Nike", "AXP": "American",
#                     "WMT": "Wall mart"})
# sys_config.config.and_clause = "Date BETWEEN '2017-10-25' AND '2018-04-18'"
sys_config.config.and_clause = "Date BETWEEN '2018-03-01' AND '2018-07-05'"
# sys_config.config.and_clause = ''
sys_config.config.api_output_size = ApiOutputsize.COMPACT

pattern_controller = PatternDetectionController(sys_config)
# browser = MyUrlBrowser4CB()
# browser.order_item('ticker', 100)
pattern_controller.run_pattern_detector()

