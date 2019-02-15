"""
Description: This module is the central class for the reinforcement trade policy
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-18
"""

from sertl_analytics.constants.pattern_constants import FT, PRD
from pattern_database.stock_access_entity import TradeEntity
from pattern_reinforcement.trade_environment import TradeEnvironment
from pattern_reinforcement.trade_policy_handler import TradePolicyHandler
from pattern_reinforcement.trade_policy_gradient import TradePolicyByPolicyGradient
import tensorflow as tf
import numpy as np
import math


class TradePolicyHandlerByGradient(TradePolicyHandler):
    def __init__(self, pattern_type=FT.CHANNEL, period=PRD.DAILY, mean_aggregation=4,
                 number_trades=math.inf, pattern_id='', compare_with_orig=True):
        TradePolicyHandler.__init__(
            self, pattern_type, period, mean_aggregation, number_trades, pattern_id, compare_with_orig)
        self._env = self.__get_environment__()

    @property
    def save_path(self):
        return './policy_pg/my_policy_net_pg.ckpt'

    @property
    def observation_space_size(self):
        observation = self._env.reset()
        return observation.size

    def train_policy_by_gradient(self, policy: TradePolicyByPolicyGradient, episodes: int, save_after_episodes=50,
                                 n_games_per_update=20, discount_rate=0.95):
        # n_games_per_update = self._trade_entity_collection.elements
        episode_rewards_orig = self._trade_entity_collection.collection_trade_result_pct
        episode_rewards_max = 0
        self._trade_policy = policy
        self._trade_policy.init_execution_phase()
        with tf.Session() as sess:
            self._trade_policy.saver.restore(sess=sess, save_path=self.save_path)
            # self._trade_policy.initializer.run()
            for episode in range(episodes):
                all_rewards = []  # all sequences of row rewards for each episode
                all_gradients = []  # gradients saved at each step of each episode
                for games in range(n_games_per_update):
                    current_rewards = []  # all row rewards from the current episode
                    current_gradients = []  # all gradients from the current episode
                    obs = self._env.reset()
                    entity = self._env.entity
                    base_obs_date = obs.wave_tick.date
                    # print('obs.value: {}'.format(obs.value_array))
                    for step_number in range(1, self._env.max_steps + 1):
                        action, gradient_val = self._trade_policy.get_action_and_gradients(obs, sess)
                        # if episode < episodes/2:
                        #     action = self._trade_policy.get_random_action()
                        obs, reward, done, info = self._env.step(action)
                        current_rewards.append(reward)
                        current_gradients.append(gradient_val)
                        if done:
                            break
                    all_rewards.append(current_rewards)
                    all_gradients.append(current_gradients)
                    if games == 0:
                        print('{}-{} (start: {} {}): Reward for {}: {:.2f}%, orig={:.2f}% (actions: {})'.format(
                            episode, games, self._env.base_observation_number, base_obs_date, entity.pattern_id,
                            sum(current_rewards), entity.trade_result_pct, self._env.actions))
                rewards_total = sum([sum(current_reward) for current_reward in all_rewards])

                #
                # self.__print_episode_details__(
                #     self._trade_entity_collection.elements, episode, rewards_total, episode_rewards_orig)

                if rewards_total > episode_rewards_max:
                    episode_rewards_max = rewards_total
                    self._trade_policy.saver.save(sess, self.save_path)
                # else:
                #     print(episode)
                # at this point we have run the policy for 10 episodes, and we are
                # ready for a policy update using the algorithm described earlier
                self._trade_policy.update_policy(sess, all_rewards, all_gradients, discount_rate)

    def train_policy_by_gradient_v2(self, policy: TradePolicyByPolicyGradient, episodes=250, save_after_episodes=50,
                                     n_games_per_update=20, discount_rate=0.95):
        entity = self._trade_entity_collection.get_first_element()
        env = TradeEnvironment(entity)
        self._trade_policy = policy
        self._trade_policy.init_execution_phase()
        with tf.Session() as sess:
            self._trade_policy.saver.restore(sess=sess, save_path=self.save_path)
            # self._trade_policy.initializer.run()
            totals = []
            for episode in range(episodes):
                episode_rewards = 0
                all_rewards = []  # all sequences of row rewards for each episode
                all_gradients = []  # gradients saved at each step of each episode
                for games in range(n_games_per_update):
                    current_rewards = []  # all row rewards from the current episode
                    current_gradients = []  # all gradients from the current episode
                    obs = env.reset()
                    for step_number in range(1000):
                        action, gradient_val = self._trade_policy.get_action_and_gradients(obs, sess)
                        obs, reward, done, info = env.step(action)
                        episode_rewards += reward
                        current_rewards.append(reward)
                        current_gradients.append(gradient_val)
                        env.render(mode='rgb_array')
                        if done:
                            break
                    all_rewards.append(current_rewards)
                    all_gradients.append(current_gradients)
                # at this point we have run the policy for 10 episodes, and we are
                # ready for a policy update using the algorithm described earlier
                print('Episode {}: reward={:.2f}%, orig={:.2f}%'.format(episode, episode_rewards,
                                                                        entity.trade_result_pct))
                self._trade_policy.update_policy(sess, all_rewards, all_gradients, discount_rate)
                totals.append(episode_rewards)
                # if episode % save_after_episodes == 0:
                #     self._trade_policy.saver.save(sess, self.save_path)
                rewards_total = sum([sum(current_reward) for current_reward in all_rewards])
            self._trade_policy.saver.save(sess, self.save_path)
        env.close()
        print('mean={}, std={}, min={}, max={}'.format(np.mean(totals), np.std(totals), np.min(totals), np.max(totals)))

    def run_policy(self, policy: TradePolicyByPolicyGradient, print_details_per_trade=False):
        episode_rewards_orig = self._trade_entity_collection.collection_trade_result_pct
        self._trade_policy = policy
        self._trade_policy.init_saver()
        with tf.Session() as sess:
            self._trade_policy.saver.restore(sess=sess, save_path=self.save_path)
            all_rewards = []
            for entity in self._trade_entity_collection.entity_number_dict.values():
                if entity.pattern_id == '1_1_1_AMAT_10_2017-11-01_00:00_2017-11-13_00:00':
                    current_rewards = []  # all row rewards from the current episode
                    obs = self._env.reset_by_entity(entity)
                    print('_env.base_observation_number={}, _env.max_steps={}, entity.max_ticks_after_breakout={}'.format(
                        self._env.base_observation_number, self._env.max_steps, entity.max_ticks_after_breakout))
                    for step_number in range(1, self._env.max_steps + 1):
                        action = self._trade_policy.get_action(obs, sess)
                        obs, reward, done, info = self._env.step(action)
                        current_rewards.append(reward)
                        if done:
                            break
                    all_rewards.append(current_rewards)
                    print('Reward for {}: {:.2f}%, orig={:.2f}% (actions: {})'.format(
                        entity.pattern_id, sum(current_rewards), entity.trade_result_pct, self._env.actions))
            rewards_total = sum([sum(current_reward) for current_reward in all_rewards])
            self.__print_episode_details__(
                self._trade_entity_collection.elements, 1, rewards_total, episode_rewards_orig)

    def __get_environment__(self) -> TradeEnvironment:
        return TradeEnvironment(self._trade_entity_collection)

    def __get_episode_rewards__(self, entity: TradeEntity):
        env = TradeEnvironment(self._trade_entity_collection, entity)
        observation = env.reset()
        for step_number in range(1, env.max_steps + 1):
            action = self._trade_policy.get_action(observation)
            observation, reward, done, info = env.step(action)
            if done:
                self.__print_reward_details__(entity.pattern_id, reward, info, step_number)
                return reward
            # elif len(info) > 0:
            #     print('\nInfo for "{}" after {} steps: {}'.format(entity.entity_key, step_number, info))
        return 0




