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
from matplotlib.patches import Circle, Wedge, Polygon, Rectangle, Arrow, Ellipse
from matplotlib.collections import PatchCollection
from datetime import datetime, timedelta
from sertl_analytics.datafetcher.database_fetcher import BaseDatabase, DatabaseDataFrame
from sertl_analytics.datafetcher.file_fetcher import NasdaqFtpFileFetcher
from sertl_analytics.pybase.df_base import PyBaseDataFrame
from sertl_analytics.pybase.date_time import MyPyDate
import stock_database as sdb
from sertl_analytics.functions import math_functions
from sertl_analytics.pybase.loop_list import LL, LoopList4Dictionaries, LoopList, ExtendedDictionary
from sertl_analytics.pybase.exceptions import MyException
import itertools
import math

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
    TRIANGLE_TOP = 'Triangle top'
    TRIANGLE_BOTTOM = 'Triangle bottom'
    TRIANGLE_UP = 'Triangle up'
    TRIANGLE_DOWN = 'Triangle down'
    CHANNEL = 'Channel'  # https://www.investopedia.com/articles/trading/05/020905.asp
    CHANNEL_UP = 'Channel up'
    CHANNEL_DOWN = 'Channel down'
    TKE_DOWN = 'TKE down'  # Trend correction extrema
    TKE_UP = 'TKE up'  # Trend correction extrema
    HEAD_SHOULDER = 'Head-Shoulder'
    ALL = 'All'

    @staticmethod
    def get_all():
        return [FT.TRIANGLE, FT.TRIANGLE_TOP, FT.TRIANGLE_BOTTOM, FT.TRIANGLE_UP, FT.TRIANGLE_DOWN
                , FT.CHANNEL, FT.CHANNEL_UP, FT.CHANNEL_DOWN, FT.TKE_UP, FT.TKE_DOWN, FT.HEAD_SHOULDER]


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


class RuntimeConfiguration:
    actual_list = []
    actual_position = 0
    actual_tick_position = 0
    actual_number = 0
    actual_ticker = ''
    actual_ticker_name = ''
    actual_and_clause = ''
    actual_pattern_type = FT.NONE
    actual_breakout = None


class PatternConfiguration:
    def __init__(self):
        self.get_data_from_db = True
        self.pattern_type_list = [FT.CHANNEL]
        self.api_period = ApiPeriod.DAILY
        self.api_output_size = ApiOutputsize.COMPACT
        self.bound_upper_value = CN.HIGH
        self.bound_lower_value = CN.LOW
        self.plot_data = True
        self.check_previous_period = False   # default
        self.breakout_over_congestion_range = False
        self.breakout_range_pct = 0.01
        self.investment = 1000
        self.max_number_securities = 1000
        self.show_final_statistics = True
        self.and_clause = "Date BETWEEN '2017-12-01' AND '2019-12-31'"
        self.runtime = RuntimeConfiguration()
        self.statistics_excel_file_name = ''
        self.ticker_dic = {}
        self.__previous_period_length = 0

    def __get_previous_period_length__(self):
        return self.__previous_period_length

    def __set_previous_period_length__(self, value: int):
        self.__previous_period_length = value

    previous_period_length = property(__get_previous_period_length__, __set_previous_period_length__)

    def print(self):
        source = 'DB' if self.get_data_from_db else 'Api'
        pattern_type = self.pattern_type_list
        and_clause = self.and_clause
        period = self.api_period
        output_size = self.api_output_size
        bound_upper_v = self.bound_upper_value
        bound_lower_v = self.bound_lower_value
        breakout_over_big_range = self.breakout_over_congestion_range

        print('\nConfiguration settings:')
        if self.get_data_from_db:
            print('Formation: {} \nSource: {} \nAnd clause: {} \nUpper/Lower Bound Value: {}/{}'
                  ' \nBreakout big range: {}\n'.format(
                    pattern_type, source, and_clause, bound_upper_v, bound_lower_v
                    , breakout_over_big_range))
        else:
            print('Formation: {} \nSource: {} \n\nApiPeriod/ApiOutput size: {}/{} \nUpper/Lower Bound Value: {}/{}'
                  ' \nBreakout big range: {}\n'.format(
                    pattern_type, source, period, output_size, bound_upper_v, bound_lower_v
                    , breakout_over_big_range))

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
        return PyBaseDataFrame.get_rows_as_dictionary(db_data_frame.df, 'Symbol', ['Symbol'])


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
    H_UPPER = 'H_UPPER'
    H_LOWER = 'H_LOWER'
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
    H_U_out = 'Helper_Upper_out'
    H_U_in = 'Helper_Upper_in'
    H_U_on = 'Helper_Upper_on'
    H_M_in = 'Helper_Middle_in'
    H_L_in = 'Helper_Low_in'
    H_L_on = 'Helper_Low_on'
    H_L_out = 'Helper_Low_out'

    NONE = 'NONE'


class CT:  # Constraint types
    ALL_IN = 'All_In'
    COUNT = 'Count'
    SERIES = 'Series'


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


class PatternConditionHandler:
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
    def open(self):
        return self.tick[CN.OPEN]

    @property
    def high(self):
        return self.tick[CN.HIGH]

    @property
    def low(self):
        return self.tick[CN.LOW]

    @property
    def close(self):
        return self.tick[CN.CLOSE]

    @property
    def volume(self):
        return self.tick[CN.VOL]

    def print(self):
        print('Pos: {}, Date: {}, High: {}, Low: {}'.format(self.position, self.date, self.high, self.low))

    def get_linear_f_params_for_max(self, tick):
        return math_functions.get_function_parameters(self.position, self.high, tick.position, tick.high)

    def get_linear_f_params_for_min(self, tick):
        return math_functions.get_function_parameters(self.position, self.low, tick.position, tick.low)

    def is_sustainable(self):
        return abs((self.open - self.close) / (self.high - self.low)) > 0.6

    def is_volume_rising(self, tick_comp, min_percentage: int):
        return self.volume / tick_comp.volume > (100 + min_percentage) / 100

    def has_gap_to(self, tick_comp):
        return self.low > tick_comp.high or self.high < tick_comp.low


class PatternFunctionContainer:
    def __init__(self, pattern_type: str, df: pd.DataFrame, f_lower: np.poly1d = None, f_upper: np.poly1d = None):
        self.pattern_type = pattern_type
        self.df = df
        self.__tick_for_helper = None
        self.__tick_first = WaveTick(self.df.iloc[0])
        self.__tick_last = WaveTick(self.df.iloc[-1])
        self.__f_lower = f_lower
        self.__f_upper = f_upper
        self.__h_lower = f_lower
        self.__h_upper = f_upper
        self.__f_regression = self.__get_f_regression__()
        self.__breakout_direction = None
        self.__pattern_direction = FD.ASC if self.__f_regression[1] > 0 else FD.DESC
        if self.is_valid():
            self.__init_tick_for_helper__()

    @property
    def number_of_positions(self):
        return self.__tick_last.position - self.__tick_first.position

    @property
    def tick_first(self):
        return self.__tick_first

    @property
    def tick_last(self):
        return self.__tick_last

    @property
    def pattern_direction(self):
        return self.__pattern_direction

    @property
    def f_lower(self):
        return self.__f_lower

    @property
    def f_upper(self):
        return self.__f_upper

    @property
    def h_lower(self):
        return self.__h_lower

    @property
    def h_upper(self):
        return self.__h_upper

    @property
    def f_upper_trade(self):
        if self.__breakout_direction == FD.DESC:
            return self.__h_lower
        else:
            return np.poly1d([0, self.__h_upper[0] + self.pattern_breadth])

    @property
    def f_lower_trade(self):
        if self.__breakout_direction == FD.DESC:
            return np.poly1d([0, self.__h_lower[0] - self.pattern_breadth])
        else:
            return self.__h_upper

    @property
    def f_regression(self):
        return self.__f_regression

    @property
    def pattern_breadth(self):
        breadth_left = self.__f_upper(self.tick_first.position) - self.__f_lower(self.tick_first.position)
        breadth_right = self.__f_upper(self.tick_for_helper.position) - self.__f_lower(self.tick_for_helper.position)
        if self.pattern_type in [FT.TKE_DOWN, FT.TKE_UP]:
            return round(breadth_right, 2)
        else:
            return round((breadth_left + breadth_right)/2, 2)

    def __set_breakout_direction__(self, breakout_direction: str):
        self.__breakout_direction = breakout_direction

    def __get_breakout_direction__(self):
        return self.__breakout_direction

    breakout_direction = property(__get_breakout_direction__, __set_breakout_direction__)

    def is_regression_value_in_pattern_for_position(self, pos):
        return self.__f_lower(pos) <= self.__f_regression(pos) <= self.__f_upper(pos)

    def is_valid(self):
        return not(self.__f_lower is None or self.__f_upper is None)

    def is_tick_breakout(self, tick: WaveTick):
        f_upper_value = self.get_upper_value_for_position(tick.position)
        f_lower_value = self.get_lower_value_for_position(tick.position)

        if self.pattern_type in [FT.TKE_UP, FT.TRIANGLE_UP, FT.CHANNEL_UP]:
            return tick.close < f_lower_value
        elif self.pattern_type in [FT.TKE_DOWN, FT.TRIANGLE_DOWN, FT.CHANNEL_DOWN]:
            return tick.close > f_upper_value
        else:
            return not (f_lower_value <= tick.close <= f_upper_value)

    def is_tick_inside_pattern_range(self, tick: WaveTick):
        if self.__pattern_direction == FD.ASC:
            h_upper_value = self.__h_upper(tick.position)
            f_lower_value = self.__f_lower(tick.position)
            return f_lower_value < h_upper_value
        else:
            h_lower_value = self.__h_lower(tick.position)
            f_upper_value = self.__f_upper(tick.position)
        return h_lower_value < f_upper_value

    def add_tick_from_main_df_to_df(self, df_main: pd.DataFrame, tick: WaveTick):
        if tick is not None:
            self.__tick_last = tick
            self.df = pd.concat([self.df, df_main.loc[tick.position:tick.position]])

    def __get_f_regression__(self) -> np.poly1d:
        np_array = np.polyfit(self.df[CN.POSITION], self.df[CN.CLOSE], 1)
        return np.poly1d([np_array[0], np_array[1]])

    def __get_tick_for_helper__(self):
        return self.__tick_for_helper

    def __set_tick_for_helper__(self, tick):
        self.__tick_for_helper = tick
        self.__h_upper = np.poly1d([0, self.__f_upper(tick.position)])
        self.__h_lower = np.poly1d([0, self.__f_lower(tick.position)])

    tick_for_helper = property(__get_tick_for_helper__, __set_tick_for_helper__)

    def set_tick_for_breakout(self, tick: WaveTick):
        if self.pattern_type != FT.TKE_DOWN:
            self.__set_tick_for_helper__(tick)

    def adjust_functions_when_required(self, tick: WaveTick):
        if self.pattern_type == FT.TKE_DOWN:
            if tick.low < self.__f_lower(tick.position):
                self.__f_lower = np.poly1d([0, tick.low])
                self.__set_tick_for_helper__(tick)

    @property
    def is_pattern_type_configured_for_helper_functions(self) -> bool:
        return self.pattern_type in [FT.TKE_DOWN, FT.TRIANGLE_UP]

    def get_upper_value_for_position(self, pos: int):
        if self.tick_for_helper is None or self.tick_for_helper.position > pos:
            return round(self.__f_upper(pos), 2)
        if self.pattern_direction == FD.ASC:
            return round(min(self.__f_upper(pos), self.__h_upper(pos)), 2)
        else:
            return round(max(self.__f_upper(pos), self.__h_upper(pos)), 2)

    def get_lower_value_for_position(self, pos: int):
        if self.tick_for_helper is None or self.tick_for_helper.position > pos:
            return round(self.__f_lower(pos), 2)
        if self.pattern_direction == FD.ASC:
            return round(min(self.__f_lower(pos), self.__h_lower(pos)), 2)
        else:
            return round(max(self.__f_lower(pos), self.__h_lower(pos)), 2)

    def __init_tick_for_helper__(self):
        if self.pattern_type == FT.TKE_UP:
            pos = self.df[CN.HIGH].idxmax(axis=0)
            tick = WaveTick(self.df.loc[pos])
            self.__set_tick_for_helper__(tick)
        elif self.pattern_type == FT.TKE_DOWN:
            pos = self.df[CN.LOW].idxmin(axis=0)
            tick = WaveTick(self.df.loc[pos])
            self.__set_tick_for_helper__(tick)


class PatternBreakoutApi:
    def __init__(self, function_cont: PatternFunctionContainer, config: PatternConfiguration):
        self.function_cont = function_cont
        self.config = config
        self.tick_previous = None
        self.tick_breakout = None
        self.constraints = None


class PatternBreakout:
    def __init__(self, api: PatternBreakoutApi):
        self.function_cont = api.function_cont
        self.config = api.config
        self.constraints = api.constraints
        self.pattern_type = self.function_cont.pattern_type
        self.tick_previous = api.tick_previous
        self.tick_breakout = api.tick_breakout
        self.breakout_date = self.tick_breakout.date
        self.volume_change_pct = round(self.tick_breakout.volume/self.tick_previous.volume, 2)
        self.tolerance_pct = self.constraints.tolerance_pct
        self.bound_upper = self.function_cont.get_upper_value_for_position(self.tick_breakout.position)
        self.bound_lower = self.function_cont.get_lower_value_for_position(self.tick_breakout.position)
        self.pattern_breadth = self.bound_upper - self.bound_lower
        self.tolerance_range = self.pattern_breadth * self.tolerance_pct
        self.limit_upper = self.bound_upper + self.tolerance_range
        self.limit_lower = self.bound_lower - self.tolerance_range
        self.breakout_direction = self.__get_breakout_direction__()
        self.sign = 1 if self.breakout_direction == FD.ASC else -1

    def is_breakout_a_signal(self) -> bool:
        if self.__is_breakout_over_limit__():
            if True or self.__is_breakout_in_allowed_range__():
                if self.tick_breakout.is_volume_rising(self.tick_previous, 10): # i.e. 10% more volume required
                    if self.__is_breakout_powerful__():
                        return True
        return False

    def get_details_for_annotations(self):
        vol_change = round(((self.tick_breakout.volume/self.tick_previous.volume) - 1) * 100, 0)
        return '{} - Volume change: {}%'.format(self.tick_breakout.date_str, vol_change)

    def __get_breakout_direction__(self) -> str:
        return FD.ASC if self.tick_breakout.close > self.bound_upper else FD.DESC

    def __is_breakout_powerful__(self) -> bool:
        return self.tick_breakout.is_sustainable or self.tick_breakout.has_gap_to(self.tick_previous)

    def __is_breakout_over_limit__(self) -> bool:
        limit_range = self.pattern_breadth if self.config.breakout_over_congestion_range \
            else self.pattern_breadth * self.config.breakout_range_pct
        if self.breakout_direction == FD.ASC:
            return self.tick_breakout.close >= self.bound_upper + limit_range
        else:
            return self.tick_breakout.close <= self.bound_lower - limit_range

    def __is_breakout_in_allowed_range__(self) -> bool:
        if self.breakout_direction == FD.ASC:
            return self.tick_breakout.close < self.bound_upper + self.pattern_breadth / 2
        else:
            return self.tick_breakout.close > self.bound_lower - self.pattern_breadth / 2


class AnnotationParameter:
    def __init__(self):
        self.text = ''
        self.xy = ()
        self.xy_text = ()
        self.arrow_props = {}
        self.visible = False

    def get_annotation(self, axes):
        annotation = axes.annotate(self.text, xy=self.xy, xytext=self.xy_text, arrowprops=self.arrow_props)
        annotation.set_visible(self.visible)
        return annotation


class PatternPart:
    def __init__(self, function_cont: PatternFunctionContainer, config: PatternConfiguration):
        self.function_cont = function_cont
        self.df = self.function_cont.df
        self.config = config
        self.pattern_type = self.function_cont.pattern_type
        self.breakout = self.config.runtime.actual_breakout
        self.tick_first = None
        self.tick_last = None
        self.tick_high = None
        self.tick_low = None
        self.breadth = 0
        self.breadth_first = 0
        self.bound_upper = 0
        self.bound_lower = 0
        self.__distance_min = 0
        self.__distance_max = 0
        self.__xy = None
        self.__xy_center = ()
        if self.df.shape[0] > 0:
            self.stock_df = StockDataFrame(self.df)
            self.__calculate_values__()
            self.__set_xy_parameter__()
            self.__set_xy_center__()

    def get_annotation_parameter(self, for_max: bool, color: str = 'blue'):
        annotation_param = AnnotationParameter()
        offset_x = -10
        offset_y = 0.5
        offset = [offset_x, offset_y] if for_max else [-offset_x, -offset_y]
        annotation_param.text = self.__get_text_for_annotation__(for_max)
        annotation_param.xy = self.__xy_center
        annotation_param.xy_text = (self.__xy_center[0] + offset[0], self.__xy_center[1] + offset[1])
        annotation_param.visible = False
        annotation_param.arrow_props = {'color': color, 'width': 0.2, 'headwidth': 4}
        return annotation_param

    @property
    def length(self):
        return self.tick_last.position - self.tick_first.position

    def __calculate_values__(self):
        self.tick_first = WaveTick(self.df.iloc[0])
        self.tick_last = WaveTick(self.df.iloc[-1])
        self.tick_high = WaveTick(self.df.loc[self.df[CN.HIGH].idxmax(axis=0)])
        self.tick_low = WaveTick(self.df.loc[self.df[CN.LOW].idxmin(axis=0)])
        tick_helper = self.function_cont.tick_for_helper
        f_upper_first = self.function_cont.get_upper_value_for_position(self.tick_first.position)
        f_lower_first = self.function_cont.get_lower_value_for_position(self.tick_first.position)
        self.breadth_first = f_upper_first - f_lower_first
        if tick_helper is None:
            f_upper_last = self.function_cont.get_upper_value_for_position(self.tick_last.position)
            f_lower_last = self.function_cont.get_lower_value_for_position(self.tick_last.position)
        else:
            f_upper_last = self.function_cont.get_upper_value_for_position(tick_helper.position)
            f_lower_last = self.function_cont.get_lower_value_for_position(tick_helper.position)
        self.bound_upper = f_upper_last
        self.bound_lower = f_lower_last
        if self.pattern_type in [FT.TKE_DOWN, FT.TKE_UP]:
            self.breadth = round(self.bound_upper - self.bound_lower, 2)
        else:
            self.__distance_min = round(min(abs(f_upper_first - f_lower_first), abs(f_upper_last - f_lower_last)), 2)
            self.__distance_max = round(max(abs(f_upper_first - f_lower_first), abs(f_upper_last - f_lower_last)), 2)
            self.breadth = round((self.__distance_min + self.__distance_max)/2, 2)

    def __set_xy_parameter__(self):
        self.__xy = self.stock_df.get_xy_parameter(self.function_cont)

    def __set_xy_center__(self):
        self.__xy_center = self.stock_df.get_xy_center(self.function_cont.f_regression)

    def get_f_regression_shape(self):
        return self.stock_df.get_f_regression_shape(self.function_cont.f_regression)

    def get_f_upper_shape(self):
        return self.stock_df.get_f_upper_shape(self.function_cont)

    def get_f_lower_shape(self):
        return self.stock_df.get_f_lower_shape(self.function_cont)

    @property
    def xy(self):
        return self.__xy

    @property
    def xy_center(self):
        return self.__xy_center

    @property
    def movement(self):
        return abs(self.tick_high.high - self.tick_low.low)

    @property
    def date_first(self):
        return self.tick_first.date

    @property
    def date_first_str(self):
        return self.tick_first.date_str

    @property
    def date_last(self):
        return self.tick_last.date

    @property
    def date_last_str(self):
        return self.tick_last.date_str

    @property
    def ticks(self):
        return self.df.shape[0]

    @property
    def mean(self):
        return self.df[CN.MEAN_HL].mean()

    @property
    def std(self):  # we need the standard deviation from the mean_HL for Low and High
        return ((self.df[CN.HIGH]-self.mean).std() + (self.df[CN.LOW]-self.mean).std())/2

    def get_slope_values(self):
        f_upper_slope = round(self.function_cont.f_upper[1], 4)
        f_lower_slope = round(self.function_cont.f_lower[1], 4)
        relation_u_l = math.inf if f_lower_slope == 0 else round(f_upper_slope / f_lower_slope, 4)
        return f_upper_slope, f_lower_slope, relation_u_l

    def get_f_regression(self) -> np.poly1d:
        return self.stock_df.get_f_regression()

    def __get_text_for_annotation__(self, for_max: bool):
        f_regression = self.get_f_regression()
        reg_slope = round(f_regression[1], 3)
        std_dev = round(self.df[CN.CLOSE].std(), 2)
        f_upper_slope, f_lower_slope, relation_u_l = self.get_slope_values()

        type_date = 'Type={}: {} - {}'.format(self.pattern_type, self.tick_first.date_str, self.tick_last.date_str)

        if self.pattern_type == FT.TKE_UP:
            slopes = 'Slopes: L={}, Reg={}'.format(f_lower_slope, reg_slope)
            breadth = 'Breadth={}, Std_dev={}'.format(self.breadth, std_dev)
        elif self.pattern_type == FT.TKE_DOWN:
            slopes = 'Slopes: U={}, Reg={}'.format(f_upper_slope, reg_slope)
            breadth = 'Breadth={}, Std_dev={}'.format(self.breadth, std_dev)
        else:
            slopes = 'Slopes: U={}, L={}, U/L={}, Reg={}'.format(
                f_upper_slope, f_lower_slope, relation_u_l, reg_slope)
            breadth = 'Breadth={}, Max={}, Min={}, Std_dev={}'.format(
                self.breadth, self.__distance_max, self.__distance_min, std_dev)

        if self.breakout is None:
            breakout_str = 'Breakout: not yet'
        else:
            breakout_str = 'Breakout: {}'.format(self.breakout.get_details_for_annotations())

        return '{}\n{}\n{}\n{}'.format(type_date, slopes, breadth, breakout_str)

    def get_retracement_pct(self, comp_part):
        if self.tick_low.low > comp_part.tick_high.high:
            return 0
        intersection = abs(comp_part.tick_high.high - self.tick_low.low)
        return round(intersection/self.movement, 2)

    def are_values_below_linear_function(self, f_lin: np.poly1d, tolerance_pct: float = 0.01, column: CN = CN.HIGH):
        for ind, rows in self.df.iterrows():
            value_function = round(f_lin(rows[CN.DATEASNUM]), 2)
            tolerance_range = value_function * tolerance_pct
            if value_function + tolerance_range < rows[column]:
                return False
        return True

    def is_high_close_to_linear_function(self, f_lin: np.poly1d, tolerance_pct: float = 0.01):
        value_function = round(f_lin(self.tick_high.high), 2)
        mean = (value_function + self.tick_high.high)/2
        value = abs(self.tick_high.high - value_function)/mean
        return value < tolerance_pct

    def is_high_before_low(self):
        return self.tick_high.position < self.tick_low.position

    def print_data(self, part: str):
        print('\n{}: min={}, max={}, mean={}, std={} \n{}'.format(part, self.tick_low.low, self.tick_high.high
            , self.mean, self.std, self.df.head(self.ticks)))


class CountConstraint:
    def __init__(self, value_category: str, comparison: str, value: float):
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
    pattern_type = FT.ALL
    tolerance_pct = 0.01

    def __init__(self):
        self.global_all_in = []
        self.global_count = []
        self.global_series = []
        self.f_upper_slope_bounds = [-0.02, 0.02]
        self.f_lower_slope_bounds = [-0.02, 0.02]
        self.f_upper_lower_slope_bounds = [-5, 5]  # the relationship bounds for the linear functions increase
        self.f_regression_slope_bounds = [-0.02, 0.02]  # this constraint checks the "direction" of the data
        # [0.8, 1.2] Channel,
        self.__fill_global_constraints__()
        self.__set_bounds_for_pattern_type__()

    def are_f_lower_f_upper_compliant(self, f_lower: np.poly1d, f_upper: np.poly1d):
        if self.__is_f_lower_compliant__(f_lower):
            if self.__is_f_upper_compliant__(f_upper):
                return self.__is_relation_f_upper_f_lower_compliant__(f_upper, f_lower)
        return False

    def is_f_regression_compliant(self, f_regression: np.poly1d):
        return self.f_regression_slope_bounds[0] <= f_regression[1] <= self.f_regression_slope_bounds[1]

    def __is_f_lower_compliant__(self, f_lower: np.poly1d):
        if len(self.f_lower_slope_bounds) == 0:  # no lower bounds defined
            return True
        return self.f_lower_slope_bounds[0] <= f_lower[1] <= self.f_lower_slope_bounds[1]

    def __is_f_upper_compliant__(self, f_upper: np.poly1d):
        if len(self.f_upper_slope_bounds) == 0:  # no upper bounds defined
            return True
        return self.f_upper_slope_bounds[0] <= f_upper[1] <= self.f_upper_slope_bounds[1]

    def __is_relation_f_upper_f_lower_compliant__(self, f_upper: np.poly1d, f_lower: np.poly1d):
        if len(self.f_upper_lower_slope_bounds) == 0:  # no relation defined for both slopes
            return True
        if f_lower[1] == 0:
            return True
        return self.f_upper_lower_slope_bounds[0] <= (f_upper[1]/f_lower[1]) <= self.f_upper_lower_slope_bounds[1]

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_slope_bounds = [-100.0, 100]
        self.f_lower_slope_bounds = self.f_upper_slope_bounds
        self.f_upper_lower_slope_bounds = [-100, 100]

    def get_unary_constraints(self, df: pd.DataFrame):
        pass

    def get_binary_constraints(self, df: pd.DataFrame):
        pass

    def __fill_global_constraints__(self):
        pass

    @property
    def f_upper_slope_bounds_complementary(self):
        return [-1 * x for x in reversed(self.f_upper_slope_bounds)]

    @property
    def f_lower_slope_bounds_complementary(self):
        return [-1 * x for x in reversed(self.f_lower_slope_bounds)]

    @property
    def f_upper_lower_slope_bounds_complementary(self):
        if len(self.f_upper_lower_slope_bounds) == 0:
            return []
        return [round(1/x, 3) for x in reversed(self.f_upper_lower_slope_bounds)]

    def __set_bounds_by_complementary_constraints__(self, comp_constaints):
        self.f_upper_slope_bounds = comp_constaints.f_lower_slope_bounds_complementary
        self.f_lower_slope_bounds = comp_constaints.f_upper_slope_bounds_complementary
        self.f_upper_lower_slope_bounds = comp_constaints.f_upper_lower_slope_bounds_complementary


class TKEDownConstraints(Constraints):
    pattern_type = FT.TKE_DOWN

    def __fill_global_constraints__(self):
        """
        1. All values have to be in a range (channel)
        2. There must be at least 3 variables with domain value = SPD.U_in (incl the ticks for the f_upper)
        3. There must be at least 3 variables with domain value = SPD.L_in (incl the ticks for the f_lower)
        """
        self.global_all_in = [SVC.U_on, SVC.U_in, SVC.M_in, SVC.L_in, SVC.L_on, SVC.H_M_in]
        self.global_count = ['AND', CountConstraint(SVC.U_in, '>=', 3)]
        self.global_series = ['OR', [SVC.U_on, SVC.U_in, SVC.U_on], [SVC.U_on, SVC.U_on, SVC.U_on]]

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_slope_bounds = [-0.6, -0.3]
        self.f_lower_slope_bounds = []  # not required
        self.f_upper_lower_slope_bounds = []
        self.f_regression_slope_bounds = self.f_upper_slope_bounds


class TKEUpConstraints(Constraints):
    pattern_type = FT.TKE_UP

    def __fill_global_constraints__(self):
        """
        1. All values have to be in a range (channel)
        2. There must be at least 3 variables with domain value = SPD.U_in (incl the ticks for the f_upper)
        3. There must be at least 3 variables with domain value = SPD.L_in (incl the ticks for the f_lower)
        """
        self.global_all_in = [SVC.L_on, SVC.L_in, SVC.M_in, SVC.U_in, SVC.U_on, SVC.H_M_in]
        self.global_count = ['AND', CountConstraint(SVC.L_in, '>=', 3)]
        self.global_series = ['OR', [SVC.L_on, SVC.L_in, SVC.L_on], [SVC.L_on, SVC.L_on, SVC.L_on]]

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_slope_bounds = []  # not required
        self.f_lower_slope_bounds = [0.3, 0.6]
        self.f_upper_lower_slope_bounds = []
        self.f_regression_slope_bounds = self.f_lower_slope_bounds


class ChannelConstraints(Constraints):
    pattern_type = FT.CHANNEL

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

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_slope_bounds = [-0.03, 0.03]
        self.f_lower_slope_bounds = self.f_upper_slope_bounds
        self.f_upper_lower_slope_bounds = []
        self.f_regression_slope_bounds = self.f_upper_slope_bounds


class ChannelUpConstraints(ChannelConstraints):
    pattern_type = FT.CHANNEL_UP

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_slope_bounds = [0.03, 0.9]
        self.f_lower_slope_bounds = self.f_upper_slope_bounds
        self.f_upper_lower_slope_bounds = [0.8, 1.2]
        self.f_regression_slope_bounds = self.f_upper_slope_bounds


class ChannelDownConstraints(ChannelConstraints):
    pattern_type = FT.CHANNEL_DOWN

    def __set_bounds_for_pattern_type__(self):
        self.__set_bounds_by_complementary_constraints__(ChannelUpConstraints())


class HeadShoulderConstraints(Constraints):
    pattern_type = FT.HEAD_SHOULDER
    tolerance_pct = 0.01

    def __fill_global_constraints__(self):
        """
        1. All values have to be in a range (channel)
        2. There must be at least 3 variables with domain value = SPD.U_in (incl the ticks for the f_upper)
        3. There must be at least 3 variables with domain value = SPD.L_in (incl the ticks for the f_lower)
        """
        self.global_all_in = [SVC.L_on, SVC.L_in, SVC.M_in, SVC.U_in, SVC.U_on]
        self.global_count = ['AND', CountConstraint(SVC.U_in, '>=', 4), CountConstraint(SVC.L_in, '>=', 1)]
        self.global_series = ['OR', [SVC.U_on, SVC.M_in, SVC.U_on, SVC.L_on, SVC.U_on, SVC.M_in, SVC.U_on],
                              [SVC.U_on, SVC.M_in, SVC.U_in, SVC.L_on, SVC.M_in, SVC.M_in, SVC.U_on]]

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_slope_bounds = [-0.01, 0.01]
        self.f_lower_slope_bounds = self.f_upper_slope_bounds
        self.f_upper_lower_slope_bounds = [0.8, 1.1]
        self.f_regression_slope_bounds = [-0.03, 0.03]


class TriangleConstraints(ChannelConstraints):
    pattern_type = FT.TRIANGLE
    tolerance_pct = 0.01

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_slope_bounds = [-0.5, -0.1]
        self.f_lower_slope_bounds = [0.1, 0.5]
        self.f_upper_lower_slope_bounds = [-10, -0.2]
        self.f_regression_slope_bounds = [-0.1, 0.1]


class TriangleTopConstraints(TriangleConstraints):
    pattern_type = FT.TRIANGLE_TOP
    tolerance_pct = 0.01

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_slope_bounds = [-0.03, 0.03]
        self.f_lower_slope_bounds = [0.2, 1.0]
        self.f_upper_lower_slope_bounds = []
        self.f_regression_slope_bounds = self.f_lower_slope_bounds


class TriangleBottomConstraints(TriangleConstraints):
    pattern_type = FT.TRIANGLE_BOTTOM
    tolerance_pct = 0.01

    def __set_bounds_for_pattern_type__(self):
        self.__set_bounds_by_complementary_constraints__(TriangleTopConstraints())
        self.f_regression_slope_bounds = self.f_upper_slope_bounds


class TriangleUpConstraints(TriangleConstraints):
    pattern_type = FT.TRIANGLE_UP
    tolerance_pct = 0.01

    def __set_bounds_for_pattern_type__(self):
        self.f_upper_slope_bounds = [0.1, 1.0]
        self.f_lower_slope_bounds = self.f_upper_slope_bounds
        self.f_upper_lower_slope_bounds = [0.3, 0.65]
        self.f_regression_slope_bounds = self.f_upper_slope_bounds


class TriangleDownConstraints(TriangleConstraints):
    pattern_type = FT.TRIANGLE_DOWN
    tolerance_pct = 0.01

    def __set_bounds_for_pattern_type__(self):
        self.__set_bounds_by_complementary_constraints__(TriangleUpConstraints())
        self.f_regression_slope_bounds = self.f_upper_slope_bounds


class ConstraintsHelper:
    @staticmethod
    def get_constraints_for_pattern_type(pattern_type: str):
        if pattern_type == FT.CHANNEL:
            return ChannelConstraints()
        elif pattern_type == FT.CHANNEL_DOWN:
            return ChannelDownConstraints()
        elif pattern_type == FT.CHANNEL_UP:
            return ChannelUpConstraints()
        elif pattern_type == FT.HEAD_SHOULDER:
            return HeadShoulderConstraints()
        elif pattern_type == FT.TRIANGLE:
            return TriangleConstraints()
        elif pattern_type == FT.TRIANGLE_TOP:
            return TriangleTopConstraints()
        elif pattern_type == FT.TRIANGLE_BOTTOM:
            return TriangleBottomConstraints()
        elif pattern_type == FT.TRIANGLE_UP:
            return TriangleUpConstraints()
        elif pattern_type == FT.TRIANGLE_DOWN:
            return TriangleDownConstraints()
        elif pattern_type == FT.TKE_DOWN:
            return TKEDownConstraints()
        elif pattern_type == FT.TKE_UP:
            return TKEUpConstraints()
        else:
            raise MyException('No constraints defined for pattern type "{}"'.format(pattern_type))


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
    def __init__(self, function_cont: PatternFunctionContainer, constraints: Constraints ):
        self.function_cont = function_cont
        self.df = function_cont.df
        self.df_length = self.df.shape[0]
        self.__f_upper = function_cont.f_upper
        self.__f_lower = function_cont.f_lower
        self.__h_upper = function_cont.h_upper
        self.__h_lower = function_cont.h_lower
        self.value_category_dic = {}  # list of value categories by position of each entry
        self.__tolerance_pct = constraints.tolerance_pct
        self.__tolerance_pct_equal = 0.001
        self.__set_f_upper_f_lower_values__()
        self.__set_h_upper_h_lower_values__()
        self.__calculate_value_categories__()

    def are_all_values_above_f_lower(self, with_tolerance: bool = False) -> bool:  # TODO with_tolerance
        tolerance = self.df[CN.LOW].mean() * self.__tolerance_pct
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

    def print_data(self):
        print('\nValue categories for u=({}) and l=({}):'.format(self.__f_upper, self.__f_lower), end='\n')
        for ind, row in self.df.iterrows():
            tick = WaveTick(row)
            print('Pos: {}, Date: {}, H/L:{}/{}, Cat={}'.format(
                tick.position, tick.date_str, tick.high, tick.low, self.value_category_dic[tick.position]))

    def are_helper_functions_available(self):
        return self.__h_lower is not None and self.__h_upper is not None

    def __set_f_upper_f_lower_values__(self):
        self.df = self.df.assign(F_UPPER=(self.__f_upper(self.df[CN.POSITION])))
        self.df = self.df.assign(F_LOWER=(self.__f_lower(self.df[CN.POSITION])))

    def __set_h_upper_h_lower_values__(self):
        if self.are_helper_functions_available():
            self.df = self.df.assign(H_UPPER=(self.__h_upper(self.df[CN.POSITION])))
            self.df = self.df.assign(H_LOWER=(self.__h_lower(self.df[CN.POSITION])))

    def __calculate_value_categories__(self):
        for ind, row in self.df.iterrows():
            self.value_category_dic[row[CN.POSITION]] = self.__get_value_categories_for_df_row__(row)

    def __get_value_categories_for_df_row__(self, row) -> list:
        pass

    def __is_row_value_in_f_upper_range__(self, row):
        return abs(row[CN.HIGH] - row[CN.F_UPPER])/np.mean([row[CN.HIGH], row[CN.F_UPPER]]) <= self.__tolerance_pct

    def __is_row_value_in_f_lower_range__(self, row):
        return abs(row[CN.LOW] - row[CN.F_LOWER]) / np.mean([row[CN.LOW], row[CN.F_LOWER]]) <= self.__tolerance_pct

    def __is_row_value_between_f_lower_f_upper__(self, row):
        return row[CN.F_LOWER] < row[CN.LOW] <= row[CN.HIGH] < row[CN.F_UPPER]

    def __is_row_value_between_h_lower_h_upper__(self, row):
        return row[CN.H_LOWER] < row[CN.LOW] <= row[CN.HIGH] < row[CN.H_UPPER] and row[CN.CLOSE] > row[CN.F_UPPER]
        # the second condition is needed to get only the values which are in the tail of the TKE pattern.

    def __is_row_value_equal_f_upper__(self, row):
        return abs(row[CN.HIGH] - row[CN.F_UPPER]) / np.mean([row[CN.HIGH], row[CN.F_UPPER]]) \
               <= self.__tolerance_pct_equal

    def __is_row_value_larger_f_upper__(self, row):
        return row[CN.HIGH] > row[CN.F_UPPER] and not self.__is_row_value_in_f_upper_range__(row)

    def __is_row_value_smaller_f_upper__(self, row):
        return row[CN.HIGH] < row[CN.F_UPPER]

    def __is_row_value_equal_f_lower__(self, row):
        return abs(row[CN.LOW] - row[CN.F_LOWER]) / np.mean([row[CN.LOW], row[CN.F_LOWER]]) \
               <= self.__tolerance_pct_equal

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

        if self.are_helper_functions_available():
            if self.__is_row_value_between_h_lower_h_upper__(row):
                return_list.append(SVC.H_M_in)
        return return_list


class Pattern:
    def __init__(self, function_cont: PatternFunctionContainer, config: PatternConfiguration, constraints: Constraints):
        self.function_cont = function_cont
        self.pattern_type = function_cont.pattern_type
        self.ticks_initial = 0
        self.check_length = 0
        self.config = config
        self.constraints = constraints
        self.part_predecessor = None
        self.part_main = PatternPart(function_cont, config)
        self.__part_trade = None
        self.tolerance_pct = constraints.tolerance_pct
        self.condition_handler = PatternConditionHandler()
        self.xy = self.part_main.xy
        self.xy_center = self.part_main.xy_center
        self.xy_trade = None
        self.date_first = self.part_main.date_first
        self.date_last = self.part_main.date_last
        self.breakout = None
        self.trade_result = TradeResult()
        self.pattern_range = PatternRange

    def add_part_trade(self, part_trade: PatternPart):
        self.__part_trade = part_trade
        self.xy_trade = self.__part_trade.xy

    def was_breakout_done(self):
        return True if self.breakout.__class__.__name__ == 'PatternBreakout' else False

    def buy_after_breakout(self):
        if self.was_breakout_done() and self.breakout.is_breakout_a_signal():
            self.condition_handler.breakout_with_buy_signal = True
            return True
        return False

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
        return self.part_main.ticks

    def is_formation_established(self):  # this is the main check whether a formation is ready for a breakout
        return True

    def get_annotation_parameter(self, for_max: bool = True, color: str = 'blue'):
        return self.part_main.get_annotation_parameter(for_max, color)

    def get_shape_part_main(self):
        return Polygon(np.array(self.xy), True)

    def get_shape_part_trade(self):
        return Polygon(np.array(self.xy_trade), True)

    def get_center_shape(self):
        return Ellipse(np.array(self.xy_center), 4, 1)

    def fill_result_set(self):
        if self.is_part_trade_available():
            self.__fill_trade_result__()

    def is_part_trade_available(self):
        return self.__part_trade is not None

    def __fill_trade_result__(self):
        tolerance_range = self.part_main.breadth * self.constraints.tolerance_pct
        self.trade_result.expected_win = round(self.part_main.breadth, 2)
        self.trade_result.bought_at = round(self.breakout.tick_breakout.close, 2)
        self.trade_result.bought_on = self.breakout.tick_breakout.date
        self.trade_result.max_ticks = self.__part_trade.df.shape[0]
        if self.breakout_direction == FD.ASC:
            self.trade_result.stop_loss_at = self.part_main.bound_upper - tolerance_range
            self.trade_result.limit = self.part_main.bound_upper + self.trade_result.expected_win
        else:
            self.trade_result.stop_loss_at = self.part_main.bound_lower + tolerance_range
            self.trade_result.limit = self.part_main.bound_lower - self.trade_result.expected_win

        for ind, rows in self.__part_trade.df.iterrows():
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


class ChannelPattern(Pattern):
    pass  # TODO ChannelPattern


class ChannelUpPattern(ChannelPattern):
    pass  # TODO ChannelUpPattern


class ChannelDownPattern(ChannelPattern):
    pass  # TODO ChannelDownPattern


class HeadShoulderPattern(Pattern):
    pass  # TODO HeadShoulderPattern


class TrianglePattern(Pattern):
    pass  # TODO: Most triangles take their first tick (e.g. min) before the 3 ticks on the other side => enhance range


class TriangleBottomPattern(TrianglePattern):
    pass  # TODO: TriangleBottomPattern


class TriangleTopPattern(TrianglePattern):
    pass  # TODO: TriangleTopPattern


class TriangleUpPattern(TrianglePattern):
    pass  # TODO: TriangleUpPattern


class TriangleDownPattern(TrianglePattern):
    pass  # TODO: TriangleDownPattern


class TKEPattern(Pattern):
    def is_formation_established(self):  # this is the main check whether a formation is ready for a breakout
        return self.part_main.breadth / self.part_main.breadth_first < 0.4


class TKEDownPattern(TKEPattern):
    pass  # TODO: TKEDownPattern


class TKEUpPattern(TKEPattern):
    pass  # TODO: TKEUpPattern


class PatternHelper:
    @staticmethod
    def get_pattern_for_pattern_type(function_cont: PatternFunctionContainer, config: PatternConfiguration
                                     , constraints: Constraints):
        if function_cont.pattern_type == FT.CHANNEL:
            return ChannelPattern(function_cont, config, constraints)
        elif function_cont.pattern_type == FT.CHANNEL_DOWN:
            return ChannelDownPattern(function_cont, config, constraints)
        elif function_cont.pattern_type == FT.CHANNEL_UP:
            return ChannelUpPattern(function_cont, config, constraints)
        elif function_cont.pattern_type == FT.HEAD_SHOULDER:
            return HeadShoulderPattern(function_cont, config, constraints)
        elif function_cont.pattern_type == FT.TRIANGLE:
            return TrianglePattern(function_cont, config, constraints)
        elif function_cont.pattern_type == FT.TRIANGLE_TOP:
            return TriangleTopPattern(function_cont, config, constraints)
        elif function_cont.pattern_type == FT.TRIANGLE_BOTTOM:
            return TriangleBottomPattern(function_cont, config, constraints)
        elif function_cont.pattern_type == FT.TRIANGLE_UP:
            return TriangleUpPattern(function_cont, config, constraints)
        elif function_cont.pattern_type == FT.TRIANGLE_DOWN:
            return TriangleDownPattern(function_cont, config, constraints)
        elif function_cont.pattern_type == FT.TKE_DOWN:
            return TKEDownPattern(function_cont, config, constraints)
        elif function_cont.pattern_type == FT.TKE_UP:
            return TKEUpPattern(function_cont, config, constraints)
        else:
            raise MyException('No pattern defined for pattern type "{}"'.format(function_cont.pattern_type))


class StockDataFrame:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.tick_first = WaveTick(self.df.iloc[0])
        self.tick_last = WaveTick(self.df.iloc[-1])

    def get_f_upper_shape(self, function_cont: PatternFunctionContainer) -> Polygon:
        return self.__get_f_param_shape__(function_cont, True)

    def get_f_lower_shape(self, function_cont: PatternFunctionContainer) -> Polygon:
        return self.__get_f_param_shape__(function_cont, False)

    def __get_f_param_shape__(self, function_cont: PatternFunctionContainer, for_upper: bool) -> Polygon:
        if function_cont.tick_for_helper is None:
            tick_list = [self.tick_first, self.tick_last]
        else:
            tick_list = [self.tick_first, function_cont.tick_for_helper, self.tick_last]
        f = function_cont.get_upper_value_for_position if for_upper else function_cont.get_lower_value_for_position
        x = [tick.date_num for tick in tick_list]
        y = [f(tick.position) for tick in tick_list]
        xy = list(zip(x, y))
        return Polygon(np.array(xy), closed=False)

    def get_f_regression(self) -> np.poly1d:
        if self.df.shape[0] < 2:
            return np.poly1d([0, 0])
        np_array = np.polyfit(self.df[CN.POSITION], self.df[CN.CLOSE], 1)
        return np.poly1d([np_array[0], np_array[1]])

    def get_f_regression_shape(self, f_regression: np.poly1d = None) -> Polygon:
        if f_regression is None:
            f_regression = self.get_f_regression()
        x_date_num = [self.tick_first.date_num, self.tick_last.date_num]
        x = [self.tick_first.position, self.tick_last.position]
        y = [f_regression(value) for value in x]
        xy = list(zip(x_date_num, y))
        return Polygon(np.array(xy), True)

    def get_xy_parameter(self, function_cont: PatternFunctionContainer):
        tick_first, tick_last, tick_helper = self.tick_first, self.tick_last, function_cont.tick_for_helper
        f_upper = function_cont.f_upper
        f_lower = function_cont.f_lower
        h_upper = function_cont.h_upper
        h_lower = function_cont.h_lower
        f_upper_extended = function_cont.get_upper_value_for_position
        f_lower_extended = function_cont.get_lower_value_for_position

        if function_cont.tick_for_helper is None:
            tick_list = [tick_first, tick_first, tick_last, tick_last]
            function_list = [f_upper, f_lower, f_lower, f_upper]
        else:
            tick_helper = function_cont.tick_for_helper
            if function_cont.pattern_type == FT.TKE_UP:
                tick_list = [tick_first, tick_last, tick_last, tick_helper, tick_first]
                function_list = [h_upper, h_upper, h_lower, h_lower, f_lower]
            elif function_cont.pattern_type == FT.TKE_DOWN:
                tick_list = [tick_first, tick_helper, tick_last, tick_last, tick_first]
                function_list = [f_upper, h_upper, h_upper, f_lower, f_lower]
            else:
                tick_list = [tick_first, tick_helper, tick_last, tick_last, tick_first]
                if function_cont.pattern_direction == FD.ASC:
                    function_list = [f_upper_extended, f_upper_extended, f_upper_extended, f_lower, f_lower]
                else:
                    function_list = [f_lower_extended, f_lower_extended, f_lower_extended, f_upper, f_upper]

        x = [tick.date_num for tick in tick_list]
        y = [func(tick_list[ind].position) for ind, func in enumerate(function_list)]

        return list(zip(x, y))

    def get_xy_center(self, f_regression: np.poly1d = None):
        diff_position = self.tick_last.position - self.tick_first.position
        middle_position = self.tick_first.position + int(diff_position/2)
        tick = self.get_nearest_tick_to_position(middle_position)
        if f_regression is None:
            f_regression = self.get_f_regression()
        return tick.date_num, f_regression(tick.position)

    def get_nearest_tick_to_position(self, pos: int):
        df = self.df.assign(DistancePos=(abs(self.df.Position - pos)))
        df = df[df["DistancePos"] == df["DistancePos"].min()]
        return WaveTick(df.iloc[0])


class ExtendedDictionary4WaveTicks(ExtendedDictionary):
    def __init__(self, df: pd.DataFrame):
        ExtendedDictionary.__init__(self)
        self.df = df
        self.__process_df__()

    def __process_df__(self):
        for ind, rows in self.df.iterrows():
            tick = WaveTick(rows)
            self.append(tick.date_num, tick)


class PatternRange:
    def __init__(self, df_min_max: pd.DataFrame, df: pd.DataFrame, tick: WaveTick, min_length: int):
        self.df_min_max = df_min_max
        self.df = df  # to be processed
        self.tick_list = [tick]
        self.tick_first = tick
        self.tick_last = WaveTick(self.df_min_max.iloc[-1])
        self.tick_breakout_predecessor = None
        self.tick_breakout_successor =  None
        self.__min_length = min_length
        self.__f_param = None

    @property
    def length(self) -> int:
        return len(self.tick_list)

    @property
    def position_first(self) -> int:
        return self.tick_first.position

    @property
    def position_last(self) -> int:
        return self.tick_last.position

    @property
    def f_regression(self) -> np.poly1d:
        stock_df = StockDataFrame(self.__get_actual_df_min_max__())
        return stock_df.get_f_regression()

    def __get_actual_df_min_max__(self):
        df_range = self.df_min_max[np.logical_and(
            self.df_min_max[CN.POSITION] >= self.tick_first.position,
            self.df_min_max[CN.POSITION] <= self.tick_last.position)]
        return df_range

    @property
    def position_list(self) -> list:
        return self.__get_position_list__()

    def add_tick(self, tick: WaveTick, f_param):
        self.tick_list.append(tick)
        self.tick_last = tick
        self.__f_param = f_param

    @property
    def is_min_length_reached(self) -> bool:
        return self.length >= self.__min_length

    def is_covering_all_positions(self, pos_list_input: list) -> bool:
        return len(set(pos_list_input) & set(self.__get_position_list__())) == len(pos_list_input)

    def print_range_details(self):
        print(self.get_range_details())

    def get_range_details(self):
        position_list = self.__get_position_list__()
        value_list = self.__get_value_list__()
        breakout_predecessor = self.__get_breakout_details__(self.tick_breakout_predecessor, False)
        breakout_successor = self.__get_breakout_details__(self.tick_breakout_successor, True)
        date_str_list = self.__get_date_str_list__()
        return [position_list, value_list, breakout_predecessor, breakout_successor, date_str_list]

    def are_values_in_function_tolerance_range(self, f_param: np.poly1d, tolerance_pct: float) -> bool:
        for ticks in self.tick_list:
            v_1 = self.__get_value__(ticks)
            v_2 = f_param(ticks.position)
            if not ToleranceCalculator.are_values_in_tolerance_range(v_1, v_2, tolerance_pct):
                return False
        return True

    @property
    def f_param_shape(self):
        stock_df = StockDataFrame(self.__get_actual_df_min_max__())
        return stock_df.get_f_param_shape(self.__f_param)

    @property
    def f_regression_shape(self):
        stock_df = StockDataFrame(self.__get_actual_df_min_max__())
        return stock_df.get_f_regression_shape()

    def __get_position_list__(self) -> list:
        return [tick.position for tick in self.tick_list]

    def __get_value_list__(self) -> list:
        return [tick.high for tick in self.tick_list]

    def __get_date_str_list__(self) -> list:
        return [tick.date_str for tick in self.tick_list]

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
    def __init__(self, df_min_max: pd.DataFrame, constraints: Constraints):
        self.constraints = constraints
        self.df_min_max = df_min_max
        self.df = self.__get_df_for_processing__(df_min_max)
        self.df_length = self.df.shape[0]
        self._number_required_ticks = 3
        self.__tolerance_pct = constraints.tolerance_pct
        self.__pattern_range_list = []
        self.__parse_data_frame__()

    @property
    def pattern_range_list(self) -> list:
        return self.__pattern_range_list

    @property
    def pattern_range_detail_list(self) -> list:
        return [p.get_range_details() for p in self.__pattern_range_list]

    @property
    def pattern_range_shape_list(self) -> list:
        return [p.f_param_shape for p in self.__pattern_range_list]

    @property
    def pattern_range_regression_shape_list(self) -> list:
        return [p.f_regression_shape for p in self.__pattern_range_list]

    def print_list_of_possible_pattern_ranges(self):
        for pattern_range in self.__pattern_range_list:
            print(pattern_range.print_range_details())

    def are_pattern_ranges_available(self) -> bool:
        return len(self.__pattern_range_list) > 0

    def __get_df_for_processing__(self, df_min_max: pd.DataFrame):
        pass

    def __add_pattern_range_to_list_after_check__(self, pattern_range: PatternRange):
        if self.__are_conditions_fulfilled_for_adding_to_pattern_range_list__(pattern_range):
            self.__pattern_range_list.append(pattern_range)

    def __are_conditions_fulfilled_for_adding_to_pattern_range_list__(self, pattern_range: PatternRange) -> bool:
        if pattern_range is None:
            return False
        if not pattern_range.is_min_length_reached:
            return False
        if not self.constraints.is_f_regression_compliant(pattern_range.f_regression):
            return False
        for pattern_range_old in self.__pattern_range_list:  # check if this list is already a sublist of an earlier list
            if pattern_range_old.is_covering_all_positions(pattern_range.position_list):
                return False
        return True

    def __parse_data_frame__(self):
        for i in range(0, self.df_length - self._number_required_ticks):
            tick_i = WaveTick(self.df.iloc[i])
            pattern_range = self.__get_pattern_range_by_tick__(tick_i)
            for k in range(i+1, self.df_length):
                tick_k = WaveTick(self.df.iloc[k])
                if pattern_range.length == 1:  # start a new one if the values is above/below the old function
                    pattern_range.add_tick(tick_k, None)
                elif self.__is_end_for_single_check_reached__(pattern_range, tick_i, tick_k):
                    # TODO add tick_k as successor
                    pattern_range.tick_breakout_successor = tick_k
                    self.__add_pattern_range_to_list_after_check__(pattern_range)
                    pattern_range = self.__get_pattern_range_by_tick__(tick_i)
                    pattern_range.add_tick(tick_k, None)
            self.__add_pattern_range_to_list_after_check__(pattern_range)  # for the latest...

    def __get_linear_f_params__(self, tick_i: WaveTick, tick_k: WaveTick) -> np.poly1d:
        pass

    def __is_end_for_single_check_reached__(self, pattern_range: PatternRange, tick_i: WaveTick, tick_k: WaveTick):
        f_param_new = self.__get_linear_f_params__(tick_i, tick_k)
        if pattern_range.are_values_in_function_tolerance_range(f_param_new, self.__tolerance_pct):
            pattern_range.add_tick(tick_k, f_param_new)
        else:
            f_value_new_last_position_right = f_param_new(pattern_range.tick_last.position)
            if self.__is_new_tick_a_breakout__(pattern_range, f_value_new_last_position_right):
                return True
        return False

    def __is_new_tick_a_breakout__(self, f_value_new_last_position_right: float):
        pass

    def __get_pattern_range_by_tick__(self, tick: WaveTick):
        pass


class PatternRangeDetectorMax(PatternRangeDetector):
    def __get_df_for_processing__(self, df_min_max: pd.DataFrame):
        return df_min_max[df_min_max[CN.IS_MAX]]

    def __get_linear_f_params__(self, tick_i: WaveTick, tick_k: WaveTick) -> np.poly1d:
        return tick_i.get_linear_f_params_for_max(tick_k)

    def __is_new_tick_a_breakout__(self, pattern_range: PatternRange, f_value_new_last_position_right: float):
        return pattern_range.tick_last.high < f_value_new_last_position_right

    def __get_pattern_range_by_tick__(self, tick: WaveTick):
        return PatternRangeMax(self.df_min_max, self.df, tick, self._number_required_ticks)


class PatternRangeDetectorMin(PatternRangeDetector):
    def __get_df_for_processing__(self, df_min_max: pd.DataFrame):
        return df_min_max[df_min_max[CN.IS_MIN]]

    def __get_linear_f_params__(self, tick_i: WaveTick, tick_k: WaveTick) -> np.poly1d:
        return tick_i.get_linear_f_params_for_min(tick_k)

    def __is_new_tick_a_breakout__(self, pattern_range: PatternRange, f_value_new_last_position_right: float):
        return pattern_range.tick_last.low > f_value_new_last_position_right

    def __get_pattern_range_by_tick__(self, tick: WaveTick):
        return PatternRangeMin(self.df_min_max, self.df, tick, self._number_required_ticks)


class DataFrameFactory:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df_length = self.df.shape[0]
        self.__add_columns__()

    def __add_columns__(self):
        pass


class DataFramePlotterFactory(DataFrameFactory):
    """
    This class has two purposes:
    1. Identify all extrema: global and local maxima and minima which is used as checkpoint for pattern detections.
    2. Identify ranges which can be used for a thorough inspection in the further process
    """
    def __init__(self, df: pd.DataFrame):
        DataFrameFactory.__init__(self, df)
        self.__length_for_global = int(self.df_length / 2)
        self.__length_for_local = 3

    def __add_columns__(self):
        self.df = self.df.assign(Date=self.df.index.map(MyPyDate.get_date_from_datetime))
        self.df = self.df.assign(DateAsNumber=self.df.index.map(dt.date2num))
        self.df[CN.DATEASNUM] = self.df[CN.DATEASNUM].apply(int)
        self.df = self.df.assign(Position=self.df.index.map(self.df.index.get_loc))
        self.df[CN.POSITION] = self.df[CN.POSITION].apply(int)

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
        self.df = self.df.assign(Date=self.df.index.map(MyPyDate.get_date_from_datetime))
        self.df = self.df.assign(DateAsNumber=self.df.index.map(dt.date2num))
        self.df[CN.DATEASNUM] = self.df[CN.DATEASNUM].apply(int)
        self.df = self.df.assign(Position=self.df.index.map(self.df.index.get_loc))
        self.df[CN.POSITION] = self.df[CN.POSITION].apply(int)
        self.df.reset_index(drop=True, inplace=True)  # get position index

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
        self.pattern_type_list = list(config.pattern_type_list)
        self.df = df
        self.df_length = self.df.shape[0]
        self.df_min_max = df_min_max
        self.df_min_max_length = self.df_min_max.shape[0]
        self.constraints = None
        self.range_detector_max = PatternRangeDetectorMax
        self.range_detector_min = PatternRangeDetectorMin
        self.pattern_list = []

    @property
    def possible_pattern_ranges_available(self):
        return self.range_detector_max.are_pattern_ranges_available \
               or self.range_detector_min.are_pattern_ranges_available

    def parse_for_pattern(self):
        """
        We parse only over the actual known min-max-dataframe
        """
        for pattern_type in self.pattern_type_list:
            self.config.runtime.actual_pattern_type = pattern_type
            self.constraints = ConstraintsHelper.get_constraints_for_pattern_type(pattern_type)
            self.__fill_possible_pattern_ranges__()  # uses some constraints related parameters
            possible_pattern_range_list = self.__get_combined_possible_pattern_ranges__()
            for pattern_range in possible_pattern_range_list:
                df_check = self.df_min_max.loc[pattern_range.position_first:pattern_range.position_last]
                function_cont = self.__get_pattern_function_container_for_df__(pattern_type, df_check)
                if function_cont.is_valid():
                    breakout, pattern_end_passed = self.__get_breakout_after_checking_next_ticks__(function_cont)
                    if breakout is None and pattern_end_passed:
                        continue
                    self.config.runtime.actual_breakout = breakout
                    pattern = PatternHelper.get_pattern_for_pattern_type(function_cont, self.config, self.constraints)
                    if pattern.is_formation_established():
                        if breakout is not None:
                            pattern.breakout = breakout
                            function_cont.breakout_direction = breakout.breakout_direction
                            self.__add_part_trade__(pattern)
                        pattern.pattern_range = pattern_range
                        self.pattern_list.append(pattern)

    def __add_part_trade__(self, pattern: Pattern):
        if not pattern.was_breakout_done():
            return None
        df = self.__get_trade_df__(pattern)
        f_upper_trade = pattern.function_cont.f_upper_trade
        f_lower_trade = pattern.function_cont.f_lower_trade
        function_cont = PatternFunctionContainer(pattern.pattern_type, df, f_lower_trade, f_upper_trade)
        part = PatternPart(function_cont, self.config)
        pattern.add_part_trade(part)

    def __get_trade_df__(self, pattern: Pattern):
        left_pos = pattern.function_cont.tick_for_helper.position
        right_pos = pattern.function_cont.tick_last.position
        right_pos += right_pos - left_pos  # double length
        return self.df.loc[left_pos:min(right_pos, self.df_length)]

    def __get_breakout_after_checking_next_ticks__(self, function_cont: PatternFunctionContainer):
        confirmed_breakout = None
        tick_last = function_cont.tick_last
        pos_start = tick_last.position + 1
        number_of_positions = function_cont.number_of_positions
        counter = 0
        pattern_end_passed = False
        for pos in range(pos_start, self.df_length):
            counter += 1
            next_tick = WaveTick(self.df.loc[pos])
            break_loop = self.__check_for_break__(function_cont, counter, number_of_positions, next_tick)
            if break_loop:
                pattern_end_passed = True
                tick_last = next_tick
                break
            function_cont.adjust_functions_when_required(next_tick)
            if confirmed_breakout is None:
                confirmed_breakout = self.__get_confirmed_breakout__(function_cont, tick_last, next_tick)
            tick_last = next_tick
        function_cont.add_tick_from_main_df_to_df(self.df, tick_last)
        return confirmed_breakout, pattern_end_passed

    def __check_for_break__(self, function_cont, counter: int, number_of_positions: int, tick: WaveTick) -> bool:
        if counter > number_of_positions:  # maximal number for the whole pattern after its building
           return True
        if not function_cont.is_regression_value_in_pattern_for_position(tick.position):
            return True
        if not function_cont.is_tick_inside_pattern_range(tick):
            return True
        return False

    def __get_confirmed_breakout__(self, function_cont, last_tick: WaveTick, next_tick: WaveTick):
        if function_cont.is_tick_breakout(next_tick):
            breakout = self.__get_pattern_breakout__(function_cont, last_tick, next_tick)
            if breakout.is_breakout_a_signal():
                function_cont.set_tick_for_breakout(next_tick)
                return breakout
        return None

    def __get_pattern_breakout__(self, function_cont: PatternFunctionContainer, tick_previous: WaveTick
                                 , tick_breakout: WaveTick) -> PatternBreakout:
        breakout_api = PatternBreakoutApi(function_cont, self.config)
        breakout_api.tick_previous = tick_previous
        breakout_api.tick_breakout = tick_breakout
        breakout_api.constraints = self.constraints
        return PatternBreakout(breakout_api)

    def __get_pattern_function_container_for_df__(self, pattern_type: str, df_check: pd.DataFrame) \
            -> PatternFunctionContainer:
        df_min = df_check[df_check[CN.IS_MIN]]
        df_max = df_check[df_check[CN.IS_MAX]]
        if df_min.shape[0] == 0 or df_max.shape[0] == 0:
            return PatternFunctionContainer(pattern_type, df_check)
        l_tick = WaveTick(df_max.iloc[0])
        r_tick = WaveTick(df_max.iloc[-1])
        f_upper = math_functions.get_function_parameters(l_tick.position, l_tick.high, r_tick.position, r_tick.high)
        f_lower_list = self.__get_valid_f_lower_function_parameters__(pattern_type, df_min, f_upper)
        for f_lower in f_lower_list:
            function_container = PatternFunctionContainer(pattern_type, df_check, f_lower, f_upper)
            value_categorizer = ChannelValueCategorizer(function_container, self.constraints)
            if self.__is_global_constraint_all_in_satisfied__(df_check, value_categorizer):
                if self.__is_global_constraint_count_satisfied__(value_categorizer):
                    if self.__is_global_constraint_series_satisfied__(df_check, value_categorizer):
                        return function_container
        return PatternFunctionContainer(pattern_type, df_check)

    def __fill_possible_pattern_ranges__(self):
        self.range_detector_max = PatternRangeDetectorMax(self.df_min_max, self.constraints)
        # self.range_detector_max.print_list_of_possible_pattern_ranges()
        self.range_detector_min = PatternRangeDetectorMin(self.df_min_max, self.constraints)
        # TODO get rid of print statements

    def __get_combined_possible_pattern_ranges__(self) -> list:
        return self.range_detector_max.pattern_range_list

    def __get_valid_f_lower_function_parameters__(self, pattern_type: str, df_min: pd.DataFrame, f_upper: np.poly1d) -> list:
        if pattern_type == FT.HEAD_SHOULDER:
            f_lower = self.__get_parallel_to_upper_by_low__(df_min, f_upper)
            return [] if f_lower is None else [f_lower]
        elif pattern_type == FT.TKE_DOWN:
            f_lower = np.poly1d([0, df_min[CN.LOW].min()])
            return [f_lower] if self.constraints.are_f_lower_f_upper_compliant(f_lower, f_upper) else []

        if df_min.shape[0] < 2:
            return []

        poly1d_list = []

        for i in range(0, df_min.shape[0] - 1):
            for m in range(i + 1, df_min.shape[0]):
                left_tick = WaveTick(df_min.iloc[i])
                right_tick = WaveTick(df_min.iloc[m])
                f_lower = math_functions.get_function_parameters(left_tick.position, left_tick.low
                                                                 , right_tick.position, right_tick.low)
                if self.constraints.are_f_lower_f_upper_compliant(f_lower, f_upper):
                    function_cont = PatternFunctionContainer(self.constraints.pattern_type, df_min, f_lower, f_upper)
                    value_categorizer = ChannelValueCategorizer(function_cont, self.constraints)
                    if value_categorizer.are_all_values_above_f_lower():
                        poly1d_list.append(f_lower)
        return poly1d_list

    def __get_parallel_to_upper_by_low__(self, df_min: pd.DataFrame, f_upper: np.poly1d):
        pos_of_min = df_min[CN.LOW].idxmin()
        value_min = df_min[CN.LOW].min()
        diff = f_upper(pos_of_min) - value_min
        f_lower = np.poly1d([f_upper[1], f_upper[0] - diff])
        if self.constraints.are_f_lower_f_upper_compliant(f_lower, f_upper):
            return f_lower
        return None

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

    def __is_series_constraint_check_done__(self, series: list, df_check: pd.DataFrame, iloc: int, value_categorizer):
        if len(series) == 0:
            return True
        if iloc == df_check.shape[0]:
            return False
        if series[0] in value_categorizer.value_category_dic[df_check.iloc[iloc][CN.POSITION]]:
            series = series[1:]
        return self.__is_series_constraint_check_done__(series, df_check, iloc + 1, value_categorizer)

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
        return self.__get_formation_color__(formation), self.__get_trade_color__(formation)

    @staticmethod
    def __get_formation_color__(formation: Pattern):
        if formation.was_breakout_done():
            return 'green'
        else:
            return 'yellow'

    @staticmethod
    def __get_trade_color__(formation: Pattern):
        if formation.was_breakout_done():
            if formation.trade_result.actual_win > 0:
                return 'lime'
            else:
                return 'orangered'
        else:
            return 'white'


class PatternPlotContainer:
    border_line_top_color = 'green'
    border_line_bottom_color = 'red'
    regression_line_color = 'blue'
    center_color = 'blue'
    """
    Contains all plotting objects for one pattern
    """
    def __init__(self, polygon: Polygon, pattern_color: str):
        self.index_list = []
        self.shape_dic = {}
        self.pc_dic = {}
        self.color_dic = {}
        self.index_list.append('pattern')
        self.shape_dic['pattern'] = polygon
        self.color_dic['pattern'] = pattern_color
        self.annotation_param = None
        self.annotation = None

    def add_trade_shape(self, trade_shape, trade_color: str):
        self.index_list.append('trade')
        self.shape_dic['trade'] = trade_shape
        self.color_dic['trade'] = trade_color

    def add_border_line_top_shape(self, line_shape):
        self.index_list.append('top')
        self.shape_dic['top'] = line_shape
        self.color_dic['top'] = self.border_line_top_color

    def add_border_line_bottom_shape(self, line_shape):
        self.index_list.append('bottom')
        self.shape_dic['bottom'] = line_shape
        self.color_dic['bottom'] = self.border_line_top_color

    def add_regression_line_shape(self, line_shape):
        self.index_list.append('regression')
        self.shape_dic['regression'] = line_shape
        self.color_dic['regression'] = self.regression_line_color

    def add_center_shape(self, center_shape):
        self.index_list.append('center')
        self.shape_dic['center'] = center_shape
        self.color_dic['center'] = self.center_color

    def hide(self):
        self.__set_visible__(False, True)

    def show(self, with_annotation: bool):
        self.__set_visible__(True, with_annotation)

    def show_annotations(self):
        self.annotation.set_visible(True)

    def hide_annotations(self):
        self.annotation.set_visible(False)

    def __set_visible__(self, visible: bool, with_annotation: bool):
        self.annotation.set_visible(visible and with_annotation)
        for key in self.pc_dic:
            if key == 'center' and visible and with_annotation:
                self.pc_dic[key].set_visible(False)
            else:
                self.pc_dic[key].set_visible(visible)

    def add_annotation(self, axes):
        self.annotation = self.annotation_param.get_annotation(axes)

    def add_elements_as_patch_collection(self, axes):
        for keys in self.index_list:
            self.pc_dic[keys] = PatchCollection([self.shape_dic[keys]], alpha=0.4)
            if keys in ['top', 'bottom']:
                self.pc_dic[keys].set_color('None')
                self.pc_dic[keys].set_edgecolor(self.color_dic[keys])
            else:
                self.pc_dic[keys].set_color(self.color_dic[keys])

            axes.add_collection(self.pc_dic[keys])


class PatternPlotContainerLoopList(LoopList):
    def show_only_selected_containers(self, event):
        show_list = []
        self.__add_first_first_selected_center_pattern_to_show_list__(event, show_list)
        if len(show_list) == 0:
            self.__add_selected_pattern_to_show_list__(event, show_list)
        if len(show_list) == 0:
            for pattern_plot_container in self.value_list:
                pattern_plot_container.show(False)
        else:
            for pattern_plot_container in self.value_list:
                pattern_plot_container.hide()
            for pattern_plot_container in show_list:
                pattern_plot_container.show(True)
        event.canvas.draw()

    def __add_selected_pattern_to_show_list__(self, event, show_list: list):
        for pattern_plot_container in self.value_list:
            for collections_keys in pattern_plot_container.pc_dic:
                collection = pattern_plot_container.pc_dic[collections_keys]
                cont, dic = collection.contains(event)
                if cont:
                    show_list.append(pattern_plot_container)

    def __add_first_first_selected_center_pattern_to_show_list__(self, event, show_list: list):
        for pattern_plot_container in self.value_list:
            collection = pattern_plot_container.pc_dic['center']
            cont, dic = collection.contains(event)
            if cont:
                show_list.append(pattern_plot_container)
                break


class PatternPlotter:
    def __init__(self, api_object, detector: PatternDetector):
        self.api_object = api_object  # StockDatabaseDataFrame or AlphavantageStockFetcher
        self.api_object_class = self.api_object.__class__.__name__
        self.detector = detector
        self.config = self.detector.config
        self.df = DataFramePlotterFactory(api_object.df).df
        self.df_data = api_object.df_data
        self.column_data = api_object.column_data
        self.df_volume = api_object.df_volume
        self.column_volume = api_object.column_volume
        self.symbol = api_object.symbol
        self.pattern_plot_container_loop_list = PatternPlotContainerLoopList()
        self.axes = None
        self.tick_by_date_num_ext_dic = ExtendedDictionary4WaveTicks(self.df)
        # TODO ext dic

    def plot_data_frame(self):
        with_close_plot = False
        with_volume_plot = False

        if with_close_plot:
            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 10), sharex='all')
            self.__plot_close__(axes[0])
            self.__plot_candlesticks__(axes[1])
            self.__plot_patterns__(axes[1])
            self.__plot_volume__(axes[2])
        else:
            if with_volume_plot:
                fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 7), sharex='all')
                self.__plot_candlesticks__(axes[0])
                self.__plot_patterns__(axes[0])
                self.__plot_volume__(axes[1])
            else:
                fig, axes = plt.subplots(figsize=(15, 7))
                self.axes = axes
                self.__plot_candlesticks__(axes)
                self.__plot_patterns__(axes)

        plt.title('{}. {} ({}) for {}'.format(self.config.runtime.actual_number, self.config.runtime.actual_ticker
                            , self.config.runtime.actual_ticker_name, self.__get_date_range_for_title__()))
        plt.tight_layout()
        plt.xticks(rotation=45)
        fig.canvas.mpl_connect('button_press_event', self.__on_click__)
        self.axes.format_coord = self.__on_hover__
        plt.show()

    def __get_date_range_for_title__(self):
        tick_first = WaveTick(self.df.iloc[0])
        tick_last = WaveTick(self.df.iloc[-1])
        return 'Date between "{}" AND "{}"'.format(tick_first.date_str, tick_last.date_str)

    def __on_click__(self, event):
        self.pattern_plot_container_loop_list.show_only_selected_containers(event)

    def __on_hover__(self, x, y):
        tick = self.tick_by_date_num_ext_dic.get_value(int(x + 0.5))
        return '{} ({:3.0f}): [{:5.1f}; {:5.1f}]; vol={:8.0f}(t); y={:0.2f}'.format(
            tick.date_str, tick.position, tick.low, tick.high, tick.volume/1000, y)

    def __plot_close__(self, axis):
        plot_01 = self.df_data[[self.column_data]].plot(ax=axis)
        plot_01.legend(loc='upper left')

    def __plot_candlesticks__(self, axis):
        ohlc_list = []
        for ind, rows in self.df.iterrows():
            append_me = int(dt.date2num(ind)), rows[CN.OPEN], rows[CN.HIGH], rows[CN.LOW], rows[CN.CLOSE]
            ohlc_list.append(append_me)
        chart = candlestick_ohlc(axis, ohlc_list, width=0.4, colorup='g')
        axis.xaxis_date()
        axis.grid()
        # self.__add_fibonacci_waves__(axis)

    def __plot_patterns__(self, axis):
        self.__fill_plot_container_list__()
        self.__add_pattern_shapes_to_plot__(axis)

    def __plot_volume__(self, axis):
        self.df_volume.plot(ax=axis, title=self.column_volume)

    def __fill_plot_container_list__(self):
        color_handler = FormationColorHandler()
        for pattern in self.detector.pattern_list:
            color_pattern, color_trade = color_handler.get_colors_for_formation(pattern)
            plot_container = PatternPlotContainer(pattern.get_shape_part_main(), color_pattern)
            if pattern.was_breakout_done() and pattern.is_part_trade_available():
                plot_container.add_trade_shape(pattern.get_shape_part_trade(), color_trade)
            plot_container.add_center_shape(pattern.get_center_shape())
            plot_container.annotation_param = pattern.get_annotation_parameter(True, 'blue')
            # plot_container.add_border_line_top_shape(pattern.part_main.get_f_upper_shape())
            # plot_container.add_border_line_bottom_shape(pattern.part_main.get_f_lower_shape())
            plot_container.add_regression_line_shape(pattern.part_main.get_f_regression_shape())
            self.pattern_plot_container_loop_list.append(plot_container)

    def __add_pattern_shapes_to_plot__(self, ax):
        for pattern_plot_container in self.pattern_plot_container_loop_list.value_list:
            pattern_plot_container.add_elements_as_patch_collection(ax)
            pattern_plot_container.add_annotation(ax)


class PSC:  # Pattern Statistics Columns
    C_BOUND_UPPER_VALUE = 'conf.bound_upper_value'  # eg. CN.HIGH
    C_BOUND_LOWER_VALUE = 'conf.bound_lower_value'  # eg. CN.LOW
    C_CHECK_PREVIOUS_PERIOD = 'conf.check_previous_period'
    C_BREAKOUT_OVER_CONGESTION = 'conf.breakout_over_congestion_range'
    C_TOLERANCE_PCT = 'conf.tolerance in %'
    C_BREAKOUT_RANGE_PCT = 'conf.breakout range in %'
    C_AND_CLAUSE = 'conf.and clause'

    CON_PREVIOUS_PERIOD_CHECK_OK = FCC.PREVIOUS_PERIOD_CHECK_OK
    CON_COMBINED_PARTS_APPLICABLE = FCC.COMBINED_PARTS_APPLICABLE
    CON_BREAKOUT_WITH_BUY_SIGNAL = FCC.BREAKOUT_WITH_BUY_SIGNAL

    NUMBER = 'Number'
    STATUS = 'Status'
    TICKER = 'Ticker'
    NAME = 'Name'
    PATTERN = 'Pattern'
    BEGIN_PREVIOUS = 'Begin previous period'
    BEGIN = 'Begin'
    END = 'End'
    LOWER = 'Lower'
    UPPER = 'Upper'
    SLOPE_UPPER = 'Slope_upper'
    SLOPE_LOWER = 'Slope_lower'
    SLOPE_RELATION = 'Slope_relation'
    TICKS = 'Ticks'
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

        self.column_list.append(PSC.NUMBER)
        self.column_list.append(PSC.TICKER)
        self.column_list.append(PSC.NAME)
        self.column_list.append(PSC.STATUS)
        self.column_list.append(PSC.PATTERN)
        self.column_list.append(PSC.BEGIN_PREVIOUS)
        self.column_list.append(PSC.BEGIN)
        self.column_list.append(PSC.END)

        self.column_list.append(PSC.C_BOUND_UPPER_VALUE)
        self.column_list.append(PSC.C_BOUND_LOWER_VALUE)
        self.column_list.append(PSC.C_CHECK_PREVIOUS_PERIOD)
        self.column_list.append(PSC.C_BREAKOUT_OVER_CONGESTION)
        self.column_list.append(PSC.C_TOLERANCE_PCT)
        self.column_list.append(PSC.C_BREAKOUT_RANGE_PCT)
        self.column_list.append(PSC.C_AND_CLAUSE)

        self.column_list.append(PSC.CON_PREVIOUS_PERIOD_CHECK_OK)
        self.column_list.append(PSC.CON_COMBINED_PARTS_APPLICABLE)
        self.column_list.append(PSC.CON_BREAKOUT_WITH_BUY_SIGNAL)

        self.column_list.append(PSC.LOWER)
        self.column_list.append(PSC.UPPER)
        self.column_list.append(PSC.SLOPE_UPPER)
        self.column_list.append(PSC.SLOPE_LOWER)
        self.column_list.append(PSC.SLOPE_RELATION)
        self.column_list.append(PSC.TICKS)
        self.column_list.append(PSC.BREAKOUT_DATE)
        self.column_list.append(PSC.BREAKOUT_DIRECTION)
        self.column_list.append(PSC.VOLUME_CHANGE)
        self.column_list.append(PSC.EXPECTED)
        self.column_list.append(PSC.RESULT)
        self.column_list.append(PSC.EXT)
        self.column_list.append(PSC.VAL)
        self.column_list.append(PSC.BOUGHT_AT)
        self.column_list.append(PSC.SOLD_AT)
        self.column_list.append(PSC.BOUGHT_ON)
        self.column_list.append(PSC.SOLD_ON)
        self.column_list.append(PSC.T_NEEDED)

        self.column_list.append(PSC.LIMIT)
        self.column_list.append(PSC.STOP_LOSS_AT)
        self.column_list.append(PSC.STOP_LOSS_TRIGGERED)

        self.column_list.append(PSC.RESULT_DF_MAX)
        self.column_list.append(PSC.RESULT_DF_MIN)
        self.column_list.append(PSC.FIRST_LIMIT_REACHED)
        self.column_list.append(PSC.STOP_LOSS_MAX_REACHED)

        self.dic = {}

    def __init_dic__(self):
        for entries in self.column_list:
            self.dic[entries] = ''

    def add_entry(self, pattern: Pattern):
        self.__init_dic__()

        self.dic[PSC.C_BOUND_UPPER_VALUE] = pattern.config.bound_upper_value
        self.dic[PSC.C_BOUND_LOWER_VALUE] = pattern.config.bound_lower_value
        self.dic[PSC.C_CHECK_PREVIOUS_PERIOD] = pattern.config.check_previous_period
        self.dic[PSC.C_BREAKOUT_OVER_CONGESTION] = pattern.config.breakout_over_congestion_range
        self.dic[PSC.C_TOLERANCE_PCT] = pattern.tolerance_pct
        self.dic[PSC.C_BREAKOUT_RANGE_PCT] = pattern.config.breakout_range_pct
        self.dic[PSC.C_AND_CLAUSE] = pattern.config.and_clause

        self.dic[PSC.CON_PREVIOUS_PERIOD_CHECK_OK] = pattern.condition_handler.previous_period_check_ok
        self.dic[PSC.CON_COMBINED_PARTS_APPLICABLE] = pattern.condition_handler.combined_parts_applicable
        self.dic[PSC.CON_BREAKOUT_WITH_BUY_SIGNAL] = pattern.condition_handler.breakout_with_buy_signal

        self.dic[PSC.STATUS] = 'Finished' if pattern.was_breakout_done() else 'Open'
        self.dic[PSC.NUMBER] = pattern.config.runtime.actual_number
        self.dic[PSC.TICKER] = pattern.config.runtime.actual_ticker
        self.dic[PSC.NAME] = pattern.config.runtime.actual_ticker_name
        self.dic[PSC.PATTERN] = pattern.pattern_type
        self.dic[PSC.BEGIN_PREVIOUS] = 'TODO'
        self.dic[PSC.BEGIN] = MyPyDate.get_date_from_datetime(pattern.date_first)
        self.dic[PSC.END] = MyPyDate.get_date_from_datetime(pattern.date_last)
        self.dic[PSC.LOWER] = round(0, 2)
        self.dic[PSC.UPPER] = round(0, 2)  # TODO Lower & Upper bound for statistics
        self.dic[PSC.SLOPE_UPPER], self.dic[PSC.SLOPE_LOWER], self.dic[PSC.SLOPE_RELATION] \
            = pattern.part_main.get_slope_values()
        self.dic[PSC.TICKS] = pattern.part_main.ticks
        if pattern.was_breakout_done():
            self.dic[PSC.BREAKOUT_DATE] = MyPyDate.get_date_from_datetime(pattern.breakout.breakout_date)
            self.dic[PSC.BREAKOUT_DIRECTION] = pattern.breakout.breakout_direction
            self.dic[PSC.VOLUME_CHANGE] = pattern.breakout.volume_change_pct
            if pattern.is_part_trade_available():
                self.dic[PSC.EXPECTED] = pattern.trade_result.expected_win
                self.dic[PSC.RESULT] = pattern.trade_result.actual_win
                self.dic[PSC.VAL] = pattern.trade_result.formation_consistent
                self.dic[PSC.EXT] = pattern.trade_result.limit_extended_counter
                self.dic[PSC.BOUGHT_AT] = round(pattern.trade_result.bought_at, 2)
                self.dic[PSC.SOLD_AT] = round(pattern.trade_result.sold_at, 2)
                # self.dic[FSC.BOUGHT_ON] = MyPyDate.get_date_from_datetime(pattern.trade_result.bought_on)
                # self.dic[FSC.SOLD_ON] = MyPyDate.get_date_from_datetime(pattern.trade_result.sold_on)
                self.dic[PSC.T_NEEDED] = pattern.trade_result.actual_ticks
                self.dic[PSC.LIMIT] = round(pattern.trade_result.limit, 2)
                self.dic[PSC.STOP_LOSS_AT] = round(pattern.trade_result.stop_loss_at, 2)
                self.dic[PSC.STOP_LOSS_TRIGGERED] = pattern.trade_result.stop_loss_reached
                # if pattern.part_trade is not None:
                #     self.dic[FSC.RESULT_DF_MAX] = pattern.part_trade.max
                #     self.dic[FSC.RESULT_DF_MIN] = pattern.part_trade.min
                self.dic[PSC.FIRST_LIMIT_REACHED] = False  # default
                self.dic[PSC.STOP_LOSS_MAX_REACHED] = False  # default
                # if pattern.breakout_direction == FD.ASC \
                #         and (pattern.bound_upper + pattern.breadth < self.dic[FSC.RESULT_DF_MAX]):
                #     self.dic[FSC.FIRST_LIMIT_REACHED] = True
                # if pattern.breakout_direction == FD.DESC \
                #         and (pattern.bound_lower - pattern.breadth > self.dic[FSC.RESULT_DF_MIN]):
                #     self.dic[FSC.FIRST_LIMIT_REACHED] = True
                # if pattern.breakout_direction == FD.ASC \
                #         and (pattern.bound_lower > self.dic[FSC.RESULT_DF_MIN]):
                #     self.dic[FSC.STOP_LOSS_MAX_REACHED] = True
                # if pattern.breakout_direction == FD.DESC \
                #         and (pattern.bound_upper < self.dic[FSC.RESULT_DF_MAX]):
                #     self.dic[FSC.STOP_LOSS_MAX_REACHED] = True

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
            if pattern.was_breakout_done() and pattern.is_part_trade_available():
                result = pattern.trade_result
                self.counter_actual_ticks += result.actual_ticks
                self.counter_ticks += result.max_ticks
                self.counter_stop_loss = self.counter_stop_loss + 1 if result.stop_loss_reached else self.counter_stop_loss
                self.counter_formation_OK = self.counter_formation_OK + 1 if result.formation_consistent else self.counter_formation_OK
                self.counter_formation_NOK = self.counter_formation_NOK + 1 if not result.formation_consistent else self.counter_formation_NOK
                # traded_entities = int(self.investment_working / result.bought_at)
                traded_entities = 0
                self.investment_working = round(self.investment_working + (traded_entities * result.actual_win), 2)


class DetectorStatistics:
    def __init__(self):
        self.list = []
        self.column_list = ['Number', 'Ticker', 'Name', 'Investment', 'Result', 'Change%', 'SL', 'F_OK', 'F_NOK', 'Ticks']

    def add_entry(self, config: PatternConfiguration, api: PatternDetectorStatisticsApi):
        new_entry = [config.runtime.actual_number, config.runtime.actual_ticker, config.runtime.actual_ticker_name
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
        self.stock_db = None
        self.plotter_input_obj = None
        self.df_data = None
        self.__excel_file_with_test_data = ''
        self.df_test_data = None
        self.loop_list_ticker = None  # format of an entry (ticker, and_clause, number)
        self.__start_row = 0
        self.__end_row = 0

    def run_pattern_checker(self, excel_file_with_test_data: str = '', start_row: int = 1, end_row: int = 0):
        self.__init_db_and_test_data__(excel_file_with_test_data, start_row, end_row)
        self.__init_loop_list_for_ticker__()

        for value_dic in self.loop_list_ticker.value_list:
            ticker = value_dic[LL.TICKER]
            self.__add_runtime_parameter_to_config__(value_dic)
            print('\nProcessing {} ({})...\n'.format(ticker, self.config.runtime.actual_ticker_name))
            if config.get_data_from_db:
                and_clause = value_dic[LL.AND_CLAUSE]
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
                if len(detector.pattern_list) == 0: # and not detector.possible_pattern_ranges_available:
                    print('...no formations found.')
                else:
                    plotter = PatternPlotter(self.plotter_input_obj, detector)
                    plotter.plot_data_frame()
                    # plotter.plot_data_frame_with_mpl3()

            if value_dic[LL.NUMBER] >= self.config.max_number_securities:
                break

        if config.show_final_statistics:
            self.__show_statistics__()

    def __add_runtime_parameter_to_config__(self, entry_dic: dict):
        self.config.runtime.actual_ticker = entry_dic[LL.TICKER]
        self.config.runtime.actual_and_clause = entry_dic[LL.AND_CLAUSE]
        self.config.runtime.actual_number = entry_dic[LL.NUMBER]
        self.config.runtime.actual_ticker_name = self.config.ticker_dic[self.config.runtime.actual_ticker]

    def __show_statistics__(self):
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

    def __init_loop_list_for_ticker__(self):
        self.loop_list_ticker = LoopList4Dictionaries()
        if self.config.get_data_from_db and self.__excel_file_with_test_data != '':
            for ind, rows in self.df_test_data.iterrows():
                if self.loop_list_ticker.counter >= self.__start_row:
                    self.config.ticker_dic[rows[PSC.TICKER]] = rows[PSC.NAME]
                    start_date = MyPyDate.get_date_from_datetime(rows[PSC.BEGIN_PREVIOUS])
                    date_end = MyPyDate.get_date_from_datetime(rows[PSC.END] + timedelta(days=rows[PSC.T_FINAL] + 20))
                    and_clause = "Date BETWEEN '{}' AND '{}'".format(start_date, date_end)
                    self.loop_list_ticker.append({LL.TICKER: rows[PSC.TICKER], LL.AND_CLAUSE: and_clause})
                if self.loop_list_ticker.counter >= self.__end_row:
                    break
        else:
            for ticker in self.config.ticker_dic:
                self.loop_list_ticker.append({LL.TICKER: ticker, LL.AND_CLAUSE: self.config.and_clause})

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
config.pattern_type_list = FT.get_all()
# config.pattern_type_list = [FT.TKE_DOWN]
config.plot_data = True
config.statistics_excel_file_name = 'statistics_pattern.xlsx'
config.statistics_excel_file_name = ''
config.bound_upper_value = CN.CLOSE
config.bound_lower_value = CN.CLOSE
config.breakout_over_congestion_range = False
# config.show_final_statistics = True
config.max_number_securities = 1000
config.breakout_range_pct = 0.01  # default is 0.01
config.use_index(Indices.MIXED)
config.use_own_dic({"INTC": "American", "TSLA": "Teslat"})  # "INTC": "Intel",  "NKE": "Nike", "V": "Visa",  "GE": "GE", MRK (Merck)
# "FCEL": "FuelCell" "KO": "Coca Cola" # "BMWYY": "BMW" NKE	Nike, "CSCO": "Nike", "AXP": "American", "WMT": "Wall mart",
# config.and_clause = "Date BETWEEN '2017-10-25' AND '2018-04-18'"
config.and_clause = "Date BETWEEN '2017-01-25' AND '2019-02-18'"
# config.and_clause = ''
config.api_output_size = ApiOutputsize.COMPACT

pattern_controller = PatternController(config)
pattern_controller.run_pattern_checker('')

# Head Shoulder: GE Date BETWEEN '2017-01-25' AND '2019-10-30'
# Triangle: Processing KO (Coca Cola)...Date BETWEEN '2017-10-25' AND '2019-10-30'
