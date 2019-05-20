"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


from sertl_analytics.datafetcher.database_fetcher import MyView
from sertl_analytics.constants.salesman_constants import SMVW, SLDC, SMTBL
from salesman_database.salesman_tables import SaleTable


# class SaleView(MyView):
#     @staticmethod
#     def __get_name__():
#         return SMVW.V_SALE
#
#     @staticmethod
#     def __get_select_statement__():
#         all_columns = ['{}.{}'.format(SMTBL.SALE, SLDC.ROW_ID)] + SaleTable().column_name_list
#         # all_columns.remove(SLDC.DESCRIPTION)
#         return "SELECT {} FROM {} JOIN {} ON {}.{}={}.{} AND {}.{}={}.{}".format(
#             ','.join(all_columns), SMTBL.SALE, SMVW.V_SALE_MAX_VERSION,
#             SMTBL.SALE, SLDC.SALE_ID, SMVW.V_SALE_MAX_VERSION, SLDC.SALE_ID_MAX,
#             SMTBL.SALE, SLDC.VERSION, SMVW.V_SALE_MAX_VERSION, SLDC.VERSION_MAX)


class SaleView(MyView):
    @staticmethod
    def __get_name__():
        return SMVW.V_SALE

    @staticmethod
    def __get_select_statement__():
        columns_from_sale = SaleTable().column_name_list
        all_columns = ['{}.{}'.format(SMTBL.SALE, SLDC.ROW_ID),
                       '{}.{}'.format(SMTBL.SALE, SLDC.SALE_ID),
                       '{}.{}'.format(SMTBL.SALE, SLDC.VERSION),
                       '{}.{}'.format(SMTBL.SALE_RELATION, SLDC.MASTER_ID),
                       ]
        # add the remaining columns from the sale table
        for column in columns_from_sale:
            if column not in [SLDC.SALE_ID, SLDC.VERSION]:
                all_columns.append('{}.{}'.format(SMTBL.SALE, column))
        # create select statement
        return "SELECT {} FROM {} JOIN {} ON {}.{}={}.{} AND {}.{}={}.{} LEFT JOIN {} ON {}.{}={}.{} AND {}.{}=''".format(
            ','.join(all_columns), SMTBL.SALE, SMVW.V_SALE_MAX_VERSION,
            SMTBL.SALE, SLDC.SALE_ID, SMVW.V_SALE_MAX_VERSION, SLDC.SALE_ID_MAX,
            SMTBL.SALE, SLDC.VERSION, SMVW.V_SALE_MAX_VERSION, SLDC.VERSION_MAX,
            SMTBL.SALE_RELATION,
            SMTBL.SALE, SLDC.SALE_ID, SMTBL.SALE_RELATION, SLDC.CHILD_ID,
            SMTBL.SALE_RELATION, SLDC.END_DATE
        )


class SaleMaxVersionView(MyView):
    @staticmethod
    def __get_name__():
        return SMVW.V_SALE_MAX_VERSION

    @staticmethod
    def __get_select_statement__():
        return "SELECT {} AS {}, MAX({}) AS {} FROM Sale GROUP BY {}".format(
            SLDC.SALE_ID, SLDC.SALE_ID_MAX, SLDC.VERSION, SLDC.VERSION_MAX, SLDC.SALE_ID)

