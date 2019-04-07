"""
Description: This module is the base class for our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from tutti_browser import MyUrlBrowser4Tutti
from tutti_offer import TuttiOffer
from spacy import displacy
from tutti_spacy import TuttiSpacy
from sertl_analytics.mydates import MyDate
from tutti_constants import TC
import pandas as pd
import xlsxwriter
from xlsxwriter import Workbook


class Tutti:
    def __init__(self, with_browser=True, with_nlp=True, write_to_excel=False, load_sm=True):
        self._write_to_excel = write_to_excel
        self._spacy = TuttiSpacy(load_sm=load_sm) if with_nlp else None
        self._my_offers = None
        self._my_virtual_offers = None
        self._similar_offer_dict = {}  # key is the ID of my_offer
        self._browser = MyUrlBrowser4Tutti(self._spacy.nlp) if with_browser else None
        if self._browser is not None:
            self._browser.enter_and_submit_credentials()
        self._virtual_offers_file_path = "tutti_virtual_offers.csv"
        self._excel_file_path = 'tutti_offers.xlsx'

    @property
    def nlp(self):
        return None if self._spacy is None else self._spacy.nlp

    def check_my_nth_offer_against_similar_offers(self, number=1):
        offer = self._browser.get_my_nth_offer_from_tutti(number)
        if offer is None:
            return
        offer.print_offer_in_original_structure()
        self._similar_offer_dict = self._browser.get_similar_offer_dict_from_tutti([offer])
        self.__check_similarity__([offer], self._similar_offer_dict)
        self.__write_to_excel__([offer], self._similar_offer_dict)

    def check_my_nth_virtual_offer_against_similar_offers(self, number=1):
        list_with_nth_offer = self.__get_my_virtual_offers__(number)
        self._similar_offer_dict = self._browser.get_similar_offer_dict_from_tutti(list_with_nth_offer)
        self.__check_similarity__(list_with_nth_offer, self._similar_offer_dict)
        self.__write_to_excel__(list_with_nth_offer, self._similar_offer_dict)

    def check_my_offers_against_similar_offers(self):
        self._my_offers = self._browser.get_my_offers_from_tutti()
        self._similar_offer_dict = self._browser.get_similar_offer_dict_from_tutti(self._my_offers)
        self.__check_similarity__(self._my_offers, self._similar_offer_dict)
        self.__write_to_excel__(self._my_offers, self._similar_offer_dict)

    def check_my_virtual_offers_against_similar_offers(self):
        self._my_virtual_offers = self.__get_my_virtual_offers__()
        self._similar_offer_dict = self._browser.get_similar_offer_dict_from_tutti(self._my_virtual_offers)
        self.__check_similarity__(self._my_virtual_offers, self._similar_offer_dict)
        self.__write_to_excel__(self._my_virtual_offers, self._similar_offer_dict)

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

    def __write_to_excel__(self, my_offers: list, similar_offer_dict: dict):
        if not self._write_to_excel:
            return
        excel_workbook = xlsxwriter.Workbook(self._excel_file_path)
        excel_workbook.add_worksheet('Similar offers')
        worksheet = excel_workbook.get_worksheet_by_name('Similar offers')
        row_list = []
        columns = TC.get_columns_for_excel()
        for col_number, col in enumerate(columns):
            worksheet.write(0, col_number, col)
        try:
            for my_offer in my_offers:
                row_list.append(my_offer.get_value_dict_for_worksheet())
                similar_offers = similar_offer_dict[my_offer.id]
                for similar_offer in similar_offers:
                    row_list.append(similar_offer.get_value_dict_for_worksheet(my_offer.id))
            for idx, value_dict in enumerate(row_list):
                row_number = idx + 1
                for col_number, col in enumerate(columns):
                    if col in value_dict:
                        value = value_dict[col]
                        worksheet.write(row_number, col_number, value)
        finally:
            excel_workbook.close()

    def __get_my_virtual_offers__(self, number=0):
        tutti_offers = []
        virtual_offer_df = self.__get_offer_elements_from_file__()
        for idx, row in virtual_offer_df.iterrows():
            print('idx={} - row={}'.format(idx, row[TC.TITLE]))
        for idx, row in virtual_offer_df.iterrows():
            if number == 0 or idx == number - 1:
                tutti_offer = self.__get_tutti_offer_from_file_row__(row, idx)
                tutti_offers.append(tutti_offer)
        return tutti_offers

    def __get_offer_elements_from_file__(self) -> pd.DataFrame:
        df = pd.read_csv(self._virtual_offers_file_path, delimiter='#', header=None)
        df.columns = TC.get_columns_for_virtual_offers_in_file()
        return df

    def __get_tutti_offer_from_file_row__(self, file_row, number: int):
        offer = TuttiOffer(self.nlp)
        offer.init_by_file_row(number, file_row)
        offer.print_offer_in_original_structure()
        return offer

    def __visualize_dependencies__(self):
        for offer in self._my_offers:
            doc_dict = {'Title': self.nlp(offer.title), 'Description': self.nlp(offer.description)}
            for key, doc in doc_dict.items():
                displacy.render(doc, style='dep')
                displacy.render(doc, style='ent')

