"""
Description: This module is the central class for the reinforcement trade policy
Author: Josef Sertl
Copyright: Aurelien Geron (Hands-On Machine learing with Scikit-Learn & Tensorflow)
Date: 2019-01-19
"""

from sertl_analytics.models.policy_action import PolicyAction
from pattern_reinforcement.trade_environment import TradeObservation
from pattern_reinforcement.trade_policy_action import TradePolicySellAction
from pattern_reinforcement.trade_policy import TradePolicy
from pattern_reinforcement.trade_policy_action import TradePolicyWaitAction, TradePolicyStopLossUpAction
import tensorflow as tf
import numpy as np
import random


class TradePolicyByPolicyGradient(TradePolicy):
    def __init__(self, input_layers: int, output_layers: int):
        TradePolicy.__init__(self)
        self._n_inputs = input_layers
        self._n_hidden = self._n_inputs
        self._n_outputs = output_layers
        self._initializer = None
        self._x_ph = None
        self._saver = None
        self._action = None
        self._grads_and_vars = None
        self._optimizer = None
        self._gradients = None
        self._gradient_placeholders = []
        self._training_optimizer = None
        self.__initialize_neural_network___()

    @property
    def initializer(self):
        return self._initializer

    @property
    def saver(self):
        return self._saver

    def __initialize_neural_network___(self):
        # 1 Specify the neural network architecture
        initializer = tf.contrib.layers.variance_scaling_initializer()
        # 2. Build the neural network
        self._x_ph = tf.placeholder(tf.float32, shape=[None, self._n_inputs])
        hidden = tf.layers.dense(self._x_ph, self._n_hidden, activation=tf.nn.elu, kernel_initializer=initializer)
        logits = tf.layers.dense(hidden, self._n_outputs, kernel_initializer=initializer)
        outputs = tf.nn.sigmoid(logits)
        # outputs = tf.nn.relu(logits)
        # 3. Select a random action based on the estimated probabilities
        p_left_and_right = tf.concat(axis=1, values=[outputs, 1-outputs])
        self._action = tf.multinomial(tf.log(p_left_and_right), num_samples=1)
        # 4. Target probability
        y = 1. - tf.to_float(self._action)
        # 5. Cost function
        learning_rate = 0.01
        cross_entropy = tf.nn.sigmoid_cross_entropy_with_logits(labels=y, logits=logits)
        self._optimizer = tf.train.AdamOptimizer(learning_rate)
        self._grads_and_vars = self._optimizer.compute_gradients(cross_entropy)
        # let's put them into a list for better access
        self._gradients = [grad for grad, variable in self._grads_and_vars]

    def init_execution_phase(self):
        """
        Okay, now comes the tricky part. During the execution phase, the algorithm will run the policy and
        at each step it will evaluate these gradient tensors and store there values. After a number of episodes
        it will tweak these gradients as explained earlier (i.e., multiply them by the action scores and normalize them)
        and compute the mean of the tweaked gradients.
        Next it will need to feed the resulting gradients back to the optimizer so that i can perform an optimization step.
        This means we need one placeholder per gradient vector. Moreover, we must create the operation that will apply
        the updated gradients. For this we will call the optimizer's apply_gradients() function, which takes a list of
        gradient vector/variable pairs.
        Instead of giving it the original gradient vertors, we will give it a list conaeining the updated gradients
        (i.e. the ones fed through the gradient placeholders)
        :return:
        """
        grads_and_vars_feed = []
        for grad, variable in self._grads_and_vars:
            gradient_placeholder = tf.placeholder(tf.float32, shape=grad.get_shape())
            self._gradient_placeholders.append(gradient_placeholder)
            grads_and_vars_feed.append((gradient_placeholder, variable))
        self._training_optimizer = self._optimizer.apply_gradients(grads_and_vars_feed)
        self._initializer = tf.global_variables_initializer()
        self._saver = tf.train.Saver()

    def init_saver(self):
        if self._saver is None:
            self._saver = tf.train.Saver()

        """
        On to the execution phase. We will need a couple of functions to compute the total discounted rewards, 
        given the row rewards and to normalize the results across multiple episodes
        """

    @staticmethod
    def discount_rewards(rewards, discount_rate):
        discounted_rewards = np.empty(len(rewards))
        cumulative_rewards = 0
        for step in reversed(range(len(rewards))):
            cumulative_rewards = rewards[step] + cumulative_rewards * discount_rate
            discounted_rewards[step] = cumulative_rewards
        return discounted_rewards

    def discount_and_normalize_rewards(self, all_rewards, discount_rate):
        all_discounted_rewards = [self.discount_rewards(rewards, discount_rate) for rewards in all_rewards]
        flat_rewards = np.concatenate(all_discounted_rewards)
        reward_mean = flat_rewards.mean()
        reward_std = flat_rewards.std()
        if reward_std == 0:
            return [0 for discounted_rewards in all_discounted_rewards]
        return [(discounted_rewards - reward_mean)/reward_std for discounted_rewards in all_discounted_rewards]

    def update_policy(self, sess: tf.Session, all_rewards: list, all_gradients: list, discount_rate: float):
        all_rewards = self.discount_and_normalize_rewards(all_rewards, discount_rate)
        feed_dict = {}
        for var_index, grad_placeholder in enumerate(self._gradient_placeholders):
            # multiply the gradients by the action scores, and compute the mean
            mean_gradients = np.mean(
                [reward * all_gradients[game_index][step][var_index]
                 for game_index, rewards in enumerate(all_rewards)
                 for step, reward in enumerate(rewards)],
                axis=0)
            feed_dict[grad_placeholder] = mean_gradients
            # print('update_policy: mean_gradients={}'.format(mean_gradients))
        sess.run(self._training_optimizer, feed_dict=feed_dict)

    # we sell just at the price the original trade was sold at - just for comparison reasons
    def get_action_and_gradients(self, observation: TradeObservation, sess: tf.Session):
        action_val, gradient_val = sess.run([self._action, self._gradients],
                                            feed_dict={self._x_ph: observation.scaled_value_array})
        action = self.__get_action_from_action_values__(action_val, observation)
        return action, gradient_val

    def get_action(self, observation: TradeObservation, sess=None) -> PolicyAction:
        action, gradient_val = self.get_action_and_gradients(observation=observation, sess=sess)
        return action

    @staticmethod
    def get_random_action():
        random_int = random.randint(0, 1)
        return TradePolicyWaitAction() if random_int == 0 else TradePolicySellAction()

    @staticmethod
    def __get_action_from_action_values__(action_val: list, obs: TradeObservation):
        stop_loss_pct_new = obs.stop_loss_pct + 1
        sell_action_active = True
        # print('action_val[0][0]={}'.format(action_val[0][0]))
        if sell_action_active:
            return TradePolicyWaitAction() if action_val[0][0] == 1 else TradePolicySellAction()
        else:
            return TradePolicyWaitAction() if action_val[0][0] == 0 else TradePolicyStopLossUpAction(
                parameter=stop_loss_pct_new)


