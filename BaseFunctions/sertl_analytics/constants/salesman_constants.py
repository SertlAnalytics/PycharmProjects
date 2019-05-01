"""
Description: This module contains the constants used mainly for salesman - but can be used elsewhere.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-09
"""

class SMPR:  # Salesman Processes
    UPDATE_SALES_DAILY = 'Update_Sales_Daily'
    UPDATE_COMPANY_DAILY = 'Update_Company_Daily'

    
class SMVW:  # salesman views
    V_SALE = 'v_sale'
    V_SALE_MAX_VERSION = 'v_sale_max_version'


class SMTBL:  # salesman tables
    SALE = 'Sale'
    COMPANY = 'Company'
    PRODUCT = 'Product'
    OBJECT = 'Object'
    PROCESS = 'Process'
    METRIC = 'Metric'

    @staticmethod
    def get_all():
        return [SMTBL.SALE, SMTBL.COMPANY, SMTBL.PRODUCT, SMTBL.OBJECT, SMTBL.PROCESS, SMTBL.METRIC]

    @staticmethod
    def get_as_options():
        return [{'label': table, 'value': table} for table in SMTBL.get_all()]

    @staticmethod
    def get_for_model_statistics():
        return [SMTBL.SALE]


class DC:  # Data Columns
    ROWID = 'rowid'
    
    
class SLSRC:  # sale sources
    DB = 'Database'
    FILE = 'File'
    ONLINE = 'Online'
    TUTTI_CH = 'Tutti.ch'
    RICARDO_CH = 'Ricardo.ch'
    EBAY_CH = 'Ebay.ch'

    @staticmethod
    def get_my_sale_sources():
        return [SLSRC.DB, SLSRC.FILE]

    @staticmethod
    def get_search_sources():
        return [SLSRC.TUTTI_CH, SLSRC.RICARDO_CH, SLSRC.EBAY_CH]
    
class SLST:  # Sale Status
    OPEN = 'open'
    SOLD = 'sold'
    VANISHED = 'vanished'
    WITHDRAWN = 'withdrawn'
    ON_HOLD = 'onhold'
    
    
class OBJST:  # Object Status
    NEW = 'new'
    USED = 'used'
    NOT_QUALIFIED = 'not qualified'


class CANTON:
    ALL = ['Alle', 'ganze-schweiz']
    AARGAU = ['Aargau', 'aargau']
    APENZELL = ['Apenzell', 'apenzell']
    BASEL = ['Basel', 'basel']
    BERN = ['bern', 'bern']
    FREIBURG = ['Freiburg', 'freiburg']
    GENF = ['Genf', 'genf']
    GLARUS = ['Glarus', 'glarus']
    GRAUBUENDEN = ['Graubünden', 'graubuenden']
    JURA = ['Jura', 'jura']
    LUZERN = ['Luzern', 'luzern']
    NEUENBURG = ['Neuenburg', 'neuenburg']
    NID_OBWALDEN = ['Nid- & Obwalden', 'nid-obwalden']
    SCHAFFHAUSEN = ['Schaffhausen', 'schaffhausen']
    SCHWYZ = ['Schwyz', 'schwyz']
    SOLOTHURN = ['Solothurn', 'soloturn']
    ST_GALLEN = ['St. Gallen', 'st-gallen']
    THURGAU = ['Thurgau', 'thurgau']
    TESSIN = ['Tessin', 'tessin']
    URI = ['Uri', 'uri']
    WAADT = ['Waadt', 'waadt']
    WALLIS = ['Wallis', 'wallis']
    ZUG = ['Zug', 'zug']
    ZUERICH = ['Zürich', 'zuerich']
    LICHTENSTEIN = ['Lichtenstein', 'lichtenstein']
    NUR_DEUTSCH = ['-- nur deutsch--', 'deutsch-schweiz']

    @staticmethod
    def get_all():
        return [CANTON.ALL, CANTON.NUR_DEUTSCH, CANTON.AARGAU, CANTON.APENZELL, 
                CANTON.BASEL, CANTON.BERN, CANTON.FREIBURG, CANTON.GENF, CANTON.GLARUS, CANTON.GRAUBUENDEN,
                CANTON.JURA, CANTON.LUZERN, CANTON.NEUENBURG, CANTON.NID_OBWALDEN, 
                CANTON.SCHAFFHAUSEN, CANTON.SCHWYZ, CANTON.SOLOTHURN, CANTON.ST_GALLEN, 
                CANTON.THURGAU, CANTON.TESSIN, CANTON.URI, CANTON.WAADT, CANTON.WALLIS, CANTON.ZUERICH,
                CANTON.ZUG, CANTON.LICHTENSTEIN
                ]
    

class PRCAT:  # Product Category, german: Rubrik
    ALL = ['Alle', 'angebote']
    ART = ['Antiquitäten & Kunst', 'antiquitaeten-kunst']
    CHILD = ['Baby & Child', 'baby-child']
    BOOKS = ['Bücher', 'buecher']
    BUSINESS = ['Büro & Gewerbe', 'buero-gewerbe']
    COMPUTER = ['Computer & Zubehör', 'computer-zubehoer']
    SERVICE = ['Dienstleistungen', 'dienstleistungen']
    VEHICELS = ['Fahrzeuge', 'fahrzeuge']
    PICTURE = ['Film', 'film']
    PHOTO_VIDEO = ['Foto & Video', 'foto-video']
    GARDEN_CRAFT = ['Garten & Handwerk', 'garten-handwerk']
    HOUSEHOLD = ['Haushalt', 'haushalt']
    REAL_ESTATE = ['Immobilien', 'immobilien']
    CLOTHES_OTHERS = ['Kleidung & Assessoires', 'kleidung-assessoires']
    MUSIC = ['Musik', 'musik']
    COLLECTIONS = ['Sammeln', 'sammeln']
    TOYS = ['Spielzeuge & Basteln', 'spielzeuge-basteln']
    SPORT_OUTDOOR = ['Sport & Outdoor', 'sport-outdoor']
    JOBS = ['Stellenangebote', 'stellenangebote']
    TV_AUDIO = ['TV & Audio', 'tv-audio']
    PHONE_NAVI = ['Telefon & Navigation', 'telefon-navigation']
    TICKETS_BONS = ['Tickets & Gutscheine', 'tickets-gutscheine']
    ANIMALS = ['Tiere', 'tiere']
    OTHERS = ['Sonstiges', 'sonstiges']
    
    @staticmethod
    def get_all():
        return [PRCAT.ALL, PRCAT.ART, PRCAT.CHILD, PRCAT.BOOKS, PRCAT.BUSINESS, PRCAT.COMPUTER,
                PRCAT.SERVICE, PRCAT.VEHICELS, PRCAT.PICTURE, PRCAT.PHOTO_VIDEO, PRCAT.GARDEN_CRAFT,
                PRCAT.HOUSEHOLD, PRCAT.REAL_ESTATE, PRCAT.CLOTHES_OTHERS, PRCAT.MUSIC, PRCAT.COLLECTIONS,
                PRCAT.TOYS, PRCAT.SPORT_OUTDOOR, PRCAT.JOBS, PRCAT.TV_AUDIO, PRCAT.PHONE_NAVI,
                PRCAT.TICKETS_BONS, PRCAT.ANIMALS, PRCAT.OTHERS                
                ]
    
    @staticmethod
    def get_product_category_for_href_part(href_part: str):
        href_part_lower = href_part.lower()
        for category_list in PRCAT.get_all():
            if href_part_lower == category_list[1]:
                return category_list[0]
        return href_part_lower.replace('-', ' & ', 1).capitalize()

    @staticmethod
    def get_product_sub_category_for_href_part(product_category: str, href_part: str):
        href_part_changed = href_part.lower().replace('-', ' & ', 1)
        return href_part_changed.capitalize()
    
    
class SLDC:  # Sale data column
    SALE_ID = 'Sale_ID'
    SALE_ID_MAX = 'Sale_ID_max'
    VERSION = 'Version'
    VERSION_MAX = 'Version_max'
    PRODUCT_CATEGORY = 'Product_Category'  # see PRCAT
    PRODUCT_SUB_CATEGORY = 'Product_SubCategory'  # see PRCAT and below...
    IS_ACTUAL = 'Is_actual'
    MASTER_ID = 'Master_ID'
    MASTER_TITLE = 'Master_Title'
    PRINT_CATEGORY = 'Print_Category'
    SOURCE = 'Source'  # Tutti, Ricardo, etc.
    SALE_STATE = 'Sale_State'  # see SLST
    HREF = 'Link'
    START_DATE = 'Start_Date'
    LOCATION = 'Location'
    OBJECT_STATE = 'Object_State'  # see OBJST
    TITLE = 'Title'
    DESCRIPTION = 'Description'
    PRICE = 'Price'
    PRICE_SINGLE = 'Price_single'
    IS_TOTAL_PRICE = 'Is_total_price'
    PRICE_ORIGINAL = 'Price_orig'
    SIZE = 'Size'
    NUMBER = 'Number'
    IS_NEW = 'Is_new'
    IS_USED = 'Is_used'
    IS_OUTLIER = 'Is_outlier'
    VISITS = 'Visits'
    BOOK_MARKS = 'Bookmarks'
    SEARCH_LABELS = 'Search_labels'
    ENTITY_LABELS = 'Entity_labels'
    ENTITY_LABELS_DICT = 'Entity_labels_dictionary'
    FOUND_BY_LABELS = 'Found_by_labels'
    LAST_CHECK_DATE = 'Last_Check_Date'
    COMMENT = 'Comment'

    @staticmethod
    def get_columns_for_virtual_sales_in_file():
        return [SLDC.SALE_ID, SLDC.TITLE, SLDC.DESCRIPTION, SLDC.PRICE, SLDC.PRICE_ORIGINAL]

    @staticmethod
    def get_columns_for_excel():
        return [SLDC.SALE_ID, SLDC.MASTER_ID, SLDC.SOURCE, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY, 
                SLDC.START_DATE, SLDC.LOCATION, SLDC.OBJECT_STATE,
                SLDC.PRICE, SLDC.PRICE_SINGLE, SLDC.IS_OUTLIER, SLDC.IS_TOTAL_PRICE, SLDC.PRICE_ORIGINAL, SLDC.NUMBER,
                SLDC.SIZE,
                SLDC.TITLE, SLDC.DESCRIPTION,
                SLDC.IS_NEW, SLDC.IS_USED, SLDC.VISITS, SLDC.BOOK_MARKS,
                SLDC.ENTITY_LABELS, SLDC.ENTITY_LABELS_DICT, SLDC.FOUND_BY_LABELS, SLDC.HREF]

    @staticmethod
    def get_columns_for_sales_tab_table():
        return [SLDC.SALE_ID, SLDC.VERSION, SLDC.MASTER_ID, SLDC.SOURCE, SLDC.START_DATE, SLDC.LOCATION, 
                SLDC.OBJECT_STATE, SLDC.PRICE_SINGLE, SLDC.IS_OUTLIER, SLDC.TITLE, SLDC.HREF]

    @staticmethod
    def get_columns_for_sales_printing():
        return [SLDC.SALE_ID, SLDC.VERSION, SLDC.MASTER_ID, SLDC.PRINT_CATEGORY,
                SLDC.SOURCE, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY,
                SLDC.START_DATE, SLDC.LOCATION,
                SLDC.OBJECT_STATE, SLDC.PRICE_SINGLE, SLDC.NUMBER, SLDC.IS_OUTLIER, SLDC.TITLE,
                SLDC.ENTITY_LABELS, SLDC.ENTITY_LABELS_DICT]

    staticmethod

    def get_columns_for_search_results():
        return [SLDC.SALE_ID, SLDC.PRINT_CATEGORY,
                SLDC.SOURCE, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY,
                SLDC.START_DATE, SLDC.LOCATION,
                SLDC.OBJECT_STATE, SLDC.PRICE_SINGLE, SLDC.NUMBER, SLDC.TITLE, SLDC.DESCRIPTION, SLDC.IS_OUTLIER,
                SLDC.ENTITY_LABELS, SLDC.ENTITY_LABELS_DICT, SLDC.HREF]


