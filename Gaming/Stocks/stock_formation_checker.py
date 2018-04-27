"""
Description: This module fetch data from any source. Transforms them into pd.DataFrame and plots them.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""

import pandas as pd
import matplotlib.pyplot as plt
import sertl_analytics.environment  # init some environment variables during load - for security reasons
import seaborn as sns
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher
from mpl_finance import candlestick_ohlc
import matplotlib.dates as dt


class CN:
    OPEN = '1. open'
    HIGH = '2. high'
    LOW = '3. low'
    CLOSE = '4. close'
    VOL = '5. volume'


class FT:
    NONE = 'NONE'
    TRIANGLE_H = 'Triangle - horizontal'
    TRIANGLE_R = 'Triangle - rizing'
    TRIANGLE_F = 'Triangle - falling'


class FormationDetector():
    def __init__(self, df: pd.DataFrame, ticks: int = 15):
        self.df = df
        self.ticks = ticks
        self.formation_dic = {}

    def parse_df(self):
        for i in range(0, self.df.shape[0] - self.ticks):
            formation = Formation(self.df.iloc[i:i+self.ticks])
            if formation.ft != FT.NONE:
                self.formation_dic[i] = formation
                i = i + self.ticks


class Formation():
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.ticks = self.df.shape[0]
        self.check_length = int(self.ticks/3)
        self.part_1 = FormationPart(self.df.iloc[0:self.check_length])
        self.part_2 = FormationPart(self.df.iloc[self.check_length:2*self.check_length])
        self.part_3 = FormationPart(self.df.iloc[2*self.check_length:self.ticks])
        self.med_1_3_max = (self.part_1.max + self.part_2.max)/2
        self.med_1_3_min = (self.part_1.min + self.part_2.min) / 2
        self.diff_1_3_max = (self.part_1.max - self.part_2.max)
        self.diff_1_3_min = (self.part_1.min - self.part_2.min)
        self.ft = self.get_formation_type()
        self.x_dates = self.part_1.id_max, self.part_1.id_min, self.part_3.id_min, self.part_3.id_max,
        self.x = dt.date2num(self.x_dates)
        self.y = self.part_1.max, self.part_1.min, self.part_3.min, self.part_3.max

    def get_formation_type(self) -> FT:
        if not self.is_part_2_fitting():
            return FT.NONE
        return FT.TRIANGLE_F

    def is_part_2_fitting(self):
        if self.part_2.max > self.med_1_3_max:
            return False
        if self.part_2.min < self.med_1_3_min:
            return False
        return True


class FormationPart():
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.ticks = self.df.shape[0]
        self.max = self.df[CN.HIGH].max()
        self.id_max = self.df[CN.HIGH].idxmax(axis=0)
        self.min = self.df[CN.LOW].min()
        self.id_min = self.df[CN.HIGH].idxmin(axis=0)
        # print('df.head()={}\ndf.shape()={}'.format(df.head(), df.shape))


class AlphavantageFetcher4Formation(AlphavantageStockFetcher):
    def plot_data_frame(self):
        print('AlphavantageFetcher4Formation')
        fig, axes = plt.subplots(nrows=3, ncols=1 )
        plot_01 = self.df_data[[self.column_data]].plot(ax=axes[0], title=self.symbol)
        plot_01.legend(loc='upper left')
        plt.tight_layout()

        ohlc = []

        for ind, rows in self.df.iterrows():
            append_me = dt.date2num(ind), rows['1. open'], rows['2. high'], rows['3. low'], rows['4. close']
            ohlc.append(append_me)

        candlestick_ohlc(axes[1], ohlc, width = 0.4, colorup = 'g')
        # self.df_data[[self.column_data]].plot(ax=axes[1], title=self.symbol)

        axes[1].xaxis_date()
        self.add_formations(axes[1])

        self.df_volume.plot(ax=axes[2], title=self.column_volume)

        plt.xticks(rotation=45)
        plt.show()

    def add_formations(self, ax):
        detector = FormationDetector(self.df, 12)
        detector.parse_df()
        for ind in detector.formation_dic:
            formation = detector.formation_dic[ind]
            ax.fill(formation.x, formation.y, "b")  # a blue polygon
            print(formation.x_dates)
            print(formation.y)


fetcher = AlphavantageFetcher4Formation('AAPL')  # stock: MSFT, Crypto: BTC
fetcher.plot_data_frame()

#1. open  2. high  3. low  4. close




