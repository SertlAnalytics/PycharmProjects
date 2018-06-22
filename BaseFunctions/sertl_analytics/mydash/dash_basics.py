"""
Description: This module is the main module for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""


import pandas as pd
from dash import Dash
import matplotlib.pyplot as plt
import pandas_datareader.data as web
from datetime import datetime

class MyDash:
    def __init__(self):
        self.f = None

    def read_csv(self):
        self.df = pd.read_csv('salaries.csv')
        print(self.df.head())
        self.df.plot()
        # self.df.boxplot()
        # Dash.config
        plt.show()

    def print(self):
        if self.f is None:
            print('a')

    def read_stock_data_from_morningstar(self):
        start = datetime(2015, 2, 9)
        end = datetime(2018, 5, 24)
        f = web.DataReader('BB', 'morningstar', start, end)
        print(f)
        # print(f.head())

    def read_stock_data_from_quandl(self):
        symbol = 'WIKI/AAPL'  # or 'AAPL.US'
        symbol = 'MMM.US'
        start = datetime(2015, 2, 9)
        end = datetime(2018, 5, 24)
        df = web.DataReader(symbol, 'quandl', '2017-01-01', '2018-06-22')
        print(df.head())


my_dash = MyDash()
my_dash.read_stock_data_from_quandl()