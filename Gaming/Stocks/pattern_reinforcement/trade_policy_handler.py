"""
Description: This module is the central class for the reinforcement trade policy
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-18
"""

from sertl_analytics.constants.pattern_constants import DC, FT, PRD, TPA
from pattern_database.stock_database import StockDatabase
from pattern_database.stock_access_layer import AccessLayer4Trade
from pattern_database.stock_access_entity import TradeEntityCollection
from pattern_reinforcement.trade_environment import TradeObservation, TradeEnvironment
from pattern_reinforcement.trade_policy import TradePolicyWaitTillEnd, TradePolicySellOnFirstWin
from pattern_reinforcement.trade_policy import TradePolicySellOnLimit, TradePolicySellOnForecastLimit
import math


class TradePolicyHandler:
    def __init__(self, number_trades=math.inf):
        self._number_trades = number_trades
        self._trade_access_layer = AccessLayer4Trade(StockDatabase())
        self._trade_entity_collection = None
        self._trade_policy = TradePolicySellOnForecastLimit()

    def train_policy(self):
        self.__fill_trade_entity_collection__()
        for episode in range(500, 501):
            episode_rewards = 0
            entity_counter = 0
            entity = self._trade_entity_collection.get_first_element()
            while entity is not None:
                entity_counter += 1
                env = TradeEnvironment(entity)
                observation = env.reset()
                for step_number in range(1, env.max_steps + 1):
                    action = self._trade_policy.get_action(observation)
                    observation, reward, done, info = env.step(action)
                    if done:
                        self.__print_reward_details__(entity.pattern_id, reward, info, step_number)
                        episode_rewards += reward
                        break
                    # elif len(info) > 0:
                    #     print('\nInfo for "{}" after {} steps: {}'.format(entity.entity_key, step_number, info))
                entity = self._trade_entity_collection.get_next_element()
            print('\nEpisode_rewards ({}) for {} entities: {:.2f} (average: {:.2f}%)'.format(
                episode, entity_counter, episode_rewards, episode_rewards/entity_counter))

    def __print_reward_details__(self, pattern_id, reward: float, info: dict, step_number: int):
        policy = self._trade_policy.__class__.__name__
        print("\nReward for '{}' and '{}' after {} steps: {}%\n--> Details: {}".format(
            policy, pattern_id, step_number, reward, info)
        )

    def __fill_trade_entity_collection__(self):
        limit_clause = '' if self._number_trades == math.inf else ' LIMIT {}'.format(self._number_trades)
        query = "SELECT * FROM {} WHERE {}='{}' and {}='{}' and {}={}{}".format(
            self._trade_access_layer.table_name, DC.PERIOD, PRD.DAILY, DC.PATTERN_TYPE, FT.CHANNEL,
            DC.TRADE_MEAN_AGGREGATION, 4, limit_clause
        )
        df = self._trade_access_layer.select_data_by_query(query)
        self._trade_entity_collection = TradeEntityCollection(df)
        self._trade_entity_collection.add_wave_tick_lists()

