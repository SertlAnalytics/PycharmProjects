"""
Description: This module is the base class for our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""
from sertl_analytics.constants.salesman_constants import SLDC, SLSRC
from salesman_database.access_layer.access_layer_sale import AccessLayer4Sale
from tutti_browser import MyUrlBrowser4Tutti
from lxml import html
from tutti_sale import TuttiSale
from spacy import displacy
from tutti_spacy import TuttiSpacy
from tutti_constants import SCLS
import pandas as pd
import xlsxwriter
import requests
from time import sleep
import numpy as np
from salesman_system_configuration import SystemConfiguration


class Tutti:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self._my_sales_source = SLSRC.TUTTI_CH
        self._write_to_excel = self.sys_config.write_to_excel
        self._spacy = TuttiSpacy(load_sm=self.sys_config.load_sm) if self.sys_config.with_nlp else None
        self._browser = None
        self._url_search_switzerland = 'https://www.tutti.ch/de/li/ganze-schweiz/angebote?q='
        self._access_layer = AccessLayer4Sale(self.sys_config.db)

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

    def check_my_nth_sale_against_similar_sales(self, number=1):
        sale = self.browser.get_my_nth_sale_from_tutti(number)
        if sale is None:
            return
        sale.print_sale_in_original_structure()
        similar_sales_dict = self.__get_similar_sale_dict_from_tutti__([sale])
        self.__process_my_sales_and_similar_sales__([sale], similar_sales_dict)

    def check_my_nth_virtual_sale_against_similar_sales(self, number=1):
        list_with_nth_sale = self.__get_my_virtual_sales__(number)
        similar_sale_dict = self.__get_similar_sale_dict_from_tutti__(list_with_nth_sale)
        self.__process_my_sales_and_similar_sales__(list_with_nth_sale, similar_sale_dict)

    def get_similar_sales_from_online_inputs(self, title: str, description: str):
        list_with_sale = self.__get_my_online_sales__(title, description)
        similar_sale_dict = self.__get_similar_sale_dict_from_tutti__(list_with_sale)
        return self.__get_similar_sales_as_dict__(list_with_sale, similar_sale_dict)

    def check_my_sales_against_similar_sales(self):
        my_sales = self._browser.get_my_sales_from_tutti()
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

    def __check_similarity__(self, my_sales: list, similar_sale_dict: dict):
        if self._spacy.sm_loaded:
            return
        for my_sale in my_sales:
            my_sale_title_doc = self.nlp(my_sale.title)
            similar_sales = similar_sale_dict[my_sale.id]
            for similar_sale in similar_sales:
                similar_sale_title_doc = self.nlp(similar_sale.title)
                similarity = my_sale_title_doc.similarity(similar_sale_title_doc)
                similarity_text = self._spacy.get_similarity_text(similarity)
                print('Similarity between {} and {}: {} ({})'.format(
                    my_sale.title, similar_sale.title, similarity, similarity_text
                ))

    @staticmethod
    def __identify_outliers__(similar_sale_dict: dict):
        if len(similar_sale_dict) == 0:
            return
        price_single_list = [similar_sale.price_single for similar_sale in similar_sale_dict.values()]
        pct_bottom = np.percentile(price_single_list, 15)
        pct_top = np.percentile(price_single_list, 85)
        for similar_sale in similar_sale_dict.values():
            is_outlier = similar_sale.price_single < pct_bottom or similar_sale.price_single > pct_top
            similar_sale.set_is_outlier(True if is_outlier else False)

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
                similar_sales = similar_sale_dict[my_sale.id]
                for similar_sale in similar_sales:
                    row_list.append(similar_sale.get_value_dict_for_worksheet(my_sale.id))
            for idx, value_dict in enumerate(row_list):
                # print(value_dict)
                row_number = idx + 1
                for col_number, col in enumerate(columns):
                    if col in value_dict:
                        value = value_dict[col]
                        worksheet.write(row_number, col_number, value)
        finally:
            excel_workbook.close()

    def __write_to_database__(self, my_sales: list, similar_sale_dict: dict):
        if not self.sys_config.write_to_database:
            return
        input_list = []
        for my_sale in my_sales:
            self.__add_sale_to_database_input_list__(my_sale, input_list)
            similar_sales = similar_sale_dict[my_sale.id]
            for similar_sale in similar_sales:
                self.__add_sale_to_database_input_list__(similar_sale, input_list)
        try:
            if len(input_list) > 0:
                self.sys_config.db.insert_sale_data(input_list)
        finally:
            print('{} sales written to database...'.format(len(input_list)))

    def __add_sale_to_database_input_list__(self, sale: TuttiSale, input_list: list):
        if sale.is_sale_ready_for_sale_table():
            sale_dict = sale.data_dict_obj.get_data_dict_for_sale_table()
            if not self._access_layer.is_sale_with_id_available(sale.id):
                input_list.append(sale_dict)

    def __get_similar_sales_as_dict__(self, my_sales: list, similar_sale_dict: dict):
        return_list = []
        for my_sale in my_sales:
            similar_sales = similar_sale_dict[my_sale.id]
            for similar_sale in similar_sales:
                if similar_sale.is_sale_ready_for_sale_table():
                    sale_dict = similar_sale.data_dict_obj.get_data_dict_for_sale_table()
                    return_list.append(sale_dict)
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

    def __get_my_online_sales__(self, title: str, description: str):
        self._my_sales_source = 'online'
        sale = TuttiSale(self._spacy, self.sys_config)
        sale.init_by_online_input(title, description)
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
        return {sale.id: self.__get_similar_sales_for_sale__(sale) for sale in sales}

    def __get_similar_sales_for_sale__(self, sale: TuttiSale) -> list:
        similar_sale_dict = {}
        start_search_label_lists = sale.get_start_search_label_lists()
        print('\nStart_search_label_lists={}'.format(start_search_label_lists))
        for start_search_label_list in start_search_label_lists:
            self.__get_sales_from_tutti_for_next_search_level__(
                similar_sale_dict, start_search_label_list, sale)
        self.__identify_outliers__(similar_sale_dict)
        similar_sales_summary = [sale for sale in similar_sale_dict.values()]
        self.__print_similar_sales__(sale, similar_sales_summary)
        return similar_sales_summary

    def __get_sales_from_tutti_for_next_search_level__(
            self, similar_sales_dict: dict, parent_search_label_list: list, sale: TuttiSale):
        similar_sales = self.__get_sales_from_tutti__(SCLS.OFFERS, parent_search_label_list)
        added_flag = False
        for similar_sale in similar_sales:
            if self.__can_similar_sale_be_added_to_dict__(similar_sales_dict, sale, similar_sale):
                similar_sale.set_master_id(sale.id)
                similar_sale.set_source(SLSRC.TUTTI_CH)
                similar_sales_dict[similar_sale.id] = similar_sale
                added_flag = True
        if added_flag:  # recursive call !!!
            next_parent_search_label_list = sale.get_label_list_with_child_labels(parent_search_label_list)
            for search_label_list in next_parent_search_label_list:
                self.__get_sales_from_tutti_for_next_search_level__(
                    similar_sales_dict, search_label_list, sale)

    def __get_sales_from_tutti__(self, class_name: str, parent_search_label_list: list) -> list:
        tutti_sales = []
        search_string = ' '.join(parent_search_label_list)
        url = '{}{}'.format(self._url_search_switzerland, search_string)
        # print('Searching for {}'.format(url))
        request = requests.get(url)
        sleep(3)
        tree = html.fromstring(request.content)
        sales = tree.xpath('//div[@class="{}"]'.format(class_name))
        for sale_element in sales:
            sale = TuttiSale(self._spacy, self.sys_config, parent_search_label_list)
            sale.init_by_html_element(sale_element)
            tutti_sales.append(sale)
            # sale.print_sale_in_original_structure()
        return tutti_sales

    def __can_similar_sale_be_added_to_dict__(self, similar_dict: dict, sale: TuttiSale, similar_sale: TuttiSale):
        if similar_sale.id == sale.id:
            return False
        if not self.__is_found_sale_similar_to_source_sale__(similar_sale, sale):
            print('Found sale "{}" not similar to "{}"'.format(similar_sale.title, sale.title))
            return False
        if similar_sale.id not in similar_dict:
            return True
        return len(similar_sale.found_by_labels) > len(similar_dict[similar_sale.id].found_by_labels)

    @staticmethod
    def __is_found_sale_similar_to_source_sale__(found_sale: TuttiSale, source_sale: TuttiSale) -> bool:
        is_company_available = found_sale.is_any_term_in_list_in_title(source_sale.company_list)
        is_product_available = found_sale.is_any_term_in_list_in_title(source_sale.product_list)
        is_object_available = found_sale.is_any_term_in_list_in_title_or_description(source_sale.object_list)
        return is_company_available and is_product_available and is_object_available

    @staticmethod
    def __print_similar_sales__(sale, similar_sales: list):
        sale.print_sale_in_original_structure()
        if len(similar_sales) == 0:
            print('\nNO SIMILAR SALES AVAILABLE for {}'.format(sale.key))
        for sale in similar_sales:
            sale.print_sale_in_original_structure()

