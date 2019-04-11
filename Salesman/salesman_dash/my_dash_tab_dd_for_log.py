"""
Description: This module contains the drop downs for the tab recommender for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-17
"""

from sertl_analytics.mydash.my_dash_components import DropDownHandler
from sertl_analytics.constants.pattern_constants import INDICES, LOGT, DTRG
from salesman_dash.my_dash_header_tables import MyHTMLTabLogHeaderTable


class LOGDD:  # recommender drop down
    LOG_TYPE = 'Log_Type'
    PROCESS = 'Process'
    PROCESS_STEP = 'Process_Step'
    DATE_RANGE = 'Date_Range'

    @staticmethod
    def get_all_as_list():
        return [LOGDD.LOG_TYPE, LOGDD.PROCESS, LOGDD.PROCESS_STEP, LOGDD.DATE_RANGE]


class LogTabDropDownHandler(DropDownHandler):
    def __init__(self):
        self._position_options = []
        DropDownHandler.__init__(self)

    def __get_drop_down_key_list__(self):
        return LOGDD.get_all_as_list()

    def __get_selected_value_dict__(self):
        return {LOGDD.LOG_TYPE: '', LOGDD.PROCESS: '', LOGDD.PROCESS_STEP: '', LOGDD.DATE_RANGE: ''}

    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            LOGDD.LOG_TYPE: 'Log Type',
            LOGDD.PROCESS: 'Process',
            LOGDD.PROCESS_STEP: 'Process Step',
            LOGDD.DATE_RANGE: 'Date Range'
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            LOGDD.LOG_TYPE: 'my_log_type_selection',
            LOGDD.PROCESS: 'my_log_process_selection',
            LOGDD.PROCESS_STEP: 'my_log_process_step_selection',
            LOGDD.DATE_RANGE: 'my_log_date_range_selection'
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None):
        default_dict = {
            LOGDD.LOG_TYPE: default_value if default_value else LOGT.WAVES,
            LOGDD.PROCESS: '',
            LOGDD.PROCESS_STEP: '',
            LOGDD.DATE_RANGE: DTRG.TODAY
        }
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            LOGDD.LOG_TYPE: 180,
            LOGDD.PROCESS: 250,
            LOGDD.PROCESS_STEP: 250,
            LOGDD.DATE_RANGE: 140
        }
        return value_dict.get(drop_down_type, 140)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            LOGDD.LOG_TYPE: self.__get_log_type_options__(),
            LOGDD.PROCESS: self.__get_process_options__(),
            LOGDD.PROCESS_STEP: self.__get_process_step_options__(),
            LOGDD.DATE_RANGE: self.__get_date_range_options__()
          }

    def __get_for_multi__(self, drop_down_type: str):
        return False

    @staticmethod
    def __get_log_type_options__():
        return MyHTMLTabLogHeaderTable.get_types_for_processing_as_options()

    @staticmethod
    def __get_process_options__():
        return [
            {'label': 'All', 'value': 'All'}
        ]

    @staticmethod
    def __get_process_step_options__():
        return [
            {'label': 'All', 'value': 'All'}
        ]

    @staticmethod
    def __get_date_range_options__():
        return DTRG.get_as_options_for_log_tab()
