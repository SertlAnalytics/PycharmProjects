"""
Description: This module contains the central search class for salesman
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-08
"""

from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from sertl_analytics.pybase.data_dictionary import DataDictionary
from salesman_system_configuration import SystemConfiguration


class SalesmanSearch:
    def __init__(self, target_data_providers: list):
        self._target_data_providers = target_data_providers
        self._target_data_provider = SLSRC.ALL
        self._search_string = ''
        self._sale = None
        self._search_label_list = []
        self._search_label_dict = {}
        self._region = ''
        self._category = ''
        self._sub_category = ''

    def search_by_string(self, search_string: str, target_data_provider=SLSRC.ALL):
        self._target_data_provider = target_data_provider
        self._search_string = search_string

