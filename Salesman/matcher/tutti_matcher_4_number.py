"""
Description: This module contains the matcher class for Number.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc
from sertl_analytics.constants.salesman_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4Number(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'BIETEN_AUF': [{'LEMMA': 'bieten'}, {'POS': POS.ADP, 'OP': '?'}, {'POS': POS.NUM}],
            'MAL': [{'POS': POS.NUM}, {'LOWER': 'mal'}],  # 2 er set
            'SET': [{'POS': POS.NUM}, {'LOWER': 'er', 'OP': '?'}, {'LOWER': 'set'}],  # 2 er set
            'PREIS_FUER_ALLE': [{'LOWER': 'preis'}, {'LOWER': 'für'}, {'LOWER': 'alle'}, {'POS': POS.NUM}],
            'PREIS_FUER': [{'LOWER': 'preis'}, {'LOWER': 'für'}, {'POS': POS.NUM}],
            'STUECK': [{'POS': POS.NUM}, {'LOWER': 'stück'}],
            'STK': [{'POS': POS.NUM}, {'LOWER': 'stk'}],
            'DIESE': [{'LOWER': 'diese'}, {'POS': POS.NUM}],
            'BIS': [{'POS': POS.NUM}, {'LEMMA': '-'}, {'POS': POS.NUM}],
            'DESIGNKLASSIKER': [{'POS': POS.NUM}, {'LOWER': 'designklassiker'}],
            'DIE_NUM_NOUN': [{'LOWER': 'die'}, {'POS': POS.NUM}, {'POS': POS.NOUN}],
            'VERKAUFEN': [{'LEMMA': 'verkaufen'}, {'POS': POS.PRON, 'OP': '?'}, {'POS': POS.NUM}],
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'BIETEN_AUF': {'Sie bieten auf 4 Top Design-Stühle': 4,
                           'Sie bieten für 5 Top Design-Stühle': 5},
            'MAL': {'Wir bieten den Tisch 7 Mal an': 7},
            'SET': {'Wie bieten an ein 2 er set': 2,
                    '4 er Set Besucherstuhl gem. Bilder': 4},
            'PREIS_FUER_ALLE': {'Preis für alle 34 Stück: 2000.-': 34},
            'PREIS_FUER': {'Preis für 6 Stück': 6},
            'STUECK': {'es sind insgesamt 4 Stück vorhanden': 4,
                       'wurde. 4 Stück in blau': 4},
            'STK': {'Stühle CONFERENCE - 3 Stk.': 3},
            'DIESE': {'DIESE 6 Stühle werden nur zusammen EN BLOC verkauft': 6},
            'BIS': {'1-5 eames alu chair vitra': 5,
                    '052 649 11 78': 1},
            'DESIGNKLASSIKER': {'4 Designklassiker': 4},
            'DIE_NUM_NOUN': {'Die vier Stühle weisen alle eine sehr schöne Patina auf': 4},
            'VERKAUFEN': {'verkaufen wir 4 der bunten Stühle': 4},
        }

    def __get_pattern_result_for_doc_as_text__(self, doc: Doc):
        replace_dict = {'zwei': '2', 'drei': '3', 'vier': '4', 'fünf': '5', 'sechs': '6', 'acht': '8'}
        for match_id, start, end in self._matcher(doc):
            if doc[start].text.lower() in ['die', 'diese']:
                number_string = doc[start + 1].text
            elif doc[end-1].text.lower() in ['stk', 'stück', 'set', 'mal', 'designklassiker']:
                number_string = doc[start].text
            else:
                number_string = doc[end - 1].text
            return replace_dict.get(number_string, number_string)
        return ''

    def get_pattern_result_for_doc(self, doc: Doc):
        number_found = self.__get_pattern_result_for_doc_as_int__(doc)
        return 1 if number_found == 0 else number_found


