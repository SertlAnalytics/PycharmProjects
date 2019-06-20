"""
Description: This module is the central class for the reinforcement trade policy
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-19
"""

from sertl_analytics.constants.pattern_constants import DC, FT, PRD, TPA
from sertl_analytics.models.policy_action import PolicyAction


class TradePolicyWaitAction(PolicyAction):
    @property
    def short(self):
        return 'W{}'.format(self.__get_parameter_info__())

    def __get_name__(self):
        return TPA.WAIT


class TradePolicySellAction(PolicyAction):
    @property
    def short(self):
        return 'S{}'.format(self.__get_parameter_info__())

    def __get_name__(self):
        return TPA.SELL


class TradePolicyLimitUpAction(PolicyAction):
    @property
    def short(self):
        return 'L_UP{}'.format(self.__get_parameter_info__())

    def __get_name__(self):
        return TPA.LIMIT_UP


class TradePolicyLimitDownAction(PolicyAction):
    @property
    def short(self):
        return 'L_DN{}'.format(self.__get_parameter_info__())

    def __get_name__(self):
        return TPA.LIMIT_DOWN


class TradePolicyStopLossUpAction(PolicyAction):
    @property
    def short(self):
        return 'S_UP{}'.format(self.__get_parameter_info__())

    def __get_name__(self):
        return TPA.STOP_LOSS_UP


class TradePolicyStopLossDownAction(PolicyAction):
    @property
    def short(self):
        return 'S_DN{}'.format(self.__get_parameter_info__())

    def __get_name__(self):
        return TPA.STOP_LOSS_DOWN

