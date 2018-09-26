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
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import CN, PRD, OPS
import seaborn as sns


class APIBaseFetcher:
    def __init__(self, symbol: str, period=PRD.DAILY, aggregation=1, output_size=OPS.COMPACT):
        self.api_key = self._get_api_key_()
        self.symbol = symbol  # like the symbol of a stock, e.g. MSFT
        self.period = period
        self.aggregation = aggregation
        self.output_size = output_size
        self.url = self._get_url_()
        print(self.url)
        self.request = requests.get(self.url)
        self.df = self.__get_data_frame__()
        self.column_list = list(self.df.columns.values)
        self.__format_column__()

    def __get_data_frame__(self):
        pass

    def __format_column__(self):
        for col in self.column_list:
            self.df[col] = pd.to_numeric(self.df[col])

    def _get_api_key_(self):
        pass

    def _get_url_(self):
        pass

    def plot_data_frame(self):
        pass

    def get_url_function(self):
        return self.period  # may be overwritten


class AlphavantageJSONFetcher (APIBaseFetcher):
    def __init__(self, symbol: str, period=PRD.DAILY, aggregation=1, output_size=OPS.COMPACT):
        self.api_symbol = ''
        APIBaseFetcher.__init__(self, symbol, period, aggregation, output_size)
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

    def get_json_data_key(self):
        pass

    def _get_api_key_(self):
        return os.environ["alphavantage_apikey"]

    def plot_data_frame(self):
        fig, axes = plt.subplots(nrows=2, ncols=1)
        plot_01 = self.df_data[[self.column_data]].plot(ax=axes[0], title=self.symbol)
        plot_01.legend(loc='upper left')
        plt.tight_layout()
        self.df_volume.plot(ax=axes[1], title = self.column_volume)
        plt.show()

    @staticmethod
    def get_standard_column_names():  # OLD: 1. open   2. high    3. low  4. close 5. volume
        return ['Open', 'High', 'Low', 'Close', 'Volume']


class AlphavantageStockFetcher (AlphavantageJSONFetcher):
    def get_column_list_data(self):
        return self.column_list

    def get_column_data(self):
        return self.column_list[-2]

    def get_column_volume(self):
        return self.column_list[-1]

    def get_url_function(self):
        dict = {PRD.WEEKLY: 'TIME_SERIES_WEEKLY',
                PRD.DAILY: 'TIME_SERIES_DAILY',
                PRD.INTRADAY: 'TIME_SERIES_INTRADAY'}
        return dict[self.period]

    def get_json_data_key(self):
        dict = {PRD.DAILY: 'Time Series (Daily)',
                PRD.WEEKLY: 'Time Series (Weekly)',
                PRD.INTRADAY: 'Time Series ({}min)'.format(self.aggregation)}
        return dict[self.period]

    def __get_data_frame__(self) -> pd.DataFrame:
        json_data = self.request.json()
        meta_data = json_data["Meta Data"]
        self.api_symbol = meta_data["2. Symbol"]
        time_series = json_data[self.get_json_data_key()]  # e.g. Time Series (Daily)
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df = df.assign(Timestamp=df.index.map(MyDate.get_epoch_seconds_from_datetime))
        df[CN.TIMESTAMP] = df[CN.TIMESTAMP].apply(int)
        df.set_index(CN.TIMESTAMP, drop=True, inplace=True)
        df.columns = self.get_standard_column_names()
        return df

    def _get_url_(self):
        url = 'https://www.alphavantage.co/query?function={}&symbol={}'.format(self.get_url_function(), self.symbol)
        if self.output_size == OPS.FULL:
            url = url + '&outputsize=full'
        if self.period == PRD.INTRADAY:
            url = url + '&interval={}min'.format(self.aggregation)
        return url + '&apikey=' + self.api_key


class AlphavantageCryptoFetcher(AlphavantageJSONFetcher):
    def __init__(self, symbol: str, period=PRD.DAILY, aggregation=1):
        AlphavantageJSONFetcher.__init__(self, symbol, period, aggregation)

    def get_column_list_data(self):
        return self.column_list

    def get_column_data(self):
        return self.column_list[-2]

    def get_column_volume(self):
        return self.column_list[-1]

    def get_url_function(self):
        dict = {PRD.WEEKLY: 'DIGITAL_CURRENCY_WEEKLY',
                PRD.DAILY: 'DIGITAL_CURRENCY_DAILY',
                PRD.INTRADAY: 'DIGITAL_CURRENCY_INTRADAY'}
        return dict[self.period]

    def get_json_data_key(self):
        dict = {PRD.DAILY: 'Time Series (Digital Currency Daily)',
                PRD.INTRADAY: 'Time Series (Digital Currency Intraday)'}
        return dict[self.period]

    def __get_data_frame__(self) -> pd.DataFrame:
        json_data = self.request.json()
        meta_data = json_data["Meta Data"]
        self.api_symbol = meta_data["2. Digital Currency Code"]
        time_series = json_data[self.get_json_data_key()]
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df = df.assign(Timestamp=df.index.map(MyDate.get_epoch_seconds_from_datetime))
        df[CN.TIMESTAMP] = df[CN.TIMESTAMP].apply(int)
        df.set_index(CN.TIMESTAMP, drop=True, inplace=True)
        if self.period == PRD.INTRADAY:
            df.drop([df.columns[0],  '3. market cap (USD)'], axis=1, inplace=True)
            df.columns = ['Open', 'Volume']
            df.insert(loc=1, column='Close', value = df[df.columns[0]])
            df.insert(loc=1, column='Low', value=df[df.columns[0]])
            df.insert(loc=1, column='High', value=df[df.columns[0]])  # ['Open', 'High', 'Low', 'Close', 'Volume']
        else:
            df.drop(['1b. open (USD)', '2b. high (USD)', '3b. low (USD)', '4b. close (USD)', '6. market cap (USD)'],
                    axis=1, inplace=True)
            df.columns = self.get_standard_column_names()
        return df

    def _get_url_(self):  # the symbol has the structure symbol_CCY like BTC_USD
        symbol = self.symbol[:-4]
        market = self.symbol[-3:]
        url = 'https://www.alphavantage.co/query?function={}&symbol={}&market={}&apikey={}'.format(
            self.get_url_function(), symbol, market, self.api_key
        )
        return url


class AlphavantageCSVFetcher (APIBaseFetcher):
    """
    key = CRYPTO for Cryptocurrency list, NYSE for New York Stock Exchange, NAS for Nasdaq, CCY for currencies
    """
    def __init__(self, symbol: str='CRYPTO'):
        APIBaseFetcher.__init__(self, symbol)

    def __get_data_frame__(self):
        content = self.request.content
        return pd.read_csv(io.StringIO(content.decode('utf-8')))

    def _get_url_(self):
        if self.symbol == 'CRYPTO':
            return 'https://www.alphavantage.co/digital_currency_list/'
        elif self.symbol == 'CCY':
            return 'https://www.alphavantage.co/physical_currency_list/'


class CryptoCompareJSONFetcher (APIBaseFetcher):
    def __init__(self, symbol: str, period: str, aggregation: int):
        self.api_symbol = ''
        APIBaseFetcher.__init__(self, symbol, period, aggregation)
        self.column_list_data = self.get_column_list_data()
        self.df_data = self.df[self.column_list_data]

    def get_column_list_data(self):
        pass

    def __format_column__(self):
        pass

    def get_json_data_key(self):
        pass

    def _get_api_key_(self):
        return 'not_yet'  # os.environ["cryptocompare_apikey"]  # doesn't exist yet

    @staticmethod
    def get_standard_column_names():  # OLD: 1. open   2. high    3. low  4. close 5. volume
        return ['Close', 'High', 'Low', 'Open', 'Volume']


class CryptoCompareCryptoFetcher(CryptoCompareJSONFetcher):
    def __init__(self, symbol: str, period=PRD.DAILY, aggregation=1, run_on_dash=False):
        self._run_on_dash = run_on_dash
        CryptoCompareJSONFetcher.__init__(self, symbol, period, aggregation)

    def get_column_list_data(self):
        return self.column_list

    def get_json_data_key(self):
        return 'Data'

    def __get_data_frame__(self) -> pd.DataFrame:
        json_data = self.request.json()
        self.api_symbol = self.symbol
        time_series = json_data[self.get_json_data_key()]
        df = pd.DataFrame(time_series)
        df.drop(['volumefrom'], axis=1, inplace=True)
        df.set_index('time', drop=True, inplace=True)
        df.columns = self.get_standard_column_names()
        return df

    def _get_url_(self):  # the symbol has the structure symbolCCY like BTCUSD
        url_function = 'histominute' if self.period == PRD.INTRADAY else 'histoday'
        url_limit = self._get_url_limit_parameter_()
        url_aggregate = self.aggregation if self.period == PRD.INTRADAY else 1
        symbol = self.symbol[:-3]
        market = self.symbol[-3:]
        url = 'https://min-api.cryptocompare.com/data/{}?fsym={}&tsym={}&limit={}&aggregate={}'.\
            format(url_function, symbol, market, url_limit, url_aggregate)
        return url

    def _get_url_limit_parameter_(self) -> int:
        if self.period == PRD.INTRADAY:
            return 200 if self._run_on_dash else 300
        return 400


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
