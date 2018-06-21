"""
Description: This module contains the main class WorldCup for the FIFA World cup predictor.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-13
"""

from world_cup_constants import FC
from world_cup_configuration import config
from world_cup_api import WorldCupRankingAdjustmentApi
from world_cup_team import WorldCupTeam, WorldCupTeamList
from world_cup_match import WorldCupMatch, WorldCupMatchList
from world_cup_excel import WorldCupExcel
import matplotlib.pyplot as plt
from sertl_analytics.datafetcher.file_fetcher import FileFetcher
import pandas as pd


class WorldCup:
    def __init__(self, year: int, host: str):
        self.year = year
        self.host = host
        self._file_name_with_data = self.__get_file_name_for_data__()
        self._sheet_name_matches = self.__get_sheet_name_with_matches__()
        self._sheet_name_ranking = self.__get_sheet_name_with_ranking__()
        # self.__update_data_in_source__()
        self.df_match = self.__get_df_match__()
        self.df_ranking = self.__get_df_ranking__()
        self.team_list = WorldCupTeamList()
        self.__fill_team_list__()
        self.match_list = WorldCupMatchList()
        self.__fill_match_list__()
        self.__print_statistics__()

    def init_by_red_enh_factor(self, red_factor: float, enh_factor: float):
        self.team_list.reset_ranking_adjusted()
        self.__adjust_ranking__(red_factor, enh_factor)
        # print('MatchList after red_factor/enh_factor = {}/{}'.format(red_factor, enh_factor))
        # self.match_list.print_list()
        # self.plot_data()

    @property
    def first_open_match_number(self):
        for number in self.match_list.index_list:
            match = self.match_list.get_match(number)
            if match.status == 'open':
                return number
        return 0

    def plot_data(self):
        xs = [self.match_list.get_match(index).team_1_ranking_adjusted for index in self.match_list.index_list]
        ys = [self.match_list.get_match(index).team_2_ranking_adjusted for index in self.match_list.index_list]
        labels = [self.match_list.get_match(index).winner for index in self.match_list.index_list]
        plt.scatter(xs, ys, c=labels)
        plt.show()

    def __get_file_name_for_data__(self):
        pass

    def __get_sheet_name_with_matches__(self):
        pass

    def __get_sheet_name_with_ranking__(self):
        pass

    def __print_statistics__(self):
        print('WorldCup statistics for {} ({}): Number Teams = {}, Number Matches with teams = {}'.format(
            self.year, self.host, self.team_list.length, self.match_list.length))

    def __adjust_ranking__(self, red_factor: float, enh_factor: float):
        for number in self.match_list.index_list:
            match = self.match_list.get_match(number)
            match.adjust_ranking(red_factor, enh_factor)

    def __update_data_in_source__(self):
        pass

    def __get_df_match__(self) -> pd.DataFrame:
        return FileFetcher(self._file_name_with_data, sheet_name=self._sheet_name_matches).df

    def __get_df_ranking__(self) -> pd.DataFrame:
        return FileFetcher(self._file_name_with_data, sheet_name=self._sheet_name_ranking).df

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


class WorldCup4Training(WorldCup):
    def __get_file_name_for_data__(self):
        return config.get_excel_2014_file_name()

    def __get_sheet_name_with_matches__(self):
        return config.excel_2014_tabs[0]

    def __get_sheet_name_with_ranking__(self):
        return config.excel_2014_tabs[1]


class WorldCup4Test(WorldCup):
    def __get_file_name_for_data__(self):
        return config.get_excel_2018_file_name()

    def __get_sheet_name_with_matches__(self):
        return config.excel_2018_tabs[0]

    def __get_sheet_name_with_ranking__(self):
        return config.excel_2018_tabs[1]

    def __update_data_in_source__(self):
        excel = WorldCupExcel(self._file_name_with_data, self._sheet_name_matches)
        excel.update_match(2, 4, 1, 9, 7)
