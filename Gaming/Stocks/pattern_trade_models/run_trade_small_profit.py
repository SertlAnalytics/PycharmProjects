"""
Description: This module is the test class for trade small profit test
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-06-20
"""

from pattern_system_configuration import SystemConfiguration
from pattern_trade_models.trade_small_profit import TradeSmallProfit
from sertl_analytics.constants.pattern_constants import FT

sys_config = SystemConfiguration()
small_profit = TradeSmallProfit()
pattern_types = small_profit.pattern_types
pattern_types.append(FT.ALL)
for pattern_type in pattern_types:
    print('...{:22}: mean_trade_reached_price={:.2f}%, mean_result={:.2f}%, '
          'std_reached_price={:.2f}%, small_profit={:.2f}%'.format(
        pattern_type,
        small_profit.get_mean_trade_reached_price_pct_for_pattern_type(pattern_type),
        small_profit.get_mean_trade_result_pct_for_pattern_type(pattern_type),
        small_profit.get_std_trade_reached_price_pct_for_pattern_type(pattern_type),
        small_profit.get_suggested_small_profit_pct_for_pattern_type(pattern_type)
    ))

print('sys_config.exchange_config.small_profit_parameter_dict={}'.format(
    sys_config.exchange_config.small_profit_parameter_dict))


