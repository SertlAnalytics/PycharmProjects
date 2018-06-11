import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader.data import DataReader
from datetime import date

# Create the pd.ExcelFile() object
xls = pd.ExcelFile('C:/Users/josef/OneDrive/Datacamp/Import_Managing_Financial Data in Python/Data/listings.xlsx')

# Extract the sheet names from xls
exchanges = xls.sheet_names

# Create an empty list: listings

listing_list = []
# Import the data
for exchange in exchanges:
    listing = pd.read_excel(xls, sheetname=exchange, na_values='n/a')
    listing['Exchange'] = exchange
    listing_list.append(listing)

listings = pd.concat(listing_list)
listing['Sector'].unique()

# Set Stock Symbol as the index
listings = listings.set_index('Stock Symbol')

# Get ticker of the largest consumer services company listed after 1997
ticker = listings.loc[(listings.Sector == 'Consumer Services') & (listings['IPO Year'] > 1998), 'Market Capitalization'].idxmax()
top_3_companies = listings.loc[(listings.Sector == 'Consumer Services') & (listings['IPO Year'] > 1998), 'Market Capitalization'].nlargest(3)

# Convert index to list
top_3_tickers = top_3_companies.index.tolist()

# Set the start date
start = date(1998,1,1)

# Import the stock data
data = DataReader(ticker, 'google', start)

# Plot Close and Volume
data[['Close', 'Volume']].plot(secondary_y='Volume', title=ticker)

# Show the plot
plt.show()

data2 = DataReader(top_3_tickers, 'google', start)
data2[['Close', 'Volume']].to_frame().plot(secondary_y='Volume', title=ticker, subplots=True)
plt.show()