import pandas as pd
from sqlalchemy import func
from sqlalchemy import create_engine, MetaData
import requests
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, Date

# Create an engine that connects to the census.sqlite file: engine
engine = create_engine('sqlite:///MyStocks.sqlite')

metadata = MetaData()

# Print table names
print(engine.table_names())

# Define a new table with a name, count, amount, and valid column: data
data = Table('Stocks', metadata,
        Column('Period', String(20)), # Monthly, Weekly, Daily, Hourly, Minutely
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
# data = Table('Company', metadata,
#         Column('Symbol', String(10), unique=True),
#         Column('Name', String(100), unique=True),
#         Column('Sector', String(100)),
#         Column('Year', Integer()),
#         Column('Revenues', Float()),
#         Column('Expenses', Float()),
#         Column('Employees', Float()),
#         Column('Savings', Float()),
#         Column('ForcastGrowth', Float())
#     )

# Use the metadata to create the table
metadata.create_all(engine)

# Print table details
print(repr(data))



