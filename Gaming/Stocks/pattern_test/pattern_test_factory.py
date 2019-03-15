"""
Description: This module contains the main test factory for the base functions.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-13
"""

from pattern_dash.my_dash_tab_for_waves import MyDashTab4WavesTest


class PatternTestFactory:
    def __init__(self, print_all_test_cases_for_units=False):
        self._print_all_test_cases_for_units = print_all_test_cases_for_units

    def run_test_for_my_dash_tab_fow_waves(self):
        test = MyDashTab4WavesTest(self._print_all_test_cases_for_units)
        test.run_test_for_all_units(test.class_name_tested)
