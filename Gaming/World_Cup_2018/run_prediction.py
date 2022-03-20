"""
Description: This module calculates predictions for the FIFA World Cup 2018 in Russia
Based on the data of FIFA World Cup 2014 in Brasil.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-13
"""

from world_cup_constants import FC, PP
from word_cup import WorldCup4Test, WorldCup4Training2014, WorldCup4Training2014ff
from world_cup_match import WorldCupMatch, WorldCupMatchPrediction, WorldCupMatchPredictionList
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import linear_model
from scipy.optimize import basinhopping
from sklearn.linear_model import LogisticRegression
from sertl_analytics.pyurl.url_process import MyUrlBrowser4EM2021Odyssee
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from random import randrange
import pandas as pd
import math
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from world_cup_configuration import config


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
        return round(randrange(1, 10)/10,1)

    @staticmethod
    def rand_end_factor():
        return round(randrange(1, 10)/10,1)

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
        # self.col_list = [4]
        # self.cv_list = [4]
        # self.n_estimators_list = [87]
        # self.red_factor_list = [0.5]
        # self.enh_factor_list = [0.5]
        self.policy_list = []
        self.best_policy_list = []
        self.__init_policy_list__()
        self.max_reward = 0
        self.max_policy = None
        self.policy_summary_list = []

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
                self.__add_to_policy_summary_list__(policy)
                if policy.reward > self.max_reward:
                    self.max_reward = policy.reward
                    self.max_policy = policy
            self.best_policy_list = self.__get_best_policies__(remaining_percent)
            self.__print_best_policy_list__('Best policies after {}/{} loop:'.format(k + 1, number_loops))
            if k < number_loops -1:
                self.__reset_best_policies__()
                self.__prepare_policy_list_for_next_run__(offsprings)

    def __add_to_policy_summary_list__(self, p: Policy):
        self.policy_summary_list.append([p.col_id, p.n_estimators, p.red_factor, p.enh_factor, p.reward])

    def __prepare_policy_list_for_next_run__(self, offspring_number: int):
        self.policy_list = []
        for best_policy_entity in self.best_policy_list:
            self.policy_list.append(best_policy_entity)
            self.policy_list = self.policy_list + best_policy_entity.get_offsprings(offspring_number)

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

    def print_best_estimated_policy(self, best_policy: Policy):
        reg = linear_model.LinearRegression()
        df_policy_summary = pd.DataFrame(self.policy_summary_list, columns=PP.get_pp_as_list())
        df_data = df_policy_summary[PP.get_pp_as_list()[0:4]]
        df_label = df_policy_summary[[PP.REWARD]]
        reg.fit(df_data, df_label)
        args = (reg.intercept_[0], reg.coef_[0][0], reg.coef_[0][1], reg.coef_[0][2], reg.coef_[0][3])
        x_min = np.array([1, 1, 0.1, 0.1])
        x_max = np.array([7, 110, 1, 1])
        bounds =  [(low, high) for low, high in zip(x_min, x_max)]
        minimizer_kwargs = {"args": args, "method": "L-BFGS-B", "bounds": bounds}
        x0 = np.array([best_policy.col_id, best_policy.n_estimators, best_policy.enh_factor, best_policy.red_factor])
        result = basinhopping(self.policy_function, x0, minimizer_kwargs=minimizer_kwargs, niter=200)
        print('Optimizer: maximum = {:4.2f} for x={}'.format(-result.fun, [round(i, 1) for i in result.x]))

    @staticmethod
    def policy_function(x: tuple, *args):
        return -(args[0] + args[1] * x[0] + args[2] * x[1] + args[3] * x[2] + args[4] * x[3])


class WorldCupModel:
    def __init__(self):
        # self.world_cup_training = WorldCup4Training2014(2014, 'Brasil')
        self.world_cup_training = WorldCup4Training2014ff(2014, 'Brasil')
        self.world_cup_test = WorldCup4Test(2021, 'EURO')
        self.first_open_match_number = self.world_cup_test.first_open_match_number
        self.df_train = pd.DataFrame
        self.df_test = pd.DataFrame
        self.forest_clf = None
        self.log_reg = None
        self.knn_clf = None
        self.match_train_list = []
        self.match_test_list = []
        self.__match_prediction_list = WorldCupMatchPredictionList()

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
        return np.array([match.winner for match in self.match_train_list])

    def __print_match_lists__(self):
        for match in self.match_train_list:
            match.print()
        print('\n')
        for match in self.match_test_list:
            match.print()

    def __fill_match_lists__(self, off_set: int):
        self.match_train_list = []
        self.match_test_list = []
        self.__fill_match_train_list__(off_set)
        self.__fill_match_test_list__(off_set)

    def __fill_match_train_list__(self, off_set: int):
        for number in self.world_cup_training.match_list.index_list:
            self.match_train_list.append(self.world_cup_training.match_list.get_match(number))
        for number in range(1, off_set):
            self.match_train_list.append(self.world_cup_test.match_list.get_match(number))

    def __fill_match_test_list__(self, off_set: int):
        for number in range(off_set, self.world_cup_test.match_list.length + 1):
            self.match_test_list.append(self.world_cup_test.match_list.get_match(number))

    def __init_world_cups_by_red_enh_factor__(self, red_factor: float, enh_factor: float):
        self.world_cup_training.init_by_red_enh_factor(red_factor, enh_factor)
        self.world_cup_test.init_by_red_enh_factor(red_factor, enh_factor)

    def check_policy(self, policy_number: int, policy: Policy):
        self.__init_models__(policy)
        self.__init_world_cups_by_red_enh_factor__(policy.red_factor, policy.enh_factor)
        for k in range(1, self.first_open_match_number):
            self.__fill_match_lists__(k)
            self.__train_models__(policy.col_id)
            x_data = self.get_x_test(1, policy.col_id)
            predict_probability = self.__get_predict_probability__(x_data)
            knn_neighbours = list(self.knn_clf.kneighbors(x_data, return_distance=False))
            match = self.world_cup_test.match_list.get_match(k)
            neighbours_match_list = self.get_knn_neighbour_match_list(knn_neighbours[0])
            match.simulate_by_probabilities(predict_probability[0], neighbours_match_list)
            policy.check_match_for_reward(match)
        print('Checked policy {:3}: {}'.format(policy_number, policy.details_with_reward))

    def __get_predict_probability__(self, x_data):
        # predict_probability = self.forest_clf.predict_proba(x_data).round(2)
        # predict_probability = self.log_reg.predict_proba(x_data).round(2)
        predict_probability = self.knn_clf.predict_proba(x_data).round(2)
        return predict_probability

    def __init_models__(self, policy: Policy):
        self.forest_clf = RandomForestClassifier(n_estimators=policy.n_estimators, random_state=42)
        self.log_reg = LogisticRegression()
        self.knn_clf = KNeighborsClassifier(n_neighbors=7, weights='distance')

    def get_knn_neighbour_match_list(self, knn_neighbour_index_list) -> list:
        return [self.match_train_list[index] for index in knn_neighbour_index_list]

    def make_prediction_for_the_next_matches(self, policy: Policy, matches: int = 5, write_to_page = False):
        print('\nPrediction of the next {} matches using {}...'.format(matches, policy.details_with_reward))
        self.__init_models__(policy)
        self.__init_world_cups_by_red_enh_factor__(policy.red_factor, policy.enh_factor)
        self.__fill_match_lists__(self.first_open_match_number)
        self.__train_models__(policy.col_id, False)
        offset_number = self.first_open_match_number
        x_test_data = self.get_x_test(matches, policy.col_id)
        predict_probability = self.__get_predict_probability__(x_test_data)
        knn_neighbours = list(self.knn_clf.kneighbors(x_test_data, return_distance=False))
        for number in range(offset_number, offset_number + matches):
            match = self.world_cup_test.match_list.get_match(number)
            index = offset_number - number
            neighbours_match_list = self.get_knn_neighbour_match_list(knn_neighbours[index])
            match.simulate_by_probabilities(predict_probability[number - offset_number], neighbours_match_list)
            match.print()
            self.__match_prediction_list.add_match_prediction(WorldCupMatchPrediction(match))
        self.__plot_train_data__(matches)
        if write_to_page:
            self.__write_to_web_page__(self.__match_prediction_list.get_best_match_prediction_list())

    def print_match_prediction_summary(self):
        best_prediction_list = self.__match_prediction_list.get_best_match_prediction_list()
        for best_prediction in best_prediction_list:
            best_prediction.print()

    @staticmethod
    def __write_to_web_page__(match_list: list):
        result_list = [[match.number, match.goal_team_1_simulation, match.goal_team_2_simulation] for match in match_list]
        browser = MyUrlBrowser4EM2021Odyssee()
        browser.add_results(result_list)

    def __train_models__(self, col_id: int, perform_test = False):
        x_train = self.get_x_train(col_id)
        if perform_test:
            self.__perform_test_on_training_data__(x_train, self.y_train)
        self.forest_clf.fit(x_train, self.y_train)
        self.log_reg.fit(x_train, self.y_train)
        self.knn_clf.fit(x_train, self.y_train)
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

    def __plot_train_data__(self, number_matches: int):
        classes = ['No winner', 'Team 1', 'Team 2', 'Test match']
        c_light = ['#FFAAAA', '#AAFFAA', '#AAAAFF', 'k']
        matches = []
        for i in range(0, len(c_light)):
            matches.append(mpatches.Rectangle((0, 0), 1, 1, fc=c_light[i]))
        cmap_light = ListedColormap(c_light[:3])
        cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF'])
        self.__train_models__(4)
        x_train = self.get_x_train(4)  # normal ranking
        x_test = self.get_x_test(number_matches, 4)
        x_min, x_max = x_train[:, 0].min() - 1, x_train[:, 0].max() + 1
        y_min, y_max = x_train[:, 1].min() - 1, x_train[:, 1].max() + 1
        h = round((max(x_max, y_max) - min (x_min, y_min))/100,2) # step size in the mesh
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                             np.arange(y_min, y_max, h))
        x = np.c_[xx.ravel(), yy.ravel()]

        clf_list = [self.forest_clf, self.log_reg, self.knn_clf]
        title_list = ['Random_Forest', 'Logistic_Regression', 'K-Nearest Neighbors: {}'.format(7)]

        f, axes = plt.subplots(len(clf_list), 1, sharex='col', figsize=(7, 10))
        plt.tight_layout()

        for index, clfs in enumerate(clf_list):
            ax = axes[index]
            Z = clfs.predict(np.c_[xx.ravel(), yy.ravel()])
            Z = Z.reshape(xx.shape)
            ax.pcolormesh(xx, yy, Z, cmap=cmap_light)
            ax.scatter(x_train[:, 0], x_train[:, 1], c=self.y_train, cmap=cmap_bold, label='Test')
            ax.scatter(x_test[:, 0], x_test[:, 1], c=c_light[-1])
            for i in range(0, x_test.shape[0]):
                match = self.match_test_list[i]
                ax.annotate(match.annotation, (x_test[i, 0], x_test[i, 1]))
            ax.legend(matches, classes, loc='upper right')
            ax.set_title(title_list[index])
        plt.show()


model = WorldCupModel()

config.with_policy_list = False
config.over_best_policy_list = True
config.next_matches = 1
config.write_predictions_to_web_page = True

if config.with_policy_list:
    policy_list = PolicyList(model, 10)
    policy_list.find_best_policy_with_genetic_algorithm(5, 20, 4)
    policy_list.print_best_estimated_policy(policy_list.best_policy)
    if config.over_best_policy_list:
        for policy in policy_list.best_policy_list:
            model.make_prediction_for_the_next_matches(policy,
                                                       config.next_matches, config.write_predictions_to_web_page)
        model.print_match_prediction_summary()
    else:
        model.make_prediction_for_the_next_matches(policy_list.best_policy,
                                                   config.next_matches, config.write_predictions_to_web_page)
else:
    best_policy = Policy(4, 74, 0.9, 1.9)
    # Policy: Columns = 7 (['N', 'SQUARED', 'SQRT']), Estimators = 74 / red_factor = 0.9, enh_factor = 1.9: Reward = 17
    model.make_prediction_for_the_next_matches(best_policy, config.next_matches, config.write_predictions_to_web_page)




