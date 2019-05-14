"""
Description: This module contains all named entities for Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""


from salesman_tutti.tutti_constants import EL
from entities.named_entity import NamedEntity


class BlackListEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Belieben', 'B x L', 'B x H', 'B x T x H', 'Beliebte',
            'Extra', 'Entspannen',
            'Grosses', 'Grössen', 'Gemäss',
            'Herzenslust', 'Holzdicke',
            'Link', 'Lust', 'L x', 'Laune', 'LxBxH', 'Lieblinge',
        ]


class AnimalEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Aal',
            'Chinchillas',
            'Esel',
            'Forelle', 'Forellen', 'Frettchen',
            'Goldfisch', 'Goldfische', 'Garnele', 'Garnelen','Graupapageien',
            'Hund', 'Hamster', 'Haustiere',
            'Katze', 'Kätzchen', 'Kater', 'Karpfen', 'Krebs', 'Krebse', 'Kleintier',
            'Maus', 'Meerschweinchen',
            'Nager',
            'Pferd', 'Papagei',
            'Stör', 'Streifenhörnchen',
            'Teddyhamster',
            'Zwerghamster',
            'Welse',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Katze': ['Kater'],
            'Hamster': ['Teddyhamster', 'Zwerghamster']
        }


class PropertyEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Autostellplatz',
            'Bad', 'Babyzimmer',
            'Dachboden', 'Dachgeschoss', 'Dach',
            'Garten', 'Garage',
            'Haus', 'Häuschen', 'Hütte',
            'Jugendzimmer',
            'Keller', 'Kinderzimmer', 'Küche'
            'Parkplatz',
            'Reduit',
            'Stellplatz', 'Schlafzimmer',
            'Tiefgarage', 'Terrasse',
            'Wohnung',
            'Zimmer',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Reduit': ['Dachboden']
        }


class ShopEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Abholung',
            'Bar',
            'Lieferfrist',
            'Online', 'Online-Shop',
            'Paypal', 'Porto', 'Portokosten', 'Postversand',
            'Twint',
            'Vorauszahlung', 'Versand',
            'Zahlungseingang',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Online': ['Online-Shop']
        }


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
            'Miete', 'Kauf', 'Leasing', 'Wohnen auf Zeit',
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
        return [
            'Aluminium', 'Akazienholz', 'Astholz',
            'Baumwolle',
            'Glas', 'Gummi',
            'Holz',
            'Kunstleder', 'Kork',
            'Leder', 'Laminat',
            'Massivholz',
            'Naturholz',
            'Parkett', 'Porzellan', 'Plattenboden', 'Parkettboden', 'Plexiglas', 'Plastik',
            'Polyurethan', 'Polyester',
            'Goretex',
            'Stoff', 'Stroh', 'Spreu', 'Sand',
            'Terracotta',
            'Wolle'
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Goretex': ['GoreTex'],
        }


class ColorEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Anthrazitgrau',
            'Blau', 'Bunt',
            'Dunkelbraun',
            'Grau', 'Grün', 'Gelb', 'Gestreift', 'Gemustert', 'Graphitschwarz',
            'Lichtgrau',
            'Orange',
            'Rot', 'Rubinrot',
            'Schwarz',
            'Violett',
            'Zitronengelb',
            'Weiss',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Zitronengelb': ['Gelb'],
        }


class JobEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Hege',
            'Pflege',
            'Tiersitting', 'Tierbetreuung',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Tiersitting': ['Tierbetreuung'],
        }


class TechnologyEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Batterie', 'Batterien',
            'WiFi', 'WLAN'
        ]

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
            'Hape', 'Hansen', 'H&M', 'Huawei', 'Honda',
            'IKEA',
            'Jacobsen',
            'Lowa', 'Louis Vuitton', 'Lladro', 'LUCAN',
            'Mercedes', 'Mercedes-Benz', 'Mango', 'Mexx',
            'Nespresso', 'name it',
            'Omega',
            'Paidi', 'Playmobil',
            'Risa', 'Range Rover', 'Ricardo',
            'Stokke', 'Samsung', 'Schöffel', 'Sunshine', 'Schuco', 'Skoda', 'Seat', 'Sunrise',
            'Tosca', 'Toyota', 'Tutti',
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
            'Alufelgen','Auto', 'Autokindersitz', 'Auto-Kindersitz', 'Anhänger', 'Anzug', 'Akku',
            'Aufbewahrungstruhe', 'Aufbewahrungsmöbel', 'Aufbewahrungstisch', 'Absturzsicherung',
            'Besucherstuhl', 'Babywanne', 'Bremsbeläge', 'Bürotisch', 'Bürostuhl', 'Bad', 'Badesand',
            'Bürodrehstuhl', 'Bild', 'Buch', 'Badehose', 'Bikini', 'Badewanne', 'Balkon', 'Behälter',
            'Baumwolleinstreu', 'Baumhaus', 'Blüten', 'Blätter', 'Buddelbox', 'Bett', 'Bücherregal',
            'Corpus', 'Chefsessel',
            'Dusche', 'Drehstuhl', 'Drosselklappensensor', 'Drosselklappenschalter', 'Doppellavabo',
            'Digitalkamera', 'Drahtgitter', 'Deckelklappe', 'Drehteller', 'Dübelversteck',
            'Einstellwerkzeug', 'Endschalldämpfer', 'Entsorgung', 'Essbereich', 'Einstreu', 'Eckschrank',
            'Felgen', 'Fahrzeuge', 'Fenster', 'Futter',
            'Fleecejacke', 'Fahrrad', 'Figur', 'Figuren', 'Frontspoiler', 'Frontlippe', 'Frontlippen', 'Foto',
            'Gartenlehnstuhl', 'Gestell', 'Geschwisterkinderwagen', 'Gewindefahrwerk', 'Grill', 'Gitter',
            'Golf-Bag', 'Glaskeramikkochfeld', 'Glaskeramik-Kochfeld', 'Gefrierfach', 'Gefrierschrank',
            'Garderobe', 'Geschirr', 'Geschirrspüler', 'Glaskäfig', 'Gehege',
            'Handtasche', 'Hängematte', 'Hut', 'Herbst-/Winterjacke', 'Herbst/Winterjacke', 'Hose', 'Heu',
            'Harlekin', 'Heckspoiler', 'Hotspot', 'Hamsterrad', 'Holzbrücke', 'Hamsterburg', 'Holzschrank',
            'Holzkäfig', 'Hamsterkäfig', 'Hamsterhöhle', 'Holztreppe', 'Hasenstahl', 'Holzhäuschen', 'Hundematte',
            'Hangenester', 'Hochbett',
            'Inspektion',
            'Jacke', 'Jeans', 'Jeanshose',
            'Kaffeemaschine', 'Kindersitz',
            'Kommunionkleid', 'Kinderwagen', 'Kinderbett', 'Kugelbahn', 'Kostüm', 'Kostüme', 'Kleid',
            'Kupplungsscheibe', 'Kühlergrill', 'Kühlmittelpumpe', 'Kleidung', 'Kinderschuhe',
            'Konferenz-Raum', 'Kratzsäule', 'Kuschelhöhle', 'Katzentoilette', 'Katzenklo', 'Kletterbaum',
            'Katzenkissen', 'Kissen', 'Katzenstreu', 'Katzentüre', 'Katzenhalsband', 'Käfig', 'Kleintiergehege',
            'Keramikhaus', 'Kleintiertransportbox', 'Kleintierstall', 'Kleintierheim', 'Klebeband',
            'Keramiknapf', 'Kräuter', 'Kokihaus', 'Kletterschutz', 'Kommode', 'Kleiderschrank',
            'Laptop', 'Lift', 'LTE-Router', 'Lavabo', 'Laufrad', 'Leiter',
            'Nebelleuchte', 'Notebook', 'NannoSim', 'Nachttisch', 'Nachtkästchen', 'Nachtschrank',
            'Nagerbehälter',
            'Matraze', 'Matrazen', 'Matratzenboden', 'Marionette', 'Modell', 'Modellauto', 'Möbellift',
            'Motorenöl', 'Motoröl', 'Motor', 'Mitfahrgelegenheit', 'MicroSim', 'Müll', 'Mäusegehege',
            'Nagerheim', 'Nagerkäfig', 'Nagerstall', 'Nagerhaus',
            'Overall', 'Öse',
            'Porzellanfigur', 'Porzellanfiguren', 'Puppe', 'Pullover', 'Plexiglasscheibe', 'PC-Halterung',
            'Rettungsweste', 'Roman', 'Ratgeber', 'Router', 'Rückwand',
            'Rollcontainer', 'Rollkorpus', 'Reifen', 'Räder', 'Regal', 'Regenschutz', 'Rucksack', 'Rock', 'Rahmen',
            'Schlafsack', 'Service', 'Scheibenwischer', 'Sachbuch', 'Schlafsofa',
            'Schlüssel', 'Schlüsselanhänger', 'Scheibenbremsbeläge', 'Strickdecke', 'Stehleuchte', 'Ski',
            'Schreibtisch', 'Stuhl', 'Stühle', 'Scheinwerfer', 'Stossstange', 'Skijacke', 'Ski/Winterjacke',
            'Sommerkleid', 'Sonnenschirm', 'Sommerhut', 'Sonnenhut', 'Strohhut', 'Schuh', 'Schuhe',
            'Sportauspuff', 'Spielzeugautos', 'Schlafsofa', 'Sommerreifen', 'Stehtisch', 'Sitzungstisch',
            'Spiegelschrank', 'Schraube', 'Streu', 'Sandbad', 'Starterset', 'Spielburg', 'Schaukel',
            'Sauerstoffboxen', 'Schale', 'Schlafhöhlen', 'Seitenschutz', 'Seitenblende', 'Sporttourer',
            'Schreibtischplatte',
            'Turnschuhe', 'Tisch', 'Toilette', 'Tasche', 'Transport', 'Taxi', 'Tumbler', 'Truhe', 'Tourer',
            'Tiefkühlfach', 'Trockenfutter', 'Terrarium', 'Terrarien',
            'Transportbox', 'Transport-Box', 'Transportboxen', 'Transportkiste', 'Transportkistli',
            'Tür', 'Treppe',
            'Trinkflasche', 'Trinkflaschen', 'Terracottahaus',
            'Umhängetasche', 'Übergangsjacke', 'Umzug', 'Unterbau', 'Unterschrank',
            'Velo',
            'Winterräder', 'Winterreifen', 'Winterkompletträder', 'Wanne', 'Wasserpumpe', 'Waschmaschine', 'WC',
            'Werkzeugkasten', 'Winterjacke', 'Winterschuhe', 'Wohnmobil', 'Wasch-Trockenmaschine',
            'Wasserflasche', 'Wasserflaschen', 'Winterstiefel', 'Wickeltisch',
            'Zeitwerkzeug', 'Zeitsteuerung', 'Zubehör', 'Zwischenboden',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Fahrrad': ['Velo'],
            'LTE-Router': ['Router'],
            'Glaskeramikkochfeld': ['Glaskeramik-Kochfeld'],
            'Jeans': ['Jeanshose'],
            'Sommerhut': ['Sonnenhut', 'Strohhut'],
            'Corpus': ['Rollcontainer', 'Rollkorpus'],
            'Bürostuhl': ['Besucherstuhl', 'Bürodrehstuhl', 'Drehstuhl'],
            'Kindersitz': ['Autokindersitz', 'Auto-Kindersitz'],
            'Notebook': ['Laptop'],
            'Kommunionkleid': ['Sommerkleid'],
            'Stuhl': ['Stühle'],
            'Transportbox': ['Transport-Box'],
            'Winterjacke': ['Herbst-/Winterjacke', 'Herbst/Winterjacke', 'Ski/Winterjacke', 'Übergangsjacke'],
            'Winterschuhe': ['Winterstiefel'],
        }


class SalesmanEntityHandler:
    @staticmethod
    def get_entity_names_for_all_entity_labels_without_loc(with_lower=False):
        return_list = []
        for entity_label in EL.get_all_without_loc():
            entity = SalesmanEntityHandler.get_entity_for_entity_label(entity_label)
            return_list = return_list + entity.entity_names
        return [entry.lower() for entry in return_list] if with_lower else return_list

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
            EL.ANIMAL: AnimalEntity(),
            EL.BLACK_LIST: BlackListEntity(),
            EL.COMPANY: CompanyEntity(),
            EL.COLOR: ColorEntity(),
            EL.JOB: JobEntity(),
            EL.PRODUCT: ProductEntity(),
            EL.PROPERTY: PropertyEntity(),
            EL.OBJECT: ObjectTypeEntity(),
            EL.TARGET_GROUP: TargetGroupEntity(),
            EL.MATERIAL: MaterialEntity(),
            EL.SHOP: ShopEntity(),
            EL.TECHNOLOGY: TechnologyEntity(),
        }.get(entity_label, CompanyEntity())




