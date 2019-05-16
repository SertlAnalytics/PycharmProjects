"""
Description: This module contains the base class for dash callback parameter handling
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-15
"""

from sertl_analytics.constants.my_constants import MYDSHC


class DashCallbackParameter:
    def __init__(self, name: str, component_type=MYDSHC.INPUT, default_value=None):
        self._name = name
        self._component_type = component_type
        self._value_last = self.__get_default_value__() if default_value is None else default_value
        self._value = self._value_last

    @property
    def name(self):
        return self._name

    @property
    def component_type(self):
        return self._component_type

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value_new):
        self._value_last = self._value
        self._value = value_new

    @property
    def value_last(self):
        return self._value_last

    def has_value_been_changed(self) -> bool:
        return self._value != self._value_last

    def __get_default_value__(self):
        return {MYDSHC.BUTTON: 0, MYDSHC.CHECK_BOX: []}.get(self._component_type, '')


class DashCallback:
    def __init__(self):
        self._parameter_list = self.__get_parameter_list__()
        self._parameter_dict = {parameter.name: parameter for parameter in self._parameter_list}

    def set_values(self, *values):
        for idx, value in enumerate(values):
            self._parameter_list[idx].value = value

    def get_parameter(self, parameter_name):
        return self._parameter_dict.get(parameter_name)
    
    def has_value_been_changed_for_parameter(self, parameter_name):
        return self._parameter_dict.get(parameter_name).has_value_been_changed()
    
    def get_parameter_value(self, parameter_name: str):
        return self._parameter_dict.get(parameter_name).value

    def get_changed_parameter(self) -> DashCallbackParameter:
        for parameter in self._parameter_list:
            if parameter.has_value_been_changed():
                return parameter

    def get_clicked_button(self) -> DashCallbackParameter:
        for parameter in self._parameter_list:
            if parameter.component_type == MYDSHC.BUTTON and parameter.has_value_been_changed():
                return parameter

    def print_details(self):
        print('\nDetails for callback {}'.format(self.__class__.__name__))
        for parameter in self._parameter_list:
            print('...{}: last_value={}, value={}, changed={}'.format(
                parameter.name, parameter.value_last, parameter.value, parameter.has_value_been_changed()
            ))

    def __get_parameter_list__(self) -> list:
        return []



