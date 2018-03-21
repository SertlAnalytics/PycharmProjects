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
import sertl_analytics.environment  # inits some environment variables during load


class APIBaseFetcher:
    def __init__(self, symbol: str, period: str = 'DAILY'):
        self.api_key = self.get_api_key()
        self.symbol = symbol  # like the symbol of a stock, e.g. MSFT
        self.period = period
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


class AlphavantageJSONFetcher (APIBaseFetcher):
    def __init__(self, symbol: str, period: str = 'DAILY'):
        self.api_symbol = ''
        APIBaseFetcher.__init__(self, symbol, period)
        self.column_list_data = self.get_column_list_data()
        self.column_volume = self.get_column_volume()
        self.df_data = self.df[self.column_list_data]
        self.df_volume = self.df[self.column_volume]

    def get_column_list_data(self):
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
        fig, axes = plt.subplots(nrows=2, ncols=1)
        self.df_data.plot(ax=axes[0], title=self.symbol)
        plt.tight_layout()
        self.df_volume.plot(ax=axes[1], title = self.column_volume)
        plt.show()


class AlphavantageStockFetcher (AlphavantageJSONFetcher):
    def get_column_list_data(self):
        return self.column_list[:-1]

    def get_column_volume(self):
        return self.column_list[-1]

    def get_data_frame(self):
        json_data = self.request.json()
        print(json_data)
        meta_data = json_data["Meta Data"]
        self.api_symbol = meta_data["2. Symbol"]
        time_series = json_data["Time Series (Daily)"]  # Time Series (Daily)
        return pd.DataFrame.from_dict(time_series, orient="index")

    def get_url(self):
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + self.symbol
        return url + '&apikey=' + self.api_key


class AlphavantageCryptoFetcher(AlphavantageJSONFetcher):
    def __init__(self, key: str, period: str, market: str = 'USD'):
        self.market = market
        AlphavantageJSONFetcher.__init__(self, key, period)

    def get_column_list_data(self):
        return self.column_list[:2]

    def get_column_volume(self):
        return self.column_list[-2]

    def get_data_frame(self):
        json_data = self.request.json()
        print(json_data)
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
    def __init__(self, key: str='CRYPTO'):
        APIBaseFetcher.__init__(self, key)

    def get_data_frame(self):
        content = self.request.content
        return pd.read_csv(io.StringIO(content.decode('utf-8')))

    def get_url(self):
        if self.symbol == 'CRYPTO':
            return 'https://www.alphavantage.co/digital_currency_list/'
        elif self.symbol == 'CCY':
            return 'https://www.alphavantage.co/physical_currency_list/'


# fetcher = AlphavantageStockFetcher('MSFT')  # stock: MSFT, Crypto: BTC
# fetcher.plot_data_frame()

fetcher = AlphavantageCryptoFetcher('XRP', 'DAILY', 'USD')  # stock: MSFT, Crypto: BTC
fetcher.plot_data_frame()

# csvFetcher = AlphavantageCSVFetcher('CRYPTO')
# print(csvFetcher.df.head())



