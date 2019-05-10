"""
Description: This module contains all named entities for Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""


from salesman_tutti.tutti_constants import EL
from entities.named_entity import NamedEntity


class TargetGroupEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Dame', 'Damen',
            'Frau', 'Frauen',
            'Mann', 'Männer',
            'Lady',
            'Mädchen', 'Junge', 'Jungen',
            'Kind', 'Kinder',
            'Baby', 'Babies'
            'Büro',
            'Gewerbe',
            'Zuhause',
            'Privat', 'Arbeit',
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


class MaterialEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return ['Aluminium', 'Baumwolle', 'Leder', 'Kunstleder', 'Goretex', 'Stoff', 'Wolle', 'Porzellan']

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Goretex': ['GoreTex'],
        }


class TechnologyEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return ['WiFi', 'WLAN']

    @staticmethod
    def __get_synonym_dict__():
        return {
            'WiFi': ['WLAN'],
        }


class CompanyEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Apple', 'Audi',
            'BMW', 'Bally', 'Bugaboo', 'Big Max',
            'Crumpler', 'CANON', 'Canon',
            'DeLonghi', 'Dyson', 'Diono'
            'Eames', 'Even&Odd',
            'GoPro', 'Gucci', 'Grüezi-Bag', 'Grüezi Bag',
            'Hape', 'Hansen', 'H&M', 'Huawei',
            'IKEA',
            'Jacobsen',
            'Lowa', 'Louis Vuitton', 'Lladro', 'LUCAN',
            'Mercedes', 'Mercedes-Benz', 'Mango', 'Mexx',
            'Nespresso', 'name it',
            'Omega',
            'Paidi',
            'Risa', 'Range Rover',
            'Stokke', 'Samsung', 'Schöffel', 'Sunshine', 'Schuco', 'Skoda', 'Seat', 'Sunrise',
            'Tosca', 'Toyota',
            'USM',
            'Waldmann', 'Wilde+Spieth',
            'Villiger',  'Vitra', 'VW', 'Volkswagen',
            'Zimstern', 'Zimtstern', 'Zanotti',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Sunshine': ['Diono'],
            'Jacobsen': ['Jacobson'],
            'Grüezi-Bag': ['Grüezi Bag'],
            'Wilde+Spieth': ['Jacobsen'],
        }


class ProductEntity(NamedEntity):
    @staticmethod
    def __get_specific_entries__() -> list:
        return [
            [['hot', 'cool'], [' ', '+', ' + ', '&', ' & '], 'concatenate'],
            [['A', 'X', 'Z'], [1, 2, 3, 4, 5, 6, 7], 'add'],
            [['Serie'], [1, 2, 3, 4, 5, 6, 7], 'add', ['', ' ', '+']],
            [['A', 'B', 'C', 'E', 'X'], ['-Klasse', '-Class'], 'add'],
            [['GL'], ['A', 'B', 'C', 'E'], 'add'],
        ]

    @staticmethod
    def __get_entity_names__():
        return [
            'alu chair', 'aluminium chair',
            'Booster',
            'Cameleon',
            'EOS 700D',
            'gtx',
            'Hot + Cool', 'hero',
            'Kitos', 'Kid Cow',
            'Looking Good',
            'MacBook', 'meda', 'Monterey',
            'Pixie', 'Panama', 'Purpose Chair',
            'Roundabout',
            'sleepi', 'Silencio',
            'Velar',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'alu chair': ['aluminum chair'],
        }


class ObjectTypeEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Alufelgen','Auto', 'Autokindersitz', 'Auto-Kindersitz', 'Anhänger', 'Anzug',
            'Besucherstuhl', 'Babywanne', 'Bremsbeläge', 'Bürotisch', 'Bürostuhl',
            'Bürodrehstuhl', 'Bild', 'Buch', 'Badehose', 'Bikini',
            'Corpus',
            'Dusche', 'Drehstuhl', 'Drosselklappensensor', 'Drosselklappenschalter',
            'Digitalkamera',
            'Einstellwerkzeug', 'Endschalldämpfer', 'Entsorgung',
            'Felgen', 'Fahrzeuge',
            'Fleecejacke', 'Fahrrad', 'Figur', 'Figuren', 'Frontspoiler', 'Frontlippe', 'Frontlippen',
            'Gartenlehnstuhl', 'Gestell', 'Geschwisterkinderwagen', 'Gewindefahrwerk', 'Grill',
            'Golf-Bag',
            'Handtasche', 'Hängematte', 'Hut', 'Herbst-/Winterjacke', 'Herbst/Winterjacke', 'Hose',
            'Harlekin', 'Heckspoiler', 'Hotspot',
            'Inspektion',
            'Jacke', 'Jeans', 'Jeanshose',
            'Kommunionkleid', 'Kinderwagen', 'Kinderbett', 'Kugelbahn', 'Kostüm', 'Kostüme', 'Kleid',
            'Kupplungsscheibe', 'Kühlergrill', 'Kühlmittelpumpe', 'Kinderzimmer', 'Kleidung', 'Kinderschuhe',
            'Laptop', 'Lift', 'LTE-Router'
            'Nebelleuchte', 'Notebook', 'NannoSim',
            'Matraze', 'Matrazen', 'Matratzenboden', 'Marionette', 'Modell', 'Modellauto', 'Möbellift',
            'Motorenöl', 'Motoröl', 'Motor', 'Mitfahrgelegenheit', 'MicroSim',
            'Overall',
            'Porzellanfigur', 'Porzellanfiguren', 'Puppe', 'Pullover',
            'Rettungsweste', 'Roman', 'Ratgeber', 'Router',
            'Rollcontainer', 'Reifen', 'Räder', 'Regal', 'Regenschutz', 'Rucksack', 'Rock', 'Rahmen',
            'Schlafsack', 'Service', 'Scheibenwischer', 'Sachbuch',
            'Schlüssel', 'Schlüsselanhänger', 'Scheibenbremsbeläge', 'Strickdecke', 'Stehleuchte', 'Ski',
            'Schreibtisch', 'Stuhl', 'Stühle', 'Scheinwerfer', 'Stossstange', 'Skijacke', 'Ski/Winterjacke',
            'Sommerkleid', 'Sonnenschirm', 'Sommerhut', 'Sonnenhut', 'Strohhut', 'Schuh', 'Schuhe',
            'Sportauspuff', 'Spielzeugautos', 'Schlafsofa', 'Sommerreifen', 'Stehtisch', 'Sitzungstisch',
            'Turnschuhe', 'Tisch', 'Toilette', 'Tasche', 'Transport', 'Taxi',
            'Umhängetasche', 'Übergangsjacke', 'Umzug',
            'Velo',
            'Winterräder', 'Winterreifen', 'Winterkompletträder', 'Wanne', 'Wasserpumpe',
            'Werkzeugkasten', 'Winterjacke', 'Winterschuhe', 'Wohnmobil',
            'Zeitwerkzeug', 'Zeitsteuerung'
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Fahrrad': ['Velo'],
            'LTE-Router': ['Router'],
            'Jeans': ['Jeanshose'],
            'Sommerhut': ['Sonnenhut', 'Strohhut'],
            'Corpus': ['Rollcontainer'],
            'Bürostuhl': ['Besucherstuhl', 'Bürodrehstuhl', 'Drehstuhl'],
            'Kindersitz': ['Autokindersitz', 'Auto-Kindersitz'],
            'Notebook': ['Laptop'],
            'Kommunionkleid': ['Sommerkleid'],
            'Winterjacke': ['Herbst-/Winterjacke', 'Herbst/Winterjacke', 'Ski/Winterjacke', 'Übergangsjacke'],
        }


class SalesmanEntityHandler:
    @staticmethod
    def get_entity_names_for_entity_label(entity_label):
        return SalesmanEntityHandler.get_entity_for_entity_label(entity_label).get_entity_names_for_phrase_matcher()

    @staticmethod
    def get_synonyms_for_entity_name(entity_label: str, entity_name: str) -> list:
        # print('get_synonyms_for_entity_name: entity_label={}, entity_name={}'.format(entity_label, entity_name))
        synonym_dict = SalesmanEntityHandler.get_entity_for_entity_label(entity_label).entity_synonym_dict
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
    def get_entity_for_entity_label(entity_label: str) -> NamedEntity:
        return {
            EL.COMPANY: CompanyEntity(),
            EL.PRODUCT: ProductEntity(),
            EL.OBJECT: ObjectTypeEntity(),
            EL.TARGET_GROUP: TargetGroupEntity(),
            EL.MATERIAL: MaterialEntity(),
            EL.TECHNOLOGY: TechnologyEntity(),
        }.get(entity_label, CompanyEntity())



