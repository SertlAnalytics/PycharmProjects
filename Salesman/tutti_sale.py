"""
Description: This module contains the information for an offer for Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.mymath import MyMath
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.salesman_constants import SLDC, SLST, OBJST
from tutti_constants import SLCLS, POS, EL
from spacy.tokens import Doc, Span
from tutti_named_entity import TuttiEntityHandler
from lxml.html import HtmlElement
from sertl_analytics.myhtml import MyHtmlElement
from tutti_spacy import TuttiSpacy
from salesman_data_dictionary import SalesmanDataDictionary
from salesman_system_configuration import SystemConfiguration


class TuttiSale:
    def __init__(self, spacy: TuttiSpacy, sys_config: SystemConfiguration, found_by_labels=None):
        self.sys_config = sys_config
        self.data_dict_obj = SalesmanDataDictionary(self.sys_config)
        self._spacy = spacy
        self._nlp = spacy.nlp
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
        self._is_outlier = False
        self._visits = 0
        self._bookmarks = 0
        self._search_labels = []
        self._entity_label_dict = {}  # contains entities with {value: label, value: label}
        self._entity_names = []
        self._search_labels_in_description = []
        self._search_labels_in_head_text = []

    @property
    def domain(self):
        return 'https://www.tutti.ch'

    @property
    def company_list(self):
        return [ent_name for ent_name, ent_label in self._entity_label_dict.items() if ent_label == EL.COMPANY]

    @property
    def product_list(self):
        return [ent_name for ent_name, ent_label in self._entity_label_dict.items() if ent_label == EL.PRODUCT]

    @property
    def object_list(self):
        return [ent_name for ent_name, ent_label in self._entity_label_dict.items() if ent_label == EL.OBJECT]

    def init_by_file_row(self, row):
        self._id = row[SLDC.SALE_ID]
        self.add_location_text('virtual')
        self.add_date_text(MyDate.get_date_as_string_from_date_time())
        self.add_title_text(row[SLDC.TITLE])
        self.add_description_text(row[SLDC.DESCRIPTION])
        self.add_price(str(row[SLDC.PRICE]))
        self.__add_search_labels__()
        self.__process_doc_extensions__()
        self.__add_data_dict_entries__()

    def init_by_online_input(self, title: str, description: str):
        self._id = MyDate.time_stamp_now()
        self.add_location_text('online')
        self.add_date_text(MyDate.get_date_as_string_from_date_time())
        self.add_title_text(title)
        self.add_description_text(description)
        self.add_price(str(0))
        self.__add_search_labels__()
        self.__process_doc_extensions__()
        self.__add_data_dict_entries__()

    def init_by_sale_element(self, offer_element):
        offer_id_obj = offer_element.find_element_by_class_name(SLCLS.MAIN_ANKER)
        self.add_href(offer_id_obj.get_attribute('href'))
        self.add_location_text(offer_element.find_element_by_class_name(SLCLS.LOCATION).text)
        self.add_date_text(offer_element.find_element_by_class_name(SLCLS.DATE).text)
        self.add_title_text(offer_element.find_element_by_class_name(SLCLS.LINK).text)
        self.add_description_text(offer_element.find_element_by_class_name(SLCLS.DESCRIPTION).text)
        self.add_price(offer_element.find_element_by_class_name(SLCLS.PRICE).text)
        if self._my_offer:
            numbers = offer_element.find_elements_by_class_name(SLCLS.NUMBERS)
            self.add_visits_text(numbers[0].text)
            self.add_bookmarks_text(numbers[1].text)
            self.__add_search_labels__()
        self.__process_doc_extensions__()
        self.__add_data_dict_entries__()

    def init_by_html_element(self, html_element: HtmlElement):
        my_html_element = MyHtmlElement(html_element)
        self.add_href(my_html_element.get_attribute_for_sub_class(SLCLS.MAIN_ANKER, 'href'))
        self.add_location_text(my_html_element.get_text_for_sub_class(SLCLS.LOCATION))
        self.add_date_text(my_html_element.get_text_for_sub_class(SLCLS.DATE))
        self.add_title_text(my_html_element.get_text_for_sub_class(SLCLS.TITLE))
        self.add_description_text(my_html_element.get_text_for_sub_class(SLCLS.DESCRIPTION))
        self.add_price(my_html_element.get_text_for_sub_class(SLCLS.PRICE))
        self.__process_doc_extensions__()
        self.__add_data_dict_entries__()

    def is_any_term_in_list_in_title_or_description(self, term_list: str):
        return self.__is_any_term_in_list_in_text__(term_list, self._title.lower() + self._description.lower())

    def is_any_term_in_list_in_title(self, term_list: str):
        return self.__is_any_term_in_list_in_text__(term_list, self._title.lower())

    def set_master_id(self, master_id: str):
        self.data_dict_obj.add(SLDC.MASTER_ID, master_id)

    def set_source(self, source: str):
        self.data_dict_obj.add(SLDC.SOURCE, source)

    @staticmethod
    def __is_any_term_in_list_in_text__(term_list: str, check_string_lower: str):
        if len(term_list) == 0:
            return True
        for term_lower in [term.lower() for term in term_list]:
            if check_string_lower.find(term_lower) >= 0:
                return True
        return False

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
        self._spacy.print_tokens_for_doc(doc)
        for token in doc:
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
        self._href = '{}{}'.format(self.domain, href) if href.find('https') < 0 else href
        self._id = self._href.split('/')[-1]

    def add_location_text(self, input_str: str):
        self._location = input_str

    def add_date_text(self, input_str: str):
        self._date_str = MyDate.get_date_str_for_date_term(input_str)

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
        print('self._entity_names: {}, dict: {}'.format(self._entity_names, self._entity_label_dict))
        if len(self._entity_names) == 0:  # we use labels in head text
            start_lists = [[label] for label in self._search_labels if label in self._search_labels_in_head_text]
        elif len(self._entity_names) == 1:  # we use all entity names
            start_lists = [self._entity_names]
        elif len(self._entity_names) == 2: # we start with all entity names
            return [self._entity_names]
        else:
            return self.__get_start_list_for_several_entity_names__()
        for start_list in start_lists:
            return_list = return_list + self.get_label_list_with_child_labels(start_list)
        return return_list

    def __get_start_list_for_several_entity_names__(self):
        # If #{PROUDCT, OBJECT} > 1 then whe have several start_search_label_list - each combination...
        c_list = [ent_name for ent_name, ent_label in self._entity_label_dict.items() if ent_label == EL.COMPANY]
        p_list = [ent_name for ent_name, ent_label in self._entity_label_dict.items() if ent_label == EL.PRODUCT]
        o_list = [ent_name for ent_name, ent_label in self._entity_label_dict.items() if ent_label == EL.OBJECT]

        if len(c_list) == 0:  # we don't have a company name
            return [[p, o] for p in p_list for o in o_list]

        if len(p_list) == 0:  # we don't have products - but company and objects
            return [[c, o] for c in c_list for o in o_list]

        return [[c, p] for c in c_list for p in p_list]

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
        return '{} ({})'.format(self.data_dict_obj.get(SLDC.SOURCE), 'My offer' if self._my_offer else 'Similar offer')

    @property
    def id(self):
        return self._id

    @property
    def key(self):
        return '{}_{}'.format(self._id, self._title)

    @property
    def sale_state(self):
        return SLST.NEW

    @property
    def object_state(self):
        if self._is_new:
            return OBJST.NEW
        else:
            return OBJST.USED if self._is_used else OBJST.NOT_QUALIFIED

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

    @property
    def price_single(self):
        return self._price_single

    def is_sale_ready_for_sale_table(self):
        return self.data_dict_obj.is_data_dict_ready_for_sale_table()

    def set_is_outlier(self, value: bool):
        self._is_outlier = value

    def get_value_dict_for_worksheet(self, master_id=None):
        self.set_master_id(self._id if master_id is None else master_id)
        worksheet_columns = SLDC.get_columns_for_excel()
        return {column: self.data_dict_obj.get(column) for column in worksheet_columns}

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
            self._entity_label_dict[entity_name] = entity_label
            entity_synonyms = TuttiEntityHandler.get_synonyms_for_entity_name(entity_label, entity_name)
            if len(entity_synonyms) > 0:
                print('Entity {} has synonym {}'.format(entity_name, entity_synonyms))
                # self._entity_names.append(entity_synonym)
                for entity_synonym in entity_synonyms:
                    self._entity_label_dict[entity_synonym] = entity_label

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

    def print_sale_in_original_structure(self):
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
        print('New: {}/Used: {} - Conclusion: {}'.format(self._is_new, self._is_used, self.object_state))
        if not self._my_offer:
            print('Is outlier: {}'.format(self._is_new, self._is_used, self._is_outlier))
        print('{}'.format(search_details))
        if self._my_offer:
            print('Entity names: {}'.format(self._entity_names))

    def print_sale_details(self):
        visits_bookmarks, search_details = self.__get_visits_bookmarks_and_search_details_for_printing__()
        print('\n{}: ID: {}, Location: {}, Date: {}, Title: {}, Description: {}, Price: {:.2f} CHF{}{}'.format(
            self.source, self._id, self._location, self._date_str, self._title,
            self._description, self._price, visits_bookmarks, search_details)
        )
        """
        ID: 24840417, Location: Aargau, 5430, Date: 26.03.2019, Title: Lowa / Rufus III GTX / Gr. 37, 
        Description: Sehr gut erhalten. Tolles Profil., Price: 20.-, Visits: 10 Besuche, Bookmarks: 0 Merkliste
        """

    def __add_data_dict_entries__(self):
        self.data_dict_obj.add(SLDC.SALE_ID, self._id)
        self.data_dict_obj.add(SLDC.MASTER_ID, self._id)  # default - will be overwritten...
        self.data_dict_obj.add(SLDC.SALE_STATE, self.sale_state)
        self.data_dict_obj.add(SLDC.SOURCE, '')  # default - will be overwritten...
        self.data_dict_obj.add(SLDC.START_DATE, self._date_str)
        self.data_dict_obj.add(SLDC.LOCATION, self._location)
        self.data_dict_obj.add(SLDC.OBJECT_STATE, self.object_state)
        self.data_dict_obj.add(SLDC.PRICE, self._price)
        self.data_dict_obj.add(SLDC.IS_TOTAL_PRICE, self._is_total_price)
        self.data_dict_obj.add(SLDC.PRICE_SINGLE, self._price_single)
        self.data_dict_obj.add(SLDC.IS_OUTLIER, self._is_outlier)
        self.data_dict_obj.add(SLDC.PRICE_ORIGINAL, self._price_original)
        self.data_dict_obj.add(SLDC.NUMBER, self._number)
        self.data_dict_obj.add(SLDC.SIZE, self._size)
        self.data_dict_obj.add(SLDC.TITLE, self._title)
        self.data_dict_obj.add(SLDC.DESCRIPTION, self._description)
        self.data_dict_obj.add(SLDC.IS_NEW, self._is_new)
        self.data_dict_obj.add(SLDC.IS_USED, self._is_used)
        self.data_dict_obj.add(SLDC.VISITS, self._visits)
        self.data_dict_obj.add(SLDC.BOOK_MARKS, self._bookmarks)
        self.data_dict_obj.add(SLDC.SEARCH_LABELS, ','.join(self._search_labels))
        self.data_dict_obj.add(SLDC.ENTITY_LABELS, ','.join(self._entity_names))
        self.data_dict_obj.add(SLDC.FOUND_BY_LABELS,
                               '' if self._found_by_labels is None else ','.join(self._found_by_labels))
        self.data_dict_obj.add(SLDC.HREF, self._href)
        self.data_dict_obj.add(SLDC.PRICE_CHANGES, '')
        self.data_dict_obj.add(SLDC.END_DATE, '')
        self.data_dict_obj.add(SLDC.END_PRICE, 0)
        self.data_dict_obj.add(SLDC.LAST_CHECK_DATE, MyDate.get_date_str_from_datetime())
        self.data_dict_obj.add(SLDC.COMMENT, '1. load')

    def __get_visits_bookmarks_and_search_details_for_printing__(self):
        if self._my_offer:
            visits_bookmarks = ', {} Besuche, {} Merkliste'.format(self._visits, self._bookmarks)
            search_details = 'Search labels: {}'.format(self._search_labels)
        else:
            visits_bookmarks = ''
            search_details = 'Found by: {}'.format(self._found_by_labels)
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