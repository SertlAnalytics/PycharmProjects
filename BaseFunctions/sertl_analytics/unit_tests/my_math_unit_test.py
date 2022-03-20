"""
Description: This module contains the unit tests for MyMath.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-13
"""

from sertl_analytics.mymath import MyMath
from sertl_analytics.test.my_test_case import MyTestCaseHandler
import unittest


class MyMathUnitTest(unittest.TestCase):
    def setUp(self):
        self._round_smart_elements = ((1.12345, 1.1235),
                                      (12.1234, 12.1234),
                                      (123.1234, 123.1234),
                                      (1234.1234, 1234.1234),
                                      (12345.1234, 12345.1234)
        )

    def testCalculation(self):
        self.__test_round_smart__()

    def __test_round_smart__(self):
        for (orig_value, round_value) in self._round_smart_elements:
            try:
                self.assertEqual(MyMath.round_smart(orig_value), round_value)
            except:
                print('error')


unittest.main()