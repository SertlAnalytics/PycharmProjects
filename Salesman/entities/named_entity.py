"""
Description: This module contains the base NamedEntity class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""


class NamedEntity:
    def __init__(self):
        self._entity_names = self.__get_entity_names__()
        self.__add_specific_entries_to_entity_names__()
        self._entity_synonym_dict = self.__get_synonym_dict__()
        self.__add_specific_entries_to_entity_synonym_dict__()
        # print('\nEntity_names: {}'.format(self._entity_names))
        # print('\nEntity_synonym_dict: {}'.format(self._entity_synonym_dict))

    def get_entity_names_for_phrase_matcher(self):
        default_list = self._entity_names
        lower_case_list = [entity_name.lower() for entity_name in default_list]
        upper_case_list = [entity_name.upper() for entity_name in default_list]
        capitalized_list = [entity_name.capitalize() for entity_name in default_list]
        summary_list = list(set(default_list + lower_case_list + upper_case_list + capitalized_list))
        return sorted(summary_list)

    @property
    def entity_synonym_dict(self):
        return self._entity_synonym_dict

    @staticmethod
    def __get_entity_names__():
        return []

    @staticmethod
    def __get_synonym_dict__() -> dict:
        return {}

    @staticmethod
    def __get_specific_entries__() -> list:
        return []

    def __add_specific_entries_to_entity_names__(self):
        specific_entries = self.__get_specific_entries__()
        for specific_entry in specific_entries:
            process_type = specific_entry[2]
            if process_type == 'concatenate':
                word_list = specific_entry[0]
                conjunction_list = specific_entry[1]  # like [' ', '+', ' + ', '&', ' & ']
                for changed_word_list in self.__get_word_list_as_list__(word_list):
                    for conjunction in conjunction_list:
                        self._entity_names.append('{}'.format(conjunction).join(changed_word_list))
            elif process_type == 'add':
                left_word_list = specific_entry[0]
                right_word_list = specific_entry[1]
                delimiter_list = [''] if len(specific_entry) <= 3 else specific_entry[3]  # like [' ', '+', ' + ']
                for left_word in left_word_list:
                    for right_word in right_word_list:
                        for delimiter in delimiter_list:
                            self._entity_names.append('{}{}{}'.format(left_word, delimiter, right_word))

    def __get_word_list_as_list__(self, word_list: list):
        return [[word.lower() for word in word_list], [word.capitalize() for word in word_list]]

    def __add_specific_entries_to_entity_synonym_dict__(self):
        specific_entries = self.__get_specific_entries__()
        for specific_entry in specific_entries:
            word_list = specific_entry[0]
            conjunction_list = specific_entry[1]
            process_type = specific_entry[2]
            if process_type == 'concatenate':
                key = ''
                synonym_list = []
                for changed_word_list in self.__get_word_list_as_list__(word_list):
                    for conjunction in conjunction_list:
                        value = '{}'.format(conjunction).join(changed_word_list)
                        if key == '':
                            key = value
                        else:
                            synonym_list.append(value)
                self._entity_synonym_dict[key] = synonym_list

