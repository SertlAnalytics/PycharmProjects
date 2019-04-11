"""
Description: This module contains the matcher class for Original Price.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc, Span
from tutti_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4OriginalPrize(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'CA': [{'LOWER': 'ca.'}, {'POS': POS.NUM}],  # ca. 2800.- 18 Stk vorhanden
            'NEUPREIS': [{'LOWER': 'neupreis'}, {'POS': POS.NUM}],
            'NEUPREIS_ADJ': [{'LOWER': 'neupreis'}, {'POS': POS.ADJ}],
            'GEKAUFT': [{'LOWER': 'gekauft'}, {'POS': POS.ADP}, {'POS': POS.NUM}],
            'CHF': [{'LOWER': 'chf'}, {'POS': POS.NUM}],
            'CHF_PROPN': [{'LOWER': 'chf'}, {'POS': POS.PROPN}],
            'CHF_NOUN': [{'LOWER': 'chf'}, {'POS': POS.NOUN}],
            'NP': [{'LOWER': 'np'}, {'POS': POS.PUNCT}, {'POS': POS.NUM}],  # NP: 2800.- 18 Stk vorhanden
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'CA': {'Topstühle! NP ca. 2900.- 18 Stk vorhanden': 2900},
            'NEUPREIS': {'Rückenlehne verstellbar Neupreis 2300.- gestern': 2300},
            'NEUPREIS_ADJ': {'Neupreis 1234.- 18 Stk vorhanden': 1234},
            'GEKAUFT': {'gekauft für 1000.- 18 Stk vorhanden': 1000},
            'CHF': {'CHF 245.- war Neupreis': 245,
                    'Neupreis gemäss Vitra-Homepage: CHF 3858.-': 3858},
            'CHF_PROPN': {'CHF 34.- war Neupreis': 34},
            'CHF_NOUN': {'CHF 32.- war Neupreis': 32},
            'NP': {'Topstühle! NP: 2800.- 18 Stk vorhanden': 2800},
        }

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_int__(doc)