"""
Description: This module contains the match classes for the FIFA world cup predictor
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""
from world_cup_constants import FC
from world_cup_team import WorldCupTeamList, WorldCupTeam
import pandas as pd


class WorldCupMatch:
    def __init__(self, team_list: WorldCupTeamList, df_row):
        self.number = df_row[FC.MATCH_NUMBER]
        self.location = df_row[FC.LOCATION]
        self.date = df_row[FC.DATE] if FC.DATE in df_row else ''
        self.status = df_row[FC.STATUS]
        self.team_1 = team_list.get_team(df_row[FC.HOME_TEAM])
        self.team_2 = team_list.get_team(df_row[FC.AWAY_TEAM])
        self.team_1_ranking_adjusted = 0
        self.team_2_ranking_adjusted = 0
        self.goal_team_1 = df_row[FC.GOALS_HOME]
        self.goal_team_2 = df_row[FC.GOALS_AWAY]
        self.goal_team_1_penalty = 0 if df_row[FC.HOME_PENALTIES] is None else df_row[FC.HOME_PENALTIES]
        self.goal_team_2_penalty = 0 if df_row[FC.AWAY_PENALTIES] is None else df_row[FC.AWAY_PENALTIES]
        self.goal_team_1_simulation = 0
        self.goal_team_2_simulation = 0
        self.probability_list = []
        self.is_simulation = False
        self.winner = self.__get_winner__()

    @property
    def team_names(self):
        return self.team_1.name + ' - ' + self.team_2.name

    @property
    def points_team_1(self):
        if self.goal_team_1 > self.goal_team_2:
            return 3
        elif self.goal_team_1 < self.goal_team_2:
            return 0
        return 1

    @property
    def team_2_points(self):
        return 1 if self.points_team_1 == 1 else 3 - self.points_team_1

    @property
    def annotation(self):
        return '{:2}. {}: {:>2.0f}:{:>2.0f} ({:>2.0f}:{:>2.0f})'.format(
            self.number, self.team_names, self.team_1_ranking_adjusted, self.team_2_ranking_adjusted,
            self.team_1.ranking, self.team_2.ranking)

    @property
    def short(self):
        return '{:2}. {:<30} {:10} {}:{}  Simulation: {}:{} - Ranking_orig: {:>2.0f}:{:>2.0f}' \
               ' - Ranking_adjusted: {:>2.0f}:{:>2.0f} {} - {}'.format(
            self.number, self.team_names, self.status, self.goal_team_1, self.goal_team_2,
            self.goal_team_1_simulation, self.goal_team_2_simulation,
            self.team_1.ranking, self.team_2.ranking,
            self.team_1_ranking_adjusted, self.team_2_ranking_adjusted,
            ' - SIMULATION' if self.is_simulation else ' - NO simulation', self.probability_list)

    def get_points_and_goals_for_team(self, team: WorldCupTeam) -> list:
        if self.team_1.name != team.name and self.team_2.name != team.name:
            return [0, 0, 0]
        if self.team_1.name == team.name:
            return [self.points_team_1, self.goal_team_1, self.goal_team_2]
        return [self.team_2_points, self.goal_team_2, self.goal_team_1]

    def print(self):
        print(self.short)

    @property
    def ranking_adjusted_difference(self):
        return abs(self.team_1.ranking_adjusted - self.team_2.ranking_adjusted)

    def __get_winner__(self):
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

    def get_reward_after_simulation(self):
        if self.goal_team_1 == self.goal_team_1_simulation and self.goal_team_2 == self.goal_team_2_simulation:
            return 2
        if self.goal_team_1 == self.goal_team_2 and self.goal_team_1_simulation == self.goal_team_2_simulation:
            return 1
        if self.goal_team_1 < self.goal_team_2 and self.goal_team_1_simulation < self.goal_team_2_simulation:
            return 1
        if self.goal_team_1 > self.goal_team_2 and self.goal_team_1_simulation > self.goal_team_2_simulation:
            return 1
        return 0

    def simulate_by_probabilities(self, probability_array, knn_matches: list):
        self.probability_list = list(probability_array)
        max_val = max(self.probability_list)
        max_idx = self.probability_list.index(max_val)
        max_idx = self.__get_corrected_max_idx__(max_idx, max_val)
        self.is_simulation = True
        simulation_goals = self.__get_goals_for_simulation_by_knn_matches__(max_idx, knn_matches)
        if len(simulation_goals) == 0:
            simulation_goals = self.__get_goals_for_simulation_by_assumption__(max_idx, max_val)
        self.goal_team_1_simulation = simulation_goals[0]
        self.goal_team_2_simulation = simulation_goals[1]
        # sometimes we get the wrong values => correct them here
        if max_idx == 1 and self.goal_team_1_simulation == self.goal_team_2_simulation:
            self.goal_team_1_simulation += 1
        elif max_idx == 1 and self.goal_team_1_simulation == self.goal_team_2_simulation:
            self.goal_team_2_simulation += 1

    @staticmethod
    def __get_goals_for_simulation_by_knn_matches__(max_idx: int, knn_matches: list) -> list:
        check_list = [0, 0, 0]
        for match in knn_matches:
            if match.winner == max_idx:
                check_list[0] += 1
                check_list[1] += match.goal_team_1
                check_list[2] += match.goal_team_2
        return [] if check_list[0] == 0 else [int(check_list[1]/check_list[0]), int(check_list[2]/check_list[0])]

    def __get_goals_for_simulation_by_assumption__(self, max_idx: int, max_val: float) -> list:
        factor = 3
        if max_idx == 0:
            return [int(round(factor * max_val)), int(round(factor * max_val))]
        elif max_idx == 1:
            return [int(round(factor * max_val)), int(round(factor * self.probability_list[2]))]
        elif max_idx == 2:
            return [int(round(factor * self.probability_list[1])), int(round(factor * max_val))]
        return []

    def __get_corrected_max_idx__(self, max_idx: int, max_val: float):
        if max_val > 0.5:
            return max_idx
        for idx, val in enumerate(self.probability_list):
            if val == max_val and idx != max_idx:
                return 1 if self.team_1.ranking_adjusted < self.team_2.ranking_adjusted else max_idx
        return max_idx

    def adjust_ranking(self, red_factor: float, enh_factor: float):
        self.__adjust_ranking__(red_factor, enh_factor)

    def __adjust_ranking__(self, red_factor: float, enh_factor: float, winner_simulation=None):
        self.team_1_ranking_adjusted = self.team_1.ranking_adjusted
        self.team_2_ranking_adjusted = self.team_2.ranking_adjusted
        winner = self.winner if winner_simulation is None else winner_simulation
        r_red = self.ranking_adjusted_difference * red_factor
        r_enh = self.ranking_adjusted_difference * enh_factor
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

        if self.team_1.ranking_adjusted < 1:
            self.team_1.ranking_adjusted = 1
        if self.team_2.ranking_adjusted < 1:
            self.team_2.ranking_adjusted = 1


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


class WorldCupMatchPrediction:
    def __init__(self, match: WorldCupMatch):
        self.number = match.number
        self.team_1_name = match.team_1.name
        self.team_2_name = match.team_2.name
        self.goal_team_1_simulation = match.goal_team_1_simulation
        self.goal_team_2_simulation = match.goal_team_2_simulation
        self.number_prediction = 1

    def iterate(self, i: int = 1):
        self.number_prediction += i

    @property
    def key(self):
        return 'Match {:2}: {} - {}: {}:{}'.format(self.number, self.team_1_name, self.team_2_name,
                                                  self.goal_team_1_simulation, self.goal_team_2_simulation)

    def print(self):
        print('{} -> {}'.format(self.key, self.number_prediction))


class WorldCupMatchPredictionList:
    def __init__(self):
        self.__match_number_list = []
        self.__match_prediction_dic = {}

    def add_match_prediction(self, match_prediction: WorldCupMatchPrediction):
        key = match_prediction.key
        if match_prediction.number not in self.__match_number_list:
            self.__match_number_list.append(match_prediction.number)

        if key in self.__match_prediction_dic:
            self.__match_prediction_dic[key].iterate()
        else:
            self.__match_prediction_dic[key] = match_prediction

    def get_best_match_prediction_list(self) -> list:
        df_data = self.__get_data_as_dataframe__()
        return_list = []
        for number in self.__match_number_list:
            df_number = df_data[df_data['Number'] == number]
            return_list.append(self.__match_prediction_dic[df_number.iloc[0].key])
        return return_list

    def __get_data_as_dataframe__(self):
        value_list = []
        for key, m_p in self.__match_prediction_dic.items():
            value_list.append([m_p.number, m_p.key, m_p.team_1_name, m_p.team_2_name,
                               m_p.goal_team_1_simulation, m_p.goal_team_2_simulation, m_p.number_prediction])
        df = pd.DataFrame(value_list, columns=['Number', 'key', 'Team_1', 'Team_2', 'Goal_1', 'Goal_2', 'Total'])
        df.sort_values(['Number', 'Total'], inplace=True, ascending=[True, False])
        print(df[['Number', 'key', 'Total']].head(len(self.__match_prediction_dic)))
        return df


class TeamPosition:
    def __init__(self, team: WorldCupTeam):
        self.team = team
        self.last_match = None
        self.points_own = 0
        self.points_foreign = 0
        self.goals_own = 0
        self.goals_foreign = 0


class WorldCupTable:
    def __init__(self, team_list: WorldCupTeamList, match_list: WorldCupMatchList):
        self.__team_list = team_list
        self.__match_list = match_list
        self.__df_columns = ['Team', 'P_0', 'G_O_0', 'G_F_0']
        self.__init_df_columns__()
        self.__df_table = None
        self.__init_df_table__()
        self.__team_ranking_before_match_dic = {}
        self.__init_team_ranking_dic__()
        self.__print_team_ranking_dic__()

    @property
    def df_table(self):
        return self.__df_table

    def __init_df_table__(self):
        table_list = []
        for name in self.__team_list.index_list:
            table_list.append(self.__get_table_row_for_team__(self.__team_list.get_team(name)))
        self.__df_table = pd.DataFrame(table_list, columns=self.__df_columns)
        self.__df_table.sort_values(['Team'], inplace=True, ascending=True)

    def __init_df_columns__(self):
        for number in self.__match_list.index_list:
            column_list = self.__get_column_names_for_match_number(number)
            for col in column_list:
                self.__df_columns.append(col)

    def __get_table_row_for_team__(self, team: WorldCupTeam):
        value_list = [team.name, self.__team_list.length - team.ranking_in_list + 1, 0, 0]
        points = value_list[1]
        goals_own = value_list[2]
        goals_foreign = value_list[3]
        for number in self.__match_list.index_list:
            match = self.__match_list.get_match(number)
            p, own, foreign = match.get_points_and_goals_for_team(team)
            points += p
            goals_own += own
            goals_foreign += foreign
            value_list.append(points)
            value_list.append(goals_own)
            value_list.append(goals_foreign)
        return value_list

    @staticmethod
    def __get_column_names_for_match_number(number: int):
        return ['P_{}'.format(number), 'G_O_{}'.format(number), 'G_F_{}'.format(number)]

    def __init_team_ranking_dic__(self):
        for index in self.__team_list.index_list:
            team = self.__team_list.get_team(index)
            self.__team_ranking_before_match_dic[team.name] = [team.ranking_in_list]

        for number in self.__match_list.index_list:
            column = 'P_{}'.format(number-1)
            self.df_table.sort_values(column, inplace=True, ascending=False)
            position = 0
            for index, row in self.df_table.iterrows():
                team_name = row['Team']
                position += 1
                self.__team_ranking_before_match_dic[team_name].append(position)

    def __print_team_ranking_dic__(self):
        df = pd.DataFrame.from_dict(self.__team_ranking_before_match_dic, orient='index')
        print(df.head())

    def get_ranking_before_match(self, match: WorldCupMatch):
        ranking_team_1_before_match = self.__get_ranking_for_team_before_match(match.team_1.name, match)
        ranking_team_2_before_match = self.__get_ranking_for_team_before_match(match.team_2.name, match)
        return ranking_team_1_before_match, ranking_team_2_before_match

    def __get_ranking_for_team_before_match(self, team_name: str, match: WorldCupMatch):
        return self.__team_ranking_before_match_dic[team_name][match.number-1]
        # column_list = ['Team'] + self.__get_column_names_for_match_number(match.number-1)
        # self.df_table.sort_values(column_list[1], inplace=True, ascending=False)
        # self.df_table.reset_index(inplace=True, drop=True)
        # team_row = self.df_table[self.df_table['Team'] == team_name]
        # return team_row['P_0'].idxmax() + 1
