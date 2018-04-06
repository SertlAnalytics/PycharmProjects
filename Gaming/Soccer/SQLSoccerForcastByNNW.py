"""
Description: This module generates test data from any league for predictions with different machine learning
algorithms. We use neuron networks and linear and logistic regression.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import math
import matplotlib.pyplot as plt
import sertl_analytics.models.learning_machine as lm
import sertl_analytics.datafetcher.database_fetcher as dbf


class SoccerHelper:
    @staticmethod
    def map_goal_difference_to_points(goal_difference: int):
        if goal_difference > 10:
            return 1
        elif goal_difference < 10:
            return 2
        return 0

    @staticmethod
    def get_points_for_teams(goal_1: int, goal_2: int):
        if goal_1 > goal_2:
            return 3, 0
        if goal_1 < goal_2:
            return 0, 3
        return 1, 1


class SoccerDatabase(dbf.BaseDatabase):
    def __get_engine__(self):
        return create_engine('sqlite:///MySoccer.sqlite')

    def get_result_set_for_league(self, league_id: int):
        connection = self.engine.connect()
        stmt = SQLStatement.get_select_statement_for_league(league_id)
        results = connection.execute(stmt).fetchall()
        connection.close()
        return results


class SQLStatement:
    @staticmethod
    def get_select_statement_for_league(league_id: int):
        stmt = """
                SELECT League.LeagueId, League.LeagueName, GameGroup.GroupOrderId, GameGroup.GroupName
                , Match.MatchId, Match.MatchDateTime, Match.NumberOfViewers
                , Team.TeamId as HomeTeamId, Team2.TeamId as ForeignTeamId
                , Team.TeamName as HomeTeamName, Team2.TeamName as ForeignTeamName
                , Case When MatchResult.PointsTeam1 is NULL THEN 0 ELSE MatchResult.PointsTeam1 END as HomeTeamGoals
                , Case When MatchResult.PointsTeam2 is NULL THEN 0 ELSE MatchResult.PointsTeam2 END as ForeignTeamGoals
                , Case When MatchResult.PointsTeam1 is NULL OR MatchResult.PointsTeam1 is NULL Then 'Open' Else 'Played' END as Status
                FROM Match
                LEFT JOIN League on League.LeagueId = Match.LeagueId
                LEFT JOIN GameGroup ON GameGroup.GroupId = Match.GroupId
                LEFT JOIN MatchTeam ON Match.MatchId = MatchTeam.MatchId and MatchTeam.IsHomeTeam = 1
                LEFT JOIN MatchTeam as MatchTeam2 ON Match.MatchId = MatchTeam2.MatchId and MatchTeam2.IsHomeTeam = 0
                LEFT JOIN Team ON Team.TeamId = MatchTeam.TeamId
                LEFT JOIN Team as Team2 ON Team2.TeamId = MatchTeam2.TeamId
                LEFT JOIN MatchResult on MatchResult.MatchId = Match.MatchId and MatchResult.ResultTypeId = 2
                WHERE (League.LeagueId = """ + str(league_id) + """)
                /*AND Not(MatchResult.PointsTeam1 is NULL OR MatchResult.PointsTeam2 is NULL)*/
                Order by League.LeagueId, GameGroup.GroupOrderId, Match.MatchId
                """
        return stmt

    @staticmethod
    def get_select_statement_for_table(table: str):
        stmt = "SELECT * FROM " + str(table)
        return stmt


class GroupDataFrame(dbf.DatabaseDataFrame):
    def __get_query__(self):
        return "SELECT * FROM GameGroup"

    def get_column_value_for_id(self, id: int, column: str):
        df_subset = self.df[self.df["GroupOrderId"] == id]
        return df_subset[column].values[0]


class TeamDataFrame(dbf.DatabaseDataFrame):
    def __init__(self, db):
        dbf.DatabaseDataFrame.__init__(self, db)
        self.team_id_name_dic = {}
        self.__init_team_id_name_dic__()

    def __init_team_id_name_dic__(self):
        for ind, row in self.df.iterrows():
            self.team_id_name_dic[int(row['TeamId'])] = row['TeamName']

    def get_team_name_for_team_id(self, team_id: int):
        return self.team_id_name_dic[team_id]

    def __get_query__(self):
        return "SELECT * FROM Team"

    def get_column_value_for_id(self, id: int, column: str):
        df_subset = self.df[self.df["TeamId"] == id]
        return df_subset[column].values[0]


class LeagueMatchesDataFrame(dbf.DatabaseDataFrame):
    def __init__(self, db: dbf.BaseDatabase, query: str = '', league_id: int = 0):
        self.league_id = league_id
        dbf.DatabaseDataFrame.__init__(self, db)
        self.league_name = self.df.columns[1]
        self.add_calculated_columns()
        self.df_played = self.df[self.df['Status'] != 'Open']  # also the simulated matches are included
        self.team_list = np.sort(pd.unique(self.df["HomeTeamId"]))
        self.group_order_id_list = np.sort(pd.unique(self.df["GroupOrderId"]))
        self.group_order_id_list_played = np.sort(pd.unique(self.df_played["GroupOrderId"]))

    def __get_query__(self):
        return SQLStatement.get_select_statement_for_league(self.league_id)

    def simulate_match(self, match_id: int, status: str, prediction: int):
        if status != 'Open':
            return
        self.df.loc[self.df.MatchId == match_id, 'Status'] = 'Simulated'
        if prediction == 0:
            self.df.loc[self.df.MatchId == match_id, 'HomeTeamGoals'] = 1
            self.df.loc[self.df.MatchId == match_id, 'ForeignTeamGoals'] = 1
            self.df.loc[self.df.MatchId == match_id, 'GoalDifferenceHome'] = 10
            self.df.loc[self.df.MatchId == match_id, 'GoalDifferenceForeign'] = 10
            self.df.loc[self.df.MatchId == match_id, 'HomePoints'] = 1
            self.df.loc[self.df.MatchId == match_id, 'ForeignPoints'] = 1
        elif prediction == 1:
            self.df.loc[self.df.MatchId == match_id, 'HomeTeamGoals'] = 2
            self.df.loc[self.df.MatchId == match_id, 'ForeignTeamGoals'] = 1
            self.df.loc[self.df.MatchId == match_id, 'GoalDifferenceHome'] = 11
            self.df.loc[self.df.MatchId == match_id, 'GoalDifferenceForeign'] = 9
            self.df.loc[self.df.MatchId == match_id, 'HomePoints'] = 3
            self.df.loc[self.df.MatchId == match_id, 'ForeignPoints'] = 0
        else:
            self.df.loc[self.df.MatchId == match_id, 'HomeTeamGoals'] = 1
            self.df.loc[self.df.MatchId == match_id, 'ForeignTeamGoals'] = 2
            self.df.loc[self.df.MatchId == match_id, 'GoalDifferenceHome'] = 9
            self.df.loc[self.df.MatchId == match_id, 'GoalDifferenceForeign'] = 11
            self.df.loc[self.df.MatchId == match_id, 'HomePoints'] = 0
            self.df.loc[self.df.MatchId == match_id, 'ForeignPoints'] = 3

    def add_calculated_columns(self):
        self.df['GoalDifferenceHome'] = 10 + np.subtract(self.df['HomeTeamGoals'], self.df['ForeignTeamGoals'])
        self.df['GoalDifferenceForeign'] = 10 + np.subtract(self.df['ForeignTeamGoals'], self.df['HomeTeamGoals'])
        [self.df['HomePoints'], self.df['ForeignPoints']] = np.vectorize(SoccerHelper.get_points_for_teams)(self.df['HomeTeamGoals'], self.df['ForeignTeamGoals'])

    def get_data_frame_for_played_home_matches_for_team_until_group_order(self, team_id: int, group_order_id: int):
        return self.get_data_frame_for_played_matches_for_team_until_group_order(team_id, group_order_id, True)

    def get_data_frame_for_played_not_at_home_matches_for_team_until_group_order__(self, team_id: int, group_order_id: int):
        return self.get_data_frame_for_played_matches_for_team_until_group_order(team_id, group_order_id, False)

    def get_data_frame_for_played_matches_for_team_until_group_order(self, team_id: int, group_order_id: int, is_home: bool):
        if is_home:
            return self.df_played[np.logical_and(self.df_played['HomeTeamId'] == team_id,
                                                self.df_played['GroupOrderId'] <= group_order_id)]
        else:
            return self.df_played[np.logical_and(self.df_played['ForeignTeamId'] == team_id,
                                                       self.df_played['GroupOrderId'] <= group_order_id)]

    def get_home_team_statistic_data_until_group_order(self, team_id: int, group_order_id: int):
        return self.__get_team_statistic_data_until_group_order__(team_id, group_order_id, 'Home')

    def get_foreign_team_statistic_data_until_group_order(self, team_id: int, group_order_id: int):
        return self.__get_team_statistic_data_until_group_order__(team_id, group_order_id, 'Foreign')

    def get_team_statistic_data_until_group_id(self, team_id: int, group_order_id: int):
        return self.__get_team_statistic_data_until_group_order__(team_id, group_order_id, 'All')

    def __get_team_statistic_data_until_group_order__(self, team_id: int, group_order_id: int, identifier: str):
        df_home = self.get_data_frame_for_played_home_matches_for_team_until_group_order(team_id, group_order_id)
        df_not_at_home = self.get_data_frame_for_played_not_at_home_matches_for_team_until_group_order__(team_id, group_order_id)

        df_home_own_goals = df_home['HomeTeamGoals'].sum()
        df_home_own_points = df_home['HomePoints'].sum()
        df_home_foreign_goals = df_home['ForeignTeamGoals'].sum()
        df_home_foreign_points = df_home['ForeignPoints'].sum()

        df_not_at_home_own_goals = df_not_at_home['ForeignTeamGoals'].sum()
        df_not_at_home_own_points = df_not_at_home['ForeignPoints'].sum()
        df_not_at_home_foreign_goals = df_not_at_home['HomeTeamGoals'].sum()
        df_not_at_home_foreign_points = df_not_at_home['HomePoints'].sum()

        if identifier == 'Home':
            return [df_home_own_goals, df_home_foreign_goals,
                    df_home_own_points, df_home_foreign_points]
        elif identifier == 'Foreign':
            return [df_not_at_home_own_goals, df_not_at_home_foreign_goals,
                    df_not_at_home_own_points, df_not_at_home_foreign_points]
        else:
            return [df_home_own_goals + df_not_at_home_own_goals, df_home_foreign_goals + df_not_at_home_foreign_goals,
                    df_home_own_points + df_not_at_home_own_points, df_home_foreign_points + df_not_at_home_foreign_points]


class Match:
    def __init__(self, db_row: pd.DataFrame):
        self.df = db_row
        self.match_id = self.df['MatchId']
        self.match_date_time = self.df['MatchDateTime']
        self.league_id = self.df['LeagueId']
        self.league_name = self.df['LeagueName']
        self.group_order_id = self.df['GroupOrderId']
        self.group_name = self.df['GroupName']
        self.team_1_id = self.df['HomeTeamId']
        self.team_1_name = self.df['HomeTeamName']
        self.team_2_id = self.df['ForeignTeamId']
        self.team_2name = self.df['ForeignTeamName']
        self.team_1_goals = self.df['HomeTeamGoals']
        self.team_2_goals = self.df['ForeignTeamGoals']
        self.goal_difference_1 = self.df['GoalDifferenceHome']
        self.goal_difference_2 = self.df['GoalDifferenceForeign']
        self.team_1_points = self.df['HomePoints']
        self.team_2_points = self.df['ForeignPoints']
        self.status = self.df['Status']

    def is_open(self):
        if self.status == 'Open':
            return True
        return False


class TeamResult:
    def __init__(self, match: Match, is_team1_home: bool):
        self.match = match
        self.match_id = self.match.match_id
        self.group_order_id = self.match.group_order_id
        self.is_home_result = is_team1_home
        self.team_id = 0
        self.goals_own = 0
        self.goals_foreign = 0
        self.points_own = 0
        self.points_foreign = 0
        self.__init_team_result_parameter__()

    def __init_team_result_parameter__(self):
        if self.is_home_result:
            self.team_id = self.match.team_1_id
            self.goals_own = self.match.team_1_goals
            self.goals_foreign = self.match.team_2_goals
            self.points_own = self.match.team_1_points
            self.points_foreign = self.match.team_2_points
        else:
            self.team_id = self.match.team_2_id
            self.goals_own = self.match.team_2_goals
            self.goals_foreign = self.match.team_1_goals
            self.points_own = self.match.team_2_points
            self.points_foreign = self.match.team_1_points


class ContinuousLeague:
    def __init__(self, mdf:LeagueMatchesDataFrame):
        self.mdf = mdf
        self.team_list = self.mdf.team_list
        self.team_dic = {}
        self.group_order_list = self.mdf.group_order_id_list
        self.match_tableau = []
        self.match_dic = {}
        self.__init_tables__()

    def __init_tables__(self):
        self.match_tableau = [[None for k in range(0, self.group_order_list.size)] for m in range(self.team_list.size)]
        for ind, team_id in enumerate(self.team_list):
            self.team_dic[team_id] = ind
        for ind, row in self.mdf.df.iterrows():
            match = Match(row)
            self.match_dic[match.match_id] = match
            self.match_tableau[self.team_dic[match.team_1_id]][match.group_order_id-1] = match
            self.match_tableau[self.team_dic[match.team_2_id]][match.group_order_id-1] = match

    def get_training_data_for_match_id(self, match_id: int, levels_back: int):
        training_data = []
        home_data = []
        foreign_data = []
        match = self.match_dic[match_id]
        for level_back in range(levels_back, 0, -1):
            home_data = home_data + self.get_cummulated_data_for_team_for_earlier_match(match.team_1_id, match.group_order_id, level_back, True)
            foreign_data = foreign_data + self.get_cummulated_data_for_team_for_earlier_match(match.team_2_id, match.group_order_id, level_back, False)
        return home_data + foreign_data

    def get_cummulated_data_for_team_for_earlier_match(self, team_id:int, group_order_set_off:int, level_back: int, for_home:bool):
        points = 0
        own_goals = 0
        foreign_goals = 0
        counter_level = 0
        for group_order_ind in range(group_order_set_off - 1, -1, -1):
            match = self.match_tableau[self.team_dic[team_id]][group_order_ind]
            if for_home and team_id == match.team_1_id:
                counter_level += 1
                if counter_level > level_back:
                    points += match.team_1_points
                    own_goals += match.team_1_goals
                    foreign_goals += match.team_2_goals
            elif not for_home and team_id == match.team_2_id:
                counter_level += 1
                if counter_level > level_back:
                    points += match.team_2_points
                    own_goals += match.team_2_goals
                    foreign_goals += match.team_1_goals

        return [points] #  [points, own_goals, foreign_goals]


class LeagueTable:
    def __init__(self, mdf: LeagueMatchesDataFrame):
        self.mdf = mdf
        self.df = mdf.df
        self.db = self.mdf.db
        self.TABLE_COL_DIC = {"TeamId": 0, "Goal_Total": 1, "Foreign_Goal_Total": 2, "Goal_Total_Diff": 3, "Points": 4
            , "Goal_At_Home": 5, "Foreign_Goal_At_Home": 6, "Points_At_Home": 7
            , "Goal_Not_At_Home": 8, "Foreign_Goal_Not_At_Home": 9, "Points_Not_At_Home": 10}
        self.team_list = mdf.team_list
        self.group_order_id_list = mdf.group_order_id_list
        self.np_table = np.empty((self.team_list.size, len(self.TABLE_COL_DIC)))
        self.np_team_position = np.empty((self.team_list.size, self.group_order_id_list.size))
        self.__initialize_np_arrays__()
        self.calculate_np_team_position()

    def __initialize_np_arrays__(self):
        self.np_table = np.zeros((self.team_list.size, len(self.TABLE_COL_DIC)), dtype=np.int32)
        self.np_team_position = np.zeros((self.team_list.size, self.group_order_id_list.size), dtype=np.int32)

    def get_position_for_team_before_group_order_id(self, group_order_id: int, team_id: int):
        team_index, = np.where(self.team_list == team_id)
        if team_index.size == 0:  # not available in this year
            return self.team_list.size
        group_index, = np.where(self.group_order_id_list == group_order_id)
        if group_index > 0:
            group_index = group_index - 1  # we want to have the previous entry
        return self.np_team_position[team_index, group_index][0]

    def get_last_position_for_team(self, team_id: int):
        team_index, = np.where(self.team_list == team_id)
        if team_index.size == 0:  # not available in this year
            return self.team_list.size
        group_index = self.group_order_id_list.size - 1
        return self.np_team_position[team_index, group_index][0]

    def calculate_np_team_position(self):
        self.__initialize_np_arrays__()

        for team_index, team_id in enumerate(self.team_list):
            self.np_table[team_index, self.TABLE_COL_DIC["TeamId"]] = team_id

        for group_order_id_index, group_order_id in enumerate(self.group_order_id_list):
            df_sel_group = self.df[self.df["GroupOrderId"] == group_order_id]
            for team_id in self.team_list:
                df_sel_group_team = df_sel_group[np.logical_or(df_sel_group["HomeTeamId"] == team_id
                                                               , df_sel_group["ForeignTeamId"] == team_id)]
                for id, row in df_sel_group_team.iterrows():
                    if row["Status"] != 'Open':
                        self.add_to_np_table(row, team_id)

            for team_index, team_id in enumerate(self.team_list):
                self.np_table[team_index, self.TABLE_COL_DIC["Goal_Total_Diff"]] = \
                    self.np_table[team_index, self.TABLE_COL_DIC["Goal_Total"]] - self.np_table[
                    team_index, self.TABLE_COL_DIC["Foreign_Goal_Total"]]

            self.np_table = self.np_table[np.lexsort((self.np_table[:, 3], self.np_table[:, 4]))]
            self.np_table = self.np_table[::-1]  # reverse
            self.add_actual_positions(group_order_id_index)

    def add_actual_positions(self, group_order_id_index: int):
        np_table_sorted_team_col = self.np_table[:, 0]
        for index_team, team_id in enumerate(self.team_list):
            if team_id in np_table_sorted_team_col:
                position = self.get_team_index_in_sorted_np_table(team_id) + 1
            else:
                position = np_table_sorted_team_col.size
            self.np_team_position[index_team, group_order_id_index] = position

    def get_team_index_in_sorted_np_table(self, team_id):
        np_table_sorted_team_col = self.np_table[:, 0]
        return np.where(np_table_sorted_team_col == team_id)[0][0]

    def add_to_np_table(self, row, team_id):
        goals_team1 = row["HomePoints"]
        goals_team2 = row["ForeignPoints"]
        [points_team1, points_team2] = SoccerHelper.get_points_for_teams(goals_team1, goals_team2)
        team_index = self.get_team_index_in_sorted_np_table(team_id)
        if row["HomeTeamId"] == team_id:
            self.np_table[team_index, self.TABLE_COL_DIC["Goal_Total"]] += goals_team1
            self.np_table[team_index, self.TABLE_COL_DIC["Goal_At_Home"]] += goals_team1

            self.np_table[team_index, self.TABLE_COL_DIC["Points"]] += points_team1
            self.np_table[team_index, self.TABLE_COL_DIC["Points_At_Home"]] += points_team1

            self.np_table[team_index, self.TABLE_COL_DIC["Foreign_Goal_Total"]] += goals_team2
            self.np_table[team_index, self.TABLE_COL_DIC["Foreign_Goal_At_Home"]] += goals_team2
        if row["ForeignTeamId"] == team_id:
            self.np_table[team_index, self.TABLE_COL_DIC["Goal_Total"]] += goals_team2
            self.np_table[team_index, self.TABLE_COL_DIC["Goal_Not_At_Home"]] += goals_team2

            self.np_table[team_index, self.TABLE_COL_DIC["Points"]] += points_team2
            self.np_table[team_index, self.TABLE_COL_DIC["Points_Not_At_Home"]] += points_team2

            self.np_table[team_index, self.TABLE_COL_DIC["Foreign_Goal_Total"]] += goals_team1
            self.np_table[team_index, self.TABLE_COL_DIC["Foreign_Goal_Not_At_Home"]] += goals_team1

    def plot_team_position(self):
        print(self.group_order_id_list)
        team = TeamDataFrame(self.db)
        group = GroupDataFrame(self.db)
        group_name_list = group.get_column_values_for_id_list(self.group_order_id_list, 'GroupName')
        position_list = [k+1 for k in range(len(self.team_list))]
        for team_index, team_id in enumerate(self.team_list):
            team_name = team.get_column_value_for_id(team_id, 'TeamName')
            position_team = self.np_team_position[team_index]
            plt.plot(group_name_list, position_team, label=team_name)
            plt.title('Team positions for actual year')
            plt.xlabel('Spieltag')
            plt.ylabel('Position')
            plt.xticks(group_name_list, rotation=45)
            plt.yticks(position_list)
            plt.tight_layout()
        plt.legend()
        plt.show()

    def show_table(self):
        df_table = pd.DataFrame(self.np_table)
        df_table.columns = self.TABLE_COL_DIC
        df_teams = TeamDataFrame(self.db)
        team_names = df_teams.get_column_values_for_key_list('TeamId', df_table['TeamId'], 'TeamName')
        del df_table['TeamId']
        df_table.insert(0, column='Team', value=team_names)
        position_list = [k for k in range(1, self.team_list.size + 1)]
        df_table.insert(0, column='Pos', value=position_list)
        print(df_table)


class TrainingTestDataProvider:
    def __init__(self, df_matches: LeagueMatchesDataFrame):
        self.df_matches = df_matches
        self.continuous_league = ContinuousLeague(self.df_matches)
        self.team_list = self.df_matches.team_list
        self.group_order_id_list = self.df_matches.group_order_id_list
        self.training_set = []
        self.test_set = []
        self.test_match_data = []
        self.np_training_data = None
        self.np_training_data_target = None
        self.np_test_data = None
        self.np_test_data_target = None

    def calculate_training_set_for_next_group_order_id(self, group_order_id_next: int):
        self.training_set = []
        self.test_set = []

        for group_order_id in range(1, group_order_id_next + 1):
            match_list_for_group_order = self.get_match_list_for_group_order(group_order_id)
            for matches in match_list_for_group_order:
                [data, match_data] = self.get_prediction_data_row(matches, group_order_id)
                if group_order_id == group_order_id_next:
                    self.test_set.append(data)
                    self.test_match_data.append(match_data)
                else:
                    self.training_set.append(data)
        self.__calculate_training_test_sets_for_current_run__()

    def calculate_continuous_league_training_set_for_next_group_order_id(self, group_order_id_next: int):
        self.training_set = []
        self.test_set = []

        for group_order_id in range(1, group_order_id_next + 1):
            match_list_for_group_order = self.get_match_list_for_group_order(group_order_id)
            for matches in match_list_for_group_order:
                [data, match_data] = self.get_prediction_data_row_for_continuous_league(matches, group_order_id)
                if group_order_id == group_order_id_next:
                    self.test_set.append(data)
                    self.test_match_data.append(match_data)
                else:
                    self.training_set.append(data)
        self.__calculate_training_test_sets_for_current_run__()

    def get_enhanced_match_data_for_match_and_group_order(self, match: Match, group_order_id):
        match_id = match.match_id
        team_1 = match.team_1_id
        team_2 = match.team_2_id
        goal_difference = match.goal_difference_1
        match_status = match.status

        data_position_team_1 = self.df_matches.get_home_team_statistic_data_until_group_order(team_1,
                                                                                              group_order_id - 1)
        data_position_team_2 = self.df_matches.get_foreign_team_statistic_data_until_group_order(team_2,
                                                                                                 group_order_id - 1)

        return [match_id, group_order_id, match_status, team_1, team_2, goal_difference
            , data_position_team_1, data_position_team_2]

    def get_prediction_data_row_for_continuous_league(self, match: Match, group_order_id):
        match_data = self.get_enhanced_match_data_for_match_and_group_order(match, group_order_id)
        test_data = self.continuous_league.get_training_data_for_match_id(match.match_id, 6)
        test_data.append(SoccerHelper.map_goal_difference_to_points(match.goal_difference_1))
        return test_data, match_data

    def add_as_simulation(self, prediction):
        df = pd.DataFrame(self.test_match_data[-prediction.size:])  # get latest matches
        df.columns = ['Match', 'SpT', 'Status', 'T_1', 'T_2', 'G_Df', 'Team_1_G:G P:P', 'Team_2_G:G P:P']
        df.insert(6, column='Pred', value=prediction)
        for ind, rows in df.iterrows():
            self.df_matches.simulate_match(rows['Match'], rows['Status'], rows['Pred'])

    def __calculate_training_test_sets_for_current_run__(self):
        np_training_set = np.array(self.training_set)
        np_test_set = np.array(self.test_set)

        self.np_training_data = np_training_set[:, :-1]

        self.np_training_data_target = np_training_set[:, -1]
        self.np_training_data_target = self.np_training_data_target.reshape((self.np_training_data_target.size, 1))
        self.np_test_data = np_test_set[:, :-1]

        # print('np_test_data = {}'.format(np_test_data))
        self.np_test_data_target = np_test_set[:, -1]
        self.np_test_data_target = self.np_test_data_target.reshape((self.np_test_data_target.size, 1))

    def get_prediction_data_row(self, match: Match, group_order_id):
        team_1 = match.team_1_id
        team_2 = match.team_2_id

        match_data = self.get_enhanced_match_data_for_match_and_group_order(match, group_order_id)

        data_team_1 = self.get_result_list_for_team_until_group_order(team_1, group_order_id, True)
        data_team_2 = self.get_result_list_for_team_until_group_order(team_2, group_order_id, False)

        match_data_home_team = self.get_position_result_list_for_team_until_group_order(team_1, group_order_id, True)
        match_data_foreign_team = self.get_position_result_list_for_team_until_group_order(team_2, group_order_id, False)

        data_home_team = self.get_list_with_team_position(team_1)
        data_foreign_team = self.get_list_with_team_position(team_2)
        test_data = data_team_1 + data_team_2 + match_data_home_team + match_data_foreign_team + \
                    data_home_team + data_foreign_team

        test_data.append( SoccerHelper.map_goal_difference_to_points(match.goal_difference_1))
        return test_data, match_data

    def get_result_list_for_team_until_group_order(self, team_id: int, group_order_id: int, is_home: bool):
        return_list = [0 for k in range(self.team_list.size)]
        df_sel = self.df_matches.get_data_frame_for_played_matches_for_team_until_group_order(team_id, group_order_id, is_home)
        index = 0
        for order_id in range(1, group_order_id + 1):
            df_sel_order = df_sel[df_sel["GroupOrderId"] == order_id]
            for id, row in df_sel_order.iterrows():
                return_list[index] = row['GoalDifferenceHome'] if is_home else row['GoalDifferenceForeign']
                index = index + 1
        return return_list

    def get_match_list_for_group_order(self, group_order_id: int):
        match_list = []
        df_sel = self.df_matches.df[self.df_matches.df["GroupOrderId"] == group_order_id]
        for id, row in df_sel.iterrows():
            match_list.append(Match(row))
        return match_list

    def get_list_with_team_position(self, team_id_input: int):
        return_list = [0 for k in range(self.team_list.size)]
        ind, = np.where(self.team_list == team_id_input)
        return_list[ind[0]] = 1
        return return_list

    def get_position_result_list_for_team_until_group_order(self, team_id: int, group_order_id: int, is_home: bool):
        return_list = [0 for k in range(self.team_list.size)]
        df_sel = self.df_matches.get_data_frame_for_played_matches_for_team_until_group_order(team_id, group_order_id,
                                                                                              is_home)
        index = 0
        for team_ind, team_id in enumerate(self.team_list):
            if is_home:
                df_sel_team = df_sel[df_sel["ForeignTeamId"] == team_id]
            else:
                df_sel_team = df_sel[df_sel["HomeTeamId"] == team_id]

            for id, row in df_sel_team.iterrows():
                return_list[team_ind] = row['GoalDifferenceHome'] if is_home else row['GoalDifferenceForeign']
                index = index + 1
        return return_list


class SoccerGamePrediction:
    def __init__(self, league_id: int):
        self.league_id = league_id
        self.df_matches = LeagueMatchesDataFrame(SoccerDatabase(), '', self.league_id)
        self.db = self.df_matches.db
        self.training_test_provider = TrainingTestDataProvider(self.df_matches)
        self.algorithm_list = []
        self.algorithm_list_for_printing = []
        self.hidden_layer_list = []
        self.model_loop_list = []
        self.np_prediction_dir = {}
        self.column_prediction = ''
        self.statistics = []
        self.range_from = 0
        self.range_to = 0
        self.with_simulation = False

    def run_algorithm(self, algorithm_list, range_from: int, range_to: int = 0, with_simulation: bool = False):
        self.with_simulation = with_simulation
        self.algorithm_list = list(algorithm_list)
        self.hidden_layer_list = []
        self.model_loop_list = []
        self.__init_hidden_layer_list__()
        self.__init_model_loop_list__()
        self.algorithm_list_for_printing = list(algorithm_list)

        if lm.ModelType.SEQUENTIAL_CLASSIFICATION in self.algorithm_list_for_printing:
            self.algorithm_list_for_printing.append(lm.ModelType.SEQUENTIAL_CLASSIFICATION + '_pct')
        self.np_prediction_dir = {}
        self.statistics = []
        self.range_from = range_from
        self.range_to = (range_from + 1) if range_to < range_from else range_to + 1
        for group_order in range(self.range_from, self.range_to):
            self.run_prediction_for_group_order(group_order)

    def __init_model_loop_list__(self):
        for algorithm in self.algorithm_list:
            if algorithm == lm.ModelType.SEQUENTIAL_CLASSIFICATION or algorithm == lm.ModelType.SEQUENTIAL_REGRESSION:
                for hidden_layers in self.hidden_layer_list:
                    self.model_loop_list.append([algorithm, hidden_layers])
            else:
                self.model_loop_list.append([algorithm, None])

    def __init_hidden_layer_list__(self):
        base_list = [10, 100, 1000, 10000]
        # self.hidden_layer_list.append([10,10])
        # self.hidden_layer_list.append([100, 10])
        # self.hidden_layer_list.append([10, 100])
        #
        # self.hidden_layer_list.append([100, 100])
        # self.hidden_layer_list.append([100, 1000])
        # self.hidden_layer_list.append([1000, 100])
        #
        # self.hidden_layer_list.append([10, 1000])
        # self.hidden_layer_list.append([1000, 10])
        #
        # self.hidden_layer_list.append([100, 10000])
        # self.hidden_layer_list.append([10000, 100])
        #
        # self.hidden_layer_list.append([100, 1000, 10000])
        # self.hidden_layer_list.append([10000, 1000, 100])

        # self.hidden_layer_list.append([10, 10, 10, 10, 10])
        # self.hidden_layer_list.append([100, 100, 100, 100, 100])
        # self.hidden_layer_list.append([1000, 1000, 1000, 1000, 1000])


        self.hidden_layer_list.append([1000, 1000, 1000, 1000])

        # self.hidden_layer_list.append([10, 10, 10, 10, 10])
        # self.hidden_layer_list.append([10, 10, 10, 10, 10, 10])
        # self.hidden_layer_list.append([10, 10, 10, 10, 10, 10, 10])
        # self.hidden_layer_list.append([10, 10, 10, 10, 10, 10, 10, 10])
        # self.hidden_layer_list.append([10, 10, 10, 10, 10, 10, 10, 10, 10])

    def run_prediction_for_group_order(self, group_order: int):
        self.training_test_provider.calculate_training_set_for_next_group_order_id(group_order)
        # self.training_test_provider.calculate_continuous_league_training_set_for_next_group_order_id(group_order)
        np_training_data = self.training_test_provider.np_training_data
        np_training_data_target = self.training_test_provider.np_training_data_target
        # print(self.training_test_provider.team_list)
        np_test_data = self.training_test_provider.np_test_data
        # print(self.training_test_provider.test_match_data)
        # print(pd.DataFrame(np_training_data))
        print(pd.DataFrame(np_test_data))
        # print(self.training_test_provider.test_match_data)
        np_test_data_target = self.training_test_provider.np_test_data_target
        # [np_training_data, np_training_data_target, np_test_data, np_test_data_target] = td.TestDataGenerator.get_test_data_for_summation()
        for models in self.model_loop_list:
            algorithm = models[0]
            hidden_layers = models[1]
            if hidden_layers == None:
                key = algorithm
            else:
                key = algorithm + '_' + str(hidden_layers)

            if not key in self.np_prediction_dir:
                self.np_prediction_dir[key] = None

            accuracy, prediction = self.get_prediction_accuracy_by_algorithm(algorithm, hidden_layers,
                                                                             np_test_data, np_test_data_target,
                                                                             np_training_data, np_training_data_target)

            self.append_to_np_prediction(key, prediction)
            if self.with_simulation:
                self.training_test_provider.add_as_simulation(prediction)
            # print('algorithm={}, k={}, accuracy={}'.format(algorithm, group_order_id, accuracy))
            self.statistics.append([key, group_order, accuracy])

    def get_prediction_accuracy_by_algorithm(self, algorithm, hidden_layers, np_test_data,
                                             np_test_data_target, np_training_data, np_training_data_target):
        if algorithm == lm.ModelType.SEQUENTIAL_REGRESSION:
            lm_regression = lm.LmSequentialRegression(hidden_layers)
            prediction = lm_regression.get_regression_prediction(np_training_data, np_training_data_target,
                                                                 np_test_data)
            lm_regression.compare_prediction_with_results(np_test_data_target)
            accuracy = lm_regression.accuracy
        if algorithm == lm.ModelType.SEQUENTIAL_CLASSIFICATION:
            lm_classification = lm.LmSequentialClassification(hidden_layers)
            prediction = lm_classification.get_regression_prediction(np_training_data, np_training_data_target,
                                                                     np_test_data)
            lm_classification.compare_prediction_with_results(np_test_data_target)
            accuracy = lm_classification.accuracy
            # self.append_to_np_prediction(algorithm + '_pct', lm_classification.prediction_pct)
        if algorithm == lm.ModelType.LINEAR_REGRESSION:
            lm_linear_regression = lm.LmLinearRegression()
            prediction = lm_linear_regression.get_regression_prediction(np_training_data, np_training_data_target,
                                                                        np_test_data)
            lm_linear_regression.compare_prediction_with_results(np_test_data_target)
            accuracy = lm_linear_regression.accuracy
        if algorithm == lm.ModelType.LINEAR_CLASSIFICATION:
            lm_logistic_regression = lm.LmLogisticRegression()
            prediction = lm_logistic_regression.get_regression_prediction(np_training_data, np_training_data_target,
                                                                          np_test_data)
            lm_logistic_regression.compare_prediction_with_results(np_test_data_target)
            accuracy = lm_logistic_regression.accuracy
        return accuracy, prediction

    def append_to_np_prediction(self, algorithm: str, prediction):
        if self.np_prediction_dir[algorithm] is None:
            self.np_prediction_dir[algorithm] = prediction
        else:
            self.np_prediction_dir[algorithm] = np.append(self.np_prediction_dir[algorithm], prediction, axis=0)

    def show_statistics(self):
        df = pd.DataFrame(self.statistics)
        df.columns = ['Algorithm', 'Spieltag', 'Accuracy']
        print(df)

        for key in self.np_prediction_dir:
            df_sub = df[df['Algorithm'] == key]
            x = df_sub['Spieltag']
            y = df_sub['Accuracy']
            plt.plot(x, y, label=key, marker='x')
            plt.plot()

        plt.xticks(df_sub['Spieltag'])
        plt.legend(loc='upper left')
        plt.show()

    def print_overview(self):
        df = pd.DataFrame(self.training_test_provider.test_match_data)
        columns = ['Match', 'SpT', 'Status', 'T_1', 'T_2', 'G_Df', 'Team_1_G:G P:P', 'Team_2_G:G P:P']
        df.columns = columns
        self.add_team_details_to_data_frame(df)
        column = columns.index('G_Df') - 2
        counter = 0
        for key in self.np_prediction_dir:
            counter = counter + 1
            column = column + 2
            self.column_prediction = 'P_' + str(counter)
            np_prediction = self.np_prediction_dir[key]
            df.insert(column + 1, column=self.column_prediction, value=np_prediction)
            df.insert(column + 2, column='OK_' + str(counter), value=df.apply(self.calculate_result, axis=1))
        print(df)

    def calculate_result(self, row):
        if row['G_Df'] == 10 and row[self.column_prediction] != 0:
            return False
        elif row['G_Df'] < 10 and row[self.column_prediction] != 2:
            return False
        elif row['G_Df'] > 10 and row[self.column_prediction] != 1:
            return False
        else:
            return True

    def add_team_details_to_data_frame(self, df: pd.DataFrame):
        team = TeamDataFrame(self.db)
        for team_id in team.team_id_name_dic:
            df.loc[df.T_1 == team_id, 'T_1'] = team.team_id_name_dic[team_id]
            df.loc[df.T_2 == team_id, 'T_2'] = team.team_id_name_dic[team_id]


# algorithms = [lm.ModelType.SEQUENTIAL_REGRESSION, lm.ModelType.SEQUENTIAL_CLASSIFICATION,
#               lm.ModelType.LINEAR_CLASSIFICATION, lm.ModelType.LINEAR_REGRESSION]
#
# # 3005|1. Fußball-Bundesliga 2016/2017 - 4153|1. Fußball-Bundesliga 2017/2018, 4156|3. Fußball-Bundesliga 2017/2018

game_prediction = SoccerGamePrediction(4153)
game_prediction.run_algorithm([lm.ModelType.LINEAR_CLASSIFICATION], 29, 29, False)
game_prediction.print_overview()
game_prediction.show_statistics()

# df_matches = LeagueMatchesDataFrame(SoccerDatabase(), '', 4153)
# continuous_league = ContinuousLeague(df_matches)
# # print(continuous_league.match_tableau)
# ret = continuous_league.get_training_data_for_match_id(45653, 2)
# print(ret)




















