"""
Description: This module contains the drop downs for the tab recommender for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-17
"""

from sertl_analytics.mydash.my_dash_components import DropDownHandler
from sertl_analytics.constants.pattern_constants import INDICES, PRD


class WAVEDD:  # Wave tab drop down
    PERIOD = 'Period'
    AGGREGATION = 'Aggregation'
    RETROSPECTIVE_TICKS = 'Retrospective_Ticks'
    INDICES = 'Indices'

    @staticmethod
    def get_all_as_list():
        return [WAVEDD.PERIOD, WAVEDD.AGGREGATION, WAVEDD.RETROSPECTIVE_TICKS, WAVEDD.INDICES]


class WaveTabDropDownHandler(DropDownHandler):
    def __init__(self):
        DropDownHandler.__init__(self)

    @property
    def selected_period(self):
        return self._selected_value_dict[WAVEDD.PERIOD]

    @property
    def selected_aggregation(self):
        return self._selected_value_dict[WAVEDD.AGGREGATION]

    @property
    def selected_retrospective_ticks(self):
        return self._selected_value_dict[WAVEDD.RETROSPECTIVE_TICKS]

    @property
    def selected_index(self):
        return self._selected_value_dict[WAVEDD.INDICES]

    @property
    def my_waves_period_selection_id(self):
        return 'my_waves_period_selection'

    @property
    def my_waves_aggregation_selection_id(self):
        return 'my_waves_aggregation_selection'

    @property
    def my_waves_retrospective_ticks_selection_id(self):
        return 'my_waves_retrospective_ticks_selection'

    @property
    def my_waves_index_selection_id(self):
        return 'my_waves_index_selection'

    def __get_drop_down_key_list__(self):
        return WAVEDD.get_all_as_list()

    def __get_selected_value_dict__(self):
        return {WAVEDD.PERIOD: PRD.DAILY, WAVEDD.AGGREGATION: 30,
                WAVEDD.RETROSPECTIVE_TICKS: 150, WAVEDD.INDICES: INDICES.ALL}

    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            WAVEDD.PERIOD: 'Period',
            WAVEDD.AGGREGATION: 'Aggregation',
            WAVEDD.RETROSPECTIVE_TICKS: 'Retrospective Ticks',
            WAVEDD.INDICES: 'Index',
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            WAVEDD.PERIOD: self.my_waves_period_selection_id,
            WAVEDD.AGGREGATION: self.my_waves_aggregation_selection_id,
            WAVEDD.RETROSPECTIVE_TICKS: self.my_waves_retrospective_ticks_selection_id,
            WAVEDD.INDICES: self.my_waves_index_selection_id,
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None):
        default_dict = {
            WAVEDD.PERIOD: default_value if default_value else self.selected_period,
            WAVEDD.AGGREGATION: default_value if default_value else self.selected_aggregation,
            WAVEDD.RETROSPECTIVE_TICKS: default_value if default_value else self.selected_retrospective_ticks,
            WAVEDD.INDICES: default_value if default_value else self.selected_index,
        }
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            WAVEDD.PERIOD: 250,
            WAVEDD.AGGREGATION: 250,
            WAVEDD.RETROSPECTIVE_TICKS: 250,
            WAVEDD.INDICES: 150,
        }
        return value_dict.get(drop_down_type, 250)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            WAVEDD.PERIOD: self.__get_waves_period_options__(),
            WAVEDD.AGGREGATION: self.__get_waves_aggregation_options__(),
            WAVEDD.RETROSPECTIVE_TICKS: self.__get_waves_retrospective_ticks_options__(),
            WAVEDD.INDICES: self.__get_index_options__(),
          }

    def __get_for_multi__(self, drop_down_type: str):
        return False

    @staticmethod
    def __get_waves_period_options__():
        return [
            {'label': PRD.DAILY, 'value': PRD.DAILY},
            {'label': PRD.INTRADAY, 'value': PRD.INTRADAY},
        ]

    @staticmethod
    def __get_waves_aggregation_options__():
        return [
            {'label': '30', 'value': 30},
            {'label': '15', 'value': 15},
        ]

    @staticmethod
    def get_max_aggregation_value():
        options = WaveTabDropDownHandler.__get_waves_aggregation_options__()
        return max([options['value'] for options in options])

    @staticmethod
    def __get_waves_retrospective_ticks_options__():
        return [
            {'label': '10', 'value': 10},
            {'label': '30', 'value': 30},
            {'label': '100', 'value': 100},
            {'label': '150', 'value': 150},
            {'label': '200', 'value': 200},
            {'label': '400', 'value': 400},
            {'label': '600', 'value': 600},
        ]

    @staticmethod
    def get_max_retrospective_ticks():
        options = WaveTabDropDownHandler.__get_waves_retrospective_ticks_options__()
        return max([options['value'] for options in options])


    @staticmethod
    def __get_index_options__():
        return [
            {'label': INDICES.ALL, 'value': INDICES.ALL},
            {'label': INDICES.CRYPTO_CCY, 'value': INDICES.CRYPTO_CCY},
            {'label': INDICES.DOW_JONES, 'value': INDICES.DOW_JONES},
            {'label': INDICES.NASDAQ100, 'value': INDICES.NASDAQ100}
        ]
