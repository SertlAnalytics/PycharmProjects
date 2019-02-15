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
    """
    This environment can be fed by a trade entity collection or by a single entity (for policy checks).
    """
    def __init__(self, trade_entity_collection: TradeEntityCollection=None, entity: TradeEntity=None):
        self._trade_entity_collection = trade_entity_collection
        self._trade_entity = entity
        self._step_counter = 0
        self._step_list = []
        self._observation_space = self.__get_observation_space__()
        self._observation_space_df = None
        self._observation_space_scaled_df = None
        self._observation_space_scaler = None
        self._base_observation_number = 0
        if self._trade_entity_collection is not None:
            self.__init_observation_space_scaler__()
            self.__scale_observations__()
        self.__init_entity_independent_variables__()

    @property
    def off_set_volume(self):
        return self._trade_entity.buy_volume

    @property
    def off_set_value(self):
        return self._trade_entity.buy_price

    @property
    def off_set_date(self):
        return self._trade_entity.buy_date

    @property
    def wave_tick_for_buying(self):
        return self._trade_entity.wave_tick_for_buying

    @property
    def max_steps(self):
        return len(self._observation_space) - self._base_observation_number

    def __init_observation_space_scaler__(self):
        self._observation_space_df = self.__get_observation_space_df__()
        self._observation_space_scaler = self.__get_fitted_scaler__()
        self._observation_space_scaled_df = self.__get_observation_space_scaled_df__()
        # self.__print_observation_spaces__()

    def __init_entity_independent_variables__(self):
        self._step_list = []
        self._step_counter = 0
        self._base_observation_number = 0

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

    @property
    def entity(self):
        return self._trade_entity

    @property
    def base_observation_number(self):
        return self._base_observation_number

    @property
    def actions(self):
        action_short_list = [step.action.short for step in self._step_list]
        return '{}: {}'.format(len(action_short_list), action_short_list)

    @property
    def observation_space(self):  # data frame for the observations, shape[0] return the numbers of observations
        return self._observation_space

    @property
    def reward_total(self):
        return sum([step.reward for step in self._step_list])

    def reset(self) -> TradeObservation:  # initialize the environment
        self.__init_entity_independent_variables__()
        if self._trade_entity_collection is not None:
            self._trade_entity = self._trade_entity_collection.get_element_by_random()
            self._observation_space = self.__get_observation_space_by_entity__(self._trade_entity)
        self.__init_entity_independent_variables__()
        return self.__get_observation_by_random__()

    def reset_by_entity(self, trade_entity: TradeEntity) -> TradeObservation:  # initialize the environment
        self.__init_entity_independent_variables__()
        self._trade_entity = trade_entity
        self._observation_space = self.__get_observation_space_by_entity__(self._trade_entity)
        self._base_observation_number = 1
        return self._observation_space[0]

    def reset_to_start(self) -> TradeObservation:  # initialize the environment
        self._base_observation_number = 1
        return self._observation_space[0]

    def render(self, mode=''):  # shows the environment
        pass

    def close(self):
        pass

    def step(self, action: PolicyAction):  # returns obs, reward, done, info
        self._step_counter += 1
        observation_after_step = self.__get_observation_for_step__()
        step = EnvironmentStep(self._step_counter, action)
        step.wave_tick = observation_after_step.wave_tick
        self._step_list.append(step)
        self.__adjust_observation_after_step_by_latest_action__(observation_after_step, step)
        done = self.__get_done_with_respect_to_current_step_and_action__(observation_after_step, step)
        self.__calculate_reward__(done, observation_after_step, step)
        return observation_after_step, step.reward, done, step.info_dict

    def __get_observation_by_random__(self):
        self._base_observation_number = random.randint(1, len(self.observation_space) - 1)
        return self._observation_space[self._base_observation_number - 1]

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
        if self._trade_entity is None:
            return self.__get_observation_space_by_entity_collection__()
        else:
            return self.__get_observation_space_by_entity__(self._trade_entity)

    def __get_observation_space_by_entity_collection__(self):
        return_list = []
        for trade_entity in self._trade_entity_collection.entity_number_dict.values():
            return_list = return_list + self.__get_observation_space_by_entity__(trade_entity)
        return return_list

    def __get_observation_space_by_entity__(self, trade_entity: TradeEntity) -> list:
        return_list = [self.__get_first_observation_for_trade_entity__(trade_entity)]
        len_list = len(trade_entity.wave_tick_list_after_breakout.tick_list)
        for index, wave_tick in enumerate(trade_entity.wave_tick_list_after_breakout.tick_list):
            obs_previous = return_list[-1]
            obs_new = self.__get_first_observation_for_trade_entity__(trade_entity)
            obs_new.current_tick_pct = round((index + 1)/len_list * 100, 2)
            self.__adjust_observation_to_wave_tick__(obs_new, wave_tick, obs_previous.wave_tick)
            return_list.append(obs_new)
        return return_list

    @staticmethod
    def __get_first_observation_for_trade_entity__(trade_entity: TradeEntity):
        observation_start_data_dict = trade_entity.get_data_dict_for_agent_first_observation()
        return TradeObservation(observation_start_data_dict, trade_entity.wave_tick_for_buying)

    def __get_observation_for_step__(self):
        return self._observation_space[self._base_observation_number + self._step_counter - 1]

    @staticmethod
    def __adjust_observation_after_step_by_latest_action__(obs: TradeObservation, step: EnvironmentStep):
        if step.action.name == TPA.STOP_LOSS_UP:
            obs.stop_loss_pct = step.action.parameter

    def __adjust_observation_to_wave_tick__(
            self, obs: TradeObservation, wave_tick: WaveTick, wave_tick_previous: WaveTick):
        obs.wave_tick = wave_tick
        obs.current_value_high_pct = MyMath.get_change_in_percentage(self.off_set_value, wave_tick.high)
        obs.current_value_low_pct = MyMath.get_change_in_percentage(self.off_set_value, wave_tick.low)
        obs.current_value_open_pct = MyMath.get_change_in_percentage(self.off_set_value, wave_tick.open)
        obs.current_value_close_pct = MyMath.get_change_in_percentage(self.off_set_value, wave_tick.close)
        obs.current_volume_buy_pct = MyMath.get_change_in_percentage(self.off_set_volume, wave_tick.volume)
        obs.current_volume_last_pct = MyMath.get_change_in_percentage(wave_tick_previous.volume, wave_tick.volume)

    def __get_done_with_respect_to_current_step_and_action__(self, obs: TradeObservation, step: EnvironmentStep):
        if self._step_counter == self.max_steps:
            step.info_dict['END Reason'] = 'Max steps reached'
            return True
        elif obs.current_value_low_pct < obs.stop_loss_pct:
            step.info_dict['END Reason'] = 'Stop loss triggered'
            step.reward = obs.stop_loss_pct
            return True
        elif step.action.name == TPA.SELL:
            step.info_dict['END Reason'] = 'Position sold by policy'
            return True
        return False

    def __calculate_reward__(self, done: bool, obs: TradeObservation, step: EnvironmentStep):
        if done:
            step.reward = obs.current_value_open_pct
            date = obs.wave_tick.date
            sold_price = MyMath.get_value_from_percentage_on_base_value(step.reward, self.off_set_value)
            step.info_dict['SOLD'] = '{:.2f} ({}) - bought: {:.2f} ({})'.format(
                sold_price, date, self.off_set_value, self.off_set_date)
        else:
            step.reward = -0.01


