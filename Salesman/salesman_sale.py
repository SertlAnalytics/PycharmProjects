"""
Description: This module contains the information for an offer for Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.mymath import MyMath
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.salesman_constants import SLDC, SLSRC, SLST, OBJST
from salesman_tutti.tutti_constants import  EL
from entities.salesman_named_entity import SalesmanEntityHandler
from salesman_nlp.salesman_doc_extended import DocExtended
from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_data_dictionary import SalesmanDataDictionary
from salesman_system_configuration import SystemConfiguration
from salesman_tutti.tutti_url_factory import TuttiUrlFactory


class SalesmanSale:
    def __init__(self, spacy: SalesmanSpacy, sys_config: SystemConfiguration, found_by_labels=None, is_my_offer=False):
        self.sys_config = sys_config
        self._data_dict_obj = SalesmanDataDictionary(self.sys_config)
        self._salesman_spacy = spacy
        self._salesman_nlp = self._salesman_spacy.nlp
        self._url_factory = TuttiUrlFactory(self.sys_config, self._salesman_spacy)
        self._my_offer = is_my_offer
        self._found_by_labels = '' if found_by_labels is None else found_by_labels
        self._product_categories_value_list = []  # is used for online searches as default product categories
        self._search_labels = []
        self._entity_label_dict = {}  # contains entities with {value: label, value: label}
        self._property_dict = {}  # contains all properties for this object (details).
        self._entity_names = []
        self._search_labels_in_description = []
        self._search_labels_in_head_text = []
        self.__init_data_dict_entries__()

    @property
    def source(self):
        return '{} ({})'.format(self.get_value(SLDC.SOURCE), 'My offer' if self._my_offer else 'Similar offer')

    @property
    def sale_id(self):
        return self.get_value(SLDC.SALE_ID)

    @property
    def version(self):
        return self.get_value(SLDC.VERSION)

    @property
    def start_date(self):
        return self.get_value(SLDC.START_DATE)

    @property
    def region(self):
        return self._data_dict_obj.get(SLDC.REGION)

    @property
    def product_category(self):
        return self._data_dict_obj.get(SLDC.PRODUCT_CATEGORY)

    @property
    def product_sub_category(self):
        return self._data_dict_obj.get(SLDC.PRODUCT_SUB_CATEGORY)

    @property
    def title(self):
        return self.get_value(SLDC.TITLE)

    @property
    def description(self):
        return self.get_value(SLDC.DESCRIPTION)

    @property
    def key(self):
        return '{}_{}'.format(self.sale_id, self.title)

    @property
    def price(self):
        return self.get_value(SLDC.PRICE)

    @property
    def price_single(self):
        return self.get_value(SLDC.PRICE_SINGLE)

    @property
    def price_new(self):
        return self.get_value(SLDC.PRICE_NEW)

    @property
    def location(self):
        return self.get_value(SLDC.LOCATION)

    @property
    def found_by_labels(self):
        return self._found_by_labels

    @property
    def material_list(self):
        return [ent_name for ent_name, ent_label in self._entity_label_dict.items() if ent_label == EL.MATERIAL]

    @property
    def target_group_list(self):
        return [ent_name for ent_name, ent_label in self._entity_label_dict.items() if ent_label == EL.TARGET_GROUP]

    @property
    def company_list(self):
        return [ent_name for ent_name, ent_label in self._entity_label_dict.items() if ent_label == EL.COMPANY]

    @property
    def product_list(self):
        return [ent_name for ent_name, ent_label in self._entity_label_dict.items() if ent_label == EL.PRODUCT]

    @property
    def object_list(self):
        return [ent_name for ent_name, ent_label in self._entity_label_dict.items() if ent_label == EL.OBJECT]

    @property
    def entity_names(self):
        return self._entity_names

    @property
    def entity_label_dict(self):
        return self._entity_label_dict

    @property
    def product_categories_value_list(self):
        return self._product_categories_value_list

    def get_value(self, key: str):
        return self._data_dict_obj.get(key, '')

    def set_value(self, key: str, value):
        return self._data_dict_obj.add(key, self.__get_corrected_value__(key, value))

    def get_data_dict_for_sale_table(self) -> dict:
        return self._data_dict_obj.get_data_dict_for_sale_table()

    def get_data_dict_for_columns(self, columns: list) -> dict:
        return self._data_dict_obj.get_data_dict_for_columns(columns)

    @staticmethod
    def __get_corrected_value__(key: str, value):
        if key == SLDC.PRICE:
            if type(value) is str:
                return MyMath.get_float_for_string(value)
        elif key == SLDC.START_DATE:
            return MyDate.get_date_str_for_date_term(value)
        elif key in [SLDC.VISITS, SLDC.BOOK_MARKS]:
            if type(value) is str:
                return int(value.split(' ')[0])
        return value

    def set_product_categories_value_list(self, product_categories_value_list):
        self._product_categories_value_list = product_categories_value_list
        print('set_product_categories_value_list: {}'.format(self._product_categories_value_list))

    def set_master_details(self, master_id: str, master_title: str):
        self.set_value(SLDC.MASTER_ID, master_id)
        self.set_value(SLDC.MASTER_TITLE, master_title)

    def is_any_term_in_list_in_title_or_description(self, term_list: str):
        return self.__is_any_term_in_list_in_text__(term_list, self.title.lower() + self.description.lower())

    def is_any_material_entity_identical(self, other_sale) -> bool:
        return self.__is_any_entity_identical__(self.material_list, other_sale.material_list, EL.MATERIAL)

    def is_any_target_group_entity_identical(self, other_sale) -> bool:
        return self.__is_any_entity_identical__(self.target_group_list, other_sale.target_group_list, EL.TARGET_GROUP)

    def is_any_company_entity_identical(self, other_sale) -> bool:
        return self.__is_any_entity_identical__(self.company_list, other_sale.company_list, EL.COMPANY)

    def is_any_product_entity_identical(self, other_sale) -> bool:
        return self.__is_any_entity_identical__(self.product_list, other_sale.product_list, EL.PRODUCT)

    def is_any_object_entity_identical(self, other_sale) -> bool:
        return self.__is_any_entity_identical__(self.object_list, other_sale.object_list, EL.OBJECT)

    @staticmethod
    def __is_any_entity_identical__(entity_list: list, entity_list_comp: list, entity_label=''):
        if min(len(entity_list), len(entity_list_comp)) == 0:
            return False
        # Now we have at least one entry in each list...
        set_01 = set([entity_name.lower() for entity_name in entity_list])
        set_02 = set([entity_name.lower() for entity_name in entity_list_comp])
        set_intersection = set_01.intersection(set_02)
        if len(set_intersection) == 0:  # we don't have anything in common
            return False
        if len(set_intersection) * 2 < max(len(set_01), len(set_02)):  # we have too many other entities per set
            return False
        return True

    def is_any_term_in_list_in_title(self, term_list: str):
        return self.__is_any_term_in_list_in_text__(term_list, self.title.lower())

    def set_source(self, source: str):
        self.set_value(SLDC.SOURCE, source)

    @staticmethod
    def __is_any_term_in_list_in_text__(term_list: str, check_string_lower: str):
        if len(term_list) == 0:
            return True
        for term_lower in [term.lower() for term in term_list]:
            if check_string_lower.find(term_lower) >= 0:
                return True
        return False

    def add_value_dict(self, value_dict: dict):
        for key, value in value_dict.items():
            self.set_value(key, value)

    def add_location_text(self, input_str: str):
        self.set_value(SLDC.LOCATION, input_str)

    def add_date_text(self, input_str: str):
        self.set_value(SLDC.START_DATE, MyDate.get_date_str_for_date_term(input_str))

    def add_title_text(self, input_str: str):
        self.set_value(SLDC.TITLE, input_str)

    def add_description_text(self, input_str: str):
        self.set_value(SLDC.DESCRIPTION, input_str)

    def add_price(self, input_str: str):
        self.set_value(SLDC.PRICE, MyMath.get_float_for_string(input_str, delimiter='.'))
        self.set_value(SLDC.PRICE_SINGLE, self.get_value(SLDC.PRICE))
        self.set_value(SLDC.PRICE_ORIGINAL, self.get_value(SLDC.PRICE))

    def add_visits_text(self, input_str: str):
        self.set_value(SLDC.VISITS, int(input_str.split(' ')[0]))

    def add_bookmarks_text(self, input_str: str):
        self.set_value(SLDC.BOOK_MARKS, int(input_str.split(' ')[0]))

    def get_search_label_lists(self):
        """
        The following rules are implemented:
        1. If object name is available => use object name
        2. If company and product names are available => use these tupels
        Material, Target_group and Company are NOT used for the search - they are used later for similarity...
        :return: list of lists
        """
        return_list = []
        if len(self.object_list) > 0:
            object_lower_list = []
            for object_name in self.object_list:
                if object_name.lower() not in object_lower_list:
                    object_lower_list.append(object_name.lower())
                    return_list.append([object_name])
        elif len(self.company_list) > 0 and len(self.product_list) > 0:
            company_lower_list = []
            product_lower_list = []
            for company_name in self.company_list:
                if company_name.lower() not in company_lower_list:
                    company_lower_list.append(company_name.lower())
                    for product_name in self.product_list:
                        if product_name.lower() not in product_lower_list:
                            product_lower_list.append(product_name.lower())
                            return_list.append([company_name, product_name])
        return return_list

    def get_extended_base_search_label_lists(self, search_label_lists: list) -> list:
        # the object list alone is too unspecific (too many results) - we add company and product
        c_p_tg_m_list = self.company_list + self.product_list + self.target_group_list + self.material_list
        if len(c_p_tg_m_list) == 0:
            return search_label_lists
        print('c_p_tg_list = {}'.format(c_p_tg_m_list))
        extended_label_lists = []
        for search_label_list in search_label_lists:
            for c_p in c_p_tg_m_list:
                list_new = list(search_label_list)
                list_new.append(c_p)
                extended_label_lists.append(list_new)
        return extended_label_lists

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

    def is_sale_ready_for_sale_table(self):
        return self._data_dict_obj.is_data_dict_ready_for_sale_table()

    def set_is_outlier(self, is_outlier: bool):
        self.set_value(SLDC.IS_OUTLIER, 1 if is_outlier else 0)

    def get_value_dict_for_worksheet(self, master_id='', master_title=''):
        if master_id == '':
            self.set_master_details(self.sale_id, self.title)
        else:
            self.set_master_details(master_id, master_title)
        worksheet_columns = SLDC.get_columns_for_excel()
        return {column: self._data_dict_obj.get(column) for column in worksheet_columns}

    def add_search_label(self, label: str, for_title: bool, is_label_head_text: bool):
        if self.__is_label_candidate_for_label_list__(label, for_title):
            if for_title:
                self.__add_label_to_label_list__(self._search_labels, label, is_label_head_text)
            else:
                self.__add_label_to_label_list__(self._search_labels_in_description, label, is_label_head_text)

    def add_entity_name_label(self, entity_name: str, entity_label: str):
        if entity_name not in self._entity_names:
            if self.sys_config.print_details:
                print('Entity is relevant for Tutti: {} {}'.format(entity_name, entity_label))
            self._entity_names.append(entity_name)
            self._entity_label_dict[entity_name] = entity_label
            entity_synonyms = SalesmanEntityHandler.get_synonyms_for_entity_name(entity_label, entity_name)
            if len(entity_synonyms) > 0:
                if self.sys_config.print_details:
                    print('Entity {} has synonyms {}'.format(entity_name, entity_synonyms))
                for entity_synonym in entity_synonyms:
                    if entity_synonym not in self._entity_names:
                        self._entity_names.append(entity_synonym)
                    self._entity_label_dict[entity_synonym] = entity_label

    def reduce_search_labels_by_entity_names(self):
        # entity names are the most important part - they are mandatory for the search - delete them from the
        # normal search labels
        if self.sys_config.print_details:
            print('')
        if len(self._entity_names) > 0:
            if self.sys_config.print_details:
                print('Search labels before entity name deletion: {}'.format(self._search_labels))
            for entity_name in self._entity_names:
                if entity_name in self._search_labels:
                    self._search_labels.remove(entity_name)
        if self.sys_config.print_details:
            print('Search labels: {}'.format(self._search_labels))

    def is_price_ready_for_update_in_tutti(self) -> bool:
        return self.price_new != self.price

    def complete_sale(self):
        nlp_doc_sale = self.__get_nlp_doc_for_sale__()
        self.__add_entity_name_labels_to_sale_from_doc__(nlp_doc_sale)
        self.__add_data_dict_entries_to_sale_from_doc__(nlp_doc_sale)
        self.__complete_date_dict_entries__()

    def print_sale_in_original_structure(self):
        visits_bookmarks, search_details = self.__get_visits_bookmarks_and_search_details_for_printing__()
        print('\n{}: ID: {}\nCategories: {} / {} / {} ({})\n{}\n{}\n{:.2f} CHF{}'.format(
            self.source, self.sale_id,
            self.region, self.product_category, self.product_sub_category, self.start_date,
            self.title, self.description, self.price, visits_bookmarks)
        )
        print('Is price total price: {}'.format(self.get_value(SLDC.IS_TOTAL_PRICE)))
        print('Single price: {}'.format(self.get_value(SLDC.PRICE_SINGLE)))
        print('Original price: {}'.format(self.get_value(SLDC.PRICE_ORIGINAL)))
        print('Size: {}'.format(self.get_value(SLDC.SIZE)))
        print('Number: {}'.format(self.get_value(SLDC.NUMBER)))
        print('New: {}/Used: {} - Conclusion: {}'.format(
            self.get_value(SLDC.IS_NEW), self.get_value(SLDC.IS_USED), self.get_value(SLDC.OBJECT_STATE)))
        if not self._my_offer:
            print('Is outlier: {}'.format(self.get_value(SLDC.IS_OUTLIER)))
        print('{}'.format(search_details))
        if self._my_offer:
            print('Entity names: {}'.format(self._entity_names))
            print('Entity_label_dict: {}'.format(self._entity_label_dict))
        else:
            print('Entity_names: {}'.format(self._entity_names))
            print('Entity_label_dict: {}'.format(self._entity_label_dict))

    def print_sale_details(self):
        visits_bookmarks, search_details = self.__get_visits_bookmarks_and_search_details_for_printing__()
        print('\n{}: ID: {}, Version: {}, Region: {}, Kategorie: {}, Bereich: {}, '
              'Date: {}, Title: {}, Description: {}, Price: {:.2f} CHF{}{}'.format(
            self.source, self.sale_id, self.version, self.region, self.product_category, self.product_sub_category,
            self.start_date, self.title, self.description, self.price, visits_bookmarks, search_details))
        print('Entity_names: {}'.format(self._entity_names))
        print('Entity_label_dict: {}'.format(self._entity_label_dict))
        """
        ID: 24840417, Location: Aargau, 5430, Date: 26.03.2019, Title: Lowa / Rufus III GTX / Gr. 37, 
        Description: Sehr gut erhalten. Tolles Profil., Price: 20.-, Visits: 10 Besuche, Bookmarks: 0 Merkliste
        """

    def __init_data_dict_entries__(self):
        self.set_value(SLDC.SOURCE, SLSRC.TUTTI_CH)
        self.set_value(SLDC.VERSION, 1)
        self.set_value(SLDC.SALE_STATE, SLST.OPEN)
        self.set_value(SLDC.PRODUCT_CATEGORY, '')
        self.set_value(SLDC.PRODUCT_SUB_CATEGORY, '')
        self.set_value(SLDC.DESCRIPTION, '')
        self.set_value(SLDC.PRICE, 0)
        self.set_value(SLDC.PRICE_SINGLE, 0)
        self.set_value(SLDC.PRICE_ORIGINAL, 0)
        self.set_value(SLDC.IS_OUTLIER, 0)
        self.set_value(SLDC.VISITS, 0)
        self.set_value(SLDC.BOOK_MARKS, 0)

    def __get_nlp_doc_for_sale__(self) -> DocExtended:
        nlp_doc_sale = DocExtended(self._salesman_nlp(self.title + ' ' + self.description))
        nlp_doc_sale.correct_single_price(self.price_single)
        return nlp_doc_sale

    def __add_entity_name_labels_to_sale_from_doc__(self, nlp_doc_sale: DocExtended):
        for ent in nlp_doc_sale.doc.ents:
            if EL.is_entity_label_tutti_relevant(ent.label_):
                self.add_entity_name_label(ent.text, ent.label_)
        self.reduce_search_labels_by_entity_names()

    def __add_data_dict_entries_to_sale_from_doc__(self, nlp_doc_sale: DocExtended):
        self.set_value(SLDC.OBJECT_STATE, nlp_doc_sale.object_state)
        self.set_value(SLDC.IS_TOTAL_PRICE, nlp_doc_sale.is_total_price)
        self.set_value(SLDC.PRICE_SINGLE, nlp_doc_sale.price_single)
        self.set_value(SLDC.PRICE_ORIGINAL, nlp_doc_sale.price_original)
        self.set_value(SLDC.NUMBER, nlp_doc_sale.number)
        self.set_value(SLDC.SIZE, nlp_doc_sale.size)
        self.set_value(SLDC.IS_NEW, nlp_doc_sale.is_new)
        self.set_value(SLDC.IS_LIKE_NEW, nlp_doc_sale.is_like_new)
        self.set_value(SLDC.IS_USED, nlp_doc_sale.is_used)
        self.set_value(SLDC.PROPERTY_DICT, nlp_doc_sale.get_properties_for_data_dict())

    def __complete_date_dict_entries__(self):
        self.set_value(SLDC.VERSION, self.sys_config.access_layer_sale.get_next_version_for_sale_id(self.sale_id))
        self.set_value(SLDC.MASTER_ID, self.sale_id)  # default - will be overwritten...
        self.set_value(SLDC.MASTER_TITLE, self.title) # default - will be overwritten...
        self.set_value(SLDC.PRICE_SINGLE, self.__get_price_single__())
        self.set_value(SLDC.MATERIAL, ', '.join(self.material_list))
        self.set_value(SLDC.SEARCH_LABELS, ', '.join(self._search_labels))
        self.set_value(SLDC.ENTITY_LABELS, ', '.join(self._entity_names))
        label_list = ['{} ({})'.format(values, self.entity_label_dict[values]) for values in self.entity_label_dict]
        self.set_value(SLDC.ENTITY_LABELS_DICT, ', '.join(label_list))
        self.set_value(SLDC.FOUND_BY_LABELS, '' if self._found_by_labels is None else self._found_by_labels)
        self.set_value(SLDC.LAST_CHECK_DATE, MyDate.get_date_str_from_datetime())
        self.set_value(SLDC.COMMENT, '1. load' if self.get_value(SLDC.VERSION) == 1 else 'some changes')
        self.set_value(SLDC.PRINT_CATEGORY, '')

    def __get_price_single__(self):
        price, number = self.get_value(SLDC.PRICE), self.get_value(SLDC.NUMBER)
        price_single = price
        if self.get_value(SLDC.IS_TOTAL_PRICE) and number > 0:
            price_single = int(price / number)
        return price_single

    def __get_visits_bookmarks_and_search_details_for_printing__(self):
        if self._my_offer:
            visits_bookmarks = ', {} Besuche, {} Merkliste'.format(
                self.get_value(SLDC.VISITS), self.get_value(SLDC.BOOK_MARKS))
            search_details = 'Search labels: {}'.format(self._search_labels)
        else:
            visits_bookmarks = ''
            search_details = 'Found by: {}'.format('Sale_ID' if self._found_by_labels == '' else self._found_by_labels)
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
                self.__print_new_old_label_behavior__(
                    'new label {} covers old label {}=> keep old label'.format(label, label_in_list))
                return
            elif label_in_list_lower.find(label_lower) >= 0:
                # the new label is more general (shorter) => we replace the old one
                self.__print_new_old_label_behavior__(
                    'new label {} is in old label {}=> replace old label'.format(label, label_in_list))
                label_list[idx] = label
                return
        label_list.append(label)

    def __print_new_old_label_behavior__(self, behavior: str):
        if self.sys_config.print_details:
            print(behavior)