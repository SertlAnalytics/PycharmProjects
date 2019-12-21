"""
Description: This module contains all named entities for Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

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


class ActivityEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Golf',
            'Lesen',
            'Wandern',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
        }


class AnimalEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Aal',
            'Chinchillas',
            'Esel',
            'Forelle', 'Forellen', 'Frettchen',
            'Goldfisch', 'Goldfische', 'Garnele', 'Garnelen','Graupapageien',
            'Hund', 'Hamster', 'Haustiere', 'Hase',
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
            'Reiheneckhaus', 'Reiheneinfamilienhaus',
            'Wohnung',
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
            'Elternschlafzimmer', 'Estrich', 'Esszimmer', 'Elternzimmer',
            'Fahrradkeller', 'Fahrradabstellplatz',
            'Garten', 'Garage', 'Gargensitzplatz', 'Grillplatz', 'Garten/Balkon',
            'Jugendzimmer',
            'Keller', 'Kinderzimmer', 'Küche', 'Kammer', 'Kellerraum',
            'Naturkeller',
            'Reduit', 'Réduit',
            'Stellplatz', 'Schlafzimmer', 'Seerosenteich',
            'Tiefgarage', 'Terrasse', 'Trocknerraum', 'Tomatenhäuschen',
            'Veranda',
            'Wohn-Esszimmer', 'Wohnzimmer', 'Wohnküche', 'Werkstatt', 'Waschküche', 'Waschraum',
            'Zimmer',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Reduit': ['Dachboden', 'Estrich']
        }


class EducationEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Bezirksschule',
            'Fachhochschule',
            'Gymnasium',
            'Hochschule',
            'Kindergarten', 'Kita', 'Kindertagesstätte',
            'Primarschule',
            'Schule', 'Schulen',
            'Schulen/Kindergarten',
            'Universität',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
        }


class TransportEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Bahnhof', 'Bushaltestelle', 'Bus', 'Bahn',
            'Buslinie',
            'Flughafen',
            'öffentlicher Verkehr',
            'Postauto',
            'S-Bahn',
            'Tram-Bahn', 'Taxi', 'Taxistand',
            'U-Bahn',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
        }


class ShopEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Apotheke',
            'Bäckerei',
            'Dorfladen',
            'Einkaufsmöglichkeiten', 'Einkaufszentren', 'Einkaufszentrum', 'Einkaufscenter',
            'Poststelle', 'Post',
            'Metzgerei',
            'Restaurants',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
        }


class EnvironmentEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Abendsonne', 'Altstadt',
            'Bauzonenrand', 'Baulandreserve',
            'Dorfkern', 'Dorfzentrum', 'Dorfmuseum',
            'Gartenparadies', 'Gehdistanz',
            'Landwirtschaftszone',
            'Museum',
            'Naherholungsgebiet',
            'Panoramablick',
            'Rebberg',
            'Schwimmbad', 'Spital', 'Spielplatz',
            'Thermalbad',
            'Vitaparcours', 'Vitaparcour',
            'Wald',
            'Zentrum', 'zentrumsnah',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
        }


class PaymentEntity(NamedEntity):
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
            'Corkx',
            'Denim', 'Daunen',
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
            'Goretex': ['Gore-Tex'],
            'Cork': ['Kork'],
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
            'Tiersitting', 'Tierbetreuung', 'Tierfleger',
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
            'Aussentemperaturanzeige', 'ABS', 'automatischem Tor',
            'Bewegungsmelder',
            'Batterie', 'Batterien', 'Breitband-Internet',
            'Elektrische Fensterheber', 'ESP',
            'Fahrlichtautomatik', 'Fernwärme',
            'GPS', 'Gasheizung',
            'höhenverstellbar',
            'Induktionskochfeld',
            'Kollisionswarnung', 'Kippmechanik', 'Klettverschluss',
            'Minergie-Standard', 'Minergie', 'Massiv-Bauweise', 'Massivbauweise', 'Minergie-Zertifiziert',
            'mechanischem Schiebetor',
            'Notrufsystem',
            'LED-Tagfahrlicht', 'LED Heckleuchten', 'LED Intelligent Light',
            'Park-Assistent',
            'Tempomat',
            'Reiserechner', 'Reifendruck-Kontrollanzeige',
            'Seitenairbag', 'SAT/TV', 'Sickerleitungen',
            'Start-Stopp-Funktion',
            'verchromt',
            'WiFi', 'WLAN', 'Wartungsintervall-Anzeige', 'Wäscheturm', 'Widerstand',
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
            'Apple', 'Audi', 'Adidas', 'Alberto', 'Aldi',
            'BMW', 'Bally', 'Bugaboo', 'Big Max', 'Becker',
            'Crumpler', 'CANON', 'Canon', 'Coop', 'CMP',
            'DeLonghi', 'Dyson', 'Diono', 'Denner',
            'Eames', 'Even&Odd',
            'Fiat', 'Ford',
            'GoPro', 'Gucci', 'Grüezi-Bag', 'Grüezi Bag', 'Garmin',
            'Hape', 'Hansen', 'H&M', 'Huawei', 'Honda', 'Harley Davidson', 'Hilfinger', 'Hyra',
            'IKEA',
            'Jacobsen', 'Joop', 'J. Lindeberg',
            'Lowa', 'Louis Vuitton', 'Lladro', 'LUCAN', 'Lidl',
            'Mercedes', 'Mercedes-Benz', 'Mango', 'Mexx', 'Mazda',
            'Nespresso', 'name it', 'Navigon', 'Nike',
            'Omega',
            'Paidi', 'Playmobil', 'Puma', 'Paglie', 'Poivre Blanc', 'Paul Green',
            'Risa', 'Range Rover', 'Ricardo', 'Renault', 'Review',
            'Stokke', 'Samsung', 'Schöffel', 'Sunshine', 'Schuco', 'Skoda', 'Seat', 'Sunrise', 'SBB', 'Schwörer',
            'Spin Master',
            'Tosca', 'Toyota', 'Tutti', 'TomTom', 'Triumph', 'Terranova', 'Typhoon',
            'USM', 'Under Armour',
            'Waldmann', 'Wilde+Spieth',
            'Villiger',  'Vitra', 'VW', 'Volkswagen', 'Volg', 'Vaude',
            'Yamaha',
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
            'Cork Family',
            'Drive Smart',
            'EOS 700D', 'EA107', 'EA 107', 'EA108', 'EA 108', 'EA 219',
            'Fiesta',
            'gtx', 'GO BASIC', 'Go Essential',
            'hero', 'Hamax',
            'Kitos', 'Kid Cow',
            'Looking Good',
            'MacBook', 'meda', 'Monterey',
            'Pixie', 'Panama', 'Purpose Chair', 'PrimaDonna', 'Punto',
            'Roundabout', 'Rufus',
            'sleepi', 'Silencio',
            'Velar', 'Vito',
            'Zümo', 'Zoomer'
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'alu chair': ['aluminum chair'],
            'EA107': ['EA 107'],
            'EA108': ['EA 108'],
        }


class ClothesEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Anzug',
            'Fleecejacke',
            'Gürtel', 'Golfgürtel',
            'Handtasche', 'Hut', 'Herbst-/Winterjacke', 'Herbst/Winterjacke', 'Hose', 'Hemd',
            'Jacke', 'Jeans', 'Jeanshose',
            'Kommunionkleid', 'Kostüm', 'Kostüme', 'Kleid', 'Krawatte', 'Kapuzenjacke',
            'Mantel',
            'Overall',
            'Pullover', 'Pulli', 'Poloshirt',
            'Rettungsweste',
            'Skijacke', 'Ski/Winterjacke', 'Sommerkleid', 'Skihose',
            'Sommerhut', 'Sonnenhut', 'Strohhut', 'Schuh', 'Schuhe', 'Schultergurt', 'Shorts',
            'Stiefel', 'Stiefelleten',
            'Turnschuhe', 'Softshelljacke',
            'Umhängetasche', 'Übergangsjacke',
            'Winterjacke', 'Winterschuhe', 'Winterstiefel', 'Wintermantel',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Kommunionkleid': ['Sommerkleid'],
            'Jeans': ['Jeanshose'],
            'Pullover': ['Pulli'],
            'Sommerhut': ['Sonnenhut', 'Strohhut'],
            'Winterjacke': ['Herbst-/Winterjacke', 'Herbst/Winterjacke', 'Ski/Winterjacke', 'Übergangsjacke'],
            'Winterschuhe': ['Winterstiefel'],
        }


class VehicleEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Auto',
            'Camper', 'Campingbus',
            'Drohne',
            'Fahrrad', 'Fahrzeug', 'Fahrzeuge',
            'Kinderwagen',
            'Lkw', 'Lastkraftwagen',
            'Motorrad',
            'Spielzeugauto',
            'Velo',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'Fahrrad': ['Velo'],
        }


class ObjectEntity(NamedEntity):
    @staticmethod
    def __get_entity_names__():
        return [
            'Ablagefach',
            'Alufelgen', 'Autokindersitz', 'Auto-Kindersitz', 'Anhänger', 'Akku',
            'Aufbewahrungstruhe', 'Aufbewahrungsmöbel', 'Aufbewahrungstisch', 'Absturzsicherung',
            'Besucherstuhl', 'Babywanne', 'Bremsbeläge', 'Bürotisch', 'Bürostuhl', 'Badesand', 'Badewanne',
            'Bürodrehstuhl', 'Bild', 'Buch', 'Badehose', 'Bikini', 'Behälter', 'Beistelltisch',
            'Baumwolleinstreu', 'Baumhaus', 'Blüten', 'Blätter', 'Buddelbox', 'Bett', 'Bücherregal',
            'Badewanne/Dusche', 'Badewanne/Whirlpool',
            'Brillenfach', 'Bottleholder', 'Bob',
            'Campinggeschirr',
            'Corpus', 'Chefsessel',
            'Doppelbett', 'Dunstabzug',
            'Dusche', 'Drehstuhl', 'Drosselklappensensor', 'Drosselklappenschalter', 'Doppellavabo',
            'Digitalkamera', 'Drahtgitter', 'Deckelklappe', 'Drehteller', 'Dübelversteck',
            'Einstellwerkzeug', 'Endschalldämpfer', 'Entsorgung', 'Essbereich', 'Einstreu', 'Eckschrank',
            'Felgen', 'Fenster', 'Futter', 'Fernseher',
            'Figur', 'Figuren', 'Frontspoiler', 'Frontlippe', 'Frontlippen', 'Foto',
            'Flaschenhalter', 'Fernbedienung',
            'Gartenlehnstuhl', 'Gestell', 'Geschwisterkinderwagen', 'Gewindefahrwerk', 'Grill', 'Gitter',
            'Golf-Bag', 'Glaskeramikkochfeld', 'Glaskeramik-Kochfeld', 'Gefrierfach', 'Gefrierschrank',
            'Garderobe', 'Geschirr', 'Geschirrspüler', 'Glaskäfig', 'Gehege',
            'Haustür',
            'Hängematte', 'Heu',
            'Harlekin', 'Heckspoiler', 'Hotspot', 'Hamsterrad', 'Holzbrücke', 'Hamsterburg', 'Holzschrank',
            'Holzkäfig', 'Hamsterkäfig', 'Hamsterhöhle', 'Holztreppe', 'Hasenstahl', 'Holzhäuschen', 'Hundematte',
            'Hangenester', 'Hochbett', 'Hinterreifen', 'Hocker',
            'Inspektion',
            'Kaffeemaschine', 'Kindersitz', 'Kühlschrank',
            'Kinderbett', 'Kugelbahn',
            'Kupplungsscheibe', 'Kühlergrill', 'Kühlmittelpumpe', 'Kleidung', 'Kinderschuhe',
            'Konferenz-Raum', 'Kratzsäule', 'Kuschelhöhle', 'Katzentoilette', 'Katzenklo', 'Kletterbaum',
            'Katzenkissen', 'Kissen', 'Katzenstreu', 'Katzentüre', 'Katzenhalsband', 'Käfig', 'Kleintiergehege',
            'Keramikhaus', 'Kleintiertransportbox', 'Kleintierstall', 'Kleintierheim', 'Klebeband',
            'Keramiknapf', 'Kräuter', 'Kokihaus', 'Kletterschutz', 'Kommode', 'Kleiderschrank',
            'Laptop', 'Lift', 'LTE-Router', 'Lavabo', 'Laufrad', 'Leiter', 'Lieferwagen', 'Lampe',
            'Nebelleuchte', 'Notebook', 'NannoSim', 'Nachttisch', 'Nachtkästchen', 'Nachtschrank',
            'Nagerbehälter', 'Navi', 'Navigationsgerät',
            'Matraze', 'Matrazen', 'Matratzenboden', 'Marionette', 'Modell', 'Modellauto', 'Möbellift',
            'Motorenöl', 'Motoröl', 'Motor', 'Mitfahrgelegenheit', 'MicroSim', 'Müll', 'Mäusegehege',
            'Multifunktionslenkrad', 'Mikrowelle',
            'Nagerheim', 'Nagerkäfig', 'Nagerstall', 'Nagerhaus',
            'Öse',
            'Porzellanfigur', 'Porzellanfiguren', 'Puppe', 'Plexiglasscheibe', 'PC-Halterung',
            'Portemonnaie', 'Pizzaofen',
            'Radio',
            'Roman', 'Ratgeber', 'Router', 'Rückwand', 'Rückfahrkamera', 'Rückenlehne', 'Rücklehne', 'Rollen',
            'Rollcontainer', 'Rollkorpus', 'Reifen', 'Räder', 'Regal', 'Regenschutz', 'Rucksack', 'Rock', 'Rahmen',
            'Schlafsack', 'Service', 'Scheibenwischer', 'Sachbuch', 'Schlafsofa', 'Sitzbank', 'Seitentaschen',
            'Schlüssel', 'Schlüsselanhänger', 'Scheibenbremsbeläge', 'Strickdecke', 'Stehleuchte', 'Ski',
            'Schreibtisch', 'Stuhl', 'Stühle', 'Scheinwerfer', 'Stossstange',
            'Sonnenschirm', 'Schlitten',
            'Sportauspuff', 'Sommerreifen', 'Stehtisch', 'Sitzungstisch',
            'Spiegelschrank', 'Schraube', 'Streu', 'Sandbad', 'Starterset', 'Spielburg', 'Schaukel',
            'Sauerstoffboxen', 'Schale', 'Schlafhöhlen', 'Seitenschutz', 'Seitenblende', 'Sporttourer',
            'Schreibtischplatte', 'Sonderzubehör', 'SIM-Karte', 'Staubsauger', 'Steamer',
            'Tankrucksack',
            'Tisch', 'Toilette', 'Tasche', 'Transport', 'Tumbler', 'Truhe', 'Tourer',
            'Tiefkühlfach', 'Trockenfutter', 'Terrarium', 'Terrarien',
            'Transportbox', 'Transport-Box', 'Transportboxen', 'Transportkiste', 'Transportkistli',
            'Tür', 'Treppe', 'TV',
            'Trinkflasche', 'Trinkflaschen', 'Terracottahaus',
            'Umzug', 'Unterbau', 'Unterschrank', 'Untergestell',
            'Vorderreifen',
            'Winterräder', 'Winterreifen', 'Winterkompletträder', 'Wanne', 'Wasserpumpe', 'Waschmaschine', 'WC',
            'Werkzeugkasten', 'Wohnmobil', 'Wasch-Trockenmaschine',
            'Wasserflasche', 'Wasserflaschen', 'Wickeltisch',
            'Zeitwerkzeug', 'Zeitsteuerung', 'Zubehör', 'Zwischenboden', 'Zahnriemen', 'Zimmerlampe',
        ]

    @staticmethod
    def __get_synonym_dict__():
        return {
            'LTE-Router': ['Router'],
            'Glaskeramikkochfeld': ['Glaskeramik-Kochfeld'],
            'Corpus': ['Rollcontainer', 'Rollkorpus'],
            'Bürostuhl': ['Besucherstuhl', 'Bürodrehstuhl', 'Drehstuhl'],
            'Fernseher': ['TV'],
            'Kindersitz': ['Autokindersitz', 'Auto-Kindersitz'],
            'Notebook': ['Laptop'],
            'Navi': ['Navigationsgerät'],
            'Stuhl': ['Stühle'],
            'Transportbox': ['Transport-Box'],
        }

