import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import func
from sqlalchemy import create_engine
import requests

# Create an engine that connects to the census.sqlite file: engine
engine = create_engine('sqlite:///MyFirstdb.db')

# Print table names
print(engine.table_names())

# Import package
import requests

# Assign URL to variable: url
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey=demo'

# Package the request, send the request and catch the response: r
r = requests.get(url)

# Decode the JSON data into a dictionary: json_data
json_data = r.json()

# Print each key-value pair in json_data
for k in json_data.keys():
    print(k + ': ', json_data[k])

