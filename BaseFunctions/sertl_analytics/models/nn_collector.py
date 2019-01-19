"""
Description: This module contains the classes for handling nearest neighbors collections.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-26
"""

from sertl_analytics.constants.pattern_constants import FT, DC, PRD
import numpy as np
import pandas as pd
import statistics


class NearestNeighborEntry:
    def __init__(self, index: int, entry_id: str):
        self._index = index
        self._id = entry_id  # example: 20_0_5_EOSUSD_20_2018-09-08_12:45_2018-09-08_16:45
        self._id_components = self._id.split('_')
        self._counter = 0
        self._distance_list = []

    @property
    def id(self):
        return self._id

    @property
    def distance_list(self) -> list:
        return self._distance_list

    @property
    def asset_type(self):
        return self._id_components[0]

    @property
    def period(self):
        return PRD.get_period(int(self._id_components[1]))

    @property
    def aggregation(self):
        return self._id_components[2]

    @property
    def symbol(self):
        return self._id_components[3]

    @property
    def pattern_type(self):
        return FT.get_pattern_type(int(self._id_components[4]))

    @property
    def date_from(self):
        return self._id_components[5]

    @property
    def date_to(self):
        return self._id_components[7]

    @property
    def counter(self):
        return self._counter

    @property
    def distance(self):
        return round(statistics.mean(self._distance_list), 2)

    def add_distance(self, distance: float):
        self._counter += 1
        self._distance_list.append(distance)

    def __gt__(self, other):  # greater means better
        return self.counter > other.counter or self.counter == other.counter and self.distance < other.distance

    def __lt__(self, other):
        return not self == other and not self > other

    def __eq__(self, other):
        return self.counter == other.counter and self.distance == other.distance

    def get_details(self):
        return '{}#{}: c={}, d={}'.format(self._index, self._id, self.counter, self.distance)


class NearestNeighborContainer:
    def __init__(self, collector_id: str):
        self._id = collector_id
        self._entry_dict = {}

    def get_pattern_id_list(self):
        return [nn.id for nn in self._entry_dict.values()]

    def add_entry_list(self, entry_list: list):
        for nn_entry in entry_list:
            if nn_entry.id in self._entry_dict:
                for distance in nn_entry.distance_list:
                    # we want later the average distance over all labels...
                    self._entry_dict[nn_entry.id].add_distance(distance)
            else:
                self._entry_dict[nn_entry.id] = nn_entry

    def get_sorted_entry_list(self, period=PRD.DAILY) -> list:
        entry_list = [entry for entry in self._entry_dict.values() if entry.period == period]
        sorted_list = sorted(entry_list, reverse=True)
        return sorted_list

    def print_sorted_list(self, elements=0):
        entry_list = self.get_sorted_entry_list()
        entry_list = entry_list[:elements] if elements > 0 else entry_list
        print('\nNearestNeighborContainer: {}'.format(self._id))
        for entry in entry_list:
            print(entry.get_details())


class NearestNeighborCollector(NearestNeighborContainer):
    def __init__(self, df_features_with_labels_and_id: pd.DataFrame, collector_id: str):
        NearestNeighborContainer.__init__(self, collector_id)
        self._df = df_features_with_labels_and_id

    def add_dist_ind_array(self, ind_array: np.array, dist_array: np.array):
        ind_list = list(ind_array[0])
        dist_list = list(dist_array[0])
        for pos, index in enumerate(ind_list):
            neighbor_entry = self.__get_entry_for_index__(index)
            neighbor_entry.add_distance(dist_list[pos])

    def __get_entry_for_index__(self, index: int) -> NearestNeighborEntry:
        if index not in self._entry_dict:
            record_id = self._df.iloc[index][DC.ID]
            self._entry_dict[index] = NearestNeighborEntry(index, record_id)
        return self._entry_dict[index]