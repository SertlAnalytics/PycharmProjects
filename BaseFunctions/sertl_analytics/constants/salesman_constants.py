"""
Description: This module contains the constants used mainly for salesman - but can be used elsewhere.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-09
"""

class OUTHDL:  # outlier handling
    KEEP_ALL = 'KEEP_ALL'
    CUT_IQR = 'CUT_IQR'
    CUT_CONFIGURED = 'CUT_CONFIGURED'  # see config parameter outlier_threshold


class EL:  # entity labels
    ANIMAL = 'ANIMAL'
    BLACK_LIST = 'BLACK_LIST'
    CLOTHES = 'CLOTHES'
    COMPANY = 'COMPANY'
    COLOR = 'COLOR'
    EDUCATION = 'EDUCATION'
    ENVIRONMENT = 'ENVIRONMENT'
    JOB = 'JOB'
    LOC = 'LOC'
    MATERIAL = 'MATERIAL'
    ORG = 'ORG'
    OBJECT = 'OBJECT'
    PAYMENT = 'PAYMENT'
    PRODUCT = 'PRODUCT'
    PROPERTY = 'PROPERTY'
    PROPERTY_PART = 'PROPERTY_PART'
    SHOP = 'SHOP'
    TRANSPORT = 'TRANSPORT'
    TARGET_GROUP = 'TARGET_GROUP'
    TECHNOLOGY = 'TECHNOLOGY'
    VEHICLE = 'VEHICLE'
    

    @staticmethod
    def get_all() -> list:
        return [EL.BLACK_LIST, EL.COLOR, EL.ANIMAL, EL.EDUCATION, EL.ENVIRONMENT, EL.JOB, EL.PRODUCT,
                EL.PROPERTY, EL.PROPERTY_PART,
                EL.LOC,
                EL.COMPANY, EL.OBJECT, EL.SHOP,
                EL.TARGET_GROUP, EL.TRANSPORT, EL.MATERIAL, EL.SHOP, EL.TECHNOLOGY, EL.VEHICLE]

    @staticmethod
    def is_entity_label_relevant_for_salesman(ent_level: str) -> bool:
        return ent_level in EL.get_all_relevant()

    @staticmethod
    def get_all_relevant() -> list:
        list_relevant = EL.get_all()
        list_relevant.remove(EL.BLACK_LIST)
        return list_relevant

    @staticmethod
    def get_labels_relevant_for_entity_category_key() -> list:
        return [EL.ANIMAL, EL.JOB, EL.EDUCATION, EL.ENVIRONMENT, EL.MATERIAL,
                EL.OBJECT, EL.PAYMENT, EL.PROPERTY, EL.PROPERTY_PART, EL.SHOP,
                EL.TARGET_GROUP, EL.TECHNOLOGY, EL.TRANSPORT, EL.VEHICLE]

    @staticmethod
    def get_all_without_loc() -> list:
        list_all = EL.get_all()
        list_all.remove(EL.LOC)
        return list_all
    
    
class POS:
    ADJ = 'ADJ'  # adjective, e.g. 'warmes' (Innenfutter)
    ADP = 'ADP'  # AD, e.g. 'in', 'Dank'
    ADV = 'ADV'  # adverb, e.g. 'kaum' (gebraucht)
    CONJ = 'CONJ'  # conjunction
    DATE = 'DATE'  # date, 27.10.1964
    NUM = 'NUM'  # number, e.g. 37
    NOUN = 'NOUN'  # noun, e.g. 'Goretex'
    PART = 'PART'  # partical, e.g. 'zu' (verkaufen)
    PRON = 'PRON'   # pronomen
    PROPN = 'PROPN'  # proper noun, e.g. 'Wanderschuhe'
    PUNCT = 'PUNCT'  # punctuation, e.g. ','
    VERB = 'VERB'  # verb, e.g. 'verkaufen'
    X = 'X'         # X = ???

    @staticmethod
    def is_pos_noun(pos: str) -> bool:
        return pos in [POS.NOUN, POS.PROPN]


class DEP:
    cj = 'cj'  # cj???, e.g. 'LOWA', mostly POS=NOUN or PROPN
    ROOT = 'ROOT'  # Root element, mostly POS=NOUN or PROPN
    pnc = 'pnc'  # punctuation, mostly POS=NOUN or PROPN
    punct = 'punct'  # punctuation, mostly POS=PUNKT
    subtok = 'subtok'  # subtoken (part of a larger token), e.g. 10 in '10-12' - head.text is the right neighbor
    nk = 'nk'  # nk = ????


class SMPR:  # Salesman Processes
    UPDATE_SALES_DATA_IN_STATISTICS_TAB = 'Update_Sales_Data_In_Statistics_Tab'
    CHECK_SALES_STATE = 'Check_Sales_State'
    UPDATE_SIMILAR_SALES_DAILY = 'Update_Similar_Sales'
    CHECK_SIMILAR_SALES_IN_DATABASE = 'Check_Similar_Sales_In_Database'    
    UPDATE_COMPANY_DAILY = 'Update_Company_Daily'

    
class SMVW:  # salesman views
    V_SALE = 'v_sale'
    V_SALE_SIMILAR = 'v_sale_similar'
    V_SALE_MAX_VERSION = 'v_sale_max_version'


class SMTBL:  # salesman tables
    SALE = 'Sale'
    SALE_RELATION = 'Sale_Relation'
    ENTITY_CATEGORY = 'Entity_Category'
    COMPANY = 'Company'
    PRODUCT = 'Product'
    OBJECT = 'Object'
    PROCESS = 'Process'
    METRIC = 'Metric'

    @staticmethod
    def get_all():
        return [SMTBL.SALE, SMTBL.SALE_RELATION, SMTBL.ENTITY_CATEGORY, 
                SMTBL.COMPANY, SMTBL.PRODUCT, SMTBL.OBJECT, SMTBL.PROCESS, SMTBL.METRIC]

    @staticmethod
    def get_as_options():
        return [{'label': table, 'value': table} for table in SMTBL.get_all()]

    @staticmethod
    def get_for_model_statistics():
        return [SMTBL.SALE]


class DC:  # Data Columns
    ROWID = 'rowid'
    
    
class SLSRC:  # sale sources
    ALL = 'All'
    DB = 'Database'
    FILE = 'File'
    ONLINE = 'Online'
    TUTTI_CH = 'Tutti.ch'
    RICARDO_CH = 'Ricardo.ch'
    EBAY_CH = 'Ebay.ch'

    @staticmethod
    def get_sale_sources():
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
    DELETE = 'delete'
    
    
class OBJST:  # Object Status
    NEW = 'new'
    LIKE_NEW = 'like new'
    USED = 'used'
    NOT_QUALIFIED = 'not qualified'


class REGION:
    GANZE_SCHWEIZ = 'Ganze Schweiz'
    AARGAU = 'Aargau'
    APPENZELL = 'Appenzell'
    BASEL = 'Basel'
    BASEL_STADT = 'Basel-Stadt'
    BERN = 'Bern'
    FREIBURG = 'Freiburg'
    GENF = 'Genf'
    GLARUS = 'Glarus'
    GRAUBUENDEN = 'Graubünden'
    JURA = 'Jura'
    LUZERN = 'Luzern'
    NEUENBURG = 'Neuenburg'
    NID_OBWALDEN = 'Nid- & Obwalden'
    SCHAFFHAUSEN = 'Schaffhausen'
    SCHWYZ = 'Schwyz'
    SOLOTHURN = 'Solothurn'
    ST_GALLEN = 'St. Gallen'
    THURGAU = 'Thurgau'
    TESSIN = 'Tessin'
    URI = 'Uri'
    WAADT = 'Waadt'
    WALLIS = 'Wallis'
    ZUG = 'Zug'
    ZUERICH = 'Zürich'
    LICHTENSTEIN = 'Lichtenstein'
    DEUTSCH_SCHWEIZ = 'Deutsch-Schweiz'

    @staticmethod
    def get_regions_for_tutti_search():
        return [
            REGION.GANZE_SCHWEIZ, REGION.AARGAU, REGION.DEUTSCH_SCHWEIZ, REGION.APPENZELL,
            REGION.BASEL, REGION.BASEL_STADT, REGION.BERN, REGION.FREIBURG, 
            REGION.GENF, REGION.GLARUS, REGION.GRAUBUENDEN,
            REGION.JURA, REGION.LUZERN, REGION.NEUENBURG, REGION.NID_OBWALDEN,
            REGION.SCHAFFHAUSEN, REGION.SCHWYZ, REGION.SOLOTHURN, REGION.ST_GALLEN,
            REGION.THURGAU, REGION.TESSIN, REGION.URI, REGION.WAADT, REGION.WALLIS, REGION.ZUERICH,
            REGION.ZUG, REGION.LICHTENSTEIN
        ]
    

class OBJPROP:  # Object properties
    SIZE = 'Size'
    NUMBER = 'Number'
    AGE = 'Age'
    YEAR = 'Year'
    USAGE = 'Usage'
    WARRANTY = 'Warrenty until'
    ORIGINAL_COVER = 'Cover available'
    SALE_TYPE = 'Type'
    

class SLDC:  # Sale data column
    ROW_ID = 'rowid'
    SALE_ID = 'Sale_ID'
    SALE_ID_MAX = 'Sale_ID_max'
    VERSION = 'Version'
    VERSION_MAX = 'Version_max'
    REGION = 'Region'  # see REGION
    PRODUCT_CATEGORY = 'Product_Category'  # see PRCAT
    PRODUCT_SUB_CATEGORY = 'Product_SubCategory'  # see PRCAT and below...
    IS_ACTUAL = 'Is_actual'
    MASTER_ID = 'Master_ID'
    CHILD_ID = 'Child_ID'
    ENTITY_LIST = 'Entity_List'
    CATEGORY_LIST = 'Category_List'
    RELATION_STATE = 'Relation_State'
    STATE_DATE = 'State_Date'
    MASTER_TITLE = 'Master_Title'
    PLOT_CATEGORY = 'Plot_Category'
    SOURCE = 'Source'  # Tutti, Ricardo, etc.
    SALE_STATE = 'Sale_State'  # see SLST
    HREF = 'Link'
    START_DATE = 'Start_Date'
    END_DATE = 'End_Date'
    LOCATION = 'Location'
    OBJECT_STATE = 'Object_State'  # see OBJST
    TITLE = 'Title'
    DESCRIPTION = 'Description'
    MATERIAL = 'Material'
    LOCATIONS_ALL = 'Locations_All'
    COLORS = 'COLORS'
    JOBS = 'JOBS'
    PROPERTY_DICT = 'Properties'
    PRICE = 'Price'
    PRICE_SINGLE = 'Price_single'
    PRICE_NEW = 'Price_new'
    IS_TOTAL_PRICE = 'Is_total_price'
    IS_SINGLE_PRICE = 'Is_single_price'
    PRICE_ORIGINAL = 'Price_orig'
    SIZE = 'Size'
    NUMBER = 'Number'
    IS_NEW = 'Is_new'
    IS_LIKE_NEW = 'Is_like_new'
    IS_USED = 'Is_used'
    IS_OUTLIER = 'Is_outlier'
    IS_MY_SALE = 'Is_my_sale'
    VISITS = 'Visits'
    BOOK_MARKS = 'Bookmarks'
    SEARCH_LABELS = 'Search_labels'
    ENTITY_LABELS = 'Entity_labels'
    ENTITY_LABELS_DICT = 'Entity_labels_dictionary'
    ENTITY_LABELS_DICT_4_EXCEL = 'Entity_labels_dictionary_4_Excel'
    FOUND_BY_LABELS = 'Found_by_labels'
    LAST_CHECK_DATE = 'Last_Check_Date'
    COMMENT = 'Comment'
    IS_VALID_FOR_SELECTION = 'Is_Valid_For_Selection'
   
    @staticmethod
    def get_columns_for_virtual_sales_in_file():
        return [SLDC.SALE_ID, SLDC.TITLE, SLDC.DESCRIPTION, SLDC.PRICE, SLDC.PRICE_ORIGINAL]

    @staticmethod
    def get_columns_for_excel():
        return [SLDC.SALE_ID, SLDC.MASTER_ID, SLDC.SOURCE, SLDC.SALE_STATE, 
                SLDC.REGION, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY,
                SLDC.START_DATE, SLDC.LOCATION, SLDC.LOCATIONS_ALL, SLDC.COLORS, SLDC.OBJECT_STATE,
                SLDC.IS_NEW, SLDC.IS_LIKE_NEW, SLDC.IS_USED,
                SLDC.PRICE, SLDC.PRICE_SINGLE, SLDC.IS_OUTLIER, SLDC.IS_TOTAL_PRICE, SLDC.PRICE_ORIGINAL, SLDC.NUMBER,
                SLDC.SIZE, SLDC.MATERIAL, SLDC.PROPERTY_DICT,
                SLDC.TITLE, SLDC.DESCRIPTION,
                SLDC.VISITS, SLDC.BOOK_MARKS,
                SLDC.ENTITY_LABELS, SLDC.ENTITY_LABELS_DICT_4_EXCEL, SLDC.FOUND_BY_LABELS, SLDC.HREF]

    @staticmethod
    def get_columns_for_sales_tab_table():
        return [SLDC.SALE_ID, SLDC.VERSION, SLDC.SALE_STATE,
                SLDC.SOURCE, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY,
                SLDC.START_DATE, SLDC.OBJECT_STATE, SLDC.PRICE_SINGLE, SLDC.TITLE]

    @staticmethod
    def get_columns_for_similar_sales_tab_table():
        return [SLDC.SALE_ID, SLDC.VERSION, SLDC.SALE_STATE,
                SLDC.SOURCE, SLDC.REGION, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY,
                SLDC.START_DATE, SLDC.OBJECT_STATE, SLDC.PRICE_SINGLE, SLDC.IS_OUTLIER,
                SLDC.TITLE, SLDC.HREF, SLDC.MASTER_ID]

    @staticmethod
    def get_columns_for_sales_plotting():
        return [SLDC.SALE_ID, SLDC.VERSION, SLDC.MASTER_ID, SLDC.PLOT_CATEGORY,
                SLDC.SOURCE, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY,
                SLDC.START_DATE, SLDC.LOCATION,
                SLDC.OBJECT_STATE, SLDC.PRICE_SINGLE, SLDC.NUMBER, SLDC.IS_OUTLIER, SLDC.TITLE,
                SLDC.ENTITY_LABELS, SLDC.ENTITY_LABELS_DICT]

    staticmethod

    def get_columns_for_search_results():
        return [SLDC.SALE_ID,
                SLDC.SOURCE, SLDC.REGION, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY,
                SLDC.START_DATE, SLDC.LOCATION, SLDC.IS_OUTLIER,
                SLDC.OBJECT_STATE, SLDC.PRICE_SINGLE, SLDC.NUMBER, SLDC.TITLE, SLDC.DESCRIPTION,
                SLDC.MATERIAL, SLDC.PROPERTY_DICT,
                SLDC.ENTITY_LABELS, SLDC.ENTITY_LABELS_DICT, SLDC.HREF]


