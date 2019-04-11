"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


from sertl_analytics.datafetcher.database_fetcher import MyView
from sertl_analytics.constants.salesman_constants import SMVW


class OfferView(MyView):
    @staticmethod
    def __get_name__():
        return SMVW.V_OFFER

    @staticmethod
    def __get_select_statement__():
        index_column = "CASE WHEN E.Exchange = 'Bitfinex' THEN 'Crypto Currencies' ELSE E.Exchange END as Equity_Index"
        wave_end_date_column = "substr(W.Wave_End_Datetime, 1, 10) AS Wave_End_Date"
        return "SELECT {}, {}, W.* FROM Wave as W JOIN Equity AS E ON E.KEY = W.Ticker_ID".format(
            index_column, wave_end_date_column
        )

