import pandas as pd
from sqlalchemy import create_engine, MetaData, insert, select, delete
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

stmt = select([stocks])
# stmt = delete([stocks])

# Execute the query to retrieve all the data returned: results
results = connection.execute(stmt).fetchall()
print(type(results))
print(len(results))

# Loop over the results
for result in results:
    print(result)
    print(result.Date, result.Symbol)

# Column('Symbol', String(20)),
# Column('Date', Date()),
# Column('Open', Float()),
# Column('High', Float()),
# Column('Low', Float()),
# Column('Close', Float()),
# Column('Volume', Float()),
# Column('BigMove', Boolean(), default=False),
# Column('Direction', Integer(), default=0)