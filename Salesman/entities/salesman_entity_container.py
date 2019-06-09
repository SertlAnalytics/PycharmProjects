"""
Description: This module contains the entity information for a sale
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from entities.salesman_entity_handler import SalesmanEntityHandler
from sertl_analytics.constants.salesman_constants import EL
import itertools


class SalesmanEntityContainer:
    """
    This class has two main purposes:
    1. Manage entities: add_entity_label_with_value
    2. Create search lists:
    2.a) __get_entity_search_lists_for_base_level__: The first level contains of company, product and all other relevant
    2.b) __add_other_levels_to_entity_based_search_lists_dict__: We reduce the search labels by one for each level
    ToDo: Find an algorithm to identify the best level to start the search with... (Entropy?)
    """
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
        # some lists for the search entities
        self._company_main_names = []
        self._product_main_names = []
        self._detail_main_names = []    # consists of the label names for object and some other labels

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
        self._company_main_names = self._entity_label_main_values_dict.get(EL.COMPANY, [])
        self._product_main_names = self._entity_label_main_values_dict.get(EL.PRODUCT, [])
        self._detail_main_names = self.__get_detail_main_names__()

    def __get_detail_main_names__(self):
        return_list = []
        entity_detail_list = [EL.OBJECT, EL.ANIMAL, EL.CLOTHES, EL.TARGET_GROUP]
        for entity_label in entity_detail_list:
            for entry in self._entity_label_main_values_dict.get(entity_label, []):
                return_list.append(entry)
        return return_list

    def compute_entity_based_search_lists(self):
            self._information_score_list = sorted(self._information_score_list, reverse=True)
            self._information_score_entity_labels_dict = {
                score: sorted(entities) for score, entities in self._information_score_entity_labels_dict.items()}
            self.__fill_entity_names_with_score_one__()
            self._level_entity_based_search_lists_dict[0] = self.__get_entity_search_lists_dict_for_base_level__()
            self.__add_other_levels_to_entity_based_search_lists_dict__()
            self.print_details()

    def print_details(self):
        print('_search_levels={}'.format(self._search_levels))
        print('_information_score_list: {}'.format(self._information_score_list))
        print('_information_score_entity_labels_dict: {}'.format(self._information_score_entity_labels_dict))
        print('_level_entity_based_search_lists_dict={}'.format(self._level_entity_based_search_lists_dict))

    def get_entity_list_by_entity_label(self, entity_label: str):
        return self._entity_label_main_values_dict.get(entity_label, [])

    def get_entity_based_search_lists(self, level: int) -> list:
        search_lists = []
        for idx, dict_lists in self._level_entity_based_search_lists_dict[level].items():
            for dict_list in dict_lists:
                search_lists.append(dict_list)
        for main_value, synonyms in self._entity_main_synonyms_dict.items():
            if len(synonyms) > 0:
                for synonym in synonyms:
                    search_lists = self.__adjust_search_lists_by_synonym__(search_lists, main_value, synonym)
        return search_lists

    def get_entity_based_search_strings_as_list(self, level: int) -> list:
        entity_based_search_lists_for_level = self._level_entity_based_search_lists_dict[level]
        return [' '.join(search_list) for search_list in entity_based_search_lists_for_level]

    def __add_other_levels_to_entity_based_search_lists_dict__(self):
        for level in range(1, len(self._entity_names_with_score_one) + 1):
            entity_based_search_lists_dict = {}
            any_list_was_changed = False
            for idx, base_lists in self._level_entity_based_search_lists_dict[0].items():
                if len(base_lists[0]) - level < 2:
                    entity_based_search_lists_dict[idx] = base_lists
                else:
                    any_list_was_changed = True
                    entity_based_search_lists_dict[idx] = []
                    if level == 1:
                        comb_list = [[value] for value in self._entity_names_with_score_one]
                    else:
                        comb = itertools.combinations(self._entity_names_with_score_one, level)
                        comb_list = list(comb)
                    for base_list in base_lists:
                        for value_list in comb_list:
                            new_list = list(base_list)
                            for value in value_list:
                                new_list.remove(value)
                            entity_based_search_lists_dict[idx].append(new_list)
            if any_list_was_changed:
                self._search_levels.append(level)
                self._level_entity_based_search_lists_dict[level] = entity_based_search_lists_dict
                print('level={}, self._level_entity_based_search_lists_dict[level]={}'.format(
                    level, entity_based_search_lists_dict))
            else:
                return

    def __get_entity_search_lists_dict_for_base_level__(self) -> dict:
        base_lists_dict = {}
        if len(self._company_main_names) > 0 and len(self._product_main_names) > 0:
            base_lists_dict['C_P_O'] = list(itertools.product(self._company_main_names, self._product_main_names))
        elif len(self._company_main_names) == 0 and len(self._product_main_names) == 0:
            base_lists_dict['O'] = [self._detail_main_names]
        elif len(self._company_main_names) > 0:
            base_lists_dict['C_O'] = [[company] for company in self._company_main_names]
        elif len(self._product_main_names) > 0:
            base_lists_dict['P_O'] = [[product] for product in self._product_main_names]

        for idx, dict_list in base_lists_dict.items():
            base_lists_dict[idx] = [list(entry) for entry in dict_list]

        print('entity_label_main_values_dict={}'.format(self._entity_label_main_values_dict))
        print('base_lists_dict={}'.format(base_lists_dict))
        for idx, base_lists in base_lists_dict.items():
            if idx != 'O':
                self.__add_lowest_score_entity_values_to_base_list__(base_lists)
        print('base_lists_dict (after adding others={}'.format(base_lists_dict))
        return base_lists_dict

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
        for search_list in search_lists_input:  # check if synonym is already available
            if synonym in search_list:
                return search_lists_input
        search_lists_output = list(search_lists_input)
        for search_list in search_lists_input:
            if main_value in search_list:
                idx_main_value = search_list.index(main_value)
                if idx_main_value >= 0:
                    search_list_output = list(search_list)
                    search_list_output[idx_main_value] = synonym
                    search_lists_output.append(search_list_output)
        return search_lists_output


