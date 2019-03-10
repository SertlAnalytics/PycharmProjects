"""
Description: This module contains the drop downs for the tab recommender for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-17
"""

from pattern_dash.my_dash_components import DropDownHandler
from sertl_analytics.constants.pattern_constants import INDICES, SCORING


class CDD:  # configuration drop down
    ORDER_MAXIMUM = 'Order_Maximum_Value'
    SOUND_MACHINE = 'Sound_Machine'

    @staticmethod
    def get_all_as_list():
        return [CDD.ORDER_MAXIMUM, CDD.SOUND_MACHINE]


class ConfigurationTabDropDownHandler(DropDownHandler):
    def __init__(self, order_max: int, sound_machine_active: bool):
        self._order_max_default = order_max
        self._sound_machine_active_default = sound_machine_active
        self._order_max_list = [100, 200, 500, 1000, 2000]
        if self._order_max_default not in self._order_max_list:
            self._order_max_list.append(self._order_max_default)
        self._sound_machine_state_list = ['active', 'inactive']
        DropDownHandler.__init__(self)

    def __get_drop_down_key_list__(self):
        return CDD.get_all_as_list()

    def __get_selected_value_dict__(self):
        return {CDD.ORDER_MAXIMUM: 0, CDD.SOUND_MACHINE: 'inactive'}

    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            CDD.ORDER_MAXIMUM: 'Order Maximum',
            CDD.SOUND_MACHINE: 'Sound Machine',
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            CDD.ORDER_MAXIMUM: 'my_configuration_order_maximum',
            CDD.SOUND_MACHINE: 'my_configuration_sound_machine_state',
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None):
        default_dict = {
            CDD.ORDER_MAXIMUM: self._order_max_default,
            CDD.SOUND_MACHINE: 'active' if self._sound_machine_active_default else 'inactive'
        }
        # print('__get_default_value__: {}: {}'.format(drop_down_type, default_dict.get(drop_down_type, None)))
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            CDD.ORDER_MAXIMUM: 150,
            CDD.SOUND_MACHINE: 150,
        }
        return value_dict.get(drop_down_type, 140)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            CDD.ORDER_MAXIMUM: self.__get_order_maximum_options__(),
            CDD.SOUND_MACHINE: self.__get_sound_machine_options__(),
        }

    def __get_for_multi__(self, drop_down_type: str):
        return False

    def __get_order_maximum_options__(self):
        return [{'label': max_value, 'value': max_value} for max_value in self._order_max_list]

    def __get_sound_machine_options__(self):
        return [{'label': state, 'value': state} for state in self._sound_machine_state_list]

