"""
Description: This class is the base class for all policy actions for reinforcement learning
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-19
"""


class PolicyAction:
    def __init__(self, parameter=None, reason=''):
        self._name = self.__get_name__()
        self._parameter = parameter
        self._reason = reason

    @property
    def name(self):
        return self._name

    @property
    def parameter(self):
        return self._parameter

    @property
    def reason(self):
        return self._reason

    def get_info_dict(self) -> dict:
        return_dict = {}
        if self.parameter is not None:
            return_dict['Action parameter'] = self.parameter
        if self.reason != '':
            return_dict['Action reason'] = self.reason
        return return_dict

    def __get_name__(self):
        return ''

