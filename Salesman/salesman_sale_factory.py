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
from salesman_tutti.tutti_url_factory import OnlineSearchApi
from salesman_sale import SalesmanSale
from salesman_web_parser import SalesmanWebParser


class SalesmanSaleFactory:
    def __init__(self, sys_config: SystemConfiguration, salesman_spacy: SalesmanSpacy):
        self.sys_config = sys_config
        self._salesman_spacy = salesman_spacy
        self._web_parser = SalesmanWebParser(self.sys_config, self._salesman_spacy)
        self._online_search_api = None

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

    def adjust_by_online_search_api(self, api: OnlineSearchApi):
        self._web_parser.adjust_by_online_search_api(api)

    def get_search_string_found_number_dict(self, search_label_lists: list) -> dict:
        return self._web_parser.get_search_string_found_number_dict(search_label_lists)

    def get_online_search_api_index_number_dict(self, api_list: list, search_label_lists: list):
        return self._web_parser.get_online_search_api_index_number_dict(api_list, search_label_lists)

    def get_sale_by_online_search_api(self, api: OnlineSearchApi) -> SalesmanSale:
        sale_data_dict = self.__get_sales_data_dict_for_online_search_api__(api)
        return self.__get_sale_by_data_dict__(sale_data_dict)

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

    def __get_sales_data_dict_for_online_search_api__(self, api):
        region = self.sys_config.region_categorizer.get_category_for_value(api.region_value)
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

    def __get_sale_by_data_dict__(self, sale_data_dict: dict, search_labels=''):
        sale = self.__get_sale_initialized__(sale_data_dict[SLDC.SALE_ID], search_labels)
        sale.add_value_dict(sale_data_dict)
        sale.complete_sale()
        return sale

    def __get_sale_initialized__(self, sale_id: str, found_by_labels=''):
        sale = SalesmanSale(self._salesman_spacy, self.sys_config, found_by_labels=found_by_labels)
        sale.set_value(SLDC.SOURCE, self.sale_factory_source)
        sale.set_value(SLDC.SALE_ID, sale_id)
        return sale


