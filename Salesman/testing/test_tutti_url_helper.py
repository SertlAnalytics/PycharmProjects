"""
Description: This module is the test module for the Tutti sale object
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-30
"""

from sertl_analytics.test.my_test_case import MyTestCaseHandler, MyTestCase
from sertl_analytics.constants.salesman_constants import SLDC, PRCAT, REGION
from salesman_tutti.tutti_url_helper import TuttiUrlHelper
from salesman_tutti.tutti_categorizer import RegionCategorizer, ProductCategorizer


class Test4TuttiUrlHelper:
    def __init__(self):
        self._href_prefix = 'https://www.tutti.ch/de/vi/'
        self._region_categorizer = RegionCategorizer()
        self._product_categorizer = ProductCategorizer()

    def run_test(self):
        test_case_dict = self.__get_test_case_dict__()
        tc_handler = MyTestCaseHandler('Testing "{}":'.format(self.__class__.__name__))
        for key, test_case_list in test_case_dict.items():
            for tc in test_case_list:
                print('\nRUN_TEST: {}'.format(tc))
                url, expected_result = tc[0], tc[1]
                url_helper = TuttiUrlHelper(
                    url, region_categorizer=self._region_categorizer, product_categorizer=self._product_categorizer)
                href_component_dict = url_helper.get_href_component_dict()
                result = href_component_dict[key]
                tc_handler.add_test_case(MyTestCase(key, url[len(self._href_prefix):], expected_result, result))
        tc_handler.print_result()

    def __get_test_case_data_dict__(self):
        test_case_base_dict = {
            'AG': 'aargau/buero-gewerbe/bueromaterial-bueromoebel/vitra-meda-slim-ab-austellung/27966535',
            'ZG': 'zug/buero-gewerbe/bueromaterial-bueromoebel/vitra-ea-219-buerostuhl-in-leder/28124689',
            'ZH': 'zuerich/haushalt/moebel/vitra-eames-pacc-buerostuhl/26808740',
            'ZW': 'zuerich/winterthur/buero-gewerbe/bueromaterial-bueromoebel/vitra-meda-chair-buerostuhl-buero-stuhl/21639212',
            'ZB': 'zuerich/buero-gewerbe/bueromaterial-bueromoebel/vitra-eames-ea-219-soft-pad-buerodrehstuhl/24275693',
            'ZA': 'zuerich/antiquitaeten-kunst/design-vintage-buerostuhl-vitra-eames-ea-219-leder-schwarz/28204116'
        }
        return {key: '{}{}'.format(self._href_prefix, test_case) for key, test_case in test_case_base_dict.items()}

    def __get_test_case_dict__(self):
        test_case_data_dict = self.__get_test_case_data_dict__()
        return {
            SLDC.REGION: [
                [test_case_data_dict['AG'], REGION.AARGAU],
                [test_case_data_dict['ZG'], REGION.ZUG],
                [test_case_data_dict['ZH'], REGION.ZUERICH],
                [test_case_data_dict['ZA'], REGION.ZUERICH],
            ],
            SLDC.PRODUCT_CATEGORY: [
                [test_case_data_dict['AG'], PRCAT.BUSINESS],
                [test_case_data_dict['ZH'], PRCAT.HOUSEHOLD],
                [test_case_data_dict['ZW'], PRCAT.BUSINESS],
                [test_case_data_dict['ZB'], PRCAT.BUSINESS],
                [test_case_data_dict['ZA'], PRCAT.ART],
            ],
            SLDC.PRODUCT_SUB_CATEGORY: [
                [test_case_data_dict['AG'], 'Büromaterial & Büromöbel'],
                [test_case_data_dict['ZH'], 'Möbel'],
                [test_case_data_dict['ZW'], 'Büromaterial & Büromöbel'],
                [test_case_data_dict['ZB'], 'Büromaterial & Büromöbel'],
                [test_case_data_dict['ZA'], ''],
            ],
            SLDC.TITLE: [
                [test_case_data_dict['AG'], 'vitra-meda-slim-ab-austellung'],
                [test_case_data_dict['ZA'], 'design-vintage-buerostuhl-vitra-eames-ea-219-leder-schwarz'],
            ],
            SLDC.SALE_ID: [
                [test_case_data_dict['AG'], '27966535'],
                [test_case_data_dict['ZA'], '28204116'],
            ],
        }


Test4TuttiUrlHelper().run_test()






