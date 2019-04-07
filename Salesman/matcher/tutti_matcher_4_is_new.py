"""
Description: This module contains the matcher class for IsNew
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc, Span
from tutti_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4IsNew(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'NEUWERTIG': [{'LOWER': 'neuwertig'}],
            'NEUWERTIGEN': [{'LOWER': 'neuwertigen'}],
            'NEUWERTIGEM': [{'LOWER': 'neuwertigem'}],
            'ORIGINALVERPACKT': [{'LOWER': 'originalverpackt'}],
            'ORIGINALVERPACKUNG': [{'LOWER': 'originalverpackung'}],
            'WIE_NEU': [{'POS': 'ADJ', 'OP': '?'}, {'LOWER': 'neu'}],
            'ZUSTAND_SEHR_GUT':
                [{'LOWER': 'zustand'}, {'POS': POS.PUNCT, 'OP': '?'}, {'LOWER': 'sehr'}, {'LOWER': 'gut'}],
            'SEHR_GUTEM_ZUSTAND': [{'LOWER': 'sehr'}, {'LEMMA': 'gut'}, {'LOWER': 'zustand'}],
            'NEU': [{'LOWER': 'neu'}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'NEUWERTIG': {'ist neuwertig': True},
            'NEUWERTIGEN': {'Ich verkaufe meine neuwertigen Damen Wanderschuhe': True},
            'NEUWERTIGEM': {'Weisser USM Haller Tisch in neuwertigem Zustand': True},
            'ORIGINALVERPACKT': {'ist noch originalverpackt': True},
            'ORIGINALVERPACKUNG': {'die Originalverpackung ist vorhanden': True},
            'WIE_NEU': {'der Tisch ist wie neu': True},
            'ZUSTAND_SEHR_GUT': {'Zustand: sehr gut': True},
            'SEHR_GUTEM_ZUSTAND': {'der Tisch ist in sehr gutem Zustand': True},
            'NEU': {'der Tisch ist neu': True, 'der Tisch ist veraltet': False},
        }

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_bool__(doc)

