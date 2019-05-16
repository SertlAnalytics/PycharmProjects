"""
Description: This module contains the factory class for sale entity
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-08
"""

from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_system_configuration import SystemConfiguration
from salesman_tutti.tutti_url_factory import SalesmanSearchApi
from salesman_sale import SalesmanSale
from salesman_web_parser import SalesmanWebParser
from salesman_sale_checks import SaleIdenticalCheck, SaleSimilarityCheck


class SalesmanSaleFactory:
    def __init__(self, sys_config: SystemConfiguration, salesman_spacy: SalesmanSpacy):
        self.sys_config = sys_config
        self._salesman_spacy = salesman_spacy
        self._web_parser = SalesmanWebParser(self.sys_config, self._salesman_spacy)
        self._online_search_api = None

    @property
    def sale_factory_source(self) -> str:
        return SLSRC.TUTTI_CH

    def are_sales_similar_by_sale_id(self, sale_id_01: str, sale_id_02: str) -> bool:
        sale_01 = self.get_sale_via_request_by_sale_id(sale_id_01)
        sale_02 = self.get_sale_via_request_by_sale_id(sale_id_02)
        return self.are_sales_similar(sale_01, sale_02, True)

    @staticmethod
    def are_sales_similar(source_sale: SalesmanSale, other_sale: SalesmanSale, with_info=True) -> bool:
        check = SaleSimilarityCheck(source_sale, other_sale)
        if with_info and not check.are_sales_similar:
            print('Not similar {} <-> {}: {} <--> {} '.format(
                source_sale.sale_id, other_sale.sale_id,
                source_sale.get_value(SLDC.ENTITY_LABELS_DICT),
                other_sale.get_value(SLDC.ENTITY_LABELS_DICT)))
        return check.are_sales_similar

    def adjust_by_search_api(self, api: SalesmanSearchApi):
        self._web_parser.adjust_by_search_api(api)

    def get_search_string_found_number_dict(self, search_label_lists: list) -> dict:
        return self._web_parser.get_search_string_found_number_dict(search_label_lists)

    def get_sale_from_db_by_sale_id(self, sale_id: str) -> SalesmanSale:
        if self.sys_config.access_layer_sale.is_sale_with_id_available(sale_id):
            df = self.sys_config.access_layer_sale.get_sale_by_id(sale_id)
            return self.get_sale_by_db_row(df.iloc[0])

    def get_sale_from_db_by_row_id(self, row_id: int) -> SalesmanSale:
        df = self.sys_config.access_layer_sale.get_sale_by_row_id(row_id)
        return self.get_sale_by_db_row(df.iloc[0])

    def get_sale_from_file_by_row_number(self, row_number: int) -> SalesmanSale:
        row = self.sys_config.access_layer_file.get_row(row_number)
        return self.get_sale_by_file_row(row)

    def fill_search_api_list_by_found_numbers(self, api_list: list, search_label_lists: list):
        self._web_parser.fill_search_api_list_by_found_numbers(api_list, search_label_lists)

    def get_sale_by_search_api(self, api: SalesmanSearchApi) -> SalesmanSale:
        sale_data_dict = self.__get_sales_data_dict_for_online_search_api__(api)
        return self.__get_sale_by_data_dict__(sale_data_dict)

    def get_sale_via_request_by_sale_id(self, sale_id: str) -> SalesmanSale:
        sale_data_dict = self._web_parser.get_sale_data_dict_for_sale_id(sale_id)
        # print('sale_data_dict={}'.format(sale_data_dict))
        if len(sale_data_dict) == 0:
            print('\nWARNING: No active sale found on {} for id={}'.format(self.sale_factory_source, sale_id))
        else:
            return self.__get_sale_by_data_dict__(sale_data_dict)

    def can_sale_be_accessed_via_request_by_sale_id(self, sale_id: str) -> bool:
        sale_data_dict = self._web_parser.get_sale_data_dict_for_sale_id(sale_id)
        return len(sale_data_dict) > 0

    def get_sales_by_search_label_list(self, search_label_list: list) -> list:
        return_sales = []
        sales_data_dict = self._web_parser.get_sales_data_dict_for_search_label_list(search_label_list)
        for sale_id, sale_data_dict in sales_data_dict.items():
            sale = self.__get_sale_by_data_dict__(sale_data_dict, ', '.join(search_label_list))
            return_sales.append(sale)
        return return_sales

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
        # sale_data_dict[SLDC.DESCRIPTION] = ''
        return self.__get_sale_by_data_dict__(sale_data_dict, is_from_db=True)

    def __get_sales_data_dict_for_online_search_api__(self, api):
        region = self.sys_config.region_categorizer.get_category_for_value(api.region_value)
        # print('__get_sales_data_dict_for_online_search_api__: region={}'.format(region))
        product_category, product_sub_category = '', ''
        if api.category_value != '':
            product_category = self.sys_config.product_categorizer.get_category_for_value(api.category_value)
            product_sub_category = self.sys_config.product_categorizer.get_sub_category_for_value(
                product_category, api.sub_category_value)
        sale_data_dict = {
            SLDC.SALE_ID: str(MyDate.time_stamp_now()),
            SLDC.LOCATION: 'online',
            SLDC.START_DATE: MyDate.get_date_as_string_from_date_time(),
            SLDC.TITLE: api.search_string,
            SLDC.REGION: region,
            SLDC.PRODUCT_CATEGORY: product_category,
            SLDC.PRODUCT_SUB_CATEGORY: product_sub_category,
        }
        # print('sale_data_dict={}'.format(sale_data_dict))
        return sale_data_dict

    def __get_sale_by_data_dict__(self, sale_data_dict: dict, search_labels='', is_from_db=False):
        sale = self.__get_sale_initialized__(sale_data_dict[SLDC.SALE_ID], search_labels)
        sale.add_value_dict(sale_data_dict)
        sale.complete_sale(is_from_db)
        return sale

    def __get_sale_initialized__(self, sale_id: str, found_by_labels=''):
        sale = SalesmanSale(self._salesman_spacy, self.sys_config, found_by_labels=found_by_labels)
        sale.set_value(SLDC.SOURCE, self.sale_factory_source)
        sale.set_value(SLDC.SALE_ID, sale_id)
        return sale



