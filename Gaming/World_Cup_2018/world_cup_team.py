"""
Description: This module contains the team classes for the FIFA world cup predictor
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""


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