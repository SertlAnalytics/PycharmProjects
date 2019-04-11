"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


from sertl_analytics.datafetcher.database_fetcher import MyTable, MyTableColumn, CDT
from sertl_analytics.constants.pattern_constants import DC, PRD, STBL, MDC, PRED, EDC, TPMDC, PRDC
from sertl_analytics.constants.salesman_constants import SMTBL, ODC
from sertl_analytics.mydates import MyDate


class PredictionFeatureTable:
    @staticmethod
    def is_label_column_for_regression(label_column: str):
        return False   # label_column[-4:] == '_PCT'


class ProcessTable(MyTable):
    @staticmethod
    def _get_name_():
        return STBL.PROCESS

    def _add_columns_(self):
        self._columns.append(MyTableColumn(PRDC.PROCESS, CDT.STRING, 50))
        self._columns.append(MyTableColumn(PRDC.TRIGGER, CDT.STRING, 50))
        self._columns.append(MyTableColumn(PRDC.START_DT, CDT.STRING, 10))
        self._columns.append(MyTableColumn(PRDC.START_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(PRDC.END_DT, CDT.STRING, 10))
        self._columns.append(MyTableColumn(PRDC.END_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(PRDC.RUNTIME_SECONDS, CDT.INTEGER))
        self._columns.append(MyTableColumn(PRDC.COMMENT, CDT.STRING, 200))


class OfferTable(MyTable):
    @staticmethod
    def _get_name_():
        return SMTBL.OFFER

    def __get_column_date__(self):
        return EDC.VALID_TO_DT

    def _add_columns_(self):
        self._columns.append(MyTableColumn(ODC.OFFER_ID, CDT.STRING, 10))
        self._columns.append(MyTableColumn(ODC.OFFER_ID_MASTER, CDT.STRING, 10))
        self._columns.append(MyTableColumn(ODC.STATE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(ODC.HREF, CDT.STRING, 150))
        self._columns.append(MyTableColumn(ODC.START_DATE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(ODC.LOCATION, CDT.STRING, 20))
        self._columns.append(MyTableColumn(ODC.DOC_STATE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(ODC.TITLE, CDT.STRING, 100))
        self._columns.append(MyTableColumn(ODC.DESCRIPTION, CDT.STRING, 1000))
        self._columns.append(MyTableColumn(ODC.PRICE, CDT.FLOAT))
        self._columns.append(MyTableColumn(ODC.PRICE_SINGLE, CDT.FLOAT))
        self._columns.append(MyTableColumn(ODC.IS_TOTAL_PRICE, CDT.BOOLEAN))
        self._columns.append(MyTableColumn(ODC.PRICE_ORIGINAL, CDT.FLOAT))
        self._columns.append(MyTableColumn(ODC.SIZE, CDT.STRING, 50))
        self._columns.append(MyTableColumn(ODC.NUMBER, CDT.INTEGER))
        self._columns.append(MyTableColumn(ODC.IS_NEW, CDT.BOOLEAN))
        self._columns.append(MyTableColumn(ODC.IS_USED, CDT.BOOLEAN))
        self._columns.append(MyTableColumn(ODC.IS_OUTLIER, CDT.BOOLEAN))
        self._columns.append(MyTableColumn(ODC.VISITS, CDT.INTEGER))
        self._columns.append(MyTableColumn(ODC.BOOK_MARKS, CDT.INTEGER))
        self._columns.append(MyTableColumn(ODC.SEARCH_LABELS, CDT.STRING, 100))
        self._columns.append(MyTableColumn(ODC.ENTITY_LABELS, CDT.STRING, 100))
        self._columns.append(MyTableColumn(ODC.FOUND_BY_LABELS, CDT.STRING, 100))
        self._columns.append(MyTableColumn(ODC.PRICE_CHANGES, CDT.STRING, 1000))
        self._columns.append(MyTableColumn(ODC.END_DATE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(ODC.END_PRICE, CDT.FLOAT))
        self._columns.append(MyTableColumn(ODC.LAST_CHECK_DATE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(ODC.COMMENT, CDT.STRING, 200))


class MetricTable(MyTable):
    @staticmethod
    def _get_name_():
        return STBL.METRIC

    def _add_columns_(self):
        self._columns.append(MyTableColumn(MDC.VALID_DT, CDT.STRING, 20))
        self._columns.append(MyTableColumn(MDC.MODEL, CDT.STRING, 50))
        self._columns.append(MyTableColumn(MDC.TABLE, CDT.STRING, 50))
        self._columns.append(MyTableColumn(MDC.PREDICTOR, CDT.STRING, 50))
        self._columns.append(MyTableColumn(MDC.LABEL, CDT.STRING, 50))
        self._columns.append(MyTableColumn(MDC.PATTERN_TYPE, CDT.STRING, 50))
        self._columns.append(MyTableColumn(MDC.VALUE, CDT.FLOAT))
        self._columns.append(MyTableColumn(MDC.PRECISION, CDT.FLOAT))
        self._columns.append(MyTableColumn(MDC.RECALL, CDT.FLOAT))
        self._columns.append(MyTableColumn(MDC.F1_SCORE, CDT.FLOAT))
        self._columns.append(MyTableColumn(MDC.ROC_AUC, CDT.FLOAT))

    def __get_key_column_name_list__(self):
        return [MDC.VALID_DT, MDC.TABLE, MDC.PREDICTOR, MDC.LABEL, MDC.PATTERN_TYPE, [MDC.VALUE]]


class CompanyTable(MyTable):
    @staticmethod
    def _get_name_():
        return STBL.COMPANY

    def _add_columns_(self):
        self._columns.append(MyTableColumn(DC.SYMBOL, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.NAME, CDT.STRING, 100))
        self._columns.append(MyTableColumn(DC.TO_BE_LOADED, CDT.BOOLEAN, default=False))
        self._columns.append(MyTableColumn(DC.SECTOR, CDT.STRING, 100))
        self._columns.append(MyTableColumn(DC.YEAR, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.REVENUES, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.EXPENSES, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.EMPLOYEES, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SAVINGS, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.FORECAST_GROWTH, CDT.FLOAT))

    @staticmethod
    def get_select_query(symbol_input='', like_input='') -> str:
        query = 'SELECT * FROM Company'
        if symbol_input != '':
            query += ' WHERE Symbol = "' + symbol_input + '"'
        elif like_input != '':
            query += ' WHERE Symbol like "%' + like_input + '"'
        query += ' ORDER BY Symbol'
        return query

    @staticmethod
    def get_alternate_name(ticker: str, name: str):
        dic_alternate = {'GOOG': 'Alphabeth', 'LBTYK': 'Liberty', 'FOX': 'Twenty-First Century'}
        return dic_alternate[ticker] if ticker in dic_alternate else name

    @staticmethod
    def get_insert_dict_for_company(symbol: str, name: str, to_be_loaded: bool) -> dict:
        return {'Symbol': symbol, 'Name': name, 'ToBeLoaded': to_be_loaded, 'Sector': '', 'Year': 2018, 'Revenues': 0,
                'Expenses': 0, 'Employees': 0, 'Savings': 0, 'ForcastGrowth': 0}

