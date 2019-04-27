"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


from sertl_analytics.datafetcher.database_fetcher import MyView
from sertl_analytics.constants.salesman_constants import SMVW, SLDC, SMTBL
from salesman_database.salesman_tables import SaleTable


class SaleView(MyView):
    @staticmethod
    def __get_name__():
        return SMVW.V_SALE

    @staticmethod
    def __get_select_statement__():
        all_columns = SaleTable().column_name_list
        return "SELECT {} FROM {} JOIN {} ON {}.{}={}.{} AND {}.{}={}.{}".format(
            ','.join(all_columns), SMTBL.SALE, SMVW.V_SALE_MAX_VERSION,
            SMTBL.SALE, SLDC.SALE_ID, SMVW.V_SALE_MAX_VERSION, SLDC.SALE_ID_MAX,
            SMTBL.SALE, SLDC.VERSION, SMVW.V_SALE_MAX_VERSION, SLDC.VERSION_MAX)


class SaleMaxVersionView(MyView):
    @staticmethod
    def __get_name__():
        return SMVW.V_SALE_MAX_VERSION

    @staticmethod
    def __get_select_statement__():
        return "SELECT {} AS {}, MAX({}) AS {} FROM Sale GROUP BY {}".format(
            SLDC.SALE_ID, SLDC.SALE_ID_MAX, SLDC.VERSION, SLDC.VERSION_MAX, SLDC.SALE_ID)

