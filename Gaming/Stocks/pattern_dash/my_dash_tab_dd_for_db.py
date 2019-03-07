"""
Description: This module contains the drop downs for the tab recommender for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-17
"""

from pattern_dash.my_dash_components import DropDownHandler
from sertl_analytics.constants.pattern_constants import STBL, DTRG


class DBDD:  # recommender drop down
    TABLE = 'Table'
    LIMIT = 'Limit'
    DATE_RANGE = 'Date_Range'


class DBTabDropDownHandler(DropDownHandler):
    def __init__(self):
        self._position_options = []
        DropDownHandler.__init__(self)

    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            DBDD.TABLE: 'Table',
            DBDD.LIMIT: 'Limit',
            DBDD.DATE_RANGE: 'Date Range',
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            DBDD.TABLE: 'my_db_table_selection',
            DBDD.LIMIT: 'my_db_limit_selection',
            DBDD.DATE_RANGE: 'my_db_date_range_selection',
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None):
        default_dict = {
            DBDD.TABLE: default_value if default_value else STBL.PROCESS,
            DBDD.LIMIT: default_value if default_value else 10,
            DBDD.DATE_RANGE: default_value if default_value else DTRG.TODAY,
        }
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            DBDD.TABLE: 180,
            DBDD.LIMIT: 180,
            DBDD.DATE_RANGE: 180,
        }
        return value_dict.get(drop_down_type, 140)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            DBDD.TABLE: self.__get_table_options__(),
            DBDD.LIMIT: self.__get_limit_options__(),
            DBDD.DATE_RANGE: self.__get_date_range_options__()
          }

    def __get_for_multi__(self, drop_down_type: str):
        return False

    @staticmethod
    def __get_table_options__():
        return STBL.get_as_options()

    @staticmethod
    def __get_limit_options__():
        return [
            {'label': '1', 'value': 1},
            {'label': '10', 'value': 10},
            {'label': '100', 'value': 100},
            {'label': '1000', 'value': 1000}
        ]

    @staticmethod
    def __get_date_range_options__():
        return DTRG.get_as_options_for_db_tab()
