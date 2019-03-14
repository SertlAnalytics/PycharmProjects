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
from sertl_analytics.constants.pattern_constants import INDICES, CN, DC, PRD, MDC, EDC, TRC, TPMDC, PRDC, FD, WPDT


class AccessLayer:
    def __init__(self, stock_db: StockDatabase=None):
        self._stock_db = StockDatabase() if stock_db is None else stock_db
        self._table = self.__get_table__()

    @property
    def table_name(self):
        return self._table.name

    def get_all_as_data_frame(self, index_col='', columns=None, where_clause=''):
        selected_columns = '*' if columns is None else ','.join(columns)
        where_clause_new = '' if where_clause == '' else ' WHERE {}'.format(where_clause)
        return self.select_data_by_query("SELECT {} from {}{}".format(
            selected_columns, self._table.name, where_clause_new), index_col)

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
        # Syntax: UPDATE users SET field1='value1', field2='value2'
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
        query = self._table.get_query_select_by_data_dict(data_dict)
        return self.__get_data_frame_with_row_id_by_query__(query)

    def __get_data_frame_with_row_id_by_query__(self, query: str) -> pd.DataFrame:
        db_df = DatabaseDataFrame(self._stock_db, query)
        return db_df.df

    def __get_table__(self) -> MyTable:
        pass

    def get_update_set_clause_from_data_dict(self, data_dict: dict):
        return self._table.get_update_set_clause_from_data_dict(data_dict)


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

    def get_all_as_data_frame(self, symbol='', columns=None, where_clause=''):
        if symbol == '':
            where_clause_new = '' if where_clause == '' else ' WHERE {}'.format(where_clause)
        else:
            where_clause_new = " WHERE symbol = '{}'".format(symbol)
            where_clause_new += '' if where_clause == '' else ' AND {}'.format(where_clause)
        return self.select_data_by_query("SELECT * from {}{} ORDER BY {}".format(
            self._table.name, where_clause_new, DC.TIMESTAMP))

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

    def get_stocks_data_frame_for_wave_completing(self, symbol='', ts_start=0) -> pd.DataFrame:
        symbol_clause = '' if symbol == '' else " AND {} = '{}'".format(DC.SYMBOL, symbol)
        ts_start_clause = '' if ts_start == 0 else " AND {} >= {}".format(DC.TIMESTAMP, ts_start)
        parameter_clauses = '{}{}'.format(symbol_clause, ts_start_clause)
        query = "SELECT rowid, * FROM {} WHERE Period = '{}'{}".format(
            self.table_name, PRD.DAILY, parameter_clauses)
        return self.select_data_by_query(query)


class AccessLayer4Pattern(AccessLayer):
    def __get_table__(self):
        return PatternTable()


class AccessLayer4Trade(AccessLayer):
    def __get_table__(self):
        return TradeTable()


class AccessLayer4Wave(AccessLayer):
    def __get_table__(self):
        return WaveTable()

    def is_wave_available_after_wave_end_ts(self, wave_end_ts, period='') -> bool:
        where_clause = ' WHERE {}>{}'.format(DC.WAVE_END_TS, wave_end_ts)
        if period != '':
            where_clause += " AND {}='{}'".format(DC.PERIOD, period)
        query = "SELECT count(*) as Number from {}{}".format(self._table.name, where_clause)
        df = self.select_data_by_query(query)
        number = df.values[0, 0]
        return number > 0

    def get_all_as_data_frame(self, index_col='', columns=None, where_clause=''):
        # With calculated columns "Index" and "Wave_End_Date"
        query = self.__get_query_for_wave_view__(where_clause=where_clause, columns=columns)
        # print('get_all_as_data_frame: query={}'.format(query))
        return self.select_data_by_query(query, index_col)

    @staticmethod
    def __get_query_for_wave_view__(where_clause: str, columns):  # With calculated columns "Index" and "Wave_End_Date"
        selected_columns = '*' if columns is None else ','.join(columns)
        query = "SELECT {} FROM v_wave".format(selected_columns)
        if where_clause != '':
            query += ' WHERE {}'.format(where_clause)
        return query + ' ORDER BY {};'.format(DC.WAVE_END_TS)

    def update_record(self, record_id: str, data_dict: dict):
        set_clause = self.get_update_set_clause_from_data_dict(data_dict)
        stmt = "UPDATE {} SET {} WHERE rowid={}".format(self._table.name, set_clause, record_id)
        self._stock_db.update_table_by_statement(self._table.name, stmt)

    def get_intraday_wave_data_frame(self, where_clause_input='') -> pd.DataFrame:
        where_clause_input = '' if where_clause_input == '' else ' AND {}'.format(where_clause_input)
        where_clause = 'WHERE {}={}{}'.format(DC.PERIOD_ID, 0, where_clause_input)
        order_by_columns = ','.join([DC.WAVE_END_TS, DC.TICKER_ID])
        query = "SELECT * FROM {} {} ORDER BY {}".format(self._table.name, where_clause, order_by_columns)
        return self.select_data_by_query(query)

    def get_grouped_by_for_wave_plotting(self):
        columns = [DC.EQUITY_INDEX, DC.PERIOD, DC.PERIOD_AGGREGATION, DC.WAVE_TYPE, DC.WAVE_END_DATE, DC.TICKER_ID]
        df = self.get_all_as_data_frame(columns=columns)
        return df.groupby(columns[:-1]).count()

    def get_grouped_by_for_wave_peak_plotting(self, wave_peak_date_type: str, aggregation=1, offset_date=''):
        if wave_peak_date_type in [WPDT.DAILY_DATE, WPDT.INTRADAY_DATE]:
            where_clause = "{}='{}'".format(
                DC.PERIOD, PRD.DAILY if wave_peak_date_type == WPDT.DAILY_DATE else PRD.INTRADAY)
            columns = [DC.EQUITY_INDEX, DC.PERIOD, DC.PERIOD_AGGREGATION, DC.WAVE_TYPE, DC.WAVE_END_DATE, DC.TICKER_ID]
        else:  # here we take only the intraday waves with the proper aggregation
            columns = [DC.EQUITY_INDEX, DC.PERIOD, DC.PERIOD_AGGREGATION, DC.WAVE_TYPE, DC.WAVE_END_TS,
                       DC.WAVE_END_DT, DC.TICKER_ID]
            offset_ts = MyDate.get_offset_timestamp(days=-10)
            where_clause = "{}='{}' AND {}>{} AND {}={}".format(
                DC.PERIOD, PRD.INTRADAY, DC.WAVE_END_TS, offset_ts, DC.PERIOD_AGGREGATION, aggregation)
        if offset_date != '':
            where_clause += " AND {}>'{}'".format(DC.WAVE_END_DATE, offset_date)
        df = self.get_all_as_data_frame(columns=columns, where_clause=where_clause)
        if df.empty:
            return df
        df = df.groupby(columns[:-1]).count()
        return df.reset_index(drop=False)

    def get_daily_wave_data_frame(self, where_clause_input='') -> pd.DataFrame:
        where_clause_input = '' if where_clause_input == '' else ' AND {}'.format(where_clause_input)
        where_clause = 'WHERE {}={}{}'.format(DC.PERIOD_ID, 1, where_clause_input)
        order_by_columns = ','.join([DC.WAVE_END_TS, DC.TICKER_ID])
        query = "SELECT * FROM {} {} ORDER BY {}".format(self._table.name, where_clause, order_by_columns)
        return self.select_data_by_query(query)

    def get_multiple_wave_data_frame(self, period_id=0, days=5) -> pd.DataFrame:
        days_list = ['{} as Day_0{}'.format(0, k) for k in range(1, days+1)]
        days_list.append('0 as Day_Max')
        days_list.append('0 as Day_Max_Retracement')
        days_columns = ', '.join(days_list)
        query = "Select Equity_Type, Period, Period_ID, Ticker_ID, Ticker_Name, Wave_Type, " \
                " W1_Begin_Timestamp, W1_Begin_Datetime, W1_Begin_Value," \
                " Wave_End_Datetime, Wave_End_Value, Wave_End_Timestamp, count(*) as counter, {}" \
                " from Wave" \
                " where Period_ID = {}" \
                " group by Ticker_ID, Wave_Type, W1_Begin_Timestamp, Wave_End_Timestamp" \
                " having count(*) > 1" \
                " ORDER by Ticker_ID, W1_Begin_Timestamp, Wave_End_Timestamp".format(days_columns, period_id)
        return self.select_data_by_query(query)

    def get_single_wave_data_frame(self, period_id=0, days=5) -> pd.DataFrame:
        days_list = ['{} as Day_0{}'.format(0, k) for k in range(1, days+1)]
        days_list.append('0 as Day_Max')
        days_list.append('0 as Day_Max_Retracement')
        days_columns = ', '.join(days_list)
        query = "Select Equity_Type, Period, Period_ID, Ticker_ID, Ticker_Name, Wave_Type, Wave_Structure, " \
                " W1_Begin_Timestamp, W1_Begin_Datetime, W1_Begin_Value," \
                " Wave_End_Datetime, Wave_End_Value, Wave_End_Timestamp, {}" \
                " from Wave" \
                " where Period_ID = {}" \
                " ORDER by Ticker_ID, W1_Begin_Timestamp, Wave_End_Timestamp".format(days_columns, period_id)
        return self.select_data_by_query(query)

    def get_base_wave_data_frame_for_prediction(self, symbol='') -> pd.DataFrame:
        symbol_part = '' if symbol == '' else " AND Ticker_ID = '{}'".format(symbol)
        query = "SELECT * FROM Wave " \
                " WHERE Period_ID = 1 AND {} in (0, 1){}" \
                " ORDER by Ticker_ID, W1_Begin_Timestamp, Wave_End_Timestamp".format(
            DC.WAVE_END_FLAG, symbol_part)
        return self.select_data_by_query(query)

    def get_wave_data_frame_without_end_data(self, symbol='', ts_start=0, ts_end=0) -> pd.DataFrame:
        symbol_clause = '' if symbol == '' else " AND {}='{}'".format(DC.TICKER_ID, symbol)
        ts_start_clause = '' if ts_start == 0 else " AND {}={}".format(DC.W1_BEGIN_TS, ts_start)
        ts_end_clause = '' if ts_end == 0 else " AND {}={}".format(DC.WAVE_END_TS, ts_end)
        parameter_clauses = '{}{}{}'.format(symbol_clause, ts_start_clause, ts_end_clause)
        query = "SELECT {}, * FROM {} WHERE Period = '{}' AND {} not in (0,1){} ORDER BY {}".format(
            DC.ROWID, self.table_name, PRD.DAILY, DC.WAVE_END_FLAG, parameter_clauses, DC.TICKER_ID)
        return self.select_data_by_query(query)

    def get_wave_data_without_prediction_data(self, symbol='', ts_start=0, ts_end=0) -> pd.DataFrame:
        symbol_clause = '' if symbol == '' else " AND {}='{}'".format(DC.TICKER_ID, symbol)
        ts_start_clause = '' if ts_start == 0 else " AND {}={}".format(DC.W1_BEGIN_TS, ts_start)
        ts_end_clause = '' if ts_end == 0 else " AND {}={}".format(DC.WAVE_END_TS, ts_end)
        parameter_clauses = '{}{}{}'.format(symbol_clause, ts_start_clause, ts_end_clause)
        query = "SELECT {}, * FROM {} WHERE {} not in (0,1){} ORDER BY {}".format(
            DC.ROWID, self.table_name, DC.FC_C_WAVE_END_FLAG, parameter_clauses, DC.TICKER_ID)
        return self.select_data_by_query(query)

    def get_wave_data_frame_with_corresponding_daily_wave_data_for_prediction(self) -> pd.DataFrame:
        df_intraday = self.get_base_wave_data_frame_for_prediction()
        df_stocks = self._stock_db.select_data_by_query("SELECT * FROM Stocks WHERE Period = 'DAILY'")
        key_list = []
        row_dict = {}
        for index, row in df_intraday.iterrows():
            wave_type = row[DC.WAVE_TYPE]
            value_start = row[DC.W1_BEGIN_VALUE]
            value_end = row[DC.WAVE_END_VALUE]
            wave_hight = abs(value_start - value_end)
            ts_end = row[DC.WAVE_END_TS]
            ts_daily_start = ts_end
            ts_daily_end = ts_daily_start + 86400 * 1 * 2  # to consider weekends (factor 2)
            ticker_id = row[DC.TICKER_ID]
            day_str = row[DC.WAVE_END_DT].split(' ')[0]
            key = '{}_{}'.format(ticker_id, day_str)
            day_counter = 0
            day_max = -math.inf
            day_max_retracement = -math.inf
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
                        day_counter += 1
                        if wave_type == FD.ASC:
                            day_value = round((value_end - row_low)/value_end * 100, 2)
                            day_value_retracement = round((value_end - row_low)/wave_hight * 100, 2)
                        else:
                            day_value = round((row_high - value_end) / value_end * 100, 2)
                            day_value_retracement = round((row_high - value_end) / wave_hight * 100, 2)
                        row['Day_0{}'.format(day_counter)] = day_value
                        if day_value > day_max:
                            day_max = day_value
                        if day_value_retracement > day_max_retracement:
                            day_max_retracement = day_value_retracement
                        if day_counter == 1:
                            row['Day_Max'] = day_max
                            row['Day_Max_Retracement'] = day_max_retracement
                            break
                if day_counter == 1:
                    row_dict[key] = row
        df_result = pd.DataFrame([row for row in row_dict.values()])
        return df_result

    def get_multiple_wave_data_frame_with_corresponding_daily_wave_data(self, period_id=0, days=5) -> pd.DataFrame:
        return self.__get_wave_data_frame_with_corresponding_daily_wave_data__(True, period_id, days)

    def get_wave_data_frame_with_corresponding_daily_wave_data(self, period_id=0, days=5) -> pd.DataFrame:
        return self.__get_wave_data_frame_with_corresponding_daily_wave_data__(False, period_id, days)

    def __get_wave_data_frame_with_corresponding_daily_wave_data__(
            self, multiple=False, period_id=0, days=5) -> pd.DataFrame:
        if multiple:
            df_intraday = self.get_multiple_wave_data_frame(period_id, days)
        else:
            df_intraday = self.get_single_wave_data_frame(period_id, days)
        df_stocks = self._stock_db.select_data_by_query("SELECT * FROM Stocks WHERE Period = 'DAILY'")
        key_list = []
        row_dict = {}
        for index, row in df_intraday.iterrows():
            wave_type = row[DC.WAVE_TYPE]
            value_start = row[DC.W1_BEGIN_VALUE]
            value_end = row[DC.WAVE_END_VALUE]
            wave_hight = abs(value_start - value_end)
            ts_end = row[DC.WAVE_END_TS]
            ts_daily_start = ts_end
            ts_daily_end = ts_daily_start + 86400 * days * 2  # to consider weekends (factor 2)
            ticker_id = row[DC.TICKER_ID]
            day_str = row[DC.WAVE_END_DT].split(' ')[0]
            key = '{}_{}'.format(ticker_id, day_str)
            day_counter = 0
            day_max = -math.inf
            day_max_retracement = -math.inf
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
                        day_counter += 1
                        if wave_type == FD.ASC:
                            day_value = round((value_end - row_low)/value_end * 100, 2)
                            day_value_retracement = round((value_end - row_low)/wave_hight * 100, 2)
                        else:
                            day_value = round((row_high - value_end) / value_end * 100, 2)
                            day_value_retracement = round((row_high - value_end) / wave_hight * 100, 2)
                        row['Day_0{}'.format(day_counter)] = day_value
                        if day_value > day_max:
                            day_max = day_value
                        if day_value_retracement > day_max_retracement:
                            day_max_retracement = day_value_retracement
                        if day_counter == days:
                            row['Day_Max'] = day_max
                            row['Day_Max_Retracement'] = day_max_retracement
                            break
                if day_counter == days:
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




