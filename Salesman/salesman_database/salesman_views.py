"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


from sertl_analytics.datafetcher.database_fetcher import MyView
from sertl_analytics.constants.salesman_constants import SMVW, SLDC
from salesman_database.salesman_tables import SaleTable


class SaleView(MyView):
    @staticmethod
    def __get_name__():
        return SMVW.V_SALE

    @staticmethod
    def __get_select_statement__():
        all_columns = SaleTable().column_name_list
        all_columns.remove(SLDC.DESCRIPTION)
        return "SELECT {} FROM Sale".format(','.join(all_columns))

