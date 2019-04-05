"""
Description: This module contains the information for an offer for Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.mymath import MyMath
import numpy as np


class TuttiOffer:
    def __init__(self, found_by_labels=None):
        self._my_offer = found_by_labels is None
        self._found_by_labels = found_by_labels
        self._id = 0
        self._href = ''
        self._location = ''
        self._date_str = ''
        self._title = ''
        self._description = ''
        self._price = 0
        self._price_new = 0
        self._price_original = 0
        self._size = ''
        self._is_new = False
        self._is_used = False
        self._visits = 0
        self._bookmarks = 0
        self._search_labels = []
        self._entity_names = []
        self._search_labels_in_description = []
        self._search_labels_in_head_text = []

    def add_href(self, href: str):
        self._href = href
        self._id = self._href.split('/')[-1]

    def add_location_text(self, input_str: str):
        self._location = input_str

    def add_date_text(self, input_str: str):
        self._date_str = input_str

    def add_title_text(self, input_str: str):
        self._title = input_str

    def add_description_text(self, input_str: str):
        self._description = input_str

    def add_price(self, input_str: str):
        input_str = input_str.replace("'", "")  # remove thousand separators
        self._price = 0 if input_str.find('.') < 0 else MyMath.get_float_for_string(input_str, delimiter='.')
        self._price_new = self._price

    def add_visits_text(self, input_str: str):
        self._visits = int(input_str.split(' ')[0])

    def add_bookmarks_text(self, input_str: str):
        self._bookmarks = int(input_str.split(' ')[0])

    def get_start_search_label_lists(self):
        return_list = []
        if len(self._entity_names) == 0:
            start_lists = [[label] for label in self._search_labels if label in self._search_labels_in_head_text]
        else:
            start_lists = [self._entity_names]
        for start_list in start_lists:
            return_list = return_list + self.get_label_list_with_child_labels(start_list)
        return return_list

    def get_label_list_with_child_labels(self, parent_label_list: list):
        if parent_label_list[-1] in self._search_labels:
            idx_last_parent = self._search_labels.index(parent_label_list[-1])
        else:
            idx_last_parent = -1  # in this case we started with the entity names...
        if idx_last_parent == len(self._search_labels) - 1:
            return []
        return_list = []
        for idx, label in enumerate(self._search_labels):
            if idx > idx_last_parent:
                list_new = list(parent_label_list)
                list_new.append(label)
                return_list.append(list_new)
        return return_list

    @property
    def source(self):
        return 'My offer' if self._my_offer else 'Similar offer'

    @property
    def id(self):
        return self._id

    @property
    def key(self):
        return '{}_{}'.format(self._id, self.title)

    @property
    def state(self):
        if self._is_new:
            return 'new'
        else:
            return 'used' if self._is_used else 'not qualified'

    @property
    def found_by_labels(self):
        return self._found_by_labels

    @property
    def href(self):
        return self._href

    @property
    def location(self):
        return self._location

    @property
    def date_str(self):
        return self._date_str

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def price(self):
        return self._price

    @property
    def price_new(self):
        return self._price_new

    @price_new.setter
    def price_new(self, value: float):
        self._price_new = value

    @property
    def price_original(self):
        return self._price_original

    @price_original.setter
    def price_original(self, value: float):
        self._price_original = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
            self._size = value

    @property
    def is_new(self):
        return self._is_new

    @is_new.setter
    def is_new(self, value):
        self._is_new = value

    @property
    def is_used(self):
        return self._is_used

    @is_used.setter
    def is_used(self, value):
        self._is_used = value

    @property
    def visits(self):
        return self._visits

    @property
    def bookmarks(self):
        return self._bookmarks

    @property
    def search_query(self):
        return self._title if len(self._search_labels) == 0 else ' '.join(self._search_labels)

    @property
    def search_labels(self):
        return self._search_labels

    def add_search_label(self, label: str, for_title: bool, is_label_head_text: bool):
        if self.__is_label_candidate_for_label_list__(label, for_title):
            if for_title:
                self.__add_label_to_label_list__(self._search_labels, label, is_label_head_text)
            else:
                self.__add_label_to_label_list__(self._search_labels_in_description, label, is_label_head_text)

    def add_entity_name_label(self, entity_name: str, entity_label: str):
        if entity_name not in self._entity_names:
            print('Entity is relevant for Tutti: {} {}'.format(entity_name, entity_label))
            self._entity_names.append(entity_name)

    def reduce_search_labels_by_entity_names(self):
        # entity names are the most important part - they are mandatory for the search - delete them from the
        # normal search labels
        print('')
        if len(self._entity_names) > 0:
            print('Search labels before entity name deletion: {}'.format(self._search_labels))
            for entity_name in self._entity_names:
                if entity_name in self._search_labels:
                    self._search_labels.remove(entity_name)
        print('Search labels: {}'.format(self._search_labels))

    def is_price_ready_for_update_in_tutti(self) -> bool:
        return self._price_new != self._price

    def print_offer_in_original_structure(self):
        visits_bookmarks, search_details = self.__get_visits_bookmarks_and_search_details_for_printing__()
        print('\n{}: ID: {}\n{}, {}\n{}\n{}\n{:.2f} CHF{}'.format(
            self.source, self._id, self._location, self._date_str, self._title,
            self._description, self._price, visits_bookmarks)
        )
        print('Original price: {}'.format(self._price_original))
        print('Size: {}'.format(self._size))
        print('New: {}/Used: {} - Conclusion: {}'.format(self._is_new, self._is_used, self.state))
        print('{}'.format(search_details))
        if self._my_offer:
            print('Entity names: {}'.format(self._entity_names))

    def print_offer_details(self):
        visits_bookmarks, search_details = self.__get_visits_bookmarks_and_search_details_for_printing__()
        print('\n{}: ID: {}, Location: {}, Date: {}, Title: {}, Description: {}, Price: {:.2f} CHF{}{}'.format(
            self.source, self._id, self._location, self._date_str, self._title,
            self._description, self._price, visits_bookmarks, search_details)
        )
        """
        ID: 24840417, Location: Aargau, 5430, Date: 26.03.2019, Title: Lowa / Rufus III GTX / Gr. 37, 
        Description: Sehr gut erhalten. Tolles Profil., Price: 20.-, Visits: 10 Besuche, Bookmarks: 0 Merkliste
        """

    def __get_visits_bookmarks_and_search_details_for_printing__(self):
        if self._my_offer:
            visits_bookmarks = ', {} Besuche, {} Merkliste'.format(self._visits, self._bookmarks)
            search_details = '\nSearch labels: {}'.format(self.search_labels)
        else:
            visits_bookmarks = ''
            search_details = '\nFound by: {}'.format(self._found_by_labels)
        return visits_bookmarks, search_details

    def __is_label_candidate_for_label_list__(self, label: str, for_title: bool):
        if label in self._search_labels and for_title:
            return False
        if label in self._search_labels_in_description and not for_title:
            return False
        if len(set(label)) < 3:
            return False
        if self.__is_label_in_black_list__(label):
            return False
        return True

    @staticmethod
    def __is_label_in_black_list__(label: str):
        return label.lower() in [
            'grösse', 'farbe'
        ]

    def __add_label_to_label_list__(self, label_list: list, label: str, is_label_head_text: bool):
        # first we check if the new label is part of an existing. If yes we take this one (which is more general)
        # ToDo: We differ between an token which serves as a head.text (major) and one without a head.text (minor)
        # Rule: Minors can't stay alone.... works great unless USM - we need ORG as new named entities...
        if is_label_head_text:
            self._search_labels_in_head_text.append(label)
        label_lower = label.lower()
        for idx, label_in_list in enumerate(label_list):
            label_in_list_lower = label_in_list.lower()
            if label_lower.find(label_in_list_lower) >= 0:
                # the new label is more specific (longer) => we keep the shorter one
                print('new label {} covers old label {}=> keep old label'.format(label, label_in_list))
                return
            elif label_in_list_lower.find(label_lower) >= 0:
                # the new label is more general (shorter) => we replace the old one
                print('new label {} is in old label {}=> replace old label'.format(label, label_in_list))
                label_list[idx] = label
                return
        label_list.append(label)