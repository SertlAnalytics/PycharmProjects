"""
Description: This module contains all constants for Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""


class PRCAT:  # Product Category, german: Rubrik
    ALL = 'Alle'
    ART = 'Antiquitäten & Kunst'
    CHILD = 'Baby & Child'
    BOOKS = 'Bücher'
    BUSINESS = 'Büro & Gewerbe'
    COMPUTER = 'Computer & Zubehör'
    SERVICE = 'Dienstleistungen'
    VEHICELS = 'Fahrzeuge'
    PICTURE = 'Film'
    PHOTO_VIDEO = 'Foto & Video'
    GARDEN_CRAFT = 'Garten & Handwerk'
    HOUSEHOLD = 'Haushalt'
    REAL_ESTATE = 'Immobilien'
    CLOTHES_OTHERS = 'Kleidung & Accessoires'
    MUSIC = 'Musik'
    COLLECTIONS = 'Sammeln'
    TOYS = 'Spielzeuge & Basteln'
    SPORT_OUTDOOR = 'Sport & Outdoor'
    JOBS = 'Stellenangebote'
    TV_AUDIO = 'TV & Audio'
    PHONE_NAVI = 'Telefon & Navigation'
    TICKETS_BONS = 'Tickets & Gutscheine'
    ANIMALS = 'Tiere'
    OTHERS = 'Sonstiges'

    @staticmethod
    def get_all():
        return [
            PRCAT.ALL, PRCAT.VEHICELS, PRCAT.REAL_ESTATE,
            PRCAT.ART, PRCAT.CHILD, PRCAT.BOOKS, PRCAT.BUSINESS, PRCAT.COMPUTER,
            PRCAT.SERVICE, PRCAT.PICTURE, PRCAT.PHOTO_VIDEO, PRCAT.GARDEN_CRAFT,
            PRCAT.HOUSEHOLD, PRCAT.CLOTHES_OTHERS, PRCAT.MUSIC, PRCAT.COLLECTIONS,
            PRCAT.TOYS, PRCAT.SPORT_OUTDOOR, PRCAT.JOBS, PRCAT.TV_AUDIO, PRCAT.PHONE_NAVI,
            PRCAT.TICKETS_BONS, PRCAT.ANIMALS, PRCAT.OTHERS
        ]

    @staticmethod
    def get_all_without_all() -> list:
        list_all = PRCAT.get_all()
        list_all.remove(PRCAT.ALL)
        return list_all


class PRSUBCAT:  # Product Sub Category, german: Unter-Rubrik
    ALL = 'Alle'
    BOOK_NOVELS = 'Romane'
    BOOK_ADVISORS = 'Sachbücher & Ratgeber'
    CHILD_STROLLER = 'Kinderwagen & Sitze'
    CHILD_ROOM = 'Kinderzimmer'
    CHILD_CLOTHES = 'Kleider & Schuhe'
    CLOTHES_FEMALE = 'Kleidung für Damen'
    CLOTHES_MALE = 'Kleidung für Herren'
    SHOES_FEMALE = 'Schuhe für Damen'
    SHOES_MALE = 'Schuhe für Herren'
    OTHERS_BAGS = 'Taschen und & Portmonnaies'
    OTHERS_WATCHES = 'Uhren & Schmuck'
    COMPUTER = 'Computer'
    COMPUTER_COMPONENTS = 'Komponenten & Zubehör'
    SOFTWARE = 'Software'
    TABLETS = 'Tablets'
    SERVICE_OFFICE = 'Büroservice'
    SERVICE_COMPUTER = 'Computer & Handys'
    SERVICE_FINANCE = 'Finanzen & Recht'
    SERVICE_CRAFT = 'Handwerk'
    SERVICE_TRANSPORT = 'Umzug & Transport'
    BUSINESS_MATERIAL = 'Büromaterial & Büromöbel'
    BUSINESS_EQUIPMENT = 'Geschäftseinrichtungen'
    SPORT_CAMPING = 'Camping'
    SPORT_FITNESS = 'Fitness'
    SPORT_BIKE = 'Velos'
    SPORT_WINTER = 'Wintersport'
    SPORT_OTHERS = 'Sonstige Sportarten'
    PHONE_FIX = 'Festnetztelefone'
    PHONE_MOBILE = 'Handys'
    PHONE_NAVI = 'Navigationssysteme'
    PHONE_COMPONENTS = 'Zubehör'
    VEHICELS_CARS = 'Autos'
    VEHICELS_COMPONENTS = 'Autozubehör'
    VEHICELS_BOATS = 'Boote & Zubehör'
    VEHICELS_BIKE_COMPONENTS = 'Motorradzubehör'
    VEHICELS_BIKE = 'Motorräder'
    VEHICELS_UTILITIES = 'Nutzfahrzeuge'
    VEHICELS_CAMPERS = 'Wohnmobile'
    REAL_ESTATE_HOLIDAY = 'Ferienobjekte'
    REAL_ESTATE_BUSINESS = 'Gewerbeobjekte'
    REAL_ESTATE_PROPERTY = 'Grundstücke'
    REAL_ESTATE_HOUSES = 'Häuser'
    REAL_ESTATE_PARKING = 'Parkplätze'
    REAL_ESTATE_COMMUNITY = 'WG-Zimmer'
    REAL_ESTATE_FLATS = 'Wohnungen'
    PHOTO_CAMERA = 'Fotokameras'
    VIDEO_CAMERA = 'Videokameras'
    PHOTO_COMPONENTS = 'Zubehör'
    GARDEN_MATERIAL = 'Baumaterial'
    GARDEN_EQUIPMENT = 'Gartenausstattung'
    GARDEN_TOOLS = 'Werkzeuge & Maschinen'
    HOUSEHOLD_LIGHT = 'Beleuchtung'
    HOUSEHOLD_TOOLS = 'Geräte & Utensilien'
    HOUSEHOLD_FOOD = 'Lebensmittel'
    HOUSEHOLD_FURNITURE = 'Möbel'
    JOBS_HEALTH = 'Gesundheitswesen'
    JOBS_OTHERS = 'Sonstige Stellen'


class EL:  # entity labels
    COMPANY = 'COMPANY'
    PRODUCT = 'PRODUCT'
    OBJECT = 'OBJECT'
    TARGET_GROUP = 'TARGET_GROUP'
    MATERIAL = 'MATERIAL'
    TECHNOLOGY = 'TECHNOLOGY'

    @staticmethod
    def is_entity_label_tutti_relevant(ent_level: str) -> bool:
        return ent_level in [EL.PRODUCT, EL.COMPANY, EL.OBJECT, EL.TARGET_GROUP, EL.MATERIAL, EL.TECHNOLOGY]


class SLCLS:  # css classes used within tutti sales
    OFFERS = '_2qT0v'
    MAIN_ANKER = '_16dGT'
    LOCATION = '_3f6Er'
    DATE = '_1kvIw'
    LINK = '_16dGT'  # or '_2SE_L'
    TITLE = '_2SE_L'
    DESCRIPTION = '_2c4Jo'
    PRICE = '_6HJe5'
    NUMBERS = '_1WJLw'


class SLSCLS:  # css classes used within tutti sale single
    OFFERS = '_142-1'
    MAIN_ANKER = '_16dGT'
    LOCATION_CLASS = '_35E6Q'  # _2ey_I'  # <div class="_35E6Q"><svg role="img" viewBox="0 0 35 35" class="svg-sprite"><use xlink:href="#canton-aargau"></use></svg><span class="_2ey_I">Aargau, 5430</span></div>
    LOCATION_SUB_CLASS = '_2ey_I'
    DATE_CLASS = '_2hsZ0'
    DATE_SUB_CLASS = '_3HMUQ'
    LINK = '_16dGT'  # or '_2SE_L'
    TITLE = '_36xB4'
    DESCRIPTION = ['_3E1vH', '_100oN', '_3MSKw']
    PRICE = '-zQvW'
    PRODUCT_CATEGORIES = '_3G0Ix'
    PRODUCT_CATEGORY_CLASS = '_2ey_I'
    PRODUCT_SUB_CATEGORY_CLASS = 'b1fl5'


class SCLS:  # css classes used within search offers
    FOUND_NUMBERS = '_3N3mg'  #'_35r2W'
    OFFERS = '_3aiCi'
    MAIN_ANKER = '_16dGT'
    LOCATION = '_3f6Er'
    DATE = '_1kvIw'
    LINK = '_16dGT'
    DESCRIPTION = '_2c4Jo'
    PRICE = '_6HJe5'
    NAVIGATION_MAIN = '_34zCr'
    NAVIGATION_ANCHOR = '_3bpXO _3vEQq'


class POS:
    ADJ = 'ADJ'  # adjective, e.g. 'warmes' (Innenfutter)
    ADP = 'ADP'  # AD, e.g. 'in', 'Dank'
    ADV = 'ADV'  # adverb, e.g. 'kaum' (gebraucht)
    CONJ = 'CONJ'  # conjunction
    DATE = 'DATE'  # date, 27.10.1964
    NUM = 'NUM'  # number, e.g. 37
    NOUN = 'NOUN'  # noun, e.g. 'Goretex'
    PART = 'PART'  # partical, e.g. 'zu' (verkaufen)
    PROPN = 'PROPN'  # proper noun, e.g. 'Wanderschuhe'
    PUNCT = 'PUNCT'  # punctuation, e.g. ','
    VERB = 'VERB'  # verb, e.g. 'verkaufen'
    X = 'X'         # X = ???

    @staticmethod
    def is_pos_noun(pos: str) -> bool:
        return pos in [POS.NOUN, POS.PROPN]


class TAG:
    ADJA = 'ADJA'  # ADJA??, e.g. 'warmes'
    ADJD = 'ADJD'  # ADJD??, e.g. 'einfach' (einfach höhenverstellbar)
    APPR = 'APPR'  # appr???, e.g. 'Dank' (Dank .. wasserdicht)
    CARD = 'CARD'  # Cardinal, e.g. 37
    NE = 'NE'  # NE??, e.g. 'Rufus', 'Lowa', 'Innenfutter', mostly POS=PROPN
    NN = 'NN'  # NN??, e.g. 'Rufus', 'Lowa', 'Innenfutter', mostly POS=NOUN
    VVFIN = 'VVFIN'  # VVFIN???, e.g. 'wasserdicht'
    VVPP = 'VVPP'  # VVPP??, e.g. 'gebraucht', 'erhalten'


class DEP:
    cj = 'cj'  # cj???, e.g. 'LOWA', mostly POS=NOUN or PROPN
    ROOT = 'ROOT'  # Root element, mostly POS=NOUN or PROPN
    pnc = 'pnc'  # punctuation, mostly POS=NOUN or PROPN
    punct = 'punct'  # punctuation, mostly POS=PUNKT
    subtok = 'subtok'  # subtoken (part of a larger token), e.g. 10 in '10-12' - head.text is the right neighbor
    nk = 'nk'  # nk = ????



