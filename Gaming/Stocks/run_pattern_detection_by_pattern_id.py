"""
Description: This module starts the pattern detection application. It is NOT stored on git hub.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from sertl_analytics.myprofiler import MyProfiler
from sertl_analytics.constants.pattern_constants import FT, Indices, CN, PRD, OPS, TP, BT, TSTR
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_detection_controller import PatternDetectionController
from pattern_test.trade_test import TradeTest, TradeTestApi


my_profiler = MyProfiler()

sys_config = SystemConfiguration()
sys_config.exchange_config.trade_strategy_dict = {BT.BREAKOUT: [TSTR.TRAILING_STEPPED_STOP]}
sys_config.config.pattern_type_list = FT.get_all()
sys_config.config.plot_data = True
sys_config.config.with_trading = True
sys_config.config.save_pattern_data = False
sys_config.config.save_trade_data = False
sys_config.config.plot_only_pattern_with_fibonacci_waves = False
sys_config.config.plot_min_max = True
sys_config.config.plot_volume = False
sys_config.config.length_for_local_min_max = 2
sys_config.config.length_for_local_min_max_fibonacci = 1
sys_config.config.bound_upper_value = CN.CLOSE
sys_config.config.bound_lower_value = CN.CLOSE
sys_config.config.breakout_range_pct = 0.05  # default is 0.05
sys_config.config.fibonacci_tolerance_pct = 0.1  # default is 0.20
sys_config.config.pattern_ids_to_find = ['1_1_1_CAT_10_2017-10-31_00:00_2017-11-15_00:00']

pattern_controller = PatternDetectionController(sys_config)
pattern_controller.run_pattern_detector()
my_profiler.disable(False)

