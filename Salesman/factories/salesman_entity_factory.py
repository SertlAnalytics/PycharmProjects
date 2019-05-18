"""
Description: This module contains the factory class for sale entity
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-08
"""

from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.salesman_constants import EL
from salesman_system_configuration import SystemConfiguration


class SalesmanEntityFactory:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self._access_layer_entity_category = self.sys_config.access_layer_entity_category
        self._key_delimiter = '#'

    def is_entity_key_available(self, entity_key: str) -> bool:
        return self._access_layer_entity_category.is_entity_key_available(entity_key)

    def change_entity_category_in_db(self, sale_entity_label_dict: dict, category_list: list):
        categories_value = self._key_delimiter.join(sorted(category_list))
        entity_key = self.__get_key_for_entity_label_dict__(sale_entity_label_dict)
        print('change_entity_category_in_db: dict={}, list={} -> key={}, cat={}'.format(
            sale_entity_label_dict, category_list, entity_key, categories_value))
        self.insert_entity_category(entity_key, categories_value)

    def get_suggested_categories(self, sale_entity_label_dict: dict):
        entity_key = self.__get_key_for_entity_label_dict__(sale_entity_label_dict)
        categories = self._access_layer_entity_category.get_existing_category_list(entity_key)
        return [] if categories == '' else categories.split(self._key_delimiter)

    def insert_entity_category(self, entity_key: str, category_string: str):
        start_date = MyDate.get_date_str_from_datetime()
        if self._access_layer_entity_category.is_entity_key_available(entity_key):
            return self._access_layer_entity_category.update_category_list(entity_key, category_string, start_date)
        else:
            data_dict = self._access_layer_entity_category.get_insert_dict_for_keys(
                entity_key, category_string, start_date)
            print('insert_entity_category: {}'.format(data_dict))
            return self._access_layer_entity_category.insert_data(data_dict)

    def __get_key_for_entity_label_dict__(self, sale_entity_label_dict: dict) -> str:
        entity_label_list = []
        for value, label in sale_entity_label_dict.items():
            if label in EL.get_labels_relevant_for_entity_category_key():
                entity_label_list.append('{}_{}'.format(label, value))
        return self._key_delimiter.join(sorted(entity_label_list))




