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


class FormationDate:
    @staticmethod
    def get_date_from_datetime(date_time):
        return datetime.strptime(str(date_time), '%Y-%m-%d %H:%M:%S').date()


class TradeResult:
    def __init__(self):
        self.__bought_at = 0
        self.__sold_at = 0
        self.expected_win = 0
        self.actual_win = 0
        self.max_ticks = 0
        self.actual_ticks = 0
        self.stop_loss_at = 0
        self.stop_loss_reached = False
        self.formation_consistent = False

    def __get_bought_at(self):
        return round(self.__bought_at, 2)

    def __set_bought_at(self, value: float):
        self.__bought_at = value

    bought_at = property(__get_bought_at, __set_bought_at)

    def __get_sold_at(self):
        return round(self.__sold_at, 2)

    def __set_sold_at(self, value: float):
        self.__sold_at = value

    sold_at = property(__get_sold_at, __set_sold_at)

    def print(self):
        print('bought_at = {}, expected_win = {}, actual_win = {}, ticks: {}/{}, stop_loss = {} ({}), formation_ok: {}'
                .format(self.bought_at, self.expected_win, self.actual_win, self.actual_ticks, self.max_ticks,
                        self.stop_loss_at, self.stop_loss_reached, self.formation_consistent))


class FormationBreakoutApi:
    def __init__(self, formation_name: str):
        self.formation_name = formation_name
        self.df = None
        self.previous_tick = None
        self.upper_bound = 0
        self.lower_bound = 0
        self.mean = 0
        self.accuracy_range = 0


class FormationBreakout:
    def __init__(self, api: FormationBreakoutApi):
        self.formation_name = api.formation_name
        self.df = api.df
        self.date = self.df.first_valid_index()
        self.tick = self.df.iloc[0]
        self.previous_tick = api.previous_tick
        self.upper_bound = api.upper_bound
        self.lower_bound = api.lower_bound
        self.accuracy_range = api.accuracy_range
        self.breakout_direction = self.__get_breakout_direction__()
        self.is_breakout_a_signal = self.__is_breakout_a_signal__()

    def __get_breakout_direction__(self):
        return FD.ASC if self.tick.Close > self.upper_bound else FD.DESC

    def __is_breakout_a_signal__(self):
        is_breakout_over_limit = self.__is_breakout_over_limit__()
        is_volume_rizing = self.previous_tick.Volume/self.tick.Volume < 0.90 # i.e. 10% more volume required
        is_breakout_tick_sustainable = abs((self.tick.Open - self.tick.Close)/(self.tick.High - self.tick.Low)) > 0.8
        return (is_breakout_over_limit or is_volume_rizing) and is_breakout_tick_sustainable

    def __is_breakout_over_limit__(self):
        if self.breakout_direction == FD.ASC:
            return self.tick.Close > self.upper_bound + self.accuracy_range
        else:
            return self.tick.Close < self.lower_bound - self.accuracy_range

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

    @property
    def std(self):
        return self.df[CN.CLOSE].std()

    def add_tick(self, tick_df: pd.DataFrame):
        self.df = pd.concat([self.df, tick_df])

    def print_data(self, part: str):
        print('\n{}: min={}, max={}, mean={}, std={} \n{}'.format(part, self.min, self.max, self.mean, self.std,
                                                         self.df.head(self.ticks)))


class Formation:
    def __init__(self, df_start: pd.DataFrame, accuracy_pct: float):
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
        self.accurary_range = self.mean * self.accuracy_pct
        self.upper_limit = self.upper_bound + self.accurary_range
        self.lower_limit = self.lower_bound - self.accurary_range
        self.xy = None
        self.xy_control = None
        self.control_df = pd.DataFrame   # DataFrame to be checked for expected/real results after breakout
        self.date_first = None
        self.date_last = None
        self.breakout = FormationBreakout
        self.trade_result = TradeResult()

    @property
    def is_finished(self):
        return True if self.breakout.__class__.__name__ == 'FormationBreakout' else False

    @property
    def buy_at_breakout(self):
        if self.is_finished and self.is_passing_final_formation_check() and self.breakout.is_breakout_a_signal:
            return True
        return False

    @property
    def breakout_direction(self):
        if self.is_finished:
            return self.breakout.breakout_direction
        return FD.NONE

    @property
    def type(self):
        return FT.NONE

    @property
    def mean(self):
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

    def is_passing_final_formation_check(self):
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
        if self.control_df.__class__.__name__ == 'DataFrame':
            if self.buy_at_breakout:
                self.__fill_trade_result__()

    def print_formation_parts_data(self):
        self.part_left.print_data('Left')
        self.part_middle.print_data('Middle')
        self.part_right.print_data('Right')

    def print_formation_data(self):
        date_left = FormationDate.get_date_from_datetime(self.date_first)
        date_right = FormationDate.get_date_from_datetime(self.date_last)
        date_breakout = FormationDate.get_date_from_datetime(self.breakout.date)
        min_v = round(self.df_final[CN.LOW].min(), 2)
        max_v = round(self.df_final[CN.HIGH].max(), 2)
        std_v = round(self.df_final[CN.HIGH].std(), 2)
        std_rate = round(std_v/(self.upper_bound - self.lower_bound))
        result, expected, ticks, hit = self.get_trade_result()
        print('Total for {} -> {}: min = {}, max = {}, std = {}, std_rate = {},  breakout date = {}: '
              '\n---> {}: result = {} after {} ticks - expected: {}, bought at: {}, sold at: {}.'.
              format(date_left, date_right, min_v, max_v, std_v, std_rate, date_breakout,
                     hit, result, ticks, expected, self.trade_result.bought_at, self.trade_result.sold_at))

    def __fill_trade_result__(self):
        self.trade_result.expected_win = round(self.upper_bound - self.lower_bound, 2)
        self.trade_result.bought_at = round(self.get_buying_price(), 2)
        self.trade_result.max_ticks = self.control_df.shape[0]
        if self.breakout_direction == FD.ASC:
            self.trade_result.stop_loss_at = self.upper_bound - self.accurary_range
        else:
            self.trade_result.stop_loss_at = self.lower_bound + self.accurary_range
        self.trade_result.stop_loss_at = self.mean  # much more worse for TSLA....

        for ind, rows in self.control_df.iterrows():
            self.trade_result.actual_ticks += 1
            if self.breakout_direction == FD.ASC:
                self.trade_result.actual_win = round(rows.Close - self.trade_result.bought_at, 2)  # default
                if rows.Low < self.trade_result.stop_loss_at:
                    self.trade_result.stop_loss_reached = True
                    self.trade_result.sold_at = self.trade_result.stop_loss_at
                    self.trade_result.actual_win = round(self.trade_result.sold_at - self.trade_result.bought_at, 2)
                    break
                if rows.High > self.upper_limit + self.trade_result.expected_win:
                    self.trade_result.sold_at = self.upper_limit + self.trade_result.expected_win
                    self.trade_result.actual_win = round(self.trade_result.sold_at - self.trade_result.bought_at, 2)
                    self.trade_result.formation_consistent = True
                    break
            else:
                self.trade_result.actual_win = round(self.trade_result.bought_at - rows.Close, 2)  # default
                if rows.High > self.trade_result.stop_loss_at:
                    self.trade_result.stop_loss_reached = True
                    self.trade_result.sold_at = self.trade_result.stop_loss_at
                    self.trade_result.actual_win = round(self.trade_result.bought_at - self.trade_result.sold_at, 2)
                    break
                if rows.Low < self.lower_limit - self.trade_result.expected_win:
                    self.trade_result.sold_at = self.lower_limit - self.trade_result.expected_win
                    self.trade_result.actual_win = round(self.trade_result.bought_at - self.trade_result.sold_at, 2)
                    self.trade_result.formation_consistent = True
                    break

    def get_trade_result(self):
        return self.trade_result.actual_win, self.trade_result.expected_win, self.trade_result.actual_ticks\
            , self.trade_result.formation_consistent

    def get_buying_price(self):  # the breakout will be bought after the confirmation (close!!!)
        return self.breakout.df.iloc[0].Close


class Channel(Formation):
    @property
    def type(self):
        return FT.CHANNEL

    @property
    def mean(self):
        return (self.part_left.mean + self.part_right.mean) / 2

    @property
    def ticks(self):
        return self.part_left.ticks + self.part_middle.ticks + self.part_right.ticks

    def __get_upper_bound__(self):
        return max(self.part_left.max, self.part_right.max)

    def __get_lower_bound__(self):
        return min(self.part_left.min, self.part_right.min)

    def is_formation_applicable(self):
        if self.are_left_right_parts_applicable_for_formation_type():
            return self.is_middle_part_applicable_for_formation_type()
        return False

    def is_passing_final_formation_check(self):
        std_v = round(self.df_final[CN.HIGH].std(), 2)
        return std_v/(self.upper_bound - self.lower_bound) > 0.0  # this check doesn't bring the expected improvement

    def are_left_right_parts_applicable_for_formation_type(self):
        if abs(self.part_left.max - self.part_right.max) / self.mean < self.accuracy_pct:
            if abs(self.part_left.min - self.part_right.min) / self.mean < self.accuracy_pct:
                if abs(self.part_left.mean - self.part_right.mean) / self.mean < self.accuracy_pct:
                    return True
        return False

    def is_middle_part_applicable_for_formation_type(self):
        if self.part_middle.max < self.upper_limit and self.part_middle.min > self.lower_limit:
            if abs(self.part_middle.mean - self.mean) / self.mean < self.accuracy_pct:
                return True
        return False

    def is_tick_fitting_to_formation(self, tick_df: pd.DataFrame):
        row = tick_df.iloc[0]
        return row.Close < self.upper_bound and row.Close > self.lower_bound

    def set_xy_formation_parameter(self):
        x_dates = [self.date_first, self.date_first, self.date_last, self.date_last]
        x = list(dt.date2num(x_dates))
        y = [self.upper_bound, self.lower_bound, self.lower_bound, self.upper_bound]
        self.xy = list(zip(x, y))

    def set_xy_control_parameter(self):
        date_first = self.control_df.first_valid_index()
        date_last = self.control_df.last_valid_index()

        x_dates = [date_first, date_first, date_last, date_last]
        x = list(dt.date2num(x_dates))

        if self.breakout_direction == FD.ASC:
            y_max = self.upper_bound + (self.upper_bound - self.lower_bound)
            y_min = self.upper_bound
        else:  # breakout downwards
            y_max = self.lower_bound
            y_min = self.lower_bound - (self.upper_bound - self.lower_bound)
        y = [y_max, y_min, y_min, y_max]
        self.xy_control = list(zip(x,y))
        # xy_dates = list(zip(x_dates, y))
        # print(xy_dates)

    def get_shape(self):
        self.set_xy_formation_parameter()
        pol = Polygon(np.array(self.xy), True)
        # pol.set_color('#eeefff')
        return pol

    def get_control_shape(self):
        self.set_xy_control_parameter()
        pol = Polygon(np.array(self.xy_control), True)
        pol.set_color('#eeefff')
        return pol


class FormationDetectorStatisticsApi:
    def __init__(self, formation_dic, investment: float):
        self.formation_dic = formation_dic
        self.counter_actual_ticks = 0
        self.counter_ticks = 0
        self.counter_stop_loss = 0
        self.counter_formation_OK = 0
        self.counter_formation_NOK = 0
        self.investment_working = investment
        self.investment_start = investment
        self.__fill_parameter__()
        self.diff_pct = round(100 * (self.investment_working - self.investment_start) / self.investment_start, 2)

    def __fill_parameter__(self):
        for ind in self.formation_dic:
            formation = self.formation_dic[ind]
            if formation.is_finished:
                result = formation.trade_result
                self.counter_actual_ticks += result.actual_ticks
                self.counter_ticks += result.max_ticks
                self.counter_stop_loss = self.counter_stop_loss + 1 if result.stop_loss_reached else self.counter_stop_loss
                self.counter_formation_OK = self.counter_formation_OK + 1 if result.formation_consistent else self.counter_formation_OK
                self.counter_formation_NOK = self.counter_formation_NOK + 1 if not result.formation_consistent else self.counter_formation_NOK
                traded_entities = int(self.investment_working / result.bought_at)
                self.investment_working = round(self.investment_working + (traded_entities * result.actual_win), 2)


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
            formation = Channel(self.df.iloc[pos:pos + self.ticks], self.accuracy_pct)
            if formation.is_formation_applicable():
                pos_new_tick = pos + self.ticks + 1
                continue_loop = True
                while continue_loop and pos_new_tick <= self.df.shape[0]:
                    tick_df = self.df.iloc[pos_new_tick - 1:pos_new_tick]
                    continue_loop = formation.is_tick_fitting_to_formation(tick_df)
                    if continue_loop:
                        formation.add_tick_to_formation(tick_df)
                        pos_new_tick += 1
                    else:
                        formation.breakout = FormationBreakout(self.__get_breakout_api__(formation, tick_df))
                        left_boundary = pos_new_tick
                        if left_boundary < self.df.shape[0]:
                            right_boundary = min(left_boundary + formation.ticks, self.df.shape[0])
                            formation.control_df = self.df.iloc[left_boundary:right_boundary]
                formation.finalize()
                if formation.buy_at_breakout or not formation.is_finished:
                    self.formation_dic[pos] = formation
                pos += formation.ticks

    def __get_breakout_api__(self, formation: Formation, tick_df: pd.DataFrame):
        api = FormationBreakoutApi(formation.__class__.__name__)
        api.df = tick_df
        api.previous_tick = formation.part_right.df.loc[formation.part_right.df.last_valid_index()]
        api.upper_bound = formation.upper_bound
        api.lower_bound = formation.lower_bound
        api.accuracy_range = formation.accurary_range
        api.mean = formation.mean
        return api

    def print_statistics(self, investment: float):
        api = self.get_statistics_api(investment)
        print('Investment change: {} -> {}, Diff: {}%'.format(api.investment_start, api.investment_working, api.diff_pct))
        print('counter_stop_loss = {}, counter_formation_OK = {}, counter_formation_NOK = {}, ticks = {}'.format(
            api.counter_stop_loss, api.counter_formation_OK, api.counter_formation_NOK, api.counter_actual_ticks
        ))

    def get_statistics_api(self, investment: float):
        return FormationDetectorStatisticsApi(self.formation_dic, investment)


class FormationColorHandler:
    def get_colors_for_formation(self, formation: Formation):
        return self.__get_formation_color__(formation), self.__get_control_color__(formation)

    @staticmethod
    def __get_formation_color__(formation: Formation):
        if formation.is_finished:
            return 'green'
        else:
            return 'yellow'

    @staticmethod
    def __get_control_color__(formation: Formation):
        if formation.is_finished:
            if formation.trade_result.actual_win > 0:
                return 'lime'
            else:
                return 'orangered'
        else:
            return 'white'


class FormationPlotter:
    def __init__(self, api_object, ticks: int = 15, accuracy_pct: float = 0.02):
        self.api_object = api_object  # StockDatabaseDataFrame or AlphavantageStockFetcher
        self.api_object_class = self.api_object.__class__.__name__
        self.ticks = ticks
        self.accuracy_pct = accuracy_pct
        self.df = api_object.df
        self.df_data = api_object.df_data
        self.column_data = api_object.column_data
        self.df_volume = api_object.df_volume
        self.column_volume = api_object.column_volume
        self.symbol = api_object.symbol
        self.detector = FormationDetector

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
        self.add_formations(axes[1])

        self.df_volume.plot(ax=axes[2], title=self.column_volume)

        plt.xticks(rotation=45)
        plt.show()

    def add_formations(self, ax):
        self.detector = FormationDetector(self.df_data, self.ticks, self.accuracy_pct)  # the number should be a multiple of 3
        color_handler = FormationColorHandler()
        self.detector.parse_df()
        patches_dic = {}
        for ind in self.detector.formation_dic:
            formation = self.detector.formation_dic[ind]
            formation.print_formation_data()
            # formation.print_formation_parts_data()
            color_formation, color_control = color_handler.get_colors_for_formation(formation)
            if color_formation in patches_dic:
                patches_dic[color_formation].append(formation.get_shape())
            else:
                patches_dic[color_formation] = [formation.get_shape()]
            if formation.is_finished:
                if color_control in patches_dic:
                    patches_dic[color_control].append(formation.get_control_shape())
                else:
                    patches_dic[color_control] = [formation.get_control_shape()]

        for colors in patches_dic:
            p = PatchCollection(patches_dic[colors], alpha=0.4)
            p.set_color(colors)
            ax.add_collection(p)

        self.detector.print_statistics(1000)
        # fig.colorbar(p, ax=ax)


class DetectorStatistics:
    def __init__(self):
        self.list = []
        self.column_list = ['Ticker', 'Name', 'Investment', 'Result', 'Change%', 'SL', 'F_OK', 'F_NOK', 'Ticks']

    def add_entry(self, ticker, name, api: FormationDetectorStatisticsApi):
        new_entry = [ticker, name, api.investment_start, api.investment_working, api.diff_pct,
                     api.counter_stop_loss, api.counter_formation_OK, api.counter_formation_NOK, api.counter_actual_ticks]
        self.list.append(new_entry)

    def get_frame_set(self):
        df = pd.DataFrame(self.list)
        df.columns = self.column_list
        return df

    def print_overview(self):
        df = self.get_frame_set()
        print(df.head(df.shape[0]))

dow_jones_dic_orig = {"MMM": "3M", "AXP": "American", "AAPL": "Apple", "BA": "Boing",
"CAT": "Caterpillar", "CVX": "Chevron", "CSCO": "Cisco", "KO": "Coca-Cola",
"DIS": "Disney", "DWDP": "DowDuPont", "XOM": "Exxon", "GE": "General",
"GS": "Goldman", "HD": "Home", "IBM": "IBM", "INTC": "Intel",
"JNJ": "Johnson", "JPM": "JPMorgan", "MCD": "McDonald's", "MRK": "Merck",
"MSFT": "Microsoft", "NKE": "Nike", "PFE": "Pfizer", "PG": "Procter",
"TRV": "Travelers", "UTX": "United", "UNH": "UnitedHealth", "VZ": "Verizon",
"V": "Visa", "WMT": "Wal-Mart"}

dow_jones_dic = {"MMM": "3M", "AXP": "American", "AAPL": "Apple",
 "CVX": "Chevron", "CSCO": "Cisco", "KO": "Coca-Cola",
"DIS": "Disney", "DWDP": "DowDuPont", "XOM": "Exxon", "GE": "General",
"GS": "Goldman", "HD": "Home", "IBM": "IBM", "INTC": "Intel",
"JNJ": "Johnson", "JPM": "JPMorgan", "MCD": "McDonald's", "MRK": "Merck",
"MSFT": "Microsoft", "NKE": "Nike", "PFE": "Pfizer", "PG": "Procter", "TSLA": "Tesla",
"TRV": "Travelers", "UTX": "United", "UNH": "UnitedHealth", "VZ": "Verizon",
"V": "Visa", "WMT": "Wal-Mart"}

dow_jones_dic = {"XOM": "Exxon"}

db = True
plotting = True
formation_default_range = 15
accuracy_pct = 0.01
investment = 1000
show_statistics = True

if db:
    statistics = DetectorStatistics()
    stock_db = stock_database.StockDatabase()
    and_clause = "Date BETWEEN '2015-01-01' AND '2019-12-31'"
    and_clause = ''
    for ticker in dow_jones_dic:
        print('\nProcessing {} - {}'.format(ticker, dow_jones_dic[ticker]))
        stock_db_df_obj = stock_database.StockDatabaseDataFrame(stock_db, ticker, and_clause)
        if plotting:
            plotter = FormationPlotter(stock_db_df_obj, formation_default_range, accuracy_pct)
            plotter.plot_data_frame()
            if show_statistics:
                statistics.add_entry(ticker, dow_jones_dic[ticker], plotter.detector.get_statistics_api(investment))
        else:
            detector = FormationDetector(stock_db_df_obj.df_data, formation_default_range, accuracy_pct)  # the number should be a multiple of 3
            detector.parse_df()
            if show_statistics:
                statistics.add_entry(ticker, dow_jones_dic[ticker], detector.get_statistics_api(investment))
            else:
                detector.print_statistics(investment)
    if show_statistics:
        statistics.print_overview()
else:
    for ticker in dow_jones_dic:
        print('\nProcessing {} - {}'.format(ticker, dow_jones_dic[ticker]))
        fetcher = AlphavantageStockFetcher(ticker)  # stock: MSFT, Crypto: BTC, AAPL, IBM, TSLA, ABB, FCEL
        if plotting:
            plotter = FormationPlotter(fetcher)
            plotter.plot_data_frame()
        else:
            detector = FormationDetector(fetcher.df_data, formation_default_range)  # the number should be a multiple of 3
            detector.parse_df()
            detector.print_statistics(investment)
    # fetcher = AlphavantageStockFetcher('FCEL', ApiPeriod.DAILY, ApiOutputsize.FULL)
    # plotter = FormationPlotter(fetcher)
    # plotter.plot_data_frame()





