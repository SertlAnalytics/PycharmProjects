"""
Description: This module contains the matcher class for Number.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc, Span
from tutti_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4Number(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'MAL': [{'POS': POS.NUM}, {'LOWER': 'mal'}],  # 2 er set
            'SET': [{'POS': POS.NUM}, {'LOWER': 'er', 'OP': '?'}, {'LOWER': 'set'}],  # 2 er set
            'PREIS_FUER_ALLE': [{'LOWER': 'preis'}, {'LOWER': 'für'}, {'LOWER': 'alle'}, {'POS': POS.NUM}],
            'PREIS_FUER': [{'LOWER': 'preis'}, {'LOWER': 'für'}, {'POS': POS.NUM}],
            'STUECK': [{'POS': POS.NUM}, {'LOWER': 'stück'}],
            'STK': [{'POS': POS.NUM}, {'LOWER': 'stk'}],
            'DIESE': [{'LOWER': 'diese'}, {'POS': POS.NUM}],
            'BIS': [{'POS': POS.NUM}, {'POS': POS.NUM}, {'POS': POS.NUM}],
            'DESIGNKLASSIKER': [{'POS': POS.NUM}, {'LOWER': 'designklassiker'}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'MAL': {'Wir bieten den Tisch 7 Mal an': 7},
            'SET': {'Wie bieten an ein 2 er set': 2},
            'PREIS_FUER_ALLE': {'Preis für alle 34 Stück: 2000.-': 34},
            'PREIS_FUER': {'Preis für 6 Stück': 6},
            'STUECK': {'es sind insgesamt 4 Stück': 4},
            'STK': {'Stühle CONFERENCE - 3 Stk.': 3},
            'DIESE': {'DIESE 6 Stühle werden nur zusammen EN BLOC verkauft': 6},
            'BIS': {'1-5 eames alu chair vitra': 5},
            'DESIGNKLASSIKER': {'4 Designklassiker': 4},
        }

    def __get_pattern_result_for_doc_as_text__(self, doc: Doc):
        for match_id, start, end in self._matcher(doc):
            if doc[end-1].text.lower() in ['stk', 'stück', 'set', 'mal', 'designklassiker']:
                return doc[start].text
            return doc[end - 1].text
        return ''

    def get_pattern_result_for_doc(self, doc: Doc):
        number_found = self.__get_pattern_result_for_doc_as_int__(doc)
        return 1 if number_found == 0 else number_found


