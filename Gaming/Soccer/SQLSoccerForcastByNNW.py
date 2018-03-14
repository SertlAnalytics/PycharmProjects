import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import math


class SoccerDatabase:
    def __init__(self):
        self.engine = create_engine('sqlite:///MySoccer.sqlite')

    def get_result_set_for_league(self, league_id: int):
        connection = self.engine.connect()
        stmt = SQLStatement.get_select_statement_for_league(league_id)
        results = connection.execute(stmt).fetchall()
        connection.close()
        return results

    def get_result_set_for_table(self, table: str):
        connection = self.engine.connect()
        stmt = SQLStatement.get_select_statement_for_table(table)
        results = connection.execute(stmt).fetchall()
        connection.close()
        return results


class SQLStatement:
    @staticmethod
    def get_select_statement_for_league(league_id: int):
        stmt = """
                SELECT League.LeagueId, League.LeagueName, GameGroup.GroupId, GameGroup.GroupName
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
                Order by League.LeagueId, GameGroup.GroupId, Match.MatchId
                """
        return stmt

    @staticmethod
    def get_select_statement_for_table(table: str):
        stmt = "SELECT * FROM " + str(table)
        return stmt


class GamePredictor:
    def __init__(self, league_id_previous: int, league_id_actual: int):
        self.db = SoccerDatabase()
        self.league_id_previous = league_id_previous
        self.league_id_actual = league_id_actual
        self.df_match_previous = None
        self.df_match_actual = None
        self.actual_team_list = None
        self.actual_group_id_list = None
        self.test_data_list = []

        # print(self.df_match_actual.year_table)
        # self.get_test_data()
        # print(self.test_data_list)

    def load_match_data_frames(self):
        self.df_match_previous = MatchDataFrame(self.db.get_result_set_for_league(self.league_id_previous))
        self.df_match_actual = MatchDataFrame(self.db.get_result_set_for_league(self.league_id_actual))

    def calculate_positions_for_df_match_actual(self):
        self.df_match_actual.fill_np_team_position_from_data_frame()
        print(self.df_match_actual.np_team_position)

    def calculate_actual_match_table(self):
        self.df_match_actual.calculate_match_table()

    def init_actual_team_list(self):
        self.actual_team_list = TeamList(self.df_match_actual.get_team_list())
        print(self.actual_team_list.sorted_id_list)

    def init_actual_group_list(self):
        self.actual_group_id_list = GroupList(self.df_match_actual.get_group_id_list())

    def get_test_data(self):
        year_table = self.df_match_actual.year_table

        for index_1, team_id1 in enumerate(self.actual_team_list):
            for index_2, team_id2 in enumerate(self.actual_team_list):
                value_list = year_table[index_1][index_2]
                group_id = value_list[-1]
                result = value_list[-2]

                for group_ids in self.actual_group_id_list:
                    if group_ids == group_id:
                        continue
                    test_data_list = [0, 0, 0, 0]  # positions last year / current year

                    for index_f, team_id_f in enumerate(self.actual_team_list):
                        test_data_list.append(0)  # default
                        if team_id1 != team_id_f:
                            value_list = year_table[index_1][index_f]
                            if value_list[-1] == group_ids:
                                test_data_list[-1] = value_list[-2]

                    for index_f, team_id_f in enumerate(self.actual_team_list):
                        test_data_list.append(0)  # default
                        if team_id2 != team_id_f:
                            value_list = year_table[index_f][index_2]
                            if value_list[-1] == group_ids:
                                test_data_list[-1] = value_list[-2]
                    test_data_list.append(result)
                    test_data_list.append(team_id1)
                    test_data_list.append(team_id2)
                    test_data_list.append(group_id)

                    self.test_data_list.append(test_data_list)


class DBBasedList:
    def __init__(self, sorted_id_list):
        self.db = SoccerDatabase()
        self.result_set = self.get_result_set_from_db()
        self.df = pd.DataFrame(self.result_set)
        self.df.columns = self.result_set[0].keys()
        self.sorted_id_list = sorted_id_list
        self.sorted_index_list = self.sorted_id_list

    def get_result_set_from_db(self):
        pass  # will be overwritten by sub classes

    def get_id_for_index(self, index: int):
        return self.sorted_id_list[index]

    def get_column_value_for_index(self, index: int, column: str):
        return self.get_column_value_for_id(self.get_id_for_index(index), column)

    def get_column_value_for_id(self, id: int, column: str):
        pass  # will be overwritten by deferred classes


class GroupList(DBBasedList):
    def get_result_set_from_db(self):
        return self.db.get_result_set_for_table('GameGroup')

    def get_column_value_for_id(self, id: int, column: str):
        df_subset = self.df[self.df["GroupId"] == id]
        return df_subset[column].values[0]


class TeamList(DBBasedList):
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
        self.group_id_list = np.sort(pd.unique(self.df["GroupId"]))
        self.match_table = []

    def get_team_list(self):
        return self.team_list

    def get_group_id_list(self):
        return self.group_id_list

    def calculate_match_table(self):  # 2 dim array for all matches with lists
        default_list = [0, 0, 0, 0, 0, 0]  # (GoalHome, GoalForeign, 10 + GH - GF, PointsHome, PointsForeign, groupId)
        self.match_table = [[default_list for t1 in self.team_list] for t2 in self.team_list]

        for index_1, team_id_1 in enumerate(self.team_list):
            for index_2, team_id_2 in enumerate(self.team_list):
                df_sel = self.df[np.logical_and(self.df["HomeTeamId"] == team_id_1, self.df["ForeignTeamId"] == team_id_2)]
                for id, row in df_sel.iterrows():
                    value_list = [0, 0, 0, 0, 0, row["GroupId"]]
                    if not math.isnan(row["PointsTeam1"]) and not math.isnan(row["PointsTeam2"]):
                        value_list[0] = row["PointsTeam1"]
                        value_list[1] = row["PointsTeam2"]
                        [value_list[2], value_list[3]] = SoccerHelper.get_points_for_teams(value_list[0], value_list[1])
                        value_list[4] = 10 + value_list[0] - value_list[1]
                    self.match_table[index_1][index_2] = value_list


class SoccerHelper:
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
        self.group_id_list = mdf.group_id_list
        self.np_table = np.empty((self.team_list.size, len(self.TABLE_COL_DIC)))
        self.np_team_position = np.empty((self.team_list.size, self.group_id_list.size))
        self.__initialize_np_arrays__()

    def __initialize_np_arrays__(self):
        self.np_table = np.zeros((self.team_list.size, len(self.TABLE_COL_DIC)), dtype=np.int32)
        self.np_team_position = np.zeros((self.team_list.size, self.group_id_list.size), dtype=np.int32)

    def calculate_np_team_position(self):
        self.__initialize_np_arrays__()

        for team_index, team_id in enumerate(self.team_list):
            print('Init np_table: team_index={}, team={}'.format(team_index, team_id))
            self.np_table[team_index, self.TABLE_COL_DIC["TeamId"]] = team_id

        for group_id_index, group_id in enumerate(self.group_id_list):
            df_sel_group = self.df[self.df["GroupId"] == group_id]
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
            self.add_actual_positions(group_id_index)

    def add_actual_positions(self, group_id_index: int):
        np_table_sorted_team_col = self.np_table[:, 0]
        for index_team, team_id in enumerate(self.team_list):
            if team_id in np_table_sorted_team_col:
                position = self.get_team_index_in_sorted_np_table(team_id) + 1
            else:
                position = np_table_sorted_team_col.size
            self.np_team_position[index_team, group_id_index] = position

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


game_predictor = GamePredictor(3005, 4153)  # 3005|1. Fußball-Bundesliga 2016/2017 --- 4153 2017/2018
game_predictor.load_match_data_frames()
# game_predictor.calculate_actual_match_table()
league_table = LeagueTable(game_predictor.df_match_actual)
league_table.calculate_np_team_position()
print(league_table.np_table)
print(league_table.np_team_position)

# print('previous table: {}'.format(soccer_db.np_table_previous))
# print('actual table: {}'.format(soccer_db.np_table_actual))
# print('team positions: {}'.format(soccer_db.team_positions))


def make_prediction(np_predictors: np.array, np_target: np.array, np_pred_data: np.array):
    import numpy as np
    from keras.layers import Dense
    from keras.models import Sequential
    # Specify, compile, and fit the model
    print('np_predictors.shape={}, np_target.shape={}, np_pred_data.shape={}'.format(np_predictors.shape, np_target.shape, np_pred_data.shape))
    n_cols = np_predictors.shape[1]
    print('n_cols = {}'.format(n_cols))
    model = Sequential()
    model.add(Dense(32, activation='relu', input_shape=(n_cols,)))
    model.add(Dense(30, activation='relu'))
    model.add(Dense(306))  # output layer
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(np_predictors, np_target)

    # Calculate predictions: predictions
    predictions = model.predict(np_pred_data)
    # Calculate predicted probability of survival: predicted_prob_true
    print(predictions)
    # predicted_prob_true = predictions[:, 1]
    # # print predicted_prob_true
    # print(predicted_prob_true)

# [np_predictors, np_target, np_pred_data] = get_nparrays(df)
# make_prediction(np_predictors, np_target, np_pred_data)







