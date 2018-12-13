"""
Description: This module contains the drop downs for the tab pattern for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-17
"""

from pattern_dash.my_dash_components import DropDownHandler
from sertl_analytics.constants.pattern_constants import INDICES


class PDD:  # pattern drop down
    INDEX = 'Index'
    STOCK_SYMBOL = 'Stock_Symbol'
    PERIOD_AGGREGATION = 'Period_Aggregation'
    REFRESH_INTERVAL = 'Refresh_Interval'
    SECOND_GRAPH_RANGE = 'Second_Graph_Range'


class PatternTabDropDownHandler(DropDownHandler):
    def __init__(self, index_options: list, ticker_options: list):
        self._index_options = index_options
        self._ticker_options = ticker_options
        DropDownHandler.__init__(self)

    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            PDD.INDEX: 'Indices',
            PDD.STOCK_SYMBOL: 'Stock _symbol',
            PDD.PERIOD_AGGREGATION: 'Aggregation',
            PDD.REFRESH_INTERVAL: 'Refresh interval',
            PDD.SECOND_GRAPH_RANGE: 'Second graph range'
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            PDD.INDEX: 'my_pattern_index_selection',
            PDD.STOCK_SYMBOL: 'my_pattern_ticker_selection',
            PDD.PERIOD_AGGREGATION: 'my_period_aggregation',
            PDD.REFRESH_INTERVAL: 'my_interval_selection',
            PDD.SECOND_GRAPH_RANGE: 'my_graph_second_days_selection'
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None) -> str:
        default_dict = {
            PDD.INDEX: self._index_options[0]['value'],
            PDD.STOCK_SYMBOL: self._ticker_options[0]['value'],
            PDD.PERIOD_AGGREGATION: default_value if default_value else 5,
            PDD.REFRESH_INTERVAL: 300,
            PDD.SECOND_GRAPH_RANGE: 1
        }
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            PDD.INDEX: 180,
            PDD.STOCK_SYMBOL: 200,
            PDD.PERIOD_AGGREGATION: 100,
            PDD.REFRESH_INTERVAL: 120,
            PDD.SECOND_GRAPH_RANGE: 140
        }
        return value_dict.get(drop_down_type, None)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            PDD.INDEX: self._index_options,
            PDD.STOCK_SYMBOL: self._ticker_options,
            PDD.PERIOD_AGGREGATION: self.__get_refresh_aggregation_options__(),
            PDD.REFRESH_INTERVAL: self.__get_refresh_interval_options__(),
            PDD.SECOND_GRAPH_RANGE: self.__get_second_graph_range_options__(),
        }

    def __get_for_multi__(self, drop_down_type: str):
        if drop_down_type in [PDD.INDEX]:
            return False
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
            {'label': '15 min', 'value': 900},
            {'label': '5 min', 'value': 300},
            {'label': '2 min', 'value': 120},
            {'label': '1 min', 'value': 60},
            {'label': '30 sec.', 'value': 30},
            {'label': '15 sec.', 'value': 15},
            {'label': '10 sec.', 'value': 10},
        ]

    @staticmethod
    def __get_second_graph_range_options__():
        return [
            {'label': 'NONE', 'value': 0},
            {'label': 'Intraday', 'value': 1},
            {'label': '60 days', 'value': 60},
            {'label': '100 days', 'value': 100},
            {'label': '200 days', 'value': 200},
            {'label': '400 days', 'value': 400}
        ]