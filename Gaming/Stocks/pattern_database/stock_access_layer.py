"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.datafetcher.database_fetcher import BaseDatabase, DatabaseDataFrame
from sertl_analytics.mydates import MyDate
from pattern_database.stock_tables import MyTable, PatternTable, TradeTable, StocksTable, \
    CompanyTable, STBL, WaveTable, AssetTable, MetricTable, EquityTable, TradePolicyMetricTable, ProcessTable
from pattern_database.stock_database import StockDatabase
from pattern_wave_tick import WaveTick, WaveTickList
import pandas as pd
import math
import numpy as np
from sertl_analytics.datafetcher.database_fetcher import MyTable
from sertl_analytics.constants.pattern_constants import INDICES, CN, DC, PRD, MDC, EDC, TRC, TPMDC, PRDC, FD


class AccessLayer:
    def __init__(self, stock_db: StockDatabase=None):
        self._stock_db = StockDatabase() if stock_db is None else stock_db
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


class AccessLayer4Process(AccessLayer):
    def __get_table__(self):
        return ProcessTable()

    def is_process_available_for_today(self, process: str) -> pd.DataFrame:
        dt_today = MyDate.get_date_as_string_from_date_time()  # e.g. dt_today = '2018-12-22'
        df = self.select_data_by_data_dict({PRDC.PROCESS: process, PRDC.START_DT: dt_today})
        return df.shape[0] > 0


class AccessLayer4Metric(AccessLayer):
    def __get_table__(self):
        return MetricTable()

    def get_actual_metric_data_frame(self) -> pd.DataFrame:
        dt_today = MyDate.get_date_as_string_from_date_time()
        # dt_today = '2018-12-22'
        return self.select_data_by_data_dict({MDC.VALID_DT: dt_today})


class AccessLayer4TradePolicyMetric(AccessLayer):
    def __get_table__(self):
        return TradePolicyMetricTable()

    def get_actual_metric_data_frame(self) -> pd.DataFrame:
        dt_today = MyDate.get_date_as_string_from_date_time()  # dt_today = '2018-12-22'
        return self.select_data_by_data_dict({MDC.VALID_DT: dt_today})

    def get_metric_data_frame_for_sell_coded_trades(self) -> pd.DataFrame:
        df = self.select_data_by_data_dict({TPMDC.POLICY: 'TradePolicySellCodedTrade'})
        return df


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

    def get_wave_tick_list_for_time_stamp_interval(self, symbol: str, ts_from: int, ts_to: int):
        df = self.select_data_by_query(
            "SELECT * from {} WHERE symbol = '{}' AND {} BETWEEN {} and {} ORDER BY {}".format(
                self._table.name, symbol, DC.TIMESTAMP, ts_from, ts_to, DC.TIMESTAMP))
        return WaveTickList(df)

    def get_wave_tick_lists_for_time_stamp_intervals(self, symbol: str, ts_list: list) -> list:
        # this is used for a faster access to several consequetive timestames (before_pattern, pattern, after_pattern)
        wave_tick_list_return = []
        ts_from = ts_list[0]
        ts_to = ts_list[-1]
        df = self.select_data_by_query(
            "SELECT * from {} WHERE symbol = '{}' AND {} BETWEEN {} and {} ORDER BY {}".format(
                self._table.name, symbol, DC.TIMESTAMP, ts_from, ts_to, DC.TIMESTAMP))
        for k in range(0, len(ts_list)-1):
            df_part = df[np.logical_and(df[DC.TIMESTAMP] >= ts_list[k], df[DC.TIMESTAMP] < ts_list[k+1])]
            wave_tick_list_return.append(WaveTickList(df_part))
        return wave_tick_list_return


class AccessLayer4Pattern(AccessLayer):
    def __get_table__(self):
        return PatternTable()


class AccessLayer4Trade(AccessLayer):
    def __get_table__(self):
        return TradeTable()


class AccessLayer4Wave(AccessLayer):
    def __get_table__(self):
        return WaveTable()

    def get_intraday_wave_data_frame(self) -> pd.DataFrame:
        order_by_columns = ','.join([DC.TICKER_ID, DC.WAVE_END_DT])
        query = "SELECT * FROM {} WHERE {}={} ORDER BY {}".format(self._table.name, DC.PERIOD_ID, 0, order_by_columns)
        return self.select_data_by_query(query)

    def get_daily_wave_data_frame(self) -> pd.DataFrame:
        order_by_columns = ','.join([DC.TICKER_ID, DC.WAVE_END_DT])
        query = "SELECT * FROM {} WHERE {}={} ORDER BY {}".format(self._table.name, DC.PERIOD_ID, 1, order_by_columns)
        return self.select_data_by_query(query)

    def get_multiple_intraday_wave_data_frame(self, period_id=0) -> pd.DataFrame:
        query = "Select Equity_Type, Period, Period_ID, Ticker_ID, Ticker_Name, Wave_Type," \
                " W1_Begin_Timestamp, W1_Begin_Datetime, W1_Begin_Value," \
                " Wave_End_Datetime, Wave_End_Value, Wave_End_Timestamp, count(*) as counter," \
                " 0 as Day_01, 0 as Day_02, 0 as Day_03, 0 as Day_04, 0 as Day_05, 0 as Day_Max" \
                " from Wave" \
                " where Period_ID = {}" \
                " group by Ticker_ID, Wave_Type, W1_Begin_Timestamp, Wave_End_Timestamp" \
                " having count(*) > 1" \
                " ORDER by Ticker_ID, W1_Begin_Timestamp, Wave_End_Timestamp".format(period_id)
        return self.select_data_by_query(query)

    def get_multiple_intraday_wave_data_frame_with_corresponding_daily_wave_data(self, period_id=0) -> pd.DataFrame:
        df_intraday = self.get_multiple_intraday_wave_data_frame(period_id)
        df_stocks = self._stock_db.select_data_by_query("SELECT * FROM Stocks WHERE Period = 'DAILY'")
        key_list = []
        row_dict = {}
        for index, row in df_intraday.iterrows():
            wave_type = row[DC.WAVE_TYPE]
            value_end = row[DC.WAVE_END_VALUE]
            ts_end = row[DC.WAVE_END_TS]
            ts_daily_start = ts_end - 86400
            ts_daily_end = ts_daily_start + 86400 * 10
            ticker_id = row[DC.TICKER_ID]
            day_str = row[DC.WAVE_END_DT].split(' ')[0]
            key = '{}_{}'.format(ticker_id, day_str)
            counter = 0
            day_max = -math.inf
            if key not in key_list:
                df_filtered_stocks = df_stocks[np.logical_and(df_stocks[DC.SYMBOL] == ticker_id,
                                                              df_stocks[DC.TIMESTAMP] >= ts_daily_start)]
                key_list.append(key)
                for index_stocks, row_stocks in df_filtered_stocks.iterrows():
                    row_low, row_high = row_stocks[DC.LOW], row_stocks[DC.HIGH]
                    if day_str == row_stocks[DC.DATE]:  # check values
                        if not (row_low <= value_end <= row_high):
                            print('{}-{}: value not in range of date {}: {} not in [{}, {}]'.format(
                              index, ticker_id, day_str, value_end, row_low, row_high
                            ))
                            break
                    else:
                        counter += 1
                        if wave_type == FD.ASC:
                            day_value = round((value_end - row_low)/value_end * 100, 2)

                        else:
                            day_value = round((row_high - value_end) / value_end * 100, 2)
                        row['Day_0{}'.format(counter)] = day_value
                        day_max = day_value if day_value > day_max else day_max
                        if counter == 5:
                            row['Day_Max'] = day_max
                            break
                if counter == 5:
                    row_dict[key] = row
        df_result = pd.DataFrame([row for row in row_dict.values()])
        return df_result

    def get_intraday_wave_data_frame_with_corresponding_daily_wave_data(self) -> pd.DataFrame:
        df_intraday = self.get_intraday_wave_data_frame()
        df_daily = self.get_daily_wave_data_frame()
        key_list = []
        row_dict = {}
        for index, row in df_intraday.iterrows():
            ticker_id = row[DC.TICKER_ID]
            day_str = row[DC.WAVE_END_DT].split(' ')[0]
            key = '{}_{}'.format(ticker_id, day_str)
            if key not in key_list:
                key_list.append(key)
                df_daily_ticker = df_daily[df_daily[DC.TICKER_ID] == ticker_id]
                for index_daily, row_daily in df_daily_ticker.iterrows():
                    day_str_daily = row_daily[DC.WAVE_END_DT].split(' ')[0]
                    if day_str == day_str_daily:
                        row[DC.WAVE_END_TS] = row_daily[DC.WAVE_END_TS]  # we want to have the daily timestamp
                        row_dict[key] = row
        df_result = pd.DataFrame([row for row in row_dict.values()])
        df_result = df_result[[DC.TICKER_ID, DC.TICKER_NAME, DC.WAVE_TYPE, DC.WAVE_TYPE_ID,
                               DC.WAVE_END_DT, DC.WAVE_END_VALUE, DC.WAVE_END_TS]]
        return df_result


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



