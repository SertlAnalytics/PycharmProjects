"""
Description: This module is the test module for the Tutti sale object
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-30
"""

from salesman_tutti.tutti_constants import EL
from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_system_configuration import SystemConfiguration
from sertl_analytics.test.my_test_case import MyTestCaseHandler, MyTestCase
from sertl_analytics.constants.salesman_constants import SLDC
from factories.salesman_sale_factory import SalesmanSaleFactory
from salesman_sale_checks import SaleSimilarityCheck
from salesman_search import SalesmanSearchApi

class Test4TuttiSale:
    def run_test(self, spacy: SalesmanSpacy, sys_config: SystemConfiguration, sale_factory: SalesmanSaleFactory):
        test_case_dict = self.__get_test_case_dict__()
        tc_handler = MyTestCaseHandler('Testing "{}":'.format(self.__class__.__name__))
        api = SalesmanSearchApi('')
        for key, test_case_list in test_case_dict.items():
            for tc in test_case_list:
                print('\nRUN_TEST: {} for {}'.format(tc, key))
                api.search_string = tc[0]
                sale_01 = sale_factory.get_sale_by_search_api(api)
                print('...sale_01.labels={}'.format(sale_01.get_value(SLDC.ENTITY_LABELS_DICT)))
                api.search_string = tc[1]
                sale_02 = sale_factory.get_sale_by_search_api(api)
                print('...sale_02.labels={}'.format(sale_02.get_value(SLDC.ENTITY_LABELS_DICT)))

                sale_similarity_check = SaleSimilarityCheck(sale_01, sale_02)
                result = sale_similarity_check.are_sales_similar
                similar_label = sale_similarity_check.similar_label
                print('...expected_label_for_check: {} ({}) - real: {}'.format(key, tc[2], similar_label))

                if sys_config.print_details:
                    print('--> Entities for "{}": {}'.format(tc[0], sale_01.entity_label_dict))
                    print('--> Entities for "{}": {}'.format(tc[1], sale_02.entity_label_dict))

                print('')
                tc_handler.add_test_case(MyTestCase(key, tc, tc[2], result))
        tc_handler.print_result()

    def __get_test_case_dict__(self):
        pass


class TestSimilarity4TuttiSale(Test4TuttiSale):
    def __get_test_case_dict__(self):
        return {
            EL.TARGET_GROUP: [
                ['Ist für Frauen und Männer geeignet', 'Ist nicht für Babies gemacht', False],
                ['Ist für Frauen und Männer geeignet', 'Frauen sind unsere Zielgruppe', True],
                ['Ist für Frauen und Männer geeignet', 'Damen sollten berücksicht werden', True],
            ],
            EL.COMPANY: [
                ['BMW und Apple sind beides tolle Firmen', 'Mercedes ist auch nicht schlecht', False],
                ['BMW und Apple sind beides tolle Firmen', 'Apple ist erfolgreicher', True]
            ],
            EL.PRODUCT: [
                ['Der Tisch Kitos und ein MacBook sind im Angebot', 'Die Kugelbahn Roundabout sollte weg', False],
                ['Der Tisch Kitos und ein MacBook sind im Angebot', 'Hoffe, dass Kitos und MacBook weggehen', True],
                ['hot+cool AM09', 'AM09 Hot Cool Heizlüfter', True],
                ['hot+cool AM09', 'hot & cool AM09 Heizlüfter', True],
                ['hot+cool AM09', 'Hot+Cool AM09 Heizlüfter', True],
                ['hot+cool AM09', 'Pure Hot & Cool Link', True],
            ],
            EL.OBJECT: [
                ['Sommerhut, Sommerkleid und der Corpus sollten raus', 'Das Auto ist unverkäuflich', False],
                ['Sommerhut, Sommerkleid und der Corpus sollten raus', 'Sommerhut und der Corpus sollten raus', True],
                ['Sommerhut und der Corpus sollten raus', 'Sonnenhut und der Rollcontainer sollten raus', True],
                ['Der Nagerkäfig sollte raus', 'Der Hamsterkäfig ist aus Holz', False],
            ],
            EL.MATERIAL: [
                ['Leder oder Kunstleder', 'Aluminium ist das Material', False],
                ['Leder oder Kunstleder', 'Leder und Aluminium', True]
            ],
        }


class TuttiSaleTestHandler:
    def __init__(self):
        self.sys_config = SystemConfiguration()
        self._spacy = SalesmanSpacy(load_sm=self.sys_config.load_sm) if self.sys_config.with_nlp else None
        self._sale_factory = SalesmanSaleFactory(self.sys_config, self._spacy)

    def test_entity_similarity(self):
        TestSimilarity4TuttiSale().run_test(self._spacy, self.sys_config, self._sale_factory)


test_handler = TuttiSaleTestHandler()
test_handler.sys_config.print_details = False
test_handler.test_entity_similarity()





