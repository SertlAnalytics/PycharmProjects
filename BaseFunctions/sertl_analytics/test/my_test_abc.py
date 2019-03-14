"""
Description: This module is the abstract base class for models and their related classes,
i.e they have to implement those functions.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-17
"""

from abc import ABCMeta, abstractmethod
from sertl_analytics.models.policy_action import PolicyAction


class TestInterface:
    __metaclass__ = ABCMeta
    
    def __init__(self, print_all_test_cases_for_units: bool):
        self._print_all_test_cases_for_units = print_all_test_cases_for_units
        self._test_unit_list = self.__get_test_unit_list__()
        self._test_unit_statistics = {}
        self._class_name_tested = self.__get_class_name_tested__()

    def run_test_for_all_units(self, class_name: str):  # tests all units in the class
        for test_unit in self._test_unit_list:
            self._test_unit_statistics[test_unit] = self.__run_test_for_unit__(test_unit)
        self.__print_statistics_for_unit_test__(class_name)

    @property
    def class_name_tested(self):
        return self._class_name_tested

    @classmethod
    def version(cls): return 1.0

    @abstractmethod
    def __get_class_name_tested__(self):  # name of the tested class
        raise NotImplementedError

    @abstractmethod
    def __get_test_unit_list__(self):  # list of all test cases which have to processed during a module test
        raise NotImplementedError

    @abstractmethod
    def __run_test_for_unit__(self, test_unit: str) -> bool:  # runs the test for a single test unit
        raise NotImplementedError
    
    def __print_statistics_for_unit_test__(self, class_name: str):
        print('\nUnit test statistics for {}:'.format(class_name))
        for test_unit, ok_nok_list in self._test_unit_statistics.items():
            ok_number = ok_nok_list[0]
            nok_number = ok_nok_list[1]
            passed = 'passed' if nok_number == 0 else 'NOT passed'
            details = '(ok={}, nok={})'.format(ok_number, nok_number)
            print('{}: {} {}'.format(test_unit, passed, details))

    def __verify_test_cases__(self, unit: str, test_case_dict: dict):
        """
        checks for each test case whether the result of the unit is identical to the expected value
        :param test_case_dict: Format {'test_case_description': [result, expected_result], ....}
        :param print_all:
        :return: True or False (if any of the result != expected result
        """
        print('\nRunning test cases for {}:'.format(unit))
        count_ok = 0
        count_nok = 0
        for test_case, result_list in test_case_dict.items():
            test_ok = result_list[0] == result_list[1]
            if test_ok:
                count_ok += 1
            else:
                count_nok += 1
            if self._print_all_test_cases_for_units or not test_ok:
                print('{:2d}) {}: result = {}, expected = {} -> {}'.format(count_ok + count_nok,
                    test_case, result_list[0], result_list[1], '{}'.format('OK' if test_ok else 'NOK')))
        return [count_ok, count_nok]
        


