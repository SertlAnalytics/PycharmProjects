"""
Description: This module is the central class for the reinforcement trade policy
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Observation: [horizontal_position (0=middle), velocity, angle_of_the_pole (0=vertical), angular_velocity]
Date: 2019-01-18
"""

import gym
import numpy as np
from time import sleep
from pattern_reinforcement.trade_policy_gradient import TradePolicyByPolicyGradient
import tensorflow as tf


class CartPolePolicyByPolicyGradient(TradePolicyByPolicyGradient):
    def get_action_and_gradients(self, observation, sess: tf.Session):
        action_val, gradient_val = sess.run([self._action, self._gradients],
                                            feed_dict={self._x_ph: observation.reshape(-1, 4)})
        return action_val[0][0], gradient_val

    def get_action(self, observation, sess=None):
        action, gradient_val = self.get_action_and_gradients(observation=observation, sess=sess)
        return action

    @staticmethod
    def get_action_for_basic_policy(obs):
        # result: mean=42.01, std=9.413283167949427, min=25.0, max=66.0
        angle = obs[2]
        return 0 if angle < 0 else 1


class CartPolePolicyHandlerByGradient:
    @property
    def save_path(self):
        return './polycy_pg/my_policy_net_pg.ckpt'

    def train_policy_by_gradient(self, policy: CartPolePolicyByPolicyGradient, episodes=250, save_after_episodes=50,
                                 n_games_per_update=10, discount_rate=0.95):
        env = gym.make("CartPole-v0")
        print('env.observation_space.n={}, env.action_space.n={}'.format(env.observation_space, env.action_space))
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
                    print('obs after reset: {}'.format(obs))
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
                self._trade_policy.update_policy(sess, all_rewards, all_gradients, discount_rate)
                sleep(2)
                totals.append(episode_rewards)
                print('Episode {}: reward={}'.format(episode, episode_rewards))
                # if episode % save_after_episodes == 0:
                #     self._trade_policy.saver.save(sess, self.save_path)
                rewards_total = sum([sum(current_reward) for current_reward in all_rewards])
        env.close()
        print('mean={}, std={}, min={}, max={}'.format(np.mean(totals), np.std(totals), np.min(totals), np.max(totals)))

    def train_policy_by_basic_policy(self, cart_pole_policy):
        env = gym.make("CartPole-v0")
        totals = []
        for episode in range(100):
            episode_rewards = 0
            obs = env.reset()
            for step in range(1000):
                action = cart_pole_policy.get_action_for_basic_policy(obs)
                obs, reward, done, info = env.step(action)
                episode_rewards += reward
                if done:
                    break
            env.render(mode='rgb_array')
            totals.append(episode_rewards)
        env.close()
        print('mean={}, std={}, min={}, max={}'.format(np.mean(totals), np.std(totals), np.min(totals), np.max(totals)))


cart_pole_policy = CartPolePolicyByPolicyGradient(input_layers=4, output_layers=1)
handler = CartPolePolicyHandlerByGradient()
handler.train_policy_by_basic_policy(cart_pole_policy)
handler.train_policy_by_gradient(cart_pole_policy, episodes=300)




