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


class LeagueTable:
    def __init__(self, mdf: LeagueMatchesDataFrame):
        self.mdf = mdf
        self.df = mdf.df
        self.TABLE_COL_DIC = {"TeamId": 0, "Goal_Total": 1, "Foreign_Goal_Total": 2, "Goal_Total_Diff": 3, "Points": 4
            , "Goal_At_Home": 5, "Foreign_Goal_At_Home": 6, "Points_At_Home": 7
            , "Goal_Not_At_Home": 8, "Foreign_Goal_Not_At_Home": 9, "Points_Not_At_Home": 10}
        self.team_list = mdf.team_list
        # print('team_list={}'.format(self.team_list))
        self.group_order_id_list = mdf.group_order_id_list
        self.np_table = np.empty((self.team_list.size, len(self.TABLE_COL_DIC)))
        self.np_team_position = np.empty((self.team_list.size, self.group_order_id_list.size))
        self.__initialize_np_arrays__()

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
                    if not math.isnan(row["PointsTeam1"]) and not math.isnan(row["PointsTeam2"]):
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
        goals_team1 = row["PointsTeam1"]
        goals_team2 = row["PointsTeam2"]
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
        team = TeamDataFrame()
        group = GroupDataFrame()
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


class GamePredictor:
    def __init__(self, league_id: int):
        self.db = SoccerDatabase()
        self.league_id = league_id
        self.df_match = LeagueMatchesDataFrame(self.db, '', self.league_id)
        self.team_list = self.df_match.team_list
        self.group_order_id_list = self.df_match.group_order_id_list
        self.training_set = []
        self.test_set = []
        self.test_match_data = []

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

    def get_prediction_data_row(self, match: Match, group_order_id):
        match_id = match.match_id
        team_1 = match.team_1_id
        team_2 = match.team_2_id
        goal_difference = match.goal_difference_1

        data_position_team_1 = self.df_match.get_home_team_statistic_data_until_group_order(team_1, group_order_id - 1)
        data_position_team_2 = self.df_match.get_foreign_team_statistic_data_until_group_order(team_2, group_order_id - 1)

        match_data = [match_id, group_order_id, team_1, team_2, goal_difference, data_position_team_1, data_position_team_2]

        data_team_1 = self.get_result_list_for_team_until_group_order(team_1, group_order_id, True)
        data_team_2 = self.get_result_list_for_team_until_group_order(team_2, group_order_id, False)

        data_home_team = self.get_list_with_team_position(team_1)
        data_foreign_team = self.get_list_with_team_position(team_2)
        test_data = data_team_1 + data_team_2 + data_home_team + data_foreign_team

        test_data.append( SoccerHelper.map_goal_difference_to_points(goal_difference))
        return test_data, match_data

    def get_result_list_for_team_until_group_order(self, team_id: int, group_order_id: int, is_home: bool):
        return_list = [0 for k in range(self.team_list.size)]
        df_sel = self.df_match.get_data_frame_for_played_matches_for_team_until_group_order(team_id, group_order_id, is_home)
        index = 0
        for order_id in range(1, group_order_id + 1):
            df_sel_order = df_sel[df_sel["GroupOrderId"] == order_id]
            for id, row in df_sel_order.iterrows():
                return_list[index] = row['GoalDifferenceHome'] if is_home else row['GoalDifferenceForeign']
                index = index + 1
        return return_list

    def get_match_list_for_group_order(self, group_order_id: int):
        match_list = []
        df_sel = self.df_match.df[self.df_match.df["GroupOrderId"] == group_order_id]
        for id, row in df_sel.iterrows():
            match_list.append(Match(row))
        return match_list

    def get_list_with_team_position(self, team_id_input: int):
        return_list = [0 for k in range(self.team_list.size)]
        ind, = np.where(self.team_list == team_id_input)
        return_list[ind[0]] = 1
        return return_list


class GamePrediction:
    def __init__(self, league_id: int):
        self.league_id = league_id
        self.game_predictor = GamePredictor(self.league_id)
        self.algorithm_list = []
        self.statistics = []
        self.range_from = 0
        self.range_to = 0

    def run_algorithm(self, algorithm_list, range_from: int, range_to: int = 0):
        self.algorithm_list = algorithm_list
        self.statistics = []
        self.np_prediction = None
        self.range_from = range_from
        self.range_to = (range_from + 1) if range_to < range_from else range_to + 1
        for k in range(self.range_from, self.range_to):
            self.game_predictor.calculate_training_set_for_next_group_order_id(k)

            np_training_set = np.array(self.game_predictor.training_set)
            np_test_set = np.array(self.game_predictor.test_set)

            np_training_data = np_training_set[:, :-1]

            np_training_data_target = np_training_set[:, -1]
            np_training_data_target = np_training_data_target.reshape((np_training_data_target.size, 1))
            np_test_data = np_test_set[:, :-1]

            # print('np_test_data = {}'.format(np_test_data))
            np_test_data_target = np_test_set[:, -1]
            np_test_data_target = np_test_data_target.reshape((np_test_data_target.size, 1))

            # [np_training_data, np_training_data_target, np_test_data, np_test_data_target] = td.TestDataGenerator.get_test_data_for_summation()

            for algorithm in algorithm_list:
                accuracy = 0

                hidden_layers = [100, 100, 100, 100, 100, 100]

                if algorithm == lm.ModelType.SEQUENTIAL_REGRESSION:
                    lm_regression = lm.LmSequentialRegression(hidden_layers)
                    lm_regression.get_regression_prediction(np_training_data, np_training_data_target, np_test_data)
                    self.append_to_np_prediction(lm_regression.prediction)
                    lm_regression.compare_prediction_with_results(np_test_data_target)
                    accuracy = lm_regression.accuracy

                if algorithm == lm.ModelType.SEQUENTIAL_CLASSIFICATION:
                    lm_classification = lm.LmSequentialClassification(hidden_layers)
                    lm_classification.get_regression_prediction(np_training_data, np_training_data_target, np_test_data)
                    self.append_to_np_prediction(lm_classification.prediction)
                    lm_classification.compare_prediction_with_results(np_test_data_target)
                    accuracy = lm_classification.accuracy

                if algorithm == lm.ModelType.LINEAR_REGRESSION:
                    lm_linear_regression = lm.LmLinearRegression()
                    lm_linear_regression.get_regression_prediction(np_training_data, np_training_data_target, np_test_data)
                    self.append_to_np_prediction(lm_linear_regression.prediction)
                    lm_linear_regression.compare_prediction_with_results(np_test_data_target)
                    accuracy = lm_linear_regression.accuracy

                if algorithm == lm.ModelType.LINEAR_CLASSIFICATION:
                    lm_logistic_regression = lm.LmLogisticRegression()
                    lm_logistic_regression.get_regression_prediction(np_training_data, np_training_data_target, np_test_data)
                    self.append_to_np_prediction(lm_logistic_regression.prediction)
                    lm_logistic_regression.compare_prediction_with_results(np_test_data_target)
                    accuracy = lm_logistic_regression.accuracy

                self.statistics.append([algorithm, k, accuracy])

    def append_to_np_prediction(self, prediction):
        if self.np_prediction is None:
            self.np_prediction = prediction
        else:
            self.np_prediction = np.append(self.np_prediction, prediction, axis=0)

    def show_statistics(self):
        df = pd.DataFrame(self.statistics)
        df.columns = ['Algorithm', 'Spieltag', 'Accuracy']

        for algorithm in self.algorithm_list:
            df_sub = df[df['Algorithm'] == algorithm]
            x = df_sub['Spieltag']
            y = df_sub['Accuracy']
            plt.plot(x, y, label=algorithm, marker='x')
            plt.plot()

        plt.legend(loc='upper left')
        plt.show()

    def print_overview(self):
        df = pd.DataFrame(self.game_predictor.test_match_data)
        df.columns = ['Match', 'SpT', 'T_1', 'T_2', 'G_Df', 'Team_1_G:G P:P', 'Team_2_G:G P:P']
        df.insert(5, column='Pred', value=self.np_prediction)
        self.add_team_details_to_data_frame(df)
        df.insert(6, column='OK', value=df.apply(self.calculate_result, axis=1))
        print(df)

    def calculate_result(self, row):
        if row['G_Df'] == 10 and row['Pred'] != 0:
            return False
        elif row['G_Df'] < 10 and row['Pred'] != 2:
            return False
        elif row['G_Df'] > 10 and row['Pred'] != 1:
            return False
        else:
            return True

    def add_team_details_to_data_frame(self, df: pd.DataFrame):
        team = TeamDataFrame(self.game_predictor.db)
        for team_id in team.team_id_name_dic:
            df.loc[df.T_1 == team_id, 'T_1'] = team.team_id_name_dic[team_id]
            df.loc[df.T_2 == team_id, 'T_2'] = team.team_id_name_dic[team_id]



algorithms = [lm.ModelType.SEQUENTIAL_REGRESSION, lm.ModelType.SEQUENTIAL_CLASSIFICATION,
              lm.ModelType.LINEAR_CLASSIFICATION, lm.ModelType.LINEAR_REGRESSION]

# 3005|1. Fußball-Bundesliga 2016/2017 - 4153|1. Fußball-Bundesliga 2017/2018
game_prediction = GamePrediction(4153)
game_prediction.run_algorithm([lm.ModelType.LINEAR_CLASSIFICATION], 27, 28)
game_prediction.show_statistics()
game_prediction.print_overview()















