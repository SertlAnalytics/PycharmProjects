"""
Description: This module starts the pattern detection application. It is NOT stored on git hub.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from sertl_analytics.constants.pattern_constants import CN, BT, TSTR, FT
from pattern_system_configuration import SystemConfiguration
from pattern_detection_controller import PatternDetectionController

sys_config = SystemConfiguration()
sys_config.sound_machine.is_active = False
sys_config.exchange_config.trade_strategy_dict = {BT.BREAKOUT: [TSTR.LIMIT]}
sys_config.exchange_config.default_trade_strategy_dict = {BT.BREAKOUT: TSTR.LIMIT}
sys_config.config.plot_data = True
# sys_config.config.with_trade_part = False
sys_config.config.with_trading = True
sys_config.config.simple_moving_average_number = 20
sys_config.config.trading_last_price_mean_aggregation = 16
sys_config.config.save_pattern_data = False
sys_config.config.save_trade_data = False
sys_config.config.plot_only_pattern_with_fibonacci_waves = False
sys_config.config.plot_min_max = True
sys_config.config.plot_volume = False
sys_config.config.length_for_local_min_max = 2
sys_config.config.length_for_local_min_max_fibonacci = 1
sys_config.config.bound_upper_value = CN.CLOSE
sys_config.config.bound_lower_value = CN.CLOSE
sys_config.config.fibonacci_tolerance_pct = 0.1  # default is 0.20

trade_strategy_dict_list = [{BT.BREAKOUT: [TSTR.LIMIT]}, {BT.BREAKOUT: [TSTR.TRAILING_STOP]},
                            {BT.BREAKOUT: [TSTR.TRAILING_STEPPED_STOP]}]

trade_strategy_dict_list = [{BT.BREAKOUT: [TSTR.SMA]}]

pattern_type_pattern_id_dict = {
    FT.CHANNEL: ['1_1_1_AXP_10_2018-05-22_00:00_2018-07-12_00:00'],
    FT.CHANNEL_DOWN: ['1_1_1_MMM_12_2018-03-12_00:00_2018-05-21_00:00'],
    FT.TRIANGLE: ['1_1_1_CVX_20_2017-10-24_00:00_2017-11-24_00:00'],
    # FT.TRIANGLE_TOP: ['1_1_1_XOM_23_2018-06-11_00:00_2018-07-26_00:00'],
    FT.TRIANGLE_BOTTOM: ['1_1_1_MRK_24_2018-02-16_00:00_2018-03-29_00:00'],
    FT.TRIANGLE_DOWN: ['1_1_1_AXP_22_2018-02-27_00:00_2018-04-05_00:00'],
    # FT.TKE_BOTTOM: [''],
    FT.FIBONACCI_DESC: ['1_1_1_KO_56_2018-01-26_00:00_2018-05-15_00:00'],
    FT.HEAD_SHOULDER_BOTTOM: ['1_1_1_JNJ_44_2018-04-16_00:00_2018-07-16_00:00'],
    FT.HEAD_SHOULDER_BOTTOM_DESC: ['1_1_1_MMM_46_2015-11-20_00:00_2016-02-24_00:00']
}

pattern_type_list_to_test = [FT.CHANNEL]

for pattern_type in pattern_type_list_to_test:
    sys_config.config.pattern_ids_to_find = pattern_type_pattern_id_dict[pattern_type]
    sys_config.config.pattern_ids_to_find = ['1_1_1_REGN_22_2018-01-11_00:00_2018-02-09_00:00']

    for trade_strategy_dict in trade_strategy_dict_list:
        sys_config.exchange_config.trade_strategy_dict = trade_strategy_dict
        pattern_controller = PatternDetectionController(sys_config)
        pattern_controller.run_pattern_detector()




