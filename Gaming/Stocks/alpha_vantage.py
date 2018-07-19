import requests
import alpha_vantage
import pandas as pd
import io

API_URL = "https://www.alphavantage.co/query"

data = {
    "function": "TIME_SERIES_DAILY",
    "symbol": "AAPL",
    "outputsize": "compact",
    "datatype": "csv",
    "apikey": "MBNAJ5C1NDPXER69"
    }

data = {
    "function": "DIGITAL_CURRENCY_INTRADAY",
    "symbol": "BTC",
    "market": "EUR",
    "apikey": "MBNAJ5C1NDPXER69",
    "datatype": "csv"
    }

data = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": "MMM",
    "interval": "1min",
    "apikey": "MBNAJ5C1NDPXER69",
    "datatype": "csv"
    }

response = requests.get(API_URL, data).content
rawData = pd.read_csv(io.StringIO(response.decode('utf-8')))
print(rawData.head())