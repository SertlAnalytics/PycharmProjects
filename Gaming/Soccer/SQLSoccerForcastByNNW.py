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
from keras.layers import Dense
from keras.models import Sequential
from keras.utils import to_categorical
from sklearn import linear_model
from sklearn.metrics import confusion_matrix, classification_report


class BaseDB:
    def __init__(self):
        self.engine = self.__get_engine__()

    def __get_engine__(self):
        pass

    def get_result_set_for_table(self, table: str):
        connection = self.engine.connect()
        stmt = SQLStatement.get_select_statement_for_table(table)
        results = connection.execute(stmt).fetchall()
        connection.close()
        return results


class SoccerDatabase(BaseDB):
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
                , Team.TeamId as HomeTeamId, Team2.TeamId as ForeignTeamId, Team.TeamName as HomeTeam, Team2.TeamName as ForeignTeam
                , MatchResult.PointsTeam1, MatchResult.PointsTeam2
                , Case When MatchResult.PointsTeam1 is NULL Then 0 Else (10 + MatchResult.PointsTeam1 - MatchResult.PointsTeam2) End as GoalDifference
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


class DBBasedList:
    def __init__(self):
        self.db = SoccerDatabase()
        self.result_set = self.get_result_set_from_db()
        self.df = pd.DataFrame(self.result_set)
        self.df.columns = self.result_set[0].keys()

    def get_result_set_from_db(self):
        pass  # will be overwritten by sub classes

    def get_column_value_for_id(self, id: int, column: str):
        pass  # will be overwritten by deferred classes

    def get_column_values_for_id_list(self, id_list, column: str):
        return_list = []
        for ids in id_list:
            return_list.append(self.get_column_value_for_id(ids, column))
        return return_list


class DBGroupList(DBBasedList):
    def get_result_set_from_db(self):
        return self.db.get_result_set_for_table('GameGroup')

    def get_column_value_for_id(self, id: int, column: str):
        df_subset = self.df[self.df["GroupOrderId"] == id]
        return df_subset[column].values[0]


class DBTeamList(DBBasedList):
    def get_result_set_from_db(self):
        return self.db.get_result_set_for_table('Team')

    def get_column_value_for_id(self, id: int, column: str):
        df_subset = self.df[self.df["TeamId"] == id]
        return df_subset[column].values[0]


class MatchDataFrame:
    def __init__(self, db_result_set):
        self.df = pd.DataFrame(db_result_set)
        self.df.columns = db_result_set[0].keys()
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


class LeagueTable:
    def __init__(self, mdf: MatchDataFrame):
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
        team = DBTeamList()
        group = DBGroupList()
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
    def __init__(self, league_id_previous: int, league_id_actual: int):
        self.db = SoccerDatabase()
        self.league_id_previous = league_id_previous
        self.league_id_actual = league_id_actual
        self.df_match_previous = None
        self.df_match_actual = None
        self.actual_team_list = None
        self.actual_group_order_id_list = None
        self.training_set = []
        self.validation_set = []
        self.test_set = []

        # print(self.df_match_actual.year_table)
        # self.get_test_data()
        # print(self.test_data_list)

    def load_match_data_frames(self):
        self.df_match_previous = MatchDataFrame(self.db.get_result_set_for_league(self.league_id_previous))
        self.df_match_actual = MatchDataFrame(self.db.get_result_set_for_league(self.league_id_actual))

    def calculate_positions_for_df_match_actual(self):
        self.df_match_actual.fill_np_team_position_from_data_frame()

    def calculate_actual_match_table(self):
        self.df_match_actual.calculate_match_table()

    def init_actual_team_list(self):
        self.actual_team_list = DBTeamList()

    def init_actual_group_list(self):
        self.actual_group_order_id_list = DBGroupList()

    def calculate_training_set_for_next_group_order_id(self, league_table_previous: LeagueTable
                                  , league_table_actual: LeagueTable, group_order_id_next: int):
        self.training_set = []
        self.validation_set = []
        self.test_set = []

        for group_order_id in range(1, group_order_id_next + 1):
            match_teams_list_for_group_order_id = self.get_match_teams_list_for_group_order_id(group_order_id)
            for match_teams_list in match_teams_list_for_group_order_id:
                data = self.get_prediction_data_row(match_teams_list, group_order_id, league_table_actual, league_table_previous)
                if group_order_id == group_order_id_next:
                    self.test_set.append(data)
                else:
                    self.training_set.append(data)

    def get_prediction_data_row(self, match_teams_list, group_order_id, league_table_actual, league_table_previous):
        match_id = match_teams_list[-4]
        team_1 = match_teams_list[-3]
        team_2 = match_teams_list[-2]
        goal_difference = match_teams_list[-1]
        position_team_1_last_year = league_table_previous.get_last_position_for_team(team_1)
        position_team_1_before_group_order_id = league_table_actual. \
            get_position_for_team_before_group_order_id(group_order_id, team_1)
        position_team_2_last_year = league_table_previous.get_last_position_for_team(team_2)
        position_team_2_before_group_order_id = league_table_actual. \
            get_position_for_team_before_group_order_id(group_order_id, team_2)
        data_position = [position_team_1_last_year, position_team_1_before_group_order_id,
                         position_team_2_last_year, position_team_2_before_group_order_id]
        # data_position = [0, 0, 0, 0]
        data_home_team = self.get_results_for_team_in_earlier_group_order_id(group_order_id, team_1, True)
        data_foreign_team = self.get_results_for_team_in_earlier_group_order_id(group_order_id, team_2, False)
        test_data = data_position + data_home_team + data_foreign_team
        test_data.append( SoccerHelper.map_goal_difference_to_points(goal_difference))
        # print('calculate_training_set, group_order_id={}, match_id={}, team1={}, team2={}, test_data={}'
        #       .format(group_order_id, match_id, team_1, team_2, test_data))
        # test_data.append([group_order_id, match_id, team_1, team_2])
        return test_data

    def get_match_teams_list_for_group_order_id(self, group_order_id: int):
        return_list = []
        df_sel = self.df_match_actual.df[self.df_match_actual.df["GroupOrderId"] == group_order_id]
        for id, row in df_sel.iterrows():
            list_element = [group_order_id, row['MatchId'], row['HomeTeamId'], row['ForeignTeamId'], row['GoalDifference']]
            return_list.append(list_element)
        return return_list

    def get_results_for_team_in_earlier_group_order_id(self, group_order_id: int, team_id: int, is_playing_home: bool):
        return_list = []
        if is_playing_home:
            df_sel = self.df_match_actual.df[np.logical_and(self.df_match_actual.df["GroupOrderId"] < group_order_id,
                                                            self.df_match_actual.df["HomeTeamId"] == team_id)]
        else:
            df_sel = self.df_match_actual.df[np.logical_and(self.df_match_actual.df["GroupOrderId"] < group_order_id,
                                                            self.df_match_actual.df["ForeignTeamId"] == team_id)]

        for team_id in self.df_match_actual.team_list:
            return_list.append(0)
            for id, row in df_sel.iterrows():
                if is_playing_home and row['ForeignTeamId'] == team_id:
                    return_list[-1] = row['GoalDifference']
                elif not is_playing_home and row['HomeTeamId'] == team_id:
                    return_list[-1] = row['GoalDifference']
        return return_list


class Optimizer:
    ADAM = "adam"
    SGD = "Stochastic gradient descent"


class LossFunction:
    MSE = "mean_squared_error"
    CAT_CROSS = "categorical_crossentropy"


class ModelType:
    SEQUENTIAL_REGRESSION = "Model: Sequential, Type: Regression"
    SEQUENTIAL_CLASSIFICATION = "Model: Sequential, Type: Classification"
    LINEAR_REGRESSION = "Model: Linear, Type: Regression"
    LINEAR_CLASSIFICATION = "Model: Linear, Type: Classification"


class LearningMachine:
    def __init__(self, hidden_layers, optimizer: Optimizer = Optimizer.ADAM
                 , loss: LossFunction = LossFunction.MSE):
        self.hidden_layers = hidden_layers
        self.model = None
        self.model_type = None
        self.optimizer = optimizer
        self.loss = loss
        self.n_cols = 0
        self.np_predictors = None
        self.np_target = None
        self.np_prediction_data = None
        self.prediction = None

    def get_regression_prediction(self, predictors: np.array, target: np.array, prediction_data: np.array):
        return self.__get_prediction__(np_predictors, np_target, np_pred_data)

    def __get_prediction__(self, predictors: np.array, target: np.array, prediction_data: np.array):
        self.np_predictors = predictors
        self.__set_np_target__(target)
        self.np_prediction_data = prediction_data
        self.n_cols = self.np_predictors.shape[1]
        # self.print_details()
        self.model = self.get_model()
        self.__add_hidden_layers__()
        self.__add_output_layer__()
        self.__compile_model__()
        self.model.fit(self.np_predictors, self.np_target)
        # make prediction
        self.prediction = self.model.predict(self.np_prediction_data)
        self.prediction = self.prediction.reshape(self.prediction.shape[0], self.np_target.shape[1])
        return self.prediction

    def get_model(self):
        pass

    def __set_np_target__(self, target: np.array):
        self.np_target = target

    def __add_output_layer__(self):
        pass

    def __get_predicted_value_for_row_index__(self, k: int):
        return self.prediction[k][0]

    def __compile_model__(self):
        pass

    def compare_prediction_with_results(self, test_set_target: np.array):
        np_comparison = np.zeros((self.prediction.shape[0], 3), dtype=np.float)
        for k in range(self.prediction.shape[0]):
            np_comparison[k, 0] = self.__get_predicted_value_for_row_index__(k)
            np_comparison[k, 1] = test_set_target[k]
            np_comparison[k, 2] = np_comparison[k, 0] - np_comparison[k, 1]
        print(np.round(np_comparison, 2))
        self.__print_statistical_data__(test_set_target)

    def __print_statistical_data__(self, test_set_target: np.array):
        pass

    def print_details(self):
        print('optimizer={}, loss={}, np_predictors.shape={}, np_target.shape={}, np_pred_data.shape={}'.format(
            self.optimizer, self.loss, self.np_predictors.shape, self.np_target.shape, self.np_prediction_data.shape))

    def __add_hidden_layers__(self):
        pass


class LmLinearRegression(LearningMachine):
    def __init__(self):  # is needed since we don't need any other parameters
        pass

    def get_model(self):
        return linear_model.LinearRegression()

    def __print_statistical_data__(self, np_test_set_target : np.array):
        print("Accuracy: {}".format(self.model.score(self.np_prediction_data, np_test_set_target)))


class LmLogisticRegression(LearningMachine):
    def __init__(self):  # is needed since we don't need any other parameters
        pass

    def get_model(self):
        return linear_model.LogisticRegression()

    def __print_statistical_data__(self, np_test_set_target : np.array):
        print("Accuracy: {}".format(self.model.score(self.np_prediction_data, np_test_set_target)))
        print(confusion_matrix(np_test_set_target, self.prediction))
        print(classification_report(np_test_set_target, self.prediction))


class LmSequentialRegression(LearningMachine):
    def get_model(self):
        return Sequential()

    def __add_hidden_layers__(self):
        for hl_index, hidden_layers in enumerate(self.hidden_layers):
            if hl_index == 0:
                self.model.add(Dense(hidden_layers, activation='relu', input_shape=(self.n_cols,)))
            else:
                self.model.add(Dense(hidden_layers, activation='relu'))

    def __add_output_layer__(self):
        self.model.add(Dense(self.np_target.shape[1]))  # output layer

    def __compile_model__(self):
        self.model.compile(optimizer=self.optimizer, loss=self.loss)


class LmSequentialClassification(LearningMachine):
    def __init__(self, hidden_layers, optimizer: Optimizer = Optimizer.ADAM
                 , loss: LossFunction = LossFunction.CAT_CROSS):
        LearningMachine.__init__(self, hidden_layers, optimizer, loss)

    def get_model(self):
        return Sequential()

    def __add_hidden_layers__(self):
        for hl_index, hidden_layers in enumerate(self.hidden_layers):
            if hl_index == 0:
                self.model.add(Dense(hidden_layers, activation='relu', input_shape=(self.n_cols,)))
            else:
                self.model.add(Dense(hidden_layers, activation='relu'))

    def __compile_model__(self):
        self.model.compile(optimizer=self.optimizer, loss=self.loss, metrics=['accuracy'])

    def __set_np_target__(self, target: np.array):
        self.np_target = to_categorical(target)

    def __add_output_layer__(self):
        self.model.add(Dense(self.np_target.shape[1], activation='softmax'))

    def __get_predicted_value_for_row_index__(self, k: int):
        return self.prediction[k].argmax(axis=0)


class TestDataGenerator:
    @staticmethod
    def get_test_data_for_summation():
        list_1 = [
            [1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1], [0, 1, 0, 0, 1], [0, 0, 1, 0, 1], [0, 0, 0, 1, 1], [0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1], [0, 1, 1, 1, 1]
        ]
        np_predictors = np.array(list_1)
        np_target = np_predictors.sum(axis=1).reshape(np_predictors.shape[0], 1)
        list_2 = [
            [1, 1, 0, 0, 0], [0, 1, 1, 0, 0], [0, 0, 1, 1, 0], [0, 0, 0, 1, 1], [0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1], [1, 1, 0, 0, 1], [0, 0, 1, 0, 1], [0, 0, 0, 1, 1], [1, 0, 0, 0, 1]
        ]
        np_pred_data = np.array(list_2)
        np_pred_data_target = np_pred_data.sum(axis=1).reshape(np_pred_data.shape[0], 1)
        return np_predictors, np_target, np_pred_data, np_pred_data_target


game_predictor = GamePredictor(3005, 4153)  # 3005|1. Fußball-Bundesliga 2016/2017 --- 4153 2017/2018
game_predictor.load_match_data_frames()

previous_table = LeagueTable(game_predictor.df_match_previous)
previous_table.calculate_np_team_position()
actual_table = LeagueTable(game_predictor.df_match_actual)
actual_table.calculate_np_team_position()

game_predictor.calculate_training_set_for_next_group_order_id(previous_table, actual_table, 10)

np_training_set = np.array(game_predictor.training_set)
np_test_set = np.array(game_predictor.test_set)

np_predictors = np_training_set[:,:-1]
np_target = np_training_set[:,-1]
np_target = np_target.reshape((np_target.size, 1))
np_pred_data = np_test_set[:,:-1]

np_test_set_target = np_test_set[:,-1]
np_test_set_target = np_test_set_target.reshape((np_test_set_target.size,1))

[np_predictors, np_target, np_pred_data, np_test_set_target] = TestDataGenerator.get_test_data_for_summation()
print(np_predictors.shape)
print(np_target.shape)
print(np_pred_data.shape)
print(np_test_set_target.shape)

# print(type(np_target))
# print(np_target)

hidden_layers = [200, 50]

lm_regression = LmSequentialRegression(hidden_layers)
lm_regression.get_regression_prediction(np_predictors, np_target, np_pred_data)
lm_regression.compare_prediction_with_results(np_test_set_target)

# lm_classification = LmSequentialClassification(hidden_layers)
# lm_classification.get_regression_prediction(np_predictors, np_target, np_pred_data)
# lm_classification.compare_prediction_with_results(np_test_set_target)

# lm_linear_regression = LmLinearRegression()
# lm_linear_regression.get_regression_prediction(np_predictors, np_target, np_pred_data)
# lm_linear_regression.compare_prediction_with_results(np_test_set_target)

# lm_logistic_regression = LmLogisticRegression()
# lm_logistic_regression.get_regression_prediction(np_predictors, np_target, np_pred_data)
# lm_logistic_regression.compare_prediction_with_results(np_test_set_target)











