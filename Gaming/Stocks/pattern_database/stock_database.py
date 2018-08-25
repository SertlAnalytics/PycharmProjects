"""
Description: This module contains the configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, Date, DateTime, Time
from sertl_analytics.datafetcher.database_fetcher import BaseDatabase, DatabaseDataFrame, MyTable, MyTableColumn, CDT
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, AlphavantageCryptoFetcher
from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod, ApiOutputsize
from sertl_analytics.mydates import MyDate
import pandas as pd
import math
from datetime import datetime
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList
from sertl_analytics.constants.pattern_constants import Indices, CN, DC
import os
import time


class FeaturesTable(MyTable):
    def __init__(self):
        MyTable.__init__(self)
        self._feature_columns_touch_points = self.__get_feature_columns_touch_points__()
        self._feature_columns_before_breakout = self.__get_feature_columns_before_breakout__()
        self._feature_columns_after_breakout = self.__get_feature_columns_after_breakout__()
        self._label_columns_touch_points = self.__get_label_columns_touch_points__()
        self._label_columns_before_breakout = self.__get_label_columns_before_breakout__()
        self._label_columns_after_breakout = self.__get_label_columns_after_breakout__()
        self._query_for_feature_and_label_data_touch_points = \
            self.__get_query_for_feature_and_label_data_touch_points__()
        self._query_for_feature_and_label_data_before_breakout = \
            self.__get_query_for_feature_and_label_data_before_breakout__()
        self._query_for_feature_and_label_data_after_breakout = \
            self.__get_query_for_feature_and_label_data_after_breakout__()

    @property
    def feature_columns_touch_points(self):
        return self._feature_columns_touch_points

    @property
    def features_columns_before_breakout(self):
        return self._feature_columns_before_breakout

    @property
    def features_columns_after_breakout(self):
        return self._feature_columns_after_breakout

    @property
    def label_columns_touch_points(self):
        return self._label_columns_touch_points

    @property
    def label_columns_before_breakout(self):
        return self._label_columns_before_breakout

    @property
    def label_columns_after_breakout(self):
        return self._label_columns_after_breakout

    @property
    def query_for_feature_and_label_data_touch_points(self):
        return self._query_for_feature_and_label_data_touch_points

    @property
    def query_for_feature_and_label_data_before_breakout(self):
        return self._query_for_feature_and_label_data_before_breakout

    @property
    def query_for_feature_and_label_data_after_breakout(self):
        return self._query_for_feature_and_label_data_after_breakout

    def _add_columns_(self):
        self._columns.append(MyTableColumn(DC.EQUITY_TYPE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.EQUITY_TYPE_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.PERIOD, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.PERIOD_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.PERIOD_AGGREGATION , CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKER_ID, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.TICKER_NAME, CDT.STRING, 100))
        self._columns.append(MyTableColumn(DC.PATTERN_TYPE, CDT.STRING, 100))
        self._columns.append(MyTableColumn(DC.PATTERN_TYPE_ID, CDT.INTEGER)) # 1x = Channel, 2x = Triangle, 3x = TKE, 4x = HS
        self._columns.append(MyTableColumn(DC.TS_PATTERN_TICK_FIRST, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TS_PATTERN_TICK_LAST, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TS_BREAKOUT, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKS_TILL_PATTERN_FORMED, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.PATTERN_BEGIN_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.PATTERN_BEGIN_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.BREAKOUT_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.BREAKOUT_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.PATTERN_END_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.PATTERN_END_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.PATTERN_TOLERANCE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.BREAKOUT_RANGE_MIN_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PATTERN_BEGIN_LOW, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PATTERN_BEGIN_HIGH, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PATTERN_END_LOW, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PATTERN_END_HIGH, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SLOPE_UPPER_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SLOPE_LOWER_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SLOPE_REGRESSION_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SLOPE_BREAKOUT_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SLOPE_VOLUME_REGRESSION_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TOUCH_POINTS_TILL_BREAKOUT_TOP, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.BREAKOUT_DIRECTION, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.BREAKOUT_DIRECTION_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.VOLUME_CHANGE_AT_BREAKOUT_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PREVIOUS_PERIOD_HALF_TOP_OUT_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PREVIOUS_PERIOD_FULL_TOP_OUT_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PREVIOUS_PERIOD_HALF_BOTTOM_OUT_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PREVIOUS_PERIOD_FULL_BOTTOM_OUT_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.NEXT_PERIOD_HALF_POSITIVE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.NEXT_PERIOD_FULL_POSITIVE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.NEXT_PERIOD_HALF_NEGATIVE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.NEXT_PERIOD_FULL_NEGATIVE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.AVAILABLE_FIBONACCI_TYPE, CDT.STRING))  # MIN, MAX
        self._columns.append(MyTableColumn(DC.AVAILABLE_FIBONACCI_TYPE_ID, CDT.INTEGER))  # 0=No, -1=MIN, 1 = MAX
        self._columns.append(MyTableColumn(DC.EXPECTED_WIN, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.FALSE_BREAKOUT, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.EXPECTED_WIN_REACHED, CDT.INTEGER))

    @staticmethod
    def _get_name_():
        return 'Features'

    def __get_query_for_feature_and_label_data_touch_points__(self) -> str:
        return "SELECT {} FROM Features".format(self.__get_concatenated_feature_label_columns_touch_points__())

    def __get_query_for_feature_and_label_data_before_breakout__(self) -> str:
        return "SELECT {} FROM Features".format(self.__get_concatenated_feature_label_columns_before_breakout__())

    def __get_query_for_feature_and_label_data_after_breakout__(self):
        return "SELECT {} FROM Features".format(self.__get_concatenated_feature_label_columns_after_breakout__())

    def __get_concatenated_feature_label_columns_touch_points__(self):
        return ', '.join(self._feature_columns_touch_points + self._label_columns_touch_points)

    def __get_concatenated_feature_label_columns_before_breakout__(self):
        return ', '.join(self._feature_columns_before_breakout + self._label_columns_before_breakout)

    def __get_concatenated_feature_label_columns_after_breakout__(self):
        return ', '.join(self._feature_columns_after_breakout + self._label_columns_after_breakout)

    @staticmethod
    def __get_feature_columns_after_breakout__():
        return [DC.EQUITY_TYPE_ID, DC.PERIOD_ID, DC.PERIOD_AGGREGATION, DC.PATTERN_TYPE_ID,
                DC.TICKS_TILL_PATTERN_FORMED, DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT,
                DC.SLOPE_UPPER_PCT, DC.SLOPE_LOWER_PCT, DC.SLOPE_REGRESSION_PCT, DC.SLOPE_BREAKOUT_PCT,
                DC.SLOPE_VOLUME_REGRESSION_PCT, DC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED_PCT,
                DC.TOUCH_POINTS_TILL_BREAKOUT_TOP, DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM,
                DC.BREAKOUT_DIRECTION_ID, DC.VOLUME_CHANGE_AT_BREAKOUT_PCT,
                DC.PREVIOUS_PERIOD_HALF_TOP_OUT_PCT, DC.PREVIOUS_PERIOD_FULL_TOP_OUT_PCT,
                DC.PREVIOUS_PERIOD_HALF_BOTTOM_OUT_PCT, DC.PREVIOUS_PERIOD_FULL_BOTTOM_OUT_PCT,
                DC.AVAILABLE_FIBONACCI_TYPE_ID]

    @staticmethod
    def __get_feature_columns_before_breakout__():
        base_list = FeaturesTable.__get_feature_columns_after_breakout__()
        del base_list[base_list.index(DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT)]
        del base_list[base_list.index(DC.BREAKOUT_DIRECTION_ID)]
        del base_list[base_list.index(DC.VOLUME_CHANGE_AT_BREAKOUT_PCT)]
        return base_list

    @staticmethod
    def __get_feature_columns_touch_points__():
        base_list = FeaturesTable.__get_feature_columns_before_breakout__()
        del base_list[base_list.index(DC.TOUCH_POINTS_TILL_BREAKOUT_TOP)]
        del base_list[base_list.index(DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM)]
        return base_list

    @staticmethod
    def __get_label_columns_after_breakout__():
        return [DC.NEXT_PERIOD_HALF_POSITIVE_PCT, DC.NEXT_PERIOD_FULL_POSITIVE_PCT,
                DC.NEXT_PERIOD_HALF_NEGATIVE_PCT, DC.NEXT_PERIOD_FULL_NEGATIVE_PCT,
                DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF, DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF,
                DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL, DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL,
                DC.FALSE_BREAKOUT]

    @staticmethod
    def __get_label_columns_before_breakout__():
        return [DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT, DC.BREAKOUT_DIRECTION_ID, DC.FALSE_BREAKOUT]

    @staticmethod
    def __get_label_columns_touch_points__():
        return [DC.TOUCH_POINTS_TILL_BREAKOUT_TOP, DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM]

    @staticmethod
    def is_label_column_for_regression(label_column: str):
        return label_column[-4:] == '_PCT'


class StockDatabase(BaseDatabase):
    _crypto_ccy_dic = IndicesComponentList.get_ticker_name_dic(Indices.CRYPTO_CCY)
    _sleep_seconds = 20

    def is_symbol_loaded(self, symbol: str):
        last_loaded_time_stamp_dic = self.__get_last_loaded_time_stamp_dic__(symbol)
        return len(last_loaded_time_stamp_dic) == 1

    def get_name_for_symbol(self, symbol: str):
        company_dic = self.__get_company_dic__(symbol)
        return '' if len(company_dic) == 0 else company_dic[symbol].Name

    def __get_engine__(self):
        db_path = self.__get_db_path__()
        return create_engine('sqlite:///' + db_path)

    def __get_db_name__(self):
        return 'MyStocks.sqlite'

    def __get_db_path__(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, self.__get_db_name__())

    def import_stock_data_by_deleting_existing_records(self, symbol: str, period: ApiPeriod = ApiPeriod.DAILY,
                                                       output_size: ApiOutputsize = ApiOutputsize.COMPACT):
        self.delete_records("DELETE from Stocks WHERE Symbol = '" + str(symbol) + "'")
        input_dic = self.get_input_values_for_stock_table(period, symbol, output_size)
        self.__insert_data_into_table__('Stocks', input_dic)

    def update_stock_data_by_index(self, index: str, period=ApiPeriod.DAILY, aggregation=1):
        company_dict = self.__get_company_dic__()
        self.__check_company_dic_against_web__(index, company_dict)
        last_loaded_date_stamp_dic = self.__get_last_loaded_time_stamp_dic__()
        index_list = self.__get_index_list__(index)
        dt_now_time_stamp = datetime.now().timestamp()
        for index in index_list:
            print('\nUpdating {}...\n'.format(index))
            ticker_dic = IndicesComponentList.get_ticker_name_dic(index)
            for ticker in ticker_dic:
                self.__update_stock_data_for_single_value__(period, aggregation, ticker, ticker_dic[ticker],
                                                            company_dict, last_loaded_date_stamp_dic,
                                                            dt_now_time_stamp)
        self.__handle_error_cases__()

    def __check_company_dic_against_web__(self, index: str, company_dict: dict):
        company_dict_by_web = IndicesComponentList.get_ticker_name_dic(index)
        for key in company_dict_by_web:
            if key not in company_dict:
                name = company_dict_by_web[key]
                self.__insert_company_in_company_table__(key, name, True)
                new_dict = self.__get_company_dic__(key)
                company_dict[key] = new_dict[key]

    def update_crypto_currencies(self, period=ApiPeriod.DAILY, aggregation=1):
        company_dic = self.__get_company_dic__(like_input='USD')
        last_loaded_date_stamp_dic = self.__get_last_loaded_time_stamp_dic__(like_input='USD')
        dt_now_time_stamp = datetime.now().timestamp()
        print('\nUpdating {}...\n'.format(Indices.CRYPTO_CCY))
        ticker_dic = IndicesComponentList.get_ticker_name_dic(Indices.CRYPTO_CCY)
        for ticker in ticker_dic:
            self.__update_stock_data_for_single_value__(period, aggregation, ticker, ticker_dic[ticker],
                                                        company_dic, last_loaded_date_stamp_dic, dt_now_time_stamp)
        self.__handle_error_cases__()

    def __handle_error_cases__(self):
        while len(self.error_handler.retry_dic) > 0:
            retry_dic = dict(self.error_handler.retry_dic)
            self.error_handler.retry_dic = {}
            for ticker in retry_dic:
                print('Handle error case for {}'.format(ticker))
                time.sleep(self._sleep_seconds)
                li = retry_dic[ticker]
                self.update_stock_data_for_symbol(ticker, li[0], li[1])

    def update_stock_data_for_symbol(self, symbol: str, name_input='', period=ApiPeriod.DAILY, aggregation=1):
        company_dic = self.__get_company_dic__(symbol)
        name = company_dic[symbol] if symbol in company_dic else name_input
        last_loaded_date_dic = self.__get_last_loaded_time_stamp_dic__(symbol)
        dt_now_time_stamp = datetime.now().timestamp()
        self.__update_stock_data_for_single_value__(period, aggregation, symbol, name,
                                                    company_dic, last_loaded_date_dic, dt_now_time_stamp)

    def insert_pattern_features(self, input_dict_list: list):
        self.__insert_data_into_table__('Features', input_dict_list)

    def __update_stock_data_for_single_value__(self, period: str, aggregation: int, ticker: str, name: str,
                                               company_dic: dict, last_loaded_date_stamp_dic: dict,
                                               dt_now_time_stamp: float):
        name = self.__get_alternate_name__(ticker, name)
        last_loaded_time_stamp = last_loaded_date_stamp_dic[ticker] if ticker in last_loaded_date_stamp_dic else 100000
        process_type = self.__get_process_type_for_update__(period, aggregation, dt_now_time_stamp,
                                                            last_loaded_time_stamp)
        if process_type == 'NONE':
            print('{} - {} is already up-to-date - no load required.'.format(ticker, name))
            return
        if ticker not in company_dic or company_dic[ticker].ToBeLoaded:
            output_size = ApiOutputsize.FULL if process_type == 'FULL' else ApiOutputsize.COMPACT
            try:
                if ticker in self._crypto_ccy_dic:
                    stock_fetcher = AlphavantageCryptoFetcher(ticker, period, aggregation)
                else:
                    stock_fetcher = AlphavantageStockFetcher(ticker, period, aggregation, output_size)
            except KeyError:
                self.error_handler.catch_known_exception(__name__, 'Ticker={}. Continue with next...'.format(ticker))
                self.error_handler.add_to_retry_dic(ticker, [name, period])
                time.sleep(self._sleep_seconds)
                return
            except:
                self.error_handler.catch_exception(__name__, 'Ticker={}. Continue with next...'.format(ticker))
                self.error_handler.add_to_retry_dic(ticker, [name, period])
                time.sleep(self._sleep_seconds)
                return
            df = stock_fetcher.df
            if ticker not in company_dic:
                to_be_loaded = df[CN.VOL].mean() > 10000
                self.__insert_company_in_company_table__(ticker, name, to_be_loaded)
                company_dic[ticker] = to_be_loaded
                if not to_be_loaded:
                    time.sleep(self._sleep_seconds)
                    return
            if ticker in last_loaded_date_stamp_dic:
                df = df.loc[last_loaded_time_stamp:].iloc[1:]
            if df.shape[0] > 0:
                input_list = self.__get_df_data_for_insert_statement__(df, period, ticker)
                self.__insert_data_into_table__('Stocks', input_list)
                print('{} - {}: inserted {} new ticks.'.format(ticker, name, df.shape[0]))
            time.sleep(self._sleep_seconds)

    @staticmethod
    def __get_process_type_for_update__(period: str, aggregation: int, dt_now_time_stamp, last_loaded_time_stamp):
        delta_time_stamp = dt_now_time_stamp - last_loaded_time_stamp
        delta_time_stamp_min = int(delta_time_stamp / 60)
        delta_time_stamp_days = int(delta_time_stamp_min / (24 * 60))
        if period == ApiPeriod.DAILY:
            if delta_time_stamp_days < 2:
                return 'NONE'
            elif delta_time_stamp_days < 50:
                return 'COMPACT'
            else:
                return 'FULL'
        else:
            if delta_time_stamp_min < aggregation:
                return 'NONE'
            else:
                return 'FULL'

    @staticmethod
    def __get_alternate_name__(ticker: str, name: str):
        dic_alternate = {'GOOG': 'Alphbeth', 'LBTYK': 'Liberty', 'FOX': 'Twenty-First Century'}
        return dic_alternate[ticker] if ticker in dic_alternate else name

    def __get_company_dic__(self, symbol_input: str = '', like_input: str = ''):
        company_dic = {}
        query = 'SELECT * FROM Company'
        if symbol_input != '':
            query += ' WHERE Symbol = "' + symbol_input + '"'
        elif like_input != '':
            query += ' WHERE Symbol like "%' + like_input + '"'
        query += ' ORDER BY Symbol'
        db_df = DatabaseDataFrame(self, query)
        for index, rows in db_df.df.iterrows():
            company_dic[rows.Symbol] = rows
        return company_dic

    def __get_last_loaded_time_stamp_dic__(self, symbol_input: str = '', like_input: str = ''):
        last_loaded_time_stamp_dic = {}
        query = 'SELECT DISTINCT Symbol from Stocks'
        if symbol_input != '':
            query += ' WHERE Symbol = "' + symbol_input + '"'
        elif like_input != '':
            query += ' WHERE Symbol like "%' + like_input + '"'
        query += ' ORDER BY Symbol'
        db_df = DatabaseDataFrame(self, query)
        loaded_symbol_list = [rows.Symbol for index, rows in db_df.df.iterrows()]
        for symbol in loaded_symbol_list:
            query = 'SELECT * FROM Stocks WHERE Symbol = "' + symbol + '" ORDER BY Timestamp Desc LIMIT 1'
            db_df = DatabaseDataFrame(self, query)
            try:
                last_loaded_time_stamp_dic[symbol] = db_df.df[CN.TIMESTAMP].values[0]
            except:
                print('Problem with __get_last_loaded_time_stamp_dic__ for {}'.format(symbol))
        return last_loaded_time_stamp_dic

    def __insert_company_in_company_table__(self, ticker: str, name: str, to_be_loaded: bool):
        input_dic = {'Symbol': ticker, 'Name': name, 'ToBeLoaded': to_be_loaded,
                     'Sector': '', 'Year': 2018, 'Revenues': 0, 'Expenses': 0,
                     'Employees': 0, 'Savings': 0, 'ForcastGrowth': 0}
        try:
            self.__insert_data_into_table__('Company', [input_dic])
        except Exception:
            self.error_handler.catch_exception(__name__)
            print('{} - {}: problem inserting into Company table.'.format(ticker, name))

    @staticmethod
    def __get_index_list__(index: str):
        return [Indices.DOW_JONES, Indices.NASDAQ100, Indices.SP500] if index == Indices.ALL else [index]

    def get_input_values_for_stock_table(self, period, symbol: str, output_size: ApiOutputsize):
        stock_fetcher = AlphavantageStockFetcher(symbol, period, output_size)
        df = stock_fetcher.__get_data_frame__()
        return self.__get_df_data_for_insert_statement__(df, period, symbol)

    @staticmethod
    def __get_df_data_for_insert_statement__(df: pd.DataFrame, period: str, symbol: str, aggregation=1):
        input_list = []
        close_previous = 0
        for timestamp, row in df.iterrows():
            date_time = MyDate.get_date_time_from_epoch_seconds(timestamp)
            v_open = float(row[CN.OPEN])
            high = float(row[CN.HIGH])
            low = float(row[CN.LOW])
            close = float(row[CN.CLOSE])
            volume = float(row[CN.VOL])
            big_move = False  # default
            direction = 0  # default
            if close != 0:
                if abs((close_previous - close) / close) > 0.03:
                    big_move = True
                    direction = math.copysign(1, close - close_previous)
            close_previous = close

            if not math.isnan(high):
                input_dic = {CN.PERIOD: str(period), CN.AGGREGATION: aggregation, CN.SYMBOL: symbol,
                             CN.TIMESTAMP: timestamp, CN.DATE: date_time.date(), CN.TIME: date_time.time(),
                             CN.OPEN: v_open, CN.HIGH: high, CN.LOW: low, CN.CLOSE: close,
                             CN.VOL: volume, CN.BIG_MOVE: big_move, CN.DIRECTION: direction}
                input_list.append(input_dic)
        return input_list

    def create_tables(self):
        metadata = MetaData()
        # Define a new table with a name, count, amount, and valid column: data
        data = Table('Stocks', metadata,
                     Column('Period', String(20)),  # WEEKLY / DAILY / INTRADAY
                     Column('Aggregation', Integer()),  # 1, 5, 15 (minute for intraday)
                     Column('Symbol', String(20)),
                     Column('Timestamp', Integer()),
                     Column('Date', Date()),
                     Column('Time', Time()),
                     Column('Open', Float()),
                     Column('High', Float()),
                     Column('Low', Float()),
                     Column('Close', Float()),
                     Column('Volume', Float()),
                     Column('BigMove', Boolean(), default=False),
                     Column('Direction', Integer(), default=0)  # 1 = up, -1 = down, 0 = default (no big move)
                     )

        # Define a new table with a name, count, amount, and valid column: data
        data = Table(
                'Company', metadata,
                Column('Symbol', String(10), unique=True),
                Column('Name', String(100)),
                Column('ToBeLoaded', Boolean(), default=False),
                Column('Sector', String(100)),
                Column('Year', Integer()),
                Column('Revenues', Float()),
                Column('Expenses', Float()),
                Column('Employees', Float()),
                Column('Savings', Float()),
                Column('ForcastGrowth', Float())
        )

        self.create_database_elements(metadata)
        print(repr(data))

    def create_pattern_feature_table(self):
        metadata = MetaData()
        feature_table = FeaturesTable()
        exec(feature_table.description())
        self.create_database_elements(metadata)
        table_obj = metadata.tables.get('Features')
        print(repr(table_obj))

    def __insert_feature_in_feature_table__(self, ticker: str, input_dic: dict):
        try:
            self.__insert_data_into_table__('Features', [input_dic])
        except Exception:
            self.error_handler.catch_exception(__name__)
            print('{}: problem inserting into Features table.'.format(ticker))

    def are_features_already_available(self, features_dict: dict) -> bool:
        query = "SELECT * FROM Features where {}={} and {}={} and {}='{}' and {}={} and {}={}".format(
            DC.EQUITY_TYPE_ID, features_dict[DC.EQUITY_TYPE_ID],
            DC.PERIOD_ID, features_dict[DC.PERIOD_ID],
            DC.TICKER_ID, features_dict[DC.TICKER_ID],
            DC.TS_PATTERN_TICK_FIRST, features_dict[DC.TS_PATTERN_TICK_FIRST],
            DC.TS_PATTERN_TICK_LAST, features_dict[DC.TS_PATTERN_TICK_LAST]
        )
        db_df = DatabaseDataFrame(self, query)
        return db_df.df.shape[0] > 0


class StockDatabaseDataFrame(DatabaseDataFrame):
    def __init__(self, db: StockDatabase, symbol='', and_clause='', period='DAILY', aggregation=1):
        self.symbol = symbol
        self.statement = "SELECT * from Stocks WHERE Symbol = '{}' and Period = '{}' and Aggregation = {}".format(
            symbol, period, aggregation)
        if and_clause != '':
            self.statement += ' and ' + and_clause
        DatabaseDataFrame.__init__(self, db, self.statement)
        self.df.set_index(CN.TIMESTAMP, drop=False, inplace=True)
        self.column_data = [CN.CLOSE]
        self.df_data = self.df[[CN.OPEN, CN.HIGH, CN.LOW, CN.CLOSE, CN.VOL, CN. TIMESTAMP, CN.BIG_MOVE, CN.DIRECTION]]


