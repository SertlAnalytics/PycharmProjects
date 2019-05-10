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
    
    
class OBJST:  # Object Status
    NEW = 'new'
    LIKE_NEW = 'like new'
    USED = 'used'
    NOT_QUALIFIED = 'not qualified'


class REGION:
    GANZE_SCHWEIZ = 'Ganze Schweiz'
    AARGAU = 'Aargau'
    APENZELL = 'Apenzell'
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
            REGION.GANZE_SCHWEIZ, REGION.AARGAU, REGION.DEUTSCH_SCHWEIZ, REGION.APENZELL,
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
    WARRANTY = 'Warrenty until'
    ORIGINAL_COVER = 'Cover available'    

class SLDC:  # Sale data column
    SALE_ID = 'Sale_ID'
    SALE_ID_MAX = 'Sale_ID_max'
    VERSION = 'Version'
    VERSION_MAX = 'Version_max'
    REGION = 'Region'  # see REGION
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
    MATERIAL = 'Material'
    PROPERTY_DICT = 'Properties'
    PRICE = 'Price'
    PRICE_SINGLE = 'Price_single'
    PRICE_NEW = 'Price_new'
    IS_TOTAL_PRICE = 'Is_total_price'
    PRICE_ORIGINAL = 'Price_orig'
    SIZE = 'Size'
    NUMBER = 'Number'
    IS_NEW = 'Is_new'
    IS_LIKE_NEW = 'Is_like_new'
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
        return [SLDC.SALE_ID, SLDC.MASTER_ID, SLDC.SOURCE,
                SLDC.REGION, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY,
                SLDC.START_DATE, SLDC.LOCATION, SLDC.OBJECT_STATE,
                SLDC.IS_NEW, SLDC.IS_LIKE_NEW, SLDC.IS_USED,
                SLDC.PRICE, SLDC.PRICE_SINGLE, SLDC.IS_OUTLIER, SLDC.IS_TOTAL_PRICE, SLDC.PRICE_ORIGINAL, SLDC.NUMBER,
                SLDC.SIZE, SLDC.MATERIAL, SLDC.PROPERTY_DICT,
                SLDC.TITLE, SLDC.DESCRIPTION,
                SLDC.VISITS, SLDC.BOOK_MARKS,
                SLDC.ENTITY_LABELS, SLDC.ENTITY_LABELS_DICT, SLDC.FOUND_BY_LABELS, SLDC.HREF]

    @staticmethod
    def get_columns_for_sales_tab_table():
        return [SLDC.SALE_ID, SLDC.VERSION,
                SLDC.SOURCE, SLDC.REGION, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY,
                SLDC.START_DATE, SLDC.OBJECT_STATE, SLDC.PRICE_SINGLE, SLDC.TITLE, SLDC.HREF]

    @staticmethod
    def get_columns_for_similar_sales_tab_table():
        return [SLDC.SALE_ID, SLDC.VERSION,
                SLDC.SOURCE, SLDC.REGION, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY,
                SLDC.START_DATE, SLDC.OBJECT_STATE, SLDC.PRICE_SINGLE, SLDC.TITLE, SLDC.HREF, SLDC.MASTER_ID]

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
                SLDC.SOURCE, SLDC.REGION, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY,
                SLDC.START_DATE, SLDC.LOCATION, SLDC.IS_OUTLIER,
                SLDC.OBJECT_STATE, SLDC.PRICE_SINGLE, SLDC.NUMBER, SLDC.TITLE, SLDC.DESCRIPTION,
                SLDC.MATERIAL, SLDC.PROPERTY_DICT,
                SLDC.ENTITY_LABELS, SLDC.ENTITY_LABELS_DICT, SLDC.HREF]


