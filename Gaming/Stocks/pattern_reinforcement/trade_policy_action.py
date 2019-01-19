"""
Description: This module is the central class for the reinforcement trade policy
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-19
"""

from sertl_analytics.constants.pattern_constants import DC, FT, PRD, TPA
from sertl_analytics.models.policy_action import PolicyAction


class TradePolicyWaitAction(PolicyAction):
    def __get_name__(self):
        return TPA.WAIT


class TradePolicySellAction(PolicyAction):
    def __get_name__(self):
        return TPA.SELL


class TradePolicyLimitUpAction(PolicyAction):
    def __get_name__(self):
        return TPA.LIMIT_UP


class TradePolicyLimitDownAction(PolicyAction):
    def __get_name__(self):
        return TPA.LIMIT_DOWN


class TradePolicyStopLossUpAction(PolicyAction):
    def __get_name__(self):
        return TPA.STOP_LOSS_UP


class TradePolicyStopLossDownAction(PolicyAction):
    def __get_name__(self):
        return TPA.STOP_LOSS_DOWN

