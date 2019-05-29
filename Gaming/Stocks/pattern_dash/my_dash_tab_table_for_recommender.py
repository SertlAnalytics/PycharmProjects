"""
Description: This module contains the dash table for recommendations
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-15
"""

from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import PRD, INDICES, DC, SCORING
from pattern_database.stock_database import StockDatabase
from pattern_data_provider import PatternDataProvider


class RWC:  # RecommenderWaveCriterias
    C_400 = '400'
    C_400_A = '400_a'
    C_200 = '200'
    C_200_A = '200_a'
    C_30 = '30'
    C_30_A = '30_a'

    @staticmethod
    def get_list():
        return [RWC.C_400, RWC.C_400_A, RWC.C_200, RWC.C_200_A, RWC.C_30, RWC.C_30_A]

    @staticmethod
    def get_scoring_point(criteria: str):
        return {RWC.C_400: 1, RWC.C_400_A: 2, RWC.C_200: 1, RWC.C_200_A: 2, RWC.C_30: 2, RWC.C_30_A: 3}.get(criteria, 0)


class RDC:  # RecommenderDataColumn
    INDEX = 'Index'
    SYMBOL = 'Symbol'
    NAME = 'Name'
    PRICE = 'Price'
    PRICE_CHANGE = 'Change (%)'
    FIBONACCI_SHORT = 'Fib. (30min)'
    FIBONACCI_MID = 'Fib. (200d)'
    FIBONACCI_LONG = 'Fib. (400d)'
    SCORING_POINTS = 'Scoring'
    PORTFOLIO = 'Portfolio'


class RecommenderRow:
    sort_column = RDC.NAME

    def __init__(self):
        self._columns = [RDC.INDEX, RDC.SYMBOL, RDC.NAME, RDC.PRICE, RDC.PRICE_CHANGE,
                         RDC.FIBONACCI_SHORT, RDC.FIBONACCI_MID, RDC.FIBONACCI_LONG, RDC.SCORING_POINTS,
                         RDC.PORTFOLIO]
        self._value_dict = {col: '' for col in self._columns}

    @property
    def value_dict(self):
        return self._value_dict

    @property
    def columns(self):
        return self._columns

    @property
    def index(self):
        return self._value_dict[RDC.INDEX]

    @property
    def symbol(self):
        return self._value_dict[RDC.SYMBOL]

    @property
    def scoring_points(self):
        return self._value_dict[RDC.SCORING_POINTS]

    def add_value(self, column: str, value):
        self._value_dict[column] = value

    def get_row_as_dict(self):
        return self._value_dict

    def __eq__(self, other):
        return self._value_dict[self.sort_column] == other.value_dict[self.sort_column]

    def __lt__(self, other):
        return self._value_dict[self.sort_column] < other.value_dict[self.sort_column]

    def __gt__(self, other):
        return self._value_dict[self.sort_column] < other.value_dict[self.sort_column]


class RecommenderTable:
    def __init__(self, db_stock: StockDatabase, data_provider: PatternDataProvider):
        self._db_stock = db_stock
        self._data_provider = data_provider
        self._indices = [INDICES.CRYPTO_CCY, INDICES.DOW_JONES, INDICES.NASDAQ100]
        self._exchange_dict = self.__get_exchange_dict__()
        self._wave_df = None
        self._wave_for_ticker_dict = {}
        self._rows_from_db = []
        self._rows_current = []
        self._selected_indices = []
        self._selected_scoring = SCORING.ALL
        self._selected_row_index = -1
        self._selected_row = None
        self._rows_selected_indices = []
        self._symbols = []
        self.__init_data_from_database__(initialize=True)

    @property
    def columns(self):
        return RecommenderRow().columns

    @property
    def selected_row_index(self):
        return self._selected_row_index

    @property
    def selected_symbol(self):
        if self._selected_row is None:
            return ''
        return self._selected_row[RDC.SYMBOL]

    @property
    def selected_index(self):
        if self._selected_row is None:
            return ''
        return self._selected_row[RDC.INDEX]

    @property
    def height_for_display(self):
        height = max(100, 50 + len(self._rows_selected_indices) * 40)
        if height > 400:
            return 400
        return max(100, height)

    def get_rows_for_selected_indices(self):
        if len(self._rows_selected_indices) == 0:
            return [RecommenderRow().get_row_as_dict()]
        RecommenderRow.sort_column = RDC.SYMBOL if self._selected_scoring == SCORING.ALL else RDC.SCORING_POINTS
        sort_reverse = False if self._selected_scoring == SCORING.ALL else True
        sorted_list = sorted(self._rows_selected_indices, reverse=sort_reverse)
        return [row.get_row_as_dict() for row in sorted_list]

    def init_selected_row(self, table_rows: list, selected_row_indices: list=None):
        if selected_row_indices is None or len(selected_row_indices) != 1:
            self._selected_row_index = -1
            self._selected_row = None
        else:
            self._selected_row_index = selected_row_indices[0]  # the latest selected is always on position 0
            self._selected_row = table_rows[self._selected_row_index]

    def update_rows_for_selected_indices(self, selected_indices: list, scoring: str):
        self._selected_row_index = -1  # no entry selected
        self._selected_scoring = scoring
        self._selected_indices = selected_indices
        if len(self._selected_indices) == 0:
            self._rows_selected_indices = []
        else:
            self.__init_data_from_database__(initialize=False)

    def __init_data_from_database__(self, initialize: bool):
        self._wave_df = self._db_stock.get_wave_records_for_recommender_as_dataframe(400)
        self.__fill_wave_for_ticker_dict__()
        self.__fill_rows_from_wave_for_ticker_dict__(initialize)
        self.__fill_rows_for_selected_indices__()

    def __fill_wave_for_ticker_dict__(self):
        ts_now = MyDate.time_stamp_now()
        ts_from_daily_200 = ts_now - 60 * 60 * 24 * 200
        ts_from_daily_actual = ts_now - 60 * 60 * 24 * 5  # within the last 5 days
        ts_from_intraday_actual = ts_now - 60 * 60 * 12  # within the last 12 hours
        for index, row in self._wave_df.iterrows():
            ticker_id = row[DC.TICKER_ID]
            if ticker_id not in self._wave_for_ticker_dict:
                self._wave_for_ticker_dict[ticker_id] = {criteria: 0 for criteria in RWC.get_list()}
            ticker_dict = self._wave_for_ticker_dict[ticker_id]
            period = row[DC.PERIOD]
            ts_wave_end = row[DC.WAVE_END_TS]
            if period == PRD.DAILY:
                ticker_dict[RWC.C_400] += 1
                if ts_wave_end > ts_from_daily_200:
                    ticker_dict[RWC.C_200] += 1
                if ts_wave_end > ts_from_daily_actual:
                    # print('{} - wave is actual: end = {} - compared to {}'.format(
                    #     ticker_id, MyDate.get_date_from_epoch_seconds(ts_wave_end),
                    #     MyDate.get_date_from_epoch_seconds(ts_from_daily_actual)))
                    ticker_dict[RWC.C_400_A] += 1
                    ticker_dict[RWC.C_200_A] += 1
            else:
                ticker_dict[RWC.C_30] += 1
                if ts_wave_end > ts_from_intraday_actual:
                    ticker_dict[RWC.C_30_A] += 1

    def __fill_rows_for_selected_indices__(self):
        self._rows_selected_indices = []
        if len(self._selected_indices) > 0:
            for row in self._rows_from_db:
                if row.index in self._selected_indices:
                    if self._selected_scoring == SCORING.ALL or row.scoring_points > 2:
                        self._rows_selected_indices.append(row)

    def __append_row_to_rows_from_db__(self, row: RecommenderRow):
        self._rows_from_db.append(row)
        self._symbols.append(row.symbol)

    def __fill_rows_from_wave_for_ticker_dict__(self, initialize: bool):
        index_list = self._indices if initialize else self._selected_indices
        for index in index_list:
            index_member_dict = self._exchange_dict[index]
            for symbol, name in index_member_dict.items():
                if not self.__is_row_for_symbol_available__(symbol):
                    row_new = self.__get_new_row_for_data_table__(index, symbol, name)
                    self.__append_row_to_rows_from_db__(row_new)

    def __get_new_row_for_data_table__(self, index: str, symbol: str, name: str) -> RecommenderRow:
        row = RecommenderRow()
        for column in row.columns:
            row.add_value(column, self.__get_column_value__(index, symbol, name, column))
        return row

    def __get_column_value__(self, index: str, symbol: str, name: str, column: str):
        if column == RDC.INDEX: return index
        elif column == RDC.SYMBOL: return symbol
        elif column == RDC.NAME: return name
        elif column == RDC.PRICE: return 0
        elif column == RDC.PRICE_CHANGE: return 0
        elif column == RDC.FIBONACCI_SHORT:
            return self.__get_fibonacci_wave_numbers__(index, symbol, 30)
        elif column == RDC.FIBONACCI_MID:
            return self.__get_fibonacci_wave_numbers__(index, symbol, 200)
        elif column == RDC.FIBONACCI_LONG:
            return self.__get_fibonacci_wave_numbers__(index, symbol, 400)
        elif column == RDC.SCORING_POINTS:
            return self.__get_scoring_points_based_on_database__(index, symbol)
        elif column == RDC.PORTFOLIO: return 'No'

    def __get_fibonacci_wave_numbers__(self, index: str, symbol: str, key_int: int) -> str:
        if symbol in self._wave_for_ticker_dict:
            ticker_dict = self._wave_for_ticker_dict[symbol]
            key, key_actual = str(key_int), '{}_a'.format(key_int)
            return '{}/{}'.format(ticker_dict[key], ticker_dict[key_actual])
        return '0'

    def __get_scoring_points_based_on_database__(self, index: str, symbol: str):
        points = 0
        if symbol in self._wave_for_ticker_dict:
            ticker_dict = self._wave_for_ticker_dict[symbol]
            for criteria in RWC.get_list():
                if ticker_dict[criteria] > 0:
                    points += RWC.get_scoring_point(criteria)
        return points

    def __is_row_for_symbol_available__(self, symbol: str) -> bool:
        return symbol in self._symbols

    def __get_exchange_dict__(self) -> dict:
        return {index: self._data_provider.get_index_members_as_dict(index) for index in self._indices}

