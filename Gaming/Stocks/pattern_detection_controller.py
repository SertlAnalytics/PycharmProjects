"""
Description: This module detects pattern from any kind of input stream.
In the first version we concentrate our target on identifying stock pattern by given formation types.
In the second version we allow the system to find own patterns or change existing pattern constraints.
The main algorithm is CSP (constraint satisfaction problems) with binary constraints.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import pandas as pd
import numpy as np
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, AlphavantageCryptoFetcher\
    , ApiPeriod, CryptoCompareCryptoFetcher
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList
from sertl_analytics.pybase.date_time import MyClock
from sertl_analytics.user_input.confirmation import UserInput
from datetime import timedelta
from sertl_analytics.pybase.date_time import MyPyDate
from sertl_analytics.pybase.loop_list import LL, LoopList4Dictionaries
from sertl_analytics.constants.pattern_constants import PSC, Indices, CN
from pattern_configuration import config, runtime
from pattern_statistics import PatternStatistics, DetectorStatistics
from pattern_data_container import pattern_data_handler
from pattern_detector import PatternDetector
from pattern_plotter import PatternPlotter
from pattern_database import stock_database
import matplotlib.dates as mdt
from datetime import datetime

"""
Implementation steps:
1. Define a framework for CSPs: Unary, Binary, Global, Preferences
2. The solver should be domain independent (i.e. it doesn't matter to check stock markets or health data...)
3. Node consistency, Arc-consistency, Path consistency.
Recall:
a) A constraint satisfaction problem consists of three components:
a.1) A set of variables X = {X1, X2, ..., Xn}
a.2) A set of domains for each variable: D = {D1, D2, ..., Dn)
a.3) A set of constraints C that specifies allowable combinations of values
b) Solving the CSP: Finding the assignment(s) that satisfy all constraints.
c) Concepts: problem formulation, backtracking search, arc consistence, etc
d) We call a solution a consistent assignment
e) Factored representation: Each state has some attribute-value properties, e.g. GPS location (properties = features)
"""


class PatternDetectionController:
    def __init__(self):
        self.detector_statistics = DetectorStatistics()
        self.pattern_statistics = PatternStatistics()
        self.stock_db = None
        self.__excel_file_with_test_data = ''
        self.df_test_data = None
        self.__loop_list_ticker = None  # format of an entry (ticker, and_clause, number)
        self.__start_row = 0
        self.__end_row = 0
        self.__crypto_ccy_dic = IndicesComponentList.get_ticker_name_dic(Indices.CRYPTO_CCY)

    def run_pattern_checker(self, excel_file_with_test_data: str = '', start_row: int = 1, end_row: int = 0):
        self.__init_db_and_test_data__(excel_file_with_test_data, start_row, end_row)
        self.__init_loop_list_for_ticker__()

        for value_dic in self.__loop_list_ticker.value_list:
            ticker = value_dic[LL.TICKER]
            self.__update_runtime_parameters__(value_dic)
            print('\nProcessing {} ({})...\n'.format(ticker, runtime.actual_ticker_name))
            df_data = self.__get_df_from_source__(ticker, value_dic)
            pattern_data_handler.init_by_df(df_data)
            detector = PatternDetector()
            detector.parse_for_pattern()
            detector.parse_for_fibonacci_waves()
            detector.check_for_intersections()

            self.__handle_statistics__(detector)

            if config.plot_data:
                if len(detector.pattern_list) == 0 and False:  # and not detector.possible_pattern_ranges_available:
                    print('...no formations found.')
                else:
                    plotter = PatternPlotter(detector)
                    plotter.plot_data_frame()

            if value_dic[LL.NUMBER] >= config.max_number_securities:
                break

        if config.show_final_statistics:
            self.__show_statistics__()

    def __get_df_from_source__(self, ticker, value_dic):
        if config.get_data_from_db:
            self.__handle_not_available_symbol__(ticker)
            and_clause = value_dic[LL.AND_CLAUSE]
            stock_db_df_obj = stock_database.StockDatabaseDataFrame(self.stock_db, ticker, and_clause)
            return stock_db_df_obj.df_data
        elif ticker in self.__crypto_ccy_dic:
            if config.api_period == ApiPeriod.INTRADAY:
                fetcher = CryptoCompareCryptoFetcher(ticker, config.api_period)
            else:
                fetcher = AlphavantageCryptoFetcher(ticker, config.api_period)
            return fetcher.df_data
        else:
            aggregation = 5 if config.api_period == ApiPeriod.INTRADAY else 1
            fetcher = AlphavantageStockFetcher(ticker, config.api_period, aggregation, config.api_output_size)
            if config.api_period == ApiPeriod.INTRADAY:
                return self.__get_with_concatenated_intraday_data__(fetcher.df_data)
            else:
                return fetcher.df_data

    def __get_with_concatenated_intraday_data__(self, df: pd.DataFrame):
        # df['time'] = df['time'].apply(datetime.fromtimestamp)
        df[CN.TIMESTAMP] = df.index.map(int)
        epoch_seconds_number = df.shape[0]
        epoch_seconds_max = df[CN.TIMESTAMP].max()
        epoch_seconds_diff = df.iloc[-1][CN.TIMESTAMP] - df.iloc[-2][CN.TIMESTAMP]
        epoch_seconds_end = epoch_seconds_max
        epoch_seconds_start = epoch_seconds_end - (epoch_seconds_number - 1) * epoch_seconds_diff
        time_series = np.linspace(epoch_seconds_start, epoch_seconds_end, epoch_seconds_number)
        df[CN.TIMESTAMP] = time_series
        df.set_index(CN.TIMESTAMP, drop=True, inplace=True)
        return df


    def __handle_not_available_symbol__(self, ticker):
        if not self.stock_db.is_symbol_loaded(ticker):
            if UserInput.get_confirmation('{} is not available. Do you want to load it'.format(ticker)):
                name = UserInput.get_input('Please enter the name for the symbol {}'.format(ticker))
                if name == 'x':
                    exit()
                self.stock_db.update_stock_data_for_symbol(ticker, name)
            else:
                exit()

    def __update_runtime_parameters__(self, entry_dic: dict):
        runtime.actual_ticker = entry_dic[LL.TICKER]
        runtime.actual_and_clause = entry_dic[LL.AND_CLAUSE]
        runtime.actual_number = entry_dic[LL.NUMBER]
        if self.stock_db is not None:
            runtime.actual_ticker_name = self.stock_db.get_name_for_symbol(entry_dic[LL.TICKER])
        if runtime.actual_ticker_name == '':
            runtime.actual_ticker_name = config.ticker_dic[entry_dic[LL.TICKER]]

    def __show_statistics__(self):
        config.print()
        if config.statistics_excel_file_name == '':
            self.pattern_statistics.print_overview()
            self.detector_statistics.print_overview()
        else:
            writer = pd.ExcelWriter(config.statistics_excel_file_name)
            self.pattern_statistics.write_to_excel(writer, 'Formations')
            self.detector_statistics.write_to_excel(writer, 'Overview')
            print('Statistics were written to file: {}'.format(config.statistics_excel_file_name))
            writer.save()

    def __init_db_and_test_data__(self, excel_file_with_test_data: str, start_row: int, end_row: int):
        self.stock_db = stock_database.StockDatabase()
        if config.get_data_from_db:
            if excel_file_with_test_data != '':
                self.__excel_file_with_test_data = excel_file_with_test_data
                self.df_test_data = pd.ExcelFile(self.__excel_file_with_test_data).parse(0)
                self.__start_row = start_row
                self.__end_row = self.df_test_data.shape[0] if end_row == 0 else end_row

    def __init_loop_list_for_ticker__(self):
        self.__loop_list_ticker = LoopList4Dictionaries()
        if config.get_data_from_db and self.__excel_file_with_test_data != '':
            for ind, rows in self.df_test_data.iterrows():
                if self.__loop_list_ticker.counter >= self.__start_row:
                    config.ticker_dic[rows[PSC.TICKER]] = rows[PSC.NAME]
                    start_date = MyPyDate.get_date_from_datetime(rows[PSC.BEGIN_PREVIOUS])
                    date_end = MyPyDate.get_date_from_datetime(rows[PSC.END] + timedelta(days=rows[PSC.T_NEEDED] + 20))
                    and_clause = "Date BETWEEN '{}' AND '{}'".format(start_date, date_end)
                    self.__loop_list_ticker.append({LL.TICKER: rows[PSC.TICKER], LL.AND_CLAUSE: and_clause})
                if self.__loop_list_ticker.counter >= self.__end_row:
                    break
        else:
            for ticker in config.ticker_dic:
                self.__loop_list_ticker.append({LL.TICKER: ticker, LL.AND_CLAUSE: config.and_clause})

    def __handle_statistics__(self, detector: PatternDetector):
        for pattern in detector.pattern_list:
            self.pattern_statistics.add_entry(pattern)

        if config.show_final_statistics:
            self.detector_statistics.add_entry(detector.get_statistics_api())
        else:
            detector.print_statistics()
