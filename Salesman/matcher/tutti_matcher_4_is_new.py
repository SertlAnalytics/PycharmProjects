"""
Description: This module contains the matcher class for IsNew
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc
from sertl_analytics.constants.salesman_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4IsNew(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'FABRIKNEU': [{'LOWER': 'fabrikneu'}],
            'NEU': [{'LOWER': 'neu', 'POS': POS.ADJ}],
            'ORIGINALVERPACKT': [{'LOWER': 'originalverpackt'}],
            'NOCH_NICHT_BENUTZT': [{'LOWER': 'noch'}, {'LOWER': 'nicht'}, {'LOWER': 'benutzt'}],
            'NOCH_NIE_GETRAGEN': [{'LOWER': 'noch'}, {'LOWER': 'nie'}, {'LOWER': 'getragen'}],
            'UNBENUTZT': [{'LOWER': 'unbenutzt'}],
            'UNGEBRAUCHT': [{'LOWER': 'ungebraucht'}],

        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'FABRIKNEU': {'Der Artikel ist fabrikneu und original-verpackt!': True},
            'NEU': {'der Tisch ist neu': True, 'der Tisch ist veraltet': False},
            'ORIGINALVERPACKT': {'ist noch originalverpackt': True},
            'NOCH_NICHT_BENUTZT': {'der TV wurde noch nicht benutzt': True},
            'NOCH_NIE_GETRAGEN': {'Neu (noch nie getragen) da zu klein gekauft': True},
            'UNBENUTZT': {'der Tisch ist noch unbenutzt': True},
            'UNGEBRAUCHT': {'der Stuhl ist noch ungebraucht': True},
        }

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_bool__(doc)

