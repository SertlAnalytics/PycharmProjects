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
import ftplib
import tempfile


class CN:
    OPEN = 'Open'
    HIGH = 'High'
    LOW = 'Low'
    CLOSE = 'Close'
    MEAN_HL = 'MeanHL'
    VOL = 'Volume'
    DATE = 'Date'
    DATEASNUM = 'DateAsNumber'


class Indices:
    DOW_JONES = 'Dow Jones'
    NASDAQ = 'Nasdaq'
    MIXED = 'Mixed'


class FT:
    NONE = 'NONE'
    TRIANGLE = 'Triangle'
    CHANNEL = 'Channel'  # https://www.investopedia.com/articles/trading/05/020905.asp


class FD:
    NONE = 'NONE'
    HOR = 'horizontal'
    ASC = 'ascending'
    DESC = 'descending'


class FormationConfiguration:
    def __init__(self):
        self.get_data_from_db = True
        self.api_period = ApiPeriod.DAILY
        self.api_output_size = ApiOutputsize.COMPACT
        self.upper_bound_value = CN.HIGH
        self.lower_bound_value = CN.LOW
        self.plot_data = True
        self.max_length_of_a_formation_part = 10
        self.min_length_of_a_formation_part = 5
        self.breakout_over_upper_lower_range = False
        self.accuracy_pct = 0.01
        self.investment = 1000
        self.max_number_securities = 1000
        self.show_final_statitics = True
        self.and_clause = "Date BETWEEN '2017-12-01' AND '2019-12-31'"
        self.actual_ticker = ''
        self.actual_ticker_name = ''
        self.statistics_excel_file_name = ''
        self._ticker_dic = {}

    def print(self):
        source = 'DB' if self.get_data_from_db else 'Api'
        and_clause = self.and_clause
        period = self.api_period
        output_size = self.api_output_size
        upper_bound_v = self.upper_bound_value
        lower_bound_v = self.lower_bound_value
        max_part_length = self.max_length_of_a_formation_part
        min_part_length = self.min_length_of_a_formation_part
        breakout_over_big_range = self.breakout_over_upper_lower_range
        accuracy_pct = self.accuracy_pct

        print('\nConfiguration settings:')
        print('Source: {} \nAnd clause: {} \nApi period/ApiOutput size: {}/{} \nUpper/Lower Bound Value: {}/{}'
              ' \nMax/Min part length: {}/{} \nBreakout big range: {}  \nAccuracy: {} \n'.
              format(source, and_clause, period, output_size, upper_bound_v, lower_bound_v,
                     max_part_length, min_part_length, breakout_over_big_range, accuracy_pct))

    def use_index(self, index: Indices):
        if index == Indices.DOW_JONES:
            self._ticker_dic = self.dow_jones_dic
        elif index == Indices.NASDAQ:
            self._ticker_dic = self.nasdaq_dic
        else:
            self._ticker_dic = self.mixed_dic

    def use_own_dic(self, dic: dict):
        self._ticker_dic = dic

    @property
    def dow_jones_dic(self):
        return {"MMM": "3M", "AXP": "American", "AAPL": "Apple", "BA": "Boing",
                "CAT": "Caterpillar", "CVX": "Chevron", "CSCO": "Cisco", "KO": "Coca-Cola",
                "DIS": "Disney", "DWDP": "DowDuPont", "XOM": "Exxon", "GE": "General",
                "GS": "Goldman", "HD": "Home", "IBM": "IBM", "INTC": "Intel",
                "JNJ": "Johnson", "JPM": "JPMorgan", "MCD": "McDonald's", "MRK": "Merck",
                "MSFT": "Microsoft", "NKE": "Nike", "PFE": "Pfizer", "PG": "Procter",
                "TRV": "Travelers", "UTX": "United", "UNH": "UnitedHealth", "VZ": "Verizon",
                "V": "Visa", "WMT": "Wal-Mart"}

    @property
    def nasdaq_dic(self):
        """
        Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares
        AABA|Altaba Inc. - Common Stock|Q|N|N|100|N|N
        """
        dic = {}
        file_name = 'nasdaqlisted.txt'
        ftp = ftplib.FTP('ftp.nasdaqtrader.com', 'anonymous', 'josef.sertl@sertl-analytics.com')
        ftp.cwd('SymbolDirectory')
        with tempfile.TemporaryFile() as temp_file:
            ftp.retrbinary('RETR {}'.format(file_name), temp_file.write)
            temp_file.seek(0)
            df = pd.read_csv(temp_file, '|')
        ftp.quit()
        for ind, rows in df.iterrows():
            if rows['Market Category'] == 'Q':
                dic[rows['Symbol']] = rows['Security Name']
        return dic

    @property
    def mixed_dic(self):
        return {"TSLA": "Tesla", "FCEL": "Full Cell"}


class FormationDate:
    @staticmethod
    def get_date_from_datetime(date_time):
        return datetime.strptime(str(date_time), '%Y-%m-%d %H:%M:%S').date()


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

    def __get_bought_on(self):
        return self.__bought_on

    def __set_bought_on(self, value: datetime):
        self.__bought_on = value

    bought_on = property(__get_bought_on, __set_bought_on)

    def __get_sold_on(self):
        return self.__sold_on

    def __set_sold_on(self, value: datetime):
        self.__sold_on = value

    sold_on = property(__get_sold_on, __set_sold_on)

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
    def __init__(self, api: FormationBreakoutApi, config: FormationConfiguration):
        self.config = config
        self.formation_name = api.formation_name
        self.df = api.df
        self.candle_stick = self.__get_candle_stick_from_df__()
        self.breakout_date = self.candle_stick.Date
        self.candle_stick_previous = Candlestick(api.previous_tick.Open, api.previous_tick.High
                                , api.previous_tick.Low, api.previous_tick.Close, api.previous_tick.Volume)
        self.volume_change_pct = round(self.candle_stick.Volume/self.candle_stick_previous.Volume, 2)
        self.upper_bound = api.upper_bound
        self.lower_bound = api.lower_bound
        self.accuracy_range = api.accuracy_range
        self.formation_range = abs(self.upper_bound - self.lower_bound)
        self.breakout_direction = self.__get_breakout_direction__()
        self.sign = 1 if self.breakout_direction == FD.ASC else -1
        self.upper_limit = self.upper_bound + self.accuracy_range
        self.lower_limit = self.lower_bound - self.accuracy_range
        self.is_breakout_a_signal = self.__is_breakout_a_signal__()

    def __get_candle_stick_from_df__(self) -> Candlestick:
        date = self.df.first_valid_index()
        tick = self.df.iloc[0]
        return Candlestick(tick.Open, tick.High, tick.Low, tick.Close, tick.Volume, date)

    def __get_breakout_direction__(self) -> FD:
        return FD.ASC if self.candle_stick.Close > self.upper_bound else FD.DESC

    def __is_breakout_a_signal__(self) -> bool:
        is_breakout_over_limit = self.__is_breakout_over_limit__()
        is_breakout_in_allowed_range = True or self.__is_breakout_in_allowed_range__()
        is_volume_rising = self.candle_stick.is_volume_rising(self.candle_stick_previous, 10) # i.e. 10% more volume required
        is_breakout_powerfull = self.__is_breakout_powerfull__()

        return is_breakout_over_limit and is_volume_rising and is_breakout_powerfull \
               and is_breakout_in_allowed_range

    def __is_breakout_powerfull__(self) -> bool:
        return self.candle_stick.is_sustainable or self.candle_stick.has_gap_to(self.candle_stick_previous)

    def __is_breakout_over_limit__(self) -> bool:
        limit_range = self.formation_range if self.config.breakout_over_upper_lower_range else self.accuracy_range
        if self.breakout_direction == FD.ASC:
            return self.candle_stick.Close > self.upper_bound + limit_range
        else:
            return self.candle_stick.Close < self.lower_bound - limit_range

    def __is_breakout_in_allowed_range__(self) -> bool:
        if self.breakout_direction == FD.ASC:
            return self.candle_stick.Close < self.upper_bound + self.formation_range/2
        else:
            return self.candle_stick.Close > self.lower_bound - self.formation_range/2


class FormationPart:
    def __init__(self, df: pd.DataFrame, config: FormationConfiguration):
        self.df = df
        self.config = config
        self.__max_close = self.df[CN.CLOSE].max()
        self.__max_high = self.df[CN.HIGH].max()
        self.__id_max_high = self.df[CN.HIGH].idxmax(axis=0)
        self.__min_close = self.df[CN.CLOSE].min()
        self.__min_low = self.df[CN.LOW].min()
        self.__id_min_low = self.df[CN.LOW].idxmin(axis=0)
        self.__upper_bound = self.__max_high  # default
        self.__lower_bound = self.__min_low  # default
        self.__use_configuration_boundary_columns__()

    @property
    def ticks(self):
        return self.df.shape[0]

    @property
    def upper_bound(self):
        return self.__upper_bound

    @property
    def lower_bound(self):
        return self.__lower_bound

    @property
    def max_close(self):
        return self.__max_close

    @property
    def max_high(self):
        return self.__max_high

    @property
    def id_max_high(self):
        return self.__id_max_high

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
    def mean(self):
        return self.df[CN.MEAN_HL].mean()

    @property
    def std(self):  # we need the standard deviation from the mean_HL for Low and High
        return ((self.df[CN.HIGH]-self.mean).std() + (self.df[CN.LOW]-self.mean).std())/2

    def __use_configuration_boundary_columns__(self):
        if self.config.upper_bound_value == CN.CLOSE:
            self.__upper_bound = self.__max_close
        if self.config.lower_bound_value == CN.CLOSE:
            self.__lower_bound = self.__min_close

    def add_tick(self, tick_df: pd.DataFrame):
        self.df = pd.concat([self.df, tick_df])

    def print_data(self, part: str):
        print('\n{}: min={}, max={}, mean={}, std={} \n{}'.format(part, self.min_low, self.max_high, self.mean, self.std,
                                                                  self.df.head(self.ticks)))


class Formation:
    def __init__(self, df_start: pd.DataFrame, config: FormationConfiguration):
        self.config = config
        self.df_start = df_start
        self.df_final = None
        self.ticks_initial = self.df_start.shape[0]
        self.check_length = int(self.ticks_initial/3)
        self.part_left = FormationPart(self.df_start.iloc[0:self.check_length], self.config)
        self.part_middle = FormationPart(self.df_start.iloc[self.check_length:2 * self.check_length], self.config)
        self.part_right = FormationPart(self.df_start.iloc[2 * self.check_length:self.ticks_initial], self.config)
        self.accuracy_pct = self.config.accuracy_pct
        self.upper_bound = self.__get_upper_bound__()
        self.lower_bound = self.__get_lower_bound__()
        self.accuracy_range = self.mean * self.accuracy_pct
        self.upper_limit = self.upper_bound + self.accuracy_range
        self.lower_limit = self.lower_bound - self.accuracy_range
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
        return max(self.part_left.max_high, self.part_right.max_high)

    def __get_lower_bound__(self):
        return min(self.part_left.min_low, self.part_right.min_low)

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

    def __fill_trade_result__(self):
        self.trade_result.expected_win = round(self.upper_bound - self.lower_bound, 2)
        self.trade_result.bought_at = round(self.get_buying_price(), 2)
        self.trade_result.bought_on = self.breakout.df.first_valid_index()
        self.trade_result.max_ticks = self.control_df.shape[0]
        if self.breakout_direction == FD.ASC:
            self.trade_result.stop_loss_at = self.upper_bound - self.accuracy_range
            self.trade_result.limit = self.upper_bound + self.trade_result.expected_win
        else:
            self.trade_result.stop_loss_at = self.lower_bound + self.accuracy_range
            self.trade_result.limit = self.lower_bound - self.trade_result.expected_win
        self.trade_result.stop_loss_at = self.mean  # much more worse for TSLA....

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


class Channel(Formation):
    @property
    def type(self):
        return FT.CHANNEL

    @property
    def mean(self):
        return (self.part_left.mean + self.part_right.mean) / 2

    def __get_upper_bound__(self):
        return max(self.part_left.upper_bound, self.part_right.upper_bound)

    def __get_lower_bound__(self):
        return min(self.part_left.lower_bound, self.part_right.lower_bound)

    def is_formation_applicable(self):
        if self.are_left_right_parts_applicable_for_formation_type():
            return self.is_middle_part_applicable_for_formation_type()
        return False

    def is_passing_final_formation_check(self):
        is_max_distribution_compliant = True or self.__is_min_max_distribution_compliant__(True)
        is_min_distribution_compliant =  True or self.__is_min_max_distribution_compliant__(False)
        std_v = round(self.df_final[CN.HIGH].std(), 2)
        std_ok = std_v/(self.upper_bound - self.lower_bound) > 0.0  # this check doesn't bring the expected improvement
        return is_max_distribution_compliant and is_min_distribution_compliant

    def __is_min_max_distribution_compliant__(self, check_max: bool):
        if check_max:
            dist = self.df_final['Close'] > (self.upper_bound - self.accuracy_range)
        else:
            dist = self.df_final['Close'] < (self.lower_bound + self.accuracy_range)
        hit_counter = 0
        loop_counter = 0
        while loop_counter < dist.shape[0]:
            if dist.iloc[loop_counter]:
                hit_counter += 1
                loop_counter += int(self.ticks_initial/3)
            else:
                loop_counter += 1
        return True if hit_counter >= 3 else False

    def are_left_right_parts_applicable_for_formation_type(self):
        return  self.__is_part_applicable_for_formation_type__(self.part_left) and \
                self.__is_part_applicable_for_formation_type__(self.part_right)

    def is_middle_part_applicable_for_formation_type(self):
        return self.__is_part_applicable_for_formation_type__(self.part_middle)

    def __is_part_applicable_for_formation_type__(self, part: FormationPart):
        is_near_upper_bound = abs(part.max_high - self.upper_bound) / self.mean < self.accuracy_pct
        is_near_lower_bound = abs(part.min_low - self.lower_bound) / self.mean < self.accuracy_pct
        is_near_mean = True or abs(part.mean - self.mean) / self.mean < self.accuracy_pct
        return is_near_upper_bound and is_near_lower_bound and is_near_mean

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


class FormationStatistics:
    def __init__(self, config: FormationConfiguration):
        self.config = config
        self.list = []
        self.column_list = ['Status', 'Ticker', 'Name'
            , 'Formation', 'Lower', 'Upper', 'Begin', 'End', 'Ticks original', 'Ticks final'
            , 'Breakout date', 'Breakout direction', 'Volume change', 'Expected', 'Result', 'Extended', 'Validated'
            , 'Bought at', 'Sold at', 'Bought on', 'Sold on', 'Ticks needed']
        self.dic = {}

    def __init_dic__(self):
        for entries in self.column_list:
            self.dic[entries] = ''

    def add_entry(self, formation: Formation):
        self.__init_dic__()
        self.dic['Status'] = 'Finished' if formation.is_finished else 'Open'
        self.dic['Ticker'] = self.config.actual_ticker
        self.dic['Name'] = self.config.actual_ticker_name
        self.dic['Formation'] = formation.__class__.__name__
        self.dic['Lower'] = round(formation.lower_bound, 2)
        self.dic['Upper'] = round(formation.upper_bound, 2)
        self.dic['Begin'] = FormationDate.get_date_from_datetime(formation.date_first)
        self.dic['End'] = FormationDate.get_date_from_datetime(formation.date_last)
        self.dic['Ticks original'] = formation.ticks_initial
        self.dic['Ticks final'] = formation.ticks
        if formation.is_finished:
            self.dic['Breakout date'] = FormationDate.get_date_from_datetime(formation.breakout.breakout_date)
            self.dic['Breakout direction'] = formation.breakout.breakout_direction
            self.dic['Volume change'] = formation.breakout.volume_change_pct
            self.dic['Expected'] = formation.trade_result.expected_win
            self.dic['Result'] = formation.trade_result.actual_win
            self.dic['Validated'] = formation.trade_result.formation_consistent
            self.dic['Extended'] = formation.trade_result.limit_extended_counter
            self.dic['Bought at'] = formation.trade_result.bought_at
            self.dic['Sold at'] = formation.trade_result.sold_at
            self.dic['Bought on'] = FormationDate.get_date_from_datetime(formation.trade_result.bought_on)
            self.dic['Sold on'] = FormationDate.get_date_from_datetime(formation.trade_result.sold_on)
            self.dic['Ticks needed'] = formation.trade_result.actual_ticks

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
    def __init__(self, df: pd.DataFrame, config: FormationConfiguration):
        self.config = config
        self.df = df.assign(MeanHL=(df.High + df.Low) / 2)
        self.df[CN.DATEASNUM] = self.df.index.map(dt.date2num)
        self.df[CN.DATEASNUM] = self.df[CN.DATEASNUM].apply(int)
        self.part_ticks_max = self.config.max_length_of_a_formation_part
        self.part_ticks_min = self.config.min_length_of_a_formation_part
        self.accuracy_pct = self.config.accuracy_pct
        self.formation_dic = {}

    def parse_df(self):
        pos = 0
        max_pos = self.df.shape[0] - self.part_ticks_min * 3
        while pos < max_pos:
            pos = self.check_actual_position_for_valid_formation(pos)

    def check_actual_position_for_valid_formation(self, pos):
        part_ticks = self.part_ticks_max
        while part_ticks >= self.part_ticks_min:  # try different lengths of the 3 parts of the formation
            ticks = part_ticks * 3
            part_ticks -= 1
            if pos + ticks < self.df.shape[0]:
                formation = Channel(self.df.iloc[pos:pos + ticks], self.config)
                if formation.is_formation_applicable():
                    self.add_new_ticks_to_formation(formation, pos, pos + ticks + 1)
                    formation.finalize()
                    return self.get_next_pos_after_conditional_add_to_dictionary(formation, pos)
        return pos + 1

    def add_new_ticks_to_formation(self, formation, pos, pos_new_tick):
        continue_loop = True
        while continue_loop and pos_new_tick <= self.df.shape[0]:
            tick_df = self.df.iloc[pos_new_tick - 1:pos_new_tick]
            continue_loop = formation.is_tick_fitting_to_formation(tick_df)
            if continue_loop:
                formation.add_tick_to_formation(tick_df)
                pos_new_tick += 1
            else:
                formation.breakout = FormationBreakout(self.__get_breakout_api__(formation, tick_df), self.config)
                left_boundary = pos_new_tick
                if left_boundary < self.df.shape[0]:
                    right_boundary = min(left_boundary + formation.ticks, self.df.shape[0])
                    formation.control_df = self.df.iloc[left_boundary:right_boundary]

    def get_next_pos_after_conditional_add_to_dictionary(self, formation, pos):
        if formation.buy_at_breakout or not formation.is_finished:
            self.formation_dic[pos] = formation
            return pos + formation.ticks * 2 + 1  # no other formation check in the control period
        return pos + formation.ticks + 1

    @staticmethod
    def __get_breakout_api__(formation: Formation, tick_df: pd.DataFrame):
        api = FormationBreakoutApi(formation.__class__.__name__)
        api.df = tick_df
        api.previous_tick = formation.part_right.df.loc[formation.part_right.df.last_valid_index()]
        api.upper_bound = formation.upper_bound
        api.lower_bound = formation.lower_bound
        api.accuracy_range = formation.accuracy_range
        api.mean = formation.mean
        return api

    def print_statistics(self):
        api = self.get_statistics_api()
        print('Investment change: {} -> {}, Diff: {}%'.format(api.investment_start, api.investment_working, api.diff_pct))
        print('counter_stop_loss = {}, counter_formation_OK = {}, counter_formation_NOK = {}, ticks = {}'.format(
            api.counter_stop_loss, api.counter_formation_OK, api.counter_formation_NOK, api.counter_actual_ticks
        ))

    def get_statistics_api(self):
        return FormationDetectorStatisticsApi(self.formation_dic, self.config.investment)


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
    def __init__(self, api_object, detector: FormationDetector):
        self.api_object = api_object  # StockDatabaseDataFrame or AlphavantageStockFetcher
        self.config = config
        self.api_object_class = self.api_object.__class__.__name__
        self.part_ticks_max = self.config.max_length_of_a_formation_part
        self.accuracy_pct = self.config.accuracy_pct
        self.df = api_object.df
        self.df_data = api_object.df_data
        self.column_data = api_object.column_data
        self.df_volume = api_object.df_volume
        self.column_volume = api_object.column_volume
        self.symbol = api_object.symbol
        self.detector = detector

    def plot_data_frame(self):
        with_close_plot = False

        if with_close_plot:
            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 10), sharex=True)
            self.__plot_close__(axes[0])
            self.__plot_candlesticks__(axes[1])
            self.__plot_volume__(axes[2])
        else:
            fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 7), sharex=True)
            self.__plot_candlesticks__(axes[0])
            self.__plot_volume__(axes[1])

        plt.title(self.symbol)
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

    def __plot_volume__(self, axis):
        self.df_volume.plot(ax=axis, title=self.column_volume)

    def add_formations(self, ax):
        color_handler = FormationColorHandler()
        patches_dic = {}
        for ind in self.detector.formation_dic:
            formation = self.detector.formation_dic[ind]
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


class DetectorStatistics:
    def __init__(self):
        self.list = []
        self.column_list = ['Ticker', 'Name', 'Investment', 'Result', 'Change%', 'SL', 'F_OK', 'F_NOK', 'Ticks']

    def add_entry(self, ticker, name, api: FormationDetectorStatisticsApi):
        new_entry = [ticker, name, api.investment_start, api.investment_working, api.diff_pct,
                     api.counter_stop_loss, api.counter_formation_OK, api.counter_formation_NOK, api.counter_actual_ticks]
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


class FormationController:
    def __init__(self, config: FormationConfiguration):
        self.config = config
        self.detector_statistics = DetectorStatistics()
        self.formation_statistics = FormationStatistics(self.config)
        self.stock_db = stock_database.StockDatabase
        self.plotter_input_obj = None
        self.df_data = None

    def run_formation_checker(self):
        if config.get_data_from_db:
            self.stock_db = stock_database.StockDatabase()

        counter = 0
        for ticker in self.config._ticker_dic:
            self.config.actual_ticker = ticker
            self.config.actual_ticker_name = self.config._ticker_dic[ticker]
            print('\nProcessing {} ({})...\n'.format(ticker, self.config.actual_ticker_name))
            if config.get_data_from_db:
                stock_db_df_obj = stock_database.StockDatabaseDataFrame(self.stock_db, ticker, self.config.and_clause)
                self.plotter_input_obj = stock_db_df_obj
                self.df_data = stock_db_df_obj.df_data
            else:
                fetcher = AlphavantageStockFetcher(ticker, self.config.api_period, self.config.api_output_size)
                self.plotter_input_obj = fetcher
                self.df_data = fetcher.df_data

            detector = FormationDetector(self.df_data, self.config)
            detector.parse_df()
            self.__handle_statistics__(detector)

            if self.config.plot_data:
                if len(detector.formation_dic) == 0:
                    print('...no formations found.')
                else:
                    plotter = FormationPlotter(self.plotter_input_obj, detector)
                    plotter.plot_data_frame()

            counter += 1
            if counter >= self.config.max_number_securities:
                break

        if config.show_final_statitics:
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

    def __handle_statistics__(self, detector: FormationDetector):
        for keys in detector.formation_dic:
            self.formation_statistics.add_entry(detector.formation_dic[keys])

        if config.show_final_statitics:
            self.detector_statistics.add_entry(self.config.actual_ticker, self.config.actual_ticker_name
                                               , detector.get_statistics_api())
        else:
            detector.print_statistics()


config = FormationConfiguration()
config.get_data_from_db = False
config.plot_data = True
config.statistics_excel_file_name = 'statistics.xlsx'
config.statistics_excel_file_name = ''
config.upper_bound_value = CN.CLOSE
config.lower_bound_value = CN.CLOSE
config.breakout_over_upper_lower_range = False
config.show_final_statitics = True
config.max_number_securities = 20
config.use_index(Indices.NASDAQ)
config.use_own_dic({"ACGLP": "Disney"})
config.and_clause = "Date BETWEEN '2010-03-07' AND '2019-04-17'"
# config.and_clause = ''
config.api_output_size = ApiOutputsize.COMPACT

formation_controller = FormationController(config)
formation_controller.run_formation_checker()

"""
DIS	Disney
JPM	JPMorgan
"""






