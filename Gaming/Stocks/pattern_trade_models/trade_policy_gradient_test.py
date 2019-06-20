"""
Description: This module is the test class for trade policy gradient (test driven development)
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-26
"""

from sertl_analytics.constants.pattern_constants import FT, PRD
from pattern_trade_models.trade_policy_handler import TradePolicyHandler
from pattern_trade_models.trade_policy_gradient import TradePolicyByPolicyGradient
from pattern_trade_models.trade_policy_handler_gradient import TradePolicyHandlerByGradient
from pattern_trade_models.trade_policy import TradePolicyWaitTillEnd, TradePolicySellOnFirstWin, TradePolicy
from pattern_trade_models.trade_policy import TradePolicySellOnLimit, TradePolicySellOnForecastLimit
from pattern_trade_models.trade_policy import TradePolicySellAfterForecastTicks, TradePolicySellCodedTrade
from pattern_trade_models.trade_policy import TradePolicySellOnFirstLargeWin, TradePolicyRollOverStopLoss
import numpy as np


class TradePolicyByPolicyGradientTest:
    def __init__(self, pattern_id=''):
        self._pattern_id = '20_1_1_LTCUSD_10_2016-12-09_00:00_2016-12-17_00:00'
        self._pattern_id = pattern_id
        self._policy_handler = TradePolicyHandler(pattern_type=FT.CHANNEL, period=PRD.DAILY, mean_aggregation=4,
                                                  number_trades=20, pattern_id=self._pattern_id)
        self._policy_gradient_handler = TradePolicyHandlerByGradient(pattern_type=FT.CHANNEL, period=PRD.DAILY,
                                                                     mean_aggregation=4, number_trades=200,
                                                                     pattern_id=self._pattern_id)
        self._observation_space_size = self._policy_gradient_handler.observation_space_size
        self._policy = TradePolicyByPolicyGradient(self._observation_space_size, 1)

    def train_trade_policy(self, trade_policy: TradePolicy, episods=1):
        self._policy_handler.train_policy(trade_policy, episods)

    def train_gradient_policy(self, episodes: int):
        self._policy_gradient_handler.train_policy_by_gradient(self._policy, episodes=episodes)

    def run_trained_trade_policy(self, print_details_per_trade=False):
        self._policy_handler.run_policy(self._policy, print_details_per_trade=print_details_per_trade)

    def run_trained_gradient_trade_policy(self, print_details_per_trade=False):
        self._policy_gradient_handler.run_policy(self._policy, print_details_per_trade=print_details_per_trade)

    def run_discount_rewards_test(self):
        discount_rewards = self._policy.discount_rewards([10, 0, -50], discount_rate=0.8)
        expected_rewards = np.array([-22., -40., -50.])
        print('Expected: {}: result={}: {}'.format(
            expected_rewards, discount_rewards, np.array_equal(discount_rewards, expected_rewards)))

        discount_rewards = self._policy.discount_and_normalize_rewards([[10, 0, -50], [10, 20]], discount_rate=0.8)
        expected_rewards = [np.array([-0.28435071, -0.86597718, -1.18910299]), np.array([1.26665318, 1.0727777])]

        print('Expected: {}: \nresult={}: {} and {}'.format(
            expected_rewards, discount_rewards,
            np.array_equal(np.round(expected_rewards[0], 8), np.round(discount_rewards[0], 8)),
            np.array_equal(np.round(expected_rewards[1], 8), np.round(discount_rewards[1], 8))
        ))