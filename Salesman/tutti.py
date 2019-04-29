"""
Description: This module is the base class for our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_database.access_layer.access_layer_sale import AccessLayer4Sale
from calculation.outlier import Outlier
from tutti_browser import MyUrlBrowser4Tutti
from lxml import html
from tutti_sale import TuttiSale
from spacy import displacy
from tutti_spacy import TuttiSpacy
from tutti_constants import SCLS, SLSCLS, EL
import pandas as pd
import xlsxwriter
import requests
from time import sleep
import numpy as np
import statistics
from salesman_system_configuration import SystemConfiguration
from printing.sale_printing import SalesmanPrint


class Tutti:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self.printing = SalesmanPrint(SLDC.get_columns_for_sales_printing())
        self._my_sales_source = SLSRC.TUTTI_CH
        self._write_to_excel = self.sys_config.write_to_excel
        self._spacy = TuttiSpacy(load_sm=self.sys_config.load_sm) if self.sys_config.with_nlp else None
        self._browser = None
        self._url_search_switzerland = 'https://www.tutti.ch/de/li/ganze-schweiz/angebote?q='
        self._access_layer = AccessLayer4Sale(self.sys_config.db)
        self._search_label_lists = []

    @property
    def nlp(self):
        return None if self._spacy is None else self._spacy.nlp

    @property
    def browser(self) -> MyUrlBrowser4Tutti:
        if self._browser is None:
            self._browser = MyUrlBrowser4Tutti(self.sys_config, self._spacy)
            self._browser.enter_and_submit_credentials()
        return self._browser

    @property
    def excel_file_path(self):
        if self._my_sales_source == SLSRC.TUTTI_CH:
            return self.sys_config.file_handler.get_file_path_for_file(
                '{}_{}'.format(self._my_sales_source, self.sys_config.sales_result_file_name))
        return self.sys_config.file_handler.get_file_path_for_file(self.sys_config.virtual_sales_result_file_name)

    @property
    def start_search_label_lists(self) -> list:
        return self._search_label_lists

    def check_my_nth_sale_against_similar_sales(self, number=1):
        sale = self.browser.get_my_nth_sale_from_tutti(number)
        if sale is None:
            return
        sale.print_sale_in_original_structure()
        similar_sales_dict = self.__get_similar_sale_dict_from_tutti__([sale])
        self.__process_my_sales_and_similar_sales__([sale], similar_sales_dict)

    def check_my_sale_on_tutti_by_sale_id_against_similar_sales(self, sale_id: str):
        sale = self.get_sale_from_tutti_by_sale_id(sale_id)
        if sale is None:
            return
        sale.print_sale_in_original_structure()
        similar_sales_dict = self.__get_similar_sale_dict_from_tutti__([sale])
        self.__process_my_sales_and_similar_sales__([sale], similar_sales_dict)

    def check_my_sale_on_tutti_by_sale_id_against_sale_in_db(self, sale_id: str):
        sale = self.get_sale_from_tutti_by_sale_id(sale_id)
        if sale is None:
            print('Sale with sale_id {} not found on Tutti'.format(sale_id))
        else:
            sale.print_sale_details()
            existing_sale = self.get_sale_from_db_by_sale_id(sale_id)
            existing_sale.print_sale_details()
            print('Are identical' if sale.is_identical(existing_sale) else 'Not identical')

    def get_sale_from_tutti_by_sale_id(self, sale_id: str) -> TuttiSale:
        url = 'https://www.tutti.ch/de/vi/{}'.format(sale_id)
        # print('Searching for {}'.format(url))
        request = requests.get(url)
        sleep(1)
        tree = html.fromstring(request.content)
        sales = tree.xpath('//div[@class="{}"]'.format(SLSCLS.OFFERS))
        for sale_element in sales:
            sale = TuttiSale(self._spacy, self.sys_config)
            sale.init_by_html_element_for_single_sale(sale_element, url)
            return sale

    def check_my_nth_virtual_sale_against_similar_sales(self, number=1):
        list_with_nth_sale = self.__get_my_virtual_sales__(number)
        similar_sale_dict = self.__get_similar_sale_dict_from_tutti__(list_with_nth_sale)
        self.__process_my_sales_and_similar_sales__(list_with_nth_sale, similar_sale_dict)

    def get_search_results_from_online_inputs(self, search_input: str) -> list:
        if search_input == '':  # we need an empty line...
            return []
        list_with_sale = self.__get_sale_list_for_online_search_string__(search_input)
        similar_sale_dict = self.__get_similar_sale_dict_from_tutti__(list_with_sale)
        self.__init_printing__(list_with_sale, similar_sale_dict)
        return self.__get_similar_sales_as_dict_list__(list_with_sale, similar_sale_dict, for_db=False)

    def search_on_tutti(self, search_string: str):
        list_with_sale = self.__get_sale_list_for_online_search_string__(search_string)
        similar_sale_dict = self.__get_similar_sale_dict_from_tutti__(list_with_sale)
        self.__process_my_sales_and_similar_sales__(list_with_sale, similar_sale_dict)

    def check_my_sales_against_similar_sales(self, state='active'):
        if state == '':
            state_list = ['active', 'pending', 'edit', 'hidden', 'archived']
        else:
            state_list = [state]

        for state in state_list:
            my_sales = self.browser.get_my_sales_from_tutti()
            similar_sale_dict = self.__get_similar_sale_dict_from_tutti__(my_sales)
            self.__process_my_sales_and_similar_sales__(my_sales, similar_sale_dict)

    def check_my_virtual_sales_against_similar_sales(self):
        my_virtual_sales = self.__get_my_virtual_sales__()
        similar_sale_dict = self.__get_similar_sale_dict_from_tutti__(my_virtual_sales)
        self.__process_my_sales_and_similar_sales__(my_virtual_sales, similar_sale_dict)

    def __process_my_sales_and_similar_sales__(self, my_sales: list, similar_sale_dict: dict):
        self.__check_similarity__(my_sales, similar_sale_dict)
        self.__write_to_excel__(my_sales, similar_sale_dict)
        self.__write_to_database__(my_sales, similar_sale_dict)
        self.__init_printing__(my_sales, similar_sale_dict)

    def __check_similarity__(self, my_sales: list, similar_sale_dict: dict):
        if self._spacy.sm_loaded:
            return
        for my_sale in my_sales:
            my_sale_title_doc = self.nlp(my_sale.title)
            similar_sales = similar_sale_dict[my_sale.sale_id]
            for similar_sale in similar_sales:
                similar_sale_title_doc = self.nlp(similar_sale.title)
                similarity = my_sale_title_doc.similarity(similar_sale_title_doc)
                similarity_text = self._spacy.get_similarity_text(similarity)
                print('Similarity between {} and {}: {} ({})'.format(
                    my_sale.title, similar_sale.title, similarity, similarity_text
                ))

    def __identify_outliers__(self, similar_sale_dict: dict):
        if len(similar_sale_dict) == 0:
            return
        price_single_list = [similar_sale.price_single for similar_sale in similar_sale_dict.values()]
        outlier = Outlier(price_single_list, self.sys_config.outlier_threshold)
        # outlier.print_outlier_details()
        for similar_sale in similar_sale_dict.values():
            similar_sale.set_is_outlier(True if outlier.is_value_outlier(similar_sale.price_single) else False)

    def __write_to_excel__(self, my_sales: list, similar_sale_dict: dict):
        if not self._write_to_excel:
            return
        # print('self._my_sales_source={}, self.excel_file_path={}'.format(self._my_sales_source, self.excel_file_path))
        excel_workbook = xlsxwriter.Workbook(self.excel_file_path)
        excel_workbook.add_worksheet('Similar sales')
        worksheet = excel_workbook.get_worksheet_by_name('Similar sales')
        row_list = []
        columns = SLDC.get_columns_for_excel()
        for col_number, col in enumerate(columns):
            worksheet.write(0, col_number, col)
        try:
            for my_sale in my_sales:
                row_list.append(my_sale.get_value_dict_for_worksheet())
                similar_sales = similar_sale_dict[my_sale.sale_id]
                for similar_sale in similar_sales:
                    row_list.append(similar_sale.get_value_dict_for_worksheet(my_sale.sale_id, my_sale.title))
            for idx, value_dict in enumerate(row_list):
                # print(value_dict)
                row_number = idx + 1
                for col_number, col in enumerate(columns):
                    if col in value_dict:
                        value = value_dict[col]
                        worksheet.write(row_number, col_number, value)
            print('Results written to {}'.format(self.excel_file_path))
        finally:
            excel_workbook.close()

    def __write_to_database__(self, my_sales: list, similar_sale_dict: dict):
        if not self.sys_config.write_to_database:
            return
        input_list = []
        for my_sale in my_sales:
            self.__add_sale_to_database_input_list__(my_sale, input_list)
            similar_sales = similar_sale_dict[my_sale.sale_id]
            for similar_sale in similar_sales:
                self.__add_sale_to_database_input_list__(similar_sale, input_list)
        try:
            if len(input_list) > 0:
                self.sys_config.db.insert_sale_data(input_list)
        finally:
            print('{} sales written to database...'.format(len(input_list)))

    def __init_printing__(self, my_sales: list, similar_sale_dict: dict):
        input_list = []
        for my_sale in my_sales:
            for label_value, entity_label in my_sale.entity_label_dict.items():
                self.__add_to_printing_list__(input_list, my_sale, similar_sale_dict, entity_label, label_value)
            self.printing.init_by_sale_dict(input_list)
            break

    def __add_to_printing_list__(
            self, input_list, my_sale: TuttiSale, similar_sale_dict: dict, entity_label: str, label_value: str):
        if entity_label == my_sale.entity_label_dict.get(label_value, ''):
            if my_sale.location != 'online':
                my_sale.data_dict_obj.add(SLDC.PRINT_CATEGORY, '{}: {}'.format(entity_label, label_value))
                input_list.append(my_sale.data_dict_obj.get_data_dict_for_columns(self.printing.columns))
        similar_sales = similar_sale_dict[my_sale.sale_id]
        for similar_sale in similar_sales:
            if entity_label == similar_sale.entity_label_dict.get(label_value, ''):
                similar_sale.data_dict_obj.add(SLDC.PRINT_CATEGORY, '{}: {}'.format(entity_label, label_value))
                input_list.append(similar_sale.data_dict_obj.get_data_dict_for_columns(self.printing.columns))

    def __add_sale_to_database_input_list__(self, sale: TuttiSale, input_list: list):
        if sale.is_sale_ready_for_sale_table():
            sale_dict = sale.data_dict_obj.get_data_dict_for_sale_table()
            existing_sale = self.get_sale_from_db_by_sale_id(sale.sale_id)
            if existing_sale is None:
                input_list.append(sale_dict)
            else:
                if not sale.is_identical(existing_sale):
                    input_list.append(sale_dict)

    def get_sale_from_db_by_sale_id(self, sale_id: str) -> TuttiSale:
        if self._access_layer.is_sale_with_id_available(sale_id):
            df = self._access_layer.get_sale_by_id(sale_id)
            existing_sale = TuttiSale(self._spacy, self.sys_config)
            existing_sale.init_by_database_row(df.iloc[0])
            return existing_sale

    @staticmethod
    def __get_similar_sales_as_dict_list__(my_sales: list, similar_sale_dict: dict, for_db=True) -> list:
        return_list = []
        for my_sale in my_sales:
            similar_sales = similar_sale_dict[my_sale.sale_id]
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
            print('idx={} - row={}'.format(idx, row[SLDC.TITLE]))
            if number == 0 or idx == number - 1:
                sale = self.__get_tutti_sale_from_file_row__(row)
                tutti_sales.append(sale)
        return tutti_sales

    def __get_sale_list_for_online_search_string__(self, search_input: str):
        self._my_sales_source = 'online'
        sale = TuttiSale(self._spacy, self.sys_config)
        sale.init_by_online_input(search_input)
        return [sale]

    def __get_sale_elements_from_file__(self) -> pd.DataFrame:
        df = pd.read_csv(self.sys_config.virtual_sales_file_path, delimiter='#', header=None)
        df.columns = SLDC.get_columns_for_virtual_sales_in_file()
        return df

    def __get_tutti_sale_from_file_row__(self, file_row):
        sale = TuttiSale(self._spacy, self.sys_config)
        sale.init_by_file_row(file_row)
        sale.set_source(self.sys_config.virtual_sales_file_name)
        sale.print_sale_in_original_structure()
        return sale

    def __visualize_dependencies__(self, sale: list):
        for sale in sale:
            doc_dict = {'Title': self.nlp(sale.title), 'Description': self.nlp(sale.description)}
            for key, doc in doc_dict.items():
                displacy.render(doc, style='dep')
                displacy.render(doc, style='ent')

    def __get_similar_sale_dict_from_tutti__(self, sales: list):  # key is the ID of my_sale
        return {sale.sale_id: self.__get_similar_sales_for_sale__(sale) for sale in sales}

    def __get_similar_sales_for_sale__(self, sale: TuttiSale) -> list:
        similar_sale_dict = {}
        self._search_label_lists = sale.get_search_label_lists()
        print('\nSearch_label_lists={}'.format(self._search_label_lists))
        request_dict = self.__get_request_dict_from_tutti_for_search_label_list__(SCLS.FOUND_NUMBERS, SCLS.OFFERS)
        found_number_list = [request_dict[search_string][0] for search_string in request_dict]
        if len(found_number_list) > 0 and max(found_number_list) > self.sys_config.number_allowed_search_results:
            print('Max number {} is larger then allowed result number {} -> change search strings...'.format(
                max(found_number_list), self.sys_config.number_allowed_search_results
            ))
            self._search_label_lists = sale.get_extended_base_search_label_lists(self._search_label_lists)
            print('\nSearch_label_lists={}'.format(self._search_label_lists))
        for search_label_list in self._search_label_lists:
            self.__get_sales_from_tutti_for_search_label_list__(similar_sale_dict, search_label_list, sale)
        self.__identify_outliers__(similar_sale_dict)
        similar_sales_summary = [sale for sale in similar_sale_dict.values()]
        self.__print_similar_sales__(sale, similar_sales_summary)
        return similar_sales_summary

    def __get_request_dict_from_tutti_for_search_label_list__(self, class_number: str, class_entries: str) -> dict:
        return_dict = {}
        for search_label_list in self._search_label_lists:
            search_string = ' '.join(search_label_list)
            url = '{}{}'.format(self._url_search_switzerland, search_string)
            request = requests.get(url)
            tree = html.fromstring(request.content)
            xpath_numbers = tree.xpath('//div[@class="{}"]'.format(class_number))
            number_found = self.__get_number_from_number_item__(xpath_numbers)
            sales = tree.xpath('//div[@class="{}"]'.format(class_entries))
            return_dict[search_string] = [number_found, sales]
        return return_dict

    def __get_number_from_number_item__(self, xpath_numbers):
        number_item = xpath_numbers[0] if type(xpath_numbers) is list else xpath_numbers
        doc_number = self.nlp(str(number_item.text_content()).replace("'", ""))
        # self._spacy.print_tokens_for_doc(doc_number)
        number_results = doc_number._.first_pos_number
        return 0 if number_results is None else number_results

    def __get_numbers_dict_from_tutti__(self, class_name: str, search_label_list: list) -> list:
        tutti_sales = []
        search_string = ' '.join(search_label_list)
        url = '{}{}'.format(self._url_search_switzerland, search_string)
        # print('Searching for {}'.format(url))
        request = requests.get(url)
        # sleep(1)
        tree = html.fromstring(request.content)
        sales = tree.xpath('//div[@class="{}"]'.format(class_name))
        for sale_element in sales:
            sale = TuttiSale(self._spacy, self.sys_config, search_label_list)
            sale.init_by_html_element(sale_element)
            tutti_sales.append(sale)
            # sale.print_sale_in_original_structure()
        return tutti_sales

    def __get_sales_from_tutti_for_search_label_list__(
            self, similar_sales_dict: dict, search_label_list: list, sale: TuttiSale):
        similar_sales = self.__get_sales_from_tutti__(SCLS.OFFERS, search_label_list)
        for similar_sale in similar_sales:
            if self.__can_similar_sale_be_added_to_dict__(similar_sales_dict, sale, similar_sale):
                similar_sale.set_master_details(sale.sale_id, sale.title)
                similar_sale.set_source(SLSRC.TUTTI_CH)
                similar_sales_dict[similar_sale.sale_id] = similar_sale

    def __get_sales_from_tutti__(self, class_name: str, parent_search_label_list: list) -> list:
        tutti_sales = []
        search_string = ' '.join(parent_search_label_list)
        url = '{}{}'.format(self._url_search_switzerland, search_string)
        # print('Searching for {}'.format(url))
        request = requests.get(url)
        # sleep(1)
        tree = html.fromstring(request.content)
        sales = tree.xpath('//div[@class="{}"]'.format(class_name))
        for sale_element in sales:
            sale = TuttiSale(self._spacy, self.sys_config, parent_search_label_list)
            sale.init_by_html_element(sale_element)
            tutti_sales.append(sale)
            # sale.print_sale_in_original_structure()
        return tutti_sales

    def __can_similar_sale_be_added_to_dict__(self, similar_dict: dict, sale: TuttiSale, similar_sale: TuttiSale):
        if similar_sale.sale_id == sale.sale_id:
            return False
        if not self.__is_found_sale_similar_to_source_sale__(similar_sale, sale):
            print('Found sale "{}" not similar to "{}"'.format(similar_sale.title, sale.title))
            print('--> entity_dict: {} <--> {}'.format(sale.entity_label_dict, similar_sale.entity_label_dict))
            return False
        if similar_sale.sale_id not in similar_dict:
            return True
        return len(similar_sale.found_by_labels) > len(similar_dict[similar_sale.sale_id].found_by_labels)

    @staticmethod
    def __is_found_sale_similar_to_source_sale__(found_sale: TuttiSale, source_sale: TuttiSale) -> bool:
        # is_company_available = found_sale.is_any_term_in_list_in_title_or_description(source_sale.company_list)
        # is_product_available = found_sale.is_any_term_in_list_in_title_or_description(source_sale.product_list)
        # is_object_available = found_sale.is_any_term_in_list_in_title(source_sale.object_list)
        # return (is_company_available or is_product_available) and is_object_available
        is_target_group_identical = found_sale.is_any_target_group_entity_identical(source_sale)
        is_product_identical = found_sale.is_any_product_entity_identical(source_sale)
        is_object_identical = found_sale.is_any_object_entity_identical(source_sale)
        return is_object_identical
        # return (is_product_identical or is_object_identical) and is_target_group_identical

    @staticmethod
    def __print_similar_sales__(sale, similar_sales: list):
        sale.print_sale_in_original_structure()
        if len(similar_sales) == 0:
            print('\nNO SIMILAR SALES AVAILABLE for {}'.format(sale.key))
        for sale in similar_sales:
            sale.print_sale_in_original_structure()

