"""
Description: This module is the central class for the reinforcement trade policy
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-18
"""

from sertl_analytics.constants.pattern_constants import DC, FT, PRD, TPA
from pattern_database.stock_database import StockDatabase
from pattern_database.stock_access_layer import AccessLayer4Trade
from pattern_database.stock_access_entity import TradeEntityCollection, TradeEntity
from pattern_reinforcement.trade_environment import TradeEnvironment
from pattern_reinforcement.trade_policy import TradePolicy, TradePolicySellCodedTrade
import math


class TradePolicyHandler:
    def __init__(self, pattern_type=FT.CHANNEL, period=PRD.DAILY, mean_aggregation=4,
                 number_trades=math.inf, pattern_id='', compare_with_orig=True):
        self._pattern_type = pattern_type
        self._period = period
        self._mean_aggregation = mean_aggregation
        self._number_trades = number_trades
        self._pattern_id = pattern_id
        self._compare_with_orig = compare_with_orig
        self._trade_access_layer = AccessLayer4Trade(StockDatabase())
        self._trade_entity_collection = None
        self._trade_policy = None
        self.__fill_trade_entity_collection__()
        self._print_details_per_trade = False

    @property
    def save_path(self):
        return ''

    @property
    def observation_space_size(self):
        env = TradeEnvironment(self._trade_entity_collection)
        observation = env.reset()
        return observation.size

    def train_policy(self, policy: TradePolicy, episodes=1, print_details_per_trade=False):
        self._trade_policy = policy
        self._print_details_per_trade = print_details_per_trade
        episode_range = range(1, episodes+1)
        for episode in episode_range:
            episode_rewards = 0
            episode_rewards_orig = 0
            entity_counter = 0
            entity = self._trade_entity_collection.get_first_element()
            while entity is not None:
                entity_counter += 1
                episode_rewards_orig += entity.trade_result_pct
                if type(self._trade_policy) is TradePolicySellCodedTrade:
                    episode_rewards = episode_rewards_orig
                else:
                    episode_rewards = self.__get_episode_rewards__(entity, episode_rewards)
                entity = self._trade_entity_collection.get_next_element()
            self.__print_episode_details__(entity_counter, episode, episode_rewards, episode_rewards_orig)

    def run_policy(self, policy: object, print_details_per_trade=False):
        self._print_details_per_trade = print_details_per_trade
        episode_rewards = 0
        episode_rewards_orig = 0
        entity_counter = 0
        entity = self._trade_entity_collection.get_first_element()
        while entity is not None:
            entity_counter += 1
            episode_rewards_orig += entity.trade_result_pct
            if type(self._trade_policy) is TradePolicySellCodedTrade:
                episode_rewards = episode_rewards_orig
            else:
                episode_rewards = self.__get_episode_rewards__(entity, episode_rewards)
            entity = self._trade_entity_collection.get_next_element()
        self.__print_episode_details__(entity_counter, 1, episode_rewards, episode_rewards_orig)

    def __print_episode_details__(
            self, entity_counter: int, episode: int, episode_rewards: float, episode_rewards_orig: float):
        reward_policy = '{:.2f} (average: {:.2f}%)'.format(episode_rewards, episode_rewards / entity_counter)
        reward_orig_trades = '{:.2f} (average: {:.2f}%)'.format(
            episode_rewards_orig, episode_rewards_orig / entity_counter)
        print('\n{} for {}-{}: Rewards for episode {} for {} entities: {} - orig: {}'.format(
            self._trade_policy.policy_name, self._pattern_type, self._mean_aggregation,
            episode, entity_counter, reward_policy, reward_orig_trades))

    def __get_episode_rewards__(self, entity: TradeEntity, episode_rewards: float):
        env = TradeEnvironment(self._trade_entity_collection, entity)
        observation = env.reset()
        for step_number in range(1, env.max_steps + 1):
            action = self._trade_policy.get_action(observation)
            observation, reward, done, info = env.step(action)
            if done:
                if self._print_details_per_trade:
                    self.__print_reward_details__(entity.pattern_id, reward, info, step_number)
                episode_rewards += reward
                break
            # elif len(info) > 0:
            #     print('\nInfo for "{}" after {} steps: {}'.format(entity.entity_key, step_number, info))
        return episode_rewards

    def __print_reward_details__(self, pattern_id, reward: float, info: dict, step_number: int):
        print("\nReward for '{}' and '{}' after {} steps: {}%\n--> Details: {}".format(
            self._trade_policy.policy_name, pattern_id, step_number, reward, info)
        )

    def __fill_trade_entity_collection__(self):
        query = self.__get_query_for_original_trades__()
        df = self._trade_access_layer.select_data_by_query(query)
        self._trade_entity_collection = TradeEntityCollection(df)
        self._trade_entity_collection.add_wave_tick_lists()

    def __get_query_for_original_trades__(self):
        if self._pattern_id == '':
            limit_clause = '' if self._number_trades == math.inf else ' LIMIT {}'.format(self._number_trades)
        else:
            limit_clause = " and {}='{}'".format(DC.PATTERN_ID, self._pattern_id)
        return "SELECT * FROM {} WHERE {}='{}' and {}='{}' and {}={}{}".format(
            self._trade_access_layer.table_name, DC.PERIOD, self._period, DC.PATTERN_TYPE, self._pattern_type,
            DC.TRADE_MEAN_AGGREGATION, self._mean_aggregation, limit_clause
        )



