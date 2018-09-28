"""
Description: This module starts the pattern detection application. It is NOT stored on git hub.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from sertl_analytics.myprofiler import MyProfiler
from sertl_analytics.constants.pattern_constants import FT, Indices, CN, BT, TSTR, PRD, OPS
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_dash.my_dash_for_pattern import MyDash4Pattern
from pattern_bitfinex import BitfinexConfiguration


my_profiler = MyProfiler()
sys_config = SystemConfiguration()
bitfinex_config = BitfinexConfiguration()
bitfinex_config.is_simulation = True
bitfinex_config.trade_strategy_dict = {BT.BREAKOUT: [TSTR.LIMIT, TSTR.TRAILING_STEPPED_STOP, TSTR.TRAILING_STOP],
                                       BT.TOUCH_POINT: [TSTR.LIMIT, TSTR.TRAILING_STOP]}

# debugger.pattern_range_position_list = [217, 224, 242]

sys_config.config.get_data_from_db = False
sys_config.config.api_period = PRD.INTRADAY
sys_config.config.pattern_type_list = FT.get_all()
sys_config.prediction_mode_active = True
sys_config.config.save_pattern_data = True
# sys_config.config.pattern_type_list = [FT.TRIANGLE]
# sys_config.config.pattern_type_list = [FT.TRIANGLE_DOWN, FT.TRIANGLE_UP, FT.TRIANGLE_BOTTOM]
sys_config.config.plot_data = True
sys_config.config.plot_only_pattern_with_fibonacci_waves = False
sys_config.config.plot_min_max = True
sys_config.config.plot_volume = False
sys_config.config.length_for_local_min_max = 2
sys_config.config.length_for_local_min_max_fibonacci = 1
sys_config.config.statistics_excel_file_name = 'pattern_statistics/statistics_pattern_06-11.xlsx'
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
# sys_config.config.use_own_dic({'TSLA': 'T', 'DWDP': 'DuPont', 'MMM': 'M', 'CAT': 'c', 'GS': 'Goldman'})
# sys_config.config.use_own_dic({'BTC_USD': 'American'})  # "INTC": "Intel",  "NKE": "Nike", "V": "Visa",  "GE": "GE", MRK (Merck)
# "FCEL": "FuelCell" "KO": "Coca Cola" # "BMWYY": "BMW" NKE	Nike, "CSCO": "Nike", "AXP": "American", "WMT": "Wall mart",
# sys_config.config.and_clause = "Date BETWEEN '2017-10-25' AND '2018-04-18'"
sys_config.config.and_clause = "Date BETWEEN '2018-03-01' AND '2019-09-21'"
# sys_config.config.and_clause = ''
sys_config.config.api_output_size = OPS.COMPACT
my_dash = MyDash4Pattern(sys_config, bitfinex_config)
my_dash.get_pattern()
my_dash.run_on_server()
my_profiler.disable(False)

# Head Shoulder: GE Date BETWEEN '2016-01-25' AND '2019-10-30'
# Triangle: Processing KO (Coca Cola)...Date BETWEEN '2017-10-25' AND '2019-10-30'
# NEO_USD, EOS_USD, IOTA_USD, BCH_USD, BTC_USD, ETH_USD, LTC_USD
