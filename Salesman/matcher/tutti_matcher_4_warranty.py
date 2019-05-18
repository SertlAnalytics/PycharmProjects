"""
Description: This module contains the matcher class for Size.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc, Span
from sertl_analytics.constants.salesman_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4Warranty(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'GARANTIE_BIS_DATE': [{'LOWER': 'garantie'}, {'POS': POS.VERB, 'OP': '?'},{'POS': POS.ADV, 'OP': '?'},
                                  {'POS': POS.ADP, 'OP': '?'}, {'SHAPE': 'dd.dd.dddd'}],
            'GARANTIE_BIS_YEAR': [{'LOWER': 'garantie'}, {'POS': POS.VERB, 'OP': '?'}, {'POS': POS.ADV, 'OP': '?'},
                                  {'POS': POS.ADP, 'OP': '?'}, {'POS': POS.NUM}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'GARANTIE_BIS_DATE': {'Garantie läuft noch bis 09.11.2020': '09.11.2020',
                                  'Garantie bis 09.12.2020': '09.12.2020',},
            'GARANTIE_BIS_YEAR': {'Garantie bis 2022': '2022'},
        }

    def __get_pattern_result_for_doc_as_text__(self, doc: Doc):
        for match_id, start, end in self._matcher(doc):
            return doc[end - 1].text
        return ''

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_text__(doc)
