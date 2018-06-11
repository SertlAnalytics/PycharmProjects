import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader.data import DataReader
from datetime import date

start = date(1900,1,1) # default Jan 1, 2010
series_code = 'DGS10'  # 10-year Treasury Rate
data_source = 'fred'  # FED Economic Data Service

data = DataReader(series_code, data_source, start)
data.info()
pd.concat([data.head(3), data.tail(3)])

series_name = '10-year Treasury'
data = data.rename(columns={series_code: series_name})
data.plot(title=series_name)
plt.show()