"""
Description: This module fetch data from any source. Transforms them into pd.DataFrame and plots them.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sertl_analytics.environment  # init some environment variables during load - for security reasons
import seaborn as sns
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher
import stock_database
from stock_database import StockSymbols
from mpl_finance import candlestick_ohlc
import matplotlib.dates as dt
from matplotlib.patches import Circle, Wedge, Polygon, Rectangle
from matplotlib.collections import PatchCollection

class CN:
    OPEN = 'Open'
    HIGH = 'High'
    LOW = 'Low'
    CLOSE = 'Close'
    VOL = 'Volume'


class FT:
    NONE = 'NONE'
    TRIANGLE_H = 'Triangle - horizontal'
    TRIANGLE_U = 'Triangle - rizing'
    TRIANGLE_D = 'Triangle - falling'
    RANGE_H = 'Range - horizontal'
    RANGE_U = 'Range - rizing'
    RANGE_D = 'Range - falling'


class FormationDetector():
    def __init__(self, df: pd.DataFrame, ticks: int = 15):
        self.df = df
        self.ticks = ticks
        self.formation_dic = {}

    def parse_df(self):
        pos = -1
        while pos < self.df.shape[0] - self.ticks:
            pos += 1
            formation = Formation(self.df.iloc[pos:pos+self.ticks])
            if formation.formation_type != FT.NONE:
                pos_new_tick = pos + self.ticks + 1
                continue_loop = True
                while continue_loop:
                    tick_df = self.df.iloc[pos_new_tick-1:pos_new_tick]
                    continue_loop = formation.is_tick_fitting_to_formation(tick_df)
                    if continue_loop:
                        formation.add_tick_to_formation(tick_df)
                        pos_new_tick += 1
                self.formation_dic[pos] = formation
                pos += formation.ticks


class Formation():
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.ticks_initial = self.df.shape[0]
        self.check_length = int(self.ticks_initial/3)
        self.part_left = FormationPart(self.df.iloc[0:self.check_length])
        self.part_middle = FormationPart(self.df.iloc[self.check_length:2 * self.check_length])
        self.part_right = FormationPart(self.df.iloc[2 * self.check_length:self.ticks_initial])
        self.threshold = 0
        self.weight = 0
        self.upper_bound = 0
        self.lower_bound = 0
        self.formation_type = FT.NONE
        self.xy = None
        self.check_and_set_formation_parameters()

    @property
    def ticks(self):
        return self.part_left.ticks + self.part_middle.ticks + self.part_right.ticks

    def is_tick_fitting_to_formation(self, tick_df: pd.DataFrame):
        if self.formation_type == FT.RANGE_H:
            for ind, rows in tick_df.iterrows():
                if rows.Close < self.upper_bound + (self.weight * self.threshold):
                    if rows.Close > self.lower_bound - (self.weight * self.threshold):
                        return True
        return False

    def add_tick_to_formation(self, tick_db: pd.DataFrame):
        self.part_right.add_tick(tick_db)

    def check_and_set_formation_parameters(self):
        ft_check_list = [FT.RANGE_H]
        for ft in ft_check_list:
            if self.is_formation_type_applicable(ft):
                self.formation_type = ft
                break

    def is_formation_type_applicable(self, formation_type_to_check: FT):
        self.threshold = self.get_threshold_for_formation_type(formation_type_to_check)
        self.weight = self.get_weight_for_formation_type(formation_type_to_check)
        self.upper_bound = self.get_upper_bound_for_formation_type(formation_type_to_check)
        self.lower_bound = self.get_lower_bound_for_formation_type(formation_type_to_check)
        if self.are_left_right_parts_applicable_for_formation_type(formation_type_to_check):
            return self.is_middle_part_applicable_for_formation_type(formation_type_to_check)
        return False

    def get_threshold_for_formation_type(self, formation_type_to_check: FT):
        if formation_type_to_check == FT.RANGE_H:
            return 0.02
        return 0

    def get_weight_for_formation_type(self, formation_type_to_check: FT):
        if formation_type_to_check == FT.RANGE_H:
            return (self.part_left.mean + self.part_right.mean)/2
        return (self.part_left.mean + self.part_right.mean)/2

    def get_upper_bound_for_formation_type(self, formation_type_to_check: FT):
        if formation_type_to_check == FT.RANGE_H:
            return max(self.part_left.max, self.part_right.max)
        return max(self.part_left.max, self.part_right.max)

    def get_lower_bound_for_formation_type(self, formation_type_to_check: FT):
        if formation_type_to_check == FT.RANGE_H:
            return min(self.part_left.min, self.part_right.min)
        return min(self.part_left.min, self.part_right.min)

    def are_left_right_parts_applicable_for_formation_type(self, formation_type_to_check: FT):
        if formation_type_to_check == FT.RANGE_H:
            if abs(self.part_left.max - self.part_right.max) / self.weight < self.threshold:
                if abs(self.part_left.min - self.part_right.min) / self.weight < self.threshold:
                    return True
        return False

    def set_xy_formation_parameter(self):
        if self.formation_type == FT.RANGE_H:
            x_dates_left = self.part_left.df.first_valid_index()
            x_dates_right = self.part_right.df.last_valid_index()
            y_max = self.upper_bound + self.weight * self.threshold
            y_min = self.lower_bound - self.weight * self.threshold
            x_dates = [x_dates_left, x_dates_left, x_dates_right, x_dates_right]
            x = list(dt.date2num(x_dates))
            y = [y_max, y_min, y_min, y_max]
            self.xy = list(zip(x, y))

    def get_shape(self):
        self.set_xy_formation_parameter()
        if self.formation_type == FT.RANGE_H:
            return Polygon(np.array(self.xy), True)

    def print_formation_data(self):
        df_total = pd.concat([self.part_left.df, self.part_middle.df, self.part_right.df])
        print('Total: min={}, max={}, std={}'.format(df_total[CN.HIGH].min(), df_total[CN.HIGH].max(),
                                                        df_total[CN.HIGH].std()))
        # self.part_left.print_data('Left')
        # self.part_middle.print_data('Middle')
        # self.part_right.print_data('Right')

    def is_middle_part_applicable_for_formation_type(self, formation_type_to_check: FT):
        if formation_type_to_check == FT.RANGE_H:
            if abs(self.part_middle.max - self.upper_bound) / self.weight < self.threshold:
                if abs(self.part_left.min - self.lower_bound) / self.weight < self.threshold:
                    return True
        return False


class FormationPart():
    def __init__(self, df: pd.DataFrame):
        self.df = df

    @property
    def ticks(self):
        return self.df.shape[0]

    @property
    def max(self):
        return self.df[CN.HIGH].max()

    @property
    def id_max(self):
        return self.df[CN.HIGH].idxmax(axis=0)

    @property
    def min(self):
        return self.df[CN.LOW].min()

    @property
    def id_min(self):
        return self.df[CN.HIGH].idxmin(axis=0)

    @property
    def mean(self):
        return self.df[CN.CLOSE].mean()

    def add_tick(self, tick_df: pd.DataFrame):
        self.df = pd.concat([self.df, tick_df])

    def print_data(self, part: str):
        print('\n{}: min={}, max={} \n{}'.format(part, self.min, self.max, self.df.head(self.ticks)))


class FormationPlotter:
    def __init__(self, api_object):
        self.api_object = api_object  # StockDatabaseDataFrame or AlphavantageStockFetcher
        self.api_object_class = self.api_object.__class__.__name__
        self.df = api_object.df
        self.df_data = api_object.df_data
        self.column_data = api_object.column_data
        self.df_volume = api_object.df_volume
        self.column_volume = api_object.column_volume
        self.symbol = api_object.symbol

    def plot_data_frame(self):
        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 10), sharex=True)

        plot_01 = self.df_data[[self.column_data]].plot(ax=axes[0], title=self.symbol)
        plot_01.legend(loc='upper left')
        # plt.figtext = 'Hallo'
        plt.tight_layout()

        ohlc = []

        for ind, rows in self.df.iterrows():
            append_me = dt.date2num(ind), rows['Open'], rows['High'], rows['Low'], rows['Close']
            ohlc.append(append_me)

        candlestick_ohlc(axes[1], ohlc, width = 0.4, colorup = 'g')
        # self.df_data[[self.column_data]].plot(ax=axes[1], title=self.symbol)

        axes[1].xaxis_date()
        self.add_formations(axes[1], fig)

        self.df_volume.plot(ax=axes[2], title=self.column_volume)

        plt.xticks(rotation=45)
        plt.show()

    def add_formations(self, ax, fig):
        detector = FormationDetector(self.df_data, 15)  # the number should be a multiple of 3
        detector.parse_df()
        patches = []
        for ind in detector.formation_dic:
            formation = detector.formation_dic[ind]
            patches.append(formation.get_shape())
            formation.print_formation_data()

        colors = 100 * np.random.rand(len(patches))
        p = PatchCollection(patches, alpha=0.4)
        p.set_array(np.array(colors))
        ax.add_collection(p)
        # fig.colorbar(p, ax=ax)


db = True
if db:
    stock_db = stock_database.StockDatabase()
    and_clause = "Date BETWEEN '2010-10-01' AND '2010-12-31'"
    and_clause = ''
    stock_db_df_obj = stock_database.StockDatabaseDataFrame(stock_db, StockSymbols.Apple, and_clause)
    plotter = FormationPlotter(stock_db_df_obj)
    plotter.plot_data_frame()
else:
    fetcher = AlphavantageStockFetcher('IBM')  # stock: MSFT, Crypto: BTC, AAPL, IBM
    plotter = FormationPlotter(fetcher)
    plotter.plot_data_frame()





