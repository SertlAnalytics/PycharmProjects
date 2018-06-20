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


class ColumnHandler:
    @staticmethod
    def get_columns_for_number(col: int):
        col_list = []
        if col >= 4:
            col_list.append('N')
            col = divmod(col, 4)[1]
        if col >= 2:
            col_list.append('SQUARED')
            col = divmod(col, 2)[1]
        if col == 1:
            col_list.append('SQRT')
        return col_list

    @staticmethod
    def get_column_data_for_source_values(r_1: float, r_2: float, col_id: int):
        col_list = ColumnHandler.get_columns_for_number(col_id)
        data_list = []
        if 'N' in col_list:
            data_list.append(r_1)
            data_list.append(r_2)
        if 'SQUARED' in col_list:
            data_list.append(r_1 ** 2)
            data_list.append(r_2 ** 2)
        if 'SQRT' in col_list:
            data_list.append(math.sqrt(r_1))
            data_list.append(math.sqrt(r_2))
        return data_list


class RG:  # random generator
    @staticmethod
    def rand_property_index():
        return randrange(0, 4)

    @staticmethod
    def rand_col():
        return randrange(1, 8)

    @staticmethod
    def rand_n_estimators():
        return randrange(2, 110)

    @staticmethod
    def rand_red_factor():
        return round(randrange(1, 20)/10,1)

    @staticmethod
    def rand_end_factor():
        return round(randrange(1, 20)/10,1)

    @staticmethod
    def get_rand_values_for_policy():
        return [RG.rand_col(), RG.rand_n_estimators(), RG.rand_red_factor(), RG.rand_end_factor()]


class Policy:
    def __init__(self, col_id: int, n_estimators: int, red_factor: float, enh_factor: float):
        self.col_id = col_id
        self.n_estimators = n_estimators  # number of estimators for Random Forest Classifier
        self.red_factor = red_factor
        self.enh_factor = enh_factor
        self.positive_match_list = []
        self.reward = 0

    def reset(self):
        self.positive_match_list = []
        self.reward = 0

    def check_match_for_reward(self, match: WorldCupMatch):
        reward = match.get_reward_after_simulation()
        self.reward += reward
        if reward > 0:
            self.positive_match_list.append(match)

    @property
    def details(self):
        return 'Policy: Columns = {} ({}), Estimators = {} / red_factor = {}, enh_factor = {}:'.\
            format(self.col_id, ColumnHandler.get_columns_for_number(self.col_id),
                   self.n_estimators, self.red_factor, self.enh_factor)

    @property
    def details_with_reward(self):
        return self.details + ' Reward = {}'.format(self.reward)

    def print(self, with_match=False):
        print(self.details_with_reward)
        if with_match:
            for match in self.positive_match_list:
                match.print()

    def get_offsprings(self, number_offsprings: int):
        offsprings = []
        old_values = [self.col_id, self.n_estimators, self.red_factor, self.enh_factor]
        for k in range(0, number_offsprings):
            property_number = RG.rand_property_index()
            rand_values = RG.get_rand_values_for_policy()
            while old_values[property_number] == rand_values[property_number]:
                rand_values = RG.get_rand_values_for_policy()
            merged = [rand_values[k] if k == property_number else old_values[k] for k in range(len(old_values))]
            offsprings.append(Policy(merged[0], merged[1], merged[2], merged[3]))
        return offsprings


class PolicyList:
    def __init__(self, world_cup_model, number_start):
        self.model = world_cup_model
        self.number_start = number_start + 1
        self.col_list = [RG.rand_col() for k in range(1, self.number_start)]  # ['N', 'SQUARED', 'SQRT']
        self.n_estimators_list = [RG.rand_n_estimators() for k in range(1, self.number_start)]
        self.red_factor_list = [RG.rand_red_factor() for k in range(1, self.number_start)]
        self.enh_factor_list = [RG.rand_end_factor() for k in range(1, self.number_start)]
        # self.cv_list = [3, 3, 4]
        # self.n_estimators_list = [87, 39, 89]
        # self.red_factor_list = [1.5, 1.6, 0.8]
        # self.enh_factor_list = [0.5, 0.9, 0.1]
        self.policy_list = []
        self.best_policy_list = []
        self.__init_policy_list__()
        self.max_reward = 0
        self.max_policy = None

    @property
    def best_policy(self) -> Policy:
        return self.max_policy

    def __init_policy_list__(self):
        for col, n_estimators, red_factor, enh_factor in \
                zip(self.col_list, self.n_estimators_list, self.red_factor_list, self.enh_factor_list):
            self.policy_list.append(Policy(col, n_estimators, red_factor, enh_factor))

    def find_best_policy(self):
        for index, policy in enumerate(self.policy_list):
            self.model.check_policy(index+1, policy)
            if policy.reward > self.max_reward:
                self.max_reward = policy.reward
                self.max_policy = policy
        self.max_policy.print(False)

    def find_best_policy_with_genetic_algorithm(self, number_loops: int, remaining_percent: int, offsprings: int):
        for k in range(0, number_loops):
            for index, policy in enumerate(self.policy_list):
                self.model.check_policy(index + 1, policy)
                if policy.reward > self.max_reward:
                    self.max_reward = policy.reward
                    self.max_policy = policy
            self.best_policy_list = self.__get_best_policies__(remaining_percent)
            self.__print_best_policy_list__('Best policies after {}/{} loop:'.format(k + 1, number_loops))
            if k < number_loops -1:
                self.__reset_best_policies__()
                self.__prepare_policy_list_for_next_run__(offsprings)

    def __prepare_policy_list_for_next_run__(self, offspring_number: int):
        self.policy_list = []
        for policy in self.best_policy_list:
            self.policy_list.append(policy)
            self.policy_list = self.policy_list + policy.get_offsprings(offspring_number)

    def __get_best_policies__(self, remaining_percent: int):
        data_list = [[index, policy.reward] for index, policy in enumerate(self.policy_list)]
        df_temp = pd.DataFrame(data_list, columns=['Index', 'Reward']).sort_values(by='Reward', ascending=False)
        print(df_temp['Reward'].value_counts(sort=False))
        remaining_numbers = int(round(len(self.policy_list) * remaining_percent / 100, 0))
        policy_list_temp = []
        counter = 0
        for index, rows in df_temp.iterrows():
            counter += 1
            policy_list_temp.append(self.policy_list[index])
            if counter >= remaining_numbers:
                break
        return policy_list_temp

    def __reset_best_policies__(self):
        for policy in self.best_policy_list:
            policy.reset()

    def __print_best_policy_list__(self, message =''):
        print('')
        if message != '':
            print(message)
        for policy in self.best_policy_list:
            policy.print()
        print('')


class WorldCupModel:
    def __init__(self):
        self.policy = Policy
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

    def get_x_train(self, col_id: int) -> np.array:
        return np.array([self.__get_x_data_for_match__(match, col_id) for match in self.match_train_list])

    def get_x_test(self, elements: int, col_id: int) -> np.array:
        return np.array([self.__get_x_data_for_match__(self.match_test_list[k], col_id) for k in range(0, elements)])

    @staticmethod
    def __get_x_data_for_match__(match: WorldCupMatch, col_id: int):
        r_1 = match.team_1_ranking_adjusted
        r_2 = match.team_2_ranking_adjusted
        return ColumnHandler.get_column_data_for_source_values(r_1, r_2, col_id)

    @property
    def y_train(self) -> np.array:
        return np.array([match.get_winner() for match in self.match_train_list])

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

    def check_policy(self, policy_number: int, policy: Policy):
        for k in range(1, self.first_open_match_number):
            self.__set_df_train__(k)
            self.__set_df_test__(k)
            self.__set_match_lists__(k, policy.red_factor, policy.enh_factor)
            self.forest_clf = RandomForestClassifier(n_estimators=policy.n_estimators, random_state=42)
            self.__train_on_old_and_new_data__(policy.col_id)
            x_data = self.get_x_test(1, policy.col_id)
            predict_probability = self.forest_clf.predict_proba(x_data).round(2)
            match = self.world_cup_2018.match_list.get_match(k)
            match.simulate_by_probabilities(predict_probability[0])
            policy.check_match_for_reward(match)
        print('Checked policy {:3}: {}'.format(policy_number, policy.details_with_reward))

    def make_prediction_for_the_next_matches(self, policy: Policy, matches: int = 5, write_to_page = False):
        print('\nPrediction of the next {} matches using {}...'.format(matches, policy.details_with_reward))
        self.policy = policy
        match_list = []
        self.__train_on_old_and_new_data__(self.policy.col_id, True)
        offset_number = self.first_open_match_number
        x_data = self.get_x_test(matches, self.policy.col_id)
        predict_probability = self.forest_clf.predict_proba(x_data).round(2)
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

    def __train_on_old_and_new_data__(self, col_id: int, perform_test = False):
        x_train = self.get_x_train(col_id)
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

with_policy_list = True
over_best_policy_list = True

if with_policy_list:
    policy_list = PolicyList(model, 100)
    policy_list.find_best_policy_with_genetic_algorithm(5, 20, 4)
    if over_best_policy_list:
        for policy in policy_list.best_policy_list:
            model.make_prediction_for_the_next_matches(policy, 6, False)
    else:
        model.make_prediction_for_the_next_matches(policy_list.best_policy, 6, False)
else:
    best_policy = Policy(7, 35, 0.9, 0.6)
    model.make_prediction_for_the_next_matches(best_policy, 6, True)




