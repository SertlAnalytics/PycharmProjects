"""
Description: This module contains the entities from the stock tables
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-17
"""

import pandas as pd
import random


class AccessEntity:
    def __init__(self, data_series):
        self._entity_data_dict = data_series.to_dict()
        self.__add_specific_columns__()

    @property
    def entity_key(self):
        return ''

    def __add_specific_columns__(self):
        pass


class EntityCollection:
    def __init__(self, df: pd.DataFrame, sort_columns=None):
        self._df = self.__get_sorted_df__(df, sort_columns)
        self._entity_key_dict = {}
        self._entity_number_dict = {}
        self._counter = 0
        self.__fill_entity_dict__()

    @property
    def elements(self):
        return len(self._entity_key_dict)

    @property
    def counter(self):
        return self._counter

    @property
    def entity_number_dict(self) -> dict:
        return self._entity_number_dict

    def get_nth_element(self, number: int):
        self._counter = number
        if 1 <= number <= self.elements:
            return self._entity_number_dict[self._counter]

    def get_first_element(self):
        return self.get_nth_element(1)

    def get_next_element(self):
        return self.get_nth_element(self._counter + 1)

    def get_previous_element(self):
        return self.get_nth_element(self._counter - 1)

    def get_last_element(self):
        return self.get_nth_element(self.elements)

    def get_element_by_random(self):
        random_index = random.randint(1, self.elements)
        return self.get_nth_element(random_index)

    def __fill_entity_dict__(self):
        counter = 0
        for index, row in self._df.iterrows():
            counter += 1
            entity = self.__get_entity_for_row__(row)
            self._entity_number_dict[counter] = entity
            self._entity_key_dict[entity.entity_key] = entity
        pass

    def __get_entity_for_row__(self, row):
        pass

    @staticmethod
    def __get_sorted_df__(df: pd.DataFrame, sort_columns: object) -> pd.DataFrame:
        if sort_columns is None:
            return df
        return df.sort_values(sort_columns)




