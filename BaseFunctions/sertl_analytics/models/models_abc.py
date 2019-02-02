"""
Description: This module is the abstract base class for models and their related classes,
i.e they have to implement those functions.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-17
"""

from abc import ABCMeta, abstractmethod
from sertl_analytics.models.policy_action import PolicyAction


class PolicyInterface:
    __metaclass__ = ABCMeta

    @classmethod
    def version(cls): return 1.0

    @abstractmethod
    def observation_space(self):  # data frame for the observations, shape[0] return the numbers of observations
        raise NotImplementedError

    @abstractmethod
    def reset(self):  # initialize the environment
        raise NotImplementedError

    @abstractmethod
    def render(self, mode=''):  # shows the environment
        raise NotImplementedError

    @abstractmethod
    def step(self, action: str):  # returns obs, reward, done, info
        raise NotImplementedError


class EnvironmentInterface:
    __metaclass__ = ABCMeta

    @classmethod
    def version(cls): return 1.0

    @abstractmethod
    def observation_space(self):  # data frame for the observations, shape[0] return the numbers of observations
        raise NotImplementedError

    @abstractmethod
    def __get_observation_space__(self):  # filling the observation space - if it is a discrete one
        raise NotImplementedError

    @abstractmethod
    def reset(self):  # initialize the environment
        raise NotImplementedError

    @abstractmethod
    def render(self, mode=''):  # shows the environment
        raise NotImplementedError

    @abstractmethod
    def step(self, action: PolicyAction):  # returns obs, reward, done, info
        raise NotImplementedError

