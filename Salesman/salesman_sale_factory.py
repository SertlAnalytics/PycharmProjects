"""
Description: This module contains the factory class for sales
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-08
"""

from sertl_analytics.mydates import MyDate
from sertl_analytics.my_text import MyText
from sertl_analytics.constants.salesman_constants import SLDC, PRCAT, SLSRC
from salesman_tutti.tutti_constants import EL
from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_system_configuration import SystemConfiguration
from salesman_nlp.salesman_doc_extended import DocExtended
from salesman_tutti.tutti_url_factory import TuttiUrlFactory, OnlineSearchApi
from salesman_sale import SalesmanSale
import math
from salesman_web_parser import SalesmanWebParser


class SalesmanSaleFactory:
    def __init__(self, sys_config: SystemConfiguration, salesman_spacy: SalesmanSpacy):
        self.sys_config = sys_config
        self._salesman_spacy = salesman_spacy
        self._nlp_sale = self._salesman_spacy.nlp
        self._web_parser = SalesmanWebParser(self.sys_config, self._salesman_spacy)

    @property
    def sale_factory_source(self) -> str:
        return SLSRC.TUTTI_CH

    @staticmethod
    def are_sales_identical(sale_01: SalesmanSale, sale_02: SalesmanSale) -> bool:
        check_col_list = [SLDC.TITLE, SLDC.DESCRIPTION, SLDC.PRICE_SINGLE]
        for col in check_col_list:
            if sale_01.get_value(col) != sale_02.get_value(col):
                print('Not identical: {}: {} and {}'.format(col, sale_01.get_value(col), sale_02.get_value(col)))
                return False
        return True

    def init_url_factory_by_online_search_api(self, api: OnlineSearchApi):
        self._web_parser.init_url_factory_by_online_search_api(api)

    def get_search_string_found_number_dict(self, search_label_lists: list) -> dict:
        return self._web_parser.get_search_string_found_number_dict(search_label_lists)

    def get_sale_by_online_search_string(self, search_string: str, with_category_number_check=True)->SalesmanSale:
        sale_data_dict = {
            SLDC.SALE_ID: str(MyDate.time_stamp_now()),
            SLDC.LOCATION: 'online',
            SLDC.START_DATE: MyDate.get_date_as_string_from_date_time(),
            SLDC.TITLE: search_string,
        }
        sale = self.__get_sale_by_data_dict__(sale_data_dict)
        if with_category_number_check:
            sale.set_product_category_value_list(
                self._web_parser.get_product_category_value_list_for_search_labels(sale.get_search_label_lists()))
        return sale

    def get_sale_via_request_by_sale_id(self, sale_id: str) -> SalesmanSale:
        sale_data_dict = self._web_parser.get_sale_data_dict_for_sale_id(sale_id)
        if len(sale_data_dict) == 0:
            print('\nWARNING: No active sale found on {} for id={}'.format(self.sale_factory_source, sale_id))
        else:
            return self.__get_sale_by_data_dict__(sale_data_dict)

    def get_sales_by_search_label_list(self, search_label_list: list) -> list:
        return_sales = []
        sales_data_dict = self._web_parser.get_sales_data_dict_for_search_label_list(search_label_list)
        for sale_id, sale_data_dict in sales_data_dict.items():
            sale = self.__get_sale_by_data_dict__(sale_data_dict, ', '.join(search_label_list))
            return_sales.append(sale)
        return return_sales

    def adjust_category_sub_category_for_url_factory(self, category_value: str, sub_category_value: str):
        self._web_parser.adjust_category_sub_category(category_value, sub_category_value)

    def get_sale_by_browser_sale_element(self, sale_element, search_labels):
        sale_data_dict = self._web_parser.get_sale_data_dict_by_browser_sale_element(sale_element)
        return self.__get_sale_by_data_dict__(sale_data_dict, search_labels)

    def get_sale_by_file_row(self, row):
        sale_data_dict = {col: row[col] for col in row.index}
        sale_data_dict[SLDC.LOCATION] = 'virtual'
        sale_data_dict[SLDC.START_DATE] = MyDate.get_date_as_string_from_date_time()
        return self.__get_sale_by_data_dict__(sale_data_dict)

    def get_sale_by_db_row(self, row):
        sale_data_dict = {col: row[col] for col in row.index}
        return self.__get_sale_by_data_dict__(sale_data_dict)

    def __get_sale_by_data_dict__(self, sale_data_dict: dict, search_labels=''):
        sale = self.__get_sale_initialized__(sale_data_dict[SLDC.SALE_ID], search_labels)
        sale.add_value_dict(sale_data_dict)
        nlp_doc_sale = self.__get_nlp_doc_for_sale__(sale)
        self.__add_entity_name_labels_to_sale_from_doc__(sale, nlp_doc_sale)
        self.__add_data_dict_entries_to_sale_from_doc__(sale, nlp_doc_sale)
        sale.complete_date_dict_entries()
        return sale

    def __get_sale_initialized__(self, sale_id: str, found_by_labels=''):
        sale = SalesmanSale(self._salesman_spacy, self.sys_config, found_by_labels=found_by_labels)
        sale.set_value(SLDC.SOURCE, self.sale_factory_source)
        sale.set_value(SLDC.SALE_ID, sale_id)
        return sale

    def __get_nlp_doc_for_sale__(self, sale: SalesmanSale) -> DocExtended:
        nlp_doc_sale = DocExtended(self._nlp_sale(sale.title + ' ' + sale.description))
        nlp_doc_sale.correct_single_price(sale.price_single)
        return nlp_doc_sale

    @staticmethod
    def __add_entity_name_labels_to_sale_from_doc__(sale: SalesmanSale, nlp_doc_sale: DocExtended):
        for ent in nlp_doc_sale.doc.ents:
            if EL.is_entity_label_tutti_relevant(ent.label_):
                sale.add_entity_name_label(ent.text, ent.label_)
        sale.reduce_search_labels_by_entity_names()

    @staticmethod
    def __add_data_dict_entries_to_sale_from_doc__(sale: SalesmanSale, nlp_doc_sale: DocExtended):
        sale.set_value(SLDC.OBJECT_STATE, nlp_doc_sale.object_state)
        sale.set_value(SLDC.IS_TOTAL_PRICE, nlp_doc_sale.is_total_price)
        sale.set_value(SLDC.PRICE_SINGLE, nlp_doc_sale.price_single)
        sale.set_value(SLDC.PRICE_ORIGINAL, nlp_doc_sale.price_original)
        sale.set_value(SLDC.NUMBER, nlp_doc_sale.number)
        sale.set_value(SLDC.SIZE, nlp_doc_sale.size)
        sale.set_value(SLDC.IS_NEW, nlp_doc_sale.is_new)
        sale.set_value(SLDC.IS_LIKE_NEW, nlp_doc_sale.is_like_new)
        sale.set_value(SLDC.IS_USED, nlp_doc_sale.is_used)
        sale.set_value(SLDC.PROPERTY_DICT, nlp_doc_sale.get_properties_for_data_dict())

