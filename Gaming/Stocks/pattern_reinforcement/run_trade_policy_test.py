"""
Description: This module is the test class for pattern reinforcement learning.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-17
"""

from sertl_analytics.constants.pattern_constants import FT, PRD
from pattern_reinforcement.trade_policy_handler import TradePolicyHandler
from pattern_reinforcement.trade_policy import TradePolicyWaitTillEnd, TradePolicySellOnFirstWin
from pattern_reinforcement.trade_policy import TradePolicySellOnLimit, TradePolicySellOnForecastLimit
from pattern_reinforcement.trade_policy import TradePolicySellAfterForecastTicks, TradePolicySellCodedTrade
from pattern_reinforcement.trade_policy import TradePolicySellOnFirstLargeWin, TradePolicyRollOverStopLoss

# pattern_id = '20_1_1_LTCUSD_10_2016-12-09_00:00_2016-12-17_00:00'
pattern_id = ''
policy_handler = TradePolicyHandler(pattern_type=FT.CHANNEL, period=PRD.DAILY, mean_aggregation=4,
                                    number_trades=20, pattern_id=pattern_id)
policy_list = [TradePolicyWaitTillEnd(),
               TradePolicySellOnFirstWin(),
               TradePolicySellOnLimit(),
               TradePolicySellOnForecastLimit(),
               TradePolicySellAfterForecastTicks()]
policy_list = [TradePolicyRollOverStopLoss(2)]
for trade_policy in policy_list:
    policy_handler.train_policy(trade_policy)


