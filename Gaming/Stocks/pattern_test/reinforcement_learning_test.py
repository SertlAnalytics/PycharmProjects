"""
Description: This module contains the trade test classes which are uses for single test and back testing
Author: FAIZAN SHAIKH, JANUARY 19, 2017
https://www.analyticsvidhya.com/blog/2017/01/introduction-to-reinforcement-learning-implementation/
Copyright: www.analyticsvidhya.com
Date: 2018-12-22
"""

# First we have to import modules that are necessary
import numpy as np
import gym

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

# Then set the relevant variables

ENV_NAME = 'CartPole-v0'

# Get the environment and extract the number of actions available in the Cartpole problem
env = gym.make(ENV_NAME)
np.random.seed(123)
env.seed(123)
nb_actions = env.action_space.n

# Next, we build a very simple single hidden layer neural network model.
model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(nb_actions))
model.add(Activation('linear'))
print(model.summary())

# Next, we configure and compile our agent. We set our policy as Epsilon Greedy and
# we also set our memory as Sequential Memory because we want to store the result of actions we performed
# and the rewards we get for each action.

policy = EpsGreedyQPolicy()
memory = SequentialMemory(limit=50000, window_length=1)
dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=10,
target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# Okay, now it's time to learn something! We visualize the training here for show, but this slows down training quite a lot.
dqn.fit(env, nb_steps=5000, visualize=True, verbose=2)

# Now we test our reinforcement learning model
dqn.test(env, nb_episodes=5, visualize=True)

