"""
Description: This module is the central class for the reinforcement trade policy
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-19
"""

from sertl_analytics.models.policy_action import PolicyAction
from pattern_reinforcement.trade_environment import TradeObservation
from pattern_reinforcement.trade_policy_action import TradePolicySellAction
from pattern_reinforcement.trade_policy_action import TradePolicyWaitAction, TradePolicyStopLossUpAction
import tensorflow as tf
import numpy as np


class TradePolicy:
    def __init__(self):
        self._sess = None
        self._observation = None

    @property
    def policy_name(self):
        return self.__class__.__name__

    def get_action(self, observation: TradeObservation, sess=None) -> PolicyAction:
        self._sess = sess
        self._observation = observation
        if self._observation.current_value_high_pct > self._observation.limit_pct:
            return TradePolicyStopLossUpAction(parameter=self._observation.current_value_low_pct)
        if self._observation.current_value_low_pct > 0.1 * self._observation.limit_pct:
            return TradePolicySellAction()
        if self._observation.current_value_low_pct > self._observation.stop_loss_pct:
            return TradePolicyWaitAction()
        return TradePolicySellAction()


class TradePolicyWaitTillEnd(TradePolicy):
    @property
    def policy_name(self):
        return self.__class__.__name__

    def get_action(self, observation: TradeObservation, sess=None) -> PolicyAction:
        self._observation = observation
        return TradePolicyWaitAction()


class TradePolicySellOnFirstWin(TradePolicy):
    def get_action(self, observation: TradeObservation, sess=None) -> PolicyAction:
        self._observation = observation
        if self._observation.current_value_low_pct > 0:
            return TradePolicySellAction()
        return TradePolicyWaitAction()


class TradePolicySellOnFirstLargeWin(TradePolicy):
    def __init__(self, threshold_pct: float):
        TradePolicy.__init__(self)
        self._threshold_pct = threshold_pct

    def get_action(self, observation: TradeObservation, sess=None) -> PolicyAction:
        self._observation = observation
        if self._observation.current_value_low_pct > self._threshold_pct:
            return TradePolicySellAction()
        return TradePolicyWaitAction()


class TradePolicyRollOverStopLoss(TradePolicy):
    def __init__(self, rollover_pct: float):
        TradePolicy.__init__(self)
        self._rollover_pct = rollover_pct

    def get_action(self, observation: TradeObservation, sess=None) -> PolicyAction:
        self._observation = observation
        if self._observation.current_value_low_pct > self._rollover_pct:
            if self._observation.current_value_low_pct - self._observation.stop_loss_pct > self._rollover_pct:
                return TradePolicyStopLossUpAction(parameter=self._observation.current_value_low_pct)
        return TradePolicyWaitAction()


class TradePolicySellOnLimit(TradePolicy):
    def get_action(self, observation: TradeObservation, session=None) -> PolicyAction:
        self._observation = observation
        if self._observation.current_value_high_pct >= self._observation.limit_pct:
            return TradePolicySellAction()
        return TradePolicyWaitAction()


class TradePolicySellOnForecastLimit(TradePolicy):
    def get_action(self, observation: TradeObservation, sess=None) -> PolicyAction:
        self._observation = observation
        if self._observation.current_value_high_pct >= self._observation.forecast_limit:
            return TradePolicySellAction()
        return TradePolicyWaitAction()


class TradePolicySellAfterForecastTicks(TradePolicy):
    # we sell if the price is max after the predicted ticks it would take
    def get_action(self, observation: TradeObservation, sess=None) -> PolicyAction:
        self._observation = observation
        if self._observation.current_tick_pct >= self._observation.forecast_ticks_to_positive_max_pct:
            if self._observation.current_value_high_pct >= self._observation.after_buy_max_pct:
                return TradePolicySellAction()
        return TradePolicyWaitAction()


class TradePolicySellCodedTrade(TradePolicy):
    # we sell just at the price the original trade was sold at - just for comparison reasons
    def get_action(self, observation: TradeObservation, sess=None) -> PolicyAction:
        self._observation = observation
        return TradePolicyWaitAction()


class TradePolicyFactory:
    @staticmethod
    def get_trade_policies_for_metric_calculation():
        return [TradePolicyWaitTillEnd(),
                TradePolicySellOnFirstWin(),
                TradePolicySellOnLimit(),
                TradePolicySellOnForecastLimit(),
                TradePolicySellAfterForecastTicks(),
                TradePolicySellCodedTrade()]
