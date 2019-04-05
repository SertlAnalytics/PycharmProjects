"""
Description: This module contains all named entities Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""


class TuttiNamedEntity:
    def __init__(self):
        self._entity_names = self.__get_entity_names__()

    def get_entity_names_for_phrase_matcher(self):
        default_list = self._entity_names
        lower_case_list = [entity_name.lower() for entity_name in default_list]
        upper_case_list = [entity_name.upper() for entity_name in default_list]
        capitalized_list = [entity_name.capitalize() for entity_name in default_list]
        summary_list = list(set(default_list + lower_case_list + upper_case_list + capitalized_list))
        return sorted(summary_list)

    @staticmethod
    def __get_entity_names__():
        return []


class TuttiCompanyEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return ['Eames', 'Lowa', 'USM', 'Zimtstern', 'BMW', 'Mercedes', 'Waldmann']


class TuttiProductEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return ['alu chair', 'gtx']


