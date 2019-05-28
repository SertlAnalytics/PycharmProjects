"""
Description: This module contains the matcher class for IsNew
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc
from sertl_analytics.constants.salesman_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4Renting(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'MIETE': [{'LEMMA': 'miete'}],
            'VERMIETEN': [{'LEMMA': 'vermieten'}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'MIETE': {'Das Haus ist zur Miete bis Ende des Jahres': True},
            'VERMIETEN': {'Im schönen Dorf Brittnau vermieten wir an bester Lage': True},
        }

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_bool__(doc)

