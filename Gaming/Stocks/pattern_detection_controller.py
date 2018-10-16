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
from sertl_analytics.datafetcher.financial_data_fetcher import CryptoCompareCryptoFetcher, BitfinexCryptoFetcher
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

    def run_pattern_detector(self, excel_file_test_data: PatternExcelFile = None):
        self._excel_file_with_test_data = excel_file_test_data
        self.__init_test_data__()
        self.__init_loop_list_for_ticker__()
        for value_dic in self._loop_list_ticker.value_list:
            ticker = value_dic[LL.TICKER]
            self.sys_config.init_predictors_without_condition_list(ticker)
            self.__update_runtime_parameters__(value_dic)
            print('\nProcessing {} ({})...\n'.format(ticker, self.sys_config.runtime.actual_ticker_name))
            df_data = self.__get_df_from_source__(ticker, value_dic)
            if df_data is None:
                print('No data available for: {} and {}'.format(ticker, self.sys_config.runtime.actual_and_clause))
                continue
            self.sys_config.pdh.init_by_df(df_data)
            detector = PatternDetector(self.sys_config)
            detector.parse_for_fibonacci_waves()
            detector.parse_for_pattern()
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

    def get_detector_for_dash(self, sys_config: SystemConfiguration, ticker: str, and_clause: str) -> PatternDetector:
        self.sys_config = sys_config
        value_dict = {LL.TICKER: ticker, LL.AND_CLAUSE: and_clause, LL.NUMBER: 1}
        self.__update_runtime_parameters__(value_dict)
        print('\nProcessing {} ({}) for {} ...\n'.format(ticker, sys_config.runtime.actual_ticker_name, and_clause))
        df_data = self.__get_df_from_source__(ticker, value_dict, True)
        self.sys_config.pdh.init_by_df(df_data)
        detector = PatternDetector(self.sys_config)
        detector.parse_for_fibonacci_waves()
        detector.parse_for_pattern()
        detector.check_for_intersections_and_endings()
        detector.save_pattern_data()
        return detector

    @property
    def loop_list_ticker(self):
        return self._loop_list_ticker

    def __get_df_from_source__(self, ticker, value_dic, run_on_dash=False):
        period = self.sys_config.config.api_period
        aggregation = self.sys_config.config.api_period_aggregation
        output_size = self.sys_config.config.api_output_size

        if self.sys_config.config.get_data_from_db:
            self.__handle_not_available_symbol__(ticker)
            and_clause = value_dic[LL.AND_CLAUSE]
            stock_db_df_obj = stock_database.StockDatabaseDataFrame(self.sys_config.db_stock, ticker, and_clause)
            return stock_db_df_obj.df_data
        elif ticker in self.sys_config.crypto_ccy_dic:
            if period == PRD.INTRADAY:
                fetcher = CryptoCompareCryptoFetcher(ticker, period, aggregation, run_on_dash)
                # fetcher = BitfinexCryptoFetcher(ticker, period, aggregation, run_on_dash)
                # self.__handle_difference_of_exchanges(fetcher.df_data, fetcher_bit.df_data)
                return fetcher.df_data
            else:
                fetcher = AlphavantageCryptoFetcher(ticker, period, aggregation)
                return fetcher.df_data
        else:
            fetcher = AlphavantageStockFetcher(ticker, period, aggregation, output_size)
            if self.sys_config.config.api_period == PRD.INTRADAY:
                return self.__get_with_concatenated_intraday_data__(fetcher.df_data)
            return fetcher.df_data

    @staticmethod
    def __handle_difference_of_exchanges(df_cc: pd.DataFrame, df_bitfinex: pd.DataFrame):
        df_diff = df_cc - df_bitfinex
        print(df_cc.head())
        print(df_bitfinex.head())
        print(df_diff.head())

    @staticmethod
    def __cut_intraday_df_to_one_day__(df: pd.DataFrame) -> pd.DataFrame:
        index_first_row = df.index[0]
        index_last_row = df.index[-1]
        timestamp_one_day_before = index_last_row - (23 * 60 * 60)  # 23 = to avoid problems with the last trade shape
        if index_first_row < timestamp_one_day_before:
            return df.loc[timestamp_one_day_before:]
        return df

    @staticmethod
    def __get_with_concatenated_intraday_data__(df: pd.DataFrame):
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
        if not self.sys_config.db_stock.is_symbol_loaded(ticker):
            if UserInput.get_confirmation('{} is not available. Do you want to load it'.format(ticker)):
                name = UserInput.get_input('Please enter the name for the symbol {}'.format(ticker))
                if name == 'x':
                    exit()
                self.sys_config.db_stock.update_stock_data_for_symbol(ticker, name)
            else:
                exit()

    def __update_runtime_parameters__(self, entry_dic: dict):
        self.sys_config.runtime.actual_ticker = entry_dic[LL.TICKER]
        if self.sys_config.runtime.actual_ticker in self.sys_config.crypto_ccy_dic:
            self.sys_config.runtime.actual_ticker_equity_type = EQUITY_TYPE.CRYPTO
            if self.sys_config.config.api_period == PRD.INTRADAY:
                self.sys_config.runtime.actual_expected_win_pct = 1
            else:
                self.sys_config.runtime.actual_expected_win_pct = 1
        else:
            self.sys_config.runtime.actual_ticker_equity_type = EQUITY_TYPE.SHARE
            self.sys_config.runtime.actual_expected_win_pct = 1
        self.sys_config.runtime.actual_and_clause = entry_dic[LL.AND_CLAUSE]
        self.sys_config.runtime.actual_number = entry_dic[LL.NUMBER]
        if self.sys_config.db_stock is not None:
            self.sys_config.runtime.actual_ticker_name = \
                self.sys_config.db_stock.get_name_for_symbol(entry_dic[LL.TICKER])
        if self.sys_config.runtime.actual_ticker_name == '':
            self.sys_config.runtime.actual_ticker_name = self.sys_config.config.ticker_dic[entry_dic[LL.TICKER]]

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
        if self.sys_config.config.get_data_from_db and self._excel_file_with_test_data is not None:
            self._df_test_data = pd.ExcelFile(self._excel_file_with_test_data.file_name).parse(0)
            self._start_row = self._excel_file_with_test_data.file_name.row_start
            if self._excel_file_with_test_data.row_end == 0:
                self._excel_file_with_test_data.row_end = self._df_test_data.shape[0]

    def __init_loop_list_for_ticker__(self):
        self._loop_list_ticker = LoopList4Dictionaries()
        if self.sys_config.config.get_data_from_db and self._excel_file_with_test_data is not None:
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
