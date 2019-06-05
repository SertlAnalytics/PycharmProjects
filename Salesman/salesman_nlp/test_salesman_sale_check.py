"""
Description: This module is the test module for the Tutti sale object
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-30
"""

from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_sale_checks import SaleSimilarityCheck
from sertl_analytics.test.my_test_case import MyTestCaseHandler, MyTestCase
from salesman_search import SalesmanSearchApi
from factories.salesman_sale_factory import SalesmanSaleFactory
from salesman_system_configuration import SystemConfiguration


class Test4SalesmanSaleCheck:
    def __init__(self):
        self._salesman_spacy = SalesmanSpacy(load_sm=True)
        self._sys_config = SystemConfiguration()
        self._factory = SalesmanSaleFactory(self._sys_config, self._salesman_spacy)

    def run_test(self):
        test_case_dict = self.__get_test_case_dict__()
        tc_handler = MyTestCaseHandler('Testing "{}":'.format(self.__class__.__name__))
        api = SalesmanSearchApi('')
        for key, test_case_list in test_case_dict.items():
            for tc in test_case_list:
                api.search_string = tc[0]
                sale_01 = self._factory.get_sale_by_search_api(api)
                api.search_string = tc[1]
                sale_02 = self._factory.get_sale_by_search_api(api)
                check = SaleSimilarityCheck(sale_01, sale_02)
                expected = tc[2]
                result = '{}-{}-{}'.format(check.are_sales_similar, check.similar_label, check.similar_score)
                tc_handler.add_test_case(MyTestCase(key, tc, expected, result))
        tc_handler.print_result()

    def __get_test_case_dict__(self):
        return {
            'SIMILAR': [
                ['Das ist ein Text mit GoreTex und goretex und Goretex und nochmals Gore-Tex',
                 'Das ist ein Text mit GoreTex und goretex und Goretex und nochmals Gore-Tex',
                 'True-MATERIAL-1'],
            ],
            'NOT_SIMILAR': [
                ['USM Kitos Tisch, rund, höhenverstellbar. Farbe: perlgrau Masse: Durchmesser 90 cm'
                 'Besonderheit: höhenverstellbar (manuell) - sehr einfach, sehr stabil'
                 'Perfekt geeignet als Sitzungstisch oder Stehtisch im Büro oder Aufenthaltsraum.',
                 'Usm Haller Kitos. Usm Haller Kitos Besprechungstisch. Durchmesser 110cm Höhe 74cm '
                 'in einem gebrauchtem Zustand. Neupreis ca.1100 CHF Jetzt nur noch 390 CHF. '
                 'Die passenden Stühle dazu finden Sie bei uns.', 'True-COMPANY,PRODUCT,OBJECT-20'],
            ],
            # 'PRODUCT': [
            #     ['Die Serie 7 ist gut. Das beste an der Serie 7 ist der Preis', 'Serie 7 (PRODUCT)'],
            #     ['Vitra Aluminium Chair EA107 oder EA 108 oder MacBook',
            #      'Aluminium (MATERIAL), EA 108 (PRODUCT), EA107 (PRODUCT), MacBook (PRODUCT), Vitra (COMPANY)'],
            #     ['Vitra Bürostuhl EA108 günstig', 'Bürostuhl (OBJECT), EA108 (PRODUCT), Vitra (COMPANY)'],
            # ],
            # 'UNKNOWN_ORG': [
            #     ['Audi und Volvo bauen die sichersten Autos.', 'Audi (COMPANY), Volvo (COMPANY)'],
            #     ['Im Dow Jones sind u.a. Travelers Companies und Verizon enthalten',
            #      'Dow Jones (LOC), Travelers Companies (COMPANY), Verizon (COMPANY)'],
            # ],
            # 'TEST': [
            #     ['Winterschuhe Kinder, Lowa, Rufus III GTX, Gr. 37, Goretex Sommerhut, Strohhut',
            #      'Dow Jones (LOC), Travelers Companies (COMPANY), Verizon (COMPANY)'],
            # ]
        }

test_spacy = Test4SalesmanSaleCheck()
test_spacy.run_test()





