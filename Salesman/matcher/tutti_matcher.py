"""
Description: This module contains the matcher classes for Tutti nlp.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-05
"""

from spacy.tokens import Doc
from spacy.matcher import Matcher
from sertl_analytics.mymath import MyMath
from sertl_analytics.test.my_test_case import MyTestCaseHandler, MyTestCase


class TuttiMatcher:
    def __init__(self, nlp):
        self._matcher = Matcher(nlp.vocab)
        self._pattern_dict = self.__get_pattern_dict__()
        self.__add_pattern_to_matcher__()

    def get_pattern_result_for_doc(self, doc: Doc):
        pass

    def run_test(self, spacy, print_token=False):
        pattern_type_testcase_dict = self.__get_pattern_type_test_case_dict__()
        tc_handler = MyTestCaseHandler('Testing "{}":'.format(self.__class__.__name__))
        for pattern_type, test_case_dict in pattern_type_testcase_dict.items():
            for test_string, expected_value in test_case_dict.items():
                doc = spacy.nlp(test_string)
                print('\nRUN_TEST: {} -> {}'.format(test_string, doc.text))
                if print_token:
                    spacy.print_tokens_for_doc(doc)
                result = self.get_pattern_result_for_doc(doc)
                tc_handler.add_test_case(MyTestCase(pattern_type, test_string, expected_value, result))
        tc_handler.print_result()

    def __get_pattern_type_test_case_dict__(self):
        return {
            'GROESSE': {'Gr. 37': '37'},
            'GR': {'Grösse 38': '38'}
        }

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



