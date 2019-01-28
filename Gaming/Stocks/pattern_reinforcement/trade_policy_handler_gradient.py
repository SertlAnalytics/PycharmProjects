"""
Description: This module is the central class for the reinforcement trade policy
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-18
"""

from pattern_database.stock_access_entity import TradeEntity
from pattern_reinforcement.trade_environment import TradeEnvironment
from pattern_reinforcement.trade_policy_handler import TradePolicyHandler
from pattern_reinforcement.trade_policy_gradient import TradePolicyByPolicyGradient
import tensorflow as tf
import numpy as np


class TradePolicyHandlerByGradient(TradePolicyHandler):
    @property
    def save_path(self):
        return './polycy_pg/my_policy_net_pg.ckpt'

    def train_policy_by_gradient(self, policy: TradePolicyByPolicyGradient, episodes=250, save_after_episodes=50,
                                 n_games_per_update=20, discount_rate=0.95):
        env = TradeEnvironment(self._trade_entity_collection)
        episode_rewards_orig = self._trade_entity_collection.collection_trade_result_pct
        self._trade_policy = policy
        self._trade_policy.init_execution_phase()
        with tf.Session() as sess:
            self._trade_policy.initializer.run()
            for episode in range(episodes):
                all_rewards = []  # all sequences of row rewards for each episode
                all_gradients = []  # gradients saved at each step of each episode
                for games in range(n_games_per_update):
                    current_rewards = []  # all row rewards from the current episode
                    current_gradients = []  # all gradients from the current episode
                    obs = env.reset()
                    # print('obs.value: {}'.format(obs.value_array))
                    for step_number in range(1, env.max_steps + 1):
                        action, gradient_val = self._trade_policy.get_action_and_gradients(obs, sess)
                        obs, reward, done, info = env.step(action)
                        current_rewards.append(reward)
                        current_gradients.append(gradient_val)
                        if done:
                            break
                    all_rewards.append(current_rewards)
                    all_gradients.append(current_gradients)
                # at this point we have run the policy for 10 episodes, and we are
                # ready for a policy update using the algorithm described earlier
                self._trade_policy.update_policy(sess, all_rewards, all_gradients, discount_rate)
                if episode % save_after_episodes == 0:
                    self._trade_policy.saver.save(sess, self.save_path)
                rewards_total = sum([sum(current_reward) for current_reward in all_rewards])
                self.__print_episode_details__(
                    self._trade_entity_collection.elements, episode, rewards_total, episode_rewards_orig)

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

    def run_policy(self, print_details_per_trade=False):
        env = TradeEnvironment(self._trade_entity_collection)
        episode_rewards_orig = self._trade_entity_collection.collection_trade_result_pct
        with tf.Session() as sess:
            self._trade_policy.saver.restore(sess=sess, save_path=self.save_path)
            all_rewards = []
            entity = self._trade_entity_collection.get_first_element()
            while entity is not None:
                env.init_by_entity(entity)
                current_rewards = []  # all row rewards from the current episode
                obs = env.reset()
                for step_number in range(1, env.max_steps + 1):
                    action = self._trade_policy.get_action(obs, sess)
                    obs, reward, done, info = env.step(action)
                    current_rewards.append(reward)
                    if done:
                        break
                all_rewards.append(current_rewards)
                print('Reward for {}: {:.2f}%, orig={:.2f}%'.format(
                    entity.pattern_id, sum(current_rewards), entity.trade_result_pct))
                entity = self._trade_entity_collection.get_next_element()
            rewards_total = sum([sum(current_reward) for current_reward in all_rewards])
            self.__print_episode_details__(
                self._trade_entity_collection.elements, 1, rewards_total, episode_rewards_orig)

    def __get_episode_rewards__(self, entity: TradeEntity, episode_rewards: float):
        env = TradeEnvironment(self._trade_entity_collection, entity)
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
        return episode_rewards




