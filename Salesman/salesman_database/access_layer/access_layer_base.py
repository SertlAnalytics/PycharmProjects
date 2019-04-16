"""
Description: This module contains the access layer base class for Salesman
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.datafetcher.database_fetcher import DatabaseDataFrame
from salesman_database.salesman_db import SalesmanDatabase
import pandas as pd
from sertl_analytics.datafetcher.database_fetcher import MyTable
from sertl_analytics.constants.salesman_constants import SLDC, DC, SMTBL


class AccessLayer:
    def __init__(self, db: SalesmanDatabase=None):
        self._db = SalesmanDatabase() if db is None else db
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

    def select_data_by_data_dict(
            self, data_dict: dict, target_columns=None, sort_columns=None, index_col='') -> pd.DataFrame:
        query = self._table.get_query_select_by_data_dict(data_dict, target_columns, sort_columns)
        db_df = DatabaseDataFrame(self._db, query)
        return self.__get_dataframe_with_index_column__(db_df.df, index_col)

    def select_data_by_query(self, query: str, index_col='') -> pd.DataFrame:
        db_df = DatabaseDataFrame(self._db, query)
        return self.__get_dataframe_with_index_column__(db_df.df, index_col)

    @staticmethod
    def __get_dataframe_with_index_column__(df: pd.DataFrame, index_col: str):
        if not df.empty and index_col != '':
            df.set_index(index_col, drop=False, inplace=True)
        return df

    def insert_data(self, input_dict_list: list):
        self._db.insert_data_into_table(self._table.name, input_dict_list)

    def update_record(self, record_id: str, data_dict: dict):
        # Syntax: UPDATE users SET field1='value1', field2='value2'
        pass

    def delete_record_by_id(self, record_id: str):
        pass

    def delete_record_by_rowid(self, rowid: int):
        query = self._table.get_query_delete_by_row_id(rowid)
        print(query)
        self._db.delete_records(query)

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
        db_df = DatabaseDataFrame(self._db, query)
        return db_df.df

    def __get_table__(self) -> MyTable:
        pass

    def get_update_set_clause_from_data_dict(self, data_dict: dict):
        return self._table.get_update_set_clause_from_data_dict(data_dict)


class SalesmanDatabaseDataFrame(DatabaseDataFrame):
    def __init__(self, db: SalesmanDatabase, offer_id_master: str):
        self.offer_id_master = offer_id_master
        self.statement = "SELECT * from {} WHERE {} = '{}'".format(SMTBL.SALE, SLDC.SALE_ID_MASTER, offer_id_master)
        DatabaseDataFrame.__init__(self, db, self.statement)
        if self.df.shape[0] == 0:
            self.df_data = None
