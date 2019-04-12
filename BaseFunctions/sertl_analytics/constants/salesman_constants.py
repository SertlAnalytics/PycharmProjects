"""
Description: This module contains the constants used mainly for salesman - but can be used elsewhere.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-09
"""

class SMPR:  # Salesman Processes
    UPDATE_OFFER_DAILY = 'Update_Offer_Daily'
    UPDATE_COMPANY_DAILY = 'Update_Company_Daily'

    
class SMVW:  # salesman views
    V_OFFER = 'v_offer'


class SMTBL:  # salesman tables
    OFFER = 'Offer'
    COMPANY = 'Company'
    PRODUCT = 'Product'
    OBJECT = 'Object'
    PROCESS = 'Process'
    METRIC = 'Metric'

    @staticmethod
    def get_all():
        return [SMTBL.OFFER, SMTBL.COMPANY, SMTBL.PRODUCT, SMTBL.OBJECT, SMTBL.PROCESS, SMTBL.METRIC]

    @staticmethod
    def get_as_options():
        return [{'label': table, 'value': table} for table in SMTBL.get_all()]

    @staticmethod
    def get_for_model_statistics():
        return [SMTBL.OFFER]


class DC:  # Data Columns
    ROWID = 'rowid'
    
    
class ODC:  # Offer data column
    OFFER_ID = 'Offer_ID'
    OFFER_ID_MASTER = 'ID_Master'
    STATE = 'State'
    HREF = 'Link'
    START_DATE = 'Start_Date'
    LOCATION = 'Location'
    DOC_STATE = 'Doc_State'
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
    FOUND_BY_LABELS = 'Found_by_labels'
    PRICE_CHANGES = 'Price_Changes'
    END_DATE = 'End_Date'
    END_PRICE = 'End_Price'
    LAST_CHECK_DATE = 'Last_Check_Date'
    COMMENT = 'Comment'

    @staticmethod
    def get_columns_for_virtual_offers_in_file():
        return [ODC.OFFER_ID, ODC.TITLE, ODC.DESCRIPTION, ODC.PRICE]

    @staticmethod
    def get_columns_for_excel():
        return [ODC.OFFER_ID, ODC.OFFER_ID_MASTER, ODC.START_DATE, ODC.LOCATION, ODC.STATE,
                ODC.PRICE, ODC.PRICE_SINGLE, ODC.IS_OUTLIER, ODC.IS_TOTAL_PRICE, ODC.PRICE_ORIGINAL, ODC.NUMBER,
                ODC.SIZE,
                ODC.TITLE, ODC.DESCRIPTION,
                ODC.IS_NEW, ODC.IS_USED, ODC.VISITS, ODC.BOOK_MARKS,
                ODC.SEARCH_LABELS, ODC.ENTITY_LABELS, ODC.FOUND_BY_LABELS, ODC.HREF]
