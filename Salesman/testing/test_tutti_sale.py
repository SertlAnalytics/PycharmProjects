"""
Description: This module is the test module for the Tutti sale object
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-30
"""

from salesman_tutti.tutti_constants import EL
from salesman_tutti.tutti_sale import TuttiSale
from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_system_configuration import SystemConfiguration
from sertl_analytics.test.my_test_case import MyTestCaseHandler, MyTestCase


class Test4TuttiSale:
    def run_test(self, spacy: SalesmanSpacy, sys_config: SystemConfiguration):
        test_case_dict = self.__get_test_case_dict__()
        tc_handler = MyTestCaseHandler('Testing "{}":'.format(self.__class__.__name__))
        for key, test_case_list in test_case_dict.items():
            for tc in test_case_list:
                print('\nRUN_TEST: {}'.format(tc))
                sale_01 = TuttiSale(spacy, sys_config)
                sale_01.init_by_online_input(tc[0])
                sale_02 = TuttiSale(spacy, sys_config)
                sale_02.init_by_online_input(tc[1])
                if sys_config.print_details:
                    print('--> Entities for "{}": {}'.format(tc[0], sale_01.entity_label_dict))
                    print('--> Entities for "{}": {}'.format(tc[1], sale_02.entity_label_dict))
                if key == EL.COMPANY:
                    result = sale_01.is_any_company_entity_identical(sale_02)
                elif key == EL.PRODUCT:
                    result = sale_01.is_any_product_entity_identical(sale_02)
                elif key == EL.OBJECT:
                    result = sale_01.is_any_object_entity_identical(sale_02)
                elif key == EL.MATERIAL:
                    result = sale_01.is_any_material_entity_identical(sale_02)
                else:
                    result = sale_01.is_any_target_group_entity_identical(sale_02)
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
                ['Der Tisch Kitos und ein MacBook sind im Angebot', 'Hoffe, das Kitos und MacBook weggehen', True],
                ['Dyson hot+cool AM09', 'Dyson AM09 Hot Cool Heizlüfter', True],
                ['Dyson hot+cool AM09', 'Dyson hot & cool AM09 Heizlüfter', True],
                ['Dyson hot+cool AM09', 'Dyson Hot+Cool AM09 Heizlüfter', True],
                ['Dyson hot+cool AM09', 'DYSON Pure Hot & Cool Link', True],
            ],
            EL.OBJECT: [
                ['Sommerhut, Sommerkleid und der Corpus sollten raus', 'Das Auto ist unverkäuflich', False],
                ['Sommerhut, Sommerkleid und der Corpus sollten raus', 'Sommerhut und der Corpus sollten raus', True],
                ['Sommerhut und der Corpus sollten raus', 'Sonnenhut und der Rollcontainer sollten raus', True],
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

    def test_entity_similarity(self):
        TestSimilarity4TuttiSale().run_test(self._spacy, self.sys_config)


test_handler = TuttiSaleTestHandler()
test_handler.sys_config.print_details = False
test_handler.test_entity_similarity()





