"""
Description: This module is the base class for our dash - deferred classes required.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Original, i.e. copied from: https://github.com/scottjbarr/bitfinex/blob/develop/bitfinex/client.py
Date: 2018-06-17
"""

from sertl_analytics.models.models_abc import EnvironmentInterface
from sertl_analytics.models.policy_action import PolicyAction
from sertl_analytics.mymath import MyMath
from sertl_analytics.constants.pattern_constants import TPA
import pandas as pd
from copy import deepcopy
from pattern_reinforcement.trade_observation import TradeObservation
from pattern_database.stock_access_entity import TradeEntity


class EnvironmentStep:
    def __init__(self, step_number: int, action: PolicyAction):
        self.action = action
        self.reward = 0
        self.info_dict = self.action.get_info_dict()
        self.wave_tick = None
        self._number = step_number


class TradeEnvironment(EnvironmentInterface):
    def __init__(self, trade_entity: TradeEntity):
        self._done = False
        self._trade_entity = trade_entity
        self._off_set_value = self._trade_entity.buy_price
        self._off_set_date = self._trade_entity.buy_date
        self._observation_orig_data_dict = self._trade_entity.get_data_dict_for_agent_first_observation()
        self._max_steps = self._trade_entity.wave_tick_list_after_breakout.df.shape[0]
        self._observation_orig = TradeObservation(self._observation_orig_data_dict)
        self._observation_space = [self._observation_orig]
        self._step_list = []
        self._step_counter = 0
        self._step = None

    @property
    def max_steps(self):
        return self._max_steps

    @property
    def observation_space(self):  # data frame for the observations, shape[0] return the numbers of observations
        return self._observation_space

    @property
    def observation_orig(self):
        return self._observation_space[0]

    @property
    def observation_last(self):
        return self._observation_space[-1]

    @property
    def reward_total(self):
        return sum([step.reward for step in self._step_list])

    def reset(self) -> TradeObservation:  # initialize the environment
        self._step_counter = 0
        self._observation_space = [self._observation_orig]
        return self._observation_orig

    def render(self, mode=''):  # shows the environment
        pass

    def step(self, action: PolicyAction):  # returns obs, reward, done, info
        self._step_counter += 1
        self._step = EnvironmentStep(self._step_counter, action)
        self._step_list.append(self._step)
        self.__add_observation_with_respect_to_latest_action__()
        self.__adjust_new_wave_tick_to_observation__()
        self.__calculate_end_with_respect_to_new_wave_tick__()
        self.__calculate_reward__()
        return self._observation_space[-1], self._step.reward, self._done, self._step.info_dict

    def __add_observation_with_respect_to_latest_action__(self):
        obs_new = deepcopy(self.observation_last)
        if self._step.action.name == TPA.WAIT:
            pass
        elif self._step.action.name == TPA.STOP_LOSS_UP:
            obs_new.stop_loss_pct = self._step.action.parameter
        self.observation_space.append(obs_new)

    def __adjust_new_wave_tick_to_observation__(self):
        self._step.wave_tick = self._trade_entity.get_wave_tick_for_step(self._step_counter)
        obs_new = self.observation_last
        obs_new.current_value_high_pct = MyMath.get_change_in_percentage(self._off_set_value, self._step.wave_tick.high)
        obs_new.current_value_low_pct = MyMath.get_change_in_percentage(self._off_set_value, self._step.wave_tick.low)
        obs_new.current_value_open_pct = MyMath.get_change_in_percentage(self._off_set_value, self._step.wave_tick.open)
        obs_new.current_value_close_pct = MyMath.get_change_in_percentage(self._off_set_value, self._step.wave_tick.close)

    def __calculate_reward__(self):
        if self._done:
            self._step.reward = self.observation_last.current_value_open_pct
            sold_price = MyMath.get_value_from_percentage_on_base_value(self._step.reward, self._off_set_value)
            self._step.info_dict['SOLD'] = '{:.2f} ({}) - bought: {:.2f} ({})'.format(
                sold_price, self._step.wave_tick.date, self._off_set_value, self._off_set_date)
        else:
            self._step.reward = 0

    def __calculate_end_with_respect_to_new_wave_tick__(self):
        if self._step_counter == self._max_steps:
            self._step.info_dict['END Reason'] = 'Max steps reached'
            self._done = True
        elif self.observation_last.current_value_low_pct < self.observation_last.stop_loss_pct:
            self._step.info_dict['END Reason'] = 'Stop loss triggered'
            self._done = True
        elif self._step.action.name == TPA.SELL:
            self._step.info_dict['END Reason'] = 'Position sold by policy'
            self._done = True


