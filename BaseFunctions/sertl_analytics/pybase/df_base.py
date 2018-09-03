"""
Description: This module contains extended functions for handling pandas dataframes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-18
"""

import pandas as pd


class PyBaseDataFrame:
    @staticmethod
    def get_rows_as_dictionary(df: pd.DataFrame, index_column: str = '', value_column_list: list = None
                               , condition_dic: dict = None):
        dic = {}
        for ind, rows in df.iterrows():
            if PyBaseDataFrame.is_row_fulfilling_conditions(rows, condition_dic):
                key = ind if index_column == '' else rows[index_column]
                dic[key] = rows if value_column_list is None else rows[value_column_list]
        return dic

    @staticmethod
    def is_row_fulfilling_conditions(row, condition_dic: dict):
        if condition_dic is not None:
            for key in condition_dic:
                if not row[key] == condition_dic[key]:
                    return False
        return True

    @staticmethod
    def change_dict_list_to_data_frame(dict_list: list):
        df_dict = {}
        for dicts in dict_list:
            for key, values in dicts.items():
                if key not in df_dict:
                    df_dict[key] = []
                df_dict[key].append(values)
        return pd.DataFrame.from_dict(df_dict)
