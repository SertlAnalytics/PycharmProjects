"""
Description: This module is the main module for database connections.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""

import pandas as pd
from sqlalchemy import MetaData, Table, insert, exc
import os
from sertl_analytics.myexceptions import ErrorHandler


class CDT:  # Column Data Types
    STRING = 'String'
    INTEGER = 'Integer'
    FLOAT = 'Float'
    DATE = 'Date'
    TIME = 'Time'
    BOOLEAN = 'Boolean'


class MyTable:
    def __init__(self):
        self._name = self._get_name_()
        self._columns = []
        self._add_columns_()
        self._column_name_list = self.__get_column_name_list__()
        self._description = self.__get_description__()
        self._query_select_all = self.query_select_all

    @property
    def name(self) -> str:
        return self._name

    @property
    def column_name_list(self) -> list:
        return self._column_name_list

    @property
    def description(self):
        return self._description

    @property
    def query_select_all(self):
        return 'SELECT * from {}'.format(self._name)

    @property
    def query_duplicate_id(self) -> str:
        return "select id, count(*) from {} group by id having count(*) > 1;".format(self._name)

    @property
    def query_id_oid(self) -> str:
        return "select id, oid from {};".format(self._name)

    def get_query_for_unique_record_by_id(self, record_id: str) -> str:
        return "SELECT * FROM {} where ID='{}'".format(self._name, record_id)

    def get_query_for_records(self, where_clause='') -> str:
        return "SELECT * FROM {}".format(self._name) + ('' if where_clause == '' else " WHERE {}".format(where_clause))

    def get_query_for_delete_by_id(self, id: str) -> str:
        return "DELETE FROM {} where ID='{}'".format(self._name, id)

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

    def _add_columns_(self):
        pass


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
    def description(self):
        return self._description

    def __get_description__(self):
        #  example:  Column('BigMove', Boolean(), default=False)
        if self._default == '':
            return "Column('{}', {}({}))".format(self._name, self._type, self._size)
        return "Column('{}', {}({}), default={})".format(self._name, self._type, self._size, self._default)


class BaseDatabase:
    def __init__(self):
        self.engine = self.__get_engine__()
        self.db_name = self.__get_db_name__()
        self.db_path = self.__get_db_path__()
        self.error_handler = ErrorHandler()

    def __get_engine__(self):
        pass  # will be overwritten by sub classes

    def __get_db_name__(self):
        pass  # will be overwritten by sub classes

    def __get_db_path__(self):
        pass  # will be overwritten by sub classes

    def get_result_set_for_query(self, query: str):
        connection = self.engine.connect()
        results = connection.execute(query).fetchall()
        connection.close()
        return results

    def delete_records(self, query: str):
        connection = self.engine.connect()
        results = connection.execute(query)
        connection.close()
        print('Deleted {} records for query {}'.format(results.rowcount, query))

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

    def create_database_elements(self, metadata: MetaData):
        metadata.create_all(self.engine)

    def __insert_data_into_table__(self, table_name: str, insert_data_dic_list: list):
        return_value = True
        if len(insert_data_dic_list) == 0:
            return True
        connection = self.engine.connect()
        metadata = MetaData()
        table_object = Table(table_name, metadata, autoload=True, autoload_with=self.engine)
        stmt = insert(table_object)
        try:
            results = connection.execute(stmt, insert_data_dic_list)
            print('Loaded into {}: {} records.'.format(table_name, results.rowcount))
        except exc.OperationalError:
            print('Problem with inserting...')
            return_value = False
        finally:
            connection.close()
        return return_value

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