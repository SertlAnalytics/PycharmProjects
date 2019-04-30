"""
Description: This module contains the classes for creating and running test cases
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-08
"""


class MyTestCase:
    def __init__(self, tc_key: str, test_data, expected, result=None):
        self._key = tc_key
        self._test_data = test_data
        self._result_expected = expected
        self._result = result

    @property
    def is_ok(self) -> bool:
        return self._result_expected == self._result

    def set_result(self, result):
        self._result = result

    def print_result(self):
        print('...{} {}:\texpected={}\tresult={}\t--> {}'.format(
            self._key, self._test_data, self._result_expected, self._result, self.is_ok
        ))


class MyTestCaseHandler:
    def __init__(self, title: str):
        self._title = title
        self._test_case_list = []
        self._counter_ok = 0

    @property
    def count(self):
        return len(self._test_case_list)

    def add_test_case(self, test_case: MyTestCase):
        self._test_case_list.append(test_case)

    def print_result(self):
        print('Results for {}'.format(self._title))
        for test_case in self._test_case_list:
            self._counter_ok += 1 if test_case.is_ok else 0
            test_case.print_result()
        passed = 'PASSED' if self.count == self._counter_ok else 'NOT passed'
        print('***Summary: {}/{} ok\t\t{} nok \t--> {}***'.format(
            self._counter_ok, self.count, self.count-self._counter_ok, passed))