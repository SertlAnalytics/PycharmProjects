"""
Description: This module calculates predictions for the FIFA World Cup 2018 in Russia
Based on the data of FIFA World Cup 2014 in Brasil.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-13
"""

from world_cup_constants import FC
from world_cup_configuration import config
from world_cup_api import WorldCupRankingAdjustmentApi
from world_cup_team import WorldCupTeam, WorldCupTeamList
from world_cup_match import WorldCupMatch, WorldCupMatchList
from word_cup import WorldCup, WorldCup4Test, WorldCup4Training
import matplotlib.pyplot as plt
from sertl_analytics.datafetcher.file_fetcher import FileFetcher
import pandas as pd
import numpy as np
import math
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
import xlsxwriter


class WorldCupModel:
    def __init__(self):
        self.world_cup_2014 = WorldCup4Training(2014, 'Brasil')
        self.world_cup_2018 = WorldCup4Test(2018, 'Russia', self.world_cup_2014.api_for_ranking_adjustments)
        self.df_train = self.world_cup_2014.df_4_ml
        self.df_test = self.world_cup_2018.df_4_ml
        self.__y_train = np.array(self.df_train.iloc[:, -1])
        self.__y_test = np.array(self.df_test.iloc[:, -1])
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
        self.__train_on_old_and_new_data__(cols)
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
        for number in range(offset_number, offset_number + matches):
            if over_train:
                match = self.world_cup_2014.match_list.get_match(number)
            else:
                match = self.world_cup_2018.match_list.get_match(number)
            match.simulate_by_probabilities(predict_probability[number - offset_number])
            match.print()

    def __train_on_old_and_new_data__(self, cols: list):
        df_train = self.df_train.loc[:, cols[0]:cols[1]]
        if self.world_cup_2018.first_open_match_number > 1:
            pos_right = self.world_cup_2018.first_open_match_number-2
            df_test = self.df_test.loc[:pos_right, cols[0]:cols[1]]
            df_train = df_train.append(df_test)
            for k in range(0, pos_right + 1):
                self.__y_train = np.append(self.__y_train, self.__y_test[k])
        x_train = np.array(df_train)
        self.forest_clf.fit(x_train, self.__y_train)


model = WorldCupModel()
model.make_prediction_for_the_next_matches(5, False)


