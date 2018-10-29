"""
Description: This module contains the configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, TP, Indices, CN, EQUITY_TYPE, PRD, OPS, DC
from pattern_database import stock_database as sdb
from pattern_data_provider import PatternDataProviderApi
from sertl_analytics.pybase.df_base import PyBaseDataFrame
from sertl_analytics.mydates import MyDate
from sertl_analytics.datafetcher.database_fetcher import DatabaseDataFrame
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList


class PatternDebugger:
    def __init__(self):
        self.__process_dic = {}
        self.pattern_range_position_list = []

    @property
    def is_active(self):
        for process in self.__process_dic:
            if self.__process_dic[process]:
                return True
        return False

    def check_range_position_list(self, position_list: list):
        process = 'position_list'
        self.__init_process__(process)
        min_len = min(len(position_list), len(self.pattern_range_position_list))
        if min_len > 0:
            intersect = set(position_list).intersection(set(self.pattern_range_position_list))
            if len(intersect) == len(self.pattern_range_position_list):
                self.__activate_process__(process)

    def __init_process__(self, process: str):
        self.__process_dic[process] = False

    def __activate_process__(self, process: str):
        self.__process_dic[process] = True


class RuntimeConfiguration:
    actual_list = []
    actual_position = 0
    actual_tick_position = 0
    actual_number = 0
    actual_ticker = ''
    actual_ticker_equity_type = EQUITY_TYPE.NONE
    actual_ticker_name = ''
    actual_and_clause = ''
    actual_pattern_type = FT.NONE
    actual_breakout = None
    actual_pattern_range = None
    actual_expected_win_pct = 0  # pct in this case is 10 for 10%
    actual_trade_process = TP.ONLINE


class PatternConfiguration:
    def __init__(self, data_provider_api: PatternDataProviderApi):
        self.data_provider_api = data_provider_api
        self.with_trade_part = True  # we need this configuration for testing touch strategy
        self.pattern_type_list = [FT.CHANNEL]
        self.simple_moving_average_number = 10
        self.save_pattern_data = True
        self.save_trade_data = True
        self.show_differences_to_stored_features = False
        self.bound_upper_value = CN.HIGH
        self.bound_lower_value = CN.LOW
        self.plot_data = True
        self.plot_min_max = False
        self.plot_only_pattern_with_fibonacci_waves = True
        self.plot_volume = False
        self.plot_close = False
        self.length_for_global_min_max = 50  # a global minimum or maximum must have at least this number as distance
        self.length_for_global_min_max_fibonacci = 10  # ...for fibonacci
        self.length_for_local_min_max = 2  # a local minimum or maximum must have at least this number as distance
        self.length_for_local_min_max_fibonacci = self.length_for_local_min_max  # fibonacci
        self.fibonacci_tolerance_pct = 0.20  # it works great for 0.20 = 20% tolerance for retracement and regression
        self.fibonacci_detail_print = False
        self.check_previous_period = False   # default
        self.breakout_over_congestion_range = False
        self.breakout_range_pct = 0.05
        self.investment = 1000
        self.max_number_securities = 1000
        self.max_pattern_range_length = 50
        self.show_final_statistics = True
        self.and_clause = "Date BETWEEN '2017-12-01' AND '2019-12-31'"
        self.statistics_excel_file_name = ''
        self.statistics_constraints_excel_file_name = 'pattern_statistics/constraints.xlsx'
        self.ticker_dic = {}
        self.__previous_period_length = 0

    @property
    def api_from_db(self):
        return self.data_provider_api.from_db

    @property
    def api_period(self):
        return self.data_provider_api.period

    @property
    def api_period_aggregation(self):
        return self.data_provider_api.period_aggregation

    @property
    def and_clause_for_pattern(self):
        return self.and_clause.replace(DC.DATE, DC.PATTERN_BEGIN_DT)

    @property
    def and_clause_for_trade(self):
        return self.and_clause.replace(DC.DATE, DC.PATTERN_RANGE_BEGIN_DT)

    @property
    def value_categorizer_tolerance_pct(self):
        if self.api_period == PRD.INTRADAY:
            if self.api_period_aggregation < 5:
                return 0.0002
            elif self.api_period_aggregation == 5:
                return 0.0005
            else:
                return 0.001
        return 0.005  # orig: 0.005

    @property
    def value_categorizer_tolerance_pct_equal(self):
        if self.api_period == PRD.INTRADAY:
            if self.api_period_aggregation <= 5:
                return 0.001
            else:
                return 0.002
        return 0.005  # orig: 0.005

    @staticmethod
    def get_and_clause(dt_start, dt_end=None):
        date_start = MyDate.get_date_from_datetime(dt_start)
        if dt_end:
            date_end = MyDate.get_date_from_datetime(dt_end)
            return "Date BETWEEN '{}' AND '{}'".format(date_start, date_end)
        return "Date >= '{}'".format(date_start)

    def init_by_nearest_neighbor_id(self, nn_id: str):  # example: 128#1_1_1_AAPL_12_2015-12-03_00:00_2016-01-07_00:00
        id_components = nn_id.split('#')
        self.init_by_pattern_id_str(id_components[1])

    def init_by_pattern_id_str(self, pattern_id: str):  # example: 1_1_1_AAPL_12_2015-12-03_00:00_2016-01-07_00:00
        id_parts = pattern_id.split('_')
        symbol = id_parts[3]
        pattern_type_id = int(id_parts[4])
        date_from = id_parts[5]
        date_to = id_parts[7]
        self.__init_by_pattern_id_components__(symbol, pattern_type_id, date_from, date_to)

    def __init_by_pattern_id_components__(self, symbol: str, pattern_type_id: int, date_from: str, date_to: str):
        self.use_own_dic({symbol: symbol})
        self.pattern_type_list = [FT.get_pattern_type(pattern_type_id)]
        date_from = MyDate.get_datetime_object(date_from)
        date_to = MyDate.get_datetime_object(date_to)
        date_from = MyDate.adjust_by_days(date_from, -30)
        date_to = MyDate.adjust_by_days(date_to, +30)
        self.and_clause = "Date BETWEEN '{}' AND '{}'".format(date_from, date_to)

    def get_time_stamp_before_one_period_aggregation(self, time_stamp: float):
        return time_stamp - self.get_seconds_for_one_period()

    def get_time_stamp_after_ticks(self, tick_number: int, ts_set_off = MyDate.get_epoch_seconds_from_datetime()):
        return int(ts_set_off + tick_number * self.get_seconds_for_one_period())

    def get_seconds_for_one_period(self):
        return PRD.get_seconds_for_period(self.api_period, self.api_period_aggregation)

    @property
    def expected_win_pct(self):
        return 1.0 if self.api_period == PRD.INTRADAY else 1.0
        # will be changed in the program for Cryptos - runtime.actual_expected_win_pct

    def __get_previous_period_length__(self):
        return self.__previous_period_length

    def __set_previous_period_length__(self, value: int):
        self.__previous_period_length = value

    previous_period_length = property(__get_previous_period_length__, __set_previous_period_length__)

    def print(self):
        source = 'DB' if self.api_from_db else 'Api'
        pattern_type = self.pattern_type_list
        and_clause = self.and_clause
        period = self.api_period
        output_size = self.api_output_size
        bound_upper_v = self.bound_upper_value
        bound_lower_v = self.bound_lower_value
        breakout_over_big_range = self.breakout_over_congestion_range

        print('\nConfiguration settings:')
        if self.api_from_db:
            print('Formation: {} \nSource: {} \nAnd clause: {} \nUpper/Lower Bound Value: {}/{}'
                  ' \nBreakout big range: {}\n'.format(
                    pattern_type, source, and_clause, bound_upper_v, bound_lower_v, breakout_over_big_range))
        else:
            print('Formation: {} \nSource: {} \n\nPeriod/Output size: {}/{} \nUpper/Lower Bound Value: {}/{}'
                  ' \nBreakout big range: {}\n'.format(
                    pattern_type, source, period, output_size, bound_upper_v, bound_lower_v, breakout_over_big_range))

    def use_index(self, index: str):
        if index == Indices.ALL_DATABASE:
            self.ticker_dic = self.get_all_in_database()
        elif index == Indices.MIXED:
            self.ticker_dic = self.get_mixed_dic()
        else:
            self.ticker_dic = IndicesComponentList.get_ticker_name_dic(index)

    def use_own_dic(self, dic: dict):
        stock_db = sdb.StockDatabase()
        self.ticker_dic = dic
        for symbol in self.ticker_dic:
            name_from_db = stock_db.get_name_for_symbol(symbol)
            if name_from_db != '':
                self.ticker_dic[symbol] = name_from_db

    @staticmethod
    def get_mixed_dic():
        return {"TSLA": "Tesla", "FCEL": "Full Cell", "ONVO": "Organovo", "MRAM": "MRAM"}

    @staticmethod
    def get_all_in_database():
        stock_db = sdb.StockDatabase()
        db_data_frame = DatabaseDataFrame(
            stock_db, query='SELECT Symbol, count(*) FROM Stocks GROUP BY Symbol HAVING count(*) > 4000')
        return PyBaseDataFrame.get_rows_as_dictionary(db_data_frame.df, 'Symbol', ['Symbol'])
