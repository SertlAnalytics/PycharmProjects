from fredapi import Fred
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

fred = Fred(api_key='10ea8a3688d94a2274fdff5c6579cd57')
data = fred.get_series('DDOI02CNA156NWDB')  # SP500

"""
https://fred.stlouisfed.org/
https://fred.stlouisfed.org/series/SP500
https://fred.stlouisfed.org/series/LFWA64TTUSM647S Working Age Population
https://fred.stlouisfed.org/series/MEPAINUSA672N Real Median Personal Income in the United States
Real Disposable Personal Income: Per Capita (A229RX0)
"""

print(type(data))
df = pd.DataFrame(data, columns=['Value'])
df = df.dropna()

print(df.info())
print(df.describe())
print(df.head())

df.index = pd.to_datetime(df.index)
# df = df.resample(rule='M').last()
print(df.head())
df['Value_PCT'] = df['Value'].pct_change()
auto_correlation = df['Value_PCT'].autocorr()
print('The auto_correlation is: ', auto_correlation)

df['Value'].plot()
# plt.yticks([1000, 2000, 3000])
# plt.yscale('log')

plt.show()
