"""
Description: This module contains the value categorizer class which is used as base for option lists.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-02
"""

from sertl_analytics.my_text import MyText


class ValueCategorizer:
    def __init__(self):
        self._category_list = self.__get_category_list__()
        self._category_value_dict = self.__get_category_value_dict__()
        self._value_category_dict = {self._category_value_dict[label]: label for label in self._category_value_dict}
        self._category_sub_category_value_dict = {}  # serves as cache for subcategories

    def get_category_value_list(self):
        return [[label, self._category_value_dict[label]] for label in self._category_list]

    def get_category_value_list_as_option_list(self):
        return [{'label': cat, 'value': self._category_value_dict[cat]} for cat in self._category_list]

    def get_category_for_value(self, value: str):
        value_lower = value.lower()
        return self._value_category_dict.get(value_lower, value_lower.capitalize())

    def get_sub_category_for_value(self, category: str, sub_category_value: str):
        sub_category_lists = self.get_sub_category_lists_for_category(category)
        for sub_category_list in sub_category_lists:
            if sub_category_list[1] == sub_category_value:
                return sub_category_list[0]
        sub_category = sub_category_value.lower().replace('-', ' & ', 1)
        return sub_category.capitalize()

    def get_sub_category_value_for_sub_category(self, category: str, sub_category: str):
        if sub_category == '':
            return ''
        sub_category_lists = self.get_sub_category_lists_for_category(category)
        for sub_category_list in sub_category_lists:
            if sub_category_list[0] == sub_category:
                return sub_category_list[1]
        return sub_category.lower().replace(' & ', '-')

    def get_sub_category_lists_for_category(self, category: str):
        return self.__get_sub_category_lists_for_category__(category)

    def get_sub_category_lists_for_category_as_option_list(self, category: str):
        sub_category_list = self.get_sub_category_lists_for_category(category)
        return [{'label': value_list[0], 'value': value_list[1]} for value_list in sub_category_list]

    def get_value_for_category(self, category: str):
        return self._category_value_dict.get(category, self.__get_default_value_for_category__())

    @staticmethod
    def __get_category_list__():
        pass

    @staticmethod
    def __get_category_value_dict__() -> dict:
        pass

    @staticmethod
    def __get_default_value_for_category__():
        pass

    def __get_sub_category_lists_for_category__(self, category: str):
        if category not in self._category_sub_category_value_dict:
            self._category_sub_category_value_dict[category] = []
            sub_categories = self.__get_sub_category_list_for_category__(category)
            for sub_category in sub_categories:
                sub_value = MyText.get_with_replaced_umlaute(sub_category.lower())
                sub_value = sub_value.replace(' & ', '-')
                self._category_sub_category_value_dict[category].append([sub_category, sub_value])
        return self._category_sub_category_value_dict[category]

    @staticmethod
    def __get_sub_category_list_for_category__(category: str):
        return []

