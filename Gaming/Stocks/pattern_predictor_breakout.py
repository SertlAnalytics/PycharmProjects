"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import CN, FD, PRD, DC
import pandas as pd
import numpy as np
from pattern_database.stock_database import StockDatabase
from pattern_database.stock_access_layer import AccessLayer4Stock
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report,confusion_matrix
from sklearn import linear_model
from sklearn import tree
from sklearn.svm import SVC
from sklearn import neighbors
from sklearn import ensemble


class MT:  # manipulation type
    ONE_ROW_MIXED_SCALED = 'One_Row_Mixed_Values_Scaled'
    ONE_ROW_MIXED_NOT_SCALED = 'One_Row_Mixed_Values_Not_Scaled'
    ONE_ROW_PER_VALUE = 'One_Row_Per_Value'


class BreakoutPredictor:
    def __init__(self, std_dev_range=30, len_learning_range=30, train_model=False,
                 number_symbols=1, manipulation_type=MT.ONE_ROW_PER_VALUE, breakout_level_threshold=0):
        self._std_dev_range = std_dev_range
        self._len_learning_range = len_learning_range
        self._db_stock = StockDatabase()
        self._manipulation_type = manipulation_type
        self._breakout_level_threshold = breakout_level_threshold
        self._list = ['MMM', 'MCD', 'MRK', 'MSFT', 'MAR', 'MXIM', 'MCHP', 'MU', 'MNST', 'MYL', 'MDLZ', 'MELI']
        self._symbols = self._list[:number_symbols]
        self._col_value_dict = {DC.OPEN: 1, DC.LOW: 2, DC.HIGH: 3, DC.CLOSE: 4, DC.VOLUME: 5}
        self._col_value_dict = {DC.OPEN: 1, DC.CLOSE: 4, DC.VOLUME: 5}
        if train_model:
            self.__train_model__()

    def __train_model__(self):
        x_dict = {}
        y_dict = {}
        for symbol in self._symbols:
            df_all_symbol = AccessLayer4Stock(self._db_stock).get_all_as_data_frame(symbol)
            df_manipulated_symbol = self.__get_data_frame_with_breakout_details_columns__(df_all_symbol)
            df_labelled = self.__get_labeled_data__(df_manipulated_symbol, symbol)
            columns = df_labelled.shape[1]
            x_dict[symbol] = df_labelled.loc[:, 0:columns-2]
            y_dict[symbol] = np.array(df_labelled.loc[:, columns-1:columns-1]).ravel()

        x_train_scaled_final = None
        x_test_scaled_final = None
        y_train_final = None
        y_test_final = None

        for symbol in x_dict:
            x = x_dict[symbol]
            y = y_dict[symbol]
            x_train, x_test, y_train, y_test = train_test_split(x, y)
            x_train, x_test = np.array(x_train), np.array(x_test)
            if self._manipulation_type == MT.ONE_ROW_MIXED_SCALED:
                scaler = StandardScaler()
                scaler.fit(x_train)  # Fit only to the training data
                x_train_scaled = scaler.transform(x_train)  # Now apply the transformations to the data...
                x_test_scaled = scaler.transform(x_test)
            else:
                x_train_scaled = x_train
                x_test_scaled = x_test

            if x_train_scaled_final is None:
                x_train_scaled_final = x_train_scaled
                x_test_scaled_final = x_test_scaled
                y_train_final = y_train
                y_test_final = y_test
            else:
                x_train_scaled_final = np.concatenate((x_train_scaled_final, x_train_scaled))
                x_test_scaled_final = np.concatenate((x_test_scaled_final, x_test_scaled))
                y_train_final = np.concatenate((y_train_final, y_train))
                y_test_final = np.concatenate((y_test_final, y_test))

        for cls in self.__get_classifier_list__():
            cls.fit(x_train_scaled_final, y_train_final)
            predictions = cls.predict(x_test_scaled_final)
            print(confusion_matrix(y_test_final, predictions))
            print(classification_report(y_test_final, predictions))

            # predictions = cls.predict(x_train_scaled_final)
            # print(confusion_matrix(y_train_final, predictions))
            # print(classification_report(y_train_final, predictions))
        # print('{}, {}, {}'.format(len(cls.coefs_), len(cls.coefs_[0]), len(cls.intercepts_[0])))

    @staticmethod
    def __get_classifier_list__():
        cls_list = [
            # ensemble.RandomForestClassifier(n_estimators=100, max_depth=2, random_state=0),
            # tree.DecisionTreeClassifier(random_state=0),
            neighbors.KNeighborsClassifier(n_neighbors=7, weights='distance'),
            MLPClassifier(),
            # SVC(gamma='auto')
        ]
        return cls_list

    def __get_labeled_data__(self, df: pd.DataFrame, symbol: str):
        if self._manipulation_type == MT.ONE_ROW_MIXED_SCALED:
            return self.__get_labeled_data_for_mixed_data_for_scaling__(df, symbol)
        elif self._manipulation_type == MT.ONE_ROW_MIXED_NOT_SCALED:
            return self.__get_labeled_data_for_mixed_data_without_scaling__(df, symbol)
        else:
            return self.__get_labeled_data_for_single_data_per_row__(df, symbol)

    def __get_labeled_data_for_mixed_data_for_scaling__(self, df: pd.DataFrame, symbol: str):
        matrix = []
        df_symbol = df.sort_values([DC.TIMESTAMP], ascending=True)
        df_symbol.reset_index(drop=True, inplace=True)
        for m in range(0, df_symbol.shape[0] - self._len_learning_range):
            value_list = []
            if m % 100 == 0:
                print('{}: {} of {}'.format(symbol, m, df_symbol.shape[0]))
            for k in range(0, self._len_learning_range):
                row = df.loc[m + k]
                # if k == 0:
                #     value_list.append(symbol)
                if k == self._len_learning_range - 1:  # from this row we need only the breakout level
                    value_list.append(self.__get_breakout_label__(row['BreakoutLevel']))
                    matrix.append(value_list)
                else:
                    value_list.append(row[DC.OPEN])
                    # value_list.append(row[DC.LOW])
                    # value_list.append(row[DC.HIGH])
                    # value_list.append(row[DC.CLOSE])
                    # value_list.append(row[DC.VOLUME])
        df_from_matrix = pd.DataFrame(matrix)
        return df_from_matrix

    def __get_labeled_data_for_mixed_data_without_scaling__(self, df: pd.DataFrame, symbol: str):
        matrix = []
        df_symbol = df.sort_values([DC.TIMESTAMP], ascending=True)
        df_symbol.reset_index(drop=True, inplace=True)
        for m in range(0, df_symbol.shape[0] - self._len_learning_range):
            if m % 100 == 0:
                print('{}: {} of {}'.format(symbol, m, df_symbol.shape[0]))
            row_m = df.loc[m]
            value_list = []
            for k in range(1, self._len_learning_range + 1):
                row_k = df.loc[m + k]
                if k == self._len_learning_range:  # from this row we need only the breakout level
                    value_list.append(self.__get_breakout_label__(row_k['BreakoutLevel']))
                    matrix.append(value_list)
                else:
                    for col, col_value in self._col_value_dict.items():
                        value_m = row_m[col]
                        value_k = row_k[col]
                        if value_m == 0:
                            value_list.append(0)
                        else:
                            value = round(value_k / value_m, 3)**2
                            value_list.append(value)  # rounding on percent level
        df_from_matrix = pd.DataFrame(matrix)
        return df_from_matrix

    def __get_labeled_data_for_single_data_per_row__(self, df: pd.DataFrame, symbol: str):
        matrix = []
        df_symbol = df.sort_values([DC.TIMESTAMP], ascending=True)
        df_symbol.reset_index(drop=True, inplace=True)
        for m in range(0, df_symbol.shape[0] - self._len_learning_range):
            if m % 100 == 0:
                print('{}: {} of {}'.format(symbol, m, df_symbol.shape[0]))
            row_m = df.loc[m]
            for col, col_value in self._col_value_dict.items():
                value_m = row_m[col]
                value_list = []
                for k in range(1, self._len_learning_range + 1):
                    row_k = df.loc[m + k]
                    if k == 1:
                        value_list.append(col_value)
                    if k == self._len_learning_range:  # from this row we need only the breakout level
                        value_list.append(self.__get_breakout_label__(row_k['BreakoutLevel']))
                        matrix.append(value_list)
                    else:
                        value_k = row_k[col]
                        if value_m == 0:
                            value_list.append(0)
                        else:
                            value_list.append(round(value_k / value_m, 2))  # rounding on percent level
        df_from_matrix = pd.DataFrame(matrix)
        return df_from_matrix

    def __get_breakout_label__(self, breakout_level: int):  # only big changes are regarded when breakout..
        if breakout_level > self._breakout_level_threshold:
            return 1
        elif breakout_level < -self._breakout_level_threshold:
            return -1
        return 0

    def __get_data_frame_with_breakout_details_columns__(self, df: pd.DataFrame):
        df = df[[CN.SYMBOL, CN.TIMESTAMP, CN.OPEN, CN.HIGH, CN.LOW, CN.CLOSE, CN.VOL]]
        df = df.sort_values([DC.TIMESTAMP], ascending=True)
        # df = df[[CN.SYMBOL, CN.TIMESTAMP, CN.CLOSE, CN.VOL]]
        # we have here only data for one symbol
        std_dev_list = []
        breakout_list = []
        breakout_sum_list = []
        for k in range(0, df.shape[0]):
            breakout_flag = 0  # default
            if len(std_dev_list) not in [0, df.shape[0] - 1]:
                close_k_1 = df.iloc[k - 1][CN.CLOSE]
                close_k = df.iloc[k][CN.CLOSE]
                previous_std_dev = std_dev_list[-1]
                if previous_std_dev == 0:
                    if close_k > close_k_1:
                        breakout_flag = 1
                    elif close_k < close_k_1:
                        breakout_flag = -1
                else:
                    breakout_flag = int((close_k - close_k_1) / previous_std_dev)
            breakout_list.append(breakout_flag)
            breakout_sum_list.append(sum(breakout_list))

            left_border = max(0, k - self._std_dev_range)
            right_border = 3 if k < 2 else k + 1
            df_part = df.iloc[left_border:right_border]
            std_dev = df_part[CN.CLOSE].std()
            std_dev_list.append(std_dev)
        df = df.assign(StdDev=std_dev_list)
        df = df.assign(BreakoutLevel=breakout_list)
        df = df.assign(BreakoutSum=breakout_sum_list)
        return df

