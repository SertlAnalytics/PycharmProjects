"""
Description: This module contains all named entities Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""


from tutti_constants import EL


class TuttiNamedEntity:
    def __init__(self):
        self._entity_names = self.__get_entity_names__()
        self._entity_synonym_dict = self.__get_synonym_dict__()

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


class TuttiCompanyEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return ['Apple', 'BMW', 'Crumpler', 'DeLonghi', 'Eames', 'GoPro', 'Nespresso', 'Lowa',
                'Grüezi-Bag',
                'Mercedes', 'Paidi', 'Samsung', 'USM', 'Schöffel',
                'Waldmann', 'Vitra', 'Zimstern', 'Zimtstern',
                'Villiger', 'Omega', 'Sunshine', 'Diono']

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Sunshine': ['Diono'],
            'Grüezi-Bag': ['Grüezi Bag']
        }


class TuttiTargetGroupEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return ['Frau', 'Frauen', 'Mann', 'Männer', 'Kind', 'Kinder', 'Baby', 'Babies']

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Frau': ['Frauen'],
            'Mann': ['Männer'],
            'Kind': ['Kinder'],
            'Baby': ['Babies'],
        }


class TuttiProductEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return ['MacBook', 'alu chair', 'aluminium chair', 'gtx', 'hero', 'Kid Cow',
                'meda', 'Monterey', 'Booster', 'pixie']

    @staticmethod
    def __get_synonym_dict__():
        return {
            'alu chair': ['aluminum chair']
        }


class TuttiObjectTypeEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return ['regal', 'tisch', 'schreibtisch', 'stuhl', 'bürostuhl', 'bürotisch', 'auto', 'fahrrad', 'velo',
                'corpus', 'kommunionskleid', 'notebook',
                'rollcontainer', 'besucherstuhl', 'schlafsack', 'chair', 'tasche']

    @staticmethod
    def __get_synonym_dict__():
        return {
            'fahrrad': ['velo'],
            'tisch': ['bürotisch'],
            'corpus': ['rollcontainer'],
            'stuhl': ['bürostuhl', 'besucherstuhl', 'chair', 'bürodrehstuhl', 'drehstuhl'],
            'kindersitz': ['autokindersitz', 'auto-kindersitz'],
            'notebook': ['laptop'],
            'umhängetasche': ['tasche'],
            'kommunionskleid': ['kommunionkleid'],
        }


class TuttiEntityHandler:
    @staticmethod
    def get_entity_names_for_entity_label(entity_label):
        return TuttiEntityHandler.get_entity_for_entity_label(entity_label).get_entity_names_for_phrase_matcher()

    @staticmethod
    def get_synonyms_for_entity_name(entity_label: str, entity_name: str) -> list:
        synonym_dict = TuttiEntityHandler.get_entity_for_entity_label(entity_label).entity_synonym_dict
        for key, value_list in synonym_dict.items():
            if key == entity_name.lower() or entity_name.lower() in value_list:
                result_list = list(value_list)
                result_list.append(entity_name.lower())
                return result_list
        return []

    @staticmethod
    def get_entity_for_entity_label(entity_type) -> TuttiNamedEntity:
        return {EL.COMPANY: TuttiCompanyEntity(),
                EL.PRODUCT: TuttiProductEntity(),
                EL.OBJECT: TuttiObjectTypeEntity(),
                EL.TARGET_GROUP: TuttiTargetGroupEntity()}.get(entity_type, TuttiCompanyEntity())




