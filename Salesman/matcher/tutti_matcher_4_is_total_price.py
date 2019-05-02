"""
Description: This module contains the matcher class for IsTotalPrice.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc
from salesman_tutti.tutti_constants import POS
from matcher.tutti_matcher import TuttiMatcher


class TuttiMatcher4IsTotalPrice(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
            return {
            'PREIS_FUER_ALLE': [{'LOWER': 'preis'}, {'LOWER': 'für'}, {'LOWER': 'alle'}],
            'ZUSAMMEN': [{'LOWER': 'zusammen'}],
            'SET_PROPN': [{'LOWER': 'set', 'POS': POS.PROPN}],
            'SET_X': [{'LOWER': 'set', 'POS': POS.X}],
            'PREIS_STUECK': [{'LOWER': 'preis/stück'}],
            'GESAMTPREIS': [{'LOWER': 'gesamtpreis'}]
        }

    def __get_pattern_type_test_case_dict__(self):
        return {
            'PREIS_FUER_ALLE': {"2'500 Fr. Preis für alle 4 Stühle zusammen": True,
                                'Preis pro Stück: 2000.-': False},
            'ZUSAMMEN': {'Der Preis ist für alle Stücke zusammen': True},
            'SET_PROPN': {'Preis ist für 4 er Set': True},
            'SET_X': {'Preis ist für 3 er set': True},
            'PREIS_STUECK': {'der Preis ist Preis/Stück.': True},
            'GESAMTPREIS': {'der Preis versteht sich als Gesamtpreis': True},
        }

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_bool__(doc)