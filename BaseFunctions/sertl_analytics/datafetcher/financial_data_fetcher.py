"""
Description: This module fetch data from any source. Transforms them into pd.DataFrame and plots them.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""
import pandas as pd
import requests
import matplotlib.pyplot as plt
import os
import io
import sertl_analytics.environment  # init some environment variables during load - for security reasons
import seaborn as sns

class ApiPeriod:
    WEEKLY = 'WEEKLY'
    DAILY = 'DAILY'
    INTRADAY = 'INTRADAY'


class ApiOutputsize:
    COMPACT = 'compact'
    FULL = 'full'


class APIBaseFetcher:
    def __init__(self, symbol: str, period: ApiPeriod = ApiPeriod.DAILY,
                 output_size: ApiOutputsize = ApiOutputsize.COMPACT):
        self.api_key = self.get_api_key()
        self.symbol = symbol  # like the symbol of a stock, e.g. MSFT
        self.period = period
        self.output_size = output_size
        self.url = self.get_url()
        print(self.url)
        self.request = requests.get(self.url)
        self.df = self.get_data_frame()
        self.column_list = list(self.df.columns.values)
        self.__format_column__()

    def get_data_frame(self):
        pass

    def __format_column__(self):
        pass

    def get_api_key(self):
        pass

    def get_url(self):
        pass

    def plot_data_frame(self):
        pass

    def get_url_function(self):
        return self.period  # may be overwritten


class AlphavantageJSONFetcher (APIBaseFetcher):
    def __init__(self, symbol: str, period: ApiPeriod = ApiPeriod.DAILY,
                 output_size: ApiOutputsize = ApiOutputsize.COMPACT):
        self.api_symbol = ''
        APIBaseFetcher.__init__(self, symbol, period, output_size)
        self.column_list_data = self.get_column_list_data()
        self.column_data = self.get_column_data()
        self.column_volume = self.get_column_volume()
        self.df_data = self.df[self.column_list_data]
        self.df_volume = self.df[self.column_volume]

    def get_column_list_data(self):
        pass

    def get_column_data(self):
        pass

    def get_column_volume(self):
        pass

    def get_data_frame(self) -> pd.DataFrame:
        pass

    def __format_column__(self):
        self.df.index = pd.to_datetime(self.df.index)
        for col in self.column_list:
            self.df[col] = pd.to_numeric(self.df[col])

    def get_json_data_key(self):
        pass

    def get_api_key(self):
        return os.environ["alphavantage_apikey"]

    def plot_data_frame(self):
        fig, axes = plt.subplots(nrows=2, ncols=1)
        plot_01 = self.df_data[[self.column_data]].plot(ax=axes[0], title=self.symbol)
        plot_01.legend(loc='upper left')
        plt.tight_layout()
        self.df_volume.plot(ax=axes[1], title = self.column_volume)
        plt.show()

    def get_stardard_column_names(self):  # OLD: 1. open   2. high    3. low  4. close 5. volume
        return ['Open', 'High', 'Low', 'Close', 'Volume']

class AlphavantageStockFetcher (AlphavantageJSONFetcher):
    def get_column_list_data(self):
        return self.column_list[:-1]

    def get_column_data(self):
        return self.column_list[-2]

    def get_column_volume(self):
        return self.column_list[-1]

    def get_url_function(self):
        dict = {ApiPeriod.WEEKLY: 'TIME_SERIES_WEEKLY',
                ApiPeriod.DAILY: 'TIME_SERIES_DAILY',
                ApiPeriod.INTRADAY: 'TIME_SERIES_INTRADAY'}
        return dict[self.period]

    def get_json_data_key(self):
        dict = {ApiPeriod.DAILY: 'Time Series (Daily)',
                ApiPeriod.WEEKLY: 'Time Series (Weekly)'}
        return dict[self.period]

    def get_data_frame(self) -> pd.DataFrame:
        json_data = self.request.json()
        meta_data = json_data["Meta Data"]
        self.api_symbol = meta_data["2. Symbol"]
        time_series = json_data[self.get_json_data_key()]  # e.g. Time Series (Daily)
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df.columns = self.get_stardard_column_names()
        return df

    def get_url(self):
        url = 'https://www.alphavantage.co/query?function=' + self.get_url_function() + '&symbol=' + self.symbol
        if self.output_size == ApiOutputsize.FULL:
            url = url + '&outputsize=full'
        return url + '&apikey=' + self.api_key


class AlphavantageCryptoFetcher(AlphavantageJSONFetcher):
    def __init__(self, key: str, period: ApiPeriod = ApiPeriod.DAILY, market: str = 'USD'):
        self.market = market
        AlphavantageJSONFetcher.__init__(self, key, period)

    def get_column_list_data(self):
        return self.column_list[:-2]

    def get_column_data(self):
        return self.column_list[-3]

    def get_column_volume(self):
        return self.column_list[-2]

    def get_url_function(self):
        dict = {ApiPeriod.WEEKLY: 'DIGITAL_CURRENCY_WEEKLY',
                ApiPeriod.DAILY: 'DIGITAL_CURRENCY_DAILY',
                ApiPeriod.INTRADAY: 'DIGITAL_CURRENCY_INTRADAY'}
        return dict[self.period]

    def get_json_data_key(self):
        dict = {ApiPeriod.DAILY: 'Time Series (Digital Currency Daily)',
                ApiPeriod.INTRADAY: 'Time Series (Digital Currency Intraday)'}
        return dict[self.period]

    def get_data_frame(self) -> pd.DataFrame:
        json_data = self.request.json()
        meta_data = json_data["Meta Data"]
        self.api_symbol = meta_data["2. Digital Currency Code"]
        time_series = json_data[self.get_json_data_key()]
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df.columns = self.get_stardard_column_names()
        return df

    def get_url(self):
        url = 'https://www.alphavantage.co/query?function=' + self.get_url_function() + '&symbol=' + self.symbol
        return url + '&market=' + self.market + '&apikey=' + self.api_key


class AlphavantageCSVFetcher (APIBaseFetcher):
    """
    key = CRYPTO for Cryptocurrency list, NYSE for New York Stock Exchange, NAS for Nasdaq, CCY for currencies
    """
    def __init__(self, symbol: str='CRYPTO'):
        APIBaseFetcher.__init__(self, symbol)

    def get_data_frame(self):
        content = self.request.content
        return pd.read_csv(io.StringIO(content.decode('utf-8')))

    def get_url(self):
        if self.symbol == 'CRYPTO':
            return 'https://www.alphavantage.co/digital_currency_list/'
        elif self.symbol == 'CCY':
            return 'https://www.alphavantage.co/physical_currency_list/'


class CorrelationHandler:
    def __init__(self):
        self.symbol_list = []
        self.df_dic = {}
        self.df_common = None
        self.index = None
        self.correlation_data_frame = None
        self.title = ''
        self.column = ''

    def fill_df_dic_for_symbol_list(self, symbol_list):
        self.symbol_list = symbol_list
        self.__fill_df_dic_for_symbol_list__()

    def __fill_df_dic_for_symbol_list__(self):
        for symbol in self.symbol_list:
            self.df_dic[symbol] = AlphavantageCryptoFetcher(symbol).df_data

    def show_correlation_heat_map(self, column: str, title: str):
        self.column = column
        self.title = title
        self.build_correlation_data_frame()
        fig, axes = plt.subplots(nrows=2, ncols=1)
        self.df_common.plot(ax=axes[0], title=self.title)
        plt.tight_layout()
        sns.heatmap(self.correlation_data_frame, ax=axes[1])
        plt.show()
        # plt.savefig('CryptoHeatmap.png')

    def build_correlation_data_frame(self):
        self.build_common_data_frame(self.column)
        print(self.build_common_data_frame)
        self.correlation_data_frame = self.df_common.corr()
        print(self.correlation_data_frame)

    def build_common_data_frame(self, column: str):
        self.df_common = None
        for keys in self.df_dic:
            df_sub = self.df_dic[keys][[column]]
            df_sub.columns = [keys]
            df_sub = df_sub.pct_change().dropna()
            if self.df_common is None:
                self.df_common = df_sub
            else:
                self.df_common = self.df_common.join(df_sub, how='inner')


class StocksCorrelationHandler(CorrelationHandler):
    def __fill_df_dic_for_symbol_list__(self):
        for symbol in self.symbol_list:
            self.df_dic[symbol] = AlphavantageStockFetcher(symbol).df_data


class CryptoCorrelationHandler(CorrelationHandler):
    def __fill_df_dic_for_symbol_list__(self):
        for symbol in self.symbol_list:
            self.df_dic[symbol] = AlphavantageCryptoFetcher(symbol).df_data
