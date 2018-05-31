"""
Description: This module contains the configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import sertl_analytics.environment  # init some environment variables during load - for security reasons
from pattern_constants import FT, Indices, CN
import stock_database as sdb
from sertl_analytics.datafetcher.financial_data_fetcher import ApiOutputsize, ApiPeriod
from sertl_analytics.datafetcher.file_fetcher import NasdaqFtpFileFetcher
from sertl_analytics.pybase.df_base import PyBaseDataFrame
from sertl_analytics.datafetcher.database_fetcher import DatabaseDataFrame


class RuntimeConfiguration:
    actual_list = []
    actual_position = 0
    actual_tick_position = 0
    actual_number = 0
    actual_ticker = ''
    actual_ticker_name = ''
    actual_and_clause = ''
    actual_pattern_type = FT.NONE
    actual_breakout = None


class PatternConfiguration:
    def __init__(self):
        self.get_data_from_db = True
        self.pattern_type_list = [FT.CHANNEL]
        self.api_period = ApiPeriod.DAILY
        self.api_output_size = ApiOutputsize.COMPACT
        self.bound_upper_value = CN.HIGH
        self.bound_lower_value = CN.LOW
        self.plot_data = True
        self.range_detector_tolerance_pct = 0.01
        self.check_previous_period = False   # default
        self.breakout_over_congestion_range = False
        self.breakout_range_pct = 0.05
        self.investment = 1000
        self.max_number_securities = 1000
        self.show_final_statistics = True
        self.and_clause = "Date BETWEEN '2017-12-01' AND '2019-12-31'"
        self.runtime = RuntimeConfiguration()
        self.statistics_excel_file_name = ''
        self.ticker_dic = {}
        self.__previous_period_length = 0

    def __get_previous_period_length__(self):
        return self.__previous_period_length

    def __set_previous_period_length__(self, value: int):
        self.__previous_period_length = value

    previous_period_length = property(__get_previous_period_length__, __set_previous_period_length__)

    def print(self):
        source = 'DB' if self.get_data_from_db else 'Api'
        pattern_type = self.pattern_type_list
        and_clause = self.and_clause
        period = self.api_period
        output_size = self.api_output_size
        bound_upper_v = self.bound_upper_value
        bound_lower_v = self.bound_lower_value
        breakout_over_big_range = self.breakout_over_congestion_range

        print('\nConfiguration settings:')
        if self.get_data_from_db:
            print('Formation: {} \nSource: {} \nAnd clause: {} \nUpper/Lower Bound Value: {}/{}'
                  ' \nBreakout big range: {}\n'.format(
                    pattern_type, source, and_clause, bound_upper_v, bound_lower_v, breakout_over_big_range))
        else:
            print('Formation: {} \nSource: {} \n\nApiPeriod/ApiOutput size: {}/{} \nUpper/Lower Bound Value: {}/{}'
                  ' \nBreakout big range: {}\n'.format(
                    pattern_type, source, period, output_size, bound_upper_v, bound_lower_v, breakout_over_big_range))

    def use_index(self, index: Indices):
        if index == Indices.DOW_JONES:
            self.ticker_dic = self.get_dow_jones_dic()
        elif index == Indices.NASDAQ:
            self.ticker_dic = self.get_nasdaq_dic()
        elif index == Indices.ALL_DATABASE:
            self.ticker_dic = self.get_all_in_database()
        else:
            self.ticker_dic = self.get_mixed_dic()

    def use_own_dic(self, dic: dict):
        self.ticker_dic = dic

    @staticmethod
    def get_dow_jones_dic():
        return {"MMM": "3M", "AXP": "American", "AAPL": "Apple", "BA": "Boing",
                "CAT": "Caterpillar", "CVX": "Chevron", "CSCO": "Cisco", "KO": "Coca-Cola",
                "DIS": "Disney", "DWDP": "DowDuPont", "XOM": "Exxon", "GE": "General",
                "GS": "Goldman", "HD": "Home", "IBM": "IBM", "INTC": "Intel",
                "JNJ": "Johnson", "JPM": "JPMorgan", "MCD": "McDonald's", "MRK": "Merck",
                "MSFT": "Microsoft", "NKE": "Nike", "PFE": "Pfizer", "PG": "Procter",
                "TRV": "Travelers", "UTX": "United", "UNH": "UnitedHealth", "VZ": "Verizon",
                "V": "Visa", "WMT": "Wal-Mart"}

    @staticmethod
    def get_nasdaq_dic():
        """
        Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares
        AABA|Altaba Inc. - Common Stock|Q|N|N|100|N|N
        """
        ftp_fetcher = NasdaqFtpFileFetcher()
        df = ftp_fetcher.get_data_frame()
        return PyBaseDataFrame.get_rows_as_dictionary(df, 'Symbol', ['Security Name'], {'Market Category': 'Q'})

    @staticmethod
    def get_mixed_dic():
        return {"TSLA": "Tesla", "FCEL": "Full Cell", "ONVO": "Organovo", "MRAM": "MRAM"}

    @staticmethod
    def get_all_in_database():
        stock_db = sdb.StockDatabase()
        db_data_frame = DatabaseDataFrame(
            stock_db, query='SELECT Symbol, count(*) FROM Stocks GROUP BY Symbol HAVING count(*) > 4000')
        return PyBaseDataFrame.get_rows_as_dictionary(db_data_frame.df, 'Symbol', ['Symbol'])