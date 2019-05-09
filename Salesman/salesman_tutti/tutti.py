"""
Description: This module is the base class for our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.constants.salesman_constants import SLDC, SLSRC, PRCAT
from sertl_analytics.my_text import MyText
from sertl_analytics.my_excel import MyExcel
from salesman_database.access_layer.access_layer_sale import AccessLayer4Sale
from calculation.outlier import Outlier
from salesman_tutti.tutti_browser import MyUrlBrowser4Tutti
from lxml import html
from salesman_sale import SalesmanSale
from spacy import displacy
from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_tutti.tutti_constants import SCLS, SLSCLS
import pandas as pd
import requests
from time import sleep
from salesman_system_configuration import SystemConfiguration
from printing.sale_printing import SalesmanPrint
import math
from salesman_web_parser import SalesmanWebParser
from salesman_tutti.tutti_url_factory import OnlineSearchApi
from salesman_sale_factory import SalesmanSaleFactory


class Tutti:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self._printing = SalesmanPrint(SLDC.get_columns_for_sales_printing())
        self._my_sales_source = SLSRC.TUTTI_CH
        self._excel = self.__get_excel__()
        self._salesman_spacy = SalesmanSpacy(load_sm=self.sys_config.load_sm) if self.sys_config.with_nlp else None
        self._sale_factory = SalesmanSaleFactory(self.sys_config, self._salesman_spacy)
        self._browser = None
        self._access_layer = AccessLayer4Sale(self.sys_config.db)
        self._search_label_lists = []
        self._current_source_sale = None
        self._current_similar_sales = []  # will get the results for the search for ONE source

    @property
    def nlp(self):
        return None if self._salesman_spacy is None else self._salesman_spacy.nlp

    @property
    def printing(self):
        return self._printing

    @property
    def current_source_sale(self):
        return self._current_source_sale

    @property
    def browser(self) -> MyUrlBrowser4Tutti:
        if self._browser is None:
            self._browser = MyUrlBrowser4Tutti(self.sys_config, self._salesman_spacy, self._sale_factory)
            self._browser.enter_and_submit_credentials()
        return self._browser

    @property
    def excel_file_path(self):
        return self.sys_config.file_handler.get_file_path_for_file(
            '{}_{}'.format(self._my_sales_source, self.sys_config.sales_result_file_name))

    @property
    def search_label_lists(self) -> list:
        return self._search_label_lists

    def close_excel(self):
        if self.sys_config.write_to_excel:
            self._excel.close()

    def search_on_tutti(self, title: str, description: str):
        sale = self._sale_factory.get_sale_by_online_search_string(title + ' ' + description)
        self.__check_sales_against_similar_sales_on_tutti__([sale])

    def check_my_nth_sale_against_similar_sales(self, number=1):
        sale = self.browser.get_my_nth_sale_from_tutti(number)
        self.__check_sales_against_similar_sales_on_tutti__([sale])

    def check_sale_on_tutti_against_similar_sales_by_sale_id(self, sale_id: str):
        sale = self.get_sale_from_tutti_by_sale_id(sale_id)
        self.__check_sales_against_similar_sales_on_tutti__([sale])

    def check_sale_in_db_against_similar_sales_by_sale_id(self, sale_id: str):
        sale = self.get_sale_from_db_by_sale_id(sale_id)
        self.__check_sales_against_similar_sales_on_tutti__([sale])

    def check_my_nth_virtual_sale_against_similar_sales(self, number=1):
        source_sale_list = self.__get_my_virtual_sales__(number)
        self.__check_sales_against_similar_sales_on_tutti__(source_sale_list)

    def __check_sales_against_similar_sales_on_tutti__(self, source_sale_list: list):
        if len(source_sale_list) == 0 or source_sale_list[0] is None:
            return
        for source_sale in source_sale_list:
            self.__check_sale_against_similar_sales_on_tutti__(source_sale)

    def __check_sale_against_similar_sales_on_tutti__(self, sale: SalesmanSale):
        if self.sys_config.print_details:
            sale.print_sale_in_original_structure()
        self._current_source_sale = sale
        self._current_similar_sales = self.__get_similar_sales_for_sale__(self._current_source_sale)
        self.__process_my_sale_and_similar_sales__()

    def print_details_for_tutti_sale_id(self, sale_id: str):
        self.sys_config.write_to_excel = False
        sale = self.get_sale_from_tutti_by_sale_id(sale_id)
        if sale is None:
            print('Cannot find {}'.format(sale_id))
        else:
            sale.print_sale_details()
            sale.print_sale_in_original_structure()

    def check_sale_against_sale_in_db_by_sale_id(self, sale_id: str):
        sale = self.get_sale_from_tutti_by_sale_id(sale_id)
        if sale is None:
            if self.sys_config.print_details:
                print('Sale with sale_id {} not found on Tutti'.format(sale_id))
        else:
            if self.sys_config.print_details:
                sale.print_sale_details()
            sale_from_db = self.get_sale_from_db_by_sale_id(sale_id)
            if self.sys_config.print_details:
                sale_from_db.print_sale_details()
            print('Are identical' if self._sale_factory.are_sales_identical(sale, sale_from_db) else 'Not identical')

    def get_sale_from_tutti_by_sale_id(self, sale_id: str) -> SalesmanSale:
        return self._sale_factory.get_sale_via_request_by_sale_id(sale_id)

    def get_search_results_by_selected_print_category(self, print_category: list):
        self.__init_printing__(self._current_similar_sales, print_category)
        return self.__get_similar_sales_as_dict_list_by_print_category_(print_category)

    def __get_similar_sales_as_dict_list_by_print_category_(self, print_category: list) -> list:
        return_list = []
        entity_label = print_category[0]
        entity_value = print_category[1]
        for similar_sale in self._current_similar_sales:
            if entity_value in similar_sale.entity_label_dict:
                if similar_sale.entity_label_dict[entity_value] == entity_label:
                    return_list.append(
                        similar_sale.data_dict_obj.get_data_dict_for_columns(SLDC.get_columns_for_search_results()))
        return return_list

    def get_search_results_from_online_inputs(self, api: OnlineSearchApi) -> list:
        if api.search_string == '':
            return []
        self._sale_factory.init_url_factory_by_online_search_api(api)
        self._current_source_sale = self._sale_factory.get_sale_by_online_search_string(api.search_string)
        self._current_similar_sales = self.__get_similar_sales_for_sale__(self._current_source_sale)
        self.__init_printing__(self._current_similar_sales)
        return self.__get_similar_sales_as_dict_list__(
            self._current_source_sale, self._current_similar_sales, for_db=False)

    def check_my_sales_against_similar_sales(self, state='active'):
        if state == '':
            state_list = ['active', 'pending', 'edit', 'hidden', 'archived']
        else:
            state_list = [state]

        for state in state_list:
            source_sale_list = self.browser.get_my_sales_from_tutti()
            for source_sale in source_sale_list:
                self._current_source_sale = source_sale
                self._current_similar_sales = self.__get_similar_sales_for_sale__(self._current_source_sale)
                self.__process_my_sale_and_similar_sales__()

    def check_my_virtual_sales_against_similar_sales(self):
        source_sale_list = self.__get_my_virtual_sales__()
        for source_sale in source_sale_list:
            self._current_source_sale = source_sale
            self._current_similar_sales = self.__get_similar_sales_for_sale__(self._current_source_sale)
            self.__process_my_sale_and_similar_sales__()

    def __process_my_sale_and_similar_sales__(self):
        self.__check_similarity__(self._current_similar_sales)
        self.__write_to_excel__(self._current_similar_sales)
        self.__write_to_database__(self._current_similar_sales)
        self.__init_printing__(self._current_similar_sales)
        self._printing.print_box_plots()

    def __check_similarity__(self, similar_sales: list):
        if self._salesman_spacy.sm_loaded:
            return
        my_sale_title_doc = self.nlp(self._current_source_sale.title)
        for similar_sale in similar_sales:
            similar_sale_title_doc = self.nlp(similar_sale.title)
            similarity = my_sale_title_doc.similarity(similar_sale_title_doc)
            similarity_text = self._salesman_spacy.get_similarity_text(similarity)
            if self.sys_config.print_details:
                print('Similarity between {} and {}: {} ({})'.format(
                    self._current_source_sale.title, similar_sale.title, similarity, similarity_text
                ))

    def __identify_outliers__(self, similar_sale_dict: dict):
        if len(similar_sale_dict) == 0:
            return
        price_single_list = [similar_sale.price_single for similar_sale in similar_sale_dict.values()]
        outlier = Outlier(price_single_list, self.sys_config.outlier_threshold)
        # outlier.print_outlier_details()
        for similar_sale in similar_sale_dict.values():
            similar_sale.set_is_outlier(True if outlier.is_value_outlier(similar_sale.price_single) else False)

    def __write_to_excel__(self, similar_sales: list):
        if not self.sys_config.write_to_excel:
            return
        row_list = []
        try:
            self._excel.start_iteration()
            row_list.append(self._current_source_sale.get_value_dict_for_worksheet())
            for similar_sale in similar_sales:
                row_list.append(similar_sale.get_value_dict_for_worksheet(
                    self._current_source_sale.sale_id, self._current_source_sale.title))
            for idx, value_dict in enumerate(row_list):
                # print('value_dict={}'.format(value_dict))
                self._excel.add_row_by_value_dict(value_dict)
        finally:
            self._excel.print_message_after_iteration(len(row_list))

    def __get_excel__(self):
        if self.sys_config.write_to_excel:
            excel_obj = MyExcel(self.excel_file_path, sheet_name='Similar sales')
            excel_obj.write_header(SLDC.get_columns_for_excel())
            return excel_obj

    def __write_to_database__(self, similar_sales: list):
        if not self.sys_config.write_to_database:
            return
        input_list = []
        self.__add_sale_to_database_input_list__(self._current_source_sale, input_list)
        for similar_sale in similar_sales:
            self.__add_sale_to_database_input_list__(similar_sale, input_list)
        try:
            if len(input_list) > 0:
                self.sys_config.db.insert_sale_data(input_list)
        finally:
            print('{} sales written to database...'.format(len(input_list)))

    def restrict_printing_to_selected_print_category(self, print_category: str):
        self.__init_printing__(self._current_similar_sales, print_category)

    def __init_printing__(self, similar_sales: list, print_category=None):
        input_list = []
        for label_value, entity_label in self._current_source_sale.entity_label_dict.items():
            print('__init_printing__: print_cateogory={}, label={}, value={}'.format(print_category, entity_label, label_value))
            if print_category is None or (print_category[0] == entity_label and print_category[1] == label_value):
                self.__add_to_printing_list__(
                    input_list, self._current_source_sale, similar_sales, entity_label, label_value)
        self._printing.init_by_sale_dict(input_list)

    def __add_to_printing_list__(
            self, input_list, my_sale: SalesmanSale, similar_sales: list, entity_label: str, label_value: str):
        if entity_label == my_sale.entity_label_dict.get(label_value, ''):
            if my_sale.location != 'online':
                my_sale.data_dict_obj.add(SLDC.PRINT_CATEGORY, '{}: {}'.format(entity_label, label_value))
                input_list.append(my_sale.data_dict_obj.get_data_dict_for_columns(self._printing.columns))
        for similar_sale in similar_sales:
            if entity_label == similar_sale.entity_label_dict.get(label_value, ''):
                similar_sale.data_dict_obj.add(SLDC.PRINT_CATEGORY, '{}: {}'.format(entity_label, label_value))
                input_list.append(similar_sale.data_dict_obj.get_data_dict_for_columns(self._printing.columns))

    def __add_sale_to_database_input_list__(self, sale: SalesmanSale, input_list: list):
        if sale.is_sale_ready_for_sale_table():
            sale_dict = sale.data_dict_obj.get_data_dict_for_sale_table()
            existing_sale = self.get_sale_from_db_by_sale_id(sale.sale_id)
            if existing_sale is None:
                input_list.append(sale_dict)
            else:
                # print('__add_sale_to_database_input_list__: {}'.format(sale_dict))
                if not self._sale_factory.are_sales_identical(sale, existing_sale):
                    input_list.append(sale_dict)

    def get_sale_from_db_by_sale_id(self, sale_id: str) -> SalesmanSale:
        if self._access_layer.is_sale_with_id_available(sale_id):
            df = self._access_layer.get_sale_by_id(sale_id)
            return self._sale_factory.get_sale_by_db_row(df.iloc[0])

    @staticmethod
    def __get_similar_sales_as_dict_list__(my_sale: SalesmanSale, similar_sales: list, for_db=True) -> list:
        return_list = []
        for similar_sale in similar_sales:
            if for_db:
                if similar_sale.is_sale_ready_for_sale_table():
                    sale_dict = similar_sale.data_dict_obj.get_data_dict_for_sale_table()
                    return_list.append(sale_dict)
            else:
                return_list.append(
                    similar_sale.data_dict_obj.get_data_dict_for_columns(SLDC.get_columns_for_search_results()))
        return return_list

    def __get_my_virtual_sales__(self, number=0):
        self._my_sales_source = 'virtual'
        tutti_sales = []
        virtual_sale_df = self.__get_sale_elements_from_file__()
        for idx, row in virtual_sale_df.iterrows():
            print('idx={} - row.title={}'.format(idx, row[SLDC.TITLE]))
            if number == 0 or idx == number - 1:
                sale = self._sale_factory.get_sale_by_file_row(row)
                tutti_sales.append(sale)
        return tutti_sales

    def __get_sale_elements_from_file__(self) -> pd.DataFrame:
        df = pd.read_csv(self.sys_config.virtual_sales_file_path, delimiter='#', header=None)
        df.columns = SLDC.get_columns_for_virtual_sales_in_file()
        return df

    def __visualize_dependencies__(self, sale: list):
        for sale in sale:
            doc_dict = {'Title': self.nlp(sale.title), 'Description': self.nlp(sale.description)}
            for key, doc in doc_dict.items():
                displacy.render(doc, style='dep')
                displacy.render(doc, style='ent')

    def __get_similar_sales_for_sale__(self, sale: SalesmanSale) -> list:
        similar_sale_dict = {}
        self._search_label_lists = sale.get_search_label_lists()
        print('\nSearch_label_lists={}, category={}'.format(self._search_label_lists, sale.product_category))
        category_sub_category_lists = self.sys_config.product_categorizer.get_search_category_sub_categories(
            sale.product_category, sale.product_sub_category)
        print('category_sub_category_lists={}'.format(category_sub_category_lists))
        for value_list in category_sub_category_lists:
            self.__adjust_search_label_lists_for_too_many_hits__(sale, value_list)
            for search_label_list in self._search_label_lists:
                if len(sale.product_category_value_list) > 0:
                    for product_category_value in sale.product_category_value_list:
                        self._sale_factory.adjust_category_sub_category_for_url_factory(product_category_value, '')
                        self.__get_sales_from_tutti_for_search_label_list__(similar_sale_dict, search_label_list, sale)
                else:
                    self.__get_sales_from_tutti_for_search_label_list__(similar_sale_dict, search_label_list, sale)
            self.__identify_outliers__(similar_sale_dict)
        similar_sales_summary = [sale for sale in similar_sale_dict.values()]
        if self.sys_config.print_details:
            self.__print_similar_sales__(sale, similar_sales_summary)
        return similar_sales_summary

    def __adjust_search_label_lists_for_too_many_hits__(self, sale: SalesmanSale, value_list: list):
        category_value = self.sys_config.product_categorizer.get_value_for_category(value_list[0])
        sub_category_value = self.sys_config.product_categorizer.get_sub_category_value_for_sub_category(
            value_list[0], value_list[1])
        print('\nSearch over cat/sub_cat={}/{}'.format(category_value, sub_category_value))
        self._sale_factory.adjust_category_sub_category_for_url_factory(category_value, sub_category_value)
        number_search_dict = self._sale_factory.get_search_string_found_number_dict(self._search_label_lists)
        found_number_list = [number_search_dict[search_string][0] for search_string in number_search_dict]
        if len(found_number_list) > 0 and max(found_number_list) > self.sys_config.number_allowed_search_results:
            print('Max number {} is larger then allowed result number {} -> change search strings...'.format(
                max(found_number_list), self.sys_config.number_allowed_search_results
            ))
            self._search_label_lists = sale.get_extended_base_search_label_lists(self._search_label_lists)
            print('\nSearch_label_lists={}'.format(self._search_label_lists))

    def __get_sales_from_tutti_for_search_label_list__(
            self, similar_sales_dict: dict, search_label_list: list, sale: SalesmanSale):
        similar_sales = self._sale_factory.get_sales_by_search_label_list(search_label_list)
        for similar_sale in similar_sales:
            if self.__can_similar_sale_be_added_to_dict__(similar_sales_dict, sale, similar_sale):
                similar_sale.set_master_details(sale.sale_id, sale.title)
                similar_sales_dict[similar_sale.sale_id] = similar_sale

    def __can_similar_sale_be_added_to_dict__(self, similar_dict: dict, sale: SalesmanSale, similar_sale: SalesmanSale):
        if similar_sale.sale_id == sale.sale_id:
            return False
        if not self.__is_found_sale_similar_to_source_sale__(similar_sale, sale):
            print('Source sale "{}" is not similar to found sale "{}"'.format(sale.title, similar_sale.title))
            print('--> entity_dict: {} <--> {}'.format(sale.entity_label_dict, similar_sale.entity_label_dict))
            return False
        if similar_sale.sale_id not in similar_dict:
            return True
        return len(similar_sale.found_by_labels) > len(similar_dict[similar_sale.sale_id].found_by_labels)

    @staticmethod
    def __is_found_sale_similar_to_source_sale__(found_sale: SalesmanSale, source_sale: SalesmanSale) -> bool:
        # is_company_available = found_sale.is_any_term_in_list_in_title_or_description(source_sale.company_list)
        # is_product_available = found_sale.is_any_term_in_list_in_title_or_description(source_sale.product_list)
        # is_object_available = found_sale.is_any_term_in_list_in_title(source_sale.object_list)
        # return (is_company_available or is_product_available) and is_object_available
        is_target_group_identical = found_sale.is_any_target_group_entity_identical(source_sale)
        is_product_identical = found_sale.is_any_product_entity_identical(source_sale)
        is_object_identical = found_sale.is_any_object_entity_identical(source_sale)
        return is_object_identical or is_product_identical
        # return (is_product_identical or is_object_identical) and is_target_group_identical

    @staticmethod
    def __print_similar_sales__(sale, similar_sales: list):
        sale.print_sale_in_original_structure()
        if len(similar_sales) == 0:
            print('\nNO SIMILAR SALES AVAILABLE for {}'.format(sale.key))
        for sale in similar_sales:
            sale.print_sale_in_original_structure()

