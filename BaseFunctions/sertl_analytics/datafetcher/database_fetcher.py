"""
Description: This module is the main module for database connections.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""

import pandas as pd
from sqlalchemy import create_engine


class BaseDatabase:
    def __init__(self):
        self.engine = self.__get_engine__()

    def __get_engine__(self):
        pass  # will be overwritten by sub classes

    def get_result_set_for_query(self, query: str):
        connection = self.engine.connect()
        results = connection.execute(query).fetchall()
        connection.close()
        return results

    def get_result_set_for_table(self, table: str):
        connection = self.engine.connect()
        stmt = "SELECT * from " + table
        results = connection.execute(stmt).fetchall()
        connection.close()
        return results


"""
Example for a derived class - connecting to a SQLite database

class SoccerDatabase(BaseDB):
    def __set_engine__(self):
       self.engine = create_engine('sqlite:///MySoccer.sqlite')
"""


class DatabaseDataFrame:
    def __init__(self, db: BaseDatabase, query: str = ''):
        self.db = db
        self.query = query
        self.query_active = self.__get_query__()
        self.result_set = self.db.get_result_set_for_query(self.query_active)
        self.df = pd.DataFrame(self.result_set)
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