"""
Description: This module contains all named entities for Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""


from sertl_analytics.constants.salesman_constants import EL
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
            'Attika', 'Attikawohnung',
            'Bauernhaus', 'Bungalow', 'Bauland',
            'Doppelhaus', 'Doppelhaushälfte', 'DHH', 'Doppeleinfamilienhaus', 'Doppelfamilienhaus',
            'Dreifamilienreihenhaus',
            'Einfamilienhaus', 'EFH', 'Eckhaus',
            'Generationenhaus',
            'Haus', 'Häuschen', 'Hütte',
            'Immobilie',
            'Lagerhalle', 'Landhaus',
            'Mehrfamilienhaus', 'MFH', 'Maisonette', 'Mittelhaus',
            'Parkplatz', 'Parkplätze',
            'Wohnung',
            'Zimmer',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Doppelhaus': ['Doppelhaushälfte', 'Doppelfamilienhaus']
        }


class PropertyPartEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Autostellplatz', 'Abstellraum', 'Ankleide', 'Aussenreduit', 'Ankleiderraum',
            'Autoeinstellhalle', 'Autoeinstellplatz',
            'Aussenschwimmbad',
            'Bastelraum/Werkstatt', 'Bastelraum',
            'Bad', 'Babyzimmer', 'Büro', 'Büroplatz', 'Badezimmer', 'Badzimmer', 'Balkon',
            'Carport', 'Cheminée',
            'Dachboden', 'Dachgeschoss', 'Dach', 'Dachterrasse',
            'Elternschlafzimmer', 'Estrich', 'Esszimmer',
            'Fahrradkeller', 'Fahrradabstellplatz',
            'Garten', 'Garage', 'Gargensitzplatz', 'Grillplatz', 'Garten/Balkon',
            'Jugendzimmer',
            'Keller', 'Kinderzimmer', 'Küche', 'Kammer', 'Kellerraum',
            'Reduit', 'Réduit',
            'Stellplatz', 'Schlafzimmer', 'Seerosenteich',
            'Tiefgarage', 'Terrasse', 'Trocknerraum',
            'Veranda',
            'Wohn-Esszimmer', 'Wohnzimmer', 'Wohnküche', 'Werkstatt', 'Waschküche',
            'Zimmer',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Reduit': ['Dachboden', 'Estrich']
        }


class EnvironmentEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Abendsonne', 'Altstadt', 'Apotheke',
            'Bahnhof', 'Bäckerei', 'Bezirksschule', 'Bauzonenrand', 'Baulandreserve', 'Bushaltestelle',
            'Dorfkern', 'Dorfzentrum', 'Dorfmuseum', 'Dorfladen',
            'Einkaufsmöglichkeiten', 'Einkaufszentren', 'Einkaufszentrum', 'Einkaufscenter',
            'Flughafen',
            'Gymnasium',
            'Kindergarten',
            'Poststelle', 'Post', 'Primarschule',
            'Landwirtschaftszone',
            'Metzgerei', 'Museum',
            'Panoramablick',
            'Rebberg',
            'Schulen', 'Schwimmbad', 'S-Bahn', 'Spital', 'Spielplatz',
            'Schulen/Kindergarten',
            'Tram-Bahn', 'Thermalbad',
            'U-Bahn',
            'Vitaparcours', 'Vitaparcour',
            'Wald',
            'Zentrum', 'zentrumsnah',
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
            'Coworking', 'Co-Working',
            'Dame', 'Damen',
            'Frau', 'Frauen',
            'Mann', 'Männer',
            'Lady',
            'Mädchen', 'Junge', 'Jungen',
            'Kind', 'Kinder',
            'Baby', 'Babies'            
            'Gewerbe',
            'Nachmieter',
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
        return [
            'Aluminium', 'Akazienholz', 'Astholz',
            'Baumwolle',
            'Glas', 'Gummi', 'Goretex',
            'Holz',
            'Kunstleder', 'Kork',
            'Leder', 'Laminat',
            'Massivholz',
            'Naturholz',
            'Parkett', 'Porzellan', 'Plattenboden', 'Parkettboden', 'Plexiglas', 'Plastik',
            'Polyurethan', 'Polyester',
            'Stoff', 'Stroh', 'Spreu', 'Sand',
            'Terracotta', 'Teakholz',
            'Vinyl',
            'Wolle'
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Goretex': ['Gore-Tex']
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
            'Aussentemperaturanzeige', 'ABS',
            'Batterie', 'Batterien', 'Breitband-Internet',
            'Elektrische Fensterheber', 'ESP',
            'Fahrlichtautomatik', 'Fernwärme',
            'GPS', 'Gasheizung',
            'höhenverstellbar',
            'Induktionskochfeld',
            'Kollisionswarnung',
            'Minergie-Standard', 'Minergie', 'Massiv-Bauweise', 'Massivbauweise',
            'Notrufsystem',
            'LED-Tagfahrlicht', 'LED Heckleuchten', 'LED Intelligent Light',
            'Park-Assistent',
            'Tempomat',
            'Reiserechner', 'Reifendruck-Kontrollanzeige',
            'Seitenairbag', 'SAT/TV', 'Sickerleitungen',
            'Start-Stopp-Funktion',
            'WiFi', 'WLAN', 'Wartungsintervall-Anzeige', 'Wäscheturm',
            'Zentralzeizung',
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
            'Apple', 'Audi', 'Adidas', 'Alberto',
            'BMW', 'Bally', 'Bugaboo', 'Big Max', 'Becker',
            'Crumpler', 'CANON', 'Canon',
            'DeLonghi', 'Dyson', 'Diono'
            'Eames', 'Even&Odd',
            'GoPro', 'Gucci', 'Grüezi-Bag', 'Grüezi Bag', 'Garmin',
            'Hape', 'Hansen', 'H&M', 'Huawei', 'Honda', 'Harley Davidson',
            'IKEA',
            'Jacobsen', 'Joop', 'J. Lindeberg',
            'Lowa', 'Louis Vuitton', 'Lladro', 'LUCAN',
            'Mercedes', 'Mercedes-Benz', 'Mango', 'Mexx',
            'Nespresso', 'name it', 'Navigon', 'Nike',
            'Omega',
            'Paidi', 'Playmobil', 'Puma',
            'Risa', 'Range Rover', 'Ricardo',
            'Stokke', 'Samsung', 'Schöffel', 'Sunshine', 'Schuco', 'Skoda', 'Seat', 'Sunrise', 'SBB',
            'Tosca', 'Toyota', 'Tutti', 'TomTom',
            'USM', 'Under Armour',
            'Waldmann', 'Wilde+Spieth',
            'Villiger',  'Vitra', 'VW', 'Volkswagen', 'Volg',
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
            'EOS 700D', 'EA107', 'EA 107', 'EA108', 'EA 108', 'EA 219',
            'gtx',
            'Hot + Cool', 'hero',
            'Kitos', 'Kid Cow',
            'Looking Good',
            'MacBook', 'meda', 'Monterey',
            'Pixie', 'Panama', 'Purpose Chair', 'PrimaDonna',
            'Roundabout',
            'sleepi', 'Silencio',
            'Velar', 'Vito',
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
            'Ablagefach',
            'Alufelgen', 'Auto', 'Autokindersitz', 'Auto-Kindersitz', 'Anhänger', 'Anzug', 'Akku',
            'Aufbewahrungstruhe', 'Aufbewahrungsmöbel', 'Aufbewahrungstisch', 'Absturzsicherung',
            'Besucherstuhl', 'Babywanne', 'Bremsbeläge', 'Bürotisch', 'Bürostuhl', 'Bad', 'Badesand', 'Badewanne',
            'Bürodrehstuhl', 'Bild', 'Buch', 'Badehose', 'Bikini', 'Badewanne', 'Balkon', 'Behälter',
            'Baumwolleinstreu', 'Baumhaus', 'Blüten', 'Blätter', 'Buddelbox', 'Bett', 'Bücherregal',
            'Badewanne/Dusche', 'Badewanne/Whirlpool',
            'Brillenfach', 'Bottleholder',
            'Campinggeschirr',
            'Corpus', 'Chefsessel',
            'Doppelbett', 'Dunstabzug',
            'Dusche', 'Drehstuhl', 'Drosselklappensensor', 'Drosselklappenschalter', 'Doppellavabo',
            'Digitalkamera', 'Drahtgitter', 'Deckelklappe', 'Drehteller', 'Dübelversteck',
            'Einstellwerkzeug', 'Endschalldämpfer', 'Entsorgung', 'Essbereich', 'Einstreu', 'Eckschrank',
            'Felgen', 'Fahrzeuge', 'Fenster', 'Futter',
            'Fleecejacke', 'Fahrrad', 'Figur', 'Figuren', 'Frontspoiler', 'Frontlippe', 'Frontlippen', 'Foto',
            'Flaschenhalter',
            'Gartenlehnstuhl', 'Gestell', 'Geschwisterkinderwagen', 'Gewindefahrwerk', 'Grill', 'Gitter',
            'Golf-Bag', 'Glaskeramikkochfeld', 'Glaskeramik-Kochfeld', 'Gefrierfach', 'Gefrierschrank',
            'Garderobe', 'Geschirr', 'Geschirrspüler', 'Glaskäfig', 'Gehege', 'Gürtel', 'Golfgürtel',
            'Haustür',
            'Handtasche', 'Hängematte', 'Hut', 'Herbst-/Winterjacke', 'Herbst/Winterjacke', 'Hose', 'Heu',
            'Harlekin', 'Heckspoiler', 'Hotspot', 'Hamsterrad', 'Holzbrücke', 'Hamsterburg', 'Holzschrank',
            'Holzkäfig', 'Hamsterkäfig', 'Hamsterhöhle', 'Holztreppe', 'Hasenstahl', 'Holzhäuschen', 'Hundematte',
            'Hangenester', 'Hochbett', 'Hinterreifen',
            'Inspektion',
            'Jacke', 'Jeans', 'Jeanshose',
            'Kaffeemaschine', 'Kindersitz', 'Kühlschrank',
            'Kommunionkleid', 'Kinderwagen', 'Kinderbett', 'Kugelbahn', 'Kostüm', 'Kostüme', 'Kleid',
            'Kupplungsscheibe', 'Kühlergrill', 'Kühlmittelpumpe', 'Kleidung', 'Kinderschuhe',
            'Konferenz-Raum', 'Kratzsäule', 'Kuschelhöhle', 'Katzentoilette', 'Katzenklo', 'Kletterbaum',
            'Katzenkissen', 'Kissen', 'Katzenstreu', 'Katzentüre', 'Katzenhalsband', 'Käfig', 'Kleintiergehege',
            'Keramikhaus', 'Kleintiertransportbox', 'Kleintierstall', 'Kleintierheim', 'Klebeband',
            'Keramiknapf', 'Kräuter', 'Kokihaus', 'Kletterschutz', 'Kommode', 'Kleiderschrank',
            'Laptop', 'Lift', 'LTE-Router', 'Lavabo', 'Laufrad', 'Leiter', 'Lieferwagen', 'Lampe',
            'Nebelleuchte', 'Notebook', 'NannoSim', 'Nachttisch', 'Nachtkästchen', 'Nachtschrank',
            'Nagerbehälter', 'Navi', 'Navigationsgerät',
            'Matraze', 'Matrazen', 'Matratzenboden', 'Marionette', 'Modell', 'Modellauto', 'Möbellift',
            'Motorenöl', 'Motoröl', 'Motor', 'Mitfahrgelegenheit', 'MicroSim', 'Müll', 'Mäusegehege', 'Motorrad',
            'Multifunktionslenkrad', 'Mikrowelle',
            'Nagerheim', 'Nagerkäfig', 'Nagerstall', 'Nagerhaus',
            'Overall', 'Öse',
            'Porzellanfigur', 'Porzellanfiguren', 'Puppe', 'Pullover', 'Plexiglasscheibe', 'PC-Halterung',
            'Portemonnaie', 'Pizzaofen',
            'Rettungsweste', 'Roman', 'Ratgeber', 'Router', 'Rückwand', 'Rückfahrkamera', 'Rückenlehne', 'Rücklehne',
            'Rollcontainer', 'Rollkorpus', 'Reifen', 'Räder', 'Regal', 'Regenschutz', 'Rucksack', 'Rock', 'Rahmen',
            'Schlafsack', 'Service', 'Scheibenwischer', 'Sachbuch', 'Schlafsofa', 'Sitzbank', 'Seitentaschen',
            'Schlüssel', 'Schlüsselanhänger', 'Scheibenbremsbeläge', 'Strickdecke', 'Stehleuchte', 'Ski',
            'Schreibtisch', 'Stuhl', 'Stühle', 'Scheinwerfer', 'Stossstange', 'Skijacke', 'Ski/Winterjacke',
            'Sommerkleid', 'Sonnenschirm', 'Sommerhut', 'Sonnenhut', 'Strohhut', 'Schuh', 'Schuhe',
            'Sportauspuff', 'Spielzeugautos', 'Schlafsofa', 'Sommerreifen', 'Stehtisch', 'Sitzungstisch',
            'Spiegelschrank', 'Schraube', 'Streu', 'Sandbad', 'Starterset', 'Spielburg', 'Schaukel',
            'Sauerstoffboxen', 'Schale', 'Schlafhöhlen', 'Seitenschutz', 'Seitenblende', 'Sporttourer',
            'Schreibtischplatte', 'Schultergurt', 'Sonderzubehör', 'SIM-Karte', 'Staubsauger', 'Steamer',
            'Turnschuhe', 'Tisch', 'Toilette', 'Tasche', 'Transport', 'Taxi', 'Tumbler', 'Truhe', 'Tourer',
            'Tiefkühlfach', 'Trockenfutter', 'Terrarium', 'Terrarien',
            'Transportbox', 'Transport-Box', 'Transportboxen', 'Transportkiste', 'Transportkistli',
            'Tür', 'Treppe',
            'Trinkflasche', 'Trinkflaschen', 'Terracottahaus',
            'Umhängetasche', 'Übergangsjacke', 'Umzug', 'Unterbau', 'Unterschrank', 'Untergestell',
            'Velo', 'Vorderreifen',
            'Winterräder', 'Winterreifen', 'Winterkompletträder', 'Wanne', 'Wasserpumpe', 'Waschmaschine', 'WC',
            'Werkzeugkasten', 'Winterjacke', 'Winterschuhe', 'Wohnmobil', 'Wasch-Trockenmaschine',
            'Wasserflasche', 'Wasserflaschen', 'Winterstiefel', 'Wickeltisch', 'Widerstand',
            'Zeitwerkzeug', 'Zeitsteuerung', 'Zubehör', 'Zwischenboden', 'Zahnriemen', 'Zimmerlampe',
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
            'Navi': ['Navigationsgerät'],
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
    def get_main_entity_name_for_entity_name(entity_label: str, entity_name: str) -> str:
        # print('get_main_entity_name_for_entity_name: entity_label={}, entity_name={}'.format(entity_label, entity_name))
        synonym_dict = SalesmanEntityHandler.get_entity_for_entity_label(entity_label).entity_synonym_dict
        if entity_name in synonym_dict:  # entity_name is already main entity_name
            return entity_name
        for key, synonym_list in synonym_dict.items():
            if entity_name in synonym_list:
                return key
        return entity_name

    @staticmethod
    def get_main_entity_value_label_dict(entity_value_label_dict: dict) -> dict:
        return {
            label_value: entity_label for label_value, entity_label in entity_value_label_dict.items()
            if SalesmanEntityHandler.get_main_entity_name_for_entity_name(entity_label, label_value) == label_value
        }

    @staticmethod
    def get_entity_for_entity_label(entity_label: str) -> NamedEntity:
        return {
            EL.ANIMAL: AnimalEntity(),
            EL.BLACK_LIST: BlackListEntity(),
            EL.COMPANY: CompanyEntity(),
            EL.COLOR: ColorEntity(),
            EL.JOB: JobEntity(),
            EL.ENVIRONMENT: EnvironmentEntity(),
            EL.PRODUCT: ProductEntity(),
            EL.PROPERTY: PropertyEntity(),
            EL.PROPERTY_PART: PropertyPartEntity(),
            EL.OBJECT: ObjectTypeEntity(),
            EL.TARGET_GROUP: TargetGroupEntity(),
            EL.MATERIAL: MaterialEntity(),
            EL.SHOP: ShopEntity(),
            EL.TECHNOLOGY: TechnologyEntity(),
        }.get(entity_label, CompanyEntity())




