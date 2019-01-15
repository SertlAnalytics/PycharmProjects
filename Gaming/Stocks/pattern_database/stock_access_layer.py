"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


from sertl_analytics.datafetcher.database_fetcher import BaseDatabase, DatabaseDataFrame
from sertl_analytics.mydates import MyDate
from pattern_database.stock_tables import MyTable, PatternTable, TradeTable, StocksTable, \
    CompanyTable, STBL, WaveTable, AssetTable, MetricTable, EquityTable
from pattern_database.stock_database import StockDatabase
import pandas as pd
import math
from sertl_analytics.datafetcher.database_fetcher import MyTable
from sertl_analytics.constants.pattern_constants import INDICES, CN, DC, PRD, MDC, EDC, TRC


class AccessLayer:
    def __init__(self, stock_db: StockDatabase):
        self._stock_db = stock_db
        self._table = self.__get_table__()

    @property
    def table_name(self):
        return self._table.name

    def get_all_as_data_frame(self, index_col=''):
        return self.select_data_by_query("SELECT * from {}".format(self._table.name), index_col)

    def get_all_as_data_dict(self, index_col: str):
        df = self.select_data_by_query("SELECT * from {}".format(self._table.name), index_col)
        return df.to_dict(orient='index')

    def get_as_data_dict_by_data_dict(self, data_dict: dict, sort_columns=None, index_col=''):
        df = self.select_data_by_data_dict(data_dict, target_columns=None, sort_columns=sort_columns, index_col=index_col)
        return df.to_dict(orient='index')

    def select_data_by_data_dict(self, data_dict: dict, target_columns=None, sort_columns=None, index_col='') -> pd.DataFrame:
        query = self._table.get_query_select_by_data_dict(data_dict, target_columns, sort_columns)
        db_df = DatabaseDataFrame(self._stock_db, query)
        return self.__get_dataframe_with_index_column__(db_df.df, index_col)

    def select_data_by_query(self, query: str, index_col='') -> pd.DataFrame:
        db_df = DatabaseDataFrame(self._stock_db, query)
        return self.__get_dataframe_with_index_column__(db_df.df, index_col)

    @staticmethod
    def __get_dataframe_with_index_column__(df: pd.DataFrame, index_col: str):
        if not df.empty and index_col != '':
            df.set_index(index_col, drop=False, inplace=True)
        return df

    def insert_data(self, input_dict_list: list):
        self._stock_db.insert_data_into_table(self._table.name, input_dict_list)

    def update_record(self, record_id: str, data_dict: dict):
        pass

    def delete_record_by_id(self, record_id: str):
        pass

    def delete_record_by_rowid(self, rowid: int):
        query = self._table.get_query_delete_by_row_id(rowid)
        print(query)
        self._stock_db.delete_records(query)

    def delete_existing_record(self, data_dict: dict):
        df = self.__get_data_frame_with_row_id__(data_dict)
        if df.shape[0] > 0:
            self.delete_record_by_rowid(df.iloc[0][DC.ROWID])
        else:
            print('Nothing to delete for table {}: {}'.format(self._table.name, data_dict))

    def is_record_available(self, data_dict: dict):
        df = self.__get_data_frame_with_row_id__(data_dict)
        return df.shape[0] > 0

    def are_any_records_available(self, data_dict: dict):
        df = self.__get_data_frame_with_row_id__(data_dict)
        return df.shape[0] > 0

    def __get_data_frame_with_row_id__(self, data_dict: dict) -> pd.DataFrame:
        query = self._table.get_query_select_for_unique_record_by_dict(data_dict)
        return self.__get_data_frame_with_row_id_by_query__(query)

    def __get_data_frame_with_row_id_by_query__(self, query: str) -> pd.DataFrame:
        db_df = DatabaseDataFrame(self._stock_db, query)
        return db_df.df

    def __get_table__(self) -> MyTable:
        pass


class AccessLayer4Equity(AccessLayer):
    def are_any_records_available_for_date(self, date: str, exchange: str, equity_type: str):
        query = "SELECT * from {} WHERE {} >= '{}' and {}='{}' and {}='{}'".format(
            self.table_name, EDC.VALID_TO_DT, date, EDC.EXCHANGE, exchange, EDC.EQUITY_TYPE, equity_type
        )
        df = self.__get_data_frame_with_row_id_by_query__(query)
        return df.shape[0] > 0

    def get_existing_equities_as_data_dict(self, equity_type: str, exchange: str):
        data_dict = {EDC.EQUITY_TYPE: equity_type, EDC.EXCHANGE: exchange}
        return self.get_as_data_dict_by_data_dict(data_dict, [EDC.EQUITY_KEY])

    def get_index_dict(self, index: str):
        data_dict = {EDC.EXCHANGE: TRC.BITFINEX} if index == INDICES.CRYPTO_CCY else {EDC.EXCHANGE: index}
        full_dict = self.get_as_data_dict_by_data_dict(data_dict, [EDC.EQUITY_KEY], EDC.EQUITY_KEY)
        return {value_dict[EDC.EQUITY_KEY]: value_dict[EDC.EQUITY_NAME] for value_dict in full_dict.values()}

    def delete_existing_equities(self, equity_type: str, exchange: str):
        query = "DELETE FROM {} WHERE {}='{}' and {}='{}';".format(
            self._table.name, EDC.EQUITY_TYPE, equity_type, EDC.EXCHANGE, exchange)
        print(query)
        self._stock_db.delete_records(query)

    def __get_table__(self):
        return EquityTable()


class AccessLayer4Asset(AccessLayer):
    def __get_table__(self):
        return AssetTable()


class AccessLayer4Metric(AccessLayer):
    def __get_table__(self):
        return MetricTable()

    def get_actual_metric_data_frame(self) -> pd.DataFrame:
        dt_today = MyDate.get_date_as_string_from_date_time()
        # dt_today = '2018-12-22'
        return self.select_data_by_data_dict({MDC.VALID_DT: dt_today})


class AccessLayer4Stock(AccessLayer):
    def __get_table__(self):
        return StocksTable()

    def get_all_as_data_frame(self, symbol=''):
        if symbol == '':
            return self.select_data_by_query("SELECT * from {} ORDER BY {}".format(self._table.name, DC.TIMESTAMP))
        else:
            return self.select_data_by_query("SELECT * from {} WHERE symbol = '{}' ORDER BY {}".format(
                self._table.name, symbol, DC.TIMESTAMP))

    def get_actual_price_for_symbol(self, symbol: str, ts_from: int) -> float:
        query = "SELECT * FROM {} WHERE symbol='{}' AND Timestamp >= {} LIMIT 1".format(
            self._table.name, symbol, ts_from)
        df_result = self.select_data_by_query(query)
        if df_result.empty:
            return 0
        return df_result.iloc[0][DC.CLOSE]


class AccessLayer4Pattern(AccessLayer):
    def __get_table__(self):
        return PatternTable()


class AccessLayer4Trade(AccessLayer):
    def __get_table__(self):
        return TradeTable()


class StockInsertData:
    def __init__(self):
        self.time_stamp = 0
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.volume = 0
        self._big_move = False
        self._direction = 0

    def set_direction_big_move(self, close_previous: float):
        if self.close != 0:
            if abs((close_previous - self.close) / self.close) > 0.03:
                self._big_move = True
                self._direction = math.copysign(1, self.close - close_previous)

    def get_dict_for_input(self, symbol: str, period: str, aggregation: int):
        if math.isnan(self.high):
            return {}
        date_time = MyDate.get_date_time_from_epoch_seconds(self.time_stamp)
        return {CN.PERIOD: period, CN.AGGREGATION: aggregation, CN.SYMBOL: symbol,
                CN.TIMESTAMP: self.time_stamp, CN.DATE: date_time.date(), CN.TIME: date_time.time(),
                CN.OPEN: self.open, CN.HIGH: self.high, CN.LOW: self.low, CN.CLOSE: self.close,
                CN.VOL: self.volume, CN.BIG_MOVE: self._big_move, CN.DIRECTION: self._direction}


class StockInsertHandler:
    def __init__(self, symbol: str, period: str, aggregation: int):
        self._symbol = symbol
        self._period = period
        self._aggregation = aggregation
        self._previous_close = 0
        self._input_dict_list = []

    @property
    def input_dict_list(self):
        return self._input_dict_list

    def add_data_frame_row(self, time_stamp: int, row):
        insert_data = StockInsertData()
        insert_data.time_stamp = time_stamp
        insert_data.open = float(row[CN.OPEN])
        insert_data.high = float(row[CN.HIGH])
        insert_data.low = float(row[CN.LOW])
        insert_data.close = float(row[CN.CLOSE])
        insert_data.volume = float(row[CN.VOL])
        self.__add_insert_data_to_list__(insert_data)

    def add_wave_tick(self, wave_tick):
        insert_data = StockInsertData()
        insert_data.time_stamp = wave_tick.time_stamp
        insert_data.open = wave_tick.open
        insert_data.high = wave_tick.high
        insert_data.low = wave_tick.low
        insert_data.close = wave_tick.close
        insert_data.volume = wave_tick.volume
        self.__add_insert_data_to_list__(insert_data)

    def __add_insert_data_to_list__(self, insert_data):
        insert_data.set_direction_big_move(self._previous_close)
        self._previous_close = insert_data.close
        input_dict = insert_data.get_dict_for_input(self._symbol, self._period, self._aggregation)
        if len(input_dict) > 0:
            self._input_dict_list.append(input_dict)


class StockDatabaseDataFrame(DatabaseDataFrame):
    def __init__(self, db: StockDatabase, symbol='', and_clause='', period=PRD.DAILY, aggregation=1):
        self.symbol = symbol
        self.statement = "SELECT * from {} WHERE Symbol = '{}' and Period = '{}' and Aggregation = {}".format(
            STBL.STOCKS, symbol, period, aggregation)
        if and_clause != '':
            self.statement += ' and ' + and_clause
        DatabaseDataFrame.__init__(self, db, self.statement)
        if self.df.shape[0] == 0:
            self.df_data = None
        else:
            self.df.set_index(CN.TIMESTAMP, drop=False, inplace=True)
            self.column_data = [CN.CLOSE]
            self.df_data = self.df[[CN.OPEN, CN.HIGH, CN.LOW, CN.CLOSE, CN.VOL, CN. TIMESTAMP, CN.BIG_MOVE, CN.DIRECTION]]




