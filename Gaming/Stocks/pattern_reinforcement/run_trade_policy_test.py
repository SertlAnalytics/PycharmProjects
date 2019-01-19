"""
Description: This module is the test class for pattern reinforcement learning.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-17
"""

from pattern_reinforcement.trade_policy_handler import TradePolicyHandler

policy_handler = TradePolicyHandler(number_trades=50)
policy_handler.train_policy()


