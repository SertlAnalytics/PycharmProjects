"""
Description: This module is the base module for database connections.
Usage: Please create your derived class for your specific purposes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-16
"""
from sqlalchemy import create_engine
import pandas as pd


class BaseDatabase:
    def __init__(self):
        self.engine = None
        self.__set_engine__()

    def __set_engine__(self):
        self.engine = create_engine('sqlite:///MySoccer.sqlite')

    def get_result_set_for_statement(self, statement: str):
        connection = self.engine.connect()
        results = connection.execute(statement).fetchall()
        connection.close()
        return results

    def get_result_set_for_table(self, table: str):
        return self.get_result_set_for_statement("SELECT * from " + table)


"""
Example for a derived class - connecting to a SQLite database

class SoccerDatabase(BaseDB):
    def __set_engine__(self):
       self.engine = create_engine('sqlite:///MySoccer.sqlite')
"""


class DatabaseDataFrame:
    def __init__(self, db: BaseDatabase, select_statement: str):
        self.db = db
        self.select_statement = select_statement
        self.result_set = None
        self.df = None
        self.df.columns = None
        self.actual_key_column = ''
        self.__init_parameters__()

    def __init_parameters__(self):
        self.result_set = self.db.get_result_set_for_statement(self.select_statement)
        self.df = pd.DataFrame(self.result_set)
        self.df.columns = self.result_set[0].keys()

    def get_column_value_for_key(self, key_column: str, key: int, value_column: str):
        if self.actual_key_column != key_column:
            self.actual_key_column = key_column
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
    def __init__(self):
        self.db = SoccerDatabase()
        self.select_statement = "Select * from GameGroup"
        self.__init_parameters__()
"""