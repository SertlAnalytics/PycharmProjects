"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


from sertl_analytics.datafetcher.database_fetcher import MyView
from sertl_analytics.constants.salesman_constants import SMVW, ODC
from salesman_database.salesman_tables import OfferTable


class OfferView(MyView):
    @staticmethod
    def __get_name__():
        return SMVW.V_OFFER

    @staticmethod
    def __get_select_statement__():
        all_columns = OfferTable().column_name_list
        all_columns.remove(ODC.DESCRIPTION)
        return "SELECT {} FROM Offer".format(','.join(all_columns))

