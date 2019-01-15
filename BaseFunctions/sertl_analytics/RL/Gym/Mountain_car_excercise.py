import numpy as np
import matplotlib.pyplot as plt
import gym
import os
from time import sleep

# create env manually to set time limit. Please don't change this.
TIME_LIMIT = 250
env = gym.wrappers.TimeLimit(gym.envs.classic_control.MountainCarEnv(), max_episode_steps=TIME_LIMIT + 1)
s = env.reset()
actions = {'left': 0, 'stop': 1, 'right': 2}

# prepare "display"
fig = plt.figure()
ax = fig.add_subplot(111)
fig.show()


def policy(t):
    # YOUR CODE HERE
    return actions['right']


for t in range(TIME_LIMIT):

    s, r, done, _ = env.step(policy(t))

    # draw game image on display
    ax.clear()
    ax.imshow(env.render('rgb_array'))
    fig.canvas.draw()

    if done:
        print("Well done!")
        break
else:
    print("Time limit exceeded. Try again.")