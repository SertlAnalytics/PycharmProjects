import pandas as pd
from sqlalchemy import create_engine, MetaData, insert
import requests
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, Date
import math
from datetime import datetime

# Create an engine that connects to the census.sqlite file: engine
engine = create_engine('sqlite:///MyStocks.sqlite')
connection = engine.connect()

metadata = MetaData()
stocks = Table('Stocks', metadata, autoload=True, autoload_with=engine)

# Print table names
print(engine.table_names())

# Assign URL to variable: url
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey=MBNAJ5C1NDPXER69'
# MBNAJ5C1NDPXER69
# Package the request, send the request and catch the response: r
r = requests.get(url)

# Decode the JSON data into a dictionary: json_data
json_data = r.json()

# Format: '2018-03-05': {'1. open': '92.3400', '2. high': '93.3200', '3. low': '92.2600', '4. close': '93.2600', '5. volume': '7551233'},
# Print each key-value pair in json_data
print(json_data)

meta_data = json_data["Meta Data"]
symbol = meta_data["2. Symbol"]
time_series = json_data["Time Series (Daily)"]  # Time Series (Daily)

# Symbol: MSFT - Date: 2017-10-10 - 1. open: 76.3300
# Symbol: MSFT - Date: 2017-10-10 - 2. high: 76.6300
# Symbol: MSFT - Date: 2017-10-10 - 3. low: 76.1400
# Symbol: MSFT - Date: 2017-10-10 - 4. close: 76.2900
# Symbol: MSFT - Date: 2017-10-10 - 5. volume: 13734627

# Column('Symbol', String(20)),
# Column('Date', Date()),
# Column('Open', Float()),
# Column('High', Float()),
# Column('Low', Float()),
# Column('Close', Float()),
# Column('Volume', Float()),
# Column('BigMove', Boolean(), default=False),
# Column('Direction', Integer(), default=0)

input_list = []
close_previous = 0
for dates in time_series.keys():
    date = datetime.strptime(dates, '%Y-%m-%d')
    values = time_series[dates]
    open = float(values["1. open"])
    high = float(values["2. high"])
    low = float(values["3. low"])
    close = float(values["4. close"])
    volume = float(values["5. volume"])
    big_move = False  # default
    direction = 0  # default

    if close_previous != 0:
        if abs((close_previous - close)/close) > 0.03:
            big_move = True
            direction = math.copysign(1, close - close_previous)
    close_previous = close

    input_dic = {'Symbol': symbol, 'Date': date, 'Open': open, 'High': high, 'Low': low, 'Close': close
        , 'Volume': volume, 'BigMove': big_move, 'Direction': direction}

    input_list.append(input_dic)
    print(input_dic)

stmt = insert(stocks)
results = connection.execute(stmt, input_list)

print(results.rowcount)


