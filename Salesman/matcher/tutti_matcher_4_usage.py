"""
Description: This module contains the matcher class for Usage.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc, Span
from sertl_analytics.constants.salesman_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4Usage(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'LAUFLEISTUNG': [{'POS': POS.NUM}, {'POS': POS.X}, {'LOWER': 'laufleistung'}],
            'PERIOD_GEBRAUCHT': [{'POS': POS.NUM}, {'POS': POS.NOUN}, {'LEMMA': 'gebrauchen'}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'LAUFLEISTUNG': {'Neuwertig ca. 2000 km Laufleistung': '2000 km'},
            'PERIOD_GEBRAUCHT': {'Der Artikel wurde nur 2 Jahre gebraucht': '2 Jahre'},
        }

    def __get_pattern_result_for_doc_as_text__(self, doc: Doc):
        for match_id, start, end in self._matcher(doc):
            if doc[end - 1].text.lower() in ['laufleistung', 'gebraucht']:
                return Span(doc, start, start + 2).text
            return doc[end - 1].text
        return ''

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_text__(doc)
