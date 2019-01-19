"""
Description: This module is the central class for the reinforcement trade policy
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-19
"""

from sertl_analytics.constants.pattern_constants import TPA
from sertl_analytics.models.policy_action import PolicyAction
from pattern_reinforcement.trade_environment import TradeObservation
from pattern_reinforcement.trade_policy_action import TradePolicySellAction
from pattern_reinforcement.trade_policy_action import TradePolicyWaitAction, TradePolicyStopLossUpAction


class TradePolicy:
    def __init__(self):
        self._observation = None

    def get_action(self, observation: TradeObservation) -> PolicyAction:
        self._observation = observation
        if self._observation.current_value_high_pct > self._observation.limit_pct:
            return TradePolicyStopLossUpAction(parameter=self._observation.current_value_low_pct)
        if self._observation.current_value_low_pct > 0.1 * self._observation.limit_pct:
            return TradePolicySellAction()
        if self._observation.current_value_low_pct > self._observation.stop_loss_pct:
            return TradePolicyWaitAction()
        return TradePolicySellAction()


class TradePolicyWaitTillEnd(TradePolicy):
    def get_action(self, observation: TradeObservation) -> PolicyAction:
        self._observation = observation
        return TradePolicyWaitAction()


class TradePolicySellOnFirstWin(TradePolicy):
    def get_action(self, observation: TradeObservation) -> PolicyAction:
        self._observation = observation
        if self._observation.current_value_low_pct > 0:
            return TradePolicySellAction()
        return TradePolicyWaitAction()


class TradePolicySellOnLimit(TradePolicy):
    def get_action(self, observation: TradeObservation) -> PolicyAction:
        self._observation = observation
        if self._observation.current_value_high_pct >= self._observation.limit_pct:
            return TradePolicySellAction()
        return TradePolicyWaitAction()


class TradePolicySellOnForecastLimit(TradePolicy):
    def get_action(self, observation: TradeObservation) -> PolicyAction:
        self._observation = observation
        if self._observation.current_value_high_pct >= self._observation.forecast_limit:
            return TradePolicySellAction()
        return TradePolicyWaitAction()