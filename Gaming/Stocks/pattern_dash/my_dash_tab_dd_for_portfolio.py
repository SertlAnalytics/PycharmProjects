"""
Description: This module contains the drop downs for the tab pattern for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-17
"""

from pattern_dash.my_dash_components import DropDownHandler
from sertl_analytics.constants.pattern_constants import INDI


class PODD:  # portfolio drop down
    PERIOD_AGGREGATION = 'Period_Aggregation'
    REFRESH_INTERVAL = 'Refresh_Interval'
    SECOND_GRAPH_RANGE = 'Second_Graph_Range'
    INDICATOR = 'Indicator'


class PortfolioTabDropDownHandler(DropDownHandler):
    def __init__(self):
        self._indicator_options = INDI.get_as_options()
        DropDownHandler.__init__(self)

    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            PODD.PERIOD_AGGREGATION: 'Aggregation',
            PODD.REFRESH_INTERVAL: 'Refresh interval',
            PODD.SECOND_GRAPH_RANGE: 'Second graph range',
            PODD.INDICATOR: 'Indicator'
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            PODD.PERIOD_AGGREGATION: 'my_portfolio_aggregation',
            PODD.REFRESH_INTERVAL: 'my_portfolio_refresh_interval_selection',
            PODD.SECOND_GRAPH_RANGE: 'my_portfolio_graph_second_days_selection',
            PODD.INDICATOR: 'my_portfolio_indicator_selection',
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None) -> str:
        default_dict = {
            PODD.PERIOD_AGGREGATION: default_value if default_value else 5,
            PODD.REFRESH_INTERVAL: default_value if default_value else 300,
            PODD.SECOND_GRAPH_RANGE: [1, 200],
            PODD.INDICATOR: self._indicator_options[0]['value'],
        }
        # print('__get_default_value__: {}: {}'.format(drop_down_type, default_dict.get(drop_down_type, None)))
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            PODD.PERIOD_AGGREGATION: 100,
            PODD.REFRESH_INTERVAL: 120,
            PODD.SECOND_GRAPH_RANGE: 140,
            PODD.INDICATOR: 160
        }
        return value_dict.get(drop_down_type, None)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            PODD.PERIOD_AGGREGATION: self.__get_refresh_aggregation_options__(),
            PODD.REFRESH_INTERVAL: self.__get_refresh_interval_options__(),
            PODD.SECOND_GRAPH_RANGE: self.__get_second_graph_range_options__(),
            PODD.INDICATOR: self._indicator_options,
        }

    def __get_for_multi__(self, drop_down_type: str):
        if drop_down_type == PODD.SECOND_GRAPH_RANGE:
            return True
        return False

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

