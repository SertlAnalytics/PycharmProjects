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
import numpy as np
import math


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
        self.match_list = WorldCupMatchList()
        self.__init_lists__()
        self._api_for_ranking_adjustments = self.__get_ranking_adjustment_parameters__()
        self._api_for_ranking_adjustments.print()
        self.__add_team_ranking_to_df_match__()
        self.df_4_ml = None
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

    def __get_file_name_for_data__(self):
        pass

    def __get_sheet_name_with_matches__(self):
        pass

    def __get_sheet_name_with_ranking__(self):
        pass

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
        self.df_4_ml = self.df_match.loc[:, FC.HOME_TEAM_RANKING:FC.WINNER]

    def __update_data_in_source__(self):
        pass

    def __get_df_match__(self) -> pd.DataFrame:
        return FileFetcher(self._file_name_with_data, sheet_name=self._sheet_name_matches).df

    def __get_df_ranking__(self) -> pd.DataFrame:
        return FileFetcher(self._file_name_with_data, sheet_name=self._sheet_name_ranking).df

    def __init_lists__(self):
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

    def __get_file_name_for_data__(self):
        return config.get_excel_2014_file_name()

    def __get_sheet_name_with_matches__(self):
        return config.excel_2014_tabs[0]

    def __get_sheet_name_with_ranking__(self):
        return config.excel_2014_tabs[1]


class WorldCup4Test(WorldCup):
    def __init__(self, year: int, host: str, api: WorldCupRankingAdjustmentApi):
        self._api_for_ranking_adjustments = api
        WorldCup.__init__(self, year, host)

    def __get_file_name_for_data__(self):
        return config.get_excel_2018_file_name()

    def __get_sheet_name_with_matches__(self):
        return config.excel_2018_tabs[0]

    def __get_sheet_name_with_ranking__(self):
        return config.excel_2018_tabs[1]

    def __get_ranking_adjustment_parameters__(self) -> WorldCupRankingAdjustmentApi:
        return self._api_for_ranking_adjustments

    def __update_data_in_source__(self):
        excel = WorldCupExcel(self._file_name_with_data, self._sheet_name_matches)
        excel.update_match(2, 4, 1, 9, 7)
