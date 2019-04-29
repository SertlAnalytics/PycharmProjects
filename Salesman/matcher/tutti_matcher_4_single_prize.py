"""
Description: This module contains the matcher class for SinglePrize.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc, Span
from tutti_constants import POS, DEP
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4SinglePrize(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'VERKAUFSPREIS': [{'LOWER': 'verkaufspreis'}, {'POS': POS.NUM}],  # Verkaufspreispreis 79.- pro Stück
            'VERKAUFSPREIS_NOUN': [{'LOWER': 'verkaufspreis'}, {'POS': POS.NOUN}],  # Verkaufspreispreis 79.- pro Stück
            'STUECK': [{'LOWER': 'stück'}, {'POS': POS.PUNCT}, {'POS': POS.X}],  # Preis pro Stück: 2000.-
            'PRO_STUECK': [{'POS': POS.NUM}, {'LOWER': 'pro'}, {'LOWER': 'stück'}],  # Verkaufspreispreis 79.- pro Stück
            'PRO_STUECK_nk': [{'DEP': DEP.nk}, {'LOWER': 'pro'}, {'LOWER': 'stück'}],  # Verkaufspreispreis 79.- pro Stück
            'CHF_STUECK': [{'POS': POS.NUM}, {'LOWER': 'chf/stück'}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'VERKAUFSPREIS': {'Verkaufspreis 79.-': 79},
            'VERKAUFSPREIS_NOUN': {'Verkaufspreis 79.-': 79},
            'STUECK': {'Preis pro Stück: 2000.-': 2000},
            'PRO_STUECK': {'wir verkaufen auch einzeln für 79.- pro Stück': 79},
            'PRO_STUECK_nk': {'wir verkaufen auch einzeln für 78.- pro Stück': 78},
            'CHF_STUECK': {'Verhandlungs Basis 380.- CHF/Stück': 380}
        }

    def __get_pattern_result_for_doc_as_text__(self, doc: Doc):
        for match_id, start, end in self._matcher(doc):
            if doc[end - 1].text.lower() in ['stück', 'chf/stück']:
                return doc[start].text
            return doc[end - 1].text
        return ''

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_int__(doc)