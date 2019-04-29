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
        return ['Baumwolle', 'Leder', 'Kunstleder', 'Goretex', 'Stoff', 'Wolle']

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
                'Grüezi-Bag', 'Jacobsen', 'Hansen', 'Mango', 'Even&Odd', 'Bally', 'Zanotti', 'Tosca', 'H&M',
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
        return ['Dame', 'Damen', 'Frau', 'Frauen', 'Mann', 'Männer',
                'Mädchen', 'Jungen',
                'Kind', 'Kinder', 'Baby', 'Babies']

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Frau': ['Dame'],
            'Frauen': ['Damen'],
            'Dame': ['Frau'],
            'Damen': ['Frauen'],
            'Mann': ['Männer'],
            'Kind': ['Kinder'],
            'Baby': ['Babies'],
            'Lady': ['Mädchen'],
        }


class TuttiProductEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return ['MacBook', 'alu chair', 'aluminium chair', 'gtx', 'hero', 'Kid Cow', 'Roundabout',
                'meda', 'Monterey', 'Booster', 'pixie', 'hot & cool', 'X3', 'Panama', 'Kitos']

    @staticmethod
    def __get_synonym_dict__():
        return {
            'alu chair': ['aluminum chair'],
            'hot & cool': ['hot+cool', 'hot + cool'],
        }


class TuttiObjectTypeEntity(TuttiNamedEntity):
    @staticmethod
    def __get_entity_names__():
        return ['Alufelgen','auto',
                'Bremsbeläge', 'bürotisch', 'Bürostuhl', 'Büro',
                'corpus', 'fleecejacke', 'hut', 'kugelbahn', 'dusche', 'toilette',
                'Einstellwerkzeug',
                'Gartenlehnstuhl', 'Gestell',
                'Hängematte',
                'Kinderbett',
                'Matraze', 'Matrazen',
                'regal', 'tisch', 'schreibtisch', 'stuhl', 'stühle',
                'winterschuhe', 'handtasche', 'nebelleuchte', 'scheinwerfer', 'stossstange',
                'fahrrad', 'velo', 'kinderwagen', 'regenschutz', 'rucksack', 'ski',
                'kommunionskleid', 'notebook', 'jacke', 'Skijacke', 'sonnenschirm', 'babywanne',
                'rollcontainer', 'besucherstuhl', 'schlafsack', 'chair', 'tasche',
                'Reifen', 'Räder',
                'schlüssel', 'schlüsselanhänger', 'Scheibenbremsbeläge', 'Strickdecke', 'Stehleuchte',
                'Turnschuhe',
                'Winterräder', 'Winterreifen', 'Winterkompletträder',
                'Werkzeugkasten', 'Winterjacke',
                'Zeitwerkzeug', 'Zeitsteuerung']

    @staticmethod
    def __get_synonym_dict__():
        return {
            'fahrrad': ['velo'],
            'hut': ['sonnenhut', 'strohhut'],
            'stuhl': ['chair', 'stühle'],
            'corpus': ['rollcontainer'],
            'bürostuhl': ['besucherstuhl', 'bürodrehstuhl', 'drehstuhl'],
            'kindersitz': ['autokindersitz', 'auto-kindersitz'],
            'notebook': ['laptop'],
            'umhängetasche': ['tasche'],
            'kommunionskleid': ['kommunionkleid'],
            'stossstange': ['stoßstange']
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
                EL.TARGET_GROUP: TuttiTargetGroupEntity(),
                EL.MATERIAL: TuttiMaterialEntity()}.get(entity_type, TuttiCompanyEntity())




