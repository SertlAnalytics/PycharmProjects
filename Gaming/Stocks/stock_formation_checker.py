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
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, ApiPeriod, ApiOutputsize
import stock_database
from stock_database import StockSymbols
from mpl_finance import candlestick_ohlc
import matplotlib.dates as dt
from matplotlib.patches import Circle, Wedge, Polygon, Rectangle
from matplotlib.collections import PatchCollection
from datetime import datetime

class CN:
    OPEN = 'Open'
    HIGH = 'High'
    LOW = 'Low'
    CLOSE = 'Close'
    VOL = 'Volume'


class FT:
    NONE = 'NONE'
    TRIANGLE = 'Triangle'
    CHANNEL = 'Channel'  # https://www.investopedia.com/articles/trading/05/020905.asp


class FD:
    NONE = 'NONE'
    HOR = 'horizontal'
    ASC = 'ascending'
    DESC = 'descending'


class TradeResult:
    def __init__(self):
        self.bought_at = 0
        self.expected_win = 0
        self.actual_win = 0
        self.max_ticks = 0
        self.actual_ticks = 0
        self.stop_loss_at = 0
        self.stop_loss_reached = False
        self.formation_consistent = False

    def print(self):
        print('bought_at = {}, expected_win = {}, actual_win = {}, ticks: {}/{}, stop_loss = {} ({}), formation_ok: {}'
                .format(self.bought_at, self.expected_win, self.actual_win, self.actual_ticks, self.max_ticks,
                        self.stop_loss_at, self.stop_loss_reached, self.formation_consistent))

class FormationDetector:
    def __init__(self, df: pd.DataFrame, ticks: int = 15, accuracy_pct: float = 0.02):
        self.df = df
        self.ticks = ticks
        self.accuracy_pct = accuracy_pct
        self.formation_dic = {}

    def parse_df(self):
        pos = -1
        while pos < self.df.shape[0] - self.ticks:
            pos += 1
            formation = Channel(self.df.iloc[pos:pos+self.ticks], self.accuracy_pct)
            if formation.is_formation_applicable():
                pos_new_tick = pos + self.ticks + 1
                continue_loop = True
                while continue_loop:
                    tick_df = self.df.iloc[pos_new_tick-1:pos_new_tick]
                    continue_loop = formation.is_tick_fitting_to_formation(tick_df)
                    if continue_loop:
                        formation.add_tick_to_formation(tick_df)
                        pos_new_tick += 1
                    else:
                        left_boundary = pos_new_tick - 1
                        right_boundary = min(left_boundary + formation.ticks, self.df.shape[0])
                        formation.control_df = self.df.iloc[left_boundary:right_boundary]
                formation.finalize()
                if formation.buy_at_breakout:
                    self.formation_dic[pos] = formation
                pos += formation.ticks

    def print_statistics(self, investment: float):
        counter_actual_ticks = 0
        counter_ticks = 0
        counter_stop_loss = 0
        counter_formation_OK = 0
        counter_formation_NOK = 0

        investment_working = investment
        investment_start = investment

        for ind in self.formation_dic:
            formation = self.formation_dic[ind]
            result = formation.trade_result
            counter_actual_ticks += result.actual_ticks
            counter_ticks += result.max_ticks
            counter_stop_loss = counter_stop_loss + 1 if result.stop_loss_reached else counter_stop_loss
            counter_formation_OK = counter_formation_OK + 1 if result.formation_consistent else counter_formation_OK
            counter_formation_NOK = counter_formation_NOK + 1 if not result.formation_consistent else counter_formation_NOK
            traded_entities = int(investment_working / result.bought_at)
            investment_working = investment_working + (traded_entities * result.actual_win)

        diff_pct = round((investment_working - investment_start)/investment_start, 4) * 100
        print('Investment change: {} -> {}, Diff: {}%'.format(investment_start, investment_working, diff_pct))
        print('counter_stop_loss = {}, counter_formation_OK = {}, counter_formation_NOK = {}, ticks = {}'.format(
            counter_stop_loss, counter_formation_OK, counter_formation_NOK, counter_actual_ticks
        ))

class Formation:
    def __init__(self, df_start: pd.DataFrame, accuracy_pct: float):
        self.direction = FD.NONE
        self.df_start = df_start
        self.df_final = None
        self.ticks_initial = self.df_start.shape[0]
        self.check_length = int(self.ticks_initial/3)
        self.part_left = FormationPart(self.df_start.iloc[0:self.check_length])
        self.part_middle = FormationPart(self.df_start.iloc[self.check_length:2 * self.check_length])
        self.part_right = FormationPart(self.df_start.iloc[2 * self.check_length:self.ticks_initial])
        self.accuracy_pct = accuracy_pct
        self.upper_bound = self.__get_upper_bound__()
        self.lower_bound = self.__get_lower_bound__()
        self.upper_limit = self.upper_bound + self.weight * self.accuracy_pct
        self.lower_limit = self.lower_bound - self.weight * self.accuracy_pct
        self.xy = None
        self.xy_control = None
        self.control_df = pd.DataFrame   # DataFrame to be checked for expected/real results after breakout
        self.date_first = None
        self.date_last = None
        self.breakout_tick_predecessor = None  # is set during finalize()
        self.breakout_tick = None  # is set during finalize()
        self.buy_at_breakout = False  # is set during finalize()
        self.trade_result = TradeResult()

    @property
    def type(self):
        return FT.NONE

    @property
    def weight(self):
        return (self.part_left.mean + self.part_right.mean)/2

    @property
    def ticks(self):
        return self.part_left.ticks + self.part_middle.ticks + self.part_right.ticks

    def __get_upper_bound__(self):
        return max(self.part_left.max, self.part_right.max)

    def __get_lower_bound__(self):
        return min(self.part_left.min, self.part_right.min)

    def is_formation_applicable(self):
        return False

    def are_left_right_parts_applicable_for_formation_type(self):
        return False

    def is_middle_part_applicable_for_formation_type(self):
        return False

    def is_tick_fitting_to_formation(self, tick_df: pd.DataFrame):
        return False

    def add_tick_to_formation(self, tick_db: pd.DataFrame):
        self.part_right.add_tick(tick_db)

    def set_xy_formation_parameter(self):
        pass

    def set_xy_control_parameter(self):
        pass

    def get_shape(self):
        return None

    def get_control_shape(self):
        pass

    def finalize(self):
        self.df_final = pd.concat([self.part_left.df, self.part_middle.df, self.part_right.df])
        self.date_first = self.df_final.first_valid_index()
        self.date_last = self.df_final.last_valid_index()
        self.breakout_tick_predecessor = self.df_final.loc[self.date_last]
        self.breakout_tick = self.control_df.iloc[0]
        self.direction = self.__get_breakout_direction__()
        self.buy_at_breakout = self.__is_breakout_a_signal__()
        if self.buy_at_breakout:
            self.__fill_trade_result__()

    def __get_breakout_direction__(self):
        pass

    def __is_breakout_a_signal__(self):
        return False

    def print_formation_data(self):
        date_left = datetime.strptime(str(self.date_first), '%Y-%m-%d %H:%M:%S').date()
        date_right = datetime.strptime(str(self.date_last), '%Y-%m-%d %H:%M:%S').date()
        min_v = round(self.df_final[CN.LOW].min(), 2)
        max_v = round(self.df_final[CN.HIGH].max(), 2)
        std_v = round(self.df_final[CN.HIGH].std(), 2)
        result, expected, ticks, hit = self.get_trade_result()
        print('Total for {} -> {}: min = {}, max = {}, std = {}: \n---> {}: result = {} after {} ticks - expected: {}.'.
              format(date_left, date_right, min_v, max_v, std_v, hit, result, ticks, expected))
        # print('formation.control_df={}'.format(self.control_df.head()))
        # self.part_left.print_data('Left')
        # self.part_middle.print_data('Middle')
        # self.part_right.print_data('Right')

    def __fill_trade_result__(self):
        self.trade_result.expected_win = round(self.upper_limit - self.lower_limit, 2) / 2
        self.trade_result.bought_at = round(self.get_buying_price(), 2)
        self.trade_result.max_ticks = self.control_df.shape[0]
        # self.trade_result.stop_loss_at = self.upper_bound if self.direction == FD.ASC else self.lower_bound
        self.trade_result.stop_loss_at = self.weight if self.direction == FD.ASC else self.weight

        for ind, rows in self.control_df.iterrows():
            self.trade_result.actual_ticks += 1
            if self.direction == FD.ASC:
                self.trade_result.actual_win = round(rows.Close - self.trade_result.bought_at, 2)  # default
                if rows.Low < self.trade_result.stop_loss_at:
                    self.trade_result.stop_loss_reached = True
                    self.trade_result.actual_win = round(self.trade_result.stop_loss_at - self.trade_result.bought_at, 2)
                    break
                if rows.High > self.upper_limit + self.trade_result.expected_win:
                    self.trade_result.actual_win = round(rows.High - self.trade_result.bought_at, 2)
                    self.trade_result.formation_consistent = True
                    break
            else:
                self.trade_result.actual_win = round(self.trade_result.bought_at - rows.Close, 2)  # default
                if rows.Low > self.trade_result.stop_loss_at:
                    self.trade_result.stop_loss_reached = True
                    self.trade_result.actual_win = round(self.trade_result.bought_at - self.trade_result.stop_loss_at,
                                                         2)
                    break
                if rows.Low < self.lower_limit - self.trade_result.expected_win:
                    self.trade_result.actual_win = round(self.trade_result.bought_at - rows.Low, 2)
                    self.trade_result.formation_consistent = True
                    break

    def get_trade_result(self):
        return self.trade_result.actual_win, self.trade_result.expected_win, self.trade_result.actual_ticks\
            , self.trade_result.formation_consistent

    def get_buying_price(self):  # the breakout will be bought after the confirmation (close!!!)
        return self.control_df.iloc[0].Close


class Channel(Formation):
    @property
    def type(self):
        return FT.CHANNEL

    @property
    def weight(self):
        return (self.part_left.mean + self.part_right.mean) / 2

    @property
    def ticks(self):
        return self.part_left.ticks + self.part_middle.ticks + self.part_right.ticks

    def __get_breakout_direction__(self):
        return FD.ASC if self.breakout_tick.Close > self.upper_limit else FD.DESC

    def __is_breakout_a_signal__(self):
        if self.direction == FD.ASC:
            if self.breakout_tick.Close > self.upper_limit + (self.weight * self.accuracy_pct):
                return True
        else:
            if self.breakout_tick.Close < self.lower_limit - (self.weight * self.accuracy_pct):
                return True
        return self.breakout_tick_predecessor.Volume/self.breakout_tick.Volume < 0.90  # i.e. 10% more volume required

    def __get_upper_bound__(self):
        return max(self.part_left.max, self.part_right.max)

    def __get_lower_bound__(self):
        return min(self.part_left.min, self.part_right.min)

    def is_formation_applicable(self):
        if self.are_left_right_parts_applicable_for_formation_type():
            return self.is_middle_part_applicable_for_formation_type()
        return False

    def are_left_right_parts_applicable_for_formation_type(self):
        if abs(self.part_left.max - self.part_right.max) / self.weight < self.accuracy_pct:
            if abs(self.part_left.min - self.part_right.min) / self.weight < self.accuracy_pct:
                return True
        return False

    def is_middle_part_applicable_for_formation_type(self):
        return self.part_middle.max < self.upper_limit and self.part_middle.min > self.lower_limit

    def is_tick_fitting_to_formation(self, tick_df: pd.DataFrame):
        row = tick_df.iloc[0]
        return row.Close < self.upper_limit and row.Close > self.lower_limit

    def set_xy_formation_parameter(self):
        x_dates = [self.date_first, self.date_first, self.date_last, self.date_last]
        x = list(dt.date2num(x_dates))
        y = [self.upper_limit, self.lower_limit, self.lower_limit, self.upper_limit]
        self.xy = list(zip(x, y))

    def set_xy_control_parameter(self):
        date_first = self.control_df.first_valid_index()
        date_last = self.control_df.last_valid_index()

        x_dates = [date_first, date_first, date_last, date_last]
        x = list(dt.date2num(x_dates))

        if self.direction == FD.ASC:
            y_max = self.upper_limit + (self.upper_limit - self.lower_limit)
            y_min = self.upper_limit
        else:  # breakout downwards
            y_max = self.lower_limit
            y_min = self.lower_limit - (self.upper_limit - self.lower_limit)
        y = [y_max, y_min, y_min, y_max]
        self.xy_control = list(zip(x,y))
        # xy_dates = list(zip(x_dates, y))
        # print(xy_dates)

    def get_shape(self):
        self.set_xy_formation_parameter()
        return Polygon(np.array(self.xy), True)

    def get_control_shape(self):
        self.set_xy_control_parameter()
        return Polygon(np.array(self.xy_control), True)


class FormationPart:
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
        plt.tight_layout()

        ohlc = []

        for ind, rows in self.df.iterrows():
            append_me = dt.date2num(ind), rows['Open'], rows['High'], rows['Low'], rows['Close']
            ohlc.append(append_me)

        candlestick_ohlc(axes[1], ohlc, width=0.4, colorup='g')

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
            # formation.print_formation_data()
            patches.append(formation.get_control_shape())

        colors = 100 * np.random.rand(len(patches))
        p = PatchCollection(patches, alpha=0.4)
        p.set_array(np.array(colors))
        ax.add_collection(p)
        detector.print_statistics(1000)
        # fig.colorbar(p, ax=ax)


dow_jones_dic = {"MMM": "3M", "AXP": "American", "AAPL": "Apple", "BA": "Boeing",
"CAT": "Caterpillar", "CVX": "Chevron", "CSCO": "Cisco", "KO": "Coca-Cola",
"DIS": "Disney", "DWDP": "DowDuPont", "XOM": "Exxon", "GE": "General",
"GS": "Goldman", "HD": "Home", "IBM": "IBM", "INTC": "Intel",
"JNJ": "Johnson", "JPM": "JPMorgan", "MCD": "McDonald's", "MRK": "Merck",
"MSFT": "Microsoft", "NKE": "Nike", "PFE": "Pfizer", "PG": "Procter",
"TRV": "Travelers", "UTX": "United", "UNH": "UnitedHealth", "VZ": "Verizon",
"V": "Visa", "WMT": "Wal-Mart"}

db = False
if db:
    stock_db = stock_database.StockDatabase()
    and_clause = "Date BETWEEN '2010-10-01' AND '2010-12-31'"
    # and_clause = ''
    stock_db_df_obj = stock_database.StockDatabaseDataFrame(stock_db, StockSymbols.Tesla, and_clause)
    plotter = FormationPlotter(stock_db_df_obj)
    plotter.plot_data_frame()
else:
    for ticker in dow_jones_dic:
        fetcher = AlphavantageStockFetcher(ticker)  # stock: MSFT, Crypto: BTC, AAPL, IBM, TSLA, ABB, FCEL
        plotter = FormationPlotter(fetcher)
        plotter.plot_data_frame()
    # fetcher = AlphavantageStockFetcher('FCEL', ApiPeriod.DAILY, ApiOutputsize.FULL)
    # plotter = FormationPlotter(fetcher)
    # plotter.plot_data_frame()





