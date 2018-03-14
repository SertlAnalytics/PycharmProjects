
#### Get ticker for largest tech company - unique
nyse['Sector'].unique()  # Unique values as numpy array
tech = nyse.loc[nyse.Sector == 'Technology']  # Filter conditions: <=, <, ==, >=, >
tech['Company Name'].head(2)
# Now together with idxmax():
nyse.loc[nyse.Sector == 'Technology', 'Market Capitalization'].idxmax()  # ORACLE

#### Get ticker for largest company
import pandas as pd
nyse = pd.read_excel('listing.xlsx', sheetname = 'nyse', na_values = 'n/a')
nyse = nyse.sort_values('Market Capitalization', ascending = False)
nyse[['Stock Symbol', 'Company Name']].head(3)
largest_by_market_cap = nyse.iloc[0]  # 1st row
largest_by_market_cap['Stock Symbol']  # Select row lable by Id, e.g. 'JNJ' - Johnson & Johnson

#### Get ticker for largest company (2) - set_index
nyse = nyse.set_index('Stock Symbol')  # Stock ticker as index
nyse.info()  # you get the information Index: 3147 entries, JNJ to EAE
# Now you can search by idxmax()
nyse['Market Capitalization'].idxmax()  # index of max value => JNJ again

#### Get data for largest tech company with 2017 IPO
ticker = nyse.loc[(nyse.Sector == 'Technology') & (nyse['IPO Year'] == 2007), 'Market Captitalization'].idxmax()
# Multiple conditions: Parentheses and logical operators
data = DataReader(ticker, 'google')  # start = default = 1.1.2010
# select close and volume:
data = data.loc[:, ['Close', 'Volume']]

#### Plotting these data
import matplotlib.pyplot as plt
data.plot(title = ticker, secondary_y = 'Volume')  # secondary_y: column on tight axis with different scale
plt.tight_layout()  # improving layout by reducing white spaces
plt.show()

####################
import pandas as pd
from pandas_datareader.data import DataReader
from datetime import date
start = date(2015,1,1) # default Jan 1, 2010
end = date(2016, 12, 31)  # default: today
ticker = 'GOOG'
data_source = 'google'
stock_data = DataReader(ticker, data_source, start, end)
stock_data.info()
pd.concat([stock_data.head(3), stock_data.tail(3)])
stock_data.tail(3)
import matplotlib.pyplot as plt
stock_data['Close'].plot(title=ticker)
plt.show()

# ------------------------ FRED

import pandas as pd
from pandas_datareader.data import DataReader
from datetime import date
start = date(1962,1,1) # default Jan 1, 2010
series_code = 'DGS10'  # 10-year Treasury Rate
data_source = 'fred'  # FED Economic Data Service
data = DataReader(series_code, data_source, start)
data.info()
pd.concat([data.head(3), data.tail(3)])
import matplotlib.pyplot as plt
series_name = '10-year Treasury'
data = data.rename(columns={series_code: series_name})
data.plot(title=series_name)
plt.show()

# combine stock and economic data
start = date(1999,1,1) # default Jan 1, 2010
series = 'DDCOILWTICO'  # West Texas Intermdiate Oil Price
data_source = 'fred'  # FED Economic Data Service
oil = DataReader(series, data_source, start)

ticker = 'XOM'  # Exxon Mobile Corporation
data_source = 'google'
stock_data = DataReader(ticker, data_source, start)

data = pd.concat([stock[['Close']], oil], axis=1)
data.info()
data.columns = ['Exxon', 'Oil Price']
data.plot()
plt.show()
#######################
import pandas as pd
from pandas_datareader.data import DataReader
from datetime import date


# Set start date
start = date(1968,1,1)

series = 'GOLDAMGBD228NLBM'

# Import the data
gold_price = DataReader(series, 'fred', start)

# Inspect the price of gold
gold_price.info()

# Plot the price of gold
gold_price.plot(title='Gold Price')

# Show the plot
plt.show()

###################
import pandas as pd
from pandas_datareader.data import DataReader
from datetime import date

# Set the start date
start = date(1950,1,1)

# Define the series codes
series = ['UNRATE', 'CIVPART']

# Import the data
econ_data = DataReader(series, 'fred', start)

# Assign new column labels
econ_data.columns = ['Unemployment Rate','Participation Rate']

# Plot econ_data
econ_data.plot(title='Labor Market', subplots=True)

# Show the plot
plt.show()

############### Compare bond and stock performance
import pandas as pd
from pandas_datareader.data import DataReader
from datetime import date

# Set the start date
start = date(2008,1,1)

# Set the series code
series = ['BAMLHYH0A0HYM2TRIV', 'SP500']

# Import the data
data = DataReader(series, 'fred', start)

# Plot the results
data.plot(title='Performance Comparison', subplots=True)

# Show the plot
plt.show()



