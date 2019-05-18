"""
Description: This module contains the matcher class for IsNew
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc
from sertl_analytics.constants.salesman_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4CoverAvailable(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'ORIGINALVERPACKT': [{'LOWER': 'originalverpackt'}],
            'IN_ORIGINALVERPACKUNG': [{'LOWER': 'in'}, {'LOWER': 'der', 'OP': '?'}, {'LOWER': 'originalverpackung'}],
            'ORIGINALVERPACKUNG_VORHANDEN': [
                {'LOWER': 'originalverpackung'}, {'LOWER': 'ist', 'OP': '?'}, {'LOWER': 'vorhanden'}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'ORIGINALVERPACKT': {'ist noch originalverpackt': True},
            'IN_ORIGINALVERPACKUNG': {'die Vase ist in der Originalverpackung': True,
                                      'der TV ist in Originalverpackung': True},
            'ORIGINALVERPACKUNG_VORHANDEN': {'die Originalverpackung ist vorhanden': True,
                                             'Originalverpackung vorhanden': True},
        }

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_bool__(doc)

