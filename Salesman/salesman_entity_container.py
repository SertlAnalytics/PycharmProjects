"""
Description: This module contains the entity information for a sale
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from entities.salesman_entity_handler import SalesmanEntityHandler


class SalesmanEntityContainer:
    def __init__(self, entity_handler: SalesmanEntityHandler):
        self._entity_handler = entity_handler
        self._entity_labels = []
        self._entity_names = []
        self._entity_label_main_values_dict = {}  # contains entities with {value: label, value: label}
        self._entity_main_synonyms_dict = {}

    @property
    def entity_names(self) -> list:
        return sorted(self._entity_names)

    @property
    def entity_labels(self) -> list:
        return sorted(self._entity_labels)

    @property
    def entity_label_main_values_dict(self):
        return {label: sorted(self._entity_label_main_values_dict[label]) for label in self.entity_labels}

    def get_entity_label_main_values_dict_as_string(self) -> str:
        return '; '.join(
            ['{}: {}'.format(label, ','.join(values)) for label, values in self.entity_label_main_values_dict.items()])

    def add_entity_label_with_value(self, label: str, value: str):
        if label not in self._entity_labels:
            self._entity_labels.append(label)
            self._entity_label_main_values_dict[label] = []

        value_main = self._entity_handler.get_main_entity_name_for_entity_name(label, value)
        if value_main not in self._entity_names:
            self._entity_names.append(value_main)
            self._entity_label_main_values_dict[label].append(value_main)
            self._entity_main_synonyms_dict[value_main] = \
                self._entity_handler.get_synonyms_for_entity_name(label, value_main)

    def get_entity_list_by_entity_label(self, entity_label: str):
        return self._entity_label_main_values_dict.get(entity_label, [])

    def get_entity_list_by_entity_label_list(self, entity_label_list: list):
        return_list = []
        for entity_label in entity_label_list:
            return_list += self.get_entity_list_by_entity_label(entity_label)
        return return_list

    def get_entity_based_search_lists(self) -> list:
        search_lists = [self.__get_entity_base_search_list__()]
        for main_value, synonyms in self._entity_main_synonyms_dict.items():
            if len(synonyms) > 0:
                for synonym in synonyms:
                    search_lists = self.__adjust_search_lists_by_synonym__(search_lists, main_value, synonym)
        return search_lists

    def get_entity_based_search_strings_as_list(self) -> list:
        return [' '.join(search_list) for search_list in self.get_entity_based_search_lists()]

    def __get_entity_base_search_list__(self) -> list:
        entity_names_list = []
        for label, values in self.entity_label_main_values_dict.items():
            for value in values:
                entity_names_list.append(value)
        return entity_names_list

    @staticmethod
    def __adjust_search_lists_by_synonym__(search_lists_input: list, main_value: str, synonym: str) -> list:
        search_lists_output = list(search_lists_input)
        for search_list in search_lists_input:
            if main_value in search_list:
                idx_main_value = search_list.index(main_value)
                if idx_main_value >= 0:
                    search_list_output = list(search_list)
                    search_list_output[idx_main_value] = synonym
                    search_lists_output.append(search_list_output)
        return search_lists_output


