"""
Description: This module contains the information for an offer for Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.mymath import MyMath
from sertl_analytics.mydates import MyDate
from tutti_constants import TC, OCLS, POS, EL
from spacy.tokens import Doc, Span
from xlsxwriter.worksheet import Worksheet


class TuttiOffer:
    def __init__(self, nlp, found_by_labels=None):
        self._nlp = nlp
        self._my_offer = found_by_labels is None
        self._found_by_labels = found_by_labels
        self._id = 0
        self._href = ''
        self._location = ''
        self._date_str = ''
        self._title = ''
        self._description = ''
        self._price = 0
        self._price_single = 0
        self._is_total_price = False
        self._price_new = 0
        self._price_original = 0
        self._size = ''
        self._number = 1
        self._is_new = False
        self._is_used = False
        self._visits = 0
        self._bookmarks = 0
        self._search_labels = []
        self._entity_names = []
        self._search_labels_in_description = []
        self._search_labels_in_head_text = []

    def init_by_file_row(self, row_number: int, row):
        self.add_href(str(row_number))
        self.add_location_text('virtual')
        self.add_date_text(MyDate.get_date_as_string_from_date_time())
        self.add_title_text(row[TC.TITLE])
        self.add_description_text(row[TC.DESCRIPTION])
        self.add_price(str(row[TC.PRICE]))
        self.__add_search_labels__()
        self.__process_doc_extensions__()

    def init_by_offer_element(self, offer_element):
        offer_id_obj = offer_element.find_element_by_class_name(OCLS.MAIN_ANKER)
        self.add_href(offer_id_obj.get_attribute('href'))
        self.add_location_text(offer_element.find_element_by_class_name(OCLS.LOCATION).text)
        self.add_date_text(offer_element.find_element_by_class_name(OCLS.DATE).text)
        self.add_title_text(offer_element.find_element_by_class_name(OCLS.LINK).text)
        self.add_description_text(offer_element.find_element_by_class_name(OCLS.DESCRIPTION).text)
        self.add_price(offer_element.find_element_by_class_name(OCLS.PRICE).text)
        if self._my_offer:
            numbers = offer_element.find_elements_by_class_name(OCLS.NUMBERS)
            self.add_visits_text(numbers[0].text)
            self.add_bookmarks_text(numbers[1].text)
            self.__add_search_labels__()
        self.__process_doc_extensions__()

    def __add_search_labels__(self):
        doc_title = self._nlp(self._title)
        doc_description = self._nlp(self._description)
        self.__add_search_labels_for_doc__(doc_title, for_title=True)
        self.__add_search_labels_for_doc__(doc_description, for_title=False)
        self.reduce_search_labels_by_entity_names()

    def __add_search_labels_for_doc__(self, doc: Doc, for_title=False):
        print('\nDoc for {}: {}'.format('title' if for_title else 'description', doc.text))
        token_text_list = []
        token_head_text_list = []
        for token in doc:
            print('Token: text={}, lemma={}, pos={}, tag={}, dep={}, head.text={}'.format(
                token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.head.text))
            if POS.is_pos_noun(token.pos_):
                token_text_list.append(token.text)
                token_head_text_list.append(token.head.text)
        # it is more important for a token when it is a head text
        for token_text in token_text_list:
            if token_text in token_head_text_list:
                self.add_search_label(token_text, for_title, is_label_head_text=True)
            else:
                self.add_search_label(token_text, for_title, is_label_head_text=False)
        for ent in doc.ents:
            if EL.is_entity_label_tutti_relevant(ent.label_):
                self.add_entity_name_label(ent.text, ent.label_)

    def __process_doc_extensions__(self):
        doc_title_description = self._nlp(self._title + ' ' + self._description)
        self._price_original = doc_title_description._.get_original_price
        self._size = doc_title_description._.get_size
        self._number = doc_title_description._.get_number
        self._is_new = doc_title_description._.is_new
        self._is_used = doc_title_description._.is_used
        single_price = doc_title_description._.get_single_price
        self._price_single = self._price if single_price == 0 else single_price
        self._is_total_price = doc_title_description._.is_total_price
        if self._is_total_price and self._number != 0:
            self._price_single = int(self._price/self._number)

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
        self._price = MyMath.get_float_for_string(input_str, delimiter='.')
        self._price_single = self._price
        self._price_new = self._price

    def add_visits_text(self, input_str: str):
        self._visits = int(input_str.split(' ')[0])

    def add_bookmarks_text(self, input_str: str):
        self._bookmarks = int(input_str.split(' ')[0])

    def get_start_search_label_lists(self):
        return_list = []
        if len(self._entity_names) > 1:
            return [self._entity_names]
        elif len(self._entity_names) == 0:
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
        return '{}_{}'.format(self._id, self._title)

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
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def price_new(self):
        return self._price_new

    @price_new.setter
    def price_new(self, value: float):
        self._price_new = value

    def get_value_dict_for_worksheet(self, master_id=None):
        return {
            TC.ID: self._id,
            TC.ID_MASTER: self._id if master_id is None else master_id,
            TC.DATE: self._date_str,
            TC.LOCATION: self._location,
            TC.STATE: self.state,
            TC.PRICE: self._price,
            TC.IS_TOTAL_PRICE: self._is_total_price,
            TC.PRICE_SINGLE: self._price_single,
            TC.PRICE_ORIGINAL: self._price_original,
            TC.NUMBER: self._number,
            TC.SIZE: self._size,
            TC.TITLE: self._title,
            TC.DESCRIPTION: self._description,
            TC.IS_NEW: self._is_new,
            TC.IS_USED: self._is_used,
            TC.VISITS: self._visits,
            TC.BOOK_MARKS: self._bookmarks,
            TC.SEARCH_LABELS: ','.join(self._search_labels),
            TC.ENTITY_LABELS: ','.join(self._entity_names),
            TC.FOUND_BY_LABELS: '' if self._found_by_labels is None else ','.join(self._found_by_labels),
            TC.HREF: self._href,
        }

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
        print('Is price total price: {}'.format(self._is_total_price))
        print('Single price: {}'.format(self._price_single))
        print('Original price: {}'.format(self._price_original))
        print('Size: {}'.format(self._size))
        print('Number: {}'.format(self._number))
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
            search_details = '\nSearch labels: {}'.format(self._search_labels)
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