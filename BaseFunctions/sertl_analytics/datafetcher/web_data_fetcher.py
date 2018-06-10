"""
Description: This module contains fetcher classes for data from the web (XML parsing, FTP).
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import Indices
from sertl_analytics.pybase.exceptions import MyException
from sertl_analytics.datafetcher.xml_parser import XMLParser4DowJones, XMLParser4Nasdaq100, XMLParser4SP500
from sertl_analytics.datafetcher.file_fetcher import NasdaqFtpFileFetcher
from sertl_analytics.pybase.df_base import PyBaseDataFrame


class IndicesComponentList:
    @staticmethod
    def get_ticker_name_dic(index: str):
        if index == Indices.DOW_JONES:
            parser = XMLParser4DowJones()
            return parser.get_result_dic()
        elif index == Indices.SP500:
            parser = XMLParser4SP500()
            return parser.get_result_dic()
        elif index == Indices.NASDAQ100:
            parser = XMLParser4Nasdaq100()
            return parser.get_result_dic()
        elif index == Indices.NASDAQ:
            ftp_fetcher = NasdaqFtpFileFetcher()
            df = ftp_fetcher.get_data_frame()
            return PyBaseDataFrame.get_rows_as_dictionary(df, 'Symbol', ['Security Name'], {'Market Category': 'Q'})
        elif index == Indices.MIXED:
            return {"TSLA": "Tesla", "FCEL": "Full Cell", "ONVO": "Organovo", "MRAM": "MRAM"}
        else:
            raise MyException('No index fetcher defined for "{}"'.format(index))