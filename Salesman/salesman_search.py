"""
Description: This module contains the central search class for salesman
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-08
"""

from sertl_analytics.constants.salesman_constants import SLSRC


class SalesmanSearchApi:
    def __init__(self, search_string: str):
        self.search_string = search_string
        self.region_value = ''
        self.category_value = ''
        self.sub_category_value = ''
        self.found_numbers = 0  # will be filled after search by these parameters

    def print_api_details(self, prefix: str):
        print('{}: region_value={}, category_value={}, sub_category_value={}'.format(
            prefix, self.region_value, self.category_value, self.sub_category_value))


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

