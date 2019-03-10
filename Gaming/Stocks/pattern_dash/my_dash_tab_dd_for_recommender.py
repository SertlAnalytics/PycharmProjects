"""
Description: This module contains the drop downs for the tab recommender for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-17
"""

from pattern_dash.my_dash_components import DropDownHandler
from sertl_analytics.constants.pattern_constants import INDICES, SCORING


class REDD:  # recommender drop down
    INDEX = 'Index'
    PERIOD_AGGREGATION = 'Period_Aggregation'
    REFRESH_INTERVAL = 'Refresh_Interval'
    SECOND_GRAPH_RANGE = 'Second_Graph_Range'
    SCORING = 'Scoring'

    @staticmethod
    def get_all_as_list():
        return [REDD.INDEX, REDD.PERIOD_AGGREGATION, REDD.REFRESH_INTERVAL, REDD.SECOND_GRAPH_RANGE, REDD.SCORING]


class RecommenderTabDropDownHandler(DropDownHandler):
    def __init__(self):
        self._position_options = []
        DropDownHandler.__init__(self)

    def __get_drop_down_key_list__(self):
        return REDD.get_all_as_list()

    def __get_selected_value_dict__(self):
        return {REDD.INDEX: '', REDD.PERIOD_AGGREGATION: '',
                REDD.REFRESH_INTERVAL: '', REDD.SECOND_GRAPH_RANGE: '', REDD.SCORING: ''}

    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            REDD.INDEX: 'Indices',
            REDD.PERIOD_AGGREGATION: 'Aggregation',
            REDD.REFRESH_INTERVAL: 'Refresh interval',
            REDD.SECOND_GRAPH_RANGE: 'Second graph range',
            REDD.SCORING: 'Scoring'
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            REDD.INDEX: 'my_recommender_index',
            REDD.PERIOD_AGGREGATION: 'my_recommender_aggregation',
            REDD.REFRESH_INTERVAL: 'my_recommender_refresh_interval_selection',
            REDD.SECOND_GRAPH_RANGE: 'my_recommender_graph_second_days_selection',
            REDD.SCORING: 'my_recommender_scoring_selection'
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None):
        default_dict = {
            REDD.INDEX: [INDICES.CRYPTO_CCY, INDICES.DOW_JONES, INDICES.NASDAQ100],
            REDD.PERIOD_AGGREGATION: default_value if default_value else 5,
            REDD.REFRESH_INTERVAL: default_value if default_value else 300,
            REDD.SECOND_GRAPH_RANGE: [1, 200],
            REDD.SCORING: SCORING.BEST
        }
        # print('__get_default_value__: {}: {}'.format(drop_down_type, default_dict.get(drop_down_type, None)))
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            REDD.INDEX: 180,
            REDD.PERIOD_AGGREGATION: 100,
            REDD.REFRESH_INTERVAL: 120,
            REDD.SECOND_GRAPH_RANGE: 140,
            REDD.SCORING: 120
        }
        return value_dict.get(drop_down_type, 140)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            REDD.INDEX: self.__get_index_options__(),
            REDD.PERIOD_AGGREGATION: self.__get_refresh_aggregation_options__(),
            REDD.REFRESH_INTERVAL: self.__get_refresh_interval_options__(),
            REDD.SECOND_GRAPH_RANGE: self.__get_second_graph_range_options__(),
            REDD.SCORING: self.__get_scoring_options__(),
        }

    def __get_for_multi__(self, drop_down_type: str):
        if drop_down_type in [REDD.INDEX, REDD.SECOND_GRAPH_RANGE]:
            return True
        return False

    @staticmethod
    def __get_index_options__():
        return [
            {'label': INDICES.CRYPTO_CCY, 'value': INDICES.CRYPTO_CCY},
            {'label': INDICES.DOW_JONES, 'value': INDICES.DOW_JONES},
            {'label': INDICES.NASDAQ100, 'value': INDICES.NASDAQ100}
        ]

    @staticmethod
    def __get_refresh_aggregation_options__():
        return [
            {'label': '5 min', 'value': 5},
            {'label': '15 min', 'value': 15},
            {'label': '30 min', 'value': 30}
        ]

    @staticmethod
    def __get_refresh_interval_options__():
        return [
            {'label': '5 min', 'value': 300},
            {'label': '15 min', 'value': 900}
        ]

    @staticmethod
    def __get_second_graph_range_options__():
        return [
            {'label': 'Intraday', 'value': 1},
            {'label': '60 days', 'value': 60},
            {'label': '100 days', 'value': 100},
            {'label': '200 days', 'value': 200},
            {'label': '400 days', 'value': 400}
        ]

    @staticmethod
    def __get_scoring_options__():
        return [
            {'label': SCORING.ALL, 'value': SCORING.ALL},
            {'label': SCORING.BEST, 'value': SCORING.BEST}
        ]

