"""
Description: This module contains the entity information for a sale
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from entities.salesman_entity_handler import SalesmanEntityHandler
import itertools


class SalesmanEntityContainer:
    def __init__(self, entity_handler: SalesmanEntityHandler):
        self._entity_handler = entity_handler
        self._entity_labels = []
        self._entity_names = []
        self._entity_names_lower = []
        self._entity_main_names = []
        self._entity_main_names_lower = []
        self._entity_label_values_dict = {}  # contains entities with {label: [value1, value2], label: [...]}
        self._entity_label_main_values_dict = {}  # contains entities with {label: [value1, value2], label: [...]}
        self._entity_main_synonyms_dict = {}
        self._entity_names_with_score_one = []
        # some properties for managing searches
        self._search_levels = [0]
        self._information_score_list = []
        self._information_score_entity_labels_dict = {}
        self._level_entity_based_search_lists_dict = {}

    @property
    def search_levels(self) -> list:
        return self._search_levels

    @property
    def entity_names(self) -> list:
        return sorted(self._entity_names)

    @property
    def entity_labels(self) -> list:
        return sorted(self._entity_labels)

    @property
    def entity_label_values_dict(self):
        return {label: sorted(self._entity_label_values_dict[label]) for label in self.entity_labels}

    @property
    def entity_label_main_values_dict(self) -> dict:
        return self._entity_label_main_values_dict

    def get_entity_label_values_dict_as_string(self):
        return '; '.join(
            ['{}: {}'.format(label, ', '.join(values)) for label, values in self.entity_label_values_dict.items()])

    def get_entity_label_main_values_dict_as_string(self) -> str:
        return '; '.join(
            ['{}: {}'.format(label, ', '.join(values)) for label, values in self._entity_label_main_values_dict.items()])

    def add_entity_label_with_value(self, label: str, value: str):
        if label not in self._entity_labels:
            self._entity_labels.append(label)
            self._entity_label_values_dict[label] = []
            self._entity_label_main_values_dict[label] = []
            information_score_for_label = self._entity_handler.get_similarity_score_for_entity_label(label)
            if information_score_for_label not in self._information_score_list:
                self._information_score_list.append(information_score_for_label)
                self._information_score_entity_labels_dict[information_score_for_label] = []
            self._information_score_entity_labels_dict[information_score_for_label].append(label)

        if value.lower() not in self._entity_names_lower:
            self._entity_names.append(value)
            self._entity_names_lower.append(value.lower())
            self._entity_label_values_dict[label].append(value)

            value_main = self._entity_handler.get_main_entity_name_for_entity_name(label, value)
            if value_main.lower() not in self._entity_main_names_lower:
                self._entity_main_names.append(value_main)
                self._entity_main_names_lower.append(value_main.lower())
                self._entity_label_main_values_dict[label].append(value_main)
                self._entity_main_synonyms_dict[value_main] = \
                    self._entity_handler.get_synonyms_for_entity_name(label, value_main)

    def finish_entity_based_parameters(self):
        self._entity_label_main_values_dict = \
            {label: sorted(self._entity_label_main_values_dict[label]) for label in self.entity_labels}

    def compute_entity_based_search_lists(self):
        self._information_score_list = sorted(self._information_score_list, reverse=True)
        self._information_score_entity_labels_dict = {
            score: sorted(entities) for score, entities in self._information_score_entity_labels_dict.items()}
        self.__fill_entity_names_with_score_one__()
        self._level_entity_based_search_lists_dict[0] = self.__get_entity_search_lists_for_base_level__()
        self.__add_other_levels_to_entity_based_search_lists_dict__()
        self.print_details()

    def print_details(self):
        print('_information_score_list: {}'.format(self._information_score_list))
        print('_information_score_entity_labels_dict: {}'.format(self._information_score_entity_labels_dict))
        print('_level_entity_based_search_lists_dict[0]={}'.format(self._level_entity_based_search_lists_dict[0]))

    def get_entity_list_by_entity_label(self, entity_label: str):
        return self._entity_label_main_values_dict.get(entity_label, [])

    def get_entity_based_search_lists(self, level: int) -> list:
        search_lists = self._level_entity_based_search_lists_dict[level]
        for main_value, synonyms in self._entity_main_synonyms_dict.items():
            if len(synonyms) > 0:
                for synonym in synonyms:
                    search_lists = self.__adjust_search_lists_by_synonym__(search_lists, main_value, synonym)
        return search_lists

    def get_entity_based_search_strings_as_list(self, level: int) -> list:
        entity_based_search_lists_for_level = self._level_entity_based_search_lists_dict[level]
        return [' '.join(search_list) for search_list in entity_based_search_lists_for_level]

    def __add_other_levels_to_entity_based_search_lists_dict__(self):
        base_lists = list(self._level_entity_based_search_lists_dict[0])
        base_list_entry_length = len(base_lists[0])  # all elements in this list have the same length - we take the 1st
        max_level = min(len(self._entity_names_with_score_one), base_list_entry_length - 2)
        print('Max_level = {}'.format(max_level))
        for level in range(1, max_level + 1):
            self._search_levels.append(level)
            level_lists = []
            if level == 1:
                comb_list = [[value] for value in self._entity_names_with_score_one]
            else:
                comb = itertools.combinations(self._entity_names_with_score_one, level)
                comb_list = list(comb)
            print('comb for level {}: {}'.format(level, comb_list))
            for base_list in base_lists:
                for value_list in comb_list:
                    new_list = list(base_list)
                    for value in value_list:
                        new_list.remove(value)
                    level_lists.append(new_list)
            self._level_entity_based_search_lists_dict[level] = level_lists
        for level, search_lists in self._level_entity_based_search_lists_dict.items():
            print('search_lists_{}: {}'.format(level, search_lists))

    def __get_entity_search_lists_for_base_level__(self) -> list:
        print('entity_label_main_values_dict={}'.format(self._entity_label_main_values_dict))
        higher_score_list = []
        for score, label_list in self._information_score_entity_labels_dict.items():
            if score > 1:
                for label in label_list:
                    higher_score_list.append(self._entity_label_main_values_dict[label])
        if len(higher_score_list) == 0:
            base_lists = [[]]
        elif len(higher_score_list) == 1:
            base_lists = [higher_score_list[0]]
        elif len(higher_score_list) == 2:
            base_lists = list(itertools.product(higher_score_list[0], higher_score_list[1]))
        elif len(higher_score_list) == 3:
            base_lists = list(itertools.product(higher_score_list[0], higher_score_list[1], higher_score_list[2]))
        else:
            base_lists = list(itertools.product(higher_score_list[0], higher_score_list[1],
                                                higher_score_list[2], higher_score_list[3]))
        base_lists = [list(value) for value in base_lists]
        self.__add_lowest_score_entity_values_to_base_list__(base_lists)
        return base_lists

    def __fill_entity_names_with_score_one__(self):
        for label in self._information_score_entity_labels_dict.get(1, []):
            for value in self._entity_label_main_values_dict[label]:
                self._entity_names_with_score_one.append(value)

    def __add_lowest_score_entity_values_to_base_list__(self, base_list: list):
        for value in self._entity_names_with_score_one:
            for single_list in base_list:
                single_list.append(value)

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


