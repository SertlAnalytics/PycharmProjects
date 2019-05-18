"""
Description: This module contains the matcher class for Size.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc, Span
from sertl_analytics.constants.salesman_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4Age(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'JAHRE_ALT': [{'POS': POS.NUM}, {'LEMMA': 'Jahr'}, {'LEMMA': 'alt'}],
            'MONATE_ALT': [{'POS': POS.NUM}, {'LEMMA': 'Monat'}, {'LEMMA': 'alt'}],
            'JAHRE_GEBRAUCHT': [{'POS': POS.NUM}, {'LEMMA': 'Jahr'}, {'LEMMA': 'gebrauchen'}],
            'MONATE_GEBRAUCHT': [{'POS': POS.NUM}, {'LEMMA': 'Monat'}, {'LEMMA': 'gebrauchen'}],
            'JAHRE_BENUTZT': [{'POS': POS.NUM}, {'LEMMA': 'Jahr'}, {'LEMMA': 'benutzen'}],
            'MONATE_BENUTZT': [{'POS': POS.NUM}, {'LEMMA': 'Monat'}, {'LEMMA': 'benutzen'}],
            'VOR_JAHREN_GEKAUFT': [{'LOWER': 'vor'}, {'POS': POS.NUM}, {'LEMMA': 'Jahr'}, {'LEMMA': 'kaufen'}],
            'VOR_MONATEN_GEKAUFT': [{'LOWER': 'vor'}, {'POS': POS.NUM}, {'LEMMA': 'Monat'}, {'LEMMA': 'kaufen'}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'JAHRE_ALT': {'Der Stuhl ist 5 Jahre alt': '5 Jahre',
                          'Verkaufe ca. 3 Jahre alte Nespresso': '3 Jahre'},
            'MONATE_ALT': {'Der Tisch ist 7 Monate alt': '7 Monate'},
            'JAHRE_GEBRAUCHT': {'Der Stuhl wurde 5 Jahre gebraucht': '5 Jahre'},
            'MONATE_GEBRAUCHT': {'Der Tisch wurde nur 7 Monate gebraucht': '7 Monate'},
            'JAHRE_BENUTZT': {'Der Stuhl wurde 5 Jahre benutzt': '5 Jahre'},
            'MONATE_BENUTZT': {'Der Tisch wurde nur 7 Monate benutzt': '7 Monate'},
            'VOR_JAHREN_GEKAUFT': {'Der Stuhl wurde vor 5 Jahren gekauft': '5 Jahren'},
            'VOR_MONATEN_GEKAUFT': {'Der Tisch wurde vor 7 Monaten gekauft': '7 Monaten'},
        }

    def __get_pattern_result_for_doc_as_text__(self, doc: Doc):
        for match_id, start, end in self._matcher(doc):
            # print('{}: doc[end - 1].text={}'.format(doc.text, doc[end-1].text))
            span = Span(doc, end - 3, end - 1)
            return span.text
        return ''

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_text__(doc)
