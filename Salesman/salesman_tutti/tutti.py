"""
Description: This module is the base class for our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.constants.salesman_constants import SLDC, SLSRC, PRCAT
from sertl_analytics.mydates import MyDate
from sertl_analytics.my_text import MyText
from sertl_analytics.my_excel import MyExcel
from salesman_database.access_layer.access_layer_sale import AccessLayer4Sale
from calculation.outlier import Outlier
from salesman_tutti.tutti_browser import MyUrlBrowser4Tutti
from lxml import html
from salesman_tutti.tutti_sale import TuttiSale
from spacy import displacy
from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_tutti.tutti_constants import SCLS, SLSCLS
import pandas as pd
import xlsxwriter
import requests
from time import sleep
from salesman_system_configuration import SystemConfiguration
from printing.sale_printing import SalesmanPrint
import math


class TuttiUrlHelper:
    def __init__(self, search_string: str, region='ganze-schweiz', category='angebote', sub_category=''):
        # 'https://www.tutti.ch/de/li/ganze-schweiz/angebote?'
        # https://www.tutti.ch/de/li/aargau?o=6&q=weste
        self._url_base = 'https://www.tutti.ch/de/li'
        self._region = region
        self._category = category
        self._sub_category = sub_category
        self._order = 0
        self._search_string = search_string
        self._url_extended_base = self.__get_url_extended_base__()

    @property
    def search_string(self):
        return self._search_string

    @property
    def url(self):
        p_dict = {
            'o': '' if self._order == 0 else '{}'.format(self._order),
            'q': '{}'.format(self._search_string)
        }
        p_list = ['{}={}'.format(key, value) for key, value in p_dict.items() if value != '']
        url = '{}?{}'.format(self._url_extended_base, '&'.join(p_list))
        return url

    def get_url_with_search_string(self, search_string: str):
        self._search_string = search_string
        return self.url

    def get_url_list(self, search_string: str):
        self._search_string = search_string
        url_list = []
        for i in range(0, 11):
            self._order = i
            url_list.append(self.url)
        self._order = 0  # reset it....
        return url_list

    def adjust_category_sub_category(self, category: str, sub_category: str):
        self._category = category
        self._sub_category = sub_category
        self._url_extended_base = self.__get_url_extended_base__()

    def __get_url_extended_base__(self):
        region = '' if self._region == '' else '/{}'.format(self._region)
        category = '' if self._category == '' else '/{}'.format(self._category)
        sub_category = '' if self._sub_category in ['', 'GANZE_SCHWEIZ'] else '/{}'.format(self._sub_category)
        return '{}{}{}{}'.format(self._url_base, region, category, sub_category)


class Tutti:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self._printing = SalesmanPrint(SLDC.get_columns_for_sales_printing())
        self._my_sales_source = SLSRC.TUTTI_CH
        self._excel = self.__get_excel__()
        self._spacy = SalesmanSpacy(load_sm=self.sys_config.load_sm) if self.sys_config.with_nlp else None
        self._browser = None
        self._url_helper = TuttiUrlHelper('')  # will be overwritten when searched
        self._access_layer = AccessLayer4Sale(self.sys_config.db)
        self._search_label_lists = []
        self._current_source_sale = None
        self._current_similar_sales_dict = {}  # will get the results for the search

    # def __del__(self):
    #     if self._excel is not None:
    #         print('Tutti.__del__: {}'.format(MyDate.get_date_time_as_string_from_date_time()))
    #         self._excel.close()

    @property
    def nlp(self):
        return None if self._spacy is None else self._spacy.nlp

    @property
    def printing(self):
        return self._printing

    @property
    def current_source_sale(self):
        return self._current_source_sale

    @property
    def browser(self) -> MyUrlBrowser4Tutti:
        if self._browser is None:
            self._browser = MyUrlBrowser4Tutti(self.sys_config, self._spacy)
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
        sale = self.__get_sale_for_online_search__(title + ' ' + description)
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

    def __check_sale_against_similar_sales_on_tutti__(self, sale: TuttiSale):
        if self.sys_config.print_details:
            sale.print_sale_in_original_structure()
        self._current_source_sale = sale
        self._current_similar_sales_dict = self.__get_similar_sales_dict_from_tutti__()
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
            print('Are identical' if sale.is_identical(sale_from_db) else 'Not identical')

    def get_sale_from_tutti_by_sale_id(self, sale_id: str) -> TuttiSale:
        url = 'https://www.tutti.ch/de/vi/{}'.format(sale_id)
        # print('Searching for {}'.format(url))
        request = requests.get(url)
        sleep(1)
        tree = html.fromstring(request.content)
        product_categories = tree.xpath('//span[@class="{}"]'.format(SLSCLS.PRODUCT_CATEGORIES))
        sales = tree.xpath('//div[@class="{}"]'.format(SLSCLS.OFFERS))
        for sale_element in sales:
            sale = TuttiSale(self._spacy, self.sys_config)
            try:
                sale.init_by_html_element_for_single_sale(product_categories, sale_element, url)
                return sale
            except:
                print('\nWARNING: No active sale found on {} for id={}'.format(self._my_sales_source, sale_id))

    def get_search_results_by_selected_print_category(self, print_category: list):
        self.__init_printing__(self._current_similar_sales_dict, print_category)
        return self.__get_similar_sales_as_dict_list_by_print_category_(print_category)

    def __get_similar_sales_as_dict_list_by_print_category_(self, print_category: list) -> list:
        return_list = []
        similar_sales = self._current_similar_sales_dict[self._current_source_sale.sale_id]
        entity_label = print_category[0]
        entity_value = print_category[1]
        for similar_sale in similar_sales:
            if entity_value in similar_sale.entity_label_dict:
                if similar_sale.entity_label_dict[entity_value] == entity_label:
                    return_list.append(
                        similar_sale.data_dict_obj.get_data_dict_for_columns(SLDC.get_columns_for_search_results()))
        return return_list

    def get_search_results_from_online_inputs(self, url_helper: TuttiUrlHelper) -> list:
        self._url_helper = url_helper
        if url_helper.search_string == '':  # we need an empty line...
            return []
        self._current_source_sale = self.__get_sale_for_online_search__(url_helper.search_string, False)
        self._current_similar_sales_dict = self.__get_similar_sales_dict_from_tutti__()
        self.__init_printing__(self._current_similar_sales_dict)
        return self.__get_similar_sales_as_dict_list__(
            self._current_source_sale, self._current_similar_sales_dict, for_db=False)

    def __get_product_category_value_list_for_online_search__(self, sale: TuttiSale):
        category_number_dict = {}
        search_label_lists = sale.get_search_label_lists()
        for search_label_list in search_label_lists:
            encoded_search_string = MyText.get_url_encode_plus(' '.join(search_label_list))
            self.__fill_category_value_found_number_dict__(category_number_dict, encoded_search_string)
        number_list = [number for category, number in category_number_dict.items()]
        max_number = max(number_list)
        return [category for category in category_number_dict
                if math.sqrt(category_number_dict[category]) > math.sqrt(max_number)/3]

    def check_my_sales_against_similar_sales(self, state='active'):
        if state == '':
            state_list = ['active', 'pending', 'edit', 'hidden', 'archived']
        else:
            state_list = [state]

        for state in state_list:
            source_sale_list = self.browser.get_my_sales_from_tutti()
            for source_sale in source_sale_list:
                self._current_source_sale = source_sale
                self._current_similar_sales_dict = self.__get_similar_sales_dict_from_tutti__()
                self.__process_my_sale_and_similar_sales__()

    def check_my_virtual_sales_against_similar_sales(self):
        source_sale_list = self.__get_my_virtual_sales__()
        for source_sale in source_sale_list:
            self._current_source_sale = source_sale
            self._current_similar_sales_dict = self.__get_similar_sales_dict_from_tutti__()
            self.__process_my_sale_and_similar_sales__()

    def __process_my_sale_and_similar_sales__(self):
        self.__check_similarity__(self._current_similar_sales_dict)
        self.__write_to_excel__(self._current_similar_sales_dict)
        self.__write_to_database__(self._current_similar_sales_dict)
        self.__init_printing__(self._current_similar_sales_dict)
        self._printing.print_box_plots()

    def __check_similarity__(self, similar_sale_dict: dict):
        if self._spacy.sm_loaded:
            return
        for my_sale in self._current_source_sale:
            my_sale_title_doc = self.nlp(my_sale.title)
            similar_sales = similar_sale_dict[my_sale.sale_id]
            for similar_sale in similar_sales:
                similar_sale_title_doc = self.nlp(similar_sale.title)
                similarity = my_sale_title_doc.similarity(similar_sale_title_doc)
                similarity_text = self._spacy.get_similarity_text(similarity)
                if self.sys_config.print_details:
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

    def __write_to_excel__(self, similar_sale_dict: dict):
        if not self.sys_config.write_to_excel:
            return
        row_list = []
        try:
            self._excel.start_iteration()
            row_list.append(self._current_source_sale.get_value_dict_for_worksheet())
            similar_sales = similar_sale_dict[self._current_source_sale.sale_id]
            for similar_sale in similar_sales:
                row_list.append(similar_sale.get_value_dict_for_worksheet(
                    self._current_source_sale.sale_id, self._current_source_sale.title))
            for value_dict in row_list:
                self._excel.add_row_by_value_dict(value_dict)
        finally:
            self._excel.print_message_after_iteration(len(row_list))

    def __get_excel__(self):
        if self.sys_config.write_to_excel:
            excel_obj = MyExcel(self.excel_file_path, sheet_name='Similar sales')
            excel_obj.write_header(SLDC.get_columns_for_excel())
            return excel_obj

    def __write_to_database__(self, similar_sale_dict: dict):
        if not self.sys_config.write_to_database:
            return
        input_list = []
        for my_sale in self._current_source_sale:
            self.__add_sale_to_database_input_list__(my_sale, input_list)
            similar_sales = similar_sale_dict[my_sale.sale_id]
            for similar_sale in similar_sales:
                self.__add_sale_to_database_input_list__(similar_sale, input_list)
        try:
            if len(input_list) > 0:
                self.sys_config.db.insert_sale_data(input_list)
        finally:
            print('{} sales written to database...'.format(len(input_list)))

    def restrict_printing_to_selected_print_category(self, print_category: str):
        self.__init_printing__(self._current_similar_sales_dict, print_category)

    def __init_printing__(self, similar_sale_dict: dict, print_category=None):
        input_list = []
        for label_value, entity_label in self._current_source_sale.entity_label_dict.items():
            print('__init_printing__: print_cateogory={}, label={}, value={}'.format(print_category, entity_label, label_value))
            if print_category is None or (print_category[0] == entity_label and print_category[1] == label_value):
                self.__add_to_printing_list__(
                    input_list, self._current_source_sale, similar_sale_dict, entity_label, label_value)
        self._printing.init_by_sale_dict(input_list)

    def __add_to_printing_list__(
            self, input_list, my_sale: TuttiSale, similar_sale_dict: dict, entity_label: str, label_value: str):
        if entity_label == my_sale.entity_label_dict.get(label_value, ''):
            if my_sale.location != 'online':
                my_sale.data_dict_obj.add(SLDC.PRINT_CATEGORY, '{}: {}'.format(entity_label, label_value))
                input_list.append(my_sale.data_dict_obj.get_data_dict_for_columns(self._printing.columns))
        similar_sales = similar_sale_dict[my_sale.sale_id]
        for similar_sale in similar_sales:
            if entity_label == similar_sale.entity_label_dict.get(label_value, ''):
                similar_sale.data_dict_obj.add(SLDC.PRINT_CATEGORY, '{}: {}'.format(entity_label, label_value))
                input_list.append(similar_sale.data_dict_obj.get_data_dict_for_columns(self._printing.columns))

    def __add_sale_to_database_input_list__(self, sale: TuttiSale, input_list: list):
        if sale.is_sale_ready_for_sale_table():
            sale_dict = sale.data_dict_obj.get_data_dict_for_sale_table()
            existing_sale = self.get_sale_from_db_by_sale_id(sale.sale_id)
            if existing_sale is None:
                input_list.append(sale_dict)
            else:
                # print('__add_sale_to_database_input_list__: {}'.format(sale_dict))
                if not sale.is_identical(existing_sale):
                    input_list.append(sale_dict)

    def get_sale_from_db_by_sale_id(self, sale_id: str) -> TuttiSale:
        if self._access_layer.is_sale_with_id_available(sale_id):
            df = self._access_layer.get_sale_by_id(sale_id)
            existing_sale = TuttiSale(self._spacy, self.sys_config)
            existing_sale.init_by_database_row(df.iloc[0])
            return existing_sale

    @staticmethod
    def __get_similar_sales_as_dict_list__(my_sale: TuttiSale, similar_sale_dict: dict, for_db=True) -> list:
        return_list = []
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

    def __get_sale_for_online_search__(self, online_search_string: str, with_product_category_value_list=True):
        self._my_sales_source = 'online'
        sale = TuttiSale(self._spacy, self.sys_config)
        sale.init_by_online_input(online_search_string)
        if with_product_category_value_list:
            sale.set_product_category_value_list(
                self.__get_product_category_value_list_for_online_search__(sale))
        return sale

    def __get_sale_elements_from_file__(self) -> pd.DataFrame:
        df = pd.read_csv(self.sys_config.virtual_sales_file_path, delimiter='#', header=None)
        df.columns = SLDC.get_columns_for_virtual_sales_in_file()
        return df

    def __get_tutti_sale_from_file_row__(self, file_row):
        sale = TuttiSale(self._spacy, self.sys_config)
        sale.init_by_file_row(file_row)
        sale.set_source(self.sys_config.virtual_sales_file_name)
        if self.sys_config.print_details:
            sale.print_sale_in_original_structure()
        return sale

    def __visualize_dependencies__(self, sale: list):
        for sale in sale:
            doc_dict = {'Title': self.nlp(sale.title), 'Description': self.nlp(sale.description)}
            for key, doc in doc_dict.items():
                displacy.render(doc, style='dep')
                displacy.render(doc, style='ent')

    def __get_similar_sales_dict_from_tutti__(self):  # key is the ID of my_sale
        return {self._current_source_sale.sale_id: self.__get_similar_sales_for_sale__(self._current_source_sale)}

    def __get_similar_sales_for_sale__(self, sale: TuttiSale) -> list:
        similar_sale_dict = {}
        self._search_label_lists = sale.get_search_label_lists()
        print('\nSearch_label_lists={}, category={}'.format(self._search_label_lists, sale.product_category))
        category_sub_category_lists = self.sys_config.product_categorizer.get_search_category_sub_categories(
            sale.product_category, sale.product_sub_category)
        print('category_sub_category_lists={}'.format(category_sub_category_lists))
        for value_list in category_sub_category_lists:
            category_value = self.sys_config.product_categorizer.get_value_for_category(value_list[0])
            sub_category_value = self.sys_config.product_categorizer.get_sub_category_value_for_sub_category(
                value_list[0], value_list[1])
            print('\nSearch over cat/sub_cat={}/{}'.format(category_value, sub_category_value))
            self._url_helper.adjust_category_sub_category(category_value, sub_category_value)
            request_dict = self.__get_search_string_found_number_request_list_dict__(SCLS.FOUND_NUMBERS, SCLS.OFFERS)
            found_number_list = [request_dict[search_string][0] for search_string in request_dict]
            if len(found_number_list) > 0 and max(found_number_list) > self.sys_config.number_allowed_search_results:
                print('Max number {} is larger then allowed result number {} -> change search strings...'.format(
                    max(found_number_list), self.sys_config.number_allowed_search_results
                ))
                self._search_label_lists = sale.get_extended_base_search_label_lists(self._search_label_lists)
                print('\nSearch_label_lists={}'.format(self._search_label_lists))
            for search_label_list in self._search_label_lists:
                if len(sale.product_category_value_list) > 0:
                    for product_category_value in sale.product_category_value_list:
                        self._url_helper.adjust_category_sub_category(product_category_value, '')
                        self.__get_sales_from_tutti_for_search_label_list__(similar_sale_dict, search_label_list, sale)
                else:
                    self.__get_sales_from_tutti_for_search_label_list__(similar_sale_dict, search_label_list, sale)
            self.__identify_outliers__(similar_sale_dict)
        similar_sales_summary = [sale for sale in similar_sale_dict.values()]
        if self.sys_config.print_details:
            self.__print_similar_sales__(sale, similar_sales_summary)
        return similar_sales_summary

    def __get_search_string_found_number_request_list_dict__(self, class_number: str, class_entries: str) -> dict:
        # gets the number and request for a search_string - only positive searches are given back
        return_dict = {}
        for search_label_list in self._search_label_lists:
            search_string = MyText.get_url_encode_plus(' '.join(search_label_list))
            url = self._url_helper.get_url_with_search_string(search_string)
            request = requests.get(url)
            tree = html.fromstring(request.content)
            xpath_numbers = tree.xpath('//div[@class="{}"]'.format(class_number))
            number_found = self.__get_number_from_number_item__(xpath_numbers)
            if number_found > 0:
                sales = tree.xpath('//div[@class="{}"]'.format(class_entries))
                return_dict[search_string] = [number_found, search_label_list, sales]
                print('--> found {} by search_label_list "{}"'.format(number_found, search_label_list))
        return return_dict

    def __fill_category_value_found_number_dict__(self, category_number_dict: dict, search_string: str):
        # gets the found number for each product category
        return_dict = {}
        for product_category in PRCAT.get_all_without_all():
            category_value = self.sys_config.product_categorizer.get_value_for_category(product_category)
            self._url_helper.adjust_category_sub_category(category_value, '')
            url = self._url_helper.get_url_with_search_string(search_string)
            request = requests.get(url)
            tree = html.fromstring(request.content)
            xpath_numbers = tree.xpath('//div[@class="{}"]'.format(SCLS.FOUND_NUMBERS))
            number_found = self.__get_number_from_number_item__(xpath_numbers)
            if product_category in category_number_dict:
                category_number_dict[category_value] += number_found
            else:
                category_number_dict[category_value] = number_found
            print('url={}: found: {}'.format(url, number_found))

    def __get_number_from_number_item__(self, xpath_numbers):
        if xpath_numbers is None or len(xpath_numbers) == 0:
            return 0
        number_item = xpath_numbers[0] if type(xpath_numbers) is list else xpath_numbers
        doc_number = self.nlp(str(number_item.text_content()).replace("'", ""))
        # self._spacy.print_tokens_for_doc(doc_number)
        number_results = doc_number._.first_pos_number
        return 0 if number_results is None else number_results

    def __get_numbers_dict_from_tutti__(self, class_name: str, search_label_list: list) -> list:
        tutti_sales = []
        search_string = MyText.get_url_encode_plus(' '.join(search_label_list))
        url = self._url_helper.get_url_with_search_string(search_string)
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

    def __get_sales_from_tutti__(self, class_name: str, search_label_list: list) -> list:
        tutti_sales = []
        encoded_search_string = MyText.get_url_encode_plus(' '.join(search_label_list))
        url_list = self._url_helper.get_url_list(encoded_search_string)
        navigation_pages = ''
        for idx, url in enumerate(url_list):
            print('checking url: {}'.format(url))
            if idx > 0 and navigation_pages.find(str(idx)) < 0:
                break
            request = requests.get(url)
            # sleep(1)
            tree = html.fromstring(request.content)
            if idx == 0:
                navigations = tree.xpath('//ul[@class="{}"]'.format(SCLS.NAVIGATION_MAIN))
                for navigation in navigations:
                    navigation_pages = str(navigation.text_content())
            sales = tree.xpath('//div[@class="{}"]'.format(class_name))
            for sale_element in sales:
                sale = TuttiSale(self._spacy, self.sys_config, search_label_list)
                sale.init_by_html_element(sale_element)
                tutti_sales.append(sale)
                # sale.print_sale_in_original_structure()
        return tutti_sales

    def __can_similar_sale_be_added_to_dict__(self, similar_dict: dict, sale: TuttiSale, similar_sale: TuttiSale):
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
    def __is_found_sale_similar_to_source_sale__(found_sale: TuttiSale, source_sale: TuttiSale) -> bool:
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

