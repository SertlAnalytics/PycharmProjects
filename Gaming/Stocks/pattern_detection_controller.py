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
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, AlphavantageCryptoFetcher
from sertl_analytics.datafetcher.financial_data_fetcher import BitfinexCryptoFetcher
from sertl_analytics.datafetcher.data_fetcher_cache import DataFetcherCacheKey
from sertl_analytics.mydates import MyDate
from sertl_analytics.user_input.confirmation import UserInput
from datetime import timedelta
from sertl_analytics.pybase.loop_list import LL, LoopList4Dictionaries
from sertl_analytics.constants.pattern_constants import PSC, EQUITY_TYPE, CN, BT, PRD
from pattern_system_configuration import SystemConfiguration
from pattern_statistics import PatternStatistics, DetectorStatistics, ConstraintsStatistics
from pattern_constraints import ConstraintsFactory
from pattern_detector import PatternDetector
from pattern_plotting.pattern_plotter import PatternPlotter
from pattern_database import stock_database
from datetime import datetime
from time import sleep
from sertl_analytics.mycache import MyCache, MyCacheObjectApi
from pattern import PatternID, PatternIdFactory
from pattern_data_container import PatternDataHandler
from pattern_data_provider import PatternDataProviderApi, PatternDataProvider


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


class PatternExcelFile:
    def __init__(self, file_name: str, row_start: int = 1, row_end: int = 0):
        self.file_name = file_name
        self.row_start = row_start
        self.row_end = row_end


class PatternDataFetcherCacheKey(DataFetcherCacheKey):
    def __init__(self, ticker: str, period: str, aggregation: int):
        DataFetcherCacheKey.__init__(self, ticker, period, aggregation)
        self.from_db = False
        self.output_size = ''
        self.limit = 0
        self.and_clause = ''

    @property
    def key(self):
        return 'from_db={}_ticker={}_period={}_aggregation={}_output_size={}_limit={}_and_clause={}'.format(
            self.from_db, self.ticker_id, self.period, self.aggregation, self.output_size, self.limit, self.and_clause)


class PatternDetectionController:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self.detector_statistics = DetectorStatistics(self.sys_config)
        self.pattern_statistics = PatternStatistics(self.sys_config)
        self.constraints_statistics = ConstraintsStatistics()
        self._excel_file_with_test_data = None
        self._df_test_data = None
        self._loop_list_ticker = None  # format of an entry (ticker, and_clause, number)
        self._number_pattern_total = 0
        self._df_source_cache = MyCache()

    def run_pattern_detector(self, excel_file_test_data: PatternExcelFile = None):
        self._excel_file_with_test_data = excel_file_test_data
        self.__init_test_data__()
        self.__init_loop_list_for_ticker__()
        for value_dic in self._loop_list_ticker.value_list:
            ticker = value_dic[LL.TICKER]
            and_clause = value_dic[LL.AND_CLAUSE]
            if not self.sys_config.init_pattern_data_handler_for_ticker_id(ticker, and_clause, limit=300):
                print('No data available for: {} and {}'.format(ticker, and_clause))
                continue
            self.sys_config.update_runtime_parameters_by_dict_values(value_dic)
            print('\nProcessing {} ({})...\n'.format(ticker, self.sys_config.runtime.actual_ticker_name))
            self.sys_config.init_predictors_without_condition_list(ticker)
            detector = PatternDetector(self.sys_config)
            detector.parse_for_fibonacci_waves()
            detector.parse_for_pattern()
            # self.check_for_optimal_trading_strategy(detector)  # ToDo error with deepcopy in the called mudule
            detector.check_for_intersections_and_endings()
            detector.save_pattern_data()
            self.__handle_statistics__(detector)
            self._number_pattern_total += len(detector.pattern_list)
            if self.sys_config.config.plot_data:
                if len(detector.pattern_list) == 0 and False:  # and not detector.possible_pattern_ranges_available:
                    print('...no formations found.')
                else:
                    plotter = PatternPlotter(self.sys_config, detector)
                    plotter.plot_data_frame()
            elif self.sys_config.config.api_period == PRD.INTRADAY:
                sleep(15)

            if value_dic[LL.NUMBER] >= self.sys_config.config.max_number_securities:
                break

        if self.sys_config.config.show_final_statistics and self._number_pattern_total > 0:
            self.__show_statistics__()
        self.__write_constraints_statistics__()

    def check_for_optimal_trading_strategy(self, detector: PatternDetector):
        pattern_list_filtered = [pattern for pattern in detector.pattern_list if pattern.was_breakout_done()]
        api = PatternDataProviderApi(True, PRD.DAILY, 1)
        sys_config_for_trading_strategy = self.sys_config.get_semi_deep_copy_for_new_pattern_data_provider_api(api)
        for pattern in pattern_list_filtered:
            for nn_entry in pattern.nearest_neighbor_entry_list:
                detector_nn_entry = self.get_detector_for_pattern_id(sys_config_for_trading_strategy, nn_entry.id)
                print('check_for_optimal_trading_strategy for {}'.format(nn_entry.id))

    def get_detector_for_dash(self, sys_config: SystemConfiguration, ticker: str, and_clause: str) -> PatternDetector:
        value_dict = {LL.TICKER: ticker, LL.AND_CLAUSE: and_clause, LL.NUMBER: 1}
        sys_config.update_runtime_parameters_by_dict_values(value_dict)
        print('\nProcessing {} ({}) for {} ...\n'.format(ticker, sys_config.runtime.actual_ticker_name, and_clause))
        sys_config.init_pattern_data_handler_for_ticker_id(ticker, and_clause, 200)
        detector = PatternDetector(sys_config)
        detector.parse_for_fibonacci_waves()
        detector.parse_for_pattern()
        detector.check_for_intersections_and_endings()
        detector.save_pattern_data()
        return detector

    def get_detector_for_pattern_id(self, sys_config: SystemConfiguration, pattern_id_str: str) -> PatternDetector:
        sys_config.config.init_by_pattern_id_str(pattern_id_str)
        ticker = sys_config.runtime.actual_ticker
        and_clause = sys_config.runtime.actual_and_clause
        value_dict = {LL.TICKER: ticker, LL.AND_CLAUSE: and_clause, LL.NUMBER: 1}
        print('\nDetector_for_pattern_id - processing {} ({}) for {} ...\n'.format(
            ticker, sys_config.runtime.actual_ticker_name, and_clause))
        sys_config.init_pattern_data_handler_for_ticker_id(ticker, and_clause, 200)
        detector = PatternDetector(sys_config)
        pattern_id = PatternIdFactory(sys_config).get_pattern_id_from_pattern_id_string(pattern_id_str)
        detector.parse_for_pattern(pattern_id)
        return detector

    @property
    def loop_list_ticker(self):
        return self._loop_list_ticker

    def __show_statistics__(self):
        self.sys_config.config.print()
        if self.sys_config.config.statistics_excel_file_name == '':
            self.pattern_statistics.print_overview()
            self.detector_statistics.print_overview()
        else:
            writer = pd.ExcelWriter(self.sys_config.config.statistics_excel_file_name)
            self.pattern_statistics.write_to_excel(writer, 'Formations')
            self.detector_statistics.write_to_excel(writer, 'Overview')
            print('Statistics were written to file: {}'.format(self.sys_config.config.statistics_excel_file_name))
            writer.save()

    def __write_constraints_statistics__(self):
        if self.sys_config.config.statistics_constraints_excel_file_name == '':
            return
        constraints_detail_dict = ConstraintsFactory.get_constraints_details_as_dict(self.sys_config)
        for key, details_dict in constraints_detail_dict.items():
            self.constraints_statistics.add_entry(key, details_dict)
        writer = pd.ExcelWriter(self.sys_config.config.statistics_constraints_excel_file_name)
        self.constraints_statistics.write_to_excel(writer, 'Constraints_{}'.format(datetime.now().date()))
        print('Constraints statistics were written to file: {}'.format(
            self.sys_config.config.statistics_constraints_excel_file_name))
        writer.save()

    def __init_test_data__(self):
        if self.sys_config.config.api_from_db and self._excel_file_with_test_data is not None:
            self._df_test_data = pd.ExcelFile(self._excel_file_with_test_data.file_name).parse(0)
            self._start_row = self._excel_file_with_test_data.file_name.row_start
            if self._excel_file_with_test_data.row_end == 0:
                self._excel_file_with_test_data.row_end = self._df_test_data.shape[0]

    def __init_loop_list_for_ticker__(self):
        self._loop_list_ticker = LoopList4Dictionaries()
        if self.sys_config.config.api_from_db and self._excel_file_with_test_data is not None:
            for ind, rows in self._df_test_data.iterrows():
                if self._loop_list_ticker.counter >= self._excel_file_with_test_data.row_start:
                    self.sys_config.config.ticker_dic[rows[PSC.TICKER]] = rows[PSC.NAME]
                    start_date = MyDate.get_date_from_datetime(rows[PSC.BEGIN_PREVIOUS])
                    date_end = MyDate.get_date_from_datetime(rows[PSC.END] + timedelta(days=rows[PSC.T_NEEDED] + 20))
                    and_clause = "Date BETWEEN '{}' AND '{}'".format(start_date, date_end)
                    self._loop_list_ticker.append({LL.TICKER: rows[PSC.TICKER], LL.AND_CLAUSE: and_clause})
                if self._loop_list_ticker.counter >= self._excel_file_with_test_data.row_end:
                    break
        else:
            for ticker in self.sys_config.config.ticker_dic:
                if ticker not in ['XRPUSD']:
                    self._loop_list_ticker.append({LL.TICKER: ticker, LL.AND_CLAUSE: self.sys_config.config.and_clause})

    def __handle_statistics__(self, detector: PatternDetector):
        for pattern in detector.pattern_list:
            self.pattern_statistics.add_entry(pattern)

        if self.sys_config.config.show_final_statistics:
            self.detector_statistics.add_entry(detector.get_statistics_api())
        else:
            detector.print_statistics()
