"""
Description: This module is the base class for our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""
from sertl_analytics.constants.salesman_constants import ODC
from salesman_database.access_layer.access_layer_offer import AccessLayer4Offer
from tutti_browser import MyUrlBrowser4Tutti
from lxml import html
from tutti_offer import TuttiOffer
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
        self._my_offers_source = 'Tutti'
        self._write_to_excel = self.sys_config.write_to_excel
        self._spacy = TuttiSpacy(load_sm=self.sys_config.load_sm) if self.sys_config.with_nlp else None
        self._browser = MyUrlBrowser4Tutti(self.sys_config, self._spacy) if self.sys_config.with_browser else None
        self._url_search_switzerland = 'https://www.tutti.ch/de/li/ganze-schweiz/angebote?q='
        if self._browser is not None:
            self._browser.enter_and_submit_credentials()
        self._virtual_offers_file_path = "Files/tutti_virtual_offers.csv"
        self._access_layer = AccessLayer4Offer(self.sys_config.db)

    @property
    def nlp(self):
        return None if self._spacy is None else self._spacy.nlp

    @property
    def excel_file_path(self):
        return 'Files/tutti_offers_result.xlsx' if self._my_offers_source == 'Tutti' \
            else 'Files/tutti_offers_virtual_result.xlsx'

    def check_my_nth_offer_against_similar_offers(self, number=1):
        offer = self._browser.get_my_nth_offer_from_tutti(number)
        if offer is None:
            return
        offer.print_offer_in_original_structure()
        similar_offer_dict = self.__get_similar_offer_dict_from_tutti__([offer])
        self.__process_my_offers_and_similar_offers__([offer], similar_offer_dict)

    def check_my_nth_virtual_offer_against_similar_offers(self, number=1):
        list_with_nth_offer = self.__get_my_virtual_offers__(number)
        similar_offer_dict = self.__get_similar_offer_dict_from_tutti__(list_with_nth_offer)
        self.__process_my_offers_and_similar_offers__(list_with_nth_offer, similar_offer_dict)

    def check_my_offers_against_similar_offers(self):
        my_offers = self._browser.get_my_offers_from_tutti()
        similar_offer_dict = self.__get_similar_offer_dict_from_tutti__(my_offers)
        self.__process_my_offers_and_similar_offers__(my_offers, similar_offer_dict)

    def check_my_virtual_offers_against_similar_offers(self):
        my_virtual_offers = self.__get_my_virtual_offers__()
        similar_offer_dict = self.__get_similar_offer_dict_from_tutti__(my_virtual_offers)
        self.__process_my_offers_and_similar_offers__(my_virtual_offers, similar_offer_dict)

    def __process_my_offers_and_similar_offers__(self, my_offers: list, similar_offer_dict: dict):
        self.__check_similarity__(my_offers, similar_offer_dict)
        self.__write_to_excel__(my_offers, similar_offer_dict)
        self.__write_to_database__(my_offers, similar_offer_dict)

    def __check_similarity__(self, my_offers: list, similar_offer_dict: dict):
        if self._spacy.sm_loaded:
            return
        for my_offer in my_offers:
            my_offer_title_doc = self.nlp(my_offer.title)
            similar_offers = similar_offer_dict[my_offer.id]
            for similar_offer in similar_offers:
                similar_offer_title_doc = self.nlp(similar_offer.title)
                similarity = my_offer_title_doc.similarity(similar_offer_title_doc)
                similarity_text = self._spacy.get_similarity_text(similarity)
                print('Similarity between {} and {}: {} ({})'.format(
                    my_offer.title, similar_offer.title, similarity, similarity_text
                ))

    @staticmethod
    def __identify_outliers__(similar_offer_dict: dict):
        if len(similar_offer_dict) == 0:
            return
        price_single_list = [similar_offer.price_single for similar_offer in similar_offer_dict.values()]
        pct_bottom = np.percentile(price_single_list, 15)
        pct_top = np.percentile(price_single_list, 85)
        for similar_offer in similar_offer_dict.values():
            is_outlier = similar_offer.price_single < pct_bottom or similar_offer.price_single > pct_top
            similar_offer.set_is_outlier(True if is_outlier else False)

    def __write_to_excel__(self, my_offers: list, similar_offer_dict: dict):
        if not self._write_to_excel:
            return
        excel_workbook = xlsxwriter.Workbook(self.excel_file_path)
        excel_workbook.add_worksheet('Similar offers')
        worksheet = excel_workbook.get_worksheet_by_name('Similar offers')
        row_list = []
        columns = ODC.get_columns_for_excel()
        for col_number, col in enumerate(columns):
            worksheet.write(0, col_number, col)
        try:
            for my_offer in my_offers:
                row_list.append(my_offer.get_value_dict_for_worksheet())
                similar_offers = similar_offer_dict[my_offer.id]
                for similar_offer in similar_offers:
                    row_list.append(similar_offer.get_value_dict_for_worksheet(my_offer.id))
            for idx, value_dict in enumerate(row_list):
                # print(value_dict)
                row_number = idx + 1
                for col_number, col in enumerate(columns):
                    if col in value_dict:
                        value = value_dict[col]
                        worksheet.write(row_number, col_number, value)
        finally:
            excel_workbook.close()

    def __write_to_database__(self, my_offers: list, similar_offer_dict: dict):
        if not self.sys_config.write_offers_to_database:
            return
        input_list = []
        for my_offer in my_offers:
            self.__add_offer_to_database_input_list__(my_offer, input_list)
            similar_offers = similar_offer_dict[my_offer.id]
            for similar_offer in similar_offers:
                self.__add_offer_to_database_input_list__(similar_offer, input_list)
        try:
            if len(input_list) > 0:
                self.sys_config.db.insert_offer_data(input_list)
        finally:
            print('{} offers written to database...'.format(len(input_list)))

    def __add_offer_to_database_input_list__(self, offer: TuttiOffer, input_list: list):
        if offer.is_offer_ready_for_offer_table():
            offer_dict = offer.data_dict_obj.get_data_dict_for_offer_table()
            if not self._access_layer.is_offer_with_offer_id_available(offer.id):
                input_list.append(offer_dict)

    def __get_my_virtual_offers__(self, number=0):
        self._my_offers_source = 'virtual'
        tutti_offers = []
        virtual_offer_df = self.__get_offer_elements_from_file__()
        for idx, row in virtual_offer_df.iterrows():
            print('idx={} - row={}'.format(idx, row[ODC.TITLE]))
            if number == 0 or idx == number - 1:
                tutti_offer = self.__get_tutti_offer_from_file_row__(row)
                tutti_offers.append(tutti_offer)
        return tutti_offers

    def __get_offer_elements_from_file__(self) -> pd.DataFrame:
        df = pd.read_csv(self._virtual_offers_file_path, delimiter='#', header=None)
        df.columns = ODC.get_columns_for_virtual_offers_in_file()
        return df

    def __get_tutti_offer_from_file_row__(self, file_row):
        offer = TuttiOffer(self._spacy, self.sys_config)
        offer.init_by_file_row(file_row)
        offer.set_source(self._virtual_offers_file_path)
        offer.print_offer_in_original_structure()
        return offer

    def __visualize_dependencies__(self, my_offers: list):
        for offer in my_offers:
            doc_dict = {'Title': self.nlp(offer.title), 'Description': self.nlp(offer.description)}
            for key, doc in doc_dict.items():
                displacy.render(doc, style='dep')
                displacy.render(doc, style='ent')

    def __get_similar_offer_dict_from_tutti__(self, offers: list):  # key is the ID of my_offer
        return {offer.id: self.__get_similar_offers_for_offer__(offer) for offer in offers}

    def __get_similar_offers_for_offer__(self, offer: TuttiOffer) -> list:
        similar_offer_dict = {}
        start_search_label_lists = offer.get_start_search_label_lists()
        print('\nStart_search_label_lists={}'.format(start_search_label_lists))
        for start_search_label_list in start_search_label_lists:
            self.__get_offers_from_tutti_for_next_search_level__(
                similar_offer_dict, start_search_label_list, offer)
        self.__identify_outliers__(similar_offer_dict)
        similar_offers_summary = [offer for offer in similar_offer_dict.values()]
        self.__print_similar_offers__(offer, similar_offers_summary)
        return similar_offers_summary

    def __get_offers_from_tutti_for_next_search_level__(
            self, similar_offer_dict: dict, parent_search_label_list: list, offer: TuttiOffer):
        similar_offers = self.__get_offers_from_tutti__(SCLS.OFFERS, parent_search_label_list)
        added_flag = False
        for similar_offer in similar_offers:
            if self.__can_similar_offer_be_added_to_dict__(similar_offer_dict, offer, similar_offer):
                similar_offer.set_master_id(offer.id)
                similar_offer.set_source('Tutti')
                similar_offer_dict[similar_offer.id] = similar_offer
                added_flag = True
        if added_flag:  # recursive call !!!
            next_parent_search_label_list = offer.get_label_list_with_child_labels(parent_search_label_list)
            for search_label_list in next_parent_search_label_list:
                self.__get_offers_from_tutti_for_next_search_level__(
                    similar_offer_dict, search_label_list, offer)

    def __get_offers_from_tutti__(self, class_name: str, parent_search_label_list: list) -> list:
        tutti_offers = []
        search_string = ' '.join(parent_search_label_list)
        url = '{}{}'.format(self._url_search_switzerland, search_string)
        # print('Searching for {}'.format(url))
        request = requests.get(url)
        sleep(3)
        tree = html.fromstring(request.content)
        offers = tree.xpath('//div[@class="{}"]'.format(class_name))
        for offer_element in offers:
            offer = TuttiOffer(self._spacy, self.sys_config, parent_search_label_list)
            offer.init_by_html_element(offer_element)
            tutti_offers.append(offer)
            # offer.print_offer_in_original_structure()
        return tutti_offers

    def __can_similar_offer_be_added_to_dict__(self, similar_dict: dict, offer: TuttiOffer, similar_offer: TuttiOffer):
        if similar_offer.id == offer.id:
            return False
        if not self.__is_found_offer_similar_to_source_offer__(similar_offer, offer):
            print('Found offer "{}" not similar to "{}"'.format(similar_offer.title, offer.title))
            return False
        if similar_offer.id not in similar_dict:
            return True
        return len(similar_offer.found_by_labels) > len(similar_dict[similar_offer.id].found_by_labels)

    @staticmethod
    def __is_found_offer_similar_to_source_offer__(found_offer: TuttiOffer, source_offer: TuttiOffer) -> bool:
        is_company_available = found_offer.is_any_term_in_list_in_title(source_offer.company_list)
        is_product_available = found_offer.is_any_term_in_list_in_title(source_offer.product_list)
        is_object_available = found_offer.is_any_term_in_list_in_title_or_description(source_offer.object_list)
        return is_company_available and is_product_available and is_object_available

    @staticmethod
    def __print_similar_offers__(offer, similar_offers: list):
        offer.print_offer_in_original_structure()
        if len(similar_offers) == 0:
            print('\nNO SIMILAR OFFERS AVAILABLE for {}'.format(offer.key))
        for similar_offer in similar_offers:
            similar_offer.print_offer_in_original_structure()

