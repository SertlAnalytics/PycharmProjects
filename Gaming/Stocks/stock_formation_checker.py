"""
Description: This module fetch data from any source. Transforms them into pd.DataFrame and plots them.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, ApiPeriod, ApiOutputsize
from stock_database.stock_database import stock_database
from mpl_finance import candlestick_ohlc
import matplotlib.dates as dt
from matplotlib.patches import Polygon, Arrow
from matplotlib.collections import PatchCollection
from datetime import datetime, timedelta
import ftplib
import tempfile
from sertl_analytics.datafetcher.database_fetcher import DatabaseDataFrame
from stock_database import stock_database as sdb


class CN:
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


class Indices:
    DOW_JONES = 'Dow Jones'
    NASDAQ = 'Nasdaq'
    MIXED = 'Mixed'
    ALL_DATABASE = 'All in database'


class FT:
    NONE = 'NONE'
    TRIANGLE = 'Triangle'
    CHANNEL = 'Channel'  # https://www.investopedia.com/articles/trading/05/020905.asp
    TKE = 'Trend correction extrema'


class FD:
    NONE = 'NONE'
    HOR = 'horizontal'
    ASC = 'ascending'
    DESC = 'descending'


class FCC:  # Formation Condition Columns
    BREAKOUT_WITH_BUY_SIGNAL = 'breakout had a buy signal'
    PREVIOUS_PERIOD_CHECK_OK = 'previous period check OK'  # eg. CN.LOW
    COMBINED_PARTS_APPLICABLE = 'combined parts are formation applicable'


class FormationConfiguration:
    def __init__(self):
        self.get_data_from_db = True
        self.formation_type = FT.TKE
        self.api_period = ApiPeriod.DAILY
        self.api_output_size = ApiOutputsize.COMPACT
        self.bound_upper_value = CN.HIGH
        self.bound_lower_value = CN.LOW
        self.plot_data = True
        self.max_length_of_a_formation_part = 10
        self.min_length_of_a_formation_part = 5
        self.check_previous_period = False   # default
        self.__previous_period_length = self.max_length_of_a_formation_part  # default
        self.breakout_over_congestion_range = False
        self.accuracy_pct = 0.05  # the high/low values can be this percentage over the upper bounds w.r.t breadth
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
        type = self.formation_type
        and_clause = self.and_clause
        period = self.api_period
        output_size = self.api_output_size
        bound_upper_v = self.bound_upper_value
        bound_lower_v = self.bound_lower_value
        max_part_length = self.max_length_of_a_formation_part
        min_part_length = self.min_length_of_a_formation_part
        breakout_over_big_range = self.breakout_over_congestion_range
        accuracy_pct = self.accuracy_pct

        print('\nConfiguration settings:')
        if self.get_data_from_db:
            print('Formation: {} \nSource: {} \nAnd clause: {} \nUpper/Lower Bound Value: {}/{}'
                  ' \nMax/Min part length: {}/{} \nBreakout big range: {}  \nAccuracy: {} \n'.format(
                type, source, and_clause, bound_upper_v, bound_lower_v
                , max_part_length, min_part_length, breakout_over_big_range, accuracy_pct))
        else:
            print('Formation: {} \nSource: {} \n\nApiPeriod/ApiOutput size: {}/{} \nUpper/Lower Bound Value: {}/{}'
                  ' \nMax/Min part length: {}/{} \nBreakout big range: {}  \nAccuracy: {} \n'.format(
                type, source, period, output_size, bound_upper_v, bound_lower_v
                , max_part_length, min_part_length, breakout_over_big_range, accuracy_pct))

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

    @staticmethod
    def get_mixed_dic():
        return {"TSLA": "Tesla", "FCEL": "Full Cell", "ONVO": "Organovo", "MRAM": "MRAM"}

    def get_all_in_database(self):
        dic = {}
        stock_db = sdb.StockDatabase()
        db_data_frame = DatabaseDataFrame(stock_db, query='SELECT Symbol, count(*) FROM Stocks GROUP BY Symbol HAVING count(*) > 4000')
        for ind, rows in db_data_frame.df.iterrows():
            dic[rows['Symbol']] = rows['Symbol']
        return dic


class FormationRange:
    def __init__(self, start_date, end_date, min_value: float, max_value: float):
        self.date_start = FormationDate.get_date_from_datetime(start_date)
        self.date_start_num = dt.date2num(self.date_start)
        self.date_end = FormationDate.get_date_from_datetime(end_date)
        self.date_end_num = dt.date2num(self.date_end)
        self.min = round(min_value, 2)
        self.max = round(max_value, 2)
        self.range = self.max - self.min

    def is_tick_fitting_to_range(self, tick):
        if self.min <= tick[CN.CLOSE] <= self.max:
            if self.date_start_num <= tick[CN.DATEASNUM] <= self.date_end_num:
                return True
        return False

    def plot_annotation(self, ax, for_max: bool = True, color: str = 'green'):
        x = self.date_start_num
        y = self.max if for_max else self.min
        text = '{}: {}'.format(self.date_start, y)
        offset_x = 0
        offset_y = self.range + y/10
        offset = [offset_x, offset_y] if for_max else [-offset_x, -offset_y]
        arrow_props = {'color': color, 'width': 0.2, 'headwidth': 4}
        ax.annotate(text, xy=(x, y), xytext=(x + offset[0], y + offset[1]), arrowprops=arrow_props)

    def print(self):
        print('{} until {}, min/max={}/{}'.format(self.date_start, self.date_end, self.min, self.max))


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


class FormationDate:
    @staticmethod
    def get_date_from_datetime(date_time):
        if date_time.__class__.__name__ == 'date':  # no change
            return date_time
        return datetime.strptime(str(date_time), '%Y-%m-%d %H:%M:%S').date()

    @staticmethod
    def get_date_from_number(num: int):
        return datetime(1, 1, 1) + timedelta(days=num)


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


class Movement:
    def __init__(self):
        self.df = pd.DataFrame
        self.min = 0
        self.max = 0
        self.date_begin = None
        self.date_end = None
        self.direction = FD.NONE
        self.tick_list = []

    @property
    def ticks(self):
        return len(self.tick_list)

    def add_tick(self, tick):
        self.tick_list.append(tick)


class WaveTick:
    def __init__(self, tick):
        self.tick = tick

    @property
    def date(self):
        return self.tick[CN.DATE]

    @property
    def position(self):
        return self.tick[CN.POSITION]

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


class WaveParser:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df_length = self.df.shape[0]
        self.length_for_global = int(self.df_length / 2)
        self.length_for_local = 3
        self.wave_tick_list = []
        self.wave_max_tick_list = []
        self.wave_min_tick_list = []
        self.__init_columns_for_ticks_distance__()
        self.__fill_wave_tick_lists__()

    def get_wave_tick_for_position(self, pos: int) -> WaveTick:
        return self.wave_tick_list[pos]

    def get_xy_max_parameter(self):
        return self.__get_xy_parameter__(False)

    def get_xy_min_parameter(self):
        return self.__get_xy_parameter__(True)

    def get_max_tick_list_for_range(self, pos_start: int, limit_value: float):
        return self.__get_tick_list_for_range__(pos_start, limit_value, True)

    def get_min_tick_list_for_range(self, pos_start: int, limit_value: float):
        return self.__get_tick_list_for_range__(pos_start, limit_value, False)

    def __get_xy_parameter__(self, is_min: bool):
        if is_min:
            df_global = self.df[self.df[CN.LOCAL_MIN]]
            col = CN.LOW
        else:
            df_global = self.df[self.df[CN.LOCAL_MAX]]
            col = CN.HIGH
        x = df_global[CN.DATEASNUM]
        y = df_global[col]
        return list(zip(x,y))

    def __get_tick_list_for_range__(self, pos_start: int, limit_value: float, is_max: bool):
        source_list = self.wave_max_tick_list if is_max else self.wave_min_tick_list
        wave_tick_list_return = []
        for ticks in source_list:
            if ticks.position > pos_start:
                if (is_max and ticks.high > limit_value) or (not is_max and ticks.low < limit_value):
                    break
                else:
                    wave_tick_list_return.append(ticks)
        return wave_tick_list_return

    def __init_columns_for_ticks_distance__(self):
        self.__add_distance_columns__()
        self.__add_min_max_columns__()

    def __fill_wave_tick_lists__(self):
        for ind, rows in self.df.iterrows():
            wave_tick = WaveTick(rows)
            self.wave_tick_list.append(wave_tick)
            if wave_tick.is_local_max:
                self.wave_max_tick_list.append(wave_tick)
            elif wave_tick.is_local_min:
                self.wave_min_tick_list.append(wave_tick)

    def __add_distance_columns__(self):
        for high in (False, True):
            for before in (False, True):
                value_list = []
                for ind, rows in self.df.iterrows():
                    value_list.append(self.__get_distance__(rows, high, before))
                if high and before:
                    self.df[CN.TICKS_BREAK_HIGH_BEFORE] = value_list
                elif high and not before:
                    self.df[CN.TICKS_BREAK_HIGH_AFTER] = value_list
                elif not high and before:
                    self.df[CN.TICKS_BREAK_LOW_BEFORE] = value_list
                elif not high and not before:
                    self.df[CN.TICKS_BREAK_LOW_AFTER] = value_list

    def __add_min_max_columns__(self):
        self.df[CN.GLOBAL_MIN] = np.logical_and(self.df[CN.TICKS_BREAK_LOW_AFTER] > self.length_for_global
                                                , self.df[CN.TICKS_BREAK_LOW_BEFORE] > self.length_for_global)
        self.df[CN.GLOBAL_MAX] = np.logical_and(self.df[CN.TICKS_BREAK_HIGH_AFTER] > self.length_for_global
                                                , self.df[CN.TICKS_BREAK_HIGH_BEFORE] > self.length_for_global)
        self.df[CN.LOCAL_MIN] = np.logical_and(self.df[CN.TICKS_BREAK_LOW_AFTER] > self.length_for_local
                                               , self.df[CN.TICKS_BREAK_LOW_BEFORE] > self.length_for_local)
        self.df[CN.LOCAL_MAX] = np.logical_and(self.df[CN.TICKS_BREAK_HIGH_AFTER] > self.length_for_local
                                               , self.df[CN.TICKS_BREAK_HIGH_BEFORE] > self.length_for_local)

    def __get_distance__(self, row, high: bool, before: bool) -> int:
        signature = -1 if before else 1
        actual_pos = int(row[CN.POSITION])
        pos = actual_pos + signature
        row_actual_pos = self.df.iloc[actual_pos]
        value_actual_pos = row_actual_pos[CN.HIGH] if high else row_actual_pos[CN.LOW]
        while 0 <= pos < self.df_length:
            row_pos = self.df.iloc[pos]
            value_pos = row_pos[CN.HIGH] if high else row_pos[CN.LOW]
            if value_pos > value_actual_pos and high:
                break
            elif value_pos < value_actual_pos and not high:
                break
            pos += signature
        return self.df_length + 1 if (pos < 0 or pos >= self.df_length) else abs(actual_pos - pos)


class FibonacciParser(WaveParser):
    def __init__(self, df: pd.DataFrame, movement_min_length: int, retracement_min_length: int = 0):
        WaveParser.__init__(self, df)
        self.movement_min_length = movement_min_length
        self.retracement_min_length = self.__get_retracement_min_length__(retracement_min_length)

    def __get_retracement_min_length__(self, retracement_min_length: int):
        return int(self.movement_min_length/2) if retracement_min_length == 0 else retracement_min_length


class WaveParser:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df_length = self.df.shape[0]
        self.length_for_global = int(self.df_length / 2)
        self.length_for_local = 3
        self.wave_tick_list = []
        self.wave_max_tick_list = []
        self.wave_min_tick_list = []
        self.__init_columns_for_ticks_distance__()
        self.__fill_wave_tick_lists__()

    def get_wave_tick_for_position(self, pos: int) -> WaveTick:
        return self.wave_tick_list[pos]

    def get_xy_max_parameter(self):
        return self.__get_xy_parameter__(False)

    def get_xy_min_parameter(self):
        return self.__get_xy_parameter__(True)

    def get_max_tick_list_for_range(self, pos_start: int, limit_value: float):
        return self.__get_tick_list_for_range__(pos_start, limit_value, True)

    def get_min_tick_list_for_range(self, pos_start: int, limit_value: float):
        return self.__get_tick_list_for_range__(pos_start, limit_value, False)

    def __get_xy_parameter__(self, is_min: bool):
        if is_min:
            df_global = self.df[self.df[CN.LOCAL_MIN]]
            col = CN.LOW
        else:
            df_global = self.df[self.df[CN.LOCAL_MAX]]
            col = CN.HIGH
        x = df_global[CN.DATEASNUM]
        y = df_global[col]
        return list(zip(x,y))

    def __get_tick_list_for_range__(self, pos_start: int, limit_value: float, is_max: bool):
        source_list = self.wave_max_tick_list if is_max else self.wave_min_tick_list
        wave_tick_list_return = []
        for ticks in source_list:
            if ticks.position > pos_start:
                if (is_max and ticks.high > limit_value) or (not is_max and ticks.low < limit_value):
                    break
                else:
                    wave_tick_list_return.append(ticks)
        return wave_tick_list_return

    def __init_columns_for_ticks_distance__(self):
        self.__add_distance_columns__()
        self.__add_min_max_columns__()

    def __fill_wave_tick_lists__(self):
        for ind, rows in self.df.iterrows():
            wave_tick = WaveTick(rows)
            self.wave_tick_list.append(wave_tick)
            if wave_tick.is_local_max:
                self.wave_max_tick_list.append(wave_tick)
            elif wave_tick.is_local_min:
                self.wave_min_tick_list.append(wave_tick)

    def __add_distance_columns__(self):
        for high in (False, True):
            for before in (False, True):
                value_list = []
                for ind, rows in self.df.iterrows():
                    value_list.append(self.__get_distance__(rows, high, before))
                if high and before:
                    self.df[CN.TICKS_BREAK_HIGH_BEFORE] = value_list
                elif high and not before:
                    self.df[CN.TICKS_BREAK_HIGH_AFTER] = value_list
                elif not high and before:
                    self.df[CN.TICKS_BREAK_LOW_BEFORE] = value_list
                elif not high and not before:
                    self.df[CN.TICKS_BREAK_LOW_AFTER] = value_list

    def __add_min_max_columns__(self):
        self.df[CN.GLOBAL_MIN] = np.logical_and(self.df[CN.TICKS_BREAK_LOW_AFTER] > self.length_for_global
                                                , self.df[CN.TICKS_BREAK_LOW_BEFORE] > self.length_for_global)
        self.df[CN.GLOBAL_MAX] = np.logical_and(self.df[CN.TICKS_BREAK_HIGH_AFTER] > self.length_for_global
                                                , self.df[CN.TICKS_BREAK_HIGH_BEFORE] > self.length_for_global)
        self.df[CN.LOCAL_MIN] = np.logical_and(self.df[CN.TICKS_BREAK_LOW_AFTER] > self.length_for_local
                                               , self.df[CN.TICKS_BREAK_LOW_BEFORE] > self.length_for_local)
        self.df[CN.LOCAL_MAX] = np.logical_and(self.df[CN.TICKS_BREAK_HIGH_AFTER] > self.length_for_local
                                               , self.df[CN.TICKS_BREAK_HIGH_BEFORE] > self.length_for_local)

    def __get_distance__(self, row, high: bool, before: bool) -> int:
        signature = -1 if before else 1
        actual_pos = int(row[CN.POSITION])
        pos = actual_pos + signature
        row_actual_pos = self.df.iloc[actual_pos]
        value_actual_pos = row_actual_pos[CN.HIGH] if high else row_actual_pos[CN.LOW]
        while 0 <= pos < self.df_length:
            row_pos = self.df.iloc[pos]
            value_pos = row_pos[CN.HIGH] if high else row_pos[CN.LOW]
            if value_pos > value_actual_pos and high:
                break
            elif value_pos < value_actual_pos and not high:
                break
            pos += signature
        return self.df_length + 1 if (pos < 0 or pos >= self.df_length) else abs(actual_pos - pos)


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
    def __init__(self, api: FormationBreakoutApi, config: FormationConfiguration):
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


class FormationPart:
    def __init__(self, df: pd.DataFrame, config: FormationConfiguration):
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


class Formation:
    ticks_initial = 0
    check_length = 0
    part_previous = FormationPart
    part_left = FormationPart
    part_middle = FormationPart
    part_right = FormationPart

    def __init__(self, df_previous: pd.DataFrame, df_start: pd.DataFrame, config: FormationConfiguration):
        self.config = config
        self.df_start = df_start
        self.df_combined = df_start  # will be changed when a new tick is added
        self.condition_handler = FormationConditionHandler()
        self.ticks_initial = self.df_start.shape[0]
        self.check_length = int(self.ticks_initial/3)
        self.accuracy_pct = self.config.accuracy_pct
        self.__init_type_formation_parts__(df_previous)
        self.bound_upper = self.__get_upper_bound__()
        self.bound_lower = self.__get_lower_bound__()
        self.breadth = self.bound_upper - self.bound_lower
        self.accuracy_range = self.breadth * self.accuracy_pct
        self.limit_upper = self.bound_upper + self.accuracy_range
        self.limit_lower = self.bound_lower - self.accuracy_range
        self.xy = None
        self.xy_control = None
        self.control_df = pd.DataFrame   # DataFrame to be checked for expected/real results after breakout
        self.date_first = None
        self.date_last = None
        self.breakout = None
        self.trade_result = TradeResult()

    def __init_type_formation_parts__(self, df_previous: pd.DataFrame):
        self.ticks_initial = self.df_start.shape[0]
        self.check_length = int(self.ticks_initial / 3)
        self.part_previous = FormationPart(df_previous, self.config)
        self.part_left = FormationPart(self.df_start.iloc[0:self.check_length], self.config)
        self.part_middle = FormationPart(self.df_start.iloc[self.check_length:2 * self.check_length], self.config)
        self.part_right = FormationPart(self.df_start.iloc[2 * self.check_length:self.ticks_initial], self.config)

    def was_breakout_done(self):
        return True if self.breakout.__class__.__name__ == 'FormationBreakout' else False

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
        return self.part_left.ticks + self.part_middle.ticks + self.part_right.ticks

    def __get_upper_bound__(self):
        return 0

    def __get_lower_bound__(self):
        return 0

    def is_formation_established(self):  # this is the main check whether a formation is ready for a breakout
        if self.__are_left_right_parts_applicable_for_formation_type__():
            if self.__is_middle_part_applicable_for_formation_type__():
                self.condition_handler.previous_period_check_ok = self.__is_previous_part_applicable_for_formation__()
                if not self.config.check_previous_period or self.condition_handler.previous_period_check_ok:
                    self.condition_handler.combined_parts_applicable \
                        = self.__are_combined_parts_applicable_for_formation__()
                    return self.condition_handler.combined_parts_applicable
        return False

    def reset_df_combined(self):
        self.df_combined = pd.concat([self.part_left.df, self.part_middle.df, self.part_right.df])

    def add_annotations(self, ax):
            pass

    def __is_previous_part_applicable_for_formation__(self):
        return True  # this is not always implemented in the deferred class

    def __are_combined_parts_applicable_for_formation__(self):
        return False

    def __are_left_right_parts_applicable_for_formation_type__(self):
        return False

    def __is_middle_part_applicable_for_formation_type__(self):
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

    def set_dates(self):
        self.date_first = self.df_combined.first_valid_index()
        self.date_last = self.df_combined.last_valid_index()

    def fill_result_set(self):
        if self.is_control_df_available():
            self.__fill_trade_result__()

    def is_control_df_available(self):
        return self.control_df.__class__.__name__ == 'DataFrame'

    def print_formation_parts_data(self):
        self.part_left.print_data('Left')
        self.part_middle.print_data('Middle')
        self.part_right.print_data('Right')

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


class TKE(Formation):
    p_13 = None
    tail_range = None  # this is the part of the curve which is the last part below the linear function

    @property
    def type(self):
        return FT.TKE

    @property
    def ticks(self):
        self.reset_df_combined()
        return self.df_combined.shape[0]

    def add_annotations(self, ax):
        self.part_left.plot_annotation(ax, True, 'blue')
        self.part_middle.plot_annotation(ax, True, 'blue')
        self.part_right.plot_annotation(ax, True, 'blue')
        if self.tail_range is not None:
            self.tail_range.plot_annotation(ax, True, 'red')

    def reset_df_combined(self):
        date_left = self.part_left.df.first_valid_index()
        date_right = self.part_right.df.last_valid_index()
        self.df_combined = self.df_start.loc[date_left:date_right]

    def __init_type_formation_parts__(self, df_previous: pd.DataFrame):
        """
        This script parses the df_start for the first part - this has to be a TKE - part already...
        :param df_previous: the dataframe with is a predecessor to the rest, i.e. only a small part.
        :return:
        """
        self.check_length = self.config.min_length_of_a_formation_part
        self.ticks_initial = self.check_length * 3
        self.part_left = FormationPart(self.df_start.iloc[0:self.check_length], self.config)
        if self.part_left.is_high_first_tick():
            self.part_middle = None
            self.part_right = None
            self.part_previous = FormationPart(df_previous, self.config)
            self.__add_missing_parts__()

    def __add_missing_parts__(self):
        wave_tick_last = self.config.actual_list[-1]
        pos = self.__get_wave_tick_position_in_start_df__(wave_tick_last.position)
        self.part_right = FormationPart(self.df_start.iloc[pos:pos + self.check_length], self.config)
        self.p_13 = self.__get_function_parameter__(self.part_left, self.part_right)
        if self.__is_right_part_applicable_for_formation_type__():
            if self.__are_left_right_parts_applicable_for_formation_type__():
                reversed_list = self.config.actual_list[::-1]
                changed_list = self.__remove_entries_not_close_to_linear_p_13_function__(reversed_list[1:])
                for wave_ticks in changed_list:
                    pos = self.__get_wave_tick_position_in_start_df__(wave_ticks.position)
                    self.part_middle = FormationPart(self.df_start.iloc[pos:pos + self.check_length], self.config)
                    if self.__is_middle_part_applicable_for_formation_type__():
                        break
                    else:
                        self.part_middle = None

    def __remove_entries_not_close_to_linear_p_13_function__(self, input_list):
        return_list = []
        if self.__is_any_entry_not_allowed_for_linear_p_13_function__(input_list):
            return return_list  # i.e. empty list

        for wave_ticks in input_list:
            pos = self.__get_wave_tick_position_in_start_df__(wave_ticks.position)
            part = FormationPart(self.df_start.iloc[pos:pos + self.check_length], self.config)
            if part.is_close_close_to_linear_function(self.p_13):
                return_list.append(wave_ticks)
        return return_list

    def __is_any_entry_not_allowed_for_linear_p_13_function__(self, input_list):
        for wave_ticks in input_list:
            pos = self.__get_wave_tick_position_in_start_df__(wave_ticks.position)
            part = FormationPart(self.df_start.iloc[pos:pos + self.check_length], self.config)
            if not part.are_values_below_linear_function(self.p_13, column=CN.CLOSE):
                return True
        return False

    def __get_wave_tick_position_in_start_df__(self, position_original: int):
        return position_original - self.config.actual_position

    @staticmethod
    def __get_function_parameter__(part_left: FormationPart, part_right: FormationPart):
        x = np.array([part_left.id_max_high_num, part_right.id_max_high_num])
        y = np.array([part_left.max_high, part_right.max_high])
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        return p

    def __are_combined_parts_applicable_for_formation__(self):
        return True

    def __is_previous_part_applicable_for_formation__(self):
        return self.part_previous.max_close < self.part_left.max_high

    def __is_right_part_applicable_for_formation_type__(self):
        df = self.df_start.loc[self.part_left.id_max_high:self.part_right.id_max_high]
        left_to_right_part = FormationPart(df, self.config)
        df_from_right_to_end = self.df_start.loc[self.part_right.id_max_high:]
        if df_from_right_to_end.shape[0] < 2:
            return True
        part_after_right_to_end = FormationPart(df_from_right_to_end[1:], self.config)  # don't take the first = HIGH
        cross_date = part_after_right_to_end.get_cross_date_when_curve_is_crossed(self.p_13)
        if cross_date is not None:  # i.e. there is a crossing
            df_from_right_to_cross = self.df_start.loc[self.part_right.id_max_high:cross_date]
            part_from_right_to_cross = FormationPart(df_from_right_to_cross, self.config)
            if left_to_right_part.min_low < part_from_right_to_cross.min_low:
                return False
        return True

    def __are_left_right_parts_applicable_for_formation_type__(self):
        if self.part_left.is_high_first_tick():
            if self.part_right.is_high_before_low():
                if self.part_left.min_low > self.part_right.max_high:
                    if self.part_left.are_values_below_linear_function(self.p_13):
                        if self.part_right.are_values_below_linear_function(self.p_13):
                            return True
        return False

    def __is_middle_part_applicable_for_formation_type__(self):
        if self.part_middle is None:
            return False
        if self.part_left.get_retracement_pct(self.part_middle) > 0.7:
            return False
        if self.part_middle.is_high_before_low():
            if self.part_left.max_high > self.part_middle.max_high:
                if self.part_left.min_low < self.part_middle.max_high:
                    if self.part_middle.max_high > self.part_right.max_high:
                        if self.part_middle.min_low > self.part_right.max_high:
                            if self.part_middle.are_values_below_linear_function(self.p_13, self.accuracy_pct, CN.CLOSE):
                                return True
        return False

    def is_tick_fitting_to_formation(self, tick_df: pd.DataFrame):
        return self.__is_tick_tke_conform__(tick_df.iloc[0])

    def __is_tick_tke_conform__(self, row) -> bool:
        if row[CN.HIGH] > self.p_13(row[CN.DATEASNUM]):
            return self.__is_tick_in_tke_tail__(row)
        return True

    def __print_break_information__(self, row):
        left_date = FormationDate.get_date_from_datetime(self.part_left.id_max_high)
        middle_date = FormationDate.get_date_from_datetime(self.part_middle.id_max_high)
        right_date = FormationDate.get_date_from_datetime(self.part_right.id_max_high)

        print('Break on {}: row[CN.HIGH]={} > self.p_13(row[CN.DATEASNUM]={})'.
              format(row[CN.DATE], row[CN.HIGH], self.p_13(row[CN.DATEASNUM])))
        print('...Hights: {} -> {} -> {}'.format(left_date, middle_date, right_date))

    def __is_tick_in_tke_tail__(self, row) -> bool:
        if self.tail_range is None:
            # self.__print_break_information__(row)
            self.part_right.recalculate_values()
            self.__set_tail_range__()
        return self.tail_range.is_tick_fitting_to_range(row)

    def __set_tail_range__(self):
        date_start = self.part_right.id_min_low
        df_tail = self.df_start.loc[date_start:]
        part_tail = FormationPart(df_tail, self.config)
        min_value = self.part_right.min_low
        max_value = self.p_13(self.part_right.id_min_low_num)
        date_end = part_tail.get_cross_date_when_min_reached(self.p_13)
        if date_end is None:
            date_end = df_tail.iloc[-1][CN.DATE]
        self.tail_range = FormationRange(date_start, date_end, min_value, max_value)
        self.bound_upper = max_value
        self.bound_lower = min_value
        # self.tail_range.print()

    def set_xy_formation_parameter(self):
        x_dates = [self.date_first, self.date_last]
        x = list(dt.date2num(x_dates))
        y = self.p_13(x)
        self.xy = list(zip(x, y)) + self.__get_xy_for_tail_range__(False)

    def set_xy_control_parameter(self):
        self.xy_control = self.__get_xy_for_tail_range__(True)

    def __get_xy_for_tail_range__(self, for_control: bool):
        if self.tail_range is None:
            return []
        date_left_num = self.tail_range.date_start_num
        date_right_num = self.tail_range.date_end_num
        min_value = self.tail_range.min
        max_value = self.tail_range.max
        range = max_value - min_value
        if for_control:
            min_value += range
            max_value += range
        x = [date_left_num, date_left_num, date_right_num, date_right_num, date_left_num]
        y = [max_value, min_value, min_value, max_value, max_value]
        return list(zip(x, y))

    def get_shape(self):
        self.set_xy_formation_parameter()
        pol = Polygon(np.array(self.xy), True)
        return pol

    def get_control_shape(self):
        self.set_xy_control_parameter()
        pol = Polygon(np.array(self.xy_control), True)
        pol.set_color('#eeefff')
        return pol


class Channel(Formation):
    @property
    def type(self):
        return FT.CHANNEL

    @property
    def mean(self):
        return (self.part_left.mean + self.part_right.mean) / 2

    def __get_upper_bound__(self):
        return max(self.part_left.bound_upper, self.part_right.bound_upper)

    def __get_lower_bound__(self):
        return min(self.part_left.bound_lower, self.part_right.bound_lower)

    def __are_combined_parts_applicable_for_formation__(self):
        if self.__is_min_max_distribution_compliant__(True):
            return self.__is_min_max_distribution_compliant__(False)
        return False

    def __is_min_max_distribution_compliant__(self, check_max: bool):
        if check_max:
            dist = self.df_combined[CN.HIGH] > (self.bound_upper - self.accuracy_range)
        else:
            dist = self.df_combined[CN.LOW] < (self.bound_lower + self.accuracy_range)
        hit_counter = 0
        loop_counter = 0
        while loop_counter < dist.shape[0]:
            if dist.iloc[loop_counter]:
                hit_counter += 1
                loop_counter += int(self.ticks_initial/3)
            else:
                loop_counter += 1
        return True if hit_counter >= 3 else False

    def __is_previous_part_applicable_for_formation__(self):
        upper_check = self.part_previous.min_close > self.df_combined[CN.CLOSE].max()
        lower_check = self.part_previous.max_close < self.df_combined[CN.CLOSE].min()
        return upper_check or lower_check

    def __are_left_right_parts_applicable_for_formation_type__(self):
        if self.__is_part_applicable_for_formation_type__(self.part_left):
            return self.__is_part_applicable_for_formation_type__(self.part_right)
        return False

    def __is_middle_part_applicable_for_formation_type__(self):
        return self.__is_part_applicable_for_formation_type__(self.part_middle)

    def __is_part_applicable_for_formation_type__(self, part: FormationPart):
        if abs(part.max_high - self.bound_upper) < self.accuracy_range:  # is_near_upper_bound
            if abs(part.min_low - self.bound_lower) < self.accuracy_range:  # is_near_lower_bound
                if True or abs(part.mean - self.mean) < self.accuracy_range:  # is_near_mean
                    return True
        return False

    def is_tick_fitting_to_formation(self, tick_df: pd.DataFrame):
        return self.bound_lower <= tick_df.iloc[0][CN.CLOSE] <= self.bound_upper

    def set_xy_formation_parameter(self):
        x_dates = [self.date_first, self.date_first, self.date_last, self.date_last]
        x = list(dt.date2num(x_dates))
        y = [self.bound_upper, self.bound_lower, self.bound_lower, self.bound_upper]
        self.xy = list(zip(x, y))

    def set_xy_control_parameter(self):
        date_first = self.control_df.first_valid_index()
        date_last = self.control_df.last_valid_index()

        x_dates = [date_first, date_first, date_last, date_last]
        x = list(dt.date2num(x_dates))

        if self.breakout_direction == FD.ASC:
            y_max = self.bound_upper + (self.bound_upper - self.bound_lower)
            y_min = self.bound_upper
        else:  # breakout downwards
            y_max = self.bound_lower
            y_min = self.bound_lower - (self.bound_upper - self.bound_lower)
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


class FSC:  # Formation Statistics Columns
    C_BOUND_UPPER_VALUE = 'conf.bound_upper_value'  # eg. CN.HIGH
    C_BOUND_LOWER_VALUE = 'conf.bound_lower_value'  # eg. CN.LOW
    C_PART_MAX_LEN = 'conf.max_length_of_a_formation_part'
    C_PART_MIN_LEN = 'conf.min_length_of_a_formation_part'
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


class FormationStatistics:
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
        self.column_list.append(FSC.C_PART_MAX_LEN)
        self.column_list.append(FSC.C_PART_MIN_LEN)
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

    def add_entry(self, formation: Formation):
        self.__init_dic__()

        self.dic[FSC.C_BOUND_UPPER_VALUE] = formation.config.bound_upper_value
        self.dic[FSC.C_BOUND_LOWER_VALUE] = formation.config.bound_lower_value
        self.dic[FSC.C_PART_MAX_LEN] = formation.config.max_length_of_a_formation_part
        self.dic[FSC.C_PART_MIN_LEN] = formation.config.min_length_of_a_formation_part
        self.dic[FSC.C_CHECK_PREVIOUS_PERIOD] = formation.config.check_previous_period
        self.dic[FSC.C_BREAKOUT_OVER_CONGESTION] = formation.config.breakout_over_congestion_range
        self.dic[FSC.C_ACCURACY_PCT] = formation.config.accuracy_pct
        self.dic[FSC.C_BREAKOUT_RANGE_PCT] = formation.config.breakout_range_pct
        self.dic[FSC.C_AND_CLAUSE] = formation.config.and_clause

        self.dic[FSC.CON_PREVIOUS_PERIOD_CHECK_OK] = formation.condition_handler.previous_period_check_ok
        self.dic[FSC.CON_COMBINED_PARTS_APPLICABLE] = formation.condition_handler.combined_parts_applicable
        self.dic[FSC.CON_BREAKOUT_WITH_BUY_SIGNAL] = formation.condition_handler.breakout_with_buy_signal

        self.dic[FSC.STATUS] = 'Finished' if formation.was_breakout_done() else 'Open'
        self.dic[FSC.NUMBER] = formation.config.actual_number
        self.dic[FSC.TICKER] = formation.config.actual_ticker
        self.dic[FSC.NAME] = formation.config.actual_ticker_name
        self.dic[FSC.FORMATION] = formation.__class__.__name__
        if formation.part_previous.df.shape[0] != 0:
            self.dic[FSC.BEGIN_PREVIOUS] = FormationDate.get_date_from_datetime(formation.part_previous.date_first)
        self.dic[FSC.BEGIN] = FormationDate.get_date_from_datetime(formation.date_first)
        self.dic[FSC.END] = FormationDate.get_date_from_datetime(formation.date_last)
        self.dic[FSC.LOWER] = round(formation.bound_lower, 2)
        self.dic[FSC.UPPER] = round(formation.bound_upper, 2)
        self.dic[FSC.T_ORIG] = formation.ticks_initial
        self.dic[FSC.T_FINAL] = formation.ticks
        if formation.was_breakout_done():
            self.dic[FSC.BREAKOUT_DATE] = FormationDate.get_date_from_datetime(formation.breakout.breakout_date)
            self.dic[FSC.BREAKOUT_DIRECTION] = formation.breakout.breakout_direction
            self.dic[FSC.VOLUME_CHANGE] = formation.breakout.volume_change_pct
            if formation.is_control_df_available():
                self.dic[FSC.EXPECTED] = formation.trade_result.expected_win
                self.dic[FSC.RESULT] = formation.trade_result.actual_win
                self.dic[FSC.VAL] = formation.trade_result.formation_consistent
                self.dic[FSC.EXT] = formation.trade_result.limit_extended_counter
                self.dic[FSC.BOUGHT_AT] = round(formation.trade_result.bought_at, 2)
                self.dic[FSC.SOLD_AT] = round(formation.trade_result.sold_at, 2)
                self.dic[FSC.BOUGHT_ON] = FormationDate.get_date_from_datetime(formation.trade_result.bought_on)
                self.dic[FSC.SOLD_ON] = FormationDate.get_date_from_datetime(formation.trade_result.sold_on)
                self.dic[FSC.T_NEEDED] = formation.trade_result.actual_ticks
                self.dic[FSC.LIMIT] = round(formation.trade_result.limit, 2)
                self.dic[FSC.STOP_LOSS_AT] = round(formation.trade_result.stop_loss_at, 2)
                self.dic[FSC.STOP_LOSS_TRIGGERED] = formation.trade_result.stop_loss_reached

                self.dic[FSC.RESULT_DF_MAX] = formation.control_df[CN.CLOSE].max()
                self.dic[FSC.RESULT_DF_MIN] = formation.control_df[CN.CLOSE].min()
                self.dic[FSC.FIRST_LIMIT_REACHED] = False  # default
                self.dic[FSC.STOP_LOSS_MAX_REACHED] = False  # default
                if formation.breakout_direction == FD.ASC \
                        and (formation.bound_upper + formation.breadth < self.dic[FSC.RESULT_DF_MAX]):
                    self.dic[FSC.FIRST_LIMIT_REACHED] = True
                if formation.breakout_direction == FD.DESC \
                        and (formation.bound_lower - formation.breadth > self.dic[FSC.RESULT_DF_MIN]):
                    self.dic[FSC.FIRST_LIMIT_REACHED] = True
                if formation.breakout_direction == FD.ASC \
                        and (formation.bound_lower > self.dic[FSC.RESULT_DF_MIN]):
                    self.dic[FSC.STOP_LOSS_MAX_REACHED] = True
                if formation.breakout_direction == FD.DESC \
                        and (formation.bound_upper < self.dic[FSC.RESULT_DF_MAX]):
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
            if formation.was_breakout_done() and formation.is_control_df_available():
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
        self.df = df.assign(MeanHL=round((df.High + df.Low) / 2, 2))
        self.df_length = self.df.shape[0]
        self.df[CN.DATE] = self.df.index.map(FormationDate.get_date_from_datetime)
        self.df[CN.DATEASNUM] = self.df.index.map(dt.date2num)
        self.df[CN.DATEASNUM] = self.df[CN.DATEASNUM].apply(int)
        self.df[CN.POSITION] = self.df.index.map(self.df.index.get_loc)
        self.df[CN.POSITION] = self.df[CN.POSITION].apply(int)
        self.accuracy_pct = self.config.accuracy_pct
        self.formation_dic = {}
        self.wave_parser = WaveParser(self.df)
        self.part_ticks_min = self.__get_part_ticks_min__()
        self.part_ticks_max = self.config.max_length_of_a_formation_part
        self.position_actual = self.__get_start_position__()
        self.position_last = self.__get_last_position__()

    def parse_df(self):
        while self.position_actual <= self.position_last:
            self.__init_config_parameter_for_loop__()
            self.position_actual = self.check_actual_position_for_valid_formation()

    def __init_config_parameter_for_loop__(self):
        if self.config.formation_type == FT.TKE:
            self.config.actual_position = self.position_actual
            tick = self.wave_parser.get_wave_tick_for_position(self.position_actual)
            self.config.actual_list = self.wave_parser.get_max_tick_list_for_range(tick.position, tick.high)

    def check_actual_position_for_valid_formation(self):
        part_ticks = self.__get_part_ticks_max_for_loop__()
        while part_ticks >= self.part_ticks_min:  # try different lengths of the 3 parts of the formation
            ticks = part_ticks * 3
            if self.position_actual + ticks < self.df_length:
                df_previous = self.__get_df_previous__()
                if self.__is_precondition_for_df_previous_fullfilled__(df_previous):
                    formation = self.__get_formation__(df_previous, ticks)
                    if formation.is_formation_established():
                        ticks = formation.ticks  # the ticks in some formation are different from the sum over the parts
                        self.__check_for_breakout__(formation, ticks)
                        next_pos = self.get_next_pos_after_adding_to_dictionary(formation)
                        if self.config.formation_type == FT.TKE:  # if TKE: there can be more than one formation
                            pass
                        else:
                            return next_pos
            part_ticks -= 1
            if self.config.formation_type == FT.TKE:
                self.config.actual_list = self.config.actual_list[:-1]
        return self.__increment_position_actual__()

    def __increment_position_actual__(self):
        if self.config.formation_type == FT.TKE:
            self.config.actual_tick_position += 1
            return self.wave_parser.wave_max_tick_list[self.config.actual_tick_position].position
        else:
            return self.position_actual + 1

    def __get_part_ticks_min__(self):
        if self.config.formation_type == FT.TKE:  # we need at least 3 min or max in wave
            return 3
        else:
            return self.config.min_length_of_a_formation_part

    def __get_part_ticks_max_for_loop__(self):
        if self.config.formation_type == FT.TKE:
            return len(self.config.actual_list)
        else:
            return self.part_ticks_max

    def __get_start_position__(self):
        if self.config.formation_type == FT.TKE:  # we don't need to loop for different sizes
            self.config.actual_tick_position = 0
            return self.wave_parser.wave_max_tick_list[self.config.actual_tick_position].position
        else:
            return self.config.min_length_of_a_formation_part  # we need some predecessor ticks

    def __get_last_position__(self):
        if self.config.formation_type == FT.TKE:  # we don't need to loop for different sizes
            return self.wave_parser.wave_max_tick_list[-2].position  # we need at least 2 remaining entries
        else:
            return self.df.shape[0] - self.part_ticks_min * 3

    def __check_for_breakout__(self, formation: Formation, ticks: int):
        last_tick_fitting_to_formation, pos_last_tick, last_tick_df = \
            self.get_details_after_adding_new_ticks_to_formation(formation, ticks)
        if not last_tick_fitting_to_formation:  # is was a breakout...
            breakout_api = self.__get_breakout_api__(formation, last_tick_df)
            formation.breakout = FormationBreakout(breakout_api, self.config)
            self.add_control_df(formation, pos_last_tick)

    def __get_formation__(self, df_previous, ticks):
        if self.config.formation_type == FT.TKE:
            df_start = self.df.iloc[self.position_actual:]
            return TKE(df_previous, df_start, self.config)
        elif self.config.formation_type == FT.CHANNEL:
            df_start = self.df.iloc[self.position_actual:self.position_actual + ticks]
            return Channel(df_previous, df_start, self.config)
        else:
            print('not implemented yet: FormationType = {}'.format(self.config.formation_type))
            exit()

    def __get_df_previous__(self):
        if self.config.formation_type == FT.TKE:
            left_boundary = max(0, self.position_actual - 4)
        else:
            left_boundary = max(0, self.position_actual - config.previous_period_length)
        return self.df.iloc[left_boundary:self.position_actual]

    def __is_precondition_for_df_previous_fullfilled__(self, df_previous: pd.DataFrame):
        return True

    def print_formation_details(self, formation: Formation, part_ticks):
        print('Checking position_actual = {} and part_ticks = {} and accuracy_range: {}'
              '\nL/U = {} / {}, \nL_1/U_1 = {} / {}, \nL_2/U_2 = {} / {}, \nL_3/U_3 = {} / {}'
              .format(self.position_actual, part_ticks, round(formation.accuracy_range, 2)
                      , formation.bound_lower, formation.bound_upper
                      , formation.part_left.bound_lower, formation.part_left.bound_upper
                      , formation.part_middle.bound_lower, formation.part_middle.bound_upper
                      , formation.part_right.bound_lower, formation.part_right.bound_upper
                      ))

    def add_control_df(self, formation, pos_new_tick):
        if pos_new_tick < self.df.shape[0]:
            left_boundary = pos_new_tick
            right_boundary = min(left_boundary + formation.ticks, self.df_length)
            formation.control_df = self.df.iloc[left_boundary:right_boundary]
            formation.fill_result_set()

    def get_details_after_adding_new_ticks_to_formation(self, formation, ticks):
        is_tick_fitting_to_formation = True
        pos_new_tick = self.position_actual + ticks + 1
        tick_df = pd.DataFrame
        while is_tick_fitting_to_formation and pos_new_tick <= self.df_length:
            tick_df = self.df.iloc[pos_new_tick - 1:pos_new_tick]
            is_tick_fitting_to_formation = formation.is_tick_fitting_to_formation(tick_df)
            if is_tick_fitting_to_formation:
                formation.add_tick_to_formation(tick_df)
                pos_new_tick += 1
        return is_tick_fitting_to_formation, pos_new_tick, tick_df

    def get_next_pos_after_adding_to_dictionary(self, formation):
        formation.reset_df_combined()
        formation.set_dates()
        self.formation_dic[self.position_actual] = formation
        if self.config.formation_type == FT.TKE:  # there can be more than one formation in the same range
            return self.position_actual + self.config.min_length_of_a_formation_part
        else:
            if formation.buy_after_breakout:
                return self.position_actual + formation.ticks * 2 + 1  # no other formation check in the control period
            return self.position_actual + formation.ticks + 1  # formation established but no valid breakout signal

    @staticmethod
    def __get_breakout_api__(formation: Formation, tick_df: pd.DataFrame):
        api = FormationBreakoutApi(formation.__class__.__name__)
        api.df = tick_df
        api.previous_tick = formation.part_right.df.loc[formation.part_right.df.last_valid_index()]
        api.bound_upper = formation.bound_upper
        api.bound_lower = formation.bound_lower
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
        if formation.was_breakout_done():
            return 'green'
        else:
            return 'yellow'

    @staticmethod
    def __get_control_color__(formation: Formation):
        if formation.was_breakout_done():
            if formation.trade_result.actual_win > 0:
                return 'lime'
            else:
                return 'orangered'
        else:
            return 'white'


class FormationPlotter:
    def __init__(self, api_object, detector: FormationDetector):
        self.api_object = api_object  # StockDatabaseDataFrame or AlphavantageStockFetcher
        self.api_object_class = self.api_object.__class__.__name__
        self.detector = detector
        self.config = self.detector.config
        self.part_ticks_max = self.config.max_length_of_a_formation_part
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
        # self.__add_fibonacci_waves__(axis)

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

            if formation.was_breakout_done() and formation.is_control_df_available():
                if color_control in patches_dic:
                    patches_dic[color_control].append(formation.get_control_shape())
                else:
                    patches_dic[color_control] = [formation.get_control_shape()]
            formation.add_annotations(ax)

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


class DetectorStatistics:
    def __init__(self):
        self.list = []
        self.column_list = ['Number', 'Ticker', 'Name', 'Investment', 'Result', 'Change%', 'SL', 'F_OK', 'F_NOK', 'Ticks']

    def add_entry(self, config: FormationConfiguration, api: FormationDetectorStatisticsApi):
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


class FormationController:
    def __init__(self, config: FormationConfiguration):
        self.config = config
        self.detector_statistics = DetectorStatistics()
        self.formation_statistics = FormationStatistics()
        self.stock_db = stock_database.StockDatabase
        self.plotter_input_obj = None
        self.df_data = None
        self.__excel_file_with_test_data = ''
        self.df_test_data = pd.DataFrame
        self.loop_list = []  # format of an entry (ticker, and_clause)
        self.__start_row = 0
        self.__end_row = 0

    def run_formation_checker(self, excel_file_with_test_data: str = '', start_row: int = 1, end_row: int = 0):
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

    def __handle_statistics__(self, detector: FormationDetector):
        for keys in detector.formation_dic:
            self.formation_statistics.add_entry(detector.formation_dic[keys])

        if config.show_final_statistics:
            self.detector_statistics.add_entry(self.config, detector.get_statistics_api())
        else:
            detector.print_statistics()


config = FormationConfiguration()
config.get_data_from_db = True
config.api_period = ApiPeriod.DAILY
config.formation_type = FT.TKE
config.plot_data = True
config.statistics_excel_file_name = 'statistics_tke.xlsx'
config.statistics_excel_file_name = ''
config.bound_upper_value = CN.CLOSE
config.bound_lower_value = CN.CLOSE
config.max_length_of_a_formation_part = 15
config.min_length_of_a_formation_part = 5
config.breakout_over_congestion_range = False
# config.show_final_statistics = True
config.max_number_securities = 1000
config.accuracy_pct = 0.03  # default is 0.05
config.breakout_range_pct = 0.1  # default is 0.01
config.use_index(Indices.DOW_JONES)
config.use_own_dic({"NKE": "???"})  # INTC	Intel NKE	Nike  V (Visa) GE
config.and_clause = "Date BETWEEN '2016-01-23' AND '2019-09-05'"
# config.and_clause = ''
config.api_output_size = ApiOutputsize.COMPACT

formation_controller = FormationController(config)
formation_controller.run_formation_checker('')
# formation_controller.run_formation_checker('channel_test_data.xlsx', 1, 1000)
"""
ACGL
BBBY
BELFA
FARM
FNSR
GE
MATW
MSTR
ONB
OPK
SAFM
SANM
SNH
SNHY
THFF
TTEC
WMT
"""

"""
DIS	Disney
JPM	JPMorgan
Date BETWEEN '2017-06-01' AND '2019-02-05
- HD check - very well
- JNJ false breakout - could be avoided by breakout range > 0
-----------
TKE: 20 MRK (Merck) perfect for Date BETWEEN '2016-09-18' AND '2019-02-05
- VZ (verizon)?
Processing WMT (Wal-Mart)... ERROR
"""






