"""
Description: This module contains the matcher class for IsSinglePrice.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc
from salesman_tutti.tutti_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4IsSinglePrice(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
            return {
                'STUECKPREIS': [{'LOWER': 'stückpreis'}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'STUECKPREIS': {'4 Stück vorhanden. Stückpreis': True},
        }

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_bool__(doc)