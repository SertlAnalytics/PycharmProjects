"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import PRED, STBL, FT, DC
import numpy as np
import pandas as pd
from pattern_database.stock_database import StockDatabase, PatternTable, TradeTable
from pattern_database.stock_database import DatabaseDataFrame


class AccessLayerPrediction:
    def __init__(self, db_stock: StockDatabase):
        self._db_stock = db_stock
        self._pattern_table = PatternTable()
        self._trade_table = TradeTable()
        self._df_features_and_labels_dict = {}
        self._features_column_dict = {}
        self._label_column_dict = {}
        self._x_data_y_train_data_dict = {}

    @staticmethod
    def get_x_data_in_correct_format(x_data) -> np.array:
        np_array = np.array(x_data)
        np_array = np_array.reshape(1, np_array.size)
        return np_array

    def get_df_features_and_labels_for_predictor(
            self, table_name: str, predictor: str, pattern_type: str, skip_condition_list: list):
        key = self.__get_key_for_dict__(table_name, predictor, pattern_type)
        if key not in self._df_features_and_labels_dict:
            self._df_features_and_labels_dict[key] = \
                self.__get_data_frame_for_features_and_labels__(
                    table_name, predictor, pattern_type, skip_condition_list)
        return self._df_features_and_labels_dict[key]

    def get_features_columns_for_predictor(self, table_name: str, predictor: str):
        key = self.__get_key_for_dict__(table_name, predictor)
        if key not in self._features_column_dict:
            self._features_column_dict[key] = self.__get_feature_columns__(table_name, predictor)
        return self._features_column_dict[key]

    def get_label_columns_for_predictor(self, table_name: str, predictor: str):
        key = self.__get_key_for_dict__(table_name, predictor)
        if key not in self._label_column_dict:
            self._label_column_dict[key] = self.__get_label_columns__(table_name, predictor)
        return self._label_column_dict[key]

    def get_x_data_y_train_data_for_predictor(
            self, table_name: str, predictor: str, label: str, pattern_type: str, skip_condition_list: list):
        key = self.__get_key_for_dict__(table_name, predictor, label, pattern_type)
        if key not in self._x_data_y_train_data_dict:
            print('Get x_y_data: {}'.format(key))
            df = self.get_df_features_and_labels_for_predictor(table_name, predictor, pattern_type, skip_condition_list)
            self._x_data_y_train_data_dict[key] = self.__get_x_train_y_train_manipulated__(
                df, table_name, predictor, label)
        return self._x_data_y_train_data_dict[key]

    def __get_x_train_y_train_manipulated__(self, df: pd.DataFrame, table_name: str, predictor: str, label: str):
        """
        1. Remove the outlines  # ToDo - current we remove only the nn% at the ends - there are smarter ways
        2. Reduce the number of classes to 10
        """
        df = pd.DataFrame(self.__drop_outliers__(df, label, 2))
        feature_columns = self.get_features_columns_for_predictor(table_name, predictor)
        x_train = df[feature_columns]
        y_train = df[label]
        y_train_compressed = self.__get_compressed_y_train__(y_train, 10)
        return x_train, y_train_compressed

    @staticmethod
    def __drop_outliers__(df: pd.DataFrame, label: str, percentile: int):
        number_rows_before = df.shape[0]
        percentile_top = 100 - percentile
        percentile_bottom = percentile
        value_top = np.percentile(df[label], percentile_top)
        value_bottom = np.percentile(df[label], percentile_bottom)
        df_top = df[df[label] > value_top]
        df_return = pd.DataFrame(df.drop(df_top.index, inplace=False))
        df_bottom = df_return[df_return[label] < value_bottom]
        df_return = pd.DataFrame(df_return.drop(df_bottom.index, inplace=False))
        if number_rows_before > df_return.shape[0]:
            print('drop_outliers_before={} - after={}'.format(number_rows_before, df_return.shape[0]))
        return df_return

    @staticmethod
    def __get_compressed_y_train__(y_train, number_classes: int):
        diff_values = list(set(y_train))
        if len(diff_values) < number_classes:
            return y_train
        min_value = np.min(diff_values)
        max_value = np.max(diff_values)
        compressor = max_value - min_value
        y_train_compressed = round(y_train / compressor, int(number_classes/10)) * compressor
        y_train_compressed = y_train_compressed.astype(np.int64)
        # print('\ny_train_orig: {}\ny_train_compressed: {}'.format(list(y_train)[:50], list(y_train_compressed)[:50]))
        return y_train_compressed

    def __get_data_frame_for_features_and_labels__(
            self, table_name: str, predictor: str, pattern_type: str, skip_condition_list: list)-> pd.DataFrame:
        if table_name == STBL.PATTERN:
            if predictor == PRED.TOUCH_POINT:
                query = self._pattern_table.query_for_feature_and_label_data_touch_points
            elif predictor == PRED.BEFORE_BREAKOUT:
                query = self._pattern_table.query_for_feature_and_label_data_before_breakout
            else:
                query = self._pattern_table.query_for_feature_and_label_data_after_breakout
        else:
            query = self._trade_table.query_for_feature_and_label_data_for_trades
        query = self.__get_query_with_skip_condition_list__(query, skip_condition_list)
        df = DatabaseDataFrame(self._db_stock, query).df
        if pattern_type != FT.ALL:
            df = df[df[DC.PATTERN_TYPE] == pattern_type]
        return df

    @staticmethod
    def __get_query_with_skip_condition_list__(query: str, skip_condition_list: list):
        if skip_condition_list is None:
            return query
        skip_condition_all = ' AND '.join(skip_condition_list)
        if query.find('WHERE') >= 0:  # already where clause available
            return query + ' AND NOT ({})'.format(skip_condition_all)
        return query + ' WHERE NOT ({})'.format(skip_condition_all)

    @staticmethod
    def __get_key_for_dict__(table_name: str, predictor: str, label='ALL', pattern_type=FT.ALL):
        return '{}-{}-{}-{}'.format(table_name, predictor, label, pattern_type)

    def __get_feature_columns__(self, table_name: str, predictor: str):
        if table_name == STBL.PATTERN:
            if predictor == PRED.TOUCH_POINT:
                return self._pattern_table.feature_columns_touch_points
            elif predictor == PRED.BEFORE_BREAKOUT:
                return self._pattern_table.features_columns_before_breakout
            else:
                return self._pattern_table.features_columns_after_breakout
        else:
            return self._trade_table.feature_columns_for_trades

    def __get_label_columns__(self, table_name: str, predictor: str):
        if table_name == STBL.PATTERN:
            if predictor == PRED.TOUCH_POINT:
                return self._pattern_table.get_label_columns_touch_points_for_statistics()
            elif predictor == PRED.BEFORE_BREAKOUT:
                return self._pattern_table.get_label_columns_before_breakout_for_statistics()
            elif predictor == PRED.AFTER_BREAKOUT:
                return self._pattern_table.get_label_columns_after_breakout_for_statistics()
        else:
            return self._trade_table.get_label_columns_for_trades_statistics()

