"""
Description: This module contains the information for an offer for Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.mymath import MyMath
from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.salesman_constants import SLDC, SLST, OBJST, SLSRC, PRCAT, OBJPROP
from salesman_tutti.tutti_constants import SLCLS, POS, EL, SLSCLS
from spacy.tokens import Doc
from entities.tutti_named_entity import TuttiEntityHandler
from lxml.html import HtmlElement
from sertl_analytics.myhtml import MyHtmlElement
from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_data_dictionary import SalesmanDataDictionary
from salesman_system_configuration import SystemConfiguration
from salesman_tutti.tutti_categorizer import ProductCategorizer, RegionCategorizer


class TuttiSale:
    def __init__(self, spacy: SalesmanSpacy, sys_config: SystemConfiguration, found_by_labels=None):
        self.sys_config = sys_config
        self.data_dict_obj = SalesmanDataDictionary(self.sys_config)
        self._spacy = spacy
        self._nlp = spacy.nlp
        self._region_categorizer = RegionCategorizer()
        self._product_categorizer = ProductCategorizer()
        self._my_offer = found_by_labels is None
        self._found_by_labels = found_by_labels

        self._source = SLSRC.TUTTI_CH
        self._region = ''
        self._product_category = ''
        self._product_sub_category = ''
        self._href = ''
        self._sale_id = ''
        self._version = 1
        self._location = ''
        self._date_str = ''
        self._title = ''
        self._description = ''
        self._size = ''
        self._age = ''
        self._number = 1
        self._price = 0
        self._price_new = 0
        self._price_original = 0
        self._price_single = 0
        self._visits = 0
        self._bookmarks = 0

        self._is_total_price = False
        self._is_new = False
        self._is_like_new = False
        self._is_used = False
        self._is_cover_available = False
        self._is_outlier = 0
        self._search_labels = []
        self._entity_label_dict = {}  # contains entities with {value: label, value: label}
        self._property_dict = {}  # contains all properties for this object (details).
        self._entity_names = []
        self._search_labels_in_description = []
        self._search_labels_in_head_text = []

    @property
    def domain(self):
        return 'https://www.tutti.ch'

    @property
    def source(self):
        return '{} ({})'.format(self.data_dict_obj.get(SLDC.SOURCE), 'My offer' if self._my_offer else 'Similar offer')

    @property
    def sale_id(self):
        return self._sale_id

    @sale_id.setter
    def sale_id(self, value):
        self.data_dict_obj.add(SLDC.SALE_ID, value)
        self._sale_id = value

    @property
    def price_new(self):
        return self._price_new

    @price_new.setter
    def price_new(self, value):
        self._price_new = value

    @property
    def title(self):
        return self._title

    @property
    def key(self):
        return '{}_{}'.format(self._sale_id, self._title)

    @property
    def price_single(self):
        return self._price_single

    @property
    def sale_state(self):
        return SLST.OPEN

    @property
    def location(self):
        return self._location

    @property
    def object_state(self):
        if self._is_like_new:
            return OBJST.LIKE_NEW
        elif self._is_used:
            return OBJST.USED
        else:
            return OBJST.NEW if self._is_new else OBJST.NOT_QUALIFIED

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

    def init_by_file_row(self, row):
        self._sale_id = row[SLDC.SALE_ID]
        self.add_location_text('virtual')
        self.add_date_text(MyDate.get_date_as_string_from_date_time())
        self.add_title_text(row[SLDC.TITLE])
        self.add_description_text(row[SLDC.DESCRIPTION])
        self.add_price(str(row[SLDC.PRICE]))
        self.__add_search_labels__()
        self.__process_doc_extensions__()
        self.__add_data_dict_entries__()

    def init_by_database_row(self, row):
        # print('init_by_database_row: {}'.format(row))
        for col in row.index:
            self.data_dict_obj.add(col, row[col])
        self.__init_variables_by_data_dict__()

    def __init_variables_by_data_dict__(self):
        self._href = self.data_dict_obj.get(SLDC.HREF)
        self._sale_id = self.data_dict_obj.get(SLDC.SALE_ID)
        self._version = self.data_dict_obj.get(SLDC.VERSION)
        self._location = self.data_dict_obj.get(SLDC.LOCATION)
        self._date_str = self.data_dict_obj.get(SLDC.START_DATE)
        self._title = self.data_dict_obj.get(SLDC.TITLE)
        self._description = self.data_dict_obj.get(SLDC.DESCRIPTION)
        self._size = self.data_dict_obj.get(SLDC.SIZE)
        self._number = self.data_dict_obj.get(SLDC.NUMBER)
        self._price = self.data_dict_obj.get(SLDC.PRICE)
        self._price_original = self.data_dict_obj.get(SLDC.PRICE_ORIGINAL)
        self._price_single = self.data_dict_obj.get(SLDC.PRICE_SINGLE)
        self._visits = self.data_dict_obj.get(SLDC.VISITS)
        self._bookmarks = self.data_dict_obj.get(SLDC.BOOK_MARKS)

    def is_identical(self, other_sale) -> bool:
        check_col_list = [SLDC.TITLE, SLDC.DESCRIPTION, SLDC.PRICE_SINGLE]
        for col in check_col_list:
            if self.data_dict_obj.get(col) != other_sale.data_dict_obj.get(col):
                print('Not identical: {}: {} and {}'.format(col, self.data_dict_obj.get(col), other_sale.data_dict_obj.get(col)))
                return False
        return True

    def init_by_online_input(self, search_input: str):
        self._sale_id = MyDate.time_stamp_now()
        self.add_location_text('online')
        self.add_date_text(MyDate.get_date_as_string_from_date_time())
        self.add_title_text(search_input)
        self.add_description_text('')
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
        self.__add_search_labels__()
        self.__process_doc_extensions__()
        self.__add_data_dict_entries__()

    def init_by_html_element_for_single_sale(self, product_categories: list, html_element: HtmlElement, url: str):
        my_html_element = MyHtmlElement(html_element)
        self.add_href(url)
        location_html_element = my_html_element.get_html_element_for_sub_class(SLSCLS.LOCATION_CLASS)
        self.add_location_text(location_html_element.get_text_for_sub_class(SLSCLS.LOCATION_SUB_CLASS))
        date_html_element = my_html_element.get_html_element_for_sub_class(SLSCLS.DATE_CLASS)
        category_off_set = 1 if len(product_categories) == 3 else 2
        self._region = product_categories[category_off_set-1].text_content()
        self._product_category = product_categories[category_off_set].text_content()
        self._product_sub_category = product_categories[category_off_set+1].text_content()
        self.add_date_text(date_html_element.get_text_for_sub_class(SLSCLS.DATE_SUB_CLASS))
        self.add_title_text(my_html_element.get_text_for_sub_class(SLSCLS.TITLE))
        self.add_description_text(my_html_element.get_text_for_sub_class(SLSCLS.DESCRIPTION))
        self.add_price(my_html_element.get_text_for_sub_class(SLSCLS.PRICE))
        self.__add_search_labels__()
        self.__process_doc_extensions__()
        self.__add_data_dict_entries__()

    def set_master_details(self, master_id: str, master_title: str):
        self.data_dict_obj.add(SLDC.MASTER_ID, master_id)
        self.data_dict_obj.add(SLDC.MASTER_TITLE, master_title)

    def is_any_term_in_list_in_title_or_description(self, term_list: str):
        return self.__is_any_term_in_list_in_text__(term_list, self._title.lower() + self._description.lower())

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
        return self.__is_any_term_in_list_in_text__(term_list, self._title.lower())

    def set_source(self, source: str):
        self._source = source
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
        if self.sys_config.print_details:
            print('\nDoc for {}: {}'.format('title' if for_title else 'description', doc.text))
        # self.__add_to_search_label__(doc, for_title)
        for ent in doc.ents:
            if EL.is_entity_label_tutti_relevant(ent.label_):
                self.add_entity_name_label(ent.text, ent.label_)

    def __add_to_search_label__(self, doc, for_title: bool):
        token_text_list = []
        token_head_text_list = []
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

    def __process_doc_extensions__(self):
        doc_title_description = self._nlp(self._title + ' ' + self._description)
        self._price_original = doc_title_description._.original_price
        self._size = doc_title_description._.size
        self._age = doc_title_description._.age
        self._number = doc_title_description._.number
        self._is_new = doc_title_description._.is_new
        self._is_like_new = doc_title_description._.is_like_new
        self._is_cover_available = doc_title_description._.is_cover_available
        self._is_used = doc_title_description._.is_used
        single_price = doc_title_description._.single_price
        self._price_single = self._price if single_price == 0 else single_price
        self._is_total_price = doc_title_description._.is_total_price
        if self._is_total_price and self._number != 0:
            self._price_single = int(self._price/self._number)

    def add_href(self, href: str):
        self._href = '{}{}'.format(self.domain, href) if href.find('https') < 0 else href
        href_splits = self._href.split('/')
        self._region, self._product_category, self._product_sub_category = self.__get_product_categories__(href_splits)
        self._sale_id = href_splits[-1]

    def __get_product_categories__(self, href_splits: list):
        region, category, sub_category = '', '', ''
        if len(href_splits) > 6:
            category_offset = 6 if len(href_splits) == 10 else 7
            region = self._region_categorizer.get_category_for_value(href_splits[category_offset-1])
            category = self._product_categorizer.get_category_for_value(href_splits[category_offset])
            sub_category_value = href_splits[category_offset+1]
            sub_category = self._product_categorizer.get_sub_category_for_value(category, sub_category_value)
        return region, category, sub_category

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
        self._price_original = self._price

    def add_visits_text(self, input_str: str):
        self._visits = int(input_str.split(' ')[0])

    def add_bookmarks_text(self, input_str: str):
        self._bookmarks = int(input_str.split(' ')[0])

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
        return self.data_dict_obj.is_data_dict_ready_for_sale_table()

    def set_is_outlier(self, value: bool):
        self._is_outlier = value
        self.data_dict_obj.add(SLDC.IS_OUTLIER, 1 if self._is_outlier else 0)

    def get_value_dict_for_worksheet(self, master_id='', master_title=''):
        if master_id == '':
            self.set_master_details(self._sale_id, self._title)
        else:
            self.set_master_details(master_id, master_title)
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
            if self.sys_config.print_details:
                print('Entity is relevant for Tutti: {} {}'.format(entity_name, entity_label))
            self._entity_names.append(entity_name)
            self._entity_label_dict[entity_name] = entity_label
            entity_synonyms = TuttiEntityHandler.get_synonyms_for_entity_name(entity_label, entity_name)
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
        return self._price_new != self._price

    def print_sale_in_original_structure(self):
        visits_bookmarks, search_details = self.__get_visits_bookmarks_and_search_details_for_printing__()
        print('\n{}: ID: {}\nCategories: {} / {} / {} ({})\n{}\n{}\n{:.2f} CHF{}'.format(
            self.source, self._sale_id,
            self._region, self._product_category, self._product_sub_category, self._date_str,
            self._title, self._description, self._price, visits_bookmarks)
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
            print('Entity_label_dict: {}'.format(self._entity_label_dict))
        else:
            print('Entity_names: {}'.format(self._entity_names))
            print('Entity_label_dict: {}'.format(self._entity_label_dict))

    def print_sale_details(self):
        visits_bookmarks, search_details = self.__get_visits_bookmarks_and_search_details_for_printing__()
        print('\n{}: ID: {}, Version: {}, Region: {}, Kategorie: {}, Bereich: {}, '
              'Date: {}, Title: {}, Description: {}, Price: {:.2f} CHF{}{}'.format(
            self.source, self._sale_id, self._version,
            self._region, self._product_category, self._product_sub_category,
            self._date_str, self._title, self._description, self._price, visits_bookmarks, search_details))
        print('Entity_names: {}'.format(self._entity_names))
        print('Entity_label_dict: {}'.format(self._entity_label_dict))
        """
        ID: 24840417, Location: Aargau, 5430, Date: 26.03.2019, Title: Lowa / Rufus III GTX / Gr. 37, 
        Description: Sehr gut erhalten. Tolles Profil., Price: 20.-, Visits: 10 Besuche, Bookmarks: 0 Merkliste
        """

    def __add_data_dict_entries__(self):
        self.data_dict_obj.add(SLDC.SALE_ID, self._sale_id)
        self.data_dict_obj.add(SLDC.VERSION,
                               self.sys_config.access_layer_sale.get_next_version_for_sale_id(self._sale_id))
        self.data_dict_obj.add(SLDC.MASTER_ID, self._sale_id)  # default - will be overwritten...
        self.data_dict_obj.add(SLDC.MASTER_TITLE, self._title) # default - will be overwritten...
        self.data_dict_obj.add(SLDC.SALE_STATE, self.sale_state)
        self.data_dict_obj.add(SLDC.SOURCE, self._source)  # default - will be overwritten...
        self.data_dict_obj.add(SLDC.REGION, self._region)
        self.data_dict_obj.add(SLDC.PRODUCT_CATEGORY, self._product_category)
        self.data_dict_obj.add(SLDC.PRODUCT_SUB_CATEGORY, self._product_sub_category)
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
        self.data_dict_obj.add(SLDC.MATERIAL, ', '.join(self.material_list))
        self.data_dict_obj.add(SLDC.IS_NEW, self._is_new)
        self.data_dict_obj.add(SLDC.IS_LIKE_NEW, self._is_like_new)
        self.data_dict_obj.add(SLDC.IS_USED, self._is_used)
        self.data_dict_obj.add(SLDC.VISITS, self._visits)
        self.data_dict_obj.add(SLDC.BOOK_MARKS, self._bookmarks)
        self.data_dict_obj.add(SLDC.SEARCH_LABELS, ', '.join(self._search_labels))
        self.data_dict_obj.add(SLDC.ENTITY_LABELS, ', '.join(self._entity_names))
        label_list = ['{} ({})'.format(values, self.entity_label_dict[values]) for values in self.entity_label_dict]
        self.data_dict_obj.add(SLDC.ENTITY_LABELS_DICT, ', '.join(label_list))
        self.__add_property_dict_to_data_dict_obj__()
        self.data_dict_obj.add(SLDC.FOUND_BY_LABELS,
                               '' if self._found_by_labels is None else ','.join(self._found_by_labels))
        self.data_dict_obj.add(SLDC.HREF, self._href)
        self.data_dict_obj.add(SLDC.LAST_CHECK_DATE, MyDate.get_date_str_from_datetime())
        self.data_dict_obj.add(SLDC.COMMENT, '1. load')
        self.data_dict_obj.add(SLDC.PRINT_CATEGORY, '')

    def __add_property_dict_to_data_dict_obj__(self):
        if self._is_cover_available:
            self._property_dict[OBJPROP.ORIGINAL_COVER] = 'Yes'
        if self._size != '':
            self._property_dict[OBJPROP.SIZE] = self._size
        if self._age != '':
            self._property_dict[OBJPROP.AGE] = self._age
        property_list = ['{}: {}'.format(prop, self._property_dict[prop]) for prop in self._property_dict]
        self.data_dict_obj.add(SLDC.PROPERTY_DICT, ', '.join(property_list))

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