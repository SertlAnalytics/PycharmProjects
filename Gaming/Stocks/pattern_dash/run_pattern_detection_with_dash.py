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

sys_config.data_provider.from_db = False
sys_config.data_provider.period = PRD.INTRADAY
sys_config.data_provider.aggregation = 15
sys_config.data_provider.output_size = OPS.COMPACT
sys_config.data_provider.limit = 200

sys_config.exchange_config = BitfinexConfiguration()
sys_config.exchange_config.is_simulation = True
sys_config.exchange_config.trade_strategy_dict = {
    BT.BREAKOUT: [TSTR.LIMIT, TSTR.TRAILING_STEPPED_STOP, TSTR.TRAILING_STOP],
    BT.TOUCH_POINT: [TSTR.LIMIT, TSTR.TRAILING_STOP]}

# debugger.pattern_range_position_list = [217, 224, 242]

sys_config.config.pattern_type_list = FT.get_all()
sys_config.prediction_mode_active = True
sys_config.config.with_trading = True
sys_config.config.save_pattern_data = True
sys_config.config.save_trade_data = False
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
sys_config.config.breakout_range_pct = 0.05  # default is 0.05
sys_config.config.fibonacci_tolerance_pct = 0.1  # default is 0.20
sys_config.config.fibonacci_detail_print = True
# sys_config.config.use_index(Indices.DOW_JONES)
sys_config.data_provider.use_index(Indices.CRYPTO_CCY)
my_dash = MyDash4Pattern(sys_config)
my_dash.get_pattern()
my_dash.run_on_server()
my_profiler.disable(False)

# Head Shoulder: GE Date BETWEEN '2016-01-25' AND '2019-10-30'
# Triangle: Processing KO (Coca Cola)...Date BETWEEN '2017-10-25' AND '2019-10-30'
# NEO_USD, EOS_USD, IOTA_USD, BCH_USD, BTC_USD, ETH_USD, LTC_USD
