#### Get ticker for largest company
import pandas as pd
nasdaq = pd.read_excel('listing.xlsx', sheetname ='nasdaq', na_values ='n/a')
nasdaq = nasdaq.sort_values('Market Capitalization', ascending = False)
nasdaq[['Stock Symbol', 'Company Name']].head(3)
largest_by_market_cap = nyse.iloc[0]  # 1st row
largest_by_market_cap['Stock Symbol']
market_cap = nasdaq['Market Capitalization'].div(10**6)
market_cap.mean()
market_cap.median()
market_cap.mode()

# Exercise 1 - list the poorest and richest countries worldwide
import pandas as pd

# Import the data
income = pd.read_csv('per_capita_income.csv')

# Inspect the result
income.info()

# Sort the data by income
income = income.sort_values('Income per Capita', ascending=False)

# Display the first and last five rows
print(income.head(5))
print(income.tail(5))

# Exercise 2 - Global incomes: Central tendency