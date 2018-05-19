"""
Description: This module detects pattern from any kind of input stream.
In the first version we concentrate our target on identifying stock pattern by given formation types.
In the second version we allow the system to find own patterns or change existing pattern constraints.
The main algorithm is CSP (constraint satisfaction problems) with binary constraints.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
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
from matplotlib.patches import Circle, Wedge, Polygon, Rectangle, Arrow
from matplotlib.collections import PatchCollection
from datetime import datetime, timedelta
import ftplib
import tempfile
from sertl_analytics.datafetcher.database_fetcher import BaseDatabase, DatabaseDataFrame
from sertl_analytics.datafetcher.file_fetcher import NasdaqFtpFileFetcher
from sertl_analytics.pybase.df_base import PyBaseDataFrame
import stock_database as sdb
from sertl_analytics.searches.smart_searches import Queue, Stack
from sertl_analytics.functions import math_functions
import math
import itertools

"""
Implementation steps:
1. Define a framework for CSPs: Unary, Binary, Global, Preferences
2. The solver should be domain independent (i.e. it doesn't matter to check stock markets or health data...)
3. Node consistency, Arc-consistency, Path consistency.
Recall:
a) A constraint satisfaction problem consists of three components:
a.1) A set of variables X = {X1, X2, ..., Xn}
a.2) A set of domains for each variable: D = {D1, D2, ..., Dn)
a.3) A set of constraints C that specifies allowable combinations of values
b) Solving the CSP: Finding the assignment(s) that satisfy all constraints.
c) Concepts: problem formulation, backtracking search, arc consistence, etc
d) We call a solution a consistent assignment
e) Factored representation: Each state has some attribute-value properties, e.g. GPS location (properties = features)
"""


class FT:
    NONE = 'NONE'
    TRIANGLE = 'Triangle'
    TRIANGLE_TOP = 'Triangle_Top'
    TRIANGLE_BOTTOM = 'Triangle_Top'
    CHANNEL = 'Channel'  # https://www.investopedia.com/articles/trading/05/020905.asp
    CHANNEL_UP = 'Channel_Up'
    CHANNEL_DOWN = 'Channel_DOWN'
    TKE = 'Trend correction extrema'
    ALL = 'All'

class Indices:
    DOW_JONES = 'Dow Jones'
    NASDAQ = 'Nasdaq'
    MIXED = 'Mixed'
    ALL_DATABASE = 'All in database'


class FD:
    NONE = 'NONE'
    HOR = 'horizontal'
    ASC = 'ascending'
    DESC = 'descending'


class FCC:  # Formation Condition Columns
    BREAKOUT_WITH_BUY_SIGNAL = 'breakout had a buy signal'
    PREVIOUS_PERIOD_CHECK_OK = 'previous period check OK'  # eg. CN.LOW
    COMBINED_PARTS_APPLICABLE = 'combined parts are formation applicable'

class PatternConfiguration:
    def __init__(self):
        self.get_data_from_db = True
        self.pattern_type = FT.CHANNEL
        self.api_period = ApiPeriod.DAILY
        self.api_output_size = ApiOutputsize.COMPACT
        self.bound_upper_value = CN.HIGH
        self.bound_lower_value = CN.LOW
        self.plot_data = True
        self.check_previous_period = False   # default
        self.breakout_over_congestion_range = False
        self.accuracy_pct = 0.01  # the high/low values can be this percentage over the upper bounds w.r.t breadth
        self.breakout_range_pct = 0.01
        self.investment = 1000
        self.max_number_securities = 1000
        self.show_final_statistics = True
        self.and_clause = "Date BETWEEN '2017-12-01' AND '2019-12-31'"
        self.actual_list = []
        self.actual_position = 0
        self.actual_tick_position = 0
        self.actual_number = 0
        self.actual_ticker = ''
        self.actual_ticker_name = ''
        self.actual_and_clause = ''
        self.statistics_excel_file_name = ''
        self.ticker_dic = {}

    def __get_previous_period_length__(self):
        return self.__previous_period_length

    def __set_previous_period_length__(self, value: int):
        self.__previous_period_length = value

    previous_period_length = property(__get_previous_period_length__, __set_previous_period_length__)

    def print(self):
        source = 'DB' if self.get_data_from_db else 'Api'
        pattern_type = self.pattern_type
        and_clause = self.and_clause
        period = self.api_period
        output_size = self.api_output_size
        bound_upper_v = self.bound_upper_value
        bound_lower_v = self.bound_lower_value
        breakout_over_big_range = self.breakout_over_congestion_range
        accuracy_pct = self.accuracy_pct

        print('\nConfiguration settings:')
        if self.get_data_from_db:
            print('Formation: {} \nSource: {} \nAnd clause: {} \nUpper/Lower Bound Value: {}/{}'
                  ' \nBreakout big range: {}  \nAccuracy: {} \n'.format(
                    pattern_type, source, and_clause, bound_upper_v, bound_lower_v
                    , breakout_over_big_range, accuracy_pct))
        else:
            print('Formation: {} \nSource: {} \n\nApiPeriod/ApiOutput size: {}/{} \nUpper/Lower Bound Value: {}/{}'
                  ' \nBreakout big range: {}  \nAccuracy: {} \n'.format(
                    pattern_type, source, period, output_size, bound_upper_v, bound_lower_v
                    , breakout_over_big_range, accuracy_pct))

    def use_index(self, index: Indices):
        if index == Indices.DOW_JONES:
            self.ticker_dic = self.get_dow_jones_dic()
        elif index == Indices.NASDAQ:
            self.ticker_dic = self.get_nasdaq_dic()
        elif index == Indices.ALL_DATABASE:
            self.ticker_dic = self.get_all_in_database()
        else:
            self.ticker_dic = self.get_mixed_dic()

    def use_own_dic(self, dic: dict):
        self.ticker_dic = dic

    @staticmethod
    def get_dow_jones_dic():
        return {"MMM": "3M", "AXP": "American", "AAPL": "Apple", "BA": "Boing",
                "CAT": "Caterpillar", "CVX": "Chevron", "CSCO": "Cisco", "KO": "Coca-Cola",
                "DIS": "Disney", "DWDP": "DowDuPont", "XOM": "Exxon", "GE": "General",
                "GS": "Goldman", "HD": "Home", "IBM": "IBM", "INTC": "Intel",
                "JNJ": "Johnson", "JPM": "JPMorgan", "MCD": "McDonald's", "MRK": "Merck",
                "MSFT": "Microsoft", "NKE": "Nike", "PFE": "Pfizer", "PG": "Procter",
                "TRV": "Travelers", "UTX": "United", "UNH": "UnitedHealth", "VZ": "Verizon",
                "V": "Visa", "WMT": "Wal-Mart"}

    @staticmethod
    def get_nasdaq_dic():
        """
        Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares
        AABA|Altaba Inc. - Common Stock|Q|N|N|100|N|N
        """
        ftp_fetcher = NasdaqFtpFileFetcher()
        df = ftp_fetcher.get_data_frame()
        return PyBaseDataFrame.get_rows_as_dictionary(df, 'Symbol', ['Security Name'], {'Market Category': 'Q'})

    @staticmethod
    def get_mixed_dic():
        return {"TSLA": "Tesla", "FCEL": "Full Cell", "ONVO": "Organovo", "MRAM": "MRAM"}

    @staticmethod
    def get_all_in_database():
        stock_db = sdb.StockDatabase()
        db_data_frame = DatabaseDataFrame(stock_db, query='SELECT Symbol, count(*) FROM Stocks GROUP BY Symbol HAVING count(*) > 4000')
        return PyBaseDataFrame.get_rows_as_dictionary(db_data_frame, 'Symbol', ['Symbol'])


class FormationDate:
    @staticmethod
    def get_date_from_datetime(date_time):
        if date_time.__class__.__name__ == 'date':  # no change
            return date_time
        return datetime.strptime(str(date_time), '%Y-%m-%d %H:%M:%S').date()

    @staticmethod
    def get_date_from_number(num: int):
        return datetime(1, 1, 1) + timedelta(days=num)


class CN:  # Column Names
    OPEN = 'Open'
    HIGH = 'High'
    LOW = 'Low'
    CLOSE = 'Close'
    MEAN_HL = 'MeanHL'
    VOL = 'Volume'
    DATE = 'Date'
    DATEASNUM = 'DateAsNumber'
    POSITION = 'Position'
    TICKS_BREAK_HIGH_BEFORE = 'BREAK_HIGH_BEFORE'
    TICKS_BREAK_HIGH_AFTER = 'BREAK_HIGH_AFTER'
    TICKS_BREAK_LOW_BEFORE = 'BREAK_LOW_BEFORE'
    TICKS_BREAK_LOW_AFTER = 'BREAK_LOW_AFTER'
    GLOBAL_MIN = 'G_MIN'
    GLOBAL_MAX = 'G_MAX'
    LOCAL_MIN = 'L_MIN'
    LOCAL_MAX = 'L_MAX'
    F_UPPER = 'F_UPPER'
    F_LOWER = 'F_LOWER'
    IS_MIN = 'Is_MIN'
    IS_MAX = 'Is_MAX'


class ValueCategories:
    pass


class SVC(ValueCategories):  # Stock value categories:
    U_out = 'Upper_out'
    U_in = 'Upper_in'
    U_on = 'Upper_on'
    M_in = 'Middle_in'
    L_in = 'Low_in'
    L_on = 'Low_on'
    L_out = 'Low_out'
    NONE = 'NONE'


class CT:  # Constraint types
    ALL_IN = 'All_In'
    COUNT = 'Count'
    SERIES = 'Series'


class Candlestick:
    def __init__(self, open, high, low, close, volume = None, date = None):
        self.Open = open
        self.High = high
        self.Low = low
        self.Close = close
        self.Volume = volume
        self.Date = date

    @property
    def is_sustainable(self):
        return abs((self.Open - self.Close) / (self.High - self.Low)) > 0.6

    def is_volume_rising(self, candle_stick_comp, min_percentage: int):
        return self.Volume / candle_stick_comp.Volume > (100 + min_percentage)/100

    def has_gap_to(self, candle_stick_comp):
        return self.Low > candle_stick_comp.High or self.High < candle_stick_comp.Low


class TradeResult:
    def __init__(self):
        self.__bought_on = None
        self.__sold_on = None
        self.__bought_at = 0
        self.__sold_at = 0
        self.expected_win = 0
        self.actual_win = 0
        self.max_ticks = 0
        self.actual_ticks = 0
        self.stop_loss_at = 0
        self.limit = 0  # expected value for selling
        self.limit_extended_counter = 0
        self.stop_loss_reached = False
        self.formation_consistent = False

    def __get_bought_on__(self):
        return self.__bought_on

    def __set_bought_on__(self, value: datetime):
        self.__bought_on = value

    bought_on = property(__get_bought_on__, __set_bought_on__)

    def __get_sold_on__(self):
        return self.__sold_on

    def __set_sold_on__(self, value: datetime):
        self.__sold_on = value

    sold_on = property(__get_sold_on__, __set_sold_on__)

    def __get_bought_at__(self):
        return round(self.__bought_at, 2)

    def __set_bought_at__(self, value: float):
        self.__bought_at = value

    bought_at = property(__get_bought_at__, __set_bought_at__)

    def __get_sold_at__(self):
        return round(self.__sold_at, 2)

    def __set_sold_at__(self, value: float):
        self.__sold_at = value

    sold_at = property(__get_sold_at__, __set_sold_at__)

    def print(self):
        print('bought_at = {}, expected_win = {}, actual_win = {}, ticks: {}/{}, stop_loss = {} ({}), formation_ok: {}'
                .format(self.bought_at, self.expected_win, self.actual_win, self.actual_ticks, self.max_ticks,
                        self.stop_loss_at, self.stop_loss_reached, self.formation_consistent))


class FormationConditionHandler:
    def __init__(self):
        self.dic = {FCC.BREAKOUT_WITH_BUY_SIGNAL: False,
                    FCC.PREVIOUS_PERIOD_CHECK_OK: False,
                    FCC.COMBINED_PARTS_APPLICABLE: False}

    def __set_breakout_with_buy_signal__(self, value: bool):
        self.dic[FCC.BREAKOUT_WITH_BUY_SIGNAL] = value

    def __get_breakout_with_buy_signal__(self):
        return self.dic[FCC.BREAKOUT_WITH_BUY_SIGNAL]

    breakout_with_buy_signal = property(__get_breakout_with_buy_signal__, __set_breakout_with_buy_signal__)

    def __set_previous_period_check_ok__(self, value: bool):
        self.dic[FCC.PREVIOUS_PERIOD_CHECK_OK] = value

    def __get_previous_period_check_ok__(self):
        return self.dic[FCC.PREVIOUS_PERIOD_CHECK_OK]

    previous_period_check_ok = property(__get_previous_period_check_ok__, __set_previous_period_check_ok__)

    def __set_combined_parts_applicable__(self, value: bool):
        self.dic[FCC.COMBINED_PARTS_APPLICABLE] = value

    def __get_combined_parts_applicable__(self):
        return self.dic[FCC.COMBINED_PARTS_APPLICABLE]

    combined_parts_applicable = property(__get_combined_parts_applicable__, __set_combined_parts_applicable__)


class FormationBreakoutApi:
    def __init__(self, formation_name: str):
        self.formation_name = formation_name
        self.df = None
        self.previous_tick = None
        self.bound_upper = 0
        self.bound_lower = 0
        self.mean = 0
        self.accuracy_range = 0


class FormationBreakout:
    def __init__(self, api: FormationBreakoutApi, config: PatternConfiguration):
        self.config = config
        self.formation_name = api.formation_name
        self.df = api.df
        self.candle_stick = self.__get_candle_stick_from_df__()
        self.breakout_date = self.candle_stick.Date
        self.candle_stick_previous = Candlestick(api.previous_tick.Open, api.previous_tick.High
                                , api.previous_tick.Low, api.previous_tick.Close, api.previous_tick.Volume)
        self.volume_change_pct = round(self.candle_stick.Volume/self.candle_stick_previous.Volume, 2)
        self.bound_upper = api.bound_upper
        self.bound_lower = api.bound_lower
        self.accuracy_range = api.accuracy_range
        self.formation_breadth = abs(self.bound_upper - self.bound_lower)
        self.breakout_direction = self.__get_breakout_direction__()
        self.sign = 1 if self.breakout_direction == FD.ASC else -1
        self.limit_upper = self.bound_upper + self.accuracy_range
        self.limit_lower = self.bound_lower - self.accuracy_range

    def is_breakout_a_signal(self) -> bool:
        if self.__is_breakout_over_limit__():
            if True or self.__is_breakout_in_allowed_range__():
                if self.candle_stick.is_volume_rising(self.candle_stick_previous, 10): # i.e. 10% more volume required
                    if self.__is_breakout_powerfull__():
                        return True
        return False

    def __get_candle_stick_from_df__(self) -> Candlestick:
        date = self.df.first_valid_index()
        tick = self.df.iloc[0]
        return Candlestick(tick.Open, tick.High, tick.Low, tick.Close, tick.Volume, date)

    def __get_breakout_direction__(self) -> FD:
        return FD.ASC if self.candle_stick.Close > self.bound_upper else FD.DESC

    def __is_breakout_powerfull__(self) -> bool:
        return self.candle_stick.is_sustainable or self.candle_stick.has_gap_to(self.candle_stick_previous)

    def __is_breakout_over_limit__(self) -> bool:
        limit_range = self.formation_breadth if self.config.breakout_over_congestion_range \
            else self.formation_breadth * self.config.breakout_range_pct
        if self.breakout_direction == FD.ASC:
            return self.candle_stick.Close >= self.bound_upper + limit_range
        else:
            return self.candle_stick.Close <= self.bound_lower - limit_range

    def __is_breakout_in_allowed_range__(self) -> bool:
        if self.breakout_direction == FD.ASC:
            return self.candle_stick.Close < self.bound_upper + self.formation_breadth / 2
        else:
            return self.candle_stick.Close > self.bound_lower - self.formation_breadth / 2


class PatternPart:
    def __init__(self, df: pd.DataFrame, config: PatternConfiguration):
        self.df = df
        self.config = config
        self.__max_close = 0
        self.__id_max_close = None
        self.__max_high = 0
        self.__id_max_high = None
        self.__min_close = 0
        self.__min_low = 0
        self.__id_min_low = None
        self.__bound_upper = self.__max_high  # default
        self.__bound_lower = self.__min_low  # default
        if self.df.shape[0] > 0:
            self.__calculate_values__()

    def __calculate_values__(self):
        self.first_tick = self.df.iloc[0]
        self.__max_close = self.df[CN.CLOSE].max()
        self.__id_max_close = self.df[CN.CLOSE].idxmax(axis=0)
        self.__max_high = self.df[CN.HIGH].max()
        self.__id_max_high = self.df[CN.HIGH].idxmax(axis=0)
        self.__min_close = self.df[CN.CLOSE].min()
        self.__min_low = self.df[CN.LOW].min()
        self.__id_min_low = self.df[CN.LOW].idxmin(axis=0)
        self.__bound_upper = self.__max_high  # default
        self.__bound_lower = self.__min_low  # default
        self.__use_configuration_boundary_columns__()

    @property
    def movement(self):
        return abs(self.max_high - self.min_low)

    @property
    def date_first(self):
        return self.df.first_valid_index()

    @property
    def date_last(self):
        return self.df.last_valid_index()

    @property
    def ticks(self):
        return self.df.shape[0]

    @property
    def bound_upper(self):
        return self.__bound_upper

    @property
    def bound_lower(self):
        return self.__bound_lower

    @property
    def max_close(self):
        return self.__max_close

    @property
    def id_max_close_num(self):
        return dt.date2num(self.__id_max_close)

    @property
    def max_high(self):
        return self.__max_high

    @property
    def id_max_high(self):
        return self.__id_max_high

    @property
    def id_max_high_num(self):
        return dt.date2num(self.__id_max_high)

    @property
    def min_close(self):
        return self.__min_close

    @property
    def min_low(self):
        return self.__min_low

    @property
    def id_min_low(self):
        return self.__id_min_low

    @property
    def id_min_low_num(self):
        return dt.date2num(self.__id_min_low)

    @property
    def mean(self):
        return self.df[CN.MEAN_HL].mean()

    @property
    def std(self):  # we need the standard deviation from the mean_HL for Low and High
        return ((self.df[CN.HIGH]-self.mean).std() + (self.df[CN.LOW]-self.mean).std())/2

    def plot_annotation(self, ax, for_max: bool = True, color: str = 'blue'):
        x, y, text = self.__get_annotation_parameters__(for_max)
        offset_x = 0
        offset_y = (y/10)
        offset = [offset_x, offset_y] if for_max else [-offset_x, -offset_y]
        arrow_props = {'color': color, 'width': 0.2, 'headwidth': 4}
        ax.annotate(text, xy=(x, y), xytext=(x + offset[0], y + offset[1]), arrowprops=arrow_props)

    def __get_annotation_parameters__(self, for_max: bool):
        if for_max:
            x = self.id_max_high_num
            y = self.max_high
            date = FormationDate.get_date_from_datetime(self.id_max_high)
        else:
            x = self.id_min_low_num
            y = self.min_low
            date = FormationDate.get_date_from_datetime(self.id_min_low)
        return x, y, '{}: {}'.format(date, round(y, 2))

    def get_retracement_pct(self, comp_part):
        if self.min_low > comp_part.max_high:
            return 0
        intersection = abs(comp_part.max_high - self.min_low)
        return round(intersection/self.movement, 2)

    def __use_configuration_boundary_columns__(self):
        if self.config.bound_upper_value == CN.CLOSE:
            self.__bound_upper = self.__max_close
        if self.config.bound_lower_value == CN.CLOSE:
            self.__bound_lower = self.__min_close

    def are_values_below_linear_function(self, f_lin, accuracy_pct: float = 0.01, column: CN = CN.HIGH):  # 1% accuracy allowed
        for ind, rows in self.df.iterrows():
            value_function = round(f_lin(rows[CN.DATEASNUM]), 2)
            accuracy_range = value_function * accuracy_pct
            if value_function + accuracy_range < rows[column]:
                return False
        return True

    def is_high_close_to_linear_function(self, f_lin, accuracy_pct: float = 0.01):  # 1% accuracy allowed
        value_function = round(f_lin(self.id_max_high_num), 2)
        mean = (value_function + self.max_high)/2
        value = abs(self.max_high - value_function)/mean
        return value < accuracy_pct

    def is_close_close_to_linear_function(self, f_lin, accuracy_pct: float = 0.01):  # 1% accuracy allowed
        value_function = round(f_lin(self.id_max_close_num), 2)
        mean = (value_function + self.max_high)/2
        value = abs(self.max_close - value_function)/mean
        return value < accuracy_pct

    def get_cross_date_when_min_reached(self, f_lin):
        return self.__get_cross_date__(f_lin, 'min')

    def get_cross_date_when_curve_is_crossed(self, f_lin):
        return self.__get_cross_date__(f_lin, 'curve')

    def __get_cross_date__(self, f_lin, cross_type: str):
        for ind, rows in self.df.iterrows():
            if (cross_type == 'min' and f_lin(rows[CN.DATEASNUM]) < self.min_low) or \
                    (cross_type == 'curve' and rows[CN.CLOSE] > f_lin(rows[CN.DATEASNUM])):
                return rows[CN.DATE]
        return None

    def is_high_first_tick(self):
        return self.first_tick.High == self.max_high

    def is_high_before_low(self):
        return self.id_max_high_num < self.id_min_low_num

    def add_tick(self, tick_df: pd.DataFrame):
        self.df = pd.concat([self.df, tick_df])

    def recalculate_values(self):
        self.__calculate_values__()

    def print_data(self, part: str):
        print('\n{}: min={}, max={}, mean={}, std={} \n{}'.format(part, self.min_low, self.max_high, self.mean, self.std,
                                                                  self.df.head(self.ticks)))


class CountConstraint:
    def __init__(self, value_category: ValueCategories, comparison: str, value: float):
        self.value_category = value_category
        self.comparison = comparison
        self.comparison_value = value

    def is_value_satisfying_constraint(self, value: float):
        if self.comparison == '=':
            return value == self.comparison_value
        if self.comparison == '<=':
            return value <= self.comparison_value
        if self.comparison == '<':
            return value < self.comparison_value
        if self.comparison == '>=':
            return value >=  self.comparison_value
        if self.comparison == '>':
            return value > self.comparison_value


class Constraints:
    def __init__(self):
        self.global_all_in = []
        self.global_count = []
        self.global_series = []
        self.f_upper_slope_bounds = [-0.02, 0.02]
        self.f_lower_slope_bounds = [-0.02, 0.02]
        self.f_upper_lower_slope_bounds = [-5, 5]  # the relationship bounds for the linear functions increase
        # [0.8, 1.2] Channel,
        self.__fill_global_constraints__()
        self.min_ticks_required = self.__get_min_ticks_required__()
        self.max_ticks_required = self.__get_max_ticks_required__()
        self.min_max_ticks_required = self.min_ticks_required + self.max_ticks_required
        self.__set_bounds_for_(FT.ALL)

    def __set_bounds_for_(self, pattern_type: FT):
        if pattern_type == FT.CHANNEL:
            self.f_upper_slope_bounds = [-0.01, 0.01]
            self.f_lower_slope_bounds = self.f_upper_slope_bounds
            self.f_upper_lower_slope_bounds = [0.6, 1.4]
        elif pattern_type == FT.CHANNEL_UP:
            self.f_upper_slope_bounds = [0.02, 2]
            self.f_lower_slope_bounds = self.f_lower_slope_bounds
            self.f_upper_lower_slope_bounds = [0.8, 1.2]
        elif pattern_type == FT.CHANNEL_DOWN:
            self.f_upper_slope_bounds = [-0.02, -2]
            self.f_lower_slope_bounds = self.f_lower_slope_bounds
            self.f_upper_lower_slope_bounds = [0.8, 1.2]
        elif pattern_type == FT.TRIANGLE:
            self.f_upper_slope_bounds = [-1.0, -0.2]
            self.f_lower_slope_bounds = - self.f_lower_slope_bounds
            self.f_upper_lower_slope_bounds = [-0.8, -1.2]
        elif pattern_type == FT.TRIANGLE_TOP:
            self.f_upper_slope_bounds = [-0.02, 0.02]
            self.f_lower_slope_bounds = [-1.0, -0.2]
            self.f_upper_lower_slope_bounds = [-10, 10]
        elif pattern_type == FT.TRIANGLE_BOTTOM:
            self.f_upper_slope_bounds = [-1.0, -0.2]
            self.f_lower_slope_bounds = [-0.02, 0.02]
            self.f_upper_lower_slope_bounds = [-10, 10]
        elif pattern_type == FT.ALL:
            self.f_upper_slope_bounds = [-100.0, 100]
            self.f_lower_slope_bounds = self.f_upper_slope_bounds
            self.f_upper_lower_slope_bounds = [-100, 100]

    def get_unary_constraints(self, df: pd.DataFrame):
        pass

    def get_binary_constraints(self, df: pd.DataFrame):
        pass

    def __get_min_ticks_required__(self):
        pass

    def __get_max_ticks_required__(self):
        pass

    def __fill_global_constraints__(self):
        pass


class ChannelConstraints(Constraints):
    def __get_max_ticks_required__(self):
        return 3

    def __get_min_ticks_required__(self):
        return 2

    def __fill_global_constraints__(self):
        """
        1. All values have to be in a range (channel)
        2. There must be at least 3 variables with domain value = SPD.U_in (incl the ticks for the f_upper)
        3. There must be at least 3 variables with domain value = SPD.L_in (incl the ticks for the f_lower)
        """
        self.global_all_in = [SVC.L_on, SVC.L_in, SVC.M_in, SVC.U_in, SVC.U_on]
        self.global_count = ['AND', CountConstraint(SVC.U_in, '>=', 3), CountConstraint(SVC.L_in, '>=', 2)]
        self.global_series = ['OR', [SVC.L_in, SVC.U_in, SVC.L_in, SVC.U_in, SVC.L_in],
                          [SVC.U_in, SVC.L_in, SVC.U_in, SVC.L_in, SVC.U_in]]


class ToleranceCalculator:
    @staticmethod
    def are_values_in_tolerance_range(val_1: float, val_2: float, tolerance_pct: float):
        test = abs((val_1 - val_2)/np.mean([val_1, val_2]))
        return True if 0 == val_1 == val_2 else abs((val_1 - val_2)/np.mean([val_1, val_2])) < tolerance_pct

    @staticmethod
    def are_values_in_function_tolerance_range(x: list, y: list, f, tolerance_pct: float):
        for k in range(len(x)):
            y_k = y[k]
            f_k = f(x[k])
            if not ToleranceCalculator.are_values_in_tolerance_range(y_k, f_k, tolerance_pct):
                return False
        return True


class ValueCategorizer:
    def __init__(self, df: pd.DataFrame, accuracy_pct: float, f_upper, f_lower = None):
        self.df = df
        self.df_length = self.df.shape[0]
        self.value_category_dic = {}  # list of value categories by position of each entry
        self.__accuracy_ptc = accuracy_pct
        self.__accuracy_ptc_equal = 0.001
        self.__f_upper = f_upper
        self.__f_lower = f_lower
        self.__set_f_upper_f_lower_values()
        self.__calculate_value_categories__()

    def are_all_values_above_f_lower(self, with_accurary: bool = False) -> bool:
        tolerance = self.df[CN.LOW].mean() * self.__accuracy_ptc
        df_local = self.df[self.df[CN.LOW] < self.df[CN.F_LOWER] - tolerance]
        return df_local.shape[0] == 0

    def are_all_values_in_value_category(self, value_category: SVC) -> bool:
        return self.df_length == self.get_number_of_rows_with_value_category(value_category)

    def are_all_values_in_value_category_list(self, value_categories: list) -> bool:
        for key in self.value_category_dic:
            if not set(self.value_category_dic[key]).issubset(set(value_categories)):
                return False
        return True

    def get_number_of_rows_with_value_category(self, value_category: SVC) -> bool:
        counter = 0
        for key in self.value_category_dic:
            if value_category in self.value_category_dic[key]:
                counter += 1
        return counter

    def __set_f_upper_f_lower_values(self):
        self.df = self.df.assign(F_UPPER=(self.__f_upper(self.df[CN.POSITION])))
        self.df = self.df.assign(F_LOWER=(self.__f_lower(self.df[CN.POSITION])))

    def __calculate_value_categories__(self):
        position = 0
        for ind, row in self.df.iterrows():
            self.value_category_dic[position] = self.__get_value_categories_for_df_row__(row)
            position += 1

    def __get_value_categories_for_df_row__(self, row) -> list:
        pass

    def __is_row_value_in_f_upper_range__(self, row):
        return abs(row[CN.HIGH] - row[CN.F_UPPER])/np.mean([row[CN.HIGH], row[CN.F_UPPER]]) <= self.__accuracy_ptc

    def __is_row_value_in_f_lower_range__(self, row):
        return abs(row[CN.LOW] - row[CN.F_LOWER]) / np.mean([row[CN.LOW], row[CN.F_LOWER]]) <= self.__accuracy_ptc

    def __is_row_value_between_f_lower_f_upper__(self, row):
        return row[CN.F_LOWER] < row[CN.LOW] <= row[CN.HIGH] < row[CN.F_UPPER]

    def __is_row_value_equal_f_upper__(self, row):
        return abs(row[CN.HIGH] - row[CN.F_UPPER]) / np.mean([row[CN.HIGH], row[CN.F_UPPER]]) <= self.__accuracy_ptc_equal

    def __is_row_value_larger_f_upper__(self, row):
        return row[CN.HIGH] > row[CN.F_UPPER] and not self.__is_row_value_in_f_upper_range__(row)

    def __is_row_value_smaller_f_upper__(self, row):
        return row[CN.HIGH] < row[CN.F_UPPER]

    def __is_row_value_equal_f_lower__(self, row):
        return abs(row[CN.LOW] - row[CN.F_LOWER]) / np.mean([row[CN.LOW], row[CN.F_LOWER]]) <= self.__accuracy_ptc_equal

    def __is_row_value_larger_f_lower__(self, row):
        return row[CN.LOW] > row[CN.F_LOWER]

    def __is_row_value_smaller_f_lower__(self, row):
        return row[CN.LOW] < row[CN.F_LOWER] and not self.__is_row_value_in_f_lower_range__(row)


class ChannelValueCategorizer(ValueCategorizer):
    def __get_value_categories_for_df_row__(self, row):  # the series is important
        return_list = []
        if self.__is_row_value_equal_f_upper__(row):
            return_list.append(SVC.U_on)
        if self.__is_row_value_in_f_upper_range__(row):
            return_list.append(SVC.U_in)
        if self.__is_row_value_larger_f_upper__(row):
            return_list.append(SVC.U_out)
        if self.__is_row_value_equal_f_lower__(row):
            return_list.append(SVC.L_on)
        if self.__is_row_value_in_f_lower_range__(row):
            return_list.append(SVC.L_in)
        if self.__is_row_value_between_f_lower_f_upper__(row):
            return_list.append(SVC.M_in)
        if self.__is_row_value_smaller_f_lower__(row):
            return_list.append(SVC.L_out)
        return return_list


class Pattern:
    ticks_initial = 0
    check_length = 0

    def __init__(self, df_start: pd.DataFrame, f_upper, f_lower, config: PatternConfiguration):
        self.config = config
        self.df_start = df_start
        self.f_upper = f_upper
        self.f_lower = f_lower
        self.left_tick = WaveTick(self.df_start.iloc[0])
        self.right_tick = WaveTick(self.df_start.iloc[-1])
        self.condition_handler = FormationConditionHandler()
        self.ticks_initial = self.df_start.shape[0]
        self.accuracy_pct = self.config.accuracy_pct
        self.bound_upper = self.__get_upper_bound__()
        self.bound_lower = self.__get_lower_bound__()
        self.breadth = self.bound_upper - self.bound_lower
        self.accuracy_range = self.breadth * self.accuracy_pct
        self.limit_upper = self.bound_upper + self.accuracy_range
        self.limit_lower = self.bound_lower - self.accuracy_range
        self.xy = None
        self.xy_control = None
        self.control_df = pd.DataFrame   # DataFrame to be checked for expected/real results after breakout
        self.date_first = self.left_tick.date
        self.date_last = self.right_tick.date
        self.breakout = None
        self.trade_result = TradeResult()

    def was_breakout_done(self):
        return True if self.breakout.__class__.__name__ == 'FormationBreakout' else False

    def buy_after_breakout(self):
        if self.was_breakout_done() and self.breakout.is_breakout_a_signal():
            self.condition_handler.breakout_with_buy_signal = True
            return True
        return False

    def __get_slope_values__(self):
        f_upper_slope = round(self.f_upper(1) - self.f_upper(0), 4)
        f_lower_slope = round(self.f_lower(1) - self.f_lower(0), 4)
        relation_u_l = round(f_upper_slope/f_lower_slope, 4)
        return f_upper_slope, f_lower_slope, relation_u_l

    @property
    def breakout_direction(self):
        if self.was_breakout_done():
            return self.breakout.breakout_direction
        return FD.NONE

    @property
    def type(self):
        return FT.NONE  # is overwritten

    @property
    def mean(self):
        return 0

    @property
    def ticks(self):
        return self.df_start.shape[0]

    def __get_upper_bound__(self):
        return 0

    def __get_lower_bound__(self):
        return 0

    def is_formation_established(self):  # this is the main check whether a formation is ready for a breakout
        return True

    def add_annotations(self, ax):
        self.plot_annotation(ax, True, 'blue')

    def plot_annotation(self, ax, for_max: bool = True, color: str = 'blue'):
        x, y, text = self.__get_annotation_parameters__(for_max)
        offset_x = 0
        offset_y = (y / 50)
        offset = [offset_x, offset_y] if for_max else [-offset_x, -offset_y]
        arrow_props = {'color': color, 'width': 0.2, 'headwidth': 4}
        ax.annotate(text, xy=(x, y), xytext=(x + offset[0], y + offset[1]), arrowprops=arrow_props)

    def __get_annotation_parameters__(self, for_max: bool):
        if for_max:
            x = self.left_tick.date_num
            y = self.left_tick.high
        else:
            x = self.left_tick.date_num
            y = self.left_tick.low
        f_upper_slope, f_lower_slope, relation_u_l = self.__get_slope_values__()
        return x, y, 'U_S={} / L_S={}\nU_S/L_S={}'.format(f_upper_slope, f_lower_slope, relation_u_l )

    def set_xy_formation_parameter(self):
        x_dates = [self.date_first, self.date_first, self.date_last, self.date_last]
        x = list(dt.date2num(x_dates))
        x_pos = [self.left_tick.position, self.left_tick.position, self.right_tick.position, self.right_tick.position]
        y = [self.f_upper(x_pos[0]), self.f_lower(x_pos[1]), self.f_lower(x_pos[2]), self.f_upper(x_pos[3])]
        self.xy = list(zip(x, y))

    def set_xy_control_parameter(self):
        pass

    def get_shape(self):
        self.set_xy_formation_parameter()
        pol = Polygon(np.array(self.xy), True)
        return pol

    def get_control_shape(self):
        pass

    def fill_result_set(self):
        if self.is_control_df_available():
            self.__fill_trade_result__()

    def is_control_df_available(self):
        return self.control_df.__class__.__name__ == 'DataFrame'

    def __fill_trade_result__(self):
        self.trade_result.expected_win = round(self.bound_upper - self.bound_lower, 2)
        self.trade_result.bought_at = round(self.get_buying_price(), 2)
        self.trade_result.bought_on = self.breakout.df.first_valid_index()
        self.trade_result.max_ticks = self.control_df.shape[0]
        if self.breakout_direction == FD.ASC:
            self.trade_result.stop_loss_at = self.bound_upper - self.accuracy_range
            self.trade_result.limit = self.bound_upper + self.trade_result.expected_win
        else:
            self.trade_result.stop_loss_at = self.bound_lower + self.accuracy_range
            self.trade_result.limit = self.bound_lower - self.trade_result.expected_win
        # self.trade_result.stop_loss_at = self.mean  # much more worse for TSLA....

        for ind, rows in self.control_df.iterrows():
            self.trade_result.actual_ticks += 1
            cont = self.__fill_trade_results_for_breakout_direction__(ind, rows)
            if not cont:
                break

    def __fill_trade_results_for_breakout_direction__(self, date, row):
        sig = 1 if self.breakout_direction == FD.ASC else -1

        self.trade_result.sold_at = round(row.Close, 2)  # default
        self.trade_result.sold_on = date # default
        self.trade_result.actual_win = sig * round(row.Close - self.trade_result.bought_at, 2)  # default

        if (self.breakout_direction == FD.ASC and row.Low < self.trade_result.stop_loss_at) \
                or (self.breakout_direction == FD.DESC and row.High > self.trade_result.stop_loss_at):
            self.trade_result.stop_loss_reached = True
            if self.breakout_direction == FD.ASC:
                self.trade_result.sold_at = min(row.Open, self.trade_result.stop_loss_at)
            else:
                self.trade_result.sold_at = max(row.Open, self.trade_result.stop_loss_at)
            self.trade_result.actual_win = sig * round(self.trade_result.sold_at - self.trade_result.bought_at, 2)
            return False

        if (self.breakout_direction == FD.ASC and row.High > self.trade_result.limit) \
                or (self.breakout_direction == FD.DESC and row.Low < self.trade_result.limit):
            if self.__is_row_trigger_for_extension__(row):  # extend the limit (let the win run)
                self.trade_result.stop_loss_at += sig * self.trade_result.expected_win
                self.trade_result.limit += sig * self.trade_result.expected_win
                self.trade_result.limit_extended_counter += 1
                self.trade_result.formation_consistent = True
            else:
                self.trade_result.sold_at = row.Close
                self.trade_result.actual_win = sig * round(self.trade_result.sold_at - self.trade_result.bought_at, 2)
                self.trade_result.formation_consistent = True
                return False
        return True

    def __is_row_trigger_for_extension__(self, row):
        threshold = 0.005
        if self.breakout_direction == FD.ASC:
            return row.Close > self.trade_result.limit or (row.Close - row.High)/row.Close < threshold
        else:
            return row.Close < self.trade_result.limit or (row.Close - row.Low)/row.Close < threshold

    def get_buying_price(self):  # the breakout will be bought after the confirmation (close!!!)
        return self.breakout.df.iloc[0].Close


class WaveTick:
    def __init__(self, tick):
        self.tick = tick

    @property
    def date(self):
        return self.tick[CN.DATE]

    @property
    def date_num(self):
        return self.tick[CN.DATEASNUM]

    @property
    def date_str(self):
        return self.tick[CN.DATE].strftime("%Y-%m-%d")

    @property
    def position(self):
        return self.tick[CN.POSITION]

    @property
    def is_max(self):
        return self.tick[CN.IS_MAX]

    @property
    def is_min(self):
        return self.tick[CN.IS_MIN]

    @property
    def is_local_max(self):
        return self.tick[CN.LOCAL_MAX]

    @property
    def is_local_min(self):
        return self.tick[CN.LOCAL_MIN]

    @property
    def high(self):
        return self.tick[CN.HIGH]

    @property
    def low(self):
        return self.tick[CN.LOW]

    def print(self):
        print('Pos: {}, Date: {}, High: {}, Low: {}'.format(self.position, self.date, self.high, self.low))

    def get_linear_f_params_for_max(self, tick):
        return math_functions.get_function_parameters(self.position, self.high, tick.position, tick.high)

    def get_linear_f_params_for_min(self, tick):
        return math_functions.get_function_parameters(self.position, self.low, tick.position, tick.low)


class PatternRange:
    def __init__(self, df_min_max: pd.DataFrame, tick: WaveTick, min_length: int):
        self.df_min_max = df_min_max
        self.tick_list = []
        self.tick_breakout_predecessor = None
        self.tick_breakout_successor = None
        self.last_added_position = 0
        self.last_added_value = 0
        self.__min_length = min_length
        self.__f_param = None
        self.__position_list = []
        self.__value_list = []
        self.__date_list = []
        self.add_tick(tick, None)

    @property
    def length(self) -> int:
        return len(self.tick_list)

    @property
    def position_list(self):
        return self.__position_list

    def add_tick(self, tick: WaveTick, f_param):
        self.tick_list.append(tick)
        self.__f_param = f_param
        self.last_added_position = tick.position
        self.last_added_value = self.__get_value__(tick)
        self.__position_list.append(tick.position)
        self.__value_list.append(self.__get_value__(tick))
        self.__date_list.append(tick.date_str)

    @property
    def is_min_length_reached(self) -> bool:
        return self.length >= self.__min_length

    def is_covering_all_positions(self, pos_list_input: list) -> bool:
        return len(set(pos_list_input) & set(self.__position_list)) == len(pos_list_input)

    def get_range_details(self):
        breakout_predecessor = self.__get_breakout_details__(self.tick_breakout_predecessor, False)
        breakout_successor = self.__get_breakout_details__(self.tick_breakout_successor, True)
        return [self.__position_list, self.__value_list, breakout_predecessor, breakout_successor, self.__date_list]

    def are_values_in_function_tolerance_range(self, f_param, accuracy_pct) -> bool:
        for ticks in self.tick_list:
            v_1 = self.__get_value__(ticks)
            v_2 = f_param(ticks.position)
            if not ToleranceCalculator.are_values_in_tolerance_range(v_1, v_2, accuracy_pct):
                return False
        return True

    def __get_breakout_details__(self, tick: WaveTick, is_breakout_successor: bool):
        if tick is None:  # extend the breakouts until the end....
            if is_breakout_successor:
                pos = self.df_min_max.iloc[-1][CN.POSITION]
            else:
                pos = self.df_min_max.iloc[0][CN.POSITION]
            return [pos, round(self.__f_param(pos), 2)]
        else:
            return [tick.position, round(self.__f_param(tick.position), 2)]

    @staticmethod
    def __get_value__(tick: WaveTick):
        return tick.high


class PatternRangeMax(PatternRange):
    @staticmethod
    def __get_value__(tick: WaveTick):
        return tick.high


class PatternRangeMin(PatternRange):
    @staticmethod
    def __get_value__(tick: WaveTick):
        return tick.low


class PatternRangeDetector:
    def __init__(self, df_min_max: pd.DataFrame, accuracy_pct: float = 0.01, ticks_required: int = 3):
        self.df = self.__get_df_for_processing__(df_min_max)
        self.df_length = self.df.shape[0]
        self._number_required_ticks = ticks_required
        self._pattern_range = None
        self.__accuracy_pct = accuracy_pct
        self.__pattern_range_list = []
        self.__parse_data_frame__()

    def __get_df_for_processing__(self, df_min_max: pd.DataFrame):
        pass

    def __get_pattern_range__(self):
        return self._pattern_range

    def __set_pattern_range__(self, value: PatternRange):
        self.__add_pattern_range_to_list_after_check__()
        self._pattern_range = value

    def __add_pattern_range_to_list_after_check__(self):
        if self.__are_conditions_fulfilled_for_adding_to_pattern_range_list__():
            self.__pattern_range_list.append(self._pattern_range)

    def __are_conditions_fulfilled_for_adding_to_pattern_range_list__(self) -> bool:
        if self._pattern_range is None:
            return False
        if not self._pattern_range.is_min_length_reached:
            return False
        for pattern in self.__pattern_range_list:  # check if this list is already a sublist of an earlier list
            if pattern.is_covering_all_positions(self._pattern_range.position_list):
                return False
        return True

    def get_list_of_possible_pattern_ranges(self):
        return [pattern.get_range_details() for pattern in self.__pattern_range_list]

    def print_list_of_possible_pattern_ranges(self):
        for pattern in self.__pattern_range_list:
            print(pattern.get_range_details())

    def __parse_data_frame__(self):
        for i in range(0, self.df_length - self._number_required_ticks):
            tick_i = WaveTick(self.df.iloc[i])
            self.__init_pattern_range_by_tick__(tick_i)
            for k in range(i+1, self.df_length):
                tick_k = WaveTick(self.df.iloc[k])
                if self._pattern_range.length == 1:  # start a new one if the values is above/below the old function
                    self._pattern_range.add_tick(tick_k, None)
                elif self.__is_end_for_single_check_reached__(tick_i, tick_k):
                    self.__init_pattern_range_by_tick__(tick_i)
                    self._pattern_range.add_tick(tick_k, None)
        self.__add_pattern_range_to_list_after_check__()  # for the latest...

    def __get_linear_f_params__(self, tick_i: WaveTick, tick_k: WaveTick):
        pass

    def __is_end_for_single_check_reached__(self, tick_i: WaveTick, tick_k: WaveTick):
        f_param_new = self.__get_linear_f_params__(tick_i, tick_k)
        if self._pattern_range.are_values_in_function_tolerance_range(f_param_new, self.__accuracy_pct):
            self._pattern_range.add_tick(tick_k, f_param_new)
        else:
            f_value_new_last_position_right = f_param_new(self._pattern_range.last_added_position)
            if self.__is_new_tick_a_breakout__(f_value_new_last_position_right):
                return True
        return False

    def __is_new_tick_a_breakout__(self, f_value_new_last_position_right: float):
        pass

    def __init_pattern_range_by_tick__(self, tick: WaveTick):
        pass


class PatternRangeDetectorMax(PatternRangeDetector):
    def __get_df_for_processing__(self, df_min_max: pd.DataFrame):
        return df_min_max[df_min_max[CN.IS_MAX]]

    def __get_linear_f_params__(self, tick_i: WaveTick, tick_k: WaveTick):
        return tick_i.get_linear_f_params_for_max(tick_k)

    def __is_new_tick_a_breakout__(self, f_value_new_last_position_right: float):
        return self._pattern_range.last_added_value < f_value_new_last_position_right

    def __init_pattern_range_by_tick__(self, tick: WaveTick):
        self.__set_pattern_range__(PatternRangeMax(self.df, tick, self._number_required_ticks))


class PatternRangeDetectorMin(PatternRangeDetector):
    def __get_df_for_processing__(self, df_min_max: pd.DataFrame):
        return df_min_max[df_min_max[CN.IS_MIN]]

    def __get_linear_f_params__(self, tick_i: WaveTick, tick_k: WaveTick):
        return tick_i.get_linear_f_params_for_min(tick_k)

    def __is_new_tick_a_breakout__(self, f_value_new_last_position_right: float):
        return self._pattern_range.last_added_value > f_value_new_last_position_right

    def __init_pattern_range_by_tick__(self, tick: WaveTick):
        self.__set_pattern_range__(PatternRangeMin(self.df, tick, self._number_required_ticks))


class DataFrameFactory:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df_length = self.df.shape[0]
        self.__add_columns__()
        self.df.reset_index(drop=True, inplace=True)  # get position index

    def __add_columns__(self):
        pass


class DataFramePatternFactory(DataFrameFactory):
    """
    This class has two purposes:
    1. Identify all extrema: global and local maxima and minima which is used as checkpoint for pattern detections.
    2. Identify ranges which can be used for a thorough inspection in the further process
    """
    def __init__(self, df: pd.DataFrame):
        DataFrameFactory.__init__(self, df)
        self.__length_for_global = int(self.df_length / 2)
        self.__length_for_local = 3
        self.__init_columns_for_ticks_distance__()
        self.df_min_max = self.df[np.logical_or(self.df[CN.IS_MIN], self.df[CN.IS_MAX])]

    def __add_columns__(self):
        self.df = self.df.assign(MeanHL=round((self.df.High + self.df.Low) / 2, 2))
        self.df = self.df.assign(Date=self.df.index.map(FormationDate.get_date_from_datetime))
        self.df = self.df.assign(DateAsNumber=self.df.index.map(dt.date2num))
        self.df[CN.DATEASNUM] = self.df[CN.DATEASNUM].apply(int)
        self.df = self.df.assign(Position=self.df.index.map(self.df.index.get_loc))
        self.df[CN.POSITION] = self.df[CN.POSITION].apply(int)

    def __init_columns_for_ticks_distance__(self):
        self.__add_distance_columns__()
        self.__add_min_max_columns__()

    def __add_distance_columns__(self):
        for pos, high, before in itertools.product(range(0, self.df_length), (False, True), (False, True)):
            value = self.__get_distance__(pos, high, before)
            if high and before:
                self.df.loc[pos, CN.TICKS_BREAK_HIGH_BEFORE] = value
            elif high and not before:
                self.df.loc[pos, CN.TICKS_BREAK_HIGH_AFTER] = value
            elif not high and before:
                self.df.loc[pos, CN.TICKS_BREAK_LOW_BEFORE] = value
            elif not high and not before:
                self.df.loc[pos, CN.TICKS_BREAK_LOW_AFTER] = value

    def __add_min_max_columns__(self):
        self.df[CN.GLOBAL_MIN] = np.logical_and(self.df[CN.TICKS_BREAK_LOW_AFTER] > self.__length_for_global
                                                , self.df[CN.TICKS_BREAK_LOW_BEFORE] > self.__length_for_global)
        self.df[CN.GLOBAL_MAX] = np.logical_and(self.df[CN.TICKS_BREAK_HIGH_AFTER] > self.__length_for_global
                                                , self.df[CN.TICKS_BREAK_HIGH_BEFORE] > self.__length_for_global)
        self.df[CN.LOCAL_MIN] = np.logical_and(self.df[CN.TICKS_BREAK_LOW_AFTER] > self.__length_for_local
                                               , self.df[CN.TICKS_BREAK_LOW_BEFORE] > self.__length_for_local)
        self.df[CN.LOCAL_MAX] = np.logical_and(self.df[CN.TICKS_BREAK_HIGH_AFTER] > self.__length_for_local
                                               , self.df[CN.TICKS_BREAK_HIGH_BEFORE] > self.__length_for_local)
        self.df[CN.IS_MIN] = np.logical_or(self.df[CN.GLOBAL_MIN], self.df[CN.LOCAL_MIN])
        self.df[CN.IS_MAX] = np.logical_or(self.df[CN.GLOBAL_MAX], self.df[CN.LOCAL_MAX])

    def __get_distance__(self, row_pos: int, for_high: bool, for_before: bool) -> int:
        signature = -1 if for_before else 1
        pos_compare = row_pos + signature
        actual_value_pair = self.__get_value_pair_for_comparison__(self.df.iloc[row_pos], for_high)
        while 0 <= pos_compare < self.df_length:
            if self.__is_new_value_a_break__(actual_value_pair, pos_compare, for_high):
                break
            pos_compare += signature
        return self.df_length + 1 if (pos_compare < 0 or pos_compare >= self.df_length) else abs(row_pos - pos_compare)

    def __is_new_value_a_break__(self, actual_value_pair: list, pos_compare: int, for_high: bool) -> bool:
        """
        We need a separate script for handling when values are different to avoid min/max neighbors with the same value
        The idea behind this algorithm is that the extrema is mostly not the longest tick.
        """
        value_pair_compare = self.__get_value_pair_for_comparison__(self.df.iloc[pos_compare], for_high)
        if for_high:
            if value_pair_compare[0] > actual_value_pair[0]:
                return True
            if value_pair_compare[0] == actual_value_pair[0]:
                return value_pair_compare[1] > actual_value_pair[1]  # break if the compare has a greater low value
        else:
            if value_pair_compare[0] < actual_value_pair[0]:
                return True
            if value_pair_compare[0] == actual_value_pair[0]:
                return value_pair_compare[1] < actual_value_pair[1]  # break if the compare has a smaller high value
        return False

    def __get_value_pair_for_comparison__(self, row, for_high: bool) -> list:
        value_first = row[CN.HIGH] if for_high else row[CN.LOW]
        value_second = row[CN.LOW] if for_high else row[CN.HIGH]
        return [value_first, value_second]


class PatternDetector:
    def __init__(self, df: pd.DataFrame, df_min_max: pd.DataFrame, config: PatternConfiguration):
        self.config = config
        self.pattern_list = []
        self.df = df
        self.df_length = self.df.shape[0]
        self.df_min_max = df_min_max
        self.df_min_max_length = self.df_min_max.shape[0]
        self.accuracy_pct = self.config.accuracy_pct
        self.pattern_check_list = ['Channel']
        self.constraints = None
        self.__possible_pattern_ranges_top = []  # format [0] = list of positions, [1] pos, value of pre, [2] for post
        self.__possible_pattern_ranges_bottom = []  # we above
        self.__possible_pattern_ranges = []

    @property
    def possible_pattern_ranges_available(self):
        return len(self.__possible_pattern_ranges_top) + len(self.__possible_pattern_ranges_bottom) > 0

    def parse_for_pattern(self):
        """
        We parse only over the actual known min-max-dataframe
        """
        for patterns in self.pattern_check_list:
            if patterns == 'Channel':
                self.constraints = ChannelConstraints()
            self.__fill_possible_pattern_ranges__()
            for range_lists in self.__possible_pattern_ranges:
                df_check = self.df_min_max.loc[range_lists[0]:range_lists[-1]]
                is_check_ok, f_upper, f_lower = self.check_tick_range(df_check)
                if is_check_ok:
                    self.pattern_list.append(Pattern(df_check, f_upper, f_lower, self.config))

    def check_tick_range(self, df_check: pd.DataFrame) -> bool:
        df_min = df_check[df_check[CN.IS_MIN]]
        df_max = df_check[df_check[CN.IS_MAX]]
        l_tick = WaveTick(df_max.iloc[0])
        r_tick =  WaveTick(df_max.iloc[-1])
        f_upper = math_functions.get_function_parameters(l_tick.position, l_tick.high, r_tick.position, r_tick.high)
        f_lower_list = self.__get_valid_f_lower_function_parameters__(df_min, f_upper)
        for f_lower in f_lower_list:
            value_categorizer = ChannelValueCategorizer(df_check, self.accuracy_pct, f_upper, f_lower)
            if self.__is_global_constraint_all_in_satisfied__(df_check, value_categorizer):
                if self.__is_global_constraint_count_satisfied__(value_categorizer):
                    if self.__is_global_constraint_series_satisfied__(df_check, value_categorizer):
                        return True, f_upper, f_lower
        return False, None, None

    def get_shapes_for_possible_pattern_ranges_top(self):
        return self.__get_shapes_for_possible_pattern_ranges__(True)

    def get_shapes_for_possible_pattern_ranges_bottom(self):
        return self.__get_shapes_for_possible_pattern_ranges__(False)

    def __get_shapes_for_possible_pattern_ranges__(self, for_top: bool):
        loop_list = self.__possible_pattern_ranges_top if for_top else self.__possible_pattern_ranges_bottom
        shape_list = []
        for entries in loop_list:
            pos_list = entries[0]
            value_list = entries[1]
            # predecessor_list = entries[2]
            successor_list = entries[3]
            x = [self.df_min_max.loc[pos_list[0]][CN.DATEASNUM], self.df_min_max.loc[successor_list[0]][CN.DATEASNUM]]
            y = [value_list[0], successor_list[1]]
            xy = list(zip(x, y))
            pol = Polygon(np.array(xy), True)
            shape_list.append(pol)
        return shape_list

    def __fill_possible_pattern_ranges__(self):
        range_detector_max = PatternRangeDetectorMax(self.df_min_max, self.config.accuracy_pct, 3)
        self.__possible_pattern_ranges_top = range_detector_max.get_list_of_possible_pattern_ranges()
        # range_detector_max.print_list_of_possible_pattern_ranges()
        range_detector_min = PatternRangeDetectorMin(self.df_min_max, self.config.accuracy_pct, 3)
        self.__possible_pattern_ranges_bottom = range_detector_min.get_list_of_possible_pattern_ranges()
        # range_detector_min.print_list_of_possible_pattern_ranges()
        self.__combine_possible_pattern_ranges__()
        # TODO get rid of print statements

    def __combine_possible_pattern_ranges__(self):
        for entry_top in self.__possible_pattern_ranges_top:
            self.__possible_pattern_ranges.append(entry_top[0])

    def __combine_possible_pattern_ranges_old__(self):
        for entry_top in self.__possible_pattern_ranges_top:
            for entry_bottom in self.__possible_pattern_ranges_bottom:
                range_top = range(entry_top[0][0], entry_top[0][-1])
                range_bottom = range(entry_bottom[0][0], entry_bottom[0][-1])
                range_top_len = len(range_top)
                range_bottom_len = len(range_bottom)
                min_len_ranges = min(range_top_len, range_bottom_len)
                if np.mean([range_top_len, range_bottom_len]) < 1.5 * min_len_ranges:
                    range_intersection = set(range_top).intersection(range_bottom)
                    if len(range_intersection) > min_len_ranges/1.5:
                        union_set = set(entry_top[0]).union(entry_bottom[0])
                        self.__possible_pattern_ranges.append(sorted(list(union_set)))

    def __get_valid_f_lower_function_parameters__(self, df_min: pd.DataFrame, f_upper) -> list:
        parameter_list = []
        if df_min.shape[0] < 2:
            return parameter_list

        for i in range(0, df_min.shape[0] - 1):
            for m in range(i + 1, df_min.shape[0]):
                left_tick = WaveTick(df_min.iloc[i])
                right_tick = WaveTick(df_min.iloc[m])
                f_lower = math_functions.get_function_parameters(left_tick.position, left_tick.low
                                                                 , right_tick.position, right_tick.low)
                if self.__is_f_lower_according_to_f_upper_lower_bounds_constraint__(f_upper, f_lower):
                    value_categorizer = ChannelValueCategorizer(df_min, self.accuracy_pct, f_upper, f_lower)
                    if value_categorizer.are_all_values_above_f_lower():
                        parameter_list.append(f_lower)
        return parameter_list

    def __is_f_lower_according_to_f_upper_lower_bounds_constraint__(self, f_upper, f_lower):
        f_upper_slope = round(f_upper(1) - f_upper(0), 4)
        if not self.constraints.f_upper_slope_bounds[0] <= f_upper_slope <= self.constraints.f_upper_slope_bounds[1]:
            return False

        f_lower_slope = round(f_lower(1) - f_lower(0), 4)
        if not self.constraints.f_lower_slope_bounds[0] <= f_lower_slope <= self.constraints.f_lower_slope_bounds[1]:
            return False

        if f_lower_slope == 0:
            return True  # TODO handle f_lower_slope == 0, i.e. parallel to x-axis...
        relation_u_l = round(f_upper_slope/f_lower_slope, 4)

        # print('f_upper = {}, f_lower = {}, relation_u_l = {}'.format(f_upper, f_lower, relation_u_l))

        return self.constraints.f_upper_lower_slope_bounds[0] <= relation_u_l <= self.constraints.f_upper_lower_slope_bounds[1]

    def __is_global_constraint_all_in_satisfied__(self, df_check: pd.DataFrame, value_categorizer):
        if len(self.constraints.global_all_in) == 0:
            return True
        return value_categorizer.are_all_values_in_value_category_list(self.constraints.global_all_in)

    def __is_global_constraint_count_satisfied__(self, value_categorizer: ValueCategorizer):
        if len(self.constraints.global_count) == 0:
            return True
        conjunction = self.constraints.global_count[0]
        for k in range(1, len(self.constraints.global_count)):
            count_constraint = self.constraints.global_count[k]
            number = value_categorizer.get_number_of_rows_with_value_category(count_constraint.value_category)
            bool_value = count_constraint.is_value_satisfying_constraint(number)
            if bool_value and conjunction == 'OR':
                return True
            elif not bool_value and conjunction == 'AND':
                return False
        return False if conjunction == 'OR' else True

    def __is_global_constraint_series_satisfied__(self, df_check: pd.DataFrame, value_categorizer):
        if len(self.constraints.global_series) == 0:
            return True
        conjunction = self.constraints.global_series[0]
        for k in range(1, len(self.constraints.global_series)):
            series = self.constraints.global_series[k]
            check_ok = self.__is_series_constraint_check_done__(series, df_check, 0, value_categorizer)
            if check_ok and conjunction == 'OR':
                return True
            elif not check_ok and conjunction == 'AND':
                return False
        return False if conjunction == 'OR' else True

    def __is_series_constraint_check_done__(self, series: list, df_check, position: int, value_categorizer):
        if len(series) == 0:
            return True
        if position == df_check.shape[0]:
            return False
        if series[0] in value_categorizer.value_category_dic[position]:
            series = series[1:]
        return self.__is_series_constraint_check_done__(series, df_check, position + 1, value_categorizer)

    def print_statistics(self):
        api = self.get_statistics_api()
        print(
            'Investment change: {} -> {}, Diff: {}%'.format(api.investment_start, api.investment_working, api.diff_pct))
        print('counter_stop_loss = {}, counter_formation_OK = {}, counter_formation_NOK = {}, ticks = {}'.format(
            api.counter_stop_loss, api.counter_formation_OK, api.counter_formation_NOK, api.counter_actual_ticks
        ))

    def get_statistics_api(self):
        return PatternDetectorStatisticsApi(self.pattern_list, self.config.investment)


class FormationColorHandler:
    def get_colors_for_formation(self, formation: Pattern):
        return self.__get_formation_color__(formation), self.__get_control_color__(formation)

    @staticmethod
    def __get_formation_color__(formation: Pattern):
        if formation.was_breakout_done():
            return 'green'
        else:
            return 'yellow'

    @staticmethod
    def __get_control_color__(formation: Pattern):
        if formation.was_breakout_done():
            if formation.trade_result.actual_win > 0:
                return 'lime'
            else:
                return 'orangered'
        else:
            return 'white'


class PatternPlotter:
    def __init__(self, api_object, detector: PatternDetector):
        self.api_object = api_object  # StockDatabaseDataFrame or AlphavantageStockFetcher
        self.api_object_class = self.api_object.__class__.__name__
        self.detector = detector
        self.config = self.detector.config
        self.accuracy_pct = self.config.accuracy_pct
        self.df = api_object.df
        self.df_data = api_object.df_data
        self.column_data = api_object.column_data
        self.df_volume = api_object.df_volume
        self.column_volume = api_object.column_volume
        self.symbol = api_object.symbol

    def plot_data_frame(self):
        with_close_plot = False

        if with_close_plot:
            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 10), sharex='all')
            self.__plot_close__(axes[0])
            self.__plot_candlesticks__(axes[1])
            self.__plot_volume__(axes[2])
        else:
            fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 7), sharex='all')
            self.__plot_candlesticks__(axes[0])
            self.__plot_volume__(axes[1])

        plt.title('{}. {} ({}) for {}'.format(self.config.actual_number, self.config.actual_ticker
                                              , self.config.actual_ticker_name, self.config.actual_and_clause))
        plt.tight_layout()
        plt.xticks(rotation=45)
        plt.show()

    def __plot_close__(self, axis):
        plot_01 = self.df_data[[self.column_data]].plot(ax=axis)
        plot_01.legend(loc='upper left')

    def __plot_candlesticks__(self, axis):
        ohlc = []
        for ind, rows in self.df.iterrows():
            append_me = int(dt.date2num(ind)), rows[CN.OPEN], rows[CN.HIGH], rows[CN.LOW], rows[CN.CLOSE]
            ohlc.append(append_me)
        candlestick_ohlc(axis, ohlc, width=0.4, colorup='g')
        axis.xaxis_date()
        self.add_formations(axis)
        self.add_possible_pattern(axis)
        axis.grid()
        # self.__add_fibonacci_waves__(axis)

    def __plot_volume__(self, axis):
        self.df_volume.plot(ax=axis, title=self.column_volume)

    def add_formations(self, ax):
        color_handler = FormationColorHandler()
        patches_dic = {}
        for pattern in self.detector.pattern_list:
            color_formation, color_control = color_handler.get_colors_for_formation(pattern)
            if color_formation in patches_dic:
                patches_dic[color_formation].append(pattern.get_shape())
            else:
                patches_dic[color_formation] = [pattern.get_shape()]

            if pattern.was_breakout_done() and pattern.is_control_df_available():
                if color_control in patches_dic:
                    patches_dic[color_control].append(pattern.get_control_shape())
                else:
                    patches_dic[color_control] = [pattern.get_control_shape()]
            pattern.add_annotations(ax)

        for colors in patches_dic:
            p = PatchCollection(patches_dic[colors], alpha=0.4)
            p.set_color(colors)
            ax.add_collection(p)

    def add_possible_pattern(self, ax):
        patches_dic = {'green': [], 'blue': []}

        for shapes in self.detector.get_shapes_for_possible_pattern_ranges_top():
            patches_dic['green'].append(shapes)
        # for shapes in self.detector.get_shapes_for_possible_pattern_ranges_bottom():
        #     patches_dic['blue'].append(shapes)

        for colors in patches_dic:
            p = PatchCollection(patches_dic[colors], alpha=0.4)
            p.set_color(colors)
            ax.add_collection(p)

    def __add_fibonacci_waves__(self, ax):
        color_dic = {'min': 'aqua', 'max': 'blue'}
        offset_dic = {'min': (1, 1), 'max': (-1, -1)}
        for key in color_dic:
            if key == 'min':
                xy_list = self.detector.wave_parser.get_xy_min_parameter()
            else:
                xy_list = self.detector.wave_parser.get_xy_max_parameter()
            offset = offset_dic[key]
            patches = []
            for xy in xy_list:
                patch = Arrow(xy[0]-offset[0], xy[1]-offset[1], offset[0], offset[1])
                patches.append(patch)
            p = PatchCollection(patches)
            p.set_color(color_dic[key])
            ax.add_collection(p)


class FSC:  # Formation Statistics Columns
    C_BOUND_UPPER_VALUE = 'conf.bound_upper_value'  # eg. CN.HIGH
    C_BOUND_LOWER_VALUE = 'conf.bound_lower_value'  # eg. CN.LOW
    C_CHECK_PREVIOUS_PERIOD = 'conf.check_previous_period'
    C_BREAKOUT_OVER_CONGESTION = 'conf.breakout_over_congestion_range'
    C_ACCURACY_PCT = 'conf.accuracy in %'
    C_BREAKOUT_RANGE_PCT = 'conf.breakout range in %'
    C_AND_CLAUSE = 'conf.and clause'

    CON_PREVIOUS_PERIOD_CHECK_OK = FCC.PREVIOUS_PERIOD_CHECK_OK
    CON_COMBINED_PARTS_APPLICABLE = FCC.COMBINED_PARTS_APPLICABLE
    CON_BREAKOUT_WITH_BUY_SIGNAL = FCC.BREAKOUT_WITH_BUY_SIGNAL

    NUMBER = 'Number'
    STATUS = 'Status'
    TICKER = 'Ticker'
    NAME = 'Name'
    FORMATION = 'Formation'
    BEGIN_PREVIOUS = 'Begin previous period'
    BEGIN = 'Begin'
    END = 'End'
    LOWER = 'Lower'
    UPPER = 'Upper'
    T_ORIG = 'Ticks original'
    T_FINAL = 'Ticks final'
    BREAKOUT_DATE = 'Breakout date'
    BREAKOUT_DIRECTION = 'Breakout direction'
    VOLUME_CHANGE = 'Volume change'
    EXPECTED = 'Expected'
    RESULT = 'Result'
    EXT = 'Extended'
    VAL = 'Validated'
    BOUGHT_AT = 'Bought at'
    SOLD_AT = 'Sold at'
    BOUGHT_ON = 'Bought on'
    SOLD_ON = 'Sold on'
    T_NEEDED = 'Ticks needed'
    LIMIT = 'Limit'
    STOP_LOSS_AT = 'Stop loss at'
    STOP_LOSS_TRIGGERED = 'Stop loss triggered'
    RESULT_DF_MAX = 'Result DF max.'
    RESULT_DF_MIN = 'Result DF min.'
    FIRST_LIMIT_REACHED = 'First limit reached'
    STOP_LOSS_MAX_REACHED = 'Max stop loss reached (bound of original range)'


class PatternStatistics:
    def __init__(self):
        self.list = []
        self.column_list = []

        self.column_list.append(FSC.NUMBER)
        self.column_list.append(FSC.TICKER)
        self.column_list.append(FSC.NAME)
        self.column_list.append(FSC.STATUS)
        self.column_list.append(FSC.FORMATION)
        self.column_list.append(FSC.BEGIN_PREVIOUS)
        self.column_list.append(FSC.BEGIN)
        self.column_list.append(FSC.END)

        self.column_list.append(FSC.C_BOUND_UPPER_VALUE)
        self.column_list.append(FSC.C_BOUND_LOWER_VALUE)
        self.column_list.append(FSC.C_CHECK_PREVIOUS_PERIOD)
        self.column_list.append(FSC.C_BREAKOUT_OVER_CONGESTION)
        self.column_list.append(FSC.C_ACCURACY_PCT)
        self.column_list.append(FSC.C_BREAKOUT_RANGE_PCT)
        self.column_list.append(FSC.C_AND_CLAUSE)

        self.column_list.append(FSC.CON_PREVIOUS_PERIOD_CHECK_OK)
        self.column_list.append(FSC.CON_COMBINED_PARTS_APPLICABLE)
        self.column_list.append(FSC.CON_BREAKOUT_WITH_BUY_SIGNAL)

        self.column_list.append(FSC.LOWER)
        self.column_list.append(FSC.UPPER)
        self.column_list.append(FSC.T_ORIG)
        self.column_list.append(FSC.T_FINAL)
        self.column_list.append(FSC.BREAKOUT_DATE)
        self.column_list.append(FSC.BREAKOUT_DIRECTION)
        self.column_list.append(FSC.VOLUME_CHANGE)
        self.column_list.append(FSC.EXPECTED)
        self.column_list.append(FSC.RESULT)
        self.column_list.append(FSC.EXT)
        self.column_list.append(FSC.VAL)
        self.column_list.append(FSC.BOUGHT_AT)
        self.column_list.append(FSC.SOLD_AT)
        self.column_list.append(FSC.BOUGHT_ON)
        self.column_list.append(FSC.SOLD_ON)
        self.column_list.append(FSC.T_NEEDED)

        self.column_list.append(FSC.LIMIT)
        self.column_list.append(FSC.STOP_LOSS_AT)
        self.column_list.append(FSC.STOP_LOSS_TRIGGERED)

        self.column_list.append(FSC.RESULT_DF_MAX)
        self.column_list.append(FSC.RESULT_DF_MIN)
        self.column_list.append(FSC.FIRST_LIMIT_REACHED)
        self.column_list.append(FSC.STOP_LOSS_MAX_REACHED)

        self.dic = {}

    def __init_dic__(self):
        for entries in self.column_list:
            self.dic[entries] = ''

    def add_entry(self, pattern: Pattern):
        self.__init_dic__()

        self.dic[FSC.C_BOUND_UPPER_VALUE] = pattern.config.bound_upper_value
        self.dic[FSC.C_BOUND_LOWER_VALUE] = pattern.config.bound_lower_value
        self.dic[FSC.C_CHECK_PREVIOUS_PERIOD] = pattern.config.check_previous_period
        self.dic[FSC.C_BREAKOUT_OVER_CONGESTION] = pattern.config.breakout_over_congestion_range
        self.dic[FSC.C_ACCURACY_PCT] = pattern.config.accuracy_pct
        self.dic[FSC.C_BREAKOUT_RANGE_PCT] = pattern.config.breakout_range_pct
        self.dic[FSC.C_AND_CLAUSE] = pattern.config.and_clause

        self.dic[FSC.CON_PREVIOUS_PERIOD_CHECK_OK] = pattern.condition_handler.previous_period_check_ok
        self.dic[FSC.CON_COMBINED_PARTS_APPLICABLE] = pattern.condition_handler.combined_parts_applicable
        self.dic[FSC.CON_BREAKOUT_WITH_BUY_SIGNAL] = pattern.condition_handler.breakout_with_buy_signal

        self.dic[FSC.STATUS] = 'Finished' if pattern.was_breakout_done() else 'Open'
        self.dic[FSC.NUMBER] = pattern.config.actual_number
        self.dic[FSC.TICKER] = pattern.config.actual_ticker
        self.dic[FSC.NAME] = pattern.config.actual_ticker_name
        self.dic[FSC.FORMATION] = pattern.__class__.__name__
        self.dic[FSC.BEGIN_PREVIOUS] = 'TODO'
        self.dic[FSC.BEGIN] = FormationDate.get_date_from_datetime(pattern.date_first)
        self.dic[FSC.END] = FormationDate.get_date_from_datetime(pattern.date_last)
        self.dic[FSC.LOWER] = round(pattern.bound_lower, 2)
        self.dic[FSC.UPPER] = round(pattern.bound_upper, 2)
        self.dic[FSC.T_ORIG] = pattern.ticks_initial
        self.dic[FSC.T_FINAL] = pattern.ticks
        if pattern.was_breakout_done():
            self.dic[FSC.BREAKOUT_DATE] = FormationDate.get_date_from_datetime(pattern.breakout.breakout_date)
            self.dic[FSC.BREAKOUT_DIRECTION] = pattern.breakout.breakout_direction
            self.dic[FSC.VOLUME_CHANGE] = pattern.breakout.volume_change_pct
            if pattern.is_control_df_available():
                self.dic[FSC.EXPECTED] = pattern.trade_result.expected_win
                self.dic[FSC.RESULT] = pattern.trade_result.actual_win
                self.dic[FSC.VAL] = pattern.trade_result.formation_consistent
                self.dic[FSC.EXT] = pattern.trade_result.limit_extended_counter
                self.dic[FSC.BOUGHT_AT] = round(pattern.trade_result.bought_at, 2)
                self.dic[FSC.SOLD_AT] = round(pattern.trade_result.sold_at, 2)
                self.dic[FSC.BOUGHT_ON] = FormationDate.get_date_from_datetime(pattern.trade_result.bought_on)
                self.dic[FSC.SOLD_ON] = FormationDate.get_date_from_datetime(pattern.trade_result.sold_on)
                self.dic[FSC.T_NEEDED] = pattern.trade_result.actual_ticks
                self.dic[FSC.LIMIT] = round(pattern.trade_result.limit, 2)
                self.dic[FSC.STOP_LOSS_AT] = round(pattern.trade_result.stop_loss_at, 2)
                self.dic[FSC.STOP_LOSS_TRIGGERED] = pattern.trade_result.stop_loss_reached

                self.dic[FSC.RESULT_DF_MAX] = pattern.control_df[CN.CLOSE].max()
                self.dic[FSC.RESULT_DF_MIN] = pattern.control_df[CN.CLOSE].min()
                self.dic[FSC.FIRST_LIMIT_REACHED] = False  # default
                self.dic[FSC.STOP_LOSS_MAX_REACHED] = False  # default
                if pattern.breakout_direction == FD.ASC \
                        and (pattern.bound_upper + pattern.breadth < self.dic[FSC.RESULT_DF_MAX]):
                    self.dic[FSC.FIRST_LIMIT_REACHED] = True
                if pattern.breakout_direction == FD.DESC \
                        and (pattern.bound_lower - pattern.breadth > self.dic[FSC.RESULT_DF_MIN]):
                    self.dic[FSC.FIRST_LIMIT_REACHED] = True
                if pattern.breakout_direction == FD.ASC \
                        and (pattern.bound_lower > self.dic[FSC.RESULT_DF_MIN]):
                    self.dic[FSC.STOP_LOSS_MAX_REACHED] = True
                if pattern.breakout_direction == FD.DESC \
                        and (pattern.bound_upper < self.dic[FSC.RESULT_DF_MAX]):
                    self.dic[FSC.STOP_LOSS_MAX_REACHED] = True

        new_entry = [self.dic[column] for column in self.column_list]
        self.list.append(new_entry)

    def get_frame_set(self) -> pd.DataFrame:
        df = pd.DataFrame(self.list)
        df.columns = self.column_list
        return df

    def print_overview(self):
        if len(self.list) == 0:
            print('No formations found')
        else:
            df = self.get_frame_set()
            print(df.head(df.shape[0]))
            print('\n')

    def write_to_excel(self, excel_writer, sheet):
        if len(self.list) == 0:
            print('No formations found')
        else:
            df = self.get_frame_set()
            df.to_excel(excel_writer, sheet)


class PatternDetectorStatisticsApi:
    def __init__(self, pattern_list, investment: float):
        self.pattern_list = pattern_list
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
        for pattern in self.pattern_list:
            if pattern.was_breakout_done() and pattern.is_control_df_available():
                result = pattern.trade_result
                self.counter_actual_ticks += result.actual_ticks
                self.counter_ticks += result.max_ticks
                self.counter_stop_loss = self.counter_stop_loss + 1 if result.stop_loss_reached else self.counter_stop_loss
                self.counter_formation_OK = self.counter_formation_OK + 1 if result.formation_consistent else self.counter_formation_OK
                self.counter_formation_NOK = self.counter_formation_NOK + 1 if not result.formation_consistent else self.counter_formation_NOK
                traded_entities = int(self.investment_working / result.bought_at)
                self.investment_working = round(self.investment_working + (traded_entities * result.actual_win), 2)


class DetectorStatistics:
    def __init__(self):
        self.list = []
        self.column_list = ['Number', 'Ticker', 'Name', 'Investment', 'Result', 'Change%', 'SL', 'F_OK', 'F_NOK', 'Ticks']

    def add_entry(self, config: PatternConfiguration, api: PatternDetectorStatisticsApi):
        new_entry = [config.actual_number, config.actual_ticker, config.actual_ticker_name
            , api.investment_start, api.investment_working, api.diff_pct
            , api.counter_stop_loss, api.counter_formation_OK, api.counter_formation_NOK, api.counter_actual_ticks]
        self.list.append(new_entry)

    def get_frame_set(self) -> pd.DataFrame:
        df = pd.DataFrame(self.list)
        df.columns = self.column_list
        return df

    def print_overview(self):
        df = self.get_frame_set()
        print(df.head(df.shape[0]))

    def write_to_excel(self, excel_writer, sheet):
        df = self.get_frame_set()
        df.to_excel(excel_writer, sheet)


class PatternController:
    def __init__(self, config: PatternConfiguration):
        self.config = config
        self.detector_statistics = DetectorStatistics()
        self.formation_statistics = PatternStatistics()
        self.stock_db = stock_database.StockDatabase
        self.plotter_input_obj = None
        self.df_data = None
        self.__excel_file_with_test_data = ''
        self.df_test_data = pd.DataFrame
        self.loop_list = []  # format of an entry (ticker, and_clause)
        self.__start_row = 0
        self.__end_row = 0

    def run_pattern_checker(self, excel_file_with_test_data: str = '', start_row: int = 1, end_row: int = 0):
        self.__init_db_and_test_data__(excel_file_with_test_data, start_row, end_row)
        self.__init_loop_list__()

        counter = 0
        for entries in self.loop_list:
            ticker = entries[0]
            and_clause = entries[1]
            self.config.actual_number = entries[2]
            self.config.actual_ticker = ticker
            self.config.actual_ticker_name = self.config.ticker_dic[ticker]
            self.config.actual_and_clause = and_clause
            print('\nProcessing {} ({})...\n'.format(ticker, self.config.actual_ticker_name))
            if config.get_data_from_db:
                stock_db_df_obj = stock_database.StockDatabaseDataFrame(self.stock_db, ticker, and_clause)
                self.plotter_input_obj = stock_db_df_obj
                self.df_data = stock_db_df_obj.df_data
            else:
                fetcher = AlphavantageStockFetcher(ticker, self.config.api_period, self.config.api_output_size)
                self.plotter_input_obj = fetcher
                self.df_data = fetcher.df_data

            data_frame_factory = DataFramePatternFactory(self.df_data)
            detector = PatternDetector(data_frame_factory.df, data_frame_factory.df_min_max, self.config)
            detector.parse_for_pattern()
            self.__handle_statistics__(detector)

            if self.config.plot_data:
                if len(detector.pattern_list) == 0 and not detector.possible_pattern_ranges_available:
                    print('...no formations found.')
                else:
                    plotter = PatternPlotter(self.plotter_input_obj, detector)
                    plotter.plot_data_frame()

            counter += 1

            if counter >= self.config.max_number_securities:
                break

        if config.show_final_statistics:
            self.config.print()
            if self.config.statistics_excel_file_name == '':
                self.formation_statistics.print_overview()
                self.detector_statistics.print_overview()
            else:
                writer = pd.ExcelWriter(self.config.statistics_excel_file_name)
                self.formation_statistics.write_to_excel(writer, 'Formations')
                self.detector_statistics.write_to_excel(writer, 'Overview')
                print('Statistics were written to file: {}'.format(self.config.statistics_excel_file_name))
                writer.save()

    def __init_db_and_test_data__(self, excel_file_with_test_data: str, start_row: int, end_row: int):
        if self.config.get_data_from_db:
            self.stock_db = stock_database.StockDatabase()
            if excel_file_with_test_data != '':
                self.__excel_file_with_test_data = excel_file_with_test_data
                self.df_test_data = pd.ExcelFile(self.__excel_file_with_test_data).parse(0)
                self.__start_row = start_row
                self.__end_row = self.df_test_data.shape[0] if end_row == 0 else end_row

    def __init_loop_list__(self):
        if self.config.get_data_from_db and self.__excel_file_with_test_data != '':
            counter = 0
            for ind, rows in self.df_test_data.iterrows():
                counter += 1
                if counter >= self.__start_row:
                    self.config.ticker_dic[rows[FSC.TICKER]] = rows[FSC.NAME]
                    start_date = FormationDate.get_date_from_datetime(rows[FSC.BEGIN_PREVIOUS])
                    date_end = FormationDate.get_date_from_datetime(rows[FSC.END] + timedelta(days=rows[FSC.T_FINAL] + 20))
                    and_clause = "Date BETWEEN '{}' AND '{}'".format(start_date, date_end)
                    self.loop_list.append([rows[FSC.TICKER], and_clause, counter])
                if counter >= self.__end_row:
                    break
        else:
            counter = 0
            for ticker in self.config.ticker_dic:
                counter += 1
                self.loop_list.append([ticker, self.config.and_clause, counter])

    def __handle_statistics__(self, detector: PatternDetector):
        for pattern in detector.pattern_list:
            self.formation_statistics.add_entry(pattern)

        if config.show_final_statistics:
            self.detector_statistics.add_entry(self.config, detector.get_statistics_api())
        else:
            detector.print_statistics()


config = PatternConfiguration()
config.get_data_from_db = True
config.api_period = ApiPeriod.DAILY
config.pattern_type = FT.CHANNEL
config.plot_data = True
config.statistics_excel_file_name = 'statistics_channel.xlsx'
config.statistics_excel_file_name = ''
config.bound_upper_value = CN.CLOSE
config.bound_lower_value = CN.CLOSE
config.breakout_over_congestion_range = False
# config.show_final_statistics = True
config.max_number_securities = 1000
config.accuracy_pct = 0.005  # default is 0.05
config.breakout_range_pct = 0.01  # default is 0.01
config.use_index(Indices.DOW_JONES)
config.use_own_dic({"GE": "GE"})  # "INTC": "Intel",  "NKE": "Nike", "V": "Visa",  "GE": "GE"
# "FCEL": "FuelCell" "KO": "Coca Cola" # "BMWYY": "BMW"
config.and_clause = "Date BETWEEN '2017-03-25' AND '2019-10-30'"
# config.and_clause = ''
config.api_output_size = ApiOutputsize.COMPACT

pattern_controller = PatternController(config)
pattern_controller.run_pattern_checker('')
