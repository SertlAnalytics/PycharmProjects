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


class APIBaseFetcher:
    def __init__(self, symbol: str, period: str = 'DAILY'):
        self.api_key = self.get_api_key()
        self.symbol = symbol  # like the symbol of a stock, e.g. MSFT
        self.period = period
        self.url = self.get_url()
        # print('APIBaseFetcher._url={}'.format(self._url))
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


class AlphavantageJSONFetcher (APIBaseFetcher):
    def __init__(self, symbol: str, period: str = 'DAILY'):
        self.api_symbol = ''
        APIBaseFetcher.__init__(self, symbol, period)
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

    def get_data_frame(self):
        pass

    def __format_column__(self):
        self.df.index = pd.to_datetime(self.df.index)
        for col in self.column_list:
            self.df[col] = pd.to_numeric(self.df[col])

    def get_api_key(self):
        return os.environ["alphavantage_apikey"]

    def plot_data_frame(self):
        print('AlphavantageJSONFetcher')
        fig, axes = plt.subplots(nrows=2, ncols=1)
        plot_01 = self.df_data[[self.column_data]].plot(ax=axes[0], title=self.symbol)
        plot_01.legend(loc='upper left')
        plt.tight_layout()
        self.df_volume.plot(ax=axes[1], title = self.column_volume)
        plt.show()


class AlphavantageStockFetcher (AlphavantageJSONFetcher):
    def get_column_list_data(self):
        return self.column_list[:-1]

    def get_column_data(self):
        return self.column_list[-2]

    def get_column_volume(self):
        return self.column_list[-1]

    def get_data_frame(self):
        json_data = self.request.json()
        meta_data = json_data["Meta Data"]
        self.api_symbol = meta_data["2. Symbol"]
        time_series = json_data["Time Series (Daily)"]  # Time Series (Daily)
        return pd.DataFrame.from_dict(time_series, orient="index")

    def get_url(self):
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + self.symbol
        return url + '&apikey=' + self.api_key


class AlphavantageCryptoFetcher(AlphavantageJSONFetcher):
    def __init__(self, key: str, period: str = 'DAILY', market: str = 'USD'):
        self.market = market
        AlphavantageJSONFetcher.__init__(self, key, period)

    def get_column_list_data(self):
        return self.column_list[:-2]

    def get_column_data(self):
        return self.column_list[-3]

    def get_column_volume(self):
        return self.column_list[-2]

    def get_data_frame(self):
        json_data = self.request.json()
        meta_data = json_data["Meta Data"]
        self.api_symbol = meta_data["2. Digital Currency Code"]
        if self.period == 'DAILY':
            time_series = json_data["Time Series (Digital Currency Daily)"]
        else:
            time_series = json_data["Time Series (Digital Currency Intraday)"]
        return pd.DataFrame.from_dict(time_series, orient="index")

    def get_url(self):
        if self.period == 'DAILY':
            url = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=' + self.symbol
        else:
            url = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_INTRADAY&symbol=' + self.symbol
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


process = 'CryptoCorrelation'

if process == 'StockCorrelation':
    correlation_handler = StocksCorrelationHandler()
    # correlation_handler.fill_df_dic_for_symbol_list(['BTC', 'LTC', 'ETH', 'XRP', 'XMR', 'EOS'], '4b. close (USD)', 'Cryptocurrencies')
    correlation_handler.fill_df_dic_for_symbol_list(['MSFT', 'AAPL', 'GM', 'DJI', 'BB', 'FSLR', 'AMZN'])
    correlation_handler.show_correlation_heat_map('4. close', 'Stocks')
elif process == 'CryptoCorrelation':
    correlation_handler = CryptoCorrelationHandler()
    # correlation_handler.fill_df_dic_for_symbol_list(['BTC', 'LTC', 'ETH', 'XRP', 'XMR', 'EOS'], '4b. close (USD)', 'Cryptocurrencies')
    correlation_handler.fill_df_dic_for_symbol_list(['BTC', 'LTC', 'ETH', 'XRP', 'XMR', 'EOS'])
    # correlation_handler.fill_df_dic_for_symbol_list(['BTC', 'LTC'])
    correlation_handler.show_correlation_heat_map('4b. close (USD)', 'Cryptocurrencies')
elif process == 'StockFetcher':
    fetcher = AlphavantageStockFetcher('XAG')  # stock: MSFT, Crypto: BTC
    fetcher.plot_data_frame()
elif process == 'CryptoFetcher':
    fetcher = AlphavantageCryptoFetcher('BTC', 'DAILY', 'USD')  # stock: MSFT, Crypto: BTC
    fetcher.plot_data_frame()
else:
    csvFetcher = AlphavantageCSVFetcher('CRYPTO')
    print(csvFetcher.df.head())



