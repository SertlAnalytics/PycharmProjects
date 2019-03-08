"""
Description: This module contains the drop downs for the tab recommender for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-17
"""

from pattern_dash.my_dash_components import DropDownHandler
from sertl_analytics.constants.pattern_constants import INDICES


class WAVEDD:  # Wave tab drop down
    RETROSPECTIVE_DAYS = 'Retrospective_Days'
    THRESHOLD_SINGLE = 'Threshold_Single'
    THRESHOLD_INDEX = 'Threshold_Index'
    INDICES = 'Indices'


class WaveTabDropDownHandler(DropDownHandler):
    def __init__(self):
        self._position_options = []
        DropDownHandler.__init__(self)

    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            WAVEDD.RETROSPECTIVE_DAYS: 'Retrospective Days',
            WAVEDD.THRESHOLD_INDEX: 'Threshold Index',
            WAVEDD.THRESHOLD_SINGLE: 'Threshold Single',
            WAVEDD.INDICES: 'Index',
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            WAVEDD.RETROSPECTIVE_DAYS: 'my_waves_retrospective_days_selection',
            WAVEDD.THRESHOLD_INDEX: 'my_waves_threshold_index_selection',
            WAVEDD.THRESHOLD_SINGLE: 'my_waves_threshold_single_selection',
            WAVEDD.INDICES: 'my_waves_index_selection',
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None):
        default_dict = {
            WAVEDD.RETROSPECTIVE_DAYS: default_value if default_value else 100,
            WAVEDD.THRESHOLD_INDEX: default_value if default_value else 10,
            WAVEDD.THRESHOLD_SINGLE: default_value if default_value else 2,
            WAVEDD.INDICES: default_value if default_value else INDICES.ALL,
        }
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            WAVEDD.RETROSPECTIVE_DAYS: 250,
            WAVEDD.THRESHOLD_INDEX: 250,
            WAVEDD.THRESHOLD_SINGLE: 250,
            WAVEDD.INDICES: 150,
        }
        return value_dict.get(drop_down_type, 250)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            WAVEDD.RETROSPECTIVE_DAYS: self.__get_waves_retrospective_days_options__(),
            WAVEDD.THRESHOLD_INDEX: self.__get_waves_threshold_index_options__(),
            WAVEDD.THRESHOLD_SINGLE: self.__get_waves_threshold_single_options__(),
            WAVEDD.INDICES: self.__get_index_options__(),
          }

    def __get_for_multi__(self, drop_down_type: str):
        return False

    @staticmethod
    def __get_waves_retrospective_days_options__():
        return [
            {'label': '10', 'value': 10},
            {'label': '30', 'value': 30},
            {'label': '100', 'value': 100},
            {'label': '200', 'value': 200},
            {'label': '400', 'value': 400},
            {'label': '600', 'value': 600},
        ]

    @staticmethod
    def get_max_retrospective_days():
        options = WaveTabDropDownHandler.__get_waves_retrospective_days_options__()
        return max([options['value'] for options in options])

    @staticmethod
    def __get_waves_threshold_single_options__():
        return [
            {'label': '1', 'value': 1},
            {'label': '2', 'value': 2},
            {'label': '3', 'value': 3},
            {'label': '4', 'value': 4},
            {'label': '5', 'value': 5},
        ]

    @staticmethod
    def __get_waves_threshold_index_options__():
        return [
            {'label': '1', 'value': 1},
            {'label': '5', 'value': 5},
            {'label': '10', 'value': 10},
            {'label': '15', 'value': 15},
            {'label': '20', 'value': 20},
            {'label': '30', 'value': 30},
            {'label': '50', 'value': 50},
        ]

    @staticmethod
    def __get_index_options__():
        return [
            {'label': INDICES.ALL, 'value': INDICES.ALL},
            {'label': INDICES.CRYPTO_CCY, 'value': INDICES.CRYPTO_CCY},
            {'label': INDICES.DOW_JONES, 'value': INDICES.DOW_JONES},
            {'label': INDICES.NASDAQ100, 'value': INDICES.NASDAQ100}
        ]
