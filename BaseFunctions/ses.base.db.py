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
        return self.get_result_set_for_statement(SQLStatement.get_select_statement_for_table(table))


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
        self.result_set = db.get_result_set_for_statement(select_statement)
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


class MatchDataFrame(DatabaseDataFrame):
    def __init__(self, db: BaseDatabase, select_statement: str):
        DatabaseDataFrame.__init__(self, db, select_statement)
        self.team_list = np.sort(pd.unique(self.df["HomeTeamId"]))
        self.group_order_id_list = np.sort(pd.unique(self.df["GroupOrderId"]))
        self.group_order_id_list_played = self.__get_played_played_group_order_id__()
        self.match_table = []

    def __get_played_played_group_order_id__(self):
        return_list = []
        for group_order_id in self.group_order_id_list:
            df_sel = self.df[self.df["GroupOrderId"] == group_order_id]
            counter = 0
            for id, row in df_sel.iterrows():
                if math.isnan(row["PointsTeam1"]) or math.isnan(row["PointsTeam2"]):
                    counter += 1
                    if counter > 2:  # eventually there are some outstanding games - skip them in this check
                        return return_list
            return_list.append(group_order_id)
        return return_list

    def get_team_list(self):
        return self.team_list

    def get_group_order_id_list(self):
        return self.group_order_id_list

    def calculate_match_table(self):  # 2 dim array for all matches with lists
        default_list = [0, 0, 0, 0, 0, 0]  # (GoalHome, GoalForeign, 10 + GH - GF, PointsHome, PointsForeign, GroupOrderId)
        self.match_table = [[default_list for t1 in self.team_list] for t2 in self.team_list]

        for index_1, team_id_1 in enumerate(self.team_list):
            for index_2, team_id_2 in enumerate(self.team_list):
                df_sel = self.df[np.logical_and(self.df["HomeTeamId"] == team_id_1, self.df["ForeignTeamId"] == team_id_2)]
                for id, row in df_sel.iterrows():
                    value_list = [0, 0, 0, 0, 0, row["GroupOrderId"]]
                    if not math.isnan(row["PointsTeam1"]) and not math.isnan(row["PointsTeam2"]):
                        value_list[0] = row["PointsTeam1"]
                        value_list[1] = row["PointsTeam2"]
                        [value_list[2], value_list[3]] = SoccerHelper.get_points_for_teams(value_list[0], value_list[1])
                        value_list[4] = 10 + value_list[0] - value_list[1]
                    self.match_table[index_1][index_2] = value_list


