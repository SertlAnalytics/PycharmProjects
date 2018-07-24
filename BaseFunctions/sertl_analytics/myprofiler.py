"""
Description: This module contains profiler class for all applications from SERTL Analytics.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-22
"""

import cProfile, pstats


class MyProfiler:  # https://docs.python.org/3/library/profile.html
    def __init__(self):
        self.profile = cProfile.Profile()
        self.profile.enable()

    def disable(self, to_print: bool = True, print_stats_filter: str = 'pattern'):
        self.profile.disable()
        if to_print:
            self.print_stats(print_stats_filter)

    def print_stats(self, filter: str):
        ps = pstats.Stats(self.profile).sort_stats('cumulative')
        ps.print_stats(0.1, filter)