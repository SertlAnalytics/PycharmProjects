import pandas as pd

# 1. Parse incorrect data
# amex = pd.read_csv('amex-listing.csv')

# 2. Deal with missing values
# amex = pd.read_csv('amex-listing.csv', na_values='n/a')

# 3. Properly parse dates
amex = pd.read_csv('amex-listing.csv', na_values='n/a', parse_dates=['Last Update'])
amex = pd.read_csv('C:/Users/josef/OneDrive/Datacamp/Import_Managing_Financial Data in Python/Data/amex-listing.csv', na_values='n/a', parse_dates=['Last Update'])
amex.info()

amex.head(5)  # Shows first n rows (default = 5)
amex.items

# Import the data from Excel
nyse = pd.read_excel('listings.xlsx', sheetname='nyse', na_values='n/a')

# Display the head of the data
print(nyse.head())

# Inspect the data
nyse.info()

# reading first a file
xls = pd.ExcelFile('listings.xlsx')

# Extract sheet names and store in exchanges
exchanges = xls.sheet_names
print(exchanges)
# Create listings dictionary with all sheet data
listings = pd.read_excel(xls, sheetname=exchanges, na_values='n/a')

# Inspect NASDAQ listings
listings['nasdaq'].info()

# 4. Combine data frames - concatenate or stack a list of pd.DataFrames
pd.concat([amex, nasdaq, nyse])

# 4.1. Add a reference column , e.g. amex['Exchange'] = 'AMEX' # this method is called broadcasting

# 4.2 Combine three data frames
nyse = pd.read_excel('listings.xlsx', sheetname='nyse', na_values='n/a')
nasdaq = pd.read_excel('listings.xlsx', sheetname='nasdaq', na_values='n/a')

# Inspect nyse and nasdaq
nyse.info()
nasdaq.info()

# Add Exchange reference columns
nyse['Exchange'] = 'NYSE'
nasdaq['Exchange'] = 'NASDAQ'

# Concatenate DataFrames
combined_listings = pd.concat([nyse, nasdaq])

# Create the pd.ExcelFile() object
xls = pd.ExcelFile('listings.xlsx')

# Extract the sheet names from xls
exchanges = xls.sheet_names

# Create an empty list: listings

listings = []
# Import the data
for exchange in exchanges:
    listing = pd.read_excel(xls, sheetname=exchange, na_values='n/a')
    listing['Exchange'] = exchange
    listings.append(listing)

# Concatenate the listings: listing_data
listing_data = pd.concat(listings)

# Inspect the results
listing_data.info()