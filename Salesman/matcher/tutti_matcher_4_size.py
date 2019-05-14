"""
Description: This module contains the matcher class for Size.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc, Span
from salesman_tutti.tutti_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4Size(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'GROESSE': [{'LOWER': 'grösse'}, {'POS': POS.PUNCT, 'OP': '?'}, {'POS': POS.NUM}, {'POS': POS.PROPN, 'OP': '?'}],
            'BREITE': [{'LOWER': 'breite'}, {'POS': POS.PUNCT, 'OP': '?'}, {'LIKE_NUM': True}, {'POS': POS.PROPN, 'OP': '?'}],
            'TIEFE': [{'LOWER': 'tiefe'}, {'POS': POS.PUNCT, 'OP': '?'}, {'LIKE_NUM': True}, {'POS': POS.PROPN, 'OP': '?'}],
            'HOEHE': [{'LOWER': 'höhe'}, {'POS': POS.PUNCT, 'OP': '?'}, {'LIKE_NUM': True}, {'POS': POS.X, 'OP': '?'}],
            'RAUMHOEHE': [{'LOWER': 'raumhöhe'}, {'POS': POS.PUNCT, 'OP': '?'},
                          {'POS': POS.PROPN, 'OP': '?'}, {'POS': POS.NUM, 'OP': '?'}, {'POS': POS.X}],
            'AUSSENHOEHE': [{'LOWER': 'aussenhöhe'}, {'POS': POS.PUNCT, 'OP': '?'},
                          {'POS': POS.PROPN, 'OP': '?'}, {'POS': POS.NUM, 'OP': '?'}, {'POS': POS.X}],
            'SCHNEELAST': [{'LOWER': 'schneelast'}, {'POS': POS.PUNCT, 'OP': '?'},
                          {'POS': POS.PROPN, 'OP': '?'}, {'POS': POS.NUM, 'OP': '?'}, {'POS': POS.X}],
            'BxH': [{'TEXT': 'B'}, {'TEXT': 'x'}, {'TEXT': 'H'}, {'POS': POS.PUNCT},
                    {'POS': POS.NUM, 'OP': '?'}, {'POS': POS.X}, {'POS': POS.NUM, 'OP': '?'}, {'POS': POS.X}],
            'BxT': [{'TEXT': 'B'}, {'TEXT': 'x'}, {'TEXT': 'T'}, {'POS': POS.PUNCT},
                    {'POS': POS.NUM, 'OP': '?'}, {'POS': POS.X}, {'POS': POS.NUM, 'OP': '?'}, {'POS': POS.X}],
            'B/T/H': [{'LEMMA': 'B/T/H'}, {'POS': POS.NUM}, {'POS': POS.PROPN}],
            'BxTxH': [{'TEXT': 'B'}, {'TEXT': 'x'}, {'TEXT': 'T'}, {'TEXT': 'x'}, {'TEXT': 'H'}, {'POS': POS.PUNCT},
                      {'POS': POS.NUM, 'OP': '?'}, {'POS': POS.X},
                      {'POS': POS.NUM, 'OP': '?'}, {'POS': POS.ADP}, {'POS': POS.NUM, 'OP': '?'}, {'POS': POS.X}],
            'GR': [{'LOWER': 'gr'}, {'POS': POS.PUNCT}, {'POS': POS.NUM}],
            'GR_2': [{'LOWER': 'gr'}, {'POS': POS.PUNCT}, {'POS': POS.NOUN}],
            'CM': [{'POS': POS.PROPN}, {'LOWER': 'cm'}],
            # 'MASSE': [{'LOWER': 'masse'}, {'POS': POS.PUNCT, 'OP': '?'}, {'POS': POS.PROPN}],
            'PROPN_CM': [{'POS': POS.PROPN, 'OP': '?'}, {'LIKE_NUM': True}, {'LOWER': 'cm'}],
            'ZIMMER': [{'POS': POS.NUM}, {'LOWER': 'zimmer'}, {'LOWER': 'wohnung', 'OP': '?'}],
            'X_X': [{'POS': POS.NUM}, {'POS': POS.X}, {'POS': POS.NUM}, {'POS': POS.X}, {'POS': POS.NUM}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'GROESSE': {'Grösse 38': '38'},
            'BREITE': {'Breite: 78.6 cm': 'Breite: 78.6 cm'},
            'TIEFE': {'Tiefe: 38.6 cm': 'Tiefe: 38.6 cm'},
            'HOEHE': {'Höhe: 148.5 cm': 'Höhe: 148.5 cm'},
            'RAUMHOEHE': {'Raumhöhe: 2.4m': 'Raumhöhe: 2.4m'},
            'AUSSENHOEHE': {'Aussenhöhe: 7m': 'Aussenhöhe: 7m'},
            'SCHNEELAST': {'Schneelast: 4t': 'Schneelast: 4t'},
            'BxH': {'B x H: 10x12m': 'B x H: 10x12m',
                    'B x H: 10 x 12m': 'B x H: 10 x 12m'},
            'BxT': {'B x T: 2.5x1.3m': 'B x T: 2.5x1.3m',
                    'B x T: 2.5 x 1.3m': 'B x T: 2.5 x 1.3m'},
            'BxTxH': {'B x T x H: 2.5 x 1.3 x 1.1 m': 'B x T x H: 2.5 x 1.3 x 1.1 m'},
            'B/T/H': {'USM Regal B/T/H 227/52/109 cm.': 'B/T/H 227/52/109 cm'},
            'GR': {'Gr. 37': '37'},
            'GR_2': {'Passt ca. Gr. 158/164': '158/164'},
            'CM': {'Masse: Durchmesser 90 cm': 'Durchmesser 90 cm'},
            # 'MASSE': {'Masse: 175x100x74 cm': '175x100x74 cm'},
            'PROPN_CM': {'175x100x74 cm': '175x100x74 cm'},
            'ZIMMER': {'3.5 Zimmer Wohnung': '3.5',
                       '4.5 Zimmer Loft': '4.5',
                       '5.5 Zimmer Haus': '5.5',},
            'X_X': {'175 x 100 x 74cm': '175 x 100 x 74'},
        }

    def __get_pattern_result_for_doc_as_text__(self, doc: Doc):
        for match_id, start, end in self._matcher(doc):
            # print('{}: Span(doc, start, end).text={}'.format(match_id, Span(doc, start, end).text))
            if doc[end-1].text in ['mm', 'cm', 'm', 'kg', 't'] or doc[end-2].text.lower() == 'x':
                span = Span(doc, start, end)
                return span.text
            elif doc[start + 1].text.lower() == 'zimmer':
                return doc[start].text
            return doc[end - 1].text
        return ''

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_text__(doc)
