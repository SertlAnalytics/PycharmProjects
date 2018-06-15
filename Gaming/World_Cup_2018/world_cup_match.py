"""
Description: This module contains the match classes for the FIFA world cup predictor
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""
from world_cup_constants import FC
from world_cup_team import WorldCupTeamList
from world_cup_api import WorldCupRankingAdjustmentApi


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