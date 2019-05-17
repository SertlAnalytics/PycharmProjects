"""
Description: This module is the test module for the Tutti sale object
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-30
"""

from salesman_nlp.salesman_spacy import SalesmanSpacy
from sertl_analytics.test.my_test_case import MyTestCaseHandler, MyTestCase
from salesman_search import SalesmanSearchApi


class Test4SalesmanSpacy:
    def __init__(self):
        self._salesman_spacy = SalesmanSpacy(load_sm=True)

    def run_test(self, print_token=False):
        test_case_dict = self.__get_test_case_dict__()
        tc_handler = MyTestCaseHandler('Testing "{}":'.format(self.__class__.__name__))
        api = SalesmanSearchApi('')
        for key, test_case_list in test_case_dict.items():
            for tc in test_case_list:
                doc = self._salesman_spacy.nlp(tc[0])
                expected = tc[1]
                self._salesman_spacy.print_entities_for_doc(doc)
                if print_token:
                    self._salesman_spacy.print_tokens_for_doc(doc)
                result = self._salesman_spacy.get_entity_list(doc)
                tc_handler.add_test_case(MyTestCase(key, tc, expected, result))
        tc_handler.print_result()

    def __get_test_case_dict__(self):
        return {
            'REPLACEMENT': [
                ['Das ist ein Text mit GoreTex und goretex und Goretex und nochmals Gore-Tex', 'Goretex (MATERIAL)'],
            ],
            'COMPANY': [
                ['BMW und Apple sind beides tolle Firmen', 'Apple (COMPANY), BMW (COMPANY)'],
            ],
            'PRODUCT': [
                ['Die Serie 7 ist gut. Das beste an der Serie 7 ist der Preis', 'Serie 7 (PRODUCT)'],
                ['Vitra Aluminium Chair EA107 oder EA 108 oder MacBook',
                 'Aluminium (MATERIAL), EA 108 (PRODUCT), EA107 (PRODUCT), MacBook (PRODUCT), Vitra (COMPANY)'],
                ['Vitra Bürostuhl EA108 günstig', 'Bürostuhl (OBJECT), EA108 (PRODUCT), Vitra (COMPANY)'],
            ],
            'UNKNOWN_ORG': [
                ['Audi und Volvo bauen die sichersten Autos.', 'Audi (COMPANY), Volvo (COMPANY)'],
                ['Im Dow Jones sind u.a. Travelers Companies und Verizon enthalten',
                 'Dow Jones (LOC), Travelers Companies (COMPANY), Verizon (COMPANY)'],
            ]
        }


test_spacy = Test4SalesmanSpacy()
test_spacy.run_test(print_token=True)





