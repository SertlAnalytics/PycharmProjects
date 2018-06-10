"""
Description: This module starts the pattern detection application. It is NOT stored on git hub.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod, ApiOutputsize
from sertl_analytics.pybase.exceptions import MyProfiler
from sertl_analytics.constants.pattern_constants import FT, Indices, CN
from pattern_configuration import config
from pattern_detection_controller import PatternDetectionController


my_profiler = MyProfiler()

config.get_data_from_db = True
config.api_period = ApiPeriod.DAILY
config.pattern_type_list = FT.get_all()
# config.pattern_type_list = [FT.CHANNEL]
config.plot_data = True
config.statistics_excel_file_name = 'statistics_pattern_06-04.xlsx'
config.statistics_excel_file_name = ''
config.bound_upper_value = CN.CLOSE
config.bound_lower_value = CN.CLOSE
config.breakout_over_congestion_range = False
config.show_final_statistics = True
config.max_number_securities = 1000
config.breakout_range_pct = 0.05  # default is 0.05
config.use_index(Indices.MIXED)
# config.use_own_dic({'CAT': 'American'})  # "INTC": "Intel",  "NKE": "Nike", "V": "Visa",  "GE": "GE", MRK (Merck)
# "FCEL": "FuelCell" "KO": "Coca Cola" # "BMWYY": "BMW" NKE	Nike, "CSCO": "Nike", "AXP": "American", "WMT": "Wall mart",
# config.and_clause = "Date BETWEEN '2017-10-25' AND '2018-04-18'"
config.and_clause = "Date BETWEEN '2017-10-01' AND '2019-07-18'"
# config.and_clause = ''
config.api_output_size = ApiOutputsize.COMPACT

pattern_controller = PatternDetectionController()
pattern_controller.run_pattern_checker('')

my_profiler.disable(False)

# Head Shoulder: GE Date BETWEEN '2016-01-25' AND '2019-10-30'
# Triangle: Processing KO (Coca Cola)...Date BETWEEN '2017-10-25' AND '2019-10-30'
"""
'CAT': 'Caterpillar'
"""
