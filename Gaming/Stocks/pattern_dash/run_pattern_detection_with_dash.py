"""
Description: This module starts the pattern detection application. It is NOT stored on git hub.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod, ApiOutputsize
from sertl_analytics.myprofiler import MyProfiler
from sertl_analytics.constants.pattern_constants import FT, Indices, CN
from pattern_configuration import config, debugger
from pattern_detection_controller import PatternDetectionController
from pattern_dash.my_dash_for_pattern import MyDash4Pattern


my_profiler = MyProfiler()

# debugger.pattern_range_position_list = [217, 224, 242]

config.get_data_from_db = False
config.api_period = ApiPeriod.INTRADAY
config.pattern_type_list = FT.get_all()
# config.pattern_type_list = [FT.CHANNEL_DOWN]
# config.pattern_type_list = [FT.TRIANGLE_DOWN, FT.TRIANGLE_UP, FT.TRIANGLE_BOTTOM]
config.plot_data = True
config.plot_only_pattern_with_fibonacci_waves = False
config.plot_min_max = True
config.plot_volume = False
config.length_for_local_min_max = 2
config.length_for_local_min_max_fibonacci = 1
config.statistics_excel_file_name = 'pattern_statistics/statistics_pattern_06-11.xlsx'
config.statistics_excel_file_name = ''
config.statistics_constraints_excel_file_name = ''
config.bound_upper_value = CN.CLOSE
config.bound_lower_value = CN.CLOSE
config.breakout_over_congestion_range = False
config.show_final_statistics = True
config.max_number_securities = 1000
config.breakout_range_pct = 0.05  # default is 0.05
config.fibonacci_tolerance_pct = 0.1  # default is 0.20
config.fibonacci_detail_print = True
# config.use_index(Indices.DOW_JONES)
config.use_index(Indices.CRYPTO_CCY)
# config.use_own_dic({'TSLA': 'T', 'DWDP': 'DuPont', 'MMM': 'M', 'CAT': 'c', 'GS': 'Goldman'})
# config.use_own_dic({'EOS_USD': 'American'})  # "INTC": "Intel",  "NKE": "Nike", "V": "Visa",  "GE": "GE", MRK (Merck)
# "FCEL": "FuelCell" "KO": "Coca Cola" # "BMWYY": "BMW" NKE	Nike, "CSCO": "Nike", "AXP": "American", "WMT": "Wall mart",
# config.and_clause = "Date BETWEEN '2017-10-25' AND '2018-04-18'"
config.and_clause = "Date BETWEEN '2018-03-01' AND '2019-09-21'"
# config.and_clause = ''
config.api_output_size = ApiOutputsize.COMPACT

my_dash = MyDash4Pattern()
my_dash.get_pattern()
my_dash.run_on_server()

my_profiler.disable(False)

# Head Shoulder: GE Date BETWEEN '2016-01-25' AND '2019-10-30'
# Triangle: Processing KO (Coca Cola)...Date BETWEEN '2017-10-25' AND '2019-10-30'
# NEO_USD, EOS_USD, IOTA_USD, BCH_USD, BTC_USD, ETH_USD, LTC_USD
