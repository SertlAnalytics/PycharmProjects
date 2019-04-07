"""
Description: This module contains the matcher classes for Tutti nlp.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy import displacy
from spacy.tokens import Doc, Span
from spacy.matcher import Matcher, PhraseMatcher
from tutti_constants import EL, POS, DEP
from sertl_analytics.mymath import MyMath
from tutti_named_entity import TuttiCompanyEntity, TuttiProductEntity
import spacy


class TuttiMatcher:
    def __init__(self, nlp):
        self._matcher = Matcher(nlp.vocab)
        self._pattern_dict = self.__get_pattern_dict__()
        self.__add_pattern_to_matcher__()

    def get_pattern_result_for_doc(self, doc: Doc):
        pass

    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {}

    def __get_pattern_result_for_doc_as_text__(self, doc: Doc):
        for match_id, start, end in self._matcher(doc):
            return doc[end - 1].text
        return ''

    def __get_pattern_result_for_doc_as_float__(self, doc: Doc):
        text_result = self.__get_pattern_result_for_doc_as_text__(doc)
        return MyMath.get_float_for_string(text_result)

    def __get_pattern_result_for_doc_as_int__(self, doc: Doc):
        return int(self.__get_pattern_result_for_doc_as_float__(doc))

    def __get_pattern_result_for_doc_as_bool__(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_text__(doc) != ''

    def __add_pattern_to_matcher__(self):
        for key, pattern in self._pattern_dict.items():
            self._matcher.add(key, None, pattern)


class TuttiMatcher4Size(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'GROESSE': [{'LOWER': 'grösse'}, {'POS': POS.NUM}],
            'GR': [{'LOWER': 'gr'}, {'POS': POS.PUNCT}, {'POS': POS.NUM}],
            'CM': [{'POS': POS.PROPN}, {'LOWER': 'cm'}],
            # 'MASSE': [{'LOWER': 'masse'}, {'POS': POS.PUNCT, 'OP': '?'}, {'POS': POS.PROPN}],
            'NOUND_CM': [{'POS': POS.PROPN, 'OP': '?'}, {'LIKE_NUM': True}, {'LOWER': 'cm'}],
        }

    def __get_pattern_result_for_doc_as_text__(self, doc: Doc):
        for match_id, start, end in self._matcher(doc):
            # print('{}: doc[end - 1].text={}'.format(doc.text, doc[end-1].text))
            if doc[end-1].text == 'cm':
                span = Span(doc, start, end)
                return span.text
            return doc[end - 1].text
        return ''

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_text__(doc)


class TuttiMatcher4OriginalPrize(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'CA': [{'LOWER': 'ca.'}, {'POS': POS.NUM}],  # ca. 2800.- 18 Stk vorhanden
            'NEUPREIS': [{'LOWER': 'neupreis'}, {'POS': POS.NUM}],
            'NEUPREIS_ADJ': [{'LOWER': 'neupreis'}, {'POS': POS.ADJ}],
            'GEKAUFT': [{'LOWER': 'gekauft'}, {'POS': POS.ADP}, {'POS': POS.NUM}],
            'CHF': [{'LOWER': 'chf'}, {'POS': POS.NUM}],
            'CHF_NOUN': [{'LOWER': 'chf'}, {'POS': POS.PROPN}],
            'NP': [{'LOWER': 'np'}, {'POS': POS.PUNCT}, {'POS': POS.NUM}],  # NP: 2800.- 18 Stk vorhanden
        }

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_int__(doc)


class TuttiMatcher4SinglePrize(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'VERKAUFSPREIS': [{'LOWER': 'verkaufspreis'}, {'POS': POS.NUM}],  # Verkaufspreispreis 79.- pro Stück
            'VERKAUFSPREIS_NOUN': [{'LOWER': 'verkaufspreis'}, {'POS': POS.NOUN}],  # Verkaufspreispreis 79.- pro Stück
            'STUECK': [{'LOWER': 'stück'}, {'POS': POS.PUNCT}, {'POS': POS.X}],  # Preis pro Stück: 2000.-
            'PRO_STUECK': [{'POS': POS.NUM}, {'LOWER': 'pro'}, {'LOWER': 'stück'}],  # Verkaufspreispreis 79.- pro Stück
            'PRO_STUECK_nk': [{'DEP': DEP.nk}, {'LOWER': 'pro'}, {'LOWER': 'stück'}],  # Verkaufspreispreis 79.- pro Stück
        }

    def __get_pattern_result_for_doc_as_text__(self, doc: Doc):
        for match_id, start, end in self._matcher(doc):
            if doc[end - 1].text.lower() in ['stück']:
                return doc[start].text
            return doc[end - 1].text
        return ''

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_int__(doc)


class TuttiMatcher4Number(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'MAL': [{'POS': POS.NUM}, {'LOWER': 'mal'}],  # 2 er set
            'SET': [{'POS': POS.NUM}, {'LOWER': 'er', 'OP': '?'}, {'LOWER': 'set'}],  # 2 er set
            'PREIS_FUER_ALLE': [{'LOWER': 'preis'}, {'LOWER': 'für'}, {'LOWER': 'alle'}, {'POS': POS.NUM}],  # Preis für alle
            'STUECK': [{'POS': POS.NUM}, {'LOWER': 'stück'}],
        }

    def __get_pattern_result_for_doc_as_text__(self, doc: Doc):
        for match_id, start, end in self._matcher(doc):
            if doc[end-1].text.lower() in ['stück', 'set', 'mal']:
                return doc[start].text
            return doc[end - 1].text
        return ''

    def get_pattern_result_for_doc(self, doc: Doc):
        number_found = self.__get_pattern_result_for_doc_as_int__(doc)
        return 1 if number_found == 0 else number_found


class TuttiMatcher4IsNew(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
        return {
            'NEUWERTIG': [{'LOWER': 'neuwertig'}],
            'NEUWERTIGEN': [{'LOWER': 'neuwertigen'}],
            'NEUWERTIGEM': [{'LOWER': 'neuwertigem'}],
            'ORIGINALVERPACKT': [{'LOWER': 'originalverpackt'}],
            'ORIGINALVERPACKUNG': [{'LOWER': 'originalverpackung'}],
            'WIE_NEU': [{'POS': 'ADJ', 'OP': '?'}, {'LOWER': 'neu'}],
            'ZUSTAND_SEHR_GUT':
                [{'LOWER': 'zustand'}, {'POS': POS.PUNCT, 'OP': '?'}, {'LOWER': 'sehr'}, {'LOWER': 'gut'}],
            'SEHR_GUTEM_ZUSTANT': [{'LOWER': 'sehr'}, {'LEMMA': 'gut'}, {'LOWER': 'zustand'}],
            'NEU': [{'LOWER': 'neu'}],
        }

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_bool__(doc)


class TuttiMatcher4IsUsed(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
            return {
            'BESCHAEDIGUNG': [{'LOWER': 'beschädigung'}],
            'FAST_NEU': [{'LOWER': 'fast'}, {'POS': 'CONJ', 'OP': '?'}, {'LOWER': 'neu'}],  # fast wie neu
            'GEBRAUCHT': [{'LOWER': 'gebraucht', 'POS': POS.VERB}],
            'GEBRAUCHSSPUREN': [{'LOWER': 'gebrauchsspuren'}],
            'GEBRAUCHSPUREN': [{'LOWER': 'gebrauchspuren'}],
            'GETRAGEN': [{'LOWER': 'getragen', 'POS': POS.VERB}],
            'GUT_ERHALTEN': [{'LOWER': 'gut'}, {'LOWER': 'erhalten', 'POS': POS.VERB}],
            'GUTER_ZUSTAND': [{'LEMMA': 'gut'}, {'LOWER': 'zustand'}],
            'IN_GUTEM_ZUSTAND': [{'LOWER': 'in'}, {'LOWER': 'gutem'}, {'POS': 'ADJ', 'OP': '?'}, {'LOWER': 'zustand'}],
            'KRATZER': [{'LOWER': 'kratzer', 'POS': POS.NOUN}],
            'NEUPREIS': [{'LOWER': 'neupreis', 'POS': POS.NOUN}],
            'NICHT_MEHR': [{'LOWER': 'nicht'}, {'LOWER': 'mehr'}, {'POS': 'ADV', 'OP': '?'}, {'LOWER': 'neu'}],
            'SCHADEN': [{'LOWER': 'schaden', 'POS': POS.NOUN}],
            'FLECKEN': [{'LOWER': 'flecken', 'POS': POS.NOUN}],
        }

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_bool__(doc)


class TuttiMatcher4IsTotalPrice(TuttiMatcher):
    @staticmethod
    def __get_pattern_dict__() -> dict:
            return {
            'PREIS_FUER_ALLE': [{'LOWER': 'preis'}, {'LOWER': 'für'}, {'LOWER': 'alle'}],
            'ZUSAMMEN': [{'LOWER': 'zusammen'}],
            'SET_PROPN': [{'LOWER': 'set', 'POS': POS.PROPN}],
            'SET_X': [{'LOWER': 'set', 'POS': POS.X}],
            'GESAMTPREIS': [{'LOWER': 'gesamtpreis'}]
        }

    def get_pattern_result_for_doc(self, doc: Doc):
        return self.__get_pattern_result_for_doc_as_bool__(doc)

