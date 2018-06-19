"""
Description: This module is the main module for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import dash


class MyDash:
    def __inti__(self):
        self.f = None

    def print(self):
        if self.f is None:
            print('a')