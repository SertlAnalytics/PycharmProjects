"""
Description: This module contains different numpy helper classes.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-14
"""

import pandas as pd


class MyPandas:
    @staticmethod
    def print_df_details(df: pd.DataFrame):
        print(df.head())
        print(df.describe())
        print(df.info())

    @staticmethod
    def get_df_reduced_regarding_category_numbers(df: pd.DataFrame, category_column: str, threshold: int):
        category_list = df[category_column].unique()
        category_remove_list = []
        for category in category_list:
            df_cat = df[df[category_column] == category]
            if df_cat.shape[0] <= threshold:
                category_remove_list.append(category)
        if len(category_remove_list) > 0:
            return df[df[category_column].isin(category_remove_list) == False]
        return df

