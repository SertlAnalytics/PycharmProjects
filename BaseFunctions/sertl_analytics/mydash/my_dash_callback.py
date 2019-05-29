"""
Description: This module contains the base class for dash callback parameter handling
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-15
"""

from sertl_analytics.constants.my_constants import DSHC, DSHVT, DSHCT


class DashCallbackParameter:
    def __init__(self, name: str, callback_type: str, component_type=DSHC.INPUT, value_type=None, default_value=None):
        self._name = name
        self._callback_type = callback_type
        self._component_type = component_type
        self._value_type = self.__get_default_value_type__() if value_type is None else value_type
        self._value_last = self.__get_default_value__() if default_value is None else default_value
        self._value = self._value_last

    @property
    def name(self):
        return self._name
    
    @property
    def callback_type(self):
        return self._callback_type

    @property
    def component_type(self):
        return self._component_type

    @property
    def value_type(self):
        return self._value_type

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
    
    def print_details(self):
        print('name={}, callback_type={}, component_type={}, value_type={}, value={}, value_last={}'.format(
            self._name, self._callback_type, self._component_type, self._value_type, self._value, self._value_last
        ))
    
    def has_value_been_changed(self) -> bool:
        return self._value != self._value_last

    def __get_default_value_type__(self):
        return {
            DSHC.BUTTON: DSHVT.N_CLICKS,
            DSHC.CHECK_BOX: DSHVT.SELECTED_ROW_INDICES,
            DSHC.INPUT: DSHVT.VALUE,
        }.get(self._component_type, DSHVT.CHILDREN)
    
    def __get_default_value__(self):
        return {
            DSHVT.N_CLICKS: 0, DSHVT.N_BLUR: 0, DSHVT.ROWS: [], DSHVT.SELECTED_ROW_INDICES: []
        }.get(self._value_type, '')
    

class DashInputCallbackParameter(DashCallbackParameter):
    def __init__(self, name: str, component_type=DSHC.INPUT, value_type=None, default_value=None):
        DashCallbackParameter.__init__(
            self, name=name, callback_type=DSHCT.INPUT,
            component_type=component_type, value_type=value_type, default_value=default_value)
        

class DashStateCallbackParameter(DashCallbackParameter):
    def __init__(self, name: str, component_type=DSHC.INPUT, value_type=None, default_value=None):
        DashCallbackParameter.__init__(
            self, name=name, callback_type=DSHCT.STATE,
            component_type=component_type, value_type=value_type, default_value=default_value)


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
        # print('get_parameter_value: {}: {}'.format(self.__class__.__name__, parameter_name))
        return self._parameter_dict.get(parameter_name).value

    def get_changed_parameter(self) -> DashCallbackParameter:
        for parameter in self._parameter_list:
            if parameter.has_value_been_changed():
                return parameter

    def get_clicked_button(self) -> DashCallbackParameter:
        for parameter in self._parameter_list:
            if parameter.component_type == DSHC.BUTTON and parameter.has_value_been_changed():
                return parameter

    def print_details(self):
        print('\nDetails for callback {}'.format(self.__class__.__name__))
        for parameter in self._parameter_list:
            print('...{}_{}_{}: last_value={}, value={}, changed={}'.format(
                parameter.callback_type, parameter.name, parameter.value_type,
                parameter.value_last, parameter.value, parameter.has_value_been_changed()
            ))

    def __get_parameter_list__(self) -> list:
        return []

