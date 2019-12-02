"""
Description: This module is the main module for database connections.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""

import pandas as pd
from sqlalchemy import MetaData, Table, insert, exc, text, Column, String, Float, Boolean, Integer, Date, create_engine
from sqlalchemy_views import CreateView, DropView
import os
import sys
from sertl_analytics.myexceptions import ErrorHandler
from sertl_analytics.myfilelog import FileLog
from time import sleep
from sertl_analytics.constants.pattern_constants import DC


class CDT:  # Column Data Types
    STRING = 'String'
    INTEGER = 'Integer'
    FLOAT = 'Float'
    DATE = 'Date'
    TIME = 'Time'
    BOOLEAN = 'Boolean'


class MyTableColumn:
    def __init__(self, column_name: str, data_type='String', data_size='', default=''):
        self._name = column_name
        self._type = data_type
        self._size = data_size
        self._default = default
        self._description = self.__get_description__()

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def is_numeric(self):
        return self._type in [CDT.FLOAT, CDT.INTEGER, CDT.BOOLEAN]

    @property
    def is_float(self):
        return self._type == CDT.FLOAT

    @property
    def is_integer(self):
        return self._type == CDT.INTEGER

    @property
    def is_boolean(self):
        return self._type == CDT.BOOLEAN

    @property
    def is_string(self):
        return self._type == CDT.STRING

    @property
    def is_date(self):
        return self._type == CDT.DATE

    @property
    def is_time(self):
        return self._type == CDT.TIME

    @property
    def is_string_date(self):
        return self.is_string and self._name.lower().find('date') > -1

    @property
    def is_time_stamp(self):
        return self.is_numeric and (self._name.lower().find('_ts') > -1 or self._name.lower().find('timestamp') > -1)

    @property
    def description(self):
        return self._description

    def __get_description__(self):
        #  example:  Column('BigMove', Boolean(), default=False)
        if self._default == '':
            return "Column('{}', {}({}))".format(self._name, self._type, self._size)
        return "Column('{}', {}({}), default={})".format(self._name, self._type, self._size, self._default)


class MyView:
    def __init__(self):
        self._name = self.__get_name__()
        self._select_statement = text(self.__get_select_statement__())
        print('MyView._select_statement={}'.format(self._select_statement))

    def get_create_view_obj(self, meta_data: MetaData):
        view = Table(self._name, meta_data)
        create_view_obj = CreateView(view, self._select_statement, or_replace=False)
        print(str(create_view_obj.compile()).strip())
        return create_view_obj

    @staticmethod
    def __get_name__():
        return 'MyView'

    @staticmethod
    def __get_select_statement__():
        return "SELECT * FROM my_table"


class MyTable:
    def __init__(self):
        self._name = self._get_name_()
        self._view_name = self.__get_view_name__()
        self._columns = []
        self._add_columns_()
        self._column_dict = {column.name: column for column in self._columns}
        self._column_name_list = [columns.name for columns in self._columns]
        self._column_sort = self.__get_column_sort__()
        self._column_date = self.__get_column_date__()
        self._column_time_stamp = self.__get_column_time_stamp__()
        self._key_column_name_list = self.__get_key_column_name_list__()
        self._key_columns = [column for column in self._columns if column.name in self._key_column_name_list]
        self._description = self.__get_description__()
        self._query_select_all = self.query_select_all

    @property
    def name(self) -> str:
        return self._name

    @property
    def column_sort(self) -> str:
        return self._column_sort

    @property
    def column_date(self) -> str:
        return self._column_date

    @property
    def column_time_stamp(self) -> str:
        return self._column_time_stamp

    @property
    def column_name_list(self) -> list:
        return self._column_name_list

    @property
    def key_column_name_list(self) -> list:
        return self._key_column_name_list

    @property
    def description(self):
        return self._description

    @property
    def query_select_all(self):
        return 'SELECT * from {}'.format(self._name)

    @property
    def query_duplicate_id(self) -> str:
        columns = ', '.join(self._key_column_name_list)
        return "select {}, count(*) from {} group by {} having count(*) > 1;".format(columns, self._name, columns)

    @property
    def query_id_oid(self) -> str:
        columns = ', '.join(self._key_column_name_list)
        return "select {}, oid from {};".format(columns, self._name)

    def get_column(self, column_name: str):
        return self._column_dict.get(column_name, None)

    def get_query_select_by_data_dict(self, data_dict: dict, target_columns=None, sort_columns=None)  -> str:
        columns = '*' if target_columns is None else ','.join(target_columns)
        and_clause = self.__get_where_clause_for_data_dict__(data_dict)
        order_by_clause = '' if sort_columns is None else ' ORDER BY {}'.format(','.join(sort_columns))
        return "SELECT {} FROM {} where {}{}".format(columns, self._name, and_clause, order_by_clause)

    def get_query_select_for_unique_record_by_id(self, record_id: str) -> str:
        return "SELECT * FROM {} where ID='{}'".format(self._name, record_id)

    def get_query_select_for_unique_record_by_dict(self, data_dict: dict) -> str:
        and_clause = self.__get_key_where_clause_for_data_dict__(data_dict)
        return "SELECT {} FROM {} WHERE {}".format(DC.ROWID, self._name, and_clause)

    def get_update_set_clause_from_data_dict(self, data_dict: dict):
        set_clause_list = self.__get_clause_list_for_data_dict__(data_dict)
        return ', '.join(set_clause_list)

    def __get_column_sort__(self):
        return self._column_name_list[0]

    def __get_column_date__(self):
        for column in self._columns:
            if column.is_string_date:
                return column.name
        return ''

    def get_string_column_names(self) -> list:
        return self.__get_column_names_by_type__(CDT.STRING)

    def __get_column_names_by_type__(self, column_type: str):
        return [col.name for col in self._columns if col.type == column_type]

    def __get_column_time_stamp__(self):
        for column in self._columns:
            if column.is_time_stamp:
                return column.name
        return ''

    def __get_where_clause_for_data_dict__(self, data_dict: dict):
        and_clause_list = self.__get_clause_list_for_data_dict__(data_dict)
        return ' and '.join(and_clause_list)

    def __get_clause_list_for_data_dict__(self, data_dict: dict):
        clause_list = []
        for column_name in data_dict:
            if column_name in self._column_dict:
                value = data_dict[column_name]
                column = self._column_dict[column_name]
                if column.is_numeric:
                    clause_list.append("{}={}".format(column.name, value))
                elif value.find("'") < 0:
                    clause_list.append("{}='{}'".format(column.name, value))
        return clause_list

    def __get_key_where_clause_for_data_dict__(self, data_dict: dict):
        key_data_dict = {col: data_dict[col] for col in self._key_column_name_list}
        return self.__get_where_clause_for_data_dict__(key_data_dict)

    def __get_key_column_name_list__(self):
        return [DC.ID] if DC.ID in self._column_name_list else self._column_name_list

    def get_query_select_for_records(self, where_clause='') -> str:
        return "SELECT * FROM {}".format(self._name) + ('' if where_clause == '' else " WHERE {}".format(where_clause))

    def get_query_delete_by_id(self, id: str) -> str:
        return "DELETE FROM {} where ID='{}';".format(self._name, id)

    def get_query_delete_by_row_id(self, row_id: int) -> str:
        return 'DELETE FROM {} WHERE oid = {};'.format(self._name, row_id)

    def __get_column_name_list__(self) -> list:
        return [columns.name for columns in self._columns]

    def __get_description__(self, meta_data: str = 'metadata'):
        table_str = "Table('" + self._name + "', " + meta_data
        for columns in self._columns:
            table_str += ", " + columns.description
        table_str += ")"
        # print('MyTable.__get_description__: {}'.format(table_str))
        return table_str

    @staticmethod
    def _get_name_():
        return 'MyTable'

    def __get_view_name__(self):  # in most cases we don't have a separate view => we use the table
        return self._name

    def _add_columns_(self):
        pass


class BaseDatabase:
    database_activated = True

    def __init__(self):
        self.engine = self.__get_engine__()
        self.db_name = self.__get_db_name__()
        self.db_path = self.__get_db_path__()
        self.error_handler = ErrorHandler()
        self._file_log = FileLog()
        self._table_dict = self.__get_table_dict__()

    def get_table_by_name(self, table_name: str) -> MyTable:
        return self._table_dict.get(table_name, None)

    def get_number_of_records_for_table(self, table_name: str) -> int:
        query = "SELECT count(*) as Number from {}".format(table_name)
        df = self.select_data_by_query(query)
        return df.values[0, 0]

    def __get_engine__(self):
        db_path = self.__get_db_path__()
        return create_engine('sqlite:///' + db_path)

    def __get_db_name__(self):
        pass  # will be overwritten by sub classes

    def __get_db_path__(self) -> str:
        pass  # will be overwritten by sub classes

    def __get_table_dict__(self) -> dict:
        return {}

    def get_result_set_for_query(self, query: str):
        connection = self.engine.connect()
        results = connection.execute(query).fetchall()
        connection.close()
        return results

    def select_data_by_query(self, query: str, index_col='') -> pd.DataFrame:
        result_set = self.get_result_set_for_query(query)
        df = pd.DataFrame(result_set)
        if df.shape[0] > 0:
            df.columns = result_set[0].keys()
        if not df.empty and index_col != '':
            df.set_index(index_col, drop=False, inplace=True)
        return df

    def delete_records(self, query: str) -> int:
        if not self.database_activated:
            print('database_deactivated for delete_records')
            return 0
        connection = self.engine.connect()
        counter = -1
        loop_counter = 0
        while counter == -1:
            try:
                results = connection.execute(query)
                counter = results.rowcount
                self._file_log.log_message('Deleted {} records for query {}'.format(counter, query), 'Delete')
            except exc.OperationalError:
                sleep(1)
                loop_counter += 1
                if loop_counter == 3:
                    self._file_log.log_error()
                    counter = 0
            except:
                self._file_log.log_error()
            finally:
                connection.close()
                return counter

    def get_result_set_for_table(self, table: str):
        connection = self.engine.connect()
        stmt = "SELECT * from " + table
        results = connection.execute(stmt).fetchall()
        connection.close()
        return results

    def drop_database(self):
        self.engine = None
        os.remove(self.db_path)
        print('Database {} removed: {}'.format(self.db_name, self.db_path))

    def __create_table__(self, table_name: str):
        print('table_name={}'.format(table_name))
        metadata = MetaData()
        table = self.get_table_by_name(table_name)
        print('table.description={}'.format(table.description))
        exec(table.description)
        self.create_database_elements(metadata)
        table_obj = metadata.tables.get(table_name)
        print(repr(table_obj))

    def __create_view__(self, view_name: str):
        metadata = MetaData()
        view = self.__get_view_by_name__(view_name)
        create_view_obj = view.get_create_view_obj(metadata)
        self.engine.execute(create_view_obj)
        self.create_database_elements(metadata)
        view_obj = metadata.tables.get(view_name)
        print(repr(view_obj))

    def create_database_elements(self, metadata: MetaData):
        metadata.create_all(self.engine)

    def __insert_data_into_table__(self, table_name: str, insert_data_dic_list: list):
        if not self.database_activated:
            print('database_deactivated for {}'.format('__insert_data_into_table__'))
            return 0
        counter = len(insert_data_dic_list)
        if counter == 0:
            return 0
        connection = self.engine.connect()
        metadata = MetaData()
        table_object = Table(table_name, metadata, autoload=True, autoload_with=self.engine)
        stmt = insert(table_object)
        try:
            counter = self.__handle_connection_execution__(connection, stmt, insert_data_dic_list)
            if counter <= 0:
                self._file_log.log_waiting_db_transaction(table_name, insert_data_dic_list)
        finally:
            connection.close()
        if counter > 1:  # we don't want to have single entries in the log
            print('Loaded into {}: {} records.'.format(table_name, counter))
            self._file_log.log_message('Loaded into {}: {} records.'.format(table_name, counter), 'Insert')
        return counter

    def __handle_connection_execution__(self, connection, stmt, insert_data_dic_list):
        retrials_max = 3
        number = 1
        while number <= retrials_max:
            try:
                results = connection.execute(stmt, insert_data_dic_list)
                return results.rowcount
            except exc.OperationalError:
                if number == retrials_max:
                    runtime_info = '{} retried: {}'.format(stmt, number)
                    self._file_log.log_error(runtime_info)
                    return -1
                sleep(1)
            finally:
                number += 1
        return 0

    def update_table_column(self, table_name: str, column: str, value, where_clause: str):
        value = "'{}'".format(value) if type(value) is str else value
        stmt = "UPDATE {} SET {}={} WHERE {}".format(table_name, column, value, where_clause)
        return self.update_table_by_statement(table_name, stmt)

    def update_table_by_statement(self, table_name: str, stmt: str):
        if not self.database_activated:
            print('database_deactivated for {}'.format('update_table_by_statement'))
            return 0
        counter = 0
        connection = self.engine.connect()
        try:
            results = connection.execute(stmt)
            counter = results.rowcount
            self._file_log.log_message('Updated in {}: {} records.'.format(table_name, counter), 'Update')
        except exc.OperationalError:
            self._file_log.log_error()
            counter = -1
        finally:
            connection.close()
        return counter

    @staticmethod
    def __get_view_by_name__(view_name: str):
        pass

"""
Example for a derived class - connecting to a SQLite database

class SoccerDatabase(BaseDB):
    def __get_engine__(self):
       return create_engine('sqlite:///MySoccer.sqlite')
"""


class DatabaseDataFrame:
    def __init__(self, db: BaseDatabase, query: str = ''):
        self.db = db
        self.query = query
        self.query_active = self.__get_query__()
        self.result_set = self.db.get_result_set_for_query(self.query_active)
        self.df = pd.DataFrame(self.result_set)
        if self.df.shape[0] > 0:
            self.df.columns = self.result_set[0].keys()

    def __get_query__(self):
        return self.query  # will be overwritten by sub classes

    def get_column_value_for_id(self, id: int, column: str):
        pass  # will be overwritten by deferred classes

    def get_column_values_for_id_list(self, id_list, column: str):
        return_list = []
        for ids in id_list:
            return_list.append(self.get_column_value_for_id(ids, column))
        return return_list

    def get_column_value_for_key(self, key_column: str, key: int, value_column: str):
        df_subset = self.df[self.df[key_column] == key]
        return df_subset[value_column].values[0]

    def get_column_values_for_key_list(self, key_column: str, key_list, value_column: str):
        return_list = []
        for key in key_list:
            return_list.append(self.get_column_value_for_key(key_column, key, value_column))
        return return_list


"""
Example for a derived class - GameGroupTable for Soccer
class SoccerGroupDataFrame(DatabaseDataFrame):
    def __get_query__(self):
        return 'SELECT * FROM GameGroup'
"""