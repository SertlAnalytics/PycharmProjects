"""
Description: This module contains the configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, Date
from sertl_analytics.datafetcher.database_fetcher import BaseDatabase, DatabaseDataFrame
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, AlphavantageCryptoFetcher
from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod, ApiOutputsize
import pandas as pd
import math
from datetime import datetime
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList
from sertl_analytics.constants.pattern_constants import Indices, CN
import os
import time


class StockDatabase(BaseDatabase):
    __crypto_ccy_dic = IndicesComponentList.get_ticker_name_dic(Indices.CRYPTO_CCY)

    def is_symbol_loaded(self, symbol: str):
        last_loaded_dic = self.__get_last_loaded_dic__(symbol)
        return len(last_loaded_dic) == 1

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
        self.insert_data_into_table('Stocks', input_dic)

    def update_stock_data_by_index(self, index: str, period: ApiPeriod = ApiPeriod.DAILY):
        company_dic = self.__get_company_dic__()
        last_loaded_date_dic = self.__get_last_loaded_dic__()
        index_list = self.__get_index_list__(index)
        dt_now = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d")
        for index in index_list:
            print('\nUpdating {}...\n'.format(index))
            ticker_dic = IndicesComponentList.get_ticker_name_dic(index)
            for ticker in ticker_dic:
                self.__update_stock_data_for_single_value__(period, ticker, ticker_dic[ticker], company_dic,
                                                            last_loaded_date_dic, dt_now)
        self.__handle_error_cases__()

    def update_crypto_currencies(self, period: ApiPeriod = ApiPeriod.DAILY):
        company_dic = self.__get_company_dic__(like_input='USD')
        last_loaded_date_dic = self.__get_last_loaded_dic__(like_input='USD')
        dt_now = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d")
        print('\nUpdating {}...\n'.format(Indices.CRYPTO_CCY))
        ticker_dic = IndicesComponentList.get_ticker_name_dic(Indices.CRYPTO_CCY)
        for ticker in ticker_dic:
            self.__update_stock_data_for_single_value__(period, ticker, ticker_dic[ticker], company_dic,
                                                        last_loaded_date_dic, dt_now)
        self.__handle_error_cases__()

    def __handle_error_cases__(self):
        while len(self.error_handler.retry_dic) > 0:
            retry_dic = dict(self.error_handler.retry_dic)
            self.error_handler.retry_dic = {}
            for ticker in retry_dic:
                time.sleep(3)
                print('Handle error case for {}'.format(ticker))
                li = retry_dic[ticker]
                self.update_stock_data_for_symbol(ticker, li[0], li[1])

    def update_stock_data_for_symbol(self, symbol: str, name_input: str = '', period: ApiPeriod = ApiPeriod.DAILY):
        company_dic = self.__get_company_dic__(symbol)
        name = company_dic[symbol] if symbol in company_dic else name_input
        last_loaded_date_dic = self.__get_last_loaded_dic__(symbol)
        dt_now = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d")
        self.__update_stock_data_for_single_value__(period, symbol, name, company_dic, last_loaded_date_dic, dt_now)

    def __update_stock_data_for_single_value__(self, period: ApiPeriod, ticker: str, name: str, company_dic: dict,
                                               last_loaded_date_dic: dict, date_time_now: datetime):
        name = self.__get_alternate_name__(ticker, name)
        last_loaded_date_str = str(last_loaded_date_dic[ticker]) if ticker in last_loaded_date_dic else '1990-01-01'
        last_loaded_date = datetime.strptime(last_loaded_date_str, "%Y-%m-%d")
        delta = date_time_now - last_loaded_date
        if delta.days < 2:
            print('{} - {} is already up-to-date - no load required.'.format(ticker, name))
            return
        if ticker not in company_dic or company_dic[ticker].ToBeLoaded:
            output_size = ApiOutputsize.FULL if delta.days > 50 else ApiOutputsize.COMPACT
            try:
                if ticker in self.__crypto_ccy_dic:
                    stock_fetcher = AlphavantageCryptoFetcher(ticker, period)
                else:
                    stock_fetcher = AlphavantageStockFetcher(ticker, period, output_size)
            except KeyError:
                self.error_handler.catch_known_exception(__name__, 'Ticker={}. Continue with next...'.format(ticker))
                self.error_handler.add_to_retry_dic(ticker, [name, period])
                return
            except:
                self.error_handler.catch_exception(__name__, 'Ticker={}. Continue with next...'.format(ticker))
                self.error_handler.add_to_retry_dic(ticker, [name, period])
                return
            df = stock_fetcher.get_data_frame()
            if ticker not in company_dic:
                to_be_loaded = df[CN.VOL].mean() > 10000
                self.__insert_company_in_company_table__(ticker, name, to_be_loaded)
                company_dic[ticker] = to_be_loaded
                if not to_be_loaded:
                    return
            if ticker in last_loaded_date_dic:
                last_date = last_loaded_date_dic[ticker]
                df = df.loc[last_date:].iloc[1:]
            if df.shape[0] > 0:
                input_list = self.__get_df_data_for_insert_statement__(df, period, ticker)
                self.insert_data_into_table('Stocks', input_list)
                print('{} - {}: inserted {} new ticks.'.format(ticker, name, df.shape[0]))

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

    def __get_last_loaded_dic__(self, symbol_input: str = '', like_input: str = ''):
        last_loaded_dic = {}
        query = 'SELECT DISTINCT Symbol from Stocks'
        if symbol_input != '':
            query += ' WHERE Symbol = "' + symbol_input + '"'
        elif like_input != '':
            query += ' WHERE Symbol like "%' + like_input + '"'
        query += ' ORDER BY Symbol'
        db_df = DatabaseDataFrame(self, query)
        loaded_symbol_list = [rows.Symbol for index, rows in db_df.df.iterrows()]
        for symbol in loaded_symbol_list:
            query = 'SELECT * FROM Stocks WHERE Symbol = "' + symbol + '" ORDER BY Date Desc LIMIT 1'
            db_df = DatabaseDataFrame(self, query)
            try:
                last_loaded_dic[symbol] = db_df.df.iloc[0].Date
            except:
                print('Problem with __get_last_loaded_dic__ for {}'.format(symbol))
        return last_loaded_dic

    def __insert_company_in_company_table__(self, ticker: str, name: str, to_be_loaded: bool):
        input_dic = {'Symbol': ticker, 'Name': name, 'ToBeLoaded': to_be_loaded,
                     'Sector': '', 'Year': 2018, 'Revenues': 0, 'Expenses': 0,
                     'Employees': 0, 'Savings': 0, 'ForcastGrowth': 0}
        try:
            self.insert_data_into_table('Company', [input_dic])
        except Exception:
            self.error_handler.catch_exception(__name__)
            print('{} - {}: problem inserting into Company table.'.format(ticker, name))

    @staticmethod
    def __get_index_list__(index: str):
        return [Indices.DOW_JONES, Indices.NASDAQ100, Indices.SP500] if index == Indices.ALL else [index]

    def get_input_values_for_stock_table(self, period, symbol: str, output_size: ApiOutputsize):
        stock_fetcher = AlphavantageStockFetcher(symbol, period, output_size)
        df = stock_fetcher.get_data_frame()
        return self.__get_df_data_for_insert_statement__(df, period, symbol)

    @staticmethod
    def __get_df_data_for_insert_statement__(df: pd.DataFrame, period: ApiPeriod, symbol: str):
        input_list = []
        close_previous = 0
        for dates, row in df.iterrows():
            date = datetime.strptime(dates, '%Y-%m-%d')
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
                input_dic = {CN.PERIOD: str(period), CN.SYMBOL: symbol, CN.DATE: date,
                             CN.OPEN: v_open, CN.HIGH: high, CN.LOW: low, CN.CLOSE: close,
                             CN.VOL: volume, CN.BIG_MOVE: big_move, CN.DIRECTION: direction}
                input_list.append(input_dic)
        return input_list

    def create_tables(self):
        metadata = MetaData()
        # Define a new table with a name, count, amount, and valid column: data
        data = Table('Stocks', metadata,
                     Column('Period', String(20)),  # MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY
                     Column('Symbol', String(20)),
                     Column('Date', Date()),
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
                Column('Name', String(100), unique=True),
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


class StockDatabaseDataFrame(DatabaseDataFrame):
    def __init__(self, db: StockDatabase, symbol: str = '', and_clause: str = ''):
        self.symbol = symbol
        self.statement = "SELECT * from Stocks WHERE Symbol = '" + symbol + "'"
        if and_clause != '':
            self.statement += ' and ' + and_clause
        DatabaseDataFrame.__init__(self, db, self.statement)
        self.df[CN.DATE] = self.df[CN.DATE].apply(pd.to_datetime)
        self.df = self.df.set_index(CN.DATE)
        self.column_list = list(self.df.columns.values)
        self.column_list_data = self.get_column_list_data()
        self.column_data = self.get_column_data()
        self.column_volume = self.get_column_volume()
        self.df_data = self.df[self.column_list_data]
        self.df_volume = self.df[self.column_volume]

    def get_column_list_data(self):
        return self.column_list[2:7]

    def get_column_data(self):
        return self.column_list[5]

    def get_column_volume(self):
        return self.column_list[6]
