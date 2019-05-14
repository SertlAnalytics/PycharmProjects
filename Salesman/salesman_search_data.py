"""
Description: This module contains the class for preparing the search for similar sales
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-08
"""

from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_system_configuration import SystemConfiguration
from salesman_tutti.tutti_constants import PRCAT
from salesman_tutti.tutti_url_factory import OnlineSearchApi
from salesman_sale import SalesmanSale
from salesman_web_parser import SalesmanWebParser, OnlineSearchApi


class SalesmanSearchData:
    def __init__(self, sys_config: SystemConfiguration, sale: SalesmanSale):
        self._sys_config = sys_config
        self._sale = sale
        self._region = self._sale.region
        self._region_value = self.__get_region_value__()
        self._category = self._sale.product_category
        self._category_value = self.__get_category_value__()
        # print('SalesmanSearchData: category={}, category_value={}'.format(self._category, self._category_value))
        self._sub_category = self._sale.product_sub_category
        self._sub_category_value = self.__get_sub_category_value__()
        self._online_search_api_list = self.__get_online_search_api_list__()
        self._max_number_found = 0

    @property
    def product_category(self):
        return self._category

    @property
    def online_search_api_list(self):
        return self._online_search_api_list

    @property
    def max_number_found(self):
        return self._max_number_found

    def adjust_online_search_api_list_by_found_number_dict(self, index_number_dict: dict):
        self._max_number_found = max([number for number in index_number_dict.values()])
        self.__print_online_search_api_list__(index_number_dict)
        self._online_search_api_list = [self._online_search_api_list[k]
                                        for k in index_number_dict if index_number_dict[k] > self._max_number_found/20]

    def __print_online_search_api_list__(self, index_number_dict: dict):
        print('online_search_api_index_number_dict={}'.format(index_number_dict))
        category_number_dict = {
            self._online_search_api_list[k].category_value: index_number_dict[k]
            for k in index_number_dict if index_number_dict[k] > self._max_number_found / 20}
        print('Search over: {}'.format(category_number_dict))

    def __get_region_value__(self):
        return ''  # we want to search in whole Switzerland
        # return '' if self._region == '' else \
        #     self._sys_config.region_categorizer.get_value_for_category(self._region)

    def __get_category_value__(self):
        return '' if self._category == '' else \
            self._sys_config.product_categorizer.get_value_for_category(self._category)

    def __get_sub_category_value__(self):
        if self._sub_category == '':
            return ''
        return self._sys_config.product_categorizer.get_sub_category_value_for_sub_category(
            self._category, self._sub_category)

    def __get_online_search_api_list__(self) -> list:
        return_list = []
        if self._category == '':
            category_value_list = self._sys_config.product_categorizer.get_category_value_list(excluded=[PRCAT.ALL])
            for category_value in category_value_list:
                api = OnlineSearchApi('')
                api.region_value = self._region_value
                api.category_value = category_value
                return_list.append(api)
            return return_list
        api = OnlineSearchApi('')
        api.region_value = self._region_value
        api.category_value = self._category_value
        api.sub_category_value = self._sub_category_value
        api_alternative = self.__get_alternative_online_search_api__()
        if api_alternative is None:
            return [api]
        else:
            api_alternative.print_api_details('Added search api')
            return [api, api_alternative]

    def __get_alternative_online_search_api__(self):
        alternative_categories = self._sys_config.product_categorizer.get_alternative_search_category_sub_categories(
            self._category, self._sub_category
        )
        if alternative_categories is not None:
            api = OnlineSearchApi('')
            api.region_value = self._region_value
            api.category_value = self._sys_config.product_categorizer.get_value_for_category(
                alternative_categories[0])
            if alternative_categories[1] != '':
                api.sub_category_value = self._sys_config.product_categorizer.get_sub_category_value_for_sub_category(
                    alternative_categories[0], alternative_categories[1])
            return api

