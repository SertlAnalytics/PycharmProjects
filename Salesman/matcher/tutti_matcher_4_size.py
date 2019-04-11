"""
Description: This module contains the matcher class for Size.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc, Span
from tutti_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4Size(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'GROESSE': [{'LOWER': 'grösse'}, {'POS': POS.NUM}],
            'GR': [{'LOWER': 'gr'}, {'POS': POS.PUNCT}, {'POS': POS.NUM}],
            'CM': [{'POS': POS.PROPN}, {'LOWER': 'cm'}],
            # 'MASSE': [{'LOWER': 'masse'}, {'POS': POS.PUNCT, 'OP': '?'}, {'POS': POS.PROPN}],
            'PROPN_CM': [{'POS': POS.PROPN, 'OP': '?'}, {'LIKE_NUM': True}, {'LOWER': 'cm'}],
            'X_X': [{'POS': POS.NUM}, {'POS': POS.X}, {'POS': POS.NUM}, {'POS': POS.X}, {'POS': POS.NUM}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'GROESSE': {'Gr. 37': '37'},
            'GR': {'Grösse 38': '38'},
            'CM': {'Masse: Durchmesser 90 cm': 'Durchmesser 90 cm'},
            # 'MASSE': {'Masse: 175x100x74 cm': '175x100x74 cm'},
            'PROPN_CM': {'175x100x74 cm': '175x100x74 cm'},
            'X_X': {'175 x 100 x 74cm': '175 x 100 x 74'},
        }

    def __get_pattern_result_for_doc_as_text__(self, doc: Doc):
        for match_id, start, end in self._matcher(doc):
            # print('{}: doc[end - 1].text={}'.format(doc.text, doc[end-1].text))
            if doc[end-1].text == 'cm' or doc[end-2].text.lower() == 'x':
                span = Span(doc, start, end)
                return span.text
            return doc[end - 1].text
        return ''

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_text__(doc)
