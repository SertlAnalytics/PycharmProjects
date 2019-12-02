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
from sertl_analytics.exchanges.exchange_cls import Ticker
from sertl_analytics.my_pandas import MyPandas
import time
import quandl
import seaborn as sns
from datetime import datetime
import math


class APIBaseFetcher:
    _last_request_ts = 0
    _request_interval_required = 0  # seconds - will be overwritten in sub classes if required
    _latest_successful_df_dict = {}  # in case of problems, key= symbol_period_aggreation_limit

    def __init__(self):
        self._api_key = self._get_api_key_()
        self._kwargs = {}
        self._df = None
        self._df_data = None
        self._df_volume = None
        self._df_columns = []

    @property
    def kw_is_check(self) -> bool:
        return self._kwargs.get('is_check', False)

    @property
    def kw_symbol(self) -> str:
        return self._kwargs.get('symbol', 'xxx')

    @property
    def kw_period(self) -> str:
        return self._kwargs.get('period', PRD.DAILY)

    @property
    def kw_aggregation(self) -> int:
        return self._kwargs.get('aggregation', 15)

    @property
    def kw_output_size(self) -> str:
        if self.kw_limit > 100:
            return self._kwargs.get('output_size', OPS.FULL)
        return self._kwargs.get('output_size', OPS.COMPACT)

    @property
    def kw_collapse(self) -> str:
        return self._kwargs.get('collapse', 'daily')

    @property
    def kw_limit(self) -> int:
        return self._kwargs.get('limit', 0)

    @property
    def kw_offset(self) -> int:
        return self._kwargs.get('offset', 0)

    @property
    def kw_filepath(self) -> str:
        return self._kwargs.get('filepath', '')

    def __get_key_for_latest_successful_df_dict__(self):  # key= symbol_period_aggreation_limit
        return '{}_{}_{}_{}'.format(self.kw_symbol, self.kw_period, self.kw_aggregation, self.kw_limit)

    def retrieve_data(self, **kwargs): # symbol: str, period=PRD.DAILY, aggregation=1, output_size=OPS.COMPACT, limit=400
        self._df = None
        self.__sleep__()
        self._kwargs = kwargs
        self.__get_data_frame_by_kwargs__(print_message=not self.kw_is_check)
        if self.kw_is_check:
            return
        key = self.__get_key_for_latest_successful_df_dict__()
        if self._df is None:
            self._df = self.__get_latest_successful_retrieved_data_frame__(key)
        else:
            try:
                self.__format_columns__()
                self.__round_df_column_values__()
                self.__correct_missing_data__()
                self.__set_latest_successful_retrieved_data_frame__(key, self._df)
            except:
                self._df = None

        if self._df is not None:
            self._df_columns = list(self._df.columns.values)

    def __get_data_frame_by_kwargs__(self, print_message=True):
        try:
            url = self._get_url_()  # like the _symbol of a stock, e.g. MSFT
            print('url={}'.format(url))
            request_data = requests.get(url)
            self._df = self.__get_data_frame__(request_data=request_data)
        except:
            if print_message:
                print('PROBLEM with retrieving data from  {}'.format(url))

    def __correct_missing_data__(self): # sometimes we have no Open data - take the last close data
        last_close = 0
        last_volume = 0
        for ind, row in self._df.iterrows():  # the values are delivered with ms instead of seconds
            if row.Open is None or math.isnan(row.Open):
                row.Open = row.Low if last_close == 0 else last_close
            if row.High is None or math.isnan(row.High):
                row.High = row.Open
            if row.Low is None or math.isnan(row.Low):
                row.Low = row.Open
            if row.Close is None or math.isnan(row.Close):
                row.Close = row.Open
            if row.Volume is None or math.isnan(row.Volume):
                row.Volume = last_volume
            last_close = row.Close
            last_volume = row.Volume

    def __get_latest_successful_retrieved_data_frame__(self, key: str):
        df_last = self._latest_successful_df_dict.get(key, None)
        if df_last is None:
            print('No latest successfully retrieved data frame available as cache: {}'.format(key))
        else:
            print('Use latest successfully retrieved data frame from cache: {}'.format(key))
            print(df_last.head())
        return df_last

    def __set_latest_successful_retrieved_data_frame__(self, key: str, df: pd.DataFrame):
        # print('Cache latest successfully retrieved data frame: {}'.format(key))
        self._latest_successful_df_dict[key] = df

    def retrieve_ticker(self, symbol: str):
        self.__sleep__()
        self._kwargs = {'function': 'GLOBAL_QUOTE', 'symbol': symbol}
        url = self._get_url_()
        return self.__retrieve_ticker__(request_data=requests.get(url))

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @property
    def df_data(self) -> pd.DataFrame:
        return self._df_data

    @property
    def df_volume(self) -> pd.DataFrame:
        return self._df_volume

    def __are_retrieved_data_correct__(self, data_stream: object):
        return True

    def __print_request_details__(self, url):
        request_time = MyDate.get_time_from_epoch_seconds(self.class_last_request_ts)
        print('{}: {}'.format(request_time, url))

    def __sleep__(self):
        request_interval_required = self.class_request_interval_required
        if request_interval_required > 0:
            ts_now = MyDate.time_stamp_now()
            ts_last_request = self.class_last_request_ts
            diff_ts = ts_now - ts_last_request
            if diff_ts < request_interval_required:
                sleep_seconds = request_interval_required - diff_ts
                print('{}: Sleeping for {} seconds. Please wait...'.format(self.__class__.__name__, sleep_seconds))
                time.sleep(sleep_seconds)
        self.class_last_request_ts = MyDate.time_stamp_now()

    @property
    def class_last_request_ts(self):
        return APIBaseFetcher._last_request_ts

    @class_last_request_ts.setter
    def class_last_request_ts(self, value):
        APIBaseFetcher._last_request_ts = value

    @property
    def class_request_interval_required(self):
        return APIBaseFetcher._request_interval_required

    def __get_data_frame__(self, request_data):
        pass

    def __retrieve_ticker__(self, request_data) -> Ticker:
        pass

    def __format_columns__(self):
        for col in self._df.columns:
            self._df[col] = pd.to_numeric(self._df[col])

    def _get_api_key_(self):
        pass

    def _get_url_(self):
        pass

    def plot_data_frame(self):
        pass

    def get_url_function(self):
        return self.kw_period  # may be overwritten

    def __round_df_column_values__(self):
        decimal = self.__get_decimals_for_df_column_rounding__()
        decimals = pd.Series([decimal, decimal, decimal, decimal, 0], index=CN.get_standard_column_names())
        self._df = self._df.round(decimals)

    def __get_decimals_for_df_column_rounding__(self):
        high_mean = self._df[CN.HIGH].mean()
        if high_mean < 2:
            return 4
        elif high_mean < 10:
            return 3
        elif high_mean < 1000:
            return 1
        return 0

class QuandlFetcher (APIBaseFetcher):
    """
     quandl.ApiConfig.api_key = os.environ["quandl_apikey"]
     mydata = quandl.get('FSE/BEI_X', start_date='2019-09-30', end_date='2019-12-31', collapse='daily')
    """
    _request_interval_required = 0  # ??? we dont know the intervall - let's try...

    def __init__(self):
        APIBaseFetcher.__init__(self)
        quandl.ApiConfig.api_key = self._api_key

    def get_kw_args(self, period: str, aggregation: int, ticker: str, output_size=OPS.FULL, limit=0):
        symbol = 'FSE/{}_X'.format(ticker.upper())
        if limit==0:
            limit = {OPS.FULL: 2000, OPS.CHECK: 2}.get(output_size, 100)
        limit = {OPS.FULL: 2000, OPS.CHECK: 2}.get(output_size, 100)
        collapse = 'daily'
        return {'period': period, 'symbol': symbol, 'aggregation': aggregation, 'limit': limit, 'collapse': collapse}

    def __get_data_frame_by_kwargs__(self, print_message=True):
        try:
            self._df = self.__get_data_frame__()
        except:
            if print_message:
                print('PROBLEM with retrieving data from Quandl for {}'.format(self.kw_symbol))

    def __get_data_frame__(self) -> pd.DataFrame:
        limit = self.kw_limit * 2
        end_date = MyDate.today_str()
        start_date = MyDate.adjust_by_days(MyDate.get_datetime_object(), -limit)
        df = quandl.get(self.kw_symbol, start_date=start_date, end_date=end_date, collapse=self.kw_collapse)
        # print('PROBLEM with retrieving data from Quandl for {}'.format(self._kwargs['symbol']))

    def __get_data_frame__(self) -> pd.DataFrame:
        limit = self._kwargs['limit'] * 2
        end_date = MyDate.today_str()
        start_date = MyDate.adjust_by_days(MyDate.get_datetime_object(), -limit)
        df = quandl.get(self._kwargs['symbol'], start_date=start_date, end_date=end_date, collapse=self._kwargs['collapse'])
        # df = quandl.get(self._kwargs['symbol'], limit=self._kwargs['limit'], collapse=self._kwargs['collapse'])
        if df is not None:
            df = df[['Open', 'High', 'Low', 'Close', 'Traded Volume']]
            df = df.assign(Timestamp=df.index.map(MyDate.get_epoch_seconds_from_datetime))
            df[CN.TIMESTAMP] = df[CN.TIMESTAMP].apply(int)
            df.set_index(CN.TIMESTAMP, drop=True, inplace=True)
            df.columns = CN.get_standard_column_names()
        return df

    def _get_api_key_(self):
        return os.environ["quandl_apikey"]


class StooqIntradayFetcher(APIBaseFetcher):
    """
     Origianal data: https://stooq.com/db/h/
     They are downloaded to D:\PD_Intraday_Data\5_min
     mydata = quandl.get('FSE/BEI_X', start_date='2019-09-30', end_date='2019-12-31', collapse='daily')
    """
    _request_interval_required = 0

    def get_kw_args(self, period: str, aggregation: int, ticker: str, output_size=OPS.FULL, limit=0, offset=0):
        symbol = ticker.upper()
        limit = 300 if limit == 0 else limit
        file_path = 'D:/PD_Intraday_Data/5_min/{}.de.txt'.format(ticker.lower())
        return {'period': period, 'symbol': symbol, 'aggregation': aggregation,
                'limit': limit, 'filepath': file_path, 'offset': offset}

    def __get_data_frame_by_kwargs__(self, print_message=True):
        try:
            self._df = self.__get_data_frame__()
            if self._df is not None:
                self._df_data = self._df[self._df.columns]
                start_dt = MyDate.get_date_time_from_epoch_seconds(self._df_data.index[0])
                end_dt = MyDate.get_date_time_from_epoch_seconds(self._df_data.index[-1])
                print('\n{} (offset: {}) - Retrieved from {}: {} - {}'.format(
                    self.kw_symbol, self.kw_offset, self.kw_filepath, start_dt, end_dt))
        except:
            if print_message:
                print('PROBLEM with retrieving data from StooqIntraday for {}'.format(self.kw_symbol))

    def __get_data_frame__(self) -> pd.DataFrame:
        df = pd.read_csv(self.kw_filepath, sep=',', header=0)
        if df is not None:
            if self.kw_offset > 0:
                offset_value = df['Date'].unique()[-self.kw_offset]
                df = df[df['Date']<offset_value]
            if df.shape[0] > self.kw_limit:
                df = df[-self.kw_limit:]
            df[CN.TIMESTAMP] = df.apply(self.__get_time_stamp_for_data_frame__, axis=1)
            df.set_index(CN.TIMESTAMP, drop=True, inplace=True)
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            df.columns = CN.get_standard_column_names()
        return df

    def __get_time_stamp_for_data_frame__(self, row) -> int:
        return int(MyDate.get_epoch_seconds_for_date_time_strings(row['Date'], row['Time']))


class AlphavantageJSONFetcher (APIBaseFetcher):
    _request_interval_required = 15  # we have only 5 _request per minute for free api-key, 15 instead of 12 for security

    def get_kw_args(self, period: str, aggregation: int, ticker: str, output_size=OPS.FULL, limit=400):
        return {'symbol': ticker, 'period': period, 'aggregation': aggregation,
                'output_size': output_size, 'limit': limit}

    def retrieve_data(self, **kwargs):
        # symbol: str, period=PRD.DAILY, aggregation=1, output_size=OPS.COMPACT):
        APIBaseFetcher.retrieve_data(self, **kwargs)
        if self._df is not None:
            self._df_data = self._df[self._get_column_list_for_data_()]
            self._df_volume = self._df[self._get_column_for_volume_()]

    @property
    def class_last_request_ts(self):
        return AlphavantageJSONFetcher._last_request_ts

    @class_last_request_ts.setter
    def class_last_request_ts(self, value):
        AlphavantageJSONFetcher._last_request_ts = value

    @property
    def class_request_interval_required(self):
        return AlphavantageJSONFetcher._request_interval_required

    def _get_column_list_for_data_(self):
        pass

    def _get_column_for_data_(self):
        pass

    def _get_column_for_volume_(self):
        pass

    def get_json_data_key(self):
        pass

    def _get_api_key_(self):
        return os.environ["alphavantage_apikey"]

    def plot_data_frame(self):
        fig, axes = plt.subplots(nrows=2, ncols=1)
        plot_01 = self.df_data[[self._get_column_for_data_()]].plot(ax=axes[0], title=self.kw_symbol)
        plot_01.legend(loc='upper left')
        plt.tight_layout()
        self.df_volume.plot(ax=axes[1], title = self._get_column_for_volume_())
        plt.show()


class AlphavantageStockFetcher (AlphavantageJSONFetcher):
    def _get_column_list_for_data_(self):
        return self._df_columns

    def _get_column_for_data_(self):
        return self._df_columns[-2]

    def _get_column_for_volume_(self):
        return self._df_columns[-1]

    def get_url_function(self):
        if 'function' in self._kwargs:
            return self._kwargs['function']
        function_dict = {PRD.WEEKLY: 'TIME_SERIES_WEEKLY', PRD.DAILY: 'TIME_SERIES_DAILY',
                         PRD.INTRADAY: 'TIME_SERIES_INTRADAY'}
        return function_dict[self.kw_period]

    def get_json_data_key(self):
        dict = {PRD.DAILY: 'Time Series (Daily)',
                PRD.WEEKLY: 'Weekly Time Series', # OLD 'Time Series (Weekly)',
                PRD.INTRADAY: 'Time Series ({}min)'.format(self.kw_aggregation)}
        return dict[self.kw_period]

    def __get_data_frame__(self, request_data) -> pd.DataFrame:
        json_data = request_data.json()
        time_series = json_data[self.get_json_data_key()]  # e.g. Time Series (Daily)
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df = df.assign(Timestamp=df.index.map(MyDate.get_epoch_seconds_from_datetime))
        df[CN.TIMESTAMP] = df[CN.TIMESTAMP].apply(int)
        df.set_index(CN.TIMESTAMP, drop=True, inplace=True)
        df.columns = CN.get_standard_column_names()
        return df

    def __retrieve_ticker__(self, request_data) -> Ticker:
        json_data = request_data.json()
        global_quote = json_data["Global Quote"]
        symbol = global_quote["01. symbol"]
        high = float(global_quote['03. high'])
        low = float(global_quote['04. low'])
        price = float(global_quote["05. price"])
        volume = float(global_quote["06. volume"])
        return Ticker(ticker_id=symbol, bid=price, ask=price, last_price=price,
                      low=low, high=high, vol=volume, ts=MyDate.time_stamp_now())

    def _get_url_(self):
        symbol = self._kwargs['symbol']
        url = 'https://www.alphavantage.co/query?function={}&symbol={}'.format(self.get_url_function(), symbol)
        if self.kw_output_size == OPS.FULL:
            url = url + '&outputsize=full'
        if self.kw_period == PRD.INTRADAY:
            url = url + '&interval={}min'.format(self.kw_aggregation)
        return url + '&apikey=' + self._api_key


class AlphavantageForexFetcher (AlphavantageJSONFetcher):
    def _get_column_list_for_data_(self):
        return self._df_columns

    def _get_column_for_data_(self):
        return self._df_columns[-2]

    def _get_column_for_volume_(self):
        return self._df_columns[-1]

    def get_url_function(self):
        dict = {PRD.WEEKLY: 'FX_WEEKLY',
                PRD.DAILY: 'FX_DAILY',
                PRD.INTRADAY: 'FX_INTRADAY'}
        return dict[self.kw_period]

    def get_json_data_key(self):
        dict = {PRD.DAILY: 'Time Series FX (Daily)',
                PRD.WEEKLY: 'Time Series FX (Weekly)',
                PRD.INTRADAY: 'Time Series FX ({}min)'.format(self.kw_aggregation)}
        return dict[self.kw_period]

    def __get_data_frame__(self, request_data) -> pd.DataFrame:
        json_data = request_data.json()
        time_series = json_data[self.get_json_data_key()]  # e.g. Time Series (Daily)
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df = df.assign(Timestamp=df.index.map(MyDate.get_epoch_seconds_from_datetime))
        df[CN.TIMESTAMP] = df[CN.TIMESTAMP].apply(int)
        df.set_index(CN.TIMESTAMP, drop=True, inplace=True)
        df[CN.VOL] = 0
        df.columns = CN.get_standard_column_names()
        return df

    def _get_url_(self):
        symbol = self._kwargs['symbol']
        from_symbol = symbol[:3]
        to_symbol = symbol[3:]
        url = 'https://www.alphavantage.co/query?function={}&from_symbol={}&to_symbol={}'.format(
            self.get_url_function(), from_symbol, to_symbol)
        if self.kw_output_size == OPS.FULL:
            url = url + '&outputsize=full'
        if self.kw_period == PRD.INTRADAY:
            url = url + '&interval={}min'.format(self.kw_aggregation)
        return url + '&apikey=' + self._api_key


class AlphavantageCryptoFetcher(AlphavantageJSONFetcher):
    def retrieve_data(self, **kwargs):
        # symbol: str, period=PRD.DAILY, aggregation=1):
        AlphavantageJSONFetcher.retrieve_data(self, **kwargs)

    def _get_column_list_for_data_(self):
        return self._df_columns

    def _get_column_for_data_(self):
        return self._df_columns[-2]

    def _get_column_for_volume_(self):
        return self._df_columns[-1]

    def get_url_function(self):
        dict = {PRD.WEEKLY: 'DIGITAL_CURRENCY_WEEKLY',
                PRD.DAILY: 'DIGITAL_CURRENCY_DAILY',
                PRD.INTRADAY: 'DIGITAL_CURRENCY_INTRADAY'}
        return dict[self.kw_period]

    def get_json_data_key(self):
        dict = {PRD.DAILY: 'Time Series (Digital Currency Daily)',
                PRD.INTRADAY: 'Time Series (Digital Currency Intraday)'}
        return dict[self.kw_period]

    def __get_data_frame__(self, request_data) -> pd.DataFrame:
        json_data = request_data.json()
        time_series = json_data[self.get_json_data_key()]
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df = df.assign(Timestamp=df.index.map(MyDate.get_epoch_seconds_from_datetime))
        df[CN.TIMESTAMP] = df[CN.TIMESTAMP].apply(int)
        df.set_index(CN.TIMESTAMP, drop=True, inplace=True)
        if self.kw_period == PRD.INTRADAY:
            df.drop([df.columns[0],  '3. market cap (USD)'], axis=1, inplace=True)
            df.columns = [CN.CLOSE, CN.VOL]
            df.insert(loc=1, column=CN.LOW, value = df[df.columns[0]])
            df.insert(loc=1, column=CN.HIGH, value=df[df.columns[0]])
            df.insert(loc=1, column=CN.OPEN, value=df[df.columns[0]])  # [CN.OPEN, CN.HIGH, CN.LOW, CN.CLOSE, CN.VOL]
        else:
            # https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_WEEKLY&symbol=BTC&market=CNY&apikey=demo
            # 1a. open (CNY), 1b. open (USD), 2a. high (CNY), 2b. high (USD),
            # 3a. low (CNY), 3b. low (USD), 4a. close (CNY), 4b. close (USD), 5. volume
            df.drop(['1b. open (USD)', '2b. high (USD)', '3b. low (USD)', '4b. close (USD)', '6. market cap (USD)'],
                    axis=1, inplace=True)
            df.columns = CN.get_standard_column_names()
        return df

    def _get_url_(self):  # the _symbol has the structure symbolCCY like BTCUSD
        symbol = self.kw_symbol[:-3]
        market = self.kw_symbol[-3:]
        url = 'https://www.alphavantage.co/query?function={}&symbol={}&market={}&apikey={}'.format(
            self.get_url_function(), symbol, market, self._api_key
        )
        return url


class AlphavantageCSVFetcher (APIBaseFetcher):
    """
    key = CRYPTO for Cryptocurrency list, NYSE for New York Stock Exchange, NAS for Nasdaq, CCY for currencies
    """
    def retrieve_data(self, **kwargs):  # symbol: str='CRYPTO'):
        APIBaseFetcher.retrieve_data(self, **kwargs)

    def __get_data_frame__(self, request_data):
        content = request_data.content
        return pd.read_csv(io.StringIO(content.decode('utf-8')))

    def _get_url_(self):
        if self.kw_symbol == 'CRYPTO':
            return 'https://www.alphavantage.co/digital_currency_list/'
        elif self.kw_symbol == 'CCY':
            return 'https://www.alphavantage.co/physical_currency_list/'


class CryptoCompareJSONFetcher (APIBaseFetcher):
    def retrieve_data(self, **kwargs):  # symbol: str, period: str, aggregation: int, limit: int):
        APIBaseFetcher.retrieve_data(self, **kwargs)
        if self._df is not None:
            self._df_data = self._df[self.get_column_list_for_data()]

    def get_column_list_for_data(self):
        pass

    def __format_columns__(self):
        pass

    def get_json_data_key(self):
        pass

    def _get_api_key_(self):
        return 'not_yet'  # os.environ["cryptocompare_apikey"]  # doesn't exist yet


class CryptoCompareCryptoFetcher(CryptoCompareJSONFetcher):
    def retrieve_data(self, **kwargs):  # symbol: str, period=PRD.DAILY, aggregation=1, limit=200):
        CryptoCompareJSONFetcher.retrieve_data(self, **kwargs)

    def get_column_list_for_data(self):
        return self._df_columns

    def get_json_data_key(self):
        return 'Data'

    def __get_data_frame__(self, request_data) -> pd.DataFrame:
        # https://min-api.cryptocompare.com/data/histominute?fsym=BCH&tsym=USD&limit=300&aggregate=15
        # "time":1540070100,"close":448.07,"high":448.23,"low":447.44,"open":448.01,"volumefrom":184.81,"volumeto":81598.81
        json_data = request_data.json()
        time_series = json_data[self.get_json_data_key()]
        df = pd.DataFrame(time_series)
        df = df[['time', 'open', 'high', 'low', 'close', 'volumeto']]
        df.set_index('time', drop=True, inplace=True)
        df.columns = CN.get_standard_column_names()
        return df

    def _get_url_(self):  # the _symbol has the structure symbolCCY like BTCUSD
        url_function = 'histominute' if self.kw_period == PRD.INTRADAY else 'histoday'
        url_limit = self._get_url_limit_parameter_()
        url_aggregate = self.kw_aggregation if self.kw_period == PRD.INTRADAY else 1
        symbol = self.kw_symbol[:-3]
        market = self.kw_symbol[-3:]
        url = 'https://min-api.cryptocompare.com/data/{}?fsym={}&tsym={}&_limit={}&aggregate={}'.\
            format(url_function, symbol, market, url_limit, url_aggregate)
        return url

    def _get_url_limit_parameter_(self) -> int:
        if self.kw_period == PRD.INTRADAY:
            return self.kw_limit
        return 400


class BitfinexCryptoFetcher(APIBaseFetcher):
    def get_kw_args(self, period: str, aggregation: int, ticker: str, section='hist', limit=400):
        return {'symbol': ticker, 'period': period, 'aggregation': aggregation, 'section': section, 'limit': limit}

    @property
    def kw_section(self) -> str:
        return self._kwargs.get('section', 'hist')

    def retrieve_data(self, **kwargs):  # symbol: str, period=PRD.DAILY, aggregation=1, section='hist', limit=400
        APIBaseFetcher.retrieve_data(self, **kwargs)
        if self._df is not None:
            column_list_data = self.get_column_list_data()
            self._df_data = self._df[column_list_data]

    def get_column_list_data(self):
        return self._df_columns

    def _get_api_key_(self):
        return ''

    def __get_data_frame__(self, request_data) -> pd.DataFrame:
        json_data = self.__get_json_data_from_request_data__(self.kw_symbol, request_data)
        if json_data is not None:
            return self.__get_data_frame_from_json__(json_data)

    @staticmethod
    def __get_data_frame_from_json__(json_data):
        if type(json_data[0]) is list:
            df = pd.DataFrame(json_data)
        else:
            series = pd.Series(json_data).values.reshape(1, len(json_data))
            df = pd.DataFrame(series)
        for ind, row in df.iterrows():  # the values are delivered with ms instead of seconds
            df.at[ind, 0] = row[0] / 1000
        df[0] = df[0].apply(int)
        # (1)Open, (2)Close, (3)High, (4)Low -> standard: # [CN.OPEN, CN.HIGH, CN.LOW, CN.CLOSE, CN.VOL]
        df = df[[0, 1, 3, 4, 2, 5]]
        df.set_index(0, drop=True, inplace=True)
        df.columns = CN.get_standard_column_names()
        df = df.sort_index()
        # _df.sort_index(inplace=True)
        return df

    def __get_json_data_from_request_data__(self, symbol, request_data):
        json_data = request_data.json()
        if self.__are_retrieved_data_correct__(json_data):
            return json_data
        return None

    def __are_retrieved_data_correct__(self, json_data):
        # JSON in error case: ["error", 11010, "ratelimit: error"] or []
        return len(json_data) > 0 and "error" not in json_data

    def _get_url_(self):  # the _symbol has the structure tsymbolCCY like tBTCUSD
        # https://api.bitfinex.com/v2/candles/trade:5m:tBTCUSD/hist
        # _symbol: e.g. tBTCUSD
        # time_frame: '1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D', '7D', '14D', '1M'
        # section = hist or last
        # limit = any number
        # return: MTS	int	millisecond time stamp
        # OPEN	float	First execution during the time frame
        # CLOSE	float	Last execution during the time frame
        # HIGH	float	Highest execution during the time frame
        # LOW	float	Lowest execution during the timeframe
        # VOLUME	float	Quantity of _symbol traded within the timeframe
        url_t_f = self.__get_url_time_frame__(self.kw_period, self.kw_aggregation)
        symbol = 't{}'.format(self.kw_symbol)
        if self.kw_section == 'last':
            url = 'https://api.bitfinex.com/v2/candles/trade:{}:{}/last'.format(url_t_f, symbol)
        elif self.kw_limit == 0:
            url = 'https://api.bitfinex.com/v2/candles/trade:{}:{}/hist'.format(url_t_f, symbol)
        else:
            url = 'https://api.bitfinex.com/v2/candles/trade:{}:{}/hist?limit={}'.format(url_t_f, symbol, self.kw_limit)
        return url

    def __get_url_time_frame__(self, period: str, aggregation: int):
        if period == PRD.DAILY:
            return '1D'
        hours = int(aggregation/60)
        if hours > 0:
            return '{}h'.format(hours)
        return '{}m'.format(aggregation)


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
        pass

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
        alphavantage_stock_fetcher = AlphavantageStockFetcher()
        for symbol in self.symbol_list:
            alphavantage_stock_fetcher.retrieve_data(**{'symbol': symbol})
            self.df_dic[symbol] = alphavantage_stock_fetcher.df_data


class CryptoCorrelationHandler(CorrelationHandler):
    def __fill_df_dic_for_symbol_list__(self):
        alphavantage_crypto_fetcher = AlphavantageCryptoFetcher()
        for symbol in self.symbol_list:
            alphavantage_crypto_fetcher.retrieve_data(**{'symbol': symbol})
            self.df_dic[symbol] = alphavantage_crypto_fetcher.df_data
