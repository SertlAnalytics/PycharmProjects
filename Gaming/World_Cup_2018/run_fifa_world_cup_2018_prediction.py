"""
Description: This module calculates predictions for the FIFA World Cup 2018 in Russia
Based on the data of FIFA World Cup 2014 in Brasil.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-13
"""

import os
import matplotlib.pyplot as plt
from sertl_analytics.datafetcher.file_fetcher import FileFetcher
import pandas as pd
import numpy as np
import math
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score


class FC:
    MATCH_NUMBER = 'match_number'
    DATE = 'date'
    LOCATION = 'location'
    STATUS = 'status'
    HOME_TEAM = 'home_team/country'
    HOME_TEAM_KEY = 'home_team/code'
    GOALS_HOME = 'home_team/goals'
    AWAY_TEAM = 'away_team/country'
    AWAY_TEAM_KEY = 'away_team/code'
    GOALS_AWAY = 'away_team/goals'
    HOME_PENALTIES = 'home_team/penalties'
    AWAY_PENALTIES = 'away_team/penalties'
    HOME_TEAM_RANKING = 'home_team_ranking'
    AWAY_TEAM_RANKING = 'away_team_ranking'
    HOME_TEAM_RANKING_SQU = 'home_team_ranking_squared'
    HOME_TEAM_RANKING_SQRT = 'home_team_ranking_sqrt'
    AWAY_TEAM_RANKING_SQU = 'away_team_ranking_squared'
    AWAY_TEAM_RANKING_SQRT = 'away_team_ranking_sqrt'
    TEAM_RANKING_PRODUCT = 'team_ranking_product'
    WINNER = 'winner_system'


class WorldCupRankingAdjustmentApi:
    def __init__(self, actual_min_penalty = np.inf):
        self.actual_min_penalty = actual_min_penalty
        self.penalty = 0
        self.ranking_difference = 0
        self.ranking_reduction_factor = 0
        self.ranking_enhancement_factor = 0
        self.penalty_wrong_winner = 0
        self.penalty_wrong_remis = 0
        self.penalty_not_remis = 0

    def clone(self):
        api = WorldCupRankingAdjustmentApi(self.actual_min_penalty)
        api.penalty = self.penalty
        api.ranking_difference = self.ranking_difference
        api.ranking_reduction_factor = self.ranking_reduction_factor
        api.ranking_enhancement_factor = self.ranking_enhancement_factor
        api.penalty_wrong_winner = self.penalty_wrong_winner
        api.penalty_wrong_remis = self.penalty_wrong_remis
        api.penalty_not_remis = self.penalty_not_remis
        return api

    def print(self):
        print('Penalty: {:2.0f} for Ranking_difference: {} Reduction_factor: {:1.1f} Enhancement_factor: {:1.1f} '
              'Penalty_wrong_winner: {} Penalty_wrong_remis: {} Penalty_not_remis: {}'.format(
            self.actual_min_penalty, self.ranking_difference, self.ranking_reduction_factor, self.ranking_enhancement_factor,
            self.penalty_wrong_winner, self.penalty_wrong_remis, self.penalty_not_remis)
        )


class WorldCupConfiguration:
    def __init__(self):
        self.__excel_directory = 'C:/Users/josef/OneDrive/Company/Machine_Learning/Soccer_2018'
        self.__excel_2014_file = 'Fifa_world_cup_2014_matches.xlsx'
        self.__excel_2014_tabs = ['Fifa_world_cup_2014_matches', 'Ranking']
        self.__excel_2018_file = 'Fifa_world_cup_2018_matches.xlsx'
        self.__excel_2018_tabs = ['Fifa_world_cup_2018_matches', 'Ranking']

    @property
    def excel_2014_tabs(self):
        return self.__excel_2014_tabs

    @property
    def excel_2018_tabs(self):
        return self.__excel_2018_tabs

    def get_excel_2014_file_path(self):
        return os.path.join(self.__excel_directory, self.__excel_2014_file)

    def get_excel_2018_file_path(self):
        return os.path.join(self.__excel_directory, self.__excel_2018_file)


config = WorldCupConfiguration()


class WorldCupTeam:
    def __init__(self, name: str, ranking: int, points: int = 0):
        self.name = name
        self.ranking = ranking
        self.points = points
        self.ranking_adjusted = self.ranking

    def print(self):
        print('Team: {:20} {:>3} {:2.0f} -> {:2.0f}'.format(
            self.name, 'Ranking:', self.ranking, self.ranking_adjusted))


class WorldCupTeamList:
    def __init__(self):
        self.__team_dic = {}

    @property
    def length(self):
        return len(self.__team_dic)

    def add_team(self, team: WorldCupTeam):
        self.__team_dic[team.name] = team

    def get_team(self, name: str) -> WorldCupTeam:
        return self.__team_dic[name]

    def reset_ranking_adjusted(self):
        for key in self.__team_dic:
            self.__team_dic[key].ranking_adjusted = self.__team_dic[key].ranking

    def print_list(self):
        for key in self.__team_dic:
            self.__team_dic[key].print()


class WorldCupMatch:
    def __init__(self, team_list: WorldCupTeamList, df_row):
        self.number = df_row[FC.MATCH_NUMBER]
        self.location = df_row[FC.LOCATION]
        self.date = df_row[FC.DATE] if FC.DATE in df_row else ''
        self.status = df_row[FC.STATUS]
        self.team_1 = team_list.get_team(df_row[FC.HOME_TEAM])
        self.team_2 = team_list.get_team(df_row[FC.AWAY_TEAM])
        self.goal_team_1 = df_row[FC.GOALS_HOME]
        self.goal_team_2 = df_row[FC.GOALS_AWAY]
        self.goal_team_1_penalty = 0 if df_row[FC.HOME_PENALTIES] is None else df_row[FC.HOME_PENALTIES]
        self.goal_team_2_penalty = 0 if df_row[FC.AWAY_PENALTIES] is None else df_row[FC.AWAY_PENALTIES]
        self.goal_team_1_simulation = 0
        self.goal_team_2_simulation = 0
        self.probability_list = []
        self.is_simulation = False

    @property
    def team_names(self):
        return self.team_1.name + ' - ' + self.team_2.name

    @property
    def short(self):
        return '{:2}. {:<30} {:10} {}:{}  Simulation: {}:{} - Ranking_adjusted: {:>4.1f} : {:>4.1f} {} - {}'.format(
            self.number, self.team_names, self.status, self.goal_team_1, self.goal_team_2,
            self.goal_team_1_simulation, self.goal_team_2_simulation,
            self.team_1.ranking_adjusted, self.team_2.ranking_adjusted,
            ' - SIMULATION' if self.is_simulation else ' - NO simulation', self.probability_list)

    def print(self):
        print(self.short)

    @property
    def ranking_adjusted_difference(self):
        return abs(self.team_1.ranking_adjusted - self.team_2.ranking_adjusted)

    def get_winner(self):
        if self.status == 'open':
            return None
        if self.goal_team_1 > self.goal_team_2:
            return 1
        elif self.goal_team_1_penalty > self.goal_team_2_penalty:
            return 1
        elif self.goal_team_1 < self.goal_team_2:
            return 2
        elif self.goal_team_1_penalty < self.goal_team_2_penalty:
            return 2
        return 0

    def simulate_by_probabilities(self, probability_array):
        self.probability_list = list(probability_array)
        max_val = max(self.probability_list)
        max_idx = self.probability_list.index(max_val)
        max_idx = self.__get_corrected_max_idx__(max_idx, max_val)
        factor = 3
        self.is_simulation = True
        if max_idx == 0:
            self.goal_team_1_simulation = int(round(factor * max_val))
            self.goal_team_2_simulation = int(round(factor * max_val))
        elif max_idx == 1:
            self.goal_team_1_simulation = int(round(factor * max_val))
            self.goal_team_2_simulation = int(round(factor * self.probability_list[2]))
        elif max_idx == 2:
            self.goal_team_1_simulation = int(round(factor * self.probability_list[1]))
            self.goal_team_2_simulation = int(round(factor * max_val))

    def __get_corrected_max_idx__(self, max_idx: int, max_val: float):
        if max_val > 0.5:
            return max_idx
        for idx, val in enumerate(self.probability_list):
            if val == max_val and idx != max_idx:
                return 1 if self.team_1.ranking_adjusted < self.team_2.ranking_adjusted else max_idx
        return max_idx

    def simulate_with_winner_by_model(self, winner_by_model: int):
        self.goal_team_1_simulation = self.goal_team_1
        self.goal_team_2_simulation = self.goal_team_2
        if self.status == 'open':
            self.is_simulation = True
            if winner_by_model == 0:
                self.goal_team_1_simulation = 1
                self.goal_team_2_simulation = 1
            elif winner_by_model == 1:
                self.goal_team_1_simulation = 2
                self.goal_team_2_simulation = 1
            elif winner_by_model == 2:
                self.goal_team_1_simulation = 1
                self.goal_team_2_simulation = 2

    def get_projected_winner(self, api: WorldCupRankingAdjustmentApi, for_simulation: bool):
        if self.status == 'completed' and for_simulation:
            return self.get_winner()
        if self.ranking_adjusted_difference >= api.ranking_difference:
            return 1 if self.team_1.ranking_adjusted < self.team_2.ranking_adjusted else 2
        else:
            return 0

    def adjust_ranking_after_simulation(self, api: WorldCupRankingAdjustmentApi, winner_simulation: int):
        self.__adjust_ranking_for_winner__(api, winner_simulation)

    def adjust_ranking(self, api: WorldCupRankingAdjustmentApi):
        winner = self.get_winner()
        self.__adjust_ranking_for_winner__(api, winner)

    def __adjust_ranking_for_winner__(self, api: WorldCupRankingAdjustmentApi, winner):
        r_red = self.ranking_adjusted_difference * api.ranking_reduction_factor
        r_enh = self.ranking_adjusted_difference * api.ranking_enhancement_factor
        if winner == 0:
            if self.team_1.ranking_adjusted < self.team_2.ranking_adjusted:
                self.team_1.ranking_adjusted += r_enh / 2
                self.team_2.ranking_adjusted += - r_red / 2
            else:
                self.team_2.ranking_adjusted += r_enh / 2
                self.team_1.ranking_adjusted += - r_red / 2
        elif winner == 1:
            if self.team_1.ranking_adjusted > self.team_2.ranking_adjusted:
                self.team_1.ranking_adjusted += - r_red
                self.team_2.ranking_adjusted += r_enh
        elif winner == 2:
            if self.team_1.ranking_adjusted < self.team_2.ranking_adjusted:
                self.team_1.ranking_adjusted += r_enh
                self.team_2.ranking_adjusted += - r_red


class WorldCupMatchList:
    def __init__(self):
        self.index_list = []
        self.__match_dic = {}

    @property
    def length(self):
        return len(self.index_list)

    def add_match(self, match: WorldCupMatch):
        self.__match_dic[match.number] = match
        self.index_list.append(match.number)

    def get_match(self, number: int) -> WorldCupMatch:
        return self.__match_dic[number]

    def print_list(self):
        for index in self.index_list:
            self.__match_dic[index].print()


class WorldCup:
    def __init__(self, year: int, host: str):
        self.year = year
        self.host = host
        self.df_match = None
        self.df_ranking = None
        self.df_4_ml = None
        self.team_list = WorldCupTeamList()
        self.match_list = WorldCupMatchList()
        self.__init_lists__()
        self._api_for_ranking_adjustments = self.__get_ranking_adjustment_parameters__()
        self._api_for_ranking_adjustments.print()
        self.__add_team_ranking_to_df_match__()
        self.__create_df_4_ml__()
        self.__print_statistics__()

    @property
    def api_for_ranking_adjustments(self):
        return self._api_for_ranking_adjustments

    @property
    def first_open_match_number(self):
        for number in self.match_list.index_list:
            match = self.match_list.get_match(number)
            if match.status == 'open':
                return number
        return 0

    def plot_data(self):
        xs = self.df_match[FC.HOME_TEAM_RANKING]
        ys = self.df_match[FC.AWAY_TEAM_RANKING]
        labels = self.df_match[FC.WINNER]
        plt.scatter(xs, ys, c=labels)
        plt.show()

    def __print_statistics__(self):
        print('WorldCup statistics for {} ({}): Number Teams = {}, Number Matches with teams = {}'.format(
            self.year, self.host, self.team_list.length, self.match_list.length))

    def __add_team_ranking_to_df_match__(self):
        for ind, rows in self.df_match.iterrows():
            if rows[FC.HOME_TEAM] not in ['', pd.np.nan]:
                match = self.match_list.get_match(rows[FC.MATCH_NUMBER])
                team_1 = self.team_list.get_team(rows[FC.HOME_TEAM])
                team_2 = self.team_list.get_team(rows[FC.AWAY_TEAM])
                self.df_match.loc[ind, FC.HOME_TEAM_RANKING] = round(team_1.ranking_adjusted, 1)
                self.df_match.loc[ind, FC.AWAY_TEAM_RANKING] = round(team_2.ranking_adjusted, 1)
                self.df_match.loc[ind, FC.HOME_TEAM_RANKING_SQU] = round(team_1.ranking_adjusted**2, 1)
                self.df_match.loc[ind, FC.AWAY_TEAM_RANKING_SQU] = round(team_2.ranking_adjusted**2, 1)
                self.df_match.loc[ind, FC.HOME_TEAM_RANKING_SQRT] = round(math.sqrt(team_1.ranking_adjusted), 1)
                self.df_match.loc[ind, FC.AWAY_TEAM_RANKING_SQRT] = round(math.sqrt(team_2.ranking_adjusted), 1)
                self.df_match.loc[ind, FC.TEAM_RANKING_PRODUCT] = \
                    round(team_1.ranking_adjusted * team_2.ranking_adjusted, 1)
                self.df_match.loc[ind, FC.WINNER] = match.get_winner()
                match.adjust_ranking(self._api_for_ranking_adjustments)

    def __create_df_4_ml__(self):
        self.df_4_ml = self.df_match.loc[:, FC.HOME_TEAM_RANKING : FC.WINNER]

    def __init_lists__(self):
        if self.year == 2014:
            file_path = config.get_excel_2014_file_path()
            self.df_match = FileFetcher(file_path, sheet_name=config.excel_2014_tabs[0]).df
            self.df_ranking = FileFetcher(file_path, sheet_name=config.excel_2014_tabs[1]).df
        else:
            file_path = config.get_excel_2018_file_path()
            self.df_match = FileFetcher(file_path, sheet_name=config.excel_2018_tabs[0]).df
            self.df_ranking = FileFetcher(file_path, sheet_name=config.excel_2018_tabs[1]).df
        self.__fill_team_list__()
        self.__fill_match_list__()

    def __fill_team_list__(self):
        for ind, row in self.df_ranking.iterrows():
            team = WorldCupTeam(row[0], row[1])
            self.__adjust_official_ranking__(team)
            self.team_list.add_team(team)

    def __adjust_official_ranking__(self, team: WorldCupTeam):
        if team.name == self.host:
            team.ranking = round(team.ranking * 0.9, 2)
            team.ranking_adjusted = team.ranking

    def __fill_match_list__(self):
        for ind, row in self.df_match.iterrows():
            if row[FC.HOME_TEAM] not in ['', pd.np.nan]:
                match = WorldCupMatch(self.team_list, row)
                self.match_list.add_match(match)

    def __get_ranking_adjustment_parameters__(self) -> WorldCupRankingAdjustmentApi:
        pass

    def simulate_model(self, api: WorldCupRankingAdjustmentApi):
        print('Caution: Simulation is done only for matches in status "open".')
        self.team_list.reset_ranking_adjusted()
        for index in self.match_list.index_list:
            match = self.match_list.get_match(index)
            winner_by_model = match.get_projected_winner(api, True)
            match.simulate_with_winner_by_model(winner_by_model)
            match.adjust_ranking_after_simulation(api, winner_by_model)


class WorldCup4Training(WorldCup):
    def __get_ranking_adjustment_parameters__(self) -> WorldCupRankingAdjustmentApi:
        ranking_diff = np.arange(10, 0, -1)
        ranking_reduction_factors = np.arange(0.7, 0, -0.1)
        ranking_enhancement_factors = np.arange(0.7, 0, -0.1)
        penalty_wrong_winner = [1, 2, 3]
        penalty_wrong_remis = [1, 2, 3]
        penalty_not_remis = [1, 2, 3]

        # ranking_diff = [1]
        # ranking_reduction_factors = [0.7]
        # ranking_enhancement_factors = [0.2]
        # penalty_wrong_winner = [1]
        # penalty_wrong_remis = [1]
        # penalty_not_remis = [1]

        api_penalty_min = WorldCupRankingAdjustmentApi(np.inf)
        for diff in ranking_diff:
            api = WorldCupRankingAdjustmentApi(api_penalty_min.actual_min_penalty)
            api.ranking_difference = diff
            for r_factors in ranking_reduction_factors:
                api.ranking_reduction_factor = r_factors
                for e_factors in ranking_enhancement_factors:
                    api.ranking_enhancement_factor = e_factors
                    for p_wrong_winner in penalty_wrong_winner:
                        api.penalty_wrong_winner = p_wrong_winner
                        for p_wrong_remis in penalty_wrong_remis:
                            api.penalty_wrong_remis = p_wrong_remis
                            for p_not_remis in penalty_not_remis:
                                api.penalty_not_remis = p_not_remis
                                self.__calculate_penalty_for_this_ranking_adjustment_model__(api)
                                if api.penalty < api_penalty_min.actual_min_penalty:
                                    api.actual_min_penalty = api.penalty
                                    api_penalty_min = api.clone()
                                    # api_penalty_min.print()
                                    # self.team_list.print_list()
        self.team_list.reset_ranking_adjusted()
        return api_penalty_min

    def __calculate_penalty_for_this_ranking_adjustment_model__(self, api: WorldCupRankingAdjustmentApi):
        api.penalty = 0
        self.team_list.reset_ranking_adjusted()
        for index in self.match_list.index_list:
            match = self.match_list.get_match(index)
            if match.status == 'completed':
                winner = match.get_winner()
                winner_by_model = match.get_projected_winner(api, False)
                match.adjust_ranking(api)
                if winner != winner_by_model:
                    if winner == 0:
                        api.penalty += api.penalty_not_remis
                    elif winner in [1, 2] and winner_by_model == 0:
                        api.penalty += api.penalty_wrong_remis
                    elif (winner == 1 and winner_by_model == 2) or (winner == 2 and winner_by_model == 1):
                        api.penalty += api.penalty_wrong_winner
                # end this check....
                if api.penalty > api.actual_min_penalty:
                    return


class WorldCup4Test(WorldCup):
    def __init__(self, year: int, host: str, api: WorldCupRankingAdjustmentApi):
        self._api_for_ranking_adjustments = api
        WorldCup.__init__(self, year, host)

    def __get_ranking_adjustment_parameters__(self) -> WorldCupRankingAdjustmentApi:
        return self._api_for_ranking_adjustments


class WorldCupModel:
    def __init__(self):
        self.world_cup_2014 = WorldCup4Training(2014, 'Brasil')
        self.world_cup_2018 = WorldCup4Test(2018, 'Russia', self.world_cup_2014.api_for_ranking_adjustments)
        self.df_train = self.world_cup_2014.df_4_ml
        self.df_test = self.world_cup_2018.df_4_ml
        self.__y_train = np.array(self.df_train.iloc[:, -1])
        self.forest_clf = RandomForestClassifier(n_estimators=10, random_state=42)

    def __get_column_start_end_with_best_score__(self) -> list:
        col_start_end_list = [[FC.HOME_TEAM_RANKING, FC.AWAY_TEAM_RANKING]]
        col_start_end_list.append([FC.HOME_TEAM_RANKING_SQU, FC.AWAY_TEAM_RANKING_SQU])
        col_start_end_list.append([FC.HOME_TEAM_RANKING_SQRT, FC.AWAY_TEAM_RANKING_SQRT])
        col_start_end_list.append([FC.HOME_TEAM_RANKING, FC.AWAY_TEAM_RANKING_SQU])
        col_start_end_list.append([FC.HOME_TEAM_RANKING_SQU, FC.AWAY_TEAM_RANKING_SQRT])
        col_start_end_list.append([FC.HOME_TEAM_RANKING, FC.AWAY_TEAM_RANKING_SQRT])
        score_high = 0
        col_start_end = None
        for cols in col_start_end_list:
            x_train = np.array(self.df_train.loc[:, cols[0]:cols[1]])
            score = cross_val_score(self.forest_clf, x_train, self.__y_train, cv=2, scoring="accuracy")
            if score.mean() > score_high:
                score_high = score.mean()
                col_start_end = cols
        print('Best columns with score.mean = {:3.2f}: {}'.format(score_high, col_start_end))
        return col_start_end

    def make_prediction_for_the_next_matches(self, matches: int = 5, over_train = False, overwrite_completed = False):
        cols = self.__get_column_start_end_with_best_score__()
        self.__train_on_old_data__(cols)
        offset_number = 1 if (over_train or overwrite_completed) else self.world_cup_2018.first_open_match_number
        offset_index = offset_number - 1
        if over_train:
            print('Columns: {}'.format(self.df_train.columns))
            df_test = self.df_train.loc[offset_index:offset_index + matches, cols[0]:cols[1]]
        else:
            print('Columns: {}'.format(self.df_test.columns))
            df_test = self.df_test.loc[offset_index:offset_index + matches, cols[0]:cols[1]]
        predict_probability = self.forest_clf.predict_proba(np.array(df_test)).round(2)
        print(df_test.head(matches))
        for number in range(offset_number, offset_number + matches + 1):
            if over_train:
                match = self.world_cup_2014.match_list.get_match(number)
            else:
                match = self.world_cup_2018.match_list.get_match(number)
            match.simulate_by_probabilities(predict_probability[number - offset_number])
            match.print()

    def __train_on_old_data__(self, cols: list):
        x_train = np.array(self.df_train.loc[:, cols[0]:cols[1]])
        self.forest_clf.fit(x_train, self.__y_train)


model = WorldCupModel()
model.make_prediction_for_the_next_matches(5, False)


