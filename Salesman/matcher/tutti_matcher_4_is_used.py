"""
Description: This module contains the matcher class for IsUsed.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc, Span
from tutti_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4IsUsed(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
            return {
            'BESCHAEDIGUNG': [{'LOWER': 'beschädigung'}],
            'FAST_NEU': [{'LOWER': 'fast'}, {'POS': 'CONJ', 'OP': '?'}, {'LOWER': 'neu'}],  # fast wie neu
            'GEBRAUCHT': [{'LOWER': 'gebraucht', 'POS': POS.VERB}],
            'GEBRAUCHSSPUREN': [{'LOWER': 'gebrauchsspuren'}],
            'GEBRAUCHSPUREN': [{'LOWER': 'gebrauchspuren'}],
            'GETRAGEN': [{'LOWER': 'getragen', 'POS': POS.VERB}],
            'BESCHAEDIGT': [{'LOWER': 'beschädigt', 'POS': POS.VERB}],
            'GUT_ERHALTEN': [{'LOWER': 'gut'}, {'LOWER': 'erhalten', 'POS': POS.VERB}],
            'GUTER_ZUSTAND': [{'LEMMA': 'gut'}, {'LOWER': 'zustand'}],
            'IN_GUTEM_ZUSTAND': [{'LOWER': 'in'}, {'LOWER': 'gutem'}, {'POS': 'ADJ', 'OP': '?'}, {'LOWER': 'zustand'}],
            'KRATZER': [{'LOWER': 'kratzer', 'POS': POS.NOUN}],
            'NEUPREIS': [{'LOWER': 'neupreis', 'POS': POS.NOUN}],
            'NICHT_MEHR': [{'LOWER': 'nicht'}, {'LOWER': 'mehr'}, {'POS': 'ADV', 'OP': '?'}, {'LOWER': 'neu'}],
            'SCHADEN': [{'LOWER': 'schaden', 'POS': POS.NOUN}],
            'FLECKEN': [{'LOWER': 'flecken', 'POS': POS.NOUN}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'BESCHAEDIGUNG': {'kleine Beschädigung liegt vor': True},
            'FAST_NEU': {'Artikel ist fast neu': True, 'Artikel is wie neu': False},
            'GEBRAUCHT': {'wenig gebraucht': True},
            'GEBRAUCHSSPUREN': {'es sind leichte Gebrauchsspuren vorhanden': True},
            'GEBRAUCHSPUREN': {'es sind leichte Gebrauchspuren vorhanden': True},
            'GETRAGEN': {'wurde kaum getragen': True},
            'BESCHAEDIGT': {'ist leicht beschädigt': True},
            'GUT_ERHALTEN': {'ist gut erhalten': True},
            'GUTER_ZUSTAND': {'ist in einem guten Zustand': True},
            'IN_GUTEM_ZUSTAND': {'ist in gutem Zustand': True},
            'KRATZER': {'die Oberfläche hat leichte Kratzer': True},
            'NEUPREIS': {'ist gut erhalten': True},
            'NICHT_MEHR': {'ist gut erhalten': True},
            'SCHADEN': {'ein kleiner Schaden vorhanden': True},
            'FLECKEN': {'die Flecken auf der Oberseite': True},
        }

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_bool__(doc)