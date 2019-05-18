"""
Description: This module contains the class for preparing the search for similar sales
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-08
"""

from salesman_system_configuration import SystemConfiguration
from salesman_tutti.tutti_constants import PRCAT
from salesman_search import SalesmanSearchApi
from salesman_sale import SalesmanSale


class SalesmanSearchData:
    def __init__(self, sys_config: SystemConfiguration, sale: SalesmanSale):
        self._sys_config = sys_config
        self._region_categorizer = self._sys_config.region_categorizer
        self._product_categorizer = self._sys_config.product_categorizer
        self._sale = sale
        self._region = self._sale.region
        self._region_value = self.__get_region_value__()
        self._category = self._sale.product_category
        self._category_value = self.__get_category_value__()
        # print('SalesmanSearchData: category={}, category_value={}'.format(self._category, self._category_value))
        self._sub_category = self._sale.product_sub_category
        self._sub_category_value = self.__get_sub_category_value__()
        self._search_api_list = self.__get_search_api_list__()

    @property
    def product_category(self):
        return self._category

    @property
    def search_api_list(self):
        return self._search_api_list

    @property
    def max_number_found(self) -> int:
        return max([api.found_numbers for api in self._search_api_list])

    def adjust_search_api_list_by_found_numbers(self):
        threshold = max([3, self.max_number_found / 20])
        self._search_api_list = [api for api in self._search_api_list if api.found_numbers >= threshold]
        print('Search over: {}'.format(
            ', '.join(['{}: {}'.format(api.category_value, api.found_numbers) for api in self._search_api_list])))

    def adjust_search_api_list_by_suggested_categories(self, suggested_categories):
        self._search_api_list = [api for api in self._search_api_list if api.category_value in suggested_categories]

    def get_api_categories(self) -> list:
        return [api.category_value for api in self._search_api_list]

    def __get_region_value__(self):
        if self._sale.description == '':  # online search
            return '' if self._region == '' else self._region_categorizer.get_value_for_category(self._region)
        else:  # sale from database: we want to search in whole Switzerland
            return ''

    def __get_category_value__(self):
        return '' if self._category == '' else \
            self._product_categorizer.get_value_for_category(self._category)

    def __get_sub_category_value__(self):
        if self._sub_category == '':
            return ''
        return self._product_categorizer.get_sub_category_value_for_sub_category(
            self._category, self._sub_category)

    def __get_search_api_list__(self) -> list:
        return_list = []
        if self._category == '':
            category_value_list = self._product_categorizer.get_category_value_list(excluded=[PRCAT.ALL])
            for category_value in category_value_list:
                api = SalesmanSearchApi('')
                api.region_value = self._region_value
                api.category_value = category_value
                return_list.append(api)
            return return_list
        api = SalesmanSearchApi('')
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
        alternative_categories = self._product_categorizer.get_alternative_search_category_sub_categories(
            self._category, self._sub_category
        )
        if alternative_categories is not None:
            api = SalesmanSearchApi('')
            api.region_value = self._region_value
            api.category_value = self._product_categorizer.get_value_for_category(
                alternative_categories[0])
            if alternative_categories[1] != '':
                api.sub_category_value = self._product_categorizer.get_sub_category_value_for_sub_category(
                    alternative_categories[0], alternative_categories[1])
            return api

