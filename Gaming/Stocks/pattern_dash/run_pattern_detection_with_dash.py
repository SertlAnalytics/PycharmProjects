"""
Description: This module starts the pattern detection application. It is NOT stored on git hub.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from sertl_analytics.myprofiler import MyProfiler
from sertl_analytics.constants.pattern_constants import FT, INDICES, CN, BT, TSTR, PRD, OPS
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_dash.my_dash_for_pattern import MyDash4Pattern

my_profiler = MyProfiler()
sys_config = SystemConfiguration(run_on_server=True)

sys_config.data_provider.from_db = False
sys_config.data_provider.period = PRD.INTRADAY
sys_config.data_provider.aggregation = 15  # ToDo: Back to 15
sys_config.data_provider.output_size = OPS.COMPACT
sys_config.data_provider.limit = 200
sys_config.exchange_config.deactivate_automatic_trading()
sys_config.exchange_config.trade_strategy_dict = {
    BT.BREAKOUT: [TSTR.LIMIT, TSTR.LIMIT_FIX, TSTR.TRAILING_STEPPED_STOP, TSTR.TRAILING_STOP],
    # BT.FC_TICKS: [TSTR.TRAILING_STOP]
}
sys_config.exchange_config.delete_vanished_patterns_from_trade_dict = False
sys_config.exchange_config.massive_breakout_pct = 5
sys_config.config.simple_moving_average_number = 20
sys_config.config.trading_last_price_mean_aggregation = 4

# debugger.pattern_range_position_list = [217, 224, 242]

sys_config.config.pattern_type_list = FT.get_all()
sys_config.config.with_trading = True
sys_config.config.save_pattern_data = True
sys_config.config.save_trade_data = True
sys_config.config.save_wave_data = False  # they are saved within other threads
# sys_config.config.pattern_type_list = [FT.TRIANGLE]
sys_config.config.pattern_type_list = FT.get_all()
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
sys_config.data_provider.use_index(INDICES.CRYPTO_CCY)
sys_config.fibonacci_wave_data_handler.load_data(PRD.ALL)
my_dash = MyDash4Pattern(sys_config)
my_dash.get_pattern()
my_dash.run_on_server()
my_profiler.disable(False)

# Head Shoulder: GE Date BETWEEN '2016-01-25' AND '2019-10-30'
# Triangle: Processing KO (Coca Cola)...Date BETWEEN '2017-10-25' AND '2019-10-30'
# NEO_USD, EOS_USD, IOTA_USD, BCH_USD, BTC_USD, ETH_USD, LTC_USD
