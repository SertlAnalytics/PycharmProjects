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
from copy import deepcopy
from pattern_reinforcement.trade_observation import TradeObservation
from pattern_database.stock_access_entity import TradeEntity, TradeEntityCollection
from pattern_wave_tick import WaveTick
import random
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class EnvironmentStep:
    def __init__(self, step_number: int, action: PolicyAction):
        self.action = action
        self.reward = 0
        self.info_dict = self.action.get_info_dict()
        self.wave_tick = None
        self._number = step_number


class TradeEnvironment(EnvironmentInterface):
    def __init__(self, trade_entity_collection: TradeEntityCollection, entity: TradeEntity=None):
        self._trade_entity_collection = trade_entity_collection
        self._entity_init = entity
        self._step = None
        self._step_counter = 0
        self._step_list = []
        self._sell_limit = None
        self._stop_loss = None
        self._trailing_distance = None
        self._observation_orig = None
        self._observation_space = None
        self._observation_space_df = None
        self._observation_space_scaled_df = None
        self._observation_space_scaler = None
        self._base_observation_number = 0
        self._max_steps = 0
        self._observation_after_step = None
        self.__init_by_entity__(entity)

    def __init_by_entity__(self, trade_entity: TradeEntity):
        self._trade_entity = self.__get_entity_by_random__() if trade_entity is None else trade_entity
        self._off_set_volume = self._trade_entity.buy_volume
        self._off_set_value = self._trade_entity.buy_price
        self._off_set_date = self._trade_entity.buy_date
        self._wave_tick_for_buying = self._trade_entity.wave_tick_for_buying
        self._max_steps = self._trade_entity.max_ticks_after_breakout
        self._observation_orig = self.__get_observation_orig__()
        self._observation_space = self.__get_observation_space__()
        self._observation_space_df = self.__get_observation_space_df__()
        self._observation_space_scaler = self.__get_fitted_scaler__()
        self._observation_space_scaled_df = self.__get_observation_space_scaled_df__()
        # self.__print_observation_spaces__()
        self.__init_entity_independent_variables__()

    def __init_entity_independent_variables__(self):
        self._done = False
        self._step_list = []
        self._step_counter = 0
        self._base_observation_number = 0
        self._step = None

    def __get_fitted_scaler__(self):
        scaler = StandardScaler()
        scaler.fit(self._observation_space_df)
        return scaler

    def __get_observation_space_scaled_df__(self):
        self.__scale_observations__()
        return self.__get_observation_space_df__(scaled=True)

    def __scale_observations__(self):
        for obs in self._observation_space:
            obs.scale_value_array(self._observation_space_scaler)

    def __get_observation_orig__(self):
        observation_orig_data_dict = self._trade_entity.get_data_dict_for_agent_first_observation()
        return TradeObservation(observation_orig_data_dict, self._wave_tick_for_buying)

    @property
    def base_observation_number(self):
        return self._base_observation_number

    @property
    def actions(self):
        action_short_list = [step.action.short for step in self._step_list]
        return '{}: {}'.format(len(action_short_list), action_short_list)

    @property
    def max_steps(self):
        return self._max_steps

    @property
    def observation_space(self):  # data frame for the observations, shape[0] return the numbers of observations
        return self._observation_space

    @property
    def reward_total(self):
        return sum([step.reward for step in self._step_list])

    def reset(self) -> TradeObservation:  # initialize the environment
        if self._entity_init is None:
            self.__init_by_entity__(self.__get_entity_by_random__())
        else:
            self.__init_entity_independent_variables__()
        return self.__get_observation_by_random__()

    def reset_by_entity(self, trade_entity: TradeEntity) -> TradeObservation:  # initialize the environment
        self.__init_by_entity__(trade_entity)
        self._base_observation_number = 1
        self._step_counter = 0
        self._max_steps = len(self.observation_space) - self._base_observation_number
        return self.observation_space[0]

    def __get_entity_by_random__(self) -> TradeEntity:
        return self._trade_entity_collection.get_element_by_random()

    def render(self, mode=''):  # shows the environment
        pass

    def close(self):
        pass

    def step(self, action: PolicyAction):  # returns obs, reward, done, info
        self._step_counter += 1
        self._observation_after_step = self.__get_observation_for_step__()
        self._step = EnvironmentStep(self._step_counter, action)
        self._step.wave_tick = self._observation_after_step.wave_tick
        self._step_list.append(self._step)
        self.__adjust_observation_after_step_with_respect_to_latest_action__()
        self.__calculate_end_with_respect_to_current_step_and_action__()
        self.__calculate_reward__()
        return self._observation_after_step, self._step.reward, self._done, self._step.info_dict

    def __get_observation_by_random__(self):
        self._base_observation_number = random.randint(1, len(self.observation_space) - 1)
        self._step_counter = 0
        self._max_steps = len(self.observation_space) - self._base_observation_number
        return self.observation_space[self._base_observation_number - 1]

    def __print_observation_spaces__(self):
        scaled_array = self._observation_space_scaler.transform(self._observation_space_df)
        scaled_df = pd.DataFrame(scaled_array)
        scaled_df.columns = self._observation_space[0].columns
        print(self._observation_space_df.describe())
        print(self._observation_space_scaled_df.describe())
        scaled_df.describe()
        print(self._observation_space_df.head())
        print(self._observation_space_scaled_df.head())

    def __get_observation_space_df__(self, scaled=False):
        space_array = np.array([obs.scaled_value_array if scaled else obs.value_array for obs in self._observation_space])
        space_array = space_array.reshape(space_array.shape[0], space_array.shape[-1])
        df = pd.DataFrame(space_array)
        df.columns = self._observation_space[0].columns
        return df

    def __get_observation_space__(self) -> list:
        return_list = [self._observation_orig]
        self._step_counter = 0
        for wave_tick in self._trade_entity.wave_tick_list_after_breakout.tick_list:
            self._step_counter += 1
            obs_previous = return_list[-1]
            obs_new = deepcopy(obs_previous)
            self.__adjust_new_observation_to_wave_tick__(obs_new, wave_tick, obs_previous.wave_tick)
            return_list.append(obs_new)
        return return_list

    def __get_observation_for_step__(self):
        return deepcopy(self._observation_space[self._base_observation_number + self._step_counter - 1])

    def __adjust_observation_after_step_with_respect_to_latest_action__(self):
        if self._step.action.name == TPA.WAIT:
            pass
        elif self._step.action.name == TPA.STOP_LOSS_UP:
            self._observation_after_step.stop_loss_pct = self._step.action.parameter

    def __adjust_new_observation_to_wave_tick__(
            self, obs: TradeObservation, wave_tick: WaveTick, wave_tick_previous: WaveTick):
        obs.wave_tick = wave_tick
        obs.current_tick_pct = round(self._step_counter/self.max_steps * 100, 2)
        obs.current_value_high_pct = MyMath.get_change_in_percentage(self._off_set_value, wave_tick.high)
        obs.current_value_low_pct = MyMath.get_change_in_percentage(self._off_set_value, wave_tick.low)
        obs.current_value_open_pct = MyMath.get_change_in_percentage(self._off_set_value, wave_tick.open)
        obs.current_value_close_pct = MyMath.get_change_in_percentage(self._off_set_value, wave_tick.close)
        obs.current_volume_buy_pct = MyMath.get_change_in_percentage(self._off_set_volume, wave_tick.volume)
        obs.current_volume_last_pct = MyMath.get_change_in_percentage(wave_tick_previous.volume, wave_tick.volume)

    def __calculate_end_with_respect_to_current_step_and_action__(self):
        if self._step_counter == self._max_steps:
            self._step.info_dict['END Reason'] = 'Max steps reached'
            self._done = True
        elif self._observation_after_step.current_value_low_pct < self._observation_after_step.stop_loss_pct:
            self._step.info_dict['END Reason'] = 'Stop loss triggered'
            self._step.reward = self._observation_after_step.stop_loss_pct
            self._done = True
        elif self._step.action.name == TPA.SELL:
            self._step.info_dict['END Reason'] = 'Position sold by policy'
            self._done = True

    def __calculate_reward__(self):
        if self._done:
            self._step.reward = self._observation_after_step.current_value_open_pct
            date = self._observation_after_step.wave_tick.date
            sold_price = MyMath.get_value_from_percentage_on_base_value(self._step.reward, self._off_set_value)
            self._step.info_dict['SOLD'] = '{:.2f} ({}) - bought: {:.2f} ({})'.format(
                sold_price, date, self._off_set_value, self._off_set_date)
        else:
            self._step.reward = -0.01


