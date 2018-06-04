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
import sertl_analytics.environment  # init some environment variables during load - for security reasons
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, ApiPeriod, ApiOutputsize
import stock_database
from datetime import timedelta
from sertl_analytics.pybase.date_time import MyPyDate
from sertl_analytics.pybase.loop_list import LL, LoopList4Dictionaries
from pattern_constants import FT, Indices, CN, PSC
from pattern_configuration import PatternConfiguration
from pattern_statistics import PatternStatistics, DetectorStatistics
from pattern_data_container import PatternDataContainer
from pattern_detector import PatternDetector
from pattern_plotter import PatternPlotter

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


class PatternController:
    def __init__(self, config: PatternConfiguration):
        self.config = config
        self.detector_statistics = DetectorStatistics()
        self.pattern_statistics = PatternStatistics()
        self.stock_db = None
        self.__excel_file_with_test_data = ''
        self.df_test_data = None
        self.__loop_list_ticker = None  # format of an entry (ticker, and_clause, number)
        self.__start_row = 0
        self.__end_row = 0

    def run_pattern_checker(self, excel_file_with_test_data: str = '', start_row: int = 1, end_row: int = 0):
        self.__init_db_and_test_data__(excel_file_with_test_data, start_row, end_row)
        self.__init_loop_list_for_ticker__()

        for value_dic in self.__loop_list_ticker.value_list:
            ticker = value_dic[LL.TICKER]
            self.__add_runtime_parameter_to_config__(value_dic)
            print('\nProcessing {} ({})...\n'.format(ticker, self.config.runtime.actual_ticker_name))
            df_data = self.__get_df_from_source__(ticker, value_dic)
            data_container = PatternDataContainer(df_data)
            detector = PatternDetector(data_container, self.config)
            detector.parse_for_pattern()
            self.__handle_statistics__(detector)

            if self.config.plot_data:
                if len(detector.pattern_list) == 0: # and not detector.possible_pattern_ranges_available:
                    print('...no formations found.')
                else:
                    plotter = PatternPlotter(data_container, detector, self.config)
                    plotter.plot_data_frame()

            if value_dic[LL.NUMBER] >= self.config.max_number_securities:
                break

        if config.show_final_statistics:
            self.__show_statistics__()

    def __get_df_from_source__(self, ticker, value_dic):
        if config.get_data_from_db:
            and_clause = value_dic[LL.AND_CLAUSE]
            stock_db_df_obj = stock_database.StockDatabaseDataFrame(self.stock_db, ticker, and_clause)
            return stock_db_df_obj.df_data
        else:
            fetcher = AlphavantageStockFetcher(ticker, self.config.api_period, self.config.api_output_size)
            return fetcher.df_data

    def __add_runtime_parameter_to_config__(self, entry_dic: dict):
        self.config.runtime.actual_ticker = entry_dic[LL.TICKER]
        self.config.runtime.actual_and_clause = entry_dic[LL.AND_CLAUSE]
        self.config.runtime.actual_number = entry_dic[LL.NUMBER]
        self.config.runtime.actual_ticker_name = self.config.ticker_dic[self.config.runtime.actual_ticker]

    def __show_statistics__(self):
        self.config.print()
        if self.config.statistics_excel_file_name == '':
            self.pattern_statistics.print_overview()
            self.detector_statistics.print_overview()
        else:
            writer = pd.ExcelWriter(self.config.statistics_excel_file_name)
            self.pattern_statistics.write_to_excel(writer, 'Formations')
            self.detector_statistics.write_to_excel(writer, 'Overview')
            print('Statistics were written to file: {}'.format(self.config.statistics_excel_file_name))
            writer.save()

    def __init_db_and_test_data__(self, excel_file_with_test_data: str, start_row: int, end_row: int):
        if self.config.get_data_from_db:
            self.stock_db = stock_database.StockDatabase()
            if excel_file_with_test_data != '':
                self.__excel_file_with_test_data = excel_file_with_test_data
                self.df_test_data = pd.ExcelFile(self.__excel_file_with_test_data).parse(0)
                self.__start_row = start_row
                self.__end_row = self.df_test_data.shape[0] if end_row == 0 else end_row

    def __init_loop_list_for_ticker__(self):
        self.__loop_list_ticker = LoopList4Dictionaries()
        if self.config.get_data_from_db and self.__excel_file_with_test_data != '':
            for ind, rows in self.df_test_data.iterrows():
                if self.__loop_list_ticker.counter >= self.__start_row:
                    self.config.ticker_dic[rows[PSC.TICKER]] = rows[PSC.NAME]
                    start_date = MyPyDate.get_date_from_datetime(rows[PSC.BEGIN_PREVIOUS])
                    date_end = MyPyDate.get_date_from_datetime(rows[PSC.END] + timedelta(days=rows[PSC.T_NEEDED] + 20))
                    and_clause = "Date BETWEEN '{}' AND '{}'".format(start_date, date_end)
                    self.__loop_list_ticker.append({LL.TICKER: rows[PSC.TICKER], LL.AND_CLAUSE: and_clause})
                if self.__loop_list_ticker.counter >= self.__end_row:
                    break
        else:
            for ticker in self.config.ticker_dic:
                self.__loop_list_ticker.append({LL.TICKER: ticker, LL.AND_CLAUSE: self.config.and_clause})

    def __handle_statistics__(self, detector: PatternDetector):
        for pattern in detector.pattern_list:
            self.pattern_statistics.add_entry(pattern)

        if config.show_final_statistics:
            self.detector_statistics.add_entry(self.config, detector.get_statistics_api())
        else:
            detector.print_statistics()


config = PatternConfiguration()
config.get_data_from_db = False
config.api_period = ApiPeriod.DAILY
config.pattern_type_list = FT.get_all()
# config.pattern_type_list = [FT.TRIANGLE_TOP]
config.plot_data = True
config.statistics_excel_file_name = 'statistics_pattern_06-04.xlsx'
config.statistics_excel_file_name = ''
config.bound_upper_value = CN.CLOSE
config.bound_lower_value = CN.CLOSE
config.breakout_over_congestion_range = False
config.show_final_statistics = True
config.max_number_securities = 1000
config.breakout_range_pct = 0.05  # default is 0.05
config.use_index(Indices.DOW_JONES)
# config.use_own_dic({'AAPL': 'American'})  # "INTC": "Intel",  "NKE": "Nike", "V": "Visa",  "GE": "GE", MRK (Merck)
# "FCEL": "FuelCell" "KO": "Coca Cola" # "BMWYY": "BMW" NKE	Nike, "CSCO": "Nike", "AXP": "American", "WMT": "Wall mart",
# config.and_clause = "Date BETWEEN '2017-10-25' AND '2018-04-18'"
config.and_clause = "Date BETWEEN '2018-01-01' AND '2019-02-18'"
# config.and_clause = ''
config.api_output_size = ApiOutputsize.COMPACT

pattern_controller = PatternController(config)
pattern_controller.run_pattern_checker('')

# Head Shoulder: GE Date BETWEEN '2016-01-25' AND '2019-10-30'
# Triangle: Processing KO (Coca Cola)...Date BETWEEN '2017-10-25' AND '2019-10-30'
"""
'CAT': 'Caterpillar'
"""

