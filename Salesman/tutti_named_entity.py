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


class TuttiMaterialEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return ['Aluminium', 'Baumwolle', 'Leder', 'Kunstleder', 'Goretex', 'Stoff', 'Wolle']

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Goretex': ['GoreTex'],
        }


class TuttiCompanyEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return ['Apple', 'BMW', 'Crumpler',
                'DeLonghi', 'Dyson',
                'Eames',
                'GoPro', 'Gucci',
                'Hape', 'Nespresso',
                'IKEA',
                'Lowa', 'Louis Vuitton',
                'name it',
                'Grüezi-Bag', 'Grüezi Bag',
                'Jacobsen', 'Hansen', 'Mango', 'Even&Odd', 'Bally', 'Zanotti', 'Tosca', 'H&M',
                'Mercedes', 'Paidi', 'Risa', 'Samsung', 'USM', 'Schöffel',
                'Waldmann', 'Vitra', 'Zimstern', 'Zimtstern',
                'Villiger', 'Omega', 'Sunshine', 'Diono']

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Sunshine': ['Diono'],
            'Jacobsen': ['Jacobson'],
            'Grüezi-Bag': ['Grüezi Bag']
        }


class TuttiTargetGroupEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Dame', 'Damen',
            'Frau', 'Frauen',
            'Mann', 'Männer',
            'Mädchen', 'Junge', 'Jungen',
            'Kind', 'Kinder',
            'Baby', 'Babies'
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Frau': ['Dame'],
            'Frauen': ['Damen'],
            'Mann': ['Männer'],
            'Kind': ['Kinder'],
            'Junge': ['Jungen'],
            'Baby': ['Babies'],
            'Lady': ['Mädchen'],
        }


class TuttiProductEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A8',
            'Booster',
            'hot cool', 'hot+cool', 'hot + cool', 'Hot+Cool', 'Hot&Cool', 'Hot Cool', 'Hot & Cool', 'hot & cool',
            'Hot + Cool',
            'Kitos',
            'MacBook', 'alu chair', 'aluminium chair', 'gtx', 'hero', 'Kid Cow', 'Roundabout',
            'meda', 'Monterey',
            'Pixie', 'Panama',
            'X1','X3','X5','X7',
            'Z3','Z3',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'alu chair': ['aluminum chair'],
            'hot cool': ['hot+cool', 'hot + cool', 'Hot Cool', 'Hot+Cool',
                         'Hot&Cool', 'Hot & Cool', 'hot & cool', 'Hot + Cool'],
        }


class TuttiObjectTypeEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Alufelgen','Auto', 'Autokindersitz', 'Auto-Kindersitz',
            'Besucherstuhl', 'Babywanne', 'Bremsbeläge', 'Bürotisch', 'Bürostuhl', 'Büro',
            'Bürodrehstuhl',
            'Corpus', 'Chair',
            'Dusche', 'Drehstuhl',
            'Einstellwerkzeug',
            'Fleecejacke', 'Fahrrad',
            'Gartenlehnstuhl', 'Gestell',
            'Handtasche', 'Hängematte', 'Hut', 'Herbst-/Winterjacke', 'Herbst/Winterjacke',
            'Jacke',
            'Kommunionkleid', 'Kinderwagen', 'Kinderbett', 'Kugelbahn',
            'Laptop',
            'Nebelleuchte', 'Notebook',
            'Matraze', 'Matrazen',
            'Rollcontainer', 'Reifen', 'Räder', 'Regal', 'Regenschutz', 'Rucksack',
            'Schlafsack', 'Tasche',
            'Schlüssel', 'Schlüsselanhänger', 'Scheibenbremsbeläge', 'Strickdecke', 'Stehleuchte', 'Ski',
            'Schreibtisch', 'Stuhl', 'Stühle', 'Scheinwerfer', 'Stossstange', 'Skijacke', 'Ski/Winterjacke',
            'Sommerkleid', 'Sonnenschirm', 'Sommerhut', 'Sonnenhut', 'Strohhut', 'Schuh', 'Schuhe',
            'Turnschuhe', 'Tisch', 'Toilette',
            'Umhängetasche',
            'Velo',
            'Winterräder', 'Winterreifen', 'Winterkompletträder',
            'Werkzeugkasten', 'Winterjacke', 'Winterschuhe',
            'Zeitwerkzeug', 'Zeitsteuerung'
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Fahrrad': ['Velo'],
            'Sommerhut': ['Sonnenhut', 'Strohhut'],
            'Stuhl': ['Chair', 'Stühle'],
            'Corpus': ['Rollcontainer'],
            'Bürostuhl': ['Besucherstuhl', 'Bürodrehstuhl', 'Drehstuhl'],
            'Kindersitz': ['Autokindersitz', 'Auto-Kindersitz'],
            'Notebook': ['Laptop'],
            'Kommunionkleid': ['Sommerkleid'],
            'Winterjacke': ['Herbst-/Winterjacke', 'Herbst/Winterjacke', 'Ski/Winterjacke'],
        }


class TuttiEntityHandler:
    @staticmethod
    def get_entity_names_for_entity_label(entity_label):
        return TuttiEntityHandler.get_entity_for_entity_label(entity_label).get_entity_names_for_phrase_matcher()

    @staticmethod
    def get_synonyms_for_entity_name(entity_label: str, entity_name: str) -> list:
        # print('get_synonyms_for_entity_name: entity_label={}, entity_name={}'.format(entity_label, entity_name))
        synonym_dict = TuttiEntityHandler.get_entity_for_entity_label(entity_label).entity_synonym_dict
        for key, synonym_list in synonym_dict.items():
            synonym_list_lower = [synonym.lower() for synonym in synonym_list]
            if key.lower() == entity_name.lower():
                return list(synonym_list)
            elif entity_name.lower() in synonym_list_lower:
                result_list = list(synonym_list)
                result_list.append(key)
                if entity_name in result_list:
                    result_list.remove(entity_name)
                return result_list
        return []

    @staticmethod
    def get_entity_for_entity_label(entity_label: str) -> TuttiNamedEntity:
        return {EL.COMPANY: TuttiCompanyEntity(),
                EL.PRODUCT: TuttiProductEntity(),
                EL.OBJECT: TuttiObjectTypeEntity(),
                EL.TARGET_GROUP: TuttiTargetGroupEntity(),
                EL.MATERIAL: TuttiMaterialEntity()}.get(entity_label, TuttiCompanyEntity())




