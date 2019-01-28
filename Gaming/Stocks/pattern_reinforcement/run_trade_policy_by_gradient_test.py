"""
Description: This module is the test class for pattern reinforcement learning.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-17
"""

from pattern_reinforcement.trade_policy_gradient_test import TradePolicyByPolicyGradientTest
from pattern_reinforcement.trade_policy import TradePolicyWaitTillEnd, TradePolicySellOnFirstWin
from pattern_reinforcement.trade_policy import TradePolicySellOnLimit, TradePolicySellOnForecastLimit
from pattern_reinforcement.trade_policy import TradePolicySellAfterForecastTicks, TradePolicySellCodedTrade
from pattern_reinforcement.trade_policy import TradePolicySellOnFirstLargeWin, TradePolicyRollOverStopLoss

test = TradePolicyByPolicyGradientTest()
# test.run_discount_rewards_test()
# test.train_trade_policy(TradePolicyWaitTillEnd(), 2)
test.train_gradient_policy(episodes=100)
test.run_trained_gradient_trade_policy(False)



