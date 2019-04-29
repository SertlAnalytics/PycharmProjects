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

