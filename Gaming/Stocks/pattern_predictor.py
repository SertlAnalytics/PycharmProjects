"""
Description: This module is the central modul for prediction pattern detection application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-08-22
"""

from sertl_analytics.constants.pattern_constants import FT, DC
import numpy as np
import pandas as pd
from pattern_database.stock_database import StockDatabase, PatternTable, TradeTable
from pattern_database.stock_database import DatabaseDataFrame
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.model_selection import train_test_split
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pattern_configuration import PatternConfiguration
from pattern_database import stock_database
from sertl_analytics.mymath import MyMath


class PatternFeaturesSelector:
    def __init__(self, _df_features_with_label: pd.DataFrame, label_column: str, features_columns_orig: list):
        self._df_features_with_label = _df_features_with_label
        self._label_column = label_column
        self._features_columns_orig = features_columns_orig
        self._features_columns_result = features_columns_orig  # default
        self._label_feature_information_gain_dict = {}

    @property
    def features_column_result(self) -> list:
        return self._features_columns_result

    def calculate_information_gain_for_feature_columns(self):
        if self._df_features_with_label.shape[0] == 0:
            return
        df = self._df_features_with_label
        binary_value = self.__get_value_for_binary_label_column__()
        label_dict = MyMath.get_entropy_dict_for_df_label_column_values(df, self._label_column, binary_value)
        # key = '{}={}'.format(column, value) return_dict[key] = [column, value, p_v, column_entropy]
        for feature_column in self._features_columns_orig:
            feature_dict = MyMath.get_entropy_dict_for_df_feature_column_values(
                df, feature_column, self._label_column, binary_value)
            self.__add_to_gain_dict__(label_dict, feature_column, feature_dict)
        self.__print_information_gains__()

    @staticmethod
    def __print_entropy_values__(label_dict, feature_dict):
        for values in label_dict.values():
            print(values)
        for values in feature_dict.values():
            print(values)

    def __print_information_gains__(self):
        for key, value in self._label_feature_information_gain_dict.items():
            print('Information gain for {}: {}'.format(key, value))

    def __add_to_gain_dict__(self, label_dict: dict, feature_column: str, feature_dict: dict):
        for label_list in label_dict.values():  # [column, value, p_v, column_entropy]
            label_column = label_list[0]
            label_value = label_list[1]
            parent_entropy = label_list[3]
            child_correction_sum = 0
            key = 'L={}, LV={}, F={}'.format(label_column, label_value, feature_column)
            for value_list in feature_dict.values():
                if label_column == value_list[0] and label_value == value_list[1]:
                # [label_column, label_value, feature_column, feature_value, p_f_v, column_entropy]
                    child_correction_sum += value_list[-2] * value_list[-1]
            child_correction_sum = round(child_correction_sum, 4)
            information_gain = round(parent_entropy - child_correction_sum, 4)
            self._label_feature_information_gain_dict[key] = [parent_entropy, child_correction_sum, information_gain]

    @staticmethod
    def __get_parent_entropy_from_label_dict__(label_column: str, label_dict: dict):
        # [column, value, p_v, column_entropy]
        summary_entropy = 0
        for value_list in label_dict.values():
            column = value_list[0]
            value_probability = value_list[2]
            value_entropy = value_list[3]
            if column == label_column:
                if len(label_dict) == 1:
                    return value_entropy  # we don't need to calculate the entropy over all the values...
                else:
                    summary_entropy += value_probability * value_entropy
        return summary_entropy

    def __calculate_entropy_for_df_features_with_label__(self):
        print('Calculate entropy for {}:'.format(self.__class__.__name__))
        if self.__class__.__name__ == 'PatternPredictorBeforeBreakout':
            pass  # Trade_Reached_Price_PCT
        else:
            return
        for columns in self.label_columns:
            entropy = MyMath.get_entropy_of_df_column(self._df_features_with_labels, columns)
            print('Entropy for label {}: {}'.format(columns, entropy))
        for columns in self.feature_columns:
            entropy = MyMath.get_entropy_of_df_column(self._df_features_with_labels, columns)
            print('Entropy for feature {}: {}'.format(columns, entropy))

    def __get_value_for_binary_label_column__(self):  # get the highest value for binary
        unique_values = sorted(self._df_features_with_label[self._label_column].unique())
        if len(unique_values) <= 2:
            return unique_values[-1]
        return None


class PatternPredictor:
    def __init__(self, db_stock: StockDatabase, pattern_type: str, skip_condition_list=None):
        # print('Loading Predictor: {}'.format(self.__class__.__name__))
        self.db_stock = db_stock
        self.pattern_type = pattern_type
        self.skip_condition_list = skip_condition_list
        self.feature_table = self.__get_table_with_prediction_features__()
        self.feature_columns = self.__get_feature_columns__()
        self.label_columns = self.__get_label_columns__()
        self._query_for_feature_and_label_data = self.__get_query_for_feature_and_label_data__()
        self._predictor_dict = self.__get_predictor_dict__()
        self._df_features_with_labels = self.__get_df_features_with_labels__()
        self._label_feature_information_gain_dict = {}
        # self.__calculate_information_gain_for_label_feature_columns__()
        # self.__calculate_entropy_for_df_features_with_label__()
        if self.is_ready_for_prediction:
            self._df_features = self._df_features_with_labels[self.feature_columns]
            self._df_labels = self._df_features_with_labels[self.label_columns]
            self._x_data = np.array(self._df_features)
            self.__train_models__(True)
        # print('self.x_data.shape={}'.format(self._x_data.shape))

    @property
    def is_ready_for_prediction(self):
        return self._df_features_with_labels.shape[0] > 10

    def __calculate_information_gain_for_label_feature_columns__(self):
        if self._df_features_with_labels.shape[0] == 0:
            return
        df = self._df_features_with_labels
        if self.__class__.__name__ == 'PatternPredictorBeforeBreakout' and self.pattern_type == FT.CHANNEL:
            pass  # Trade_Reached_Price_PCT
        else:
            return
        print('Calculate entropy for {} and {}:'.format(self.pattern_type, self.__class__.__name__))
        for label_column in self.label_columns:
            # if label_column in [DC.FALSE_BREAKOUT, DC.BREAKOUT_DIRECTION_ID]:
            if label_column in [DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT]:
                binary_value = self.__get_value_for_binary_label_column__(label_column)
                label_dict = MyMath.get_entropy_dict_for_df_label_column_values(df, label_column, binary_value)
                # key = '{}={}'.format(column, value) return_dict[key] = [column, value, p_v, column_entropy]
                for feature_column in self.feature_columns:
                    if feature_column == DC.TOUCH_POINTS_TILL_BREAKOUT_TOP:
                        feature_dict = MyMath.get_entropy_dict_for_df_feature_column_values(
                            df, feature_column, label_column, binary_value)
                        # self.__print_entropy_values__(label_dict, feature_dict)
                        self.__add_to_gain_dict__(label_dict, feature_column, feature_dict)
        self.__print_information_gains__()

    @staticmethod
    def __print_entropy_values__(label_dict, feature_dict):
        for values in label_dict.values():
            print(values)
        for values in feature_dict.values():
            print(values)

    def __print_information_gains__(self):
        for key, value in self._label_feature_information_gain_dict.items():
            print('Information gain for {}: {}'.format(key, value))

    def __add_to_gain_dict__(self, label_dict: dict, feature_column: str, feature_dict: dict):
        for label_list in label_dict.values():  # [column, value, p_v, column_entropy]
            label_column = label_list[0]
            label_value = label_list[1]
            parent_entropy = label_list[3]
            child_correction_sum = 0
            key = 'L={}, LV={}, F={}'.format(label_column, label_value, feature_column)
            for value_list in feature_dict.values():
                if label_column == value_list[0] and label_value == value_list[1]:
                # [label_column, label_value, feature_column, feature_value, p_f_v, column_entropy]
                    child_correction_sum += value_list[-2] * value_list[-1]
            child_correction_sum = round(child_correction_sum, 4)
            information_gain = round(parent_entropy - child_correction_sum, 4)
            self._label_feature_information_gain_dict[key] = [parent_entropy, child_correction_sum, information_gain]

    @staticmethod
    def __get_parent_entropy_from_label_dict__(label_column: str, label_dict: dict):
        # [column, value, p_v, column_entropy]
        summary_entropy = 0
        for value_list in label_dict.values():
            column = value_list[0]
            value_probability = value_list[2]
            value_entropy = value_list[3]
            if column == label_column:
                if len(label_dict) == 1:
                    return value_entropy  # we don't need to calculate the entropy over all the values...
                else:
                    summary_entropy += value_probability * value_entropy
        return summary_entropy

    def __calculate_entropy_for_df_features_with_label__(self):
        print('Calculate entropy for {}:'.format(self.__class__.__name__))
        if self.__class__.__name__ == 'PatternPredictorBeforeBreakout':
            pass  # Trade_Reached_Price_PCT
        else:
            return
        for columns in self.label_columns:
            entropy = MyMath.get_entropy_of_df_column(self._df_features_with_labels, columns)
            print('Entropy for label {}: {}'.format(columns, entropy))
        for columns in self.feature_columns:
            entropy = MyMath.get_entropy_of_df_column(self._df_features_with_labels, columns)
            print('Entropy for feature {}: {}'.format(columns, entropy))

    @staticmethod
    def __get_value_for_binary_label_column__(column: str):
        column_value_dict = {
            DC.TRADE_RESULT_ID: 1,
            DC.TRADE_REACHED_PRICE: 1,
            DC.BREAKOUT_DIRECTION_ID: 1,
            DC.FALSE_BREAKOUT: 1
        }
        return column_value_dict.get(column, None)

    def predict_for_label_columns(self, x_input: pd.Series):
        np_array = x_input.values
        np_array = np_array.reshape(1, np_array.size)
        return_dict = {}
        for label in self.label_columns:
            if self.is_ready_for_prediction:
                prediction = self._predictor_dict[label].predict(np_array)[0]
            else:
                prediction = 0
            if self.feature_table.is_label_column_for_regression(label):
                return_dict[label] = round(prediction, -1)
            else:
                return_dict[label] = int(prediction)
        return return_dict

    def __get_base_query_with_pattern_type_condition__(self, base_query: str):
        if self.pattern_type != '':
            if base_query.find('WHERE') >= 0:  # already where clause available
                return base_query + " AND Pattern_Type = '{}'".format(self.pattern_type)
            return base_query + " WHERE Pattern_Type = '{}'".format(self.pattern_type)
        return base_query

    def __get_base_query_with_skip_conditions__(self, base_query: str):
        if self.skip_condition_list:
            skip_condition_all = ' AND '.join(self.skip_condition_list)
            if base_query.find('WHERE') >= 0:  # already where clause available
                return base_query + ' AND NOT ({})'.format(skip_condition_all)
            return base_query + ' WHERE NOT ({})'.format(skip_condition_all)
        return base_query

    def __get_table_with_prediction_features__(self):
        pass

    def __get_feature_columns__(self):
        pass

    def __get_label_columns__(self):
        pass

    def __get_query_for_feature_and_label_data__(self):
        pass

    def __get_y_train_for_label_column__(self, label_column: str) -> np.array:
        return np.array(self._df_labels[label_column])

    def __get_df_features_with_labels__(self):
        return DatabaseDataFrame(self.db_stock, self._query_for_feature_and_label_data).df

    def __get_predictor_dict__(self) -> dict:
        return {label: self.__get_predictor_for_label_column__(label) for label in self.label_columns}

    def __get_predictor_for_label_column__(self, label_column: str):
        if self.feature_table.is_label_column_for_regression(label_column):
            return KNeighborsRegressor(n_neighbors=7, weights='distance')
            # return RandomForestRegressor(n_estimators=3, random_state=42)
        else:
            return KNeighborsClassifier(n_neighbors=7, weights='distance')
            # return RandomForestClassifier(n_estimators=3, random_state=42)

    @staticmethod
    def __get_predict_probability__(predictor, x_data):
        predict_probability = predictor.predict_proba(x_data).round(2)
        return predict_probability

    def __train_models__(self, perform_test=False):
        for label_columns in self.label_columns:
            self.__train_model__(label_columns, perform_test)

    def __train_model__(self, label_column: str, perform_test):
        # print('\nTrain model for label "{}"'.format(label_column))
        x_train = self._x_data
        y_train = self.__get_y_train_for_label_column__(label_column)
        predictor = self._predictor_dict[label_column]
        if perform_test:
            self.__perform_test_on_training_data__(x_train, y_train, predictor, label_column)
        else:
            predictor.fit(x_train, y_train)
            self.__print_report__(x_train, y_train, predictor, label_column)

    def __perform_test_on_training_data__(self, x_input, y_input, predictor, label_column: str):
        X_train, X_test, y_train, y_test = train_test_split(x_input, y_input, test_size=0.3)
        predictor.fit(X_train, y_train)
        self.__print_report__(X_test, y_test, predictor, label_column)

    def __print_report__(self, x_input, y_input, predictor, label_column: str):
        rfc_pred = predictor.predict(x_input)
        if self.feature_table.is_label_column_for_regression(label_column):
            self.__print_prediction_details__(y_input, rfc_pred, True)
        else:
            self.__print_prediction_details__(y_input, rfc_pred, False)
            # print(confusion_matrix(y_input, rfc_pred))
            # print('\n')
            # print(classification_report(y_input, rfc_pred))

    @staticmethod
    def __print_prediction_details__(y_input, v_predict, for_regression: bool):
        return
        for k in range(0, len(y_input)):
            if for_regression:
                print('{:6.2f} / {:6.2f}: diff = {:6.2f}'.format(y_input[k], v_predict[k], y_input[k]-v_predict[k]))
            else:
                print('{:2d} / {:2d}: diff = {:2d}'.format(y_input[k], v_predict[k], y_input[k] - v_predict[k]))

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


class PatternPredictorTouchPoints(PatternPredictor):
    def __get_table_with_prediction_features__(self) -> PatternTable:
        return PatternTable()

    def __get_feature_columns__(self):
        return self.feature_table.feature_columns_touch_points

    def __get_label_columns__(self):
        return self.feature_table.label_columns_touch_points

    def __get_query_for_feature_and_label_data__(self):
        base_query = self.feature_table.query_for_feature_and_label_data_touch_points
        base_query = self.__get_base_query_with_pattern_type_condition__(base_query)
        return self.__get_base_query_with_skip_conditions__(base_query)


class PatternPredictorBeforeBreakout(PatternPredictor):
    def __get_table_with_prediction_features__(self) -> PatternTable:
        return PatternTable()

    def __get_feature_columns__(self):
        return self.feature_table.features_columns_before_breakout

    def __get_label_columns__(self):
        return self.feature_table.label_columns_before_breakout

    def __get_query_for_feature_and_label_data__(self):
        base_query = self.feature_table.query_for_feature_and_label_data_before_breakout
        base_query = self.__get_base_query_with_pattern_type_condition__(base_query)
        return self.__get_base_query_with_skip_conditions__(base_query)


class PatternPredictorAfterBreakout(PatternPredictor):
    def __get_table_with_prediction_features__(self) -> PatternTable:
        return PatternTable()

    def __get_feature_columns__(self):
        return self.feature_table.features_columns_after_breakout

    def __get_label_columns__(self):
        return self.feature_table.label_columns_after_breakout

    def __get_query_for_feature_and_label_data__(self):
        base_query = self.feature_table.query_for_feature_and_label_data_after_breakout
        base_query = self.__get_base_query_with_pattern_type_condition__(base_query)
        return self.__get_base_query_with_skip_conditions__(base_query)


class PatternPredictorForTrades(PatternPredictor):
    def __get_table_with_prediction_features__(self) -> TradeTable:
        return TradeTable()

    def __get_feature_columns__(self):
        return self.feature_table.feature_columns_for_trades

    def __get_label_columns__(self):
        return self.feature_table.label_columns_for_trades

    def __get_query_for_feature_and_label_data__(self):
        base_query = self.feature_table.query_for_feature_and_label_data_for_trades
        base_query = self.__get_base_query_with_pattern_type_condition__(base_query)
        return self.__get_base_query_with_skip_conditions__(base_query)


class PatternMasterPredictor:
    def __init__(self, config: PatternConfiguration):
        self.config = config
        self.pattern_table = stock_database.PatternTable()
        self.trade_table = stock_database.TradeTable()
        self.db_stock = stock_database.StockDatabase()
        self.predictor_dict = {}
        self.__init_predictor_dict__()

    def get_feature_columns(self, pattern_type: str):
        predictor = self.predictor_dict[pattern_type]
        return predictor.feature_columns

    def predict_for_label_columns(self, pattern_type: str, x_input: np.array):
        predictor = self.predictor_dict[pattern_type]
        return predictor.predict_for_label_columns(x_input)

    def init_without_condition_list(self, ticker_id: str):
        self.__init_predictor_dict__(self.__get_skip_condition_list__(ticker_id))

    def __init_predictor_dict__(self, skip_condition_list=None):
        for pattern_type in FT.get_all():
            self.predictor_dict[pattern_type] = \
                self.__get_predictor_for_pattern_type__(pattern_type, skip_condition_list)

    def __get_skip_condition_list__(self, ticker_id: str) -> list:
        pass

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        pass


class PatternMasterPredictorTouchPoints(PatternMasterPredictor):
    def __get_skip_condition_list__(self, ticker_id: str) -> list:
        return ["Ticker_ID = '{}'".format(ticker_id), self.config.and_clause_for_pattern]

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        return PatternPredictorTouchPoints(self.db_stock, pattern_type, skip_condition_list)


class PatternMasterPredictorBeforeBreakout(PatternMasterPredictor):
    def __get_skip_condition_list__(self, ticker_id: str) -> list:
        return ["Ticker_ID = '{}'".format(ticker_id), self.config.and_clause_for_pattern]

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        return PatternPredictorBeforeBreakout(self.db_stock, pattern_type, skip_condition_list)


class PatternMasterPredictorAfterBreakout(PatternMasterPredictor):
    def __get_skip_condition_list__(self, ticker_id: str) -> list:
        return ["Ticker_ID = '{}'".format(ticker_id), self.config.and_clause_for_pattern]

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        return PatternPredictorAfterBreakout(self.db_stock, pattern_type, skip_condition_list)


class PatternMasterPredictorForTrades(PatternMasterPredictor):
    def __get_skip_condition_list__(self, ticker_id: str) -> list:
        return ["Ticker_ID = '{}'".format(ticker_id), self.config.and_clause_for_trade]

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        return PatternPredictorForTrades(self.db_stock, pattern_type, skip_condition_list)
