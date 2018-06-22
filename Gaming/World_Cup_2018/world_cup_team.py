"""
Description: This module contains the team classes for the FIFA world cup predictor
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""

import pandas as pd

class WorldCupTeam:
    def __init__(self, name: str, ranking: int, points: int = 0):
        self.name = name
        self.ranking = ranking
        self.points = points
        self.ranking_adjusted = self.ranking
        self.ranking_in_list = 0

    def print(self):
        print('Team: {:20} {:>3} {:2.0f} -> {:2.0f}. Ranking in list: {:2}'.format(
            self.name, 'Ranking:', self.ranking, self.ranking_adjusted, self.ranking_in_list))


class WorldCupTeamList:
    def __init__(self):
        self.__index_list = []
        self.__team_dic = {}

    @property
    def length(self):
        return len(self.__team_dic)

    @property
    def index_list(self):
        return self.__index_list

    def add_team(self, team: WorldCupTeam):
        self.__index_list.append(team.name)
        self.__team_dic[team.name] = team
        self.__adjust_ranking_in_list__()

    def __adjust_ranking_in_list__(self):
        data_list = [[team.name, team.ranking] for team in self.__team_dic.values()]
        df_team = pd.DataFrame(data_list, columns=['Team', 'Ranking'])
        df_team.sort_values('Ranking', inplace=True)
        df_team.reset_index(inplace=True, drop=True)
        for index, row in df_team.iterrows():
            team = self.get_team(row['Team'])
            team.ranking_in_list = index + 1

    def get_team(self, name: str) -> WorldCupTeam:
        return self.__team_dic[name]

    def reset_ranking_adjusted(self):
        for key in self.__team_dic:
            self.__team_dic[key].ranking_adjusted = self.__team_dic[key].ranking

    def print_list(self):
        for key in self.__team_dic:
            self.__team_dic[key].print()

