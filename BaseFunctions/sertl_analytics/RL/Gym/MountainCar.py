import numpy as np
import matplotlib.pyplot as plt
import gym
import os
from time import sleep

if False:
    env = gym.make("MountainCar-v0")

    plt.imshow(env.render('rgb_array'))
    print("Observation space:", env.observation_space)
    print("Action space:", env.action_space)

    sleep(2)
    env.close()
else:
    # env = gym.make('CartPole-v0')
    env = gym.make("MountainCar-v0")
    env.reset()
    print('action space={}'.format(type(env.action_space)))
    for _ in range(1000):
        env.render()
        env.step(env.action_space.sample())  # take a random action
    env.close()
