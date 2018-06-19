"""
Description: This module calculates predictions for the FIFA World Cup 2018 in Russia
Based on the data of FIFA World Cup 2014 in Brasil.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-13
"""

from world_cup_constants import FC
from word_cup import WorldCup4Test, WorldCup4Training
from world_cup_match import WorldCupMatch
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sertl_analytics.pyurl.url_process import MyUrlBrowser4WM2018Watson
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from random import randrange
import pandas as pd
import math


class Policy:
    def __init__(self, columns: str, cv: int, n_estimators: int, red_factor: float, enh_factor: float):
        self.columns = columns  # ['N', 'SQUARED', 'SQRT']
        self.cv = cv  # number of cross validations looking for the best features
        self.n_estimators = n_estimators  # number of estimators for Random Forest Classifier
        self.ranking_reduction_factor = red_factor
        self.ranking_enhancement_factor = enh_factor
        self.positive_match_list = []
        self.reward = 0

    def check_match_for_reward(self, match: WorldCupMatch):
        reward = match.get_reward_after_simulation()
        self.reward += reward
        if reward > 0:
            self.positive_match_list.append(match)

    @property
    def details(self):
        return 'Policy: CV = {} / Estimators = {} / red_factor = {}, enh_factor = {}:'.\
            format(self.cv, self.n_estimators, self.ranking_reduction_factor, self.ranking_enhancement_factor)

    def print(self, with_match=False):
        print(self.details + ' Reward = {}'.format(self.reward))
        if with_match:
            for match in self.positive_match_list:
                match.print()


class PolicyList:
    def __init__(self, number_start):
        self.number_start = number_start + 1
        self.columns = ['N', 'SQUARED', 'SQRT']
        self.cv_list = [randrange(2, 5) for k in range(1, self.number_start)]
        self.n_estimators_list = [randrange(2, 110) for k in range(1, self.number_start)]
        self.red_factor_list = [randrange(1, 20)/10 for k in range(1, self.number_start)]
        self.enh_factor_list = [randrange(1, 20)/10 for k in range(1, self.number_start)]
        self.cv_list = [3, 3, 4]
        self.n_estimators_list = [87, 39, 89]
        self.red_factor_list = [1.5, 1.6, 0.8]
        self.enh_factor_list = [0.5, 0.9, 0.1]
        self.policy_list = []
        self.__init_policy_list__()
        self.model = WorldCupModel()
        self.max_reward = 0
        self.max_policy = Policy

    def __init_policy_list__(self):
        for cv, n_estimators, red_factor, enh_factor in \
                zip(self.cv_list, self.n_estimators_list, self.red_factor_list, self.enh_factor_list):
            self.policy_list.append(Policy('column', cv, n_estimators, red_factor, enh_factor))

    def find_best_policy(self):
        for policy in self.policy_list:
            self.model.check_policy(policy)
            if policy.reward > self.max_reward:
                self.max_reward = policy.reward
                self.max_policy = policy
        self.max_policy.print(False)


class WorldCupModel:
    def __init__(self):
        self.world_cup_2014 = WorldCup4Training(2014, 'Brasil')
        self.world_cup_2018 = WorldCup4Test(2018, 'Russia', self.world_cup_2014.api_for_ranking_adjustments)
        self.red_factor = self.world_cup_2014.api_for_ranking_adjustments.ranking_reduction_factor
        self.end_factor = self.world_cup_2014.api_for_ranking_adjustments.ranking_enhancement_factor
        self.first_open_match_number = self.world_cup_2018.first_open_match_number
        self.df_train = pd.DataFrame
        self.__set_df_train__(self.first_open_match_number)
        self.df_test = pd.DataFrame
        self.__set_df_test__(self.first_open_match_number)
        self.forest_clf = RandomForestClassifier(n_estimators=88, random_state=42)
        self.match_train_list = []
        self.match_test_list = []
        self.__set_match_lists__(self.first_open_match_number, self.red_factor, self.end_factor)
        # self.__print_match_lists__()

    def get_x_train(self, cols: list) -> np.array:
        # df_train = self.df_train.loc[:, cols[0]:cols[1]]
        # return np.array(df_train)
        return np.array([self.__get_x_data_for_match__(match) for match in self.match_train_list])

    def get_x_test(self, elements: int) -> np.array:
        # df_train = self.df_train.loc[:, cols[0]:cols[1]]
        # return np.array(df_train)
        return np.array([self.__get_x_data_for_match__(self.match_test_list[k]) for k in range(0, elements)])

    def __get_x_data_for_match__(self, match: WorldCupMatch):
        r_1 = match.team_1_ranking_adjusted
        r_2 = match.team_2_ranking_adjusted
        # return [r_1, r_2, r_1**2, r_2**2]
        return [r_1, r_2]
        # return [math.sqrt(match.team_1_ranking_adjusted), math.sqrt(match.team_2_ranking_adjusted)]

    @property
    def y_train(self) -> np.array:
        return np.array([match.get_winner() for match in self.match_train_list])
        # return np.array(self.df_train.iloc[:, -1])

    def __print_match_lists__(self):
        for match in self.match_train_list:
            match.print()
        print('\n')
        for match in self.match_test_list:
            match.print()

    def __set_match_lists__(self, first_open_match_number: int, red_factor: float, enh_factor: float):
        self.__set_match_train_list__(first_open_match_number, red_factor, enh_factor)
        self.__set_match_test_list__(first_open_match_number)

    def __set_match_train_list__(self, first_open_match_number: int, red_factor: float, enh_factor: float):
        self.match_train_list = []
        self.world_cup_2014.team_list.reset_ranking_adjusted()
        for number in self.world_cup_2014.match_list.index_list:
            match = self.world_cup_2014.match_list.get_match(number)
            match.adjust_ranking(red_factor, enh_factor)
            self.match_train_list.append(match)

        self.world_cup_2018.team_list.reset_ranking_adjusted()
        for number in range(1, first_open_match_number):
            match = self.world_cup_2018.match_list.get_match(number)
            match.adjust_ranking(red_factor, enh_factor)
            self.match_train_list.append(match)

    def __set_match_test_list__(self,  first_open_match_number: int):
        self.match_test_list = []
        self.world_cup_2018.team_list.reset_ranking_adjusted()
        for number in range(first_open_match_number, self.world_cup_2018.match_list.length):
            match = self.world_cup_2018.match_list.get_match(number)
            self.match_test_list.append(match)

    def __set_df_train__(self, first_open_match_number: int):
        self.df_train = self.world_cup_2014.df_4_ml

        if first_open_match_number > 1:
            pos_right = first_open_match_number - 2
            self.df_train = self.df_train.append(self.world_cup_2018.df_4_ml.loc[:pos_right,:])

    def __set_df_test__(self, first_open_match_number: int):
        if first_open_match_number > 1:
            self.df_test = self.world_cup_2018.df_4_ml.loc[first_open_match_number-1:,:]
        else:
            self.df_test = self.world_cup_2018.df_4_ml

    def __get_column_start_end_with_best_score__(self, cv=2) -> list:
        col_start_end_list = [[FC.HOME_TEAM_RANKING, FC.AWAY_TEAM_RANKING]]
        col_start_end_list.append([FC.HOME_TEAM_RANKING_SQU, FC.AWAY_TEAM_RANKING_SQU])
        col_start_end_list.append([FC.HOME_TEAM_RANKING_SQRT, FC.AWAY_TEAM_RANKING_SQRT])
        col_start_end_list.append([FC.HOME_TEAM_RANKING, FC.AWAY_TEAM_RANKING_SQU])
        col_start_end_list.append([FC.HOME_TEAM_RANKING_SQU, FC.AWAY_TEAM_RANKING_SQRT])
        col_start_end_list.append([FC.HOME_TEAM_RANKING, FC.AWAY_TEAM_RANKING_SQRT])
        score_high = 0
        col_start_end = None
        for cols in col_start_end_list:
            score = cross_val_score(self.forest_clf, self.get_x_train(cols), self.y_train, cv=cv, scoring="accuracy")
            if score.mean() > score_high:
                score_high = score.mean()
                col_start_end = cols
        # print('Best columns with score.mean = {:3.2f}: {}'.format(score_high, col_start_end))
        return col_start_end

    def check_policy(self, policy: Policy):
        print('Checking policy: {}'.format(policy.details))
        for k in range(1, self.first_open_match_number):
            self.__set_df_train__(k)
            self.__set_df_test__(k)
            self.__set_match_lists__(k, policy.ranking_reduction_factor, policy.ranking_enhancement_factor)
            self.forest_clf = RandomForestClassifier(n_estimators=policy.n_estimators, random_state=42)
            cols = self.__get_column_start_end_with_best_score__(policy.cv)
            self.__train_on_old_and_new_data__(cols)
            offset_number = k
            offset_index = offset_number - 1
            df_test = self.df_test.loc[offset_index:offset_index + 1, cols[0]:cols[1]]
            x_data = self.get_x_test(1)
            predict_probability = self.forest_clf.predict_proba(x_data).round(2)
            match = self.world_cup_2018.match_list.get_match(k)
            match.simulate_by_probabilities(predict_probability[k - offset_number])
            policy.check_match_for_reward(match)
        print('...reward: {}'.format(policy.reward))
        policy.print(True)
            # match.print()
            # policy.print()

    def make_prediction_for_the_next_matches(self, matches: int = 5, write_to_page = False):
        match_list = []
        cols = self.__get_column_start_end_with_best_score__()
        self.__train_on_old_and_new_data__(cols, True)
        offset_number = self.first_open_match_number
        offset_index = offset_number - 1
        df_test = self.df_test.loc[offset_index:offset_index + matches, cols[0]:cols[1]]
        x_data = self.get_x_test(matches)
        predict_probability = self.forest_clf.predict_proba(x_data).round(2)
        print(df_test.head(matches))
        for number in range(offset_number, offset_number + matches):
            match = self.world_cup_2018.match_list.get_match(number)
            match.simulate_by_probabilities(predict_probability[number - offset_number])
            match.print()
            match_list.append(match)
        if len(match_list) > 0 and write_to_page:
            self.__write_to_web_page__(match_list)

    @staticmethod
    def __write_to_web_page__(match_list: list):
        result_list = [[match.number, match.goal_team_1_simulation, match.goal_team_2_simulation] for match in match_list]
        browser = MyUrlBrowser4WM2018Watson()
        browser.add_results(result_list)

    def __train_on_old_and_new_data__(self, cols: list, perform_test = False):
        x_train = self.get_x_train(cols)
        if perform_test:
            self.__perform_test_on_training_data__(x_train, self.y_train)
        self.forest_clf.fit(x_train, self.y_train)
        # self.__print_report__(x_train, self.__y_train)

    def __perform_test_on_training_data__(self, x_input, y_input):
        X_train, X_test, y_train, y_test = train_test_split(x_input, y_input, test_size=0.3)
        self.forest_clf.fit(X_train, y_train)
        self.__print_report__(X_test, y_test)

    def __print_report__(self, x_input, y_input):
        rfc_pred = self.forest_clf.predict(x_input)
        print(confusion_matrix(y_input, rfc_pred))
        print('\n')
        print(classification_report(y_input, rfc_pred))


model = WorldCupModel()
model.make_prediction_for_the_next_matches(6, False)

# policy_list = PolicyList(20)
# policy_list.find_best_policy()


